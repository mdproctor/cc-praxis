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

## Task DSL Quick Reference

Common task patterns (full API reference in `funcDSL-reference.md`):

| Pattern | Quick Example |
|---------|---------------|
| **Function call** | `function(svc::process, Request.class)` |
| **Named task** | `function("step1", svc::process, Request.class)` |
| **Agent** | `agent("drafter", ai::draft, String.class)` |
| **Data extraction** | `.inputFrom("$.cart.items")` |
| **Result transform** | `.outputAs("{ status: ., processed: true }")` |
| **Context merge** | `.exportAs((result, ctx) -> merge(result, ctx), Type.class)` |
| **Branching** | `switchWhenOrElse(pred, "yesStep", "noStep", Type.class)` |
| **Emit event** | `emitJson("org.acme.event.type", Data.class)` |
| **Wait for event** | `listen("wait", toOne("org.acme.done"))` |
| **HTTP call** | `get("https://api.example.com/resource")` |
| **Iteration** | `forEach(ctx -> ctx.items(), inner -> ...)` |
| **Side effect** | `consume("log", data -> logger.info(...), Type.class)` |

**Key rule**: Name tasks you branch to. Keep transformations close to the task that needs them.

See **funcDSL-reference.md** for complete examples and all patterns.

---

## Testing

For comprehensive testing patterns (unit tests, YAML workflow tests, REST
integration tests, AI service mocking), use the **quarkus-flow-testing** skill.

Quick test example:
~~~java
@QuarkusTest
class MyWorkflowTest {
    @Inject MyWorkflow workflow;

    @Test
    void should_complete() throws Exception {
        var result = workflow.instance(Map.of("input", "value"))
            .start().toCompletableFuture().get(5, TimeUnit.SECONDS);
        assertThat(result.asMap().orElseThrow().get("output"))
            .isEqualTo("expected");
    }
}
~~~

**Note**: blocking with `.get()` is OK in tests, never in production.

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

- When implementing a new workflow: apply `java-dev` rules for safety and
  concurrency, then this skill for DSL patterns.
- When writing tests: use **quarkus-flow-testing** for testing patterns.
- When done: invoke **code-review** before committing.
- When committing: invoke **java-git-commit** (which chains **update-design**).
- If the workflow represents a significant architectural addition, ensure
  **update-design** captures it in DESIGN.md even outside of a commit.