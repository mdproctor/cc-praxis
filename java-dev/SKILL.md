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

If code is intended for a single-threaded hot loop, add a comment:
~~~java
// NOT thread-safe — designed for single-threaded use only
~~~

Always establish whether code is single- or multi-threaded before writing it.
Minimize critical sections. When they are unavoidable: document the lock
ordering, the invariants being protected, and any tradeoffs made.

## Performance

This codebase targets cloud-hosted Quarkus services where efficiency matters
at scale. Be mindful of allocations and GC pressure.

- Avoid `java.util.stream` and functional overhead in performance-critical paths
- Prefer primitive collections or arrays over boxed wrapper types to reduce GC
  pressure
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

## Red Flags — These Thoughts Mean STOP

If you catch yourself thinking any of these, **STOP** and apply the correct approach:

| Rationalization | Reality |
|-----------------|---------|
| "Resource will close automatically" | Not without try-with-resources or explicit finally. Add it now. |
| "This is single-threaded, no sync needed" | Document it with `// NOT thread-safe` comment or future-you will forget. |
| "I'll add the test after I finish this" | Test coverage gaps never get filled. Add integration test now. |
| "This is performance-critical, streams are too slow" | Measure first. Don't pre-optimize without profiling data. |
| "Just this once I'll catch and ignore the exception" | Silent failures cause production mysteries. Log it or rethrow. |
| "I know this blocks, but it's quick" | Blocking Vert.x event loop causes cascading failures. Use @Blocking. |
| "ThreadLocal cleanup isn't critical here" | Classloader leaks accumulate slowly then crash. Always clean up. |
| "The lock order doesn't matter for this simple case" | Simple cases become complex. Document lock ordering now. |
| "This allocation is trivial" | In a hot loop, trivial allocations cause GC pressure. Use primitives. |
| "I'll use HashMap, order doesn't matter" | If it's build-time code, order matters. Use LinkedHashMap or TreeMap. |
| "Mockito is faster than a real test database" | Mocks drift from reality. Use @QuarkusTest with real DB. |
| "Let me refactor this code I haven't read yet" | Read first, understand, then refactor. Don't break working code. |

## Skill chaining

- After implementing or refactoring, if the user wants to commit: invoke
  **java-git-commit**, which will also sync DESIGN.md via **update-design**.
- If a change has significant architectural impact and no commit is planned,
  suggest running **/update-design** independently.