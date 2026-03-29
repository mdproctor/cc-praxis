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

## Skill chaining

- After implementing or refactoring, if the user wants to commit: invoke
  **java-git-commit**, which will also sync DESIGN.md via **update-design**.
- If a change has significant architectural impact and no commit is planned,
  suggest running **/update-design** independently.