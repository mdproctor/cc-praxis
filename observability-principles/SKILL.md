---
name: observability-principles
description: >
  Universal observability principles covering structured logging, distributed
  tracing, and metrics. Includes MDC/correlation ID patterns, header
  propagation, trace span concepts, and metrics types. Technology-agnostic
  guidance for production observability. Use as foundation for
  framework-specific observability skills.
---

# Observability Principles

Universal principles for production observability: structured logging, distributed tracing, and metrics. Enables debugging production issues and understanding system behavior at scale.

## Why This Matters

**With observability vs. without:**
- With correlation IDs: Find all logs for failing request in seconds
- Without correlation IDs: Grep through gigabytes of logs manually for hours

**What observability enables:**
- **Root cause analysis** — trace request end-to-end across services to find bottleneck
- **Production debugging** — filter logs by correlation ID to see exact failure path
- **Performance optimization** — identify slowest spans in distributed trace
- **Proactive monitoring** — alert on metrics before users notice issues

**The three pillars:**
1. **Logs** — discrete events with context (what happened, when, where)
2. **Traces** — request flows across services (path through system)
3. **Metrics** — aggregated measurements over time (counters, histograms)

## Workflow

### Step 1 — Configure structured logging

Enable JSON output for production, set appropriate log levels, configure MDC for correlation fields.

### Step 2 — Implement correlation ID propagation

Generate correlation IDs at entry points, store in MDC/context, propagate via HTTP headers to downstream services.

### Step 3 — Enable distributed tracing

Configure OpenTelemetry exporter, set service name, add custom spans for business operations.

### Step 4 — Instrument custom metrics

Create counters, histograms, and gauges for business-relevant operations with consistent naming.

### Step 5 — Verify observability stack

Test that logs include correlation fields, traces appear in collector, metrics endpoint exposes data.

---

## Structured Logging Checklist

Apply these patterns when configuring logging:

**Enable structured output for production:**
- JSON format for machine-readability
- Consistent field names across services
- Disable in dev/test for human readability

**Configure log levels appropriately:**
- Avoid DEBUG globally in production (too verbose)
- ERROR for failures requiring intervention
- WARN for degraded but functional states
- INFO for significant business events

**Never log sensitive data:**
- No passwords, tokens, API keys
- No PII (personally identifiable information)
- No credit card numbers or payment details
- Sanitize user input before logging

**Always include context:**
- Request/correlation IDs
- User/session identifiers
- Operation/task names
- Timestamps (with timezone)

## MDC/Correlation ID Patterns

**MDC (Mapped Diagnostic Context)** adds correlation fields to all log messages
within a scope:

**Essential correlation fields:**
- **Request/Correlation ID** — unique ID for request, propagated across services
- **Instance ID** — identifies specific workflow/operation instance
- **Task ID** — identifies current step/task in multi-step operation
- **User ID** — identifies user making request (if authenticated)
- **Session ID** — groups requests in same session
- **Timestamp** — when operation started

**Pattern:**
1. Generate correlation ID at entry point (HTTP handler, message listener)
2. Store in MDC/context
3. Include in all log messages automatically
4. Propagate to downstream services via headers

**Querying by correlation:**
- Filter logs by correlation ID to see full request flow
- Track request across multiple services
- Debug issues by following single request end-to-end

## HTTP Header Propagation

**Propagate correlation IDs via HTTP headers:**
- Use standardized or documented header names
- Include in all outgoing HTTP requests
- Extract and use in downstream services
- Document header names for team/external consumers

**Common header names:**
- `X-Request-ID` / `X-Correlation-ID`
- `X-Session-ID`
- `X-User-ID` (if not sensitive)

**Pattern:**
1. Extract correlation ID from incoming request header
2. Store in MDC/context
3. Add to all outgoing HTTP requests
4. Enables end-to-end correlation across services

## Distributed Tracing Concepts

**OpenTelemetry (OTEL)** is the standard for distributed tracing:

**Core concepts:**
- **Span** — single operation with start/end time
- **Trace** — collection of spans representing full request
- **Service name** — identifies which service created span
- **Span attributes** — key-value metadata (user ID, operation type)
- **Span events** — timestamped annotations within span

**OTLP (OpenTelemetry Protocol):**
- Standard protocol for sending traces to collectors
- Configure exporter endpoint (Jaeger, Zipkin, Tempo, etc.)
- Set service name for identification

**Creating custom spans:**
- Add spans for significant business operations
- Include relevant attributes (entity IDs, operation types)
- Avoid over-instrumentation (only meaningful operations)
- Group related spans in same trace

**Correlation with logs:**
- Include trace ID in log MDC
- Search logs by trace ID
- Jump from trace to logs and vice versa

## Metrics Concepts

**Metrics types:**

**Counter** — monotonically increasing value:
- Total requests processed
- Total errors encountered
- Total items created

**Histogram** — distribution of values:
- Request duration
- Payload size
- Query execution time

**Gauge** — current value that can go up or down:
- Active connections
- Queue depth
- Memory usage

**Creating custom application metrics:**
- Instrument business-relevant operations
- Use consistent naming conventions (e.g., `service_operation_unit`)
- Include relevant labels (operation type, status, user type)
- Avoid high-cardinality labels (unique IDs as labels)

**Metrics endpoint exposure:**
- Expose metrics endpoint for scraping (e.g., `/metrics`, `/actuator/prometheus`)
- Secure endpoint or limit to internal network
- Document metrics format and naming

## Production Configuration Checklist

**Logging:**
- ✅ Structured logging enabled (JSON output)
- ✅ Appropriate log levels set (INFO default, DEBUG off)
- ✅ Correlation fields configured (request ID, user ID, task ID)
- ✅ Sensitive data exclusion verified

**Tracing:**
- ✅ Distributed tracing enabled
- ✅ OTLP exporter configured with collector endpoint
- ✅ Service name set appropriately
- ✅ Custom spans added for business operations
- ✅ Header propagation configured for downstream calls

**Metrics:**
- ✅ Metrics collection enabled
- ✅ Metrics endpoint exposed
- ✅ Custom business metrics instrumented
- ✅ Metric naming conventions followed

---

## Querying Observability Data

**Log aggregators** (Kibana, Loki, Datadog, Splunk):
- Filter by correlation ID to see request flow
- Search by error messages or stack traces
- Group by service/operation for error rates
- Time-range filtering for incident investigation

**Trace viewers** (Jaeger, Zipkin, Tempo):
- Search by trace ID or service name
- View request latency breakdown
- Identify slow operations
- Understand service dependencies

**Metrics dashboards** (Grafana, Prometheus):
- Graph request rate, error rate, duration (RED metrics)
- Alert on metric thresholds
- Visualize trends over time
- Compare before/after deployments

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Missing structured logging config | Logs unparseable by aggregators | Enable JSON output for production |
| Disabled tracing in production | Can't debug performance issues | Enable tracing, configure sampling if needed |
| Broken header propagation | Correlation lost between services | Test header propagation end-to-end |
| Collector connectivity issues | Traces/metrics lost silently | Monitor exporter errors, use fallback |
| Logging sensitive data | Security/privacy violation | Sanitize logs, never log passwords/PII |
| Unstructured log format | Can't query/filter effectively | Use structured logging with consistent fields |
| Missing correlation IDs | Can't trace requests across services | Implement MDC and header propagation |
| High-cardinality labels in metrics | Metrics explosion, performance issues | Use low-cardinality labels only |
| Over-instrumentation | Performance overhead, noise | Instrument significant operations only |
| Debug logs in production | Log volume explosion | Set INFO as default level |

---

## Skill Chaining

Framework-specific observability skills (`quarkus-observability` for Quarkus,
`python-observability`, `go-observability`, etc.) implement these principles
with framework-specific configuration, APIs, and instrumentation.
