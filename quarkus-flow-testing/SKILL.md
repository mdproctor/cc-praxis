---
name: quarkus-flow-testing
description: >
  Use when writing or debugging tests for quarkus-flow workflows. Triggers on:
  creating @QuarkusTest for Flow classes, testing YAML workflows, writing REST
  integration tests for workflow endpoints, mocking AI agents in tests, debugging
  workflow test failures, or when the user mentions "test workflow", "workflow
  test", "mock agent", or "@QuarkusTest". Always applies alongside java-dev for
  general testing practices.
---

# Quarkus Flow Testing Patterns

Expert testing patterns for quarkus-flow workflows, covering unit tests,
integration tests, and AI service mocking.

## Prerequisites

**This skill builds on [`java-dev`] and [`quarkus-flow-dev`]**.

Apply all rules from:
- **`java-dev`**: Testing practices (JUnit 5, AssertJ, real CDI over mocking, @QuarkusTest patterns)
- **`quarkus-flow-dev`**: Workflow structure, DSL patterns, and quarkus-flow concepts

Then apply the workflow-specific testing patterns below.

## Quick Reference

| Test Type | Annotation | When to Use |
|-----------|------------|-------------|
| **Unit test** | `@QuarkusTest` | Test workflow logic with injected Flow |
| **YAML test** | `@QuarkusTest` + `@Identifier` | Test YAML-defined workflows |
| **REST integration** | `@QuarkusTest` + REST Assured | Test workflow via HTTP endpoints |
| **Error mapping** | `@QuarkusTest` + REST Assured | Verify RFC 7807 problem details |
| **Mock AI services** | `@InjectMock` or `@QuarkusTestProfile` | Avoid flaky LLM tests |

## Unit Test (Inject and Execute Directly)

```java
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
```

**Note**: blocking with `.get()` or `.join()` is acceptable in tests.
Never block the event loop in production code.

## Test YAML Workflow

```java
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
```

## Integration Test via REST (REST Assured)

```java
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
```

## Test HTTP Error Mapping (RFC 7807)

```java
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
```

**Important**: your JAX-RS resource must be **reactive** (return `Uni` or
`CompletionStage`) for automatic error mapping to work. Blocking with
`.await().indefinitely()` wraps the error in `ExecutionException` and
breaks the mapper.

## Enable Tracing in Tests

```properties
# application.properties
%test.quarkus.flow.tracing.enabled=true
```

Useful for debugging workflow execution flow in test failures.

## Mock AI Agents in Tests

Always mock LangChain4j AI services in unit/integration tests to avoid
flaky tests from network calls and non-deterministic LLM responses.

### Option 1: @InjectMock (Simple)

```java
@QuarkusTest
class AIDrivenWorkflowTest {

    @InjectMock
    MyAIService aiService;

    @Test
    void should_process_with_mocked_ai() {
        when(aiService.generateResponse(any()))
            .thenReturn("mocked response");

        // Test workflow that uses aiService
    }
}
```

### Option 2: @QuarkusTestProfile (Complex Stubbing)

```java
public class MockedAIProfile implements QuarkusTestProfile {
    @Override
    public Map<String, String> getConfigOverrides() {
        return Map.of("quarkus.langchain4j.mock", "true");
    }

    @TestProfile.List
    public static class Beans {
        @Produces
        @ApplicationScoped
        public MyAIService mockAIService() {
            return new MyAIService() {
                @Override
                public String generate(String prompt) {
                    return "deterministic test response";
                }
            };
        }
    }
}

@QuarkusTest
@TestProfile(MockedAIProfile.class)
class WorkflowWithAITest {
    // Tests using mocked AI service
}
```

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Blocking `.await().indefinitely()` in resource | Breaks error mapping, wraps in ExecutionException | Return `Uni` or `CompletionStage` from JAX-RS resource |
| Calling real LLM API in tests | Flaky, slow, non-deterministic | Use `@InjectMock` or `@QuarkusTestProfile` stub |
| Testing with `@QuarkusTest` but no assertions on result | Test passes even if workflow fails silently | Assert on `result.asMap()` or specific fields |
| Forgetting `@Identifier` for YAML workflow | Injection fails with "bean not found" | Add `@Identifier("flow:namespace:name")` |
| Using short timeout on `.get(timeout)` | Flaky failures on slow CI | Use 5-10 seconds minimum, or no timeout in tests |
| Testing workflow without enabling tracing | Hard to debug failures | Set `%test.quarkus.flow.tracing.enabled=true` |
| Not testing error paths | Assumes workflows always succeed | Add tests for validation failures, external service errors |

## Skill Chaining

**Invoked by:** [`quarkus-flow-dev`] when writing or debugging tests for quarkus-flow workflows

**Invokes:** [`java-code-review`] before committing, [`java-git-commit`] when ready to commit

**Can be invoked independently:** User writes @QuarkusTest for Flow classes, tests YAML workflows, or debugs workflow test failures
