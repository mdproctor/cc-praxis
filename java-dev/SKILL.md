---
name: java-dev
description: >
  Use this skill for all Java development and debugging tasks in Claude Code,
  targeting Quarkus server-side applications running in the cloud. Triggers on:
  writing new Java classes or methods, fixing Java bugs, refactoring Java code,
  reviewing Java code for correctness or performance, adding tests, or any task
  involving .java, pom.xml, or build.gradle files. Also triggers when the user
  says "implement", "fix", "refactor", "review", or "add tests" in a Java/Quarkus
  project context. When a task also involves committing, chain with the
  java-git-commit skill.
---

## Quick Reference

| Category | Rule | How to Apply |
|----------|------|--------------|
| **Safety** | Resource leaks | Always use try-with-resources for Closeable |
| | Deadlocks | Document lock ordering; minimize critical sections |
| | Classloader leaks | Remove ThreadLocal values in finally |
| | Silent corruption | Never swallow exceptions; log or rethrow |
| **Concurrency** | Thread model | Prefer thread-local or event-loop over shared state |
| | Vert.x integration | Never block I/O thread; use @Blocking annotation |
| | Single-threaded code | Add `// NOT thread-safe` comment |
| **Performance** | Hot paths | Avoid streams, boxing, allocations in tight loops |
| | Measuring | Profile before optimizing; don't pre-optimize cold code |
| **Testing** | Framework | JUnit 5 + AssertJ + QuarkusTest |
| | Mocking | Prefer real CDI/in-memory over Mockito |
| | Integration tests | Use real database, not mocks |
| **Code Quality** | Mutability | Mark new parameters/variables `final` unless mutated |
| | Imports | Use simple names with imports, not FQNs |
| | Documentation | Javadoc only for non-trivial methods; focus on why |
| | Changes | Minimize line changes; don't reformat untouched code |

## Rule Priority Flow

```dot
digraph rule_priority {
    "Writing code" [shape=doublecircle];
    "Safety violation?" [shape=diamond];
    "Apply Safety rules" [shape=box, style=filled, fillcolor=red];
    "Concurrency issue?" [shape=diamond];
    "Apply Concurrency rules" [shape=box, style=filled, fillcolor=orange];
    "Performance-critical path?" [shape=diamond];
    "Apply Performance rules" [shape=box, style=filled, fillcolor=yellow];
    "Apply Code Quality rules" [shape=box, style=filled, fillcolor=lightblue];
    "Code complete" [shape=doublecircle];

    "Writing code" -> "Safety violation?";
    "Safety violation?" -> "Apply Safety rules" [label="yes (NEVER compromise)"];
    "Safety violation?" -> "Concurrency issue?" [label="no"];
    "Apply Safety rules" -> "Code complete";

    "Concurrency issue?" -> "Apply Concurrency rules" [label="yes (shared state/threading)"];
    "Concurrency issue?" -> "Performance-critical path?" [label="no"];
    "Apply Concurrency rules" -> "Code complete";

    "Performance-critical path?" -> "Apply Performance rules" [label="yes (hot path/tight loop)"];
    "Performance-critical path?" -> "Apply Code Quality rules" [label="no (cold path)"];
    "Apply Performance rules" -> "Code complete";
    "Apply Code Quality rules" -> "Code complete";
}
```

**Priority order:** Safety > Concurrency > Performance > Code Quality

## Why These Rules Matter

**Resource leaks:** A production Quarkus service leaked 50 file descriptors per hour from unclosed HTTP connections. The limit of 1024 was exhausted in 20 hours, causing cascading failures. Kubernetes restarted the pod daily. The fix: one missing try-with-resources block.

**Deadlocks:** Thread dump showed lock ordering violation between cache update and event publishing. Service hung for 3 hours during peak traffic. Fix required documenting lock acquisition order in comments and refactoring to minimize critical sections.

**Classloader leaks:** ThreadLocal values holding references to request-scoped beans prevented classloader garbage collection after hot redeployments. Memory grew 200MB per deployment. After 10 deployments in development, OutOfMemoryError crashed the JVM. Fix: explicit ThreadLocal.remove() in finally blocks.

**Silent corruption:** Exception swallowed in event handler caused payment records to be marked "processed" without actually processing them. Discovered 3 days later when customer complained. 1,200 transactions lost. Fix: log exception and set error flag instead of swallowing.

**Blocking on event loop:** Synchronous database call in Vert.x event loop handler blocked all concurrent requests. Single slow query (5 seconds) froze entire service. 503 errors cascaded to all endpoints. Fix: `@Blocking` annotation on handler method.

**Premature optimization:** Developer used primitive arrays and manual indexing "for performance" in config parser (called once at startup). Introduced off-by-one bug that corrupted plugin loading. Cost: 4 hours debugging. Config parser is not a hot path.

These are real incidents. The rules exist because the pain is real.

## Safety

Our code is deployed in mission-critical scenarios. Never compromise on:
- Resource leaks (file descriptors, memory, connections)
- Deadlocks or livelock
- Classloader leaks
- Silent data corruption

**Resource leaks:**
~~~java
// ❌ BAD: Stream not closed if exception thrown
FileInputStream fis = new FileInputStream(path);
byte[] data = fis.readAllBytes();
fis.close();  // Never reached if readAllBytes() throws

// ✅ GOOD: Guaranteed cleanup
try (FileInputStream fis = new FileInputStream(path)) {
    byte[] data = fis.readAllBytes();
}
~~~

**Classloader leaks:**
~~~java
// ❌ BAD: ThreadLocal never removed, holds classloader reference
ThreadLocal<RequestContext> context = new ThreadLocal<>();
context.set(new RequestContext());
// ... use it ...
// Classloader can't be GC'd after hot reload

// ✅ GOOD: Explicit cleanup
ThreadLocal<RequestContext> context = new ThreadLocal<>();
try {
    context.set(new RequestContext());
    // ... use it ...
} finally {
    context.remove();  // Releases classloader reference
}
~~~

**Silent data corruption:**
~~~java
// ❌ BAD: Exception swallowed, order marked complete incorrectly
try {
    processPayment(order);
    order.setStatus(COMPLETE);
} catch (Exception e) { }  // Payment failed but order shows complete

// ✅ GOOD: Log and propagate
try {
    processPayment(order);
    order.setStatus(COMPLETE);
} catch (Exception e) {
    LOG.error("Payment failed for order {}", order.getId(), e);
    order.setStatus(FAILED);
    throw e;
}
~~~

When a violation of these rules is detected in existing code, output a
**CRITICAL SAFETY WARNING** block with:
- The specific risk (e.g. "potential deadlock between locks A and B")
- The technical context (code path, thread model)
- Actionable fix suggestions

Emit runtime warnings in code when assumption violations can be detected at
runtime. Warning messages must be actionable, not generic.

## Reproducibility

Prefer deterministic behaviour. In non-performance-critical code (build tools,
bootstrap, configuration), prefer sorted structures over hash-based ones to
avoid ordering non-determinism.

In performance-critical runtime paths, efficiency takes precedence over
reproducibility — but document the tradeoff explicitly.

Security requirements (e.g. salted data structures) always take precedence.
Document the reason when security or correctness drives a structural decision.

**When to ask**: if it's unclear whether code is build-time or runtime-critical,
ask before proceeding.

## Concurrency

Most of our state is confined to a single thread. Prefer thread-local storage
or event-loop patterns over shared-state concurrency. This aligns with
Quarkus's Vert.x event-loop model — avoid blocking the I/O thread.

**Single-threaded code:**
~~~java
// ❌ BAD: No indication of thread model
public class EventProcessor {
    private List<Event> buffer = new ArrayList<>();  // Is this shared?

    public void add(Event e) {
        buffer.add(e);
    }
}

// ✅ GOOD: Explicit thread model
public class EventProcessor {
    // NOT thread-safe — designed for single-threaded use only
    private List<Event> buffer = new ArrayList<>();

    public void add(Event e) {
        buffer.add(e);
    }
}
~~~

**Blocking on event loop:**
~~~java
// ❌ BAD: JDBC call blocks event loop thread
@Path("/orders")
public class OrderResource {
    public Order create(OrderRequest req) {
        return orderRepo.persist(req);  // Blocks I/O thread
    }
}

// ✅ GOOD: Dispatched to worker thread
@Path("/orders")
public class OrderResource {
    @Blocking  // Runs on worker thread
    public Order create(OrderRequest req) {
        return orderRepo.persist(req);
    }
}
~~~

Always establish whether code is single- or multi-threaded before writing it.
Minimize critical sections. When they are unavoidable: document the lock
ordering, the invariants being protected, and any tradeoffs made.

## Performance

This codebase targets cloud-hosted Quarkus services where efficiency matters
at scale. Be mindful of allocations and GC pressure.

**Hot path optimization:**
~~~java
// ❌ BAD: Stream overhead in per-request path
@Path("/items")
public List<String> getActive() {
    return items.stream()
        .filter(Item::isActive)
        .map(Item::getName)
        .collect(Collectors.toList());
}

// ✅ GOOD: Simple loop for hot path
@Path("/items")
public List<String> getActive() {
    List<String> result = new ArrayList<>(items.size());
    for (Item item : items) {
        if (item.isActive()) {
            result.add(item.getName());
        }
    }
    return result;
}
~~~

**Avoid unnecessary boxing:**
~~~java
// ❌ BAD: Boxing creates GC pressure
List<Integer> counts = getCounts();
int sum = 0;
for (Integer count : counts) {  // Boxing/unboxing
    sum += count;
}

// ✅ GOOD: Primitives when possible
int[] counts = getCounts();
int sum = 0;
for (int count : counts) {
    sum += count;
}
~~~

- For hot paths, measure before optimizing — don't pre-optimize cold code

**What counts as performance-critical**: tight loops, per-request processing,
and any code path called at high frequency. Config parsing, startup code, and
build-time logic are generally not critical — use idiomatic Java there.

## Code duplication

Before writing new helpers or utilities, check for existing code that can be
reused. Prefer extension or composition over duplication.

## Code clarity

- Mark parameters and variables `final` in new code unless mutability is required
- Omit `this.` prefix unless required for disambiguation (e.g. constructor
  field assignments)
- Use simple class names with imports rather than fully qualified names, unless
  two classes share the same simple name in the same file

## Testing

Preferred stack:
- **JUnit 5** — the standard test runner
- **AssertJ** — for fluent, readable assertions (used directly in quarkus-flow)
- **MockServer / MockWebServer** — for HTTP-level mocking of external services;
  prefer these over Mockito for integration scenarios involving HTTP dependencies
- **`@QuarkusTest`** — starts the full CDI container; use for any test that
  needs injection, lifecycle, or framework behaviour
- **`@QuarkusIntegrationTest`** — black-box testing against a built jar or
  native image; use for end-to-end validation
- **`@QuarkusComponentTest`** — lightweight CDI component testing without
  starting the full application; prefer over `@QuarkusTest` when testing a
  single bean in isolation

Prefer real CDI wiring in tests over mocking. Reach for Mockito only when
a dependency genuinely cannot be substituted with a real or in-memory
implementation.

Strive for a fully automated integration test. If impractical, discuss with
the user before skipping it.

Add unit tests for classes with complex logic or data transformations. Skip
unit tests when they only duplicate integration test coverage and create
excessive coupling.

## Documentation

Add Javadoc and comments only on non-trivial methods. Keep them brief.
Focus on *why* and *tradeoffs*, not *what* (the code shows what).

Choose class names carefully. When in doubt, propose 2–3 options before
proceeding.

Do not add `@author` tags unless explicitly requested.

## Minimize changes

Keep modified lines to a minimum to reduce conflicts and ease review:
- Do not alter existing method signatures unless semantically necessary
- Do not reformat lines that don't need changing — respect existing conventions
- Do not add `final` to existing method signatures (new code only)
- Do not change whitespace or imports in lines you're not otherwise touching

## Refactoring

When refactoring, use the **IntelliJ MCP if available** — it gives a
project-wide view of impact and is faster for large-scale changes.

If IntelliJ MCP is unavailable:
1. Inform the user
2. Ask: continue with Bash-based tools, or start IntelliJ MCP first?
3. If continuing without it: use `git diff` to validate scope, make changes
   conservatively, and run the build/tests after each logical step

## Compilation and errors

When IntelliJ MCP is available, use it for project-wide error detection
alongside your own analysis. Prefer it when it's faster — but never let it
substitute for catching compilation errors you can see directly.

## Common Pitfalls — These Thoughts Mean STOP

If you catch yourself thinking any of these, **STOP** and apply the correct approach:

| Rationalization | Problem | Impact | Fix |
|-----------------|---------|--------|-----|
| "Resource will close automatically" | Missing try-with-resources | FD exhaustion after 20hrs | Wrap in try-with-resources |
| "This is single-threaded, no sync needed" | Undocumented thread model | Future bugs when threading added | Add `// NOT thread-safe` comment |
| "I'll add the test after I finish this" | No test coverage | Gaps never get filled | Add integration test now |
| "This is performance-critical, streams are too slow" | Premature optimization | Bugs from complex code | Measure first with profiler |
| "Just this once I'll catch and ignore the exception" | Swallowed exception | Silent failures, lost data | Log exception or rethrow |
| "I know this blocks, but it's quick" | Blocking event loop | Cascading 503 errors | Use @Blocking annotation |
| "ThreadLocal cleanup isn't critical here" | Classloader leak | OOM after 10 deployments | Remove in finally block |
| "The lock order doesn't matter for this simple case" | Undocumented lock order | Deadlock when code grows | Document ordering now |
| "This allocation is trivial" | Boxing in hot loop | GC pressure, latency spikes | Use primitive types |
| "I'll use HashMap, order doesn't matter" | Non-deterministic ordering | Build flakiness | Use LinkedHashMap/TreeMap |
| "Mockito is faster than a real test database" | Mocked database | Mock/prod drift, broken prod | Use @QuarkusTest + real DB |
| "Let me refactor this code I haven't read yet" | Refactoring unknown code | Breaking working functionality | Read and understand first |

## Skill Chaining

- **Before committing:** invoke **java-code-review** to catch safety, concurrency, and performance issues
- **After implementing or refactoring:** if the user wants to commit, invoke
  **java-git-commit**, which will also sync DESIGN.md via **update-design**
- **For architectural decisions:** suggest running **adr** to document significant decisions
- **For logging/observability setup:** invoke **quarkus-observability** when implementing structured logging, tracing, or metrics
- **For security-critical code:** invoke **java-security-audit** when handling authentication, authorization, payment, or PII
- **If architectural impact without commit:** suggest running **update-design** independently