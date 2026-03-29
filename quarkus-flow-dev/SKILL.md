---
name: quarkus-flow-dev
description: >
  Use this skill for all development tasks involving quarkus-flow workflows,
  agentic AI pipelines, and LangChain4j integration. Triggers on: writing or
  editing a Flow subclass, working with the FuncDSL, defining tasks with
  function/agent/emit/listen/switchWhen/forEach/http/openapi, writing workflow
  tests with @QuarkusTest, injecting WorkflowDefinition or Flow beans, working
  with YAML workflow definitions, or when the user mentions "workflow", "flow",
  "agent", "HITL", "human-in-the-loop", "agentic", "LangChain4j", or
  "serverless workflow". Always applies in addition to java-dev, not instead
  of it.
---

# Quarkus Flow Development

You are an expert in quarkus-flow, the CNCF Serverless Workflow engine for
Quarkus. This skill extends java-dev with quarkus-flow-specific patterns,
conventions, and pitfalls.

## Core Concepts

### Workflow class structure

All workflows extend `io.quarkiverse.flow.Flow`, are `@ApplicationScoped`
CDI beans, and override `descriptor()`. They are **discovered at build time**
— no manual registration needed.

~~~java
import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.*;
import static io.serverlessworkflow.fluent.func.spec.FuncWorkflowBuilder.workflow;

@ApplicationScoped
public class MyWorkflow extends Flow {
    @Override
    public Workflow descriptor() {
        return workflow("my-workflow")
            .tasks(/* ... */)
            .build();
    }
}
~~~

### Key imports (always use static imports for brevity)

~~~java
import io.serverlessworkflow.api.types.Workflow;
import io.serverlessworkflow.fluent.func.spec.FuncWorkflowBuilder;
import static io.serverlessworkflow.fluent.func.dsl.FuncDSL.*;
import static io.serverlessworkflow.fluent.func.spec.FuncWorkflowBuilder.workflow;
~~~

### Injecting workflows

~~~java
// Inject a Java DSL workflow by class
@Inject
MyWorkflow workflow;

// Inject a YAML-defined workflow by identifier
@Inject
@Identifier("flow:echo-name")  // namespace:name from the YAML document section
WorkflowDefinition definition;
~~~

---

## Task DSL Patterns

### Calling Java methods

~~~java
// Simple function call (input type inferred)
function(myService::process)

// Explicit input type
function(myService::process, ProcessRequest.class)

// Named (required when branching to this task)
function("processStep", myService::process, ProcessRequest.class)

// With workflow context (payload + context)
withContext((payload, ctx) -> svc.run(ctx, payload), Input.class)

// Agent call — uses unique id as memory id (for LangChain4j AI services)
agent("draftAgent", drafterAgent::draft, String.class)

// Agent with instance id (stateful agents, HITL loops)
withInstanceId((id, prompt) -> agent.run(id, prompt), Prompt.class)
~~~

### Data flow: inputFrom / outputAs / exportAs

~~~java
// Extract a slice of the context as input
function(pricing::quote, QuoteRequest.class)
    .inputFrom("$.cart.quoteRequest")

// Transform the task result before merging
function(nlp::classify, Text.class)
    .outputAs("{ sentiment: ., reviewed: false }")

// Merge result back into global context
agent("draftNewsletter", drafter::draft, Draft.class)
    .exportAs((draft, wfCtx) -> {
        var current = (NewsletterContext) wfCtx.currentData();
        return current.withDraft(draft);
    }, Draft.class)
~~~

**Rule**: keep transformations close to the step that needs them. Don't
use global context mutations when a targeted `exportAs` will do.

### Branching

~~~java
// Single condition
switchWhen(".score >= 80", "sendStep")

// Typed predicate + else
switchWhenOrElse(
    (HumanReview h) -> h.needsRevision(),
    "reviseStep",
    "sendStep",
    HumanReview.class
)

// Typed predicate + directive (END, CONTINUE, etc.)
switchWhenOrElse(
    (HumanReview h) -> h.approved(),
    "sendStep",
    FlowDirectiveEnum.END,
    HumanReview.class
)
~~~

### Events (emit / listen)

~~~java
// Emit a JSON CloudEvent
emitJson("org.acme.newsletter.review.required", Review.class)

// Wait for a single event (HITL pattern)
listen("waitHuman", toOne("org.acme.review.done"))
    .outputAs((Collection<Object> c) -> c.iterator().next())

// Wait for any of several events
listen(toAny("org.acme.approved", "org.acme.rejected"))
~~~

### HTTP and OpenAPI tasks

~~~java
// Fluent HTTP GET
get("https://service/api/resource")

// Named GET (required if you branch to it)
get("fetchUser", "https://service/users/" + id)

// POST with body
post(Map.of("name", "Ricardo"), "https://service/users")

// OpenAPI call
call(openapi()
    .document("https://petstore3.swagger.io/api/v3/openapi.json")
    .operation("findPetById"))
~~~

### Side effects and iteration

~~~java
// Fire-and-forget (no result merged to context)
consume("sendEmail",
    (HumanReview r) -> mailService.send("to@acme.com", "Subject", r.draft()),
    HumanReview.class
)

// Iterate over a collection
forEach(order -> order.items(),
    inner -> inner.tasks(
        function(inventoryService::reserve, Item.class)
    )
)
~~~

---

## Testing Workflows

### Unit test (inject and execute directly)

~~~java
@QuarkusTest
class MyWorkflowTest {

    @Inject
    MyWorkflow workflow;

    @Test
    void should_produce_expected_output() throws Exception {
        WorkflowModel result = workflow.instance(Map.of("input", "value"))
            .start()
            .toCompletableFuture()
            .get(5, TimeUnit.SECONDS);

        assertThat(result.asMap().orElseThrow().get("output"))
            .isEqualTo("expected");
    }
}
~~~

**Note**: blocking with `.get()` or `.join()` is acceptable in tests.
Never block the event loop in production code.

### Test a YAML workflow

~~~java
@QuarkusTest
class EchoYamlWorkflowTest {

    @Inject
    @Identifier("flow:echo-name")
    WorkflowDefinition definition;

    @Test
    void should_echo_name() throws Exception {
        WorkflowModel result = definition.instance(Map.of("name", "Joe"))
            .start()
            .toCompletableFuture()
            .get(5, TimeUnit.SECONDS);

        assertThat(result.asMap().orElseThrow().get("message"))
            .isEqualTo("echo: Joe");
    }
}
~~~

### Integration test via REST (REST Assured)

~~~java
@QuarkusTest
class MyResourceTest {

    @Test
    void should_trigger_workflow_via_http() {
        given()
            .queryParam("name", "John")
        .when()
            .get("/my-endpoint")
        .then()
            .statusCode(200)
            .body("message", equalTo("Hello, John!"));
    }
}
~~~

### Test HTTP error mapping (RFC 7807)

~~~java
@Test
void should_map_workflow_exception_to_problem_details() {
    given()
        .queryParam("customerId", "unauthorized")
    .when()
        .get("/customer/profile")
    .then()
        .statusCode(401)
        .body("type", equalTo(
            "https://serverlessworkflow.io/spec/1.0.0/errors/communication"))
        .body("status", equalTo(401));
}
~~~

**Important**: your JAX-RS resource must be **reactive** (return `Uni` or
`CompletionStage`) for automatic error mapping to work. Blocking with
`.await().indefinitely()` wraps the error in `ExecutionException` and
breaks the mapper.

### Enable tracing in tests

~~~properties
# application.properties
%test.quarkus.flow.tracing.enabled=true
~~~

### Mock AI agents in tests

Always mock LangChain4j AI services in unit/integration tests to avoid
flaky tests from network calls and non-deterministic LLM responses. Use
`@InjectMock` or a `@QuarkusTestProfile` that substitutes a stub bean.

---

## Common Pitfalls

| Mistake | Correct approach |
|---|---|
| Unnamed task used as branch target | Always name tasks you `switchWhen*` to |
| Blocking event loop in a `function` task | Annotate with `@Blocking` or dispatch via `executeBlocking` |
| Using `outputAs` when you mean `exportAs` | `outputAs` transforms the task result; `exportAs` merges into global context — don't confuse them |
| Forgetting `@Identifier` when injecting YAML workflow | YAML workflows need `@Identifier("flow:<name>")` to resolve |
| Blocking in REST resource | Resource must return `Uni`/`CompletionStage` for error mapping to work |
| Using Mockito to mock AI services | Prefer stub CDI beans or `@InjectMock`; keep tests deterministic |
| Mutable shared state in a `Flow` subclass | `Flow` beans are `@ApplicationScoped` — treat as stateless; all state belongs in the workflow context |

---

## HITL (Human-in-the-loop) Pattern

The standard HITL loop in quarkus-flow:

~~~java
workflow("review-loop")
    .tasks(
        // 1. Do work
        agent("draftAgent", drafter::draft, String.class)
            .inputFrom("$.seedPrompt")
            .exportAs("{ draft: . }"),

        // 2. Notify human
        emitJson("org.acme.review.required", Draft.class),

        // 3. Wait for human decision
        listen("waitHuman", toOne("org.acme.review.done"))
            .outputAs((Collection<Object> c) -> c.iterator().next()),

        // 4. Branch on outcome
        switchWhenOrElse(
            (HumanReview h) -> h.needsRevision(),
            "draftAgent",          // loop back
            "finalizeStep",
            HumanReview.class
        ),

        // 5. Final action
        consume("finalizeStep",
            (HumanReview r) -> mailService.send("out@acme.com", "Done", r.draft()),
            HumanReview.class
        )
    )
    .build()
~~~

---

## Skill chaining

- When implementing a new workflow: apply `java-dev` rules for safety,
  concurrency, and testing, then apply this skill for DSL patterns.
- When done: invoke `code-review` before committing.
- When committing: invoke `java-git-commit` (which chains `update-design`).
- If the workflow represents a significant architectural addition, ensure
  `update-design` captures it in DESIGN.md even outside of a commit.