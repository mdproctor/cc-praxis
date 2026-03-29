---
name: logging-observability
description: >
  Use when the user mentions "logging", "tracing", "observability", "MDC",
  "structured logs", "JSON logs", "OpenTelemetry", "OTel", "Prometheus",
  "metrics", "Kibana", "Loki", "Datadog", "workflow tracing", or
  "quarkus.flow.tracing". Also use when debugging a workflow in production
  or setting up monitoring. Configures structured logging, MDC fields,
  distributed tracing, and metrics for Quarkus and quarkus-flow applications.
---

# Logging and Observability

Quarkus and quarkus-flow provide three complementary observability
mechanisms: structured logging with MDC, distributed tracing via
OpenTelemetry, and metrics via Micrometer/Prometheus. This skill covers
how to configure and use them together correctly.

---

## 1. Structured JSON Logging

### Enable JSON console output

~~~properties
quarkus.log.console.json.enabled=true
~~~

This is the standard for cloud deployments — log aggregators (Kibana,
Loki, Datadog, GCP Logging) parse structured JSON fields directly.

### Disable in dev/test (human-readable output)

~~~properties
%dev.quarkus.log.console.json.enabled=false
%test.quarkus.log.console.json.enabled=false
~~~

### Log levels

~~~properties
# Global level
quarkus.log.level=INFO

# Per-package (avoid DEBUG globally in prod — too noisy)
quarkus.log.category."io.quarkiverse.flow".level=INFO
quarkus.log.category."org.acme.casehub".level=INFO

# Debug for a specific subsystem during investigation
%dev.quarkus.log.category."io.quarkiverse.flow".level=DEBUG
~~~

### Using SLF4J correctly in application code

~~~java
import org.jboss.logging.Logger;

// Prefer JBoss Logger (Quarkus native) over SLF4J in Quarkus apps
private static final Logger LOG = Logger.getLogger(MyService.class);

// Log with context — always include identifiers
LOG.infof("Processing case caseId=%s workflowId=%s", caseId, workflowId);

// Never log sensitive data (PII, tokens, passwords)
// Bad:
LOG.infof("User authenticated email=%s password=%s", email, password);
// Good:
LOG.infof("User authenticated userId=%s", userId);
~~~

---

## 2. quarkus-flow Workflow Tracing

### MDC fields emitted by quarkus-flow

Every workflow lifecycle event includes these MDC fields in logs:

| MDC Key | Example value | When present |
|---|---|---|
| `quarkus.flow.instanceId` | `01K9GDCXJVN89V0N4CWVG40R7C` | Always |
| `quarkus.flow.event` | `workflow.started`, `task.failed` | Always |
| `quarkus.flow.time` | `2026-03-12T19:20:59.120Z` | Always |
| `quarkus.flow.task` | `fetchCaseData` | Task events only |
| `quarkus.flow.taskPos` | `do/0/fetchCaseData` | Task events only |

### Enable tracing

~~~properties
# Enabled by default in dev/test, disabled in prod
quarkus.flow.tracing.enabled=true

# Disable in dev if too noisy during development
%dev.quarkus.flow.tracing.enabled=false
~~~

### Query by instance in your log aggregator

With JSON logging enabled, filter a complete workflow execution:

~~~
# Kibana / OpenSearch
mdc.quarkus.flow.instanceId: "01K9GDCXJVN89V0N4CWVG40R7C"

# Loki / Grafana
{app="casehub"} | json | mdc_quarkus_flow_instanceId="01K9GDCXJVN89V0N4CWVG40R7C"

# Datadog
@mdc.quarkus.flow.instanceId:01K9GDCXJVN89V0N4CWVG40R7C
~~~

### Plain text format (if JSON not enabled)

~~~properties
quarkus.log.console.format=%d{HH:mm:ss} %-5p instanceId=%X{quarkus.flow.instanceId} task=%X{quarkus.flow.task} [%c{2.}] %s%n
~~~

### HTTP header propagation

quarkus-flow automatically adds correlation headers to all outgoing HTTP
calls from workflow tasks:

| Header | Maps to MDC field |
|---|---|
| `X-Flow-Instance-Id` | `quarkus.flow.instanceId` |
| `X-Flow-Task-Id` | `quarkus.flow.taskPos` |

Downstream services should log these headers to enable end-to-end
correlation. Disable if a strict API rejects unknown headers:

~~~properties
quarkus.flow.http.client.enable-metadata-propagation=false
~~~

### Workflow tracing vs messaging lifecycle events

| Mechanism | Output | Use for |
|---|---|---|
| `quarkus.flow.tracing.enabled` | Stdout / log aggregator | Operational debugging, log search |
| `quarkus.flow.messaging.lifecycle-enabled` | Kafka CloudEvents | System integration, triggering downstream services |

Both can be active simultaneously.

---

## 3. OpenTelemetry (OTel) Distributed Tracing

### Dependencies

~~~xml
<dependency>
  <groupId>io.quarkus</groupId>
  <artifactId>quarkus-opentelemetry</artifactId>
</dependency>
~~~

### Configuration

~~~properties
# OTLP exporter endpoint (Jaeger, Tempo, Honeycomb, etc.)
quarkus.otel.exporter.otlp.endpoint=http://localhost:4317

# Service name — appears in trace UIs
quarkus.otel.resource.attributes=service.name=casehub

# Disable in dev if no collector running locally
%dev.quarkus.otel.sdk.disabled=true
%test.quarkus.otel.sdk.disabled=true
~~~

### Adding custom spans in application code

~~~java
import io.opentelemetry.instrumentation.annotations.WithSpan;
import io.opentelemetry.instrumentation.annotations.SpanAttribute;

// Annotate methods that represent meaningful units of work
@WithSpan("casehub.processCase")
public Uni<CaseResult> processCase(
        @SpanAttribute("case.id") String caseId) {
    // ...
}
~~~

**Do not** annotate every method — only meaningful business operations.
Over-instrumentation creates noise and overhead.

### Correlation with quarkus-flow

The `quarkus.flow.instanceId` from MDC and the OTel `traceId` are
separate identifiers. To correlate them, add the flow instance ID as
a span attribute in your workflow entry point:

~~~java
import io.opentelemetry.api.trace.Span;

// In a REST resource that starts a workflow:
Span.current().setAttribute("flow.instanceId", instanceId);
~~~

---

## 4. Metrics (Micrometer + Prometheus)

### Dependencies

~~~xml
<dependency>
  <groupId>io.quarkus</groupId>
  <artifactId>quarkus-micrometer-registry-prometheus</artifactId>
</dependency>
~~~

### Expose metrics endpoint

~~~properties
# Metrics available at /q/metrics by default
quarkus.micrometer.export.prometheus.enabled=true
~~~

### quarkus-flow built-in metrics

quarkus-flow exposes workflow metrics automatically when Micrometer is
on the classpath. Key metrics:

| Metric | Type | Description |
|---|---|---|
| `quarkus_flow_workflow_started_total` | Counter | Workflows started |
| `quarkus_flow_workflow_completed_total` | Counter | Workflows completed |
| `quarkus_flow_workflow_failed_total` | Counter | Workflows failed |
| `quarkus_flow_task_duration_seconds` | Histogram | Per-task execution time |

### Custom application metrics

~~~java
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Counter;

@ApplicationScoped
public class CaseMetrics {

    private final Counter casesProcessed;

    public CaseMetrics(MeterRegistry registry) {
        casesProcessed = Counter.builder("casehub.cases.processed")
            .description("Total cases processed")
            .tag("status", "success")
            .register(registry);
    }

    public void recordProcessed() {
        casesProcessed.increment();
    }
}
~~~

---

## 5. Common Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| No MDC fields in logs | JSON logging disabled or plain text format missing `%X{}` | Enable JSON or add MDC keys to format string |
| `instanceId` missing from task logs | Tracing disabled in prod | Set `quarkus.flow.tracing.enabled=true` |
| Downstream service can't correlate | Header propagation disabled or downstream ignores headers | Check `enable-metadata-propagation`; add header logging downstream |
| OTel traces not appearing | Collector not running or wrong endpoint | Disable OTel in dev with `quarkus.otel.sdk.disabled=true` |
| Sensitive data in logs | Logging full request/response objects | Log only IDs and status codes; never log PII |
| Log aggregator can't parse fields | Plain text format used instead of JSON | Enable `quarkus.log.console.json.enabled=true` in prod |

---

## Recommended production configuration

~~~properties
# Structured logging
quarkus.log.console.json.enabled=true
quarkus.log.level=INFO
quarkus.log.category."org.acme.casehub".level=INFO

# quarkus-flow tracing
quarkus.flow.tracing.enabled=true

# OTel (set endpoint to your collector)
quarkus.otel.exporter.otlp.endpoint=http://otel-collector:4317
quarkus.otel.resource.attributes=service.name=casehub

# Metrics
quarkus.micrometer.export.prometheus.enabled=true
~~~

---

## Skill Chaining

- If adding OTel or Micrometer dependencies: invoke **dependency-update**
  to verify BOM alignment.
- If this is the first time setting up observability for CaseHub: consider
  an ADR via **adr** documenting the logging and tracing strategy chosen.
- Observability config changes are good candidates for **java-git-commit**
  with type `chore(observability)`.