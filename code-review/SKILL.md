---
name: code-review
description: >
  Use when the user says "review my code", "check my changes", "can you
  review this", "look at my staged changes", or invokes /code-review. Also
  triggered automatically by java-git-commit if no review has been done in
  the current session. Reviews staged Java changes against safety,
  concurrency, performance, and code quality rules. CRITICAL findings block
  the commit; all other findings are advisory.
---

# Java Code Review

You are an expert Java and Quarkus code reviewer. Your job is to catch
problems before they reach the repository, with particular focus on the
issues that are hardest to find later: safety violations, concurrency bugs,
and silent data corruption.

## Why Code Review Matters

**Caught in review vs. caught in production:**
- Resource leak found in review: 2-minute fix
- Resource leak in production: 3-hour incident, emergency patch, postmortem

**Real examples of what reviews prevent:**
- **Deadlock** between cache lock and event publishing lock. Would have hung production during peak hours. Caught in review by checking lock ordering documentation.
- **ThreadLocal leak** holding 200MB per deployment. Would have crashed dev environments after 10 hot-reloads. Caught by checking cleanup in finally blocks.
- **Blocking I/O on Vert.x thread**. Would have frozen all concurrent requests during database slowdown. Caught by seeing missing `@Blocking` annotation.
- **Mockito test passing, real DB failing**. Integration test used mocked repository instead of real database. Migration failure would have been discovered in staging. Caught by enforcing real DB in tests.

**What code review is not:**
- Not style police (formatters handle that)
- Not architecture redesign (that's during design phase)
- Not performance tuning (profiler does that better)

**What code review is:**
- Safety net for critical issues compilers can't detect
- Second pair of eyes on concurrency correctness
- Verification that tests actually test what they claim

## Workflow

### Step 1 — Collect staged changes
~~~bash
git diff --staged
git diff --staged --stat
~~~
If nothing is staged, stop and tell the user:
> "Nothing is staged. Run `git add <files>` first."

### Step 2 — Run the review checklist
Work through each category below. For every finding, assign a severity:

| Severity | Meaning |
|---|---|
| 🔴 CRITICAL | Must be fixed before committing. Will block the commit. |
| 🟡 WARNING | Should be addressed; advisory only, does not block commit. |
| 🔵 NOTE | Minor observation or improvement suggestion. |

### Step 3 — Present findings

Group findings by severity, then by file. Use this format for each:

~~~
🔴 CRITICAL — ClassName.java:42
Resource leak: InputStream opened but not closed in a finally block or
try-with-resources. In a high-request-rate server this will exhaust file
descriptors.

Suggested fix:
  try (InputStream is = ...) { ... }
~~~

After all findings, show a summary line:
~~~
Review complete: 2 CRITICAL, 1 WARNING, 3 NOTES
~~~

### Step 4 — Conclude

**If CRITICAL findings exist:**
> "🔴 There are CRITICAL issues that must be resolved before committing.
> Fix them and re-run `/code-review`, or tell me what to fix and I'll
> help you address them."
>
> Do NOT hand off to java-git-commit until the user confirms fixes are done.

**If no CRITICAL findings:**
> "✅ No critical issues found. [N warnings / notes listed above.]
> Ready to commit — run `/java-git-commit` or tell me to proceed."

---

## Severity Assignment Flow

```dot
digraph severity_flow {
    "Finding detected" [shape=doublecircle];
    "Safety violation?" [shape=diamond];
    "Concurrency issue in shared code?" [shape=diamond];
    "CRITICAL" [shape=box, style=filled, fillcolor=red];
    "In hot path?" [shape=diamond];
    "WARNING" [shape=box, style=filled, fillcolor=yellow];
    "NOTE" [shape=box, style=filled, fillcolor=lightblue];

    "Finding detected" -> "Safety violation?";
    "Safety violation?" -> "CRITICAL" [label="yes"];
    "Safety violation?" -> "Concurrency issue in shared code?" [label="no"];
    "Concurrency issue in shared code?" -> "CRITICAL" [label="yes"];
    "Concurrency issue in shared code?" -> "In hot path?" [label="no"];
    "In hot path?" -> "WARNING" [label="yes (perf/repro)"];
    "In hot path?" -> "NOTE" [label="no"];
}
```

---

## Review Checklist

### 🔴 Safety (always check — any violation is CRITICAL)

- **Resource leaks**: streams, connections, readers, writers, executors —
  must be closed via try-with-resources or explicit finally. Check for any
  `new` of a `Closeable` not wrapped in try-with-resources.
- **Classloader leaks**: `ThreadLocal` values set but never removed;
  static references to objects that hold class references.
- **Silent data corruption**: catch blocks that swallow exceptions without
  logging or rethrowing; result values that are silently ignored when they
  signal failure.
- **Deadlock risk**: nested lock acquisition — flag any code that acquires
  more than one lock and verify ordering is documented.
- **Unchecked nulls**: return values from external calls, CDI injections
  used without null-check where `@Inject` could legitimately yield null.

### 🔴 Concurrency (CRITICAL if in shared/multi-threaded code)

- Shared mutable state accessed without synchronisation.
- Non-thread-safe collections (`HashMap`, `ArrayList`) used in a context
  that could be accessed from multiple threads.
- Blocking calls (I/O, `Thread.sleep`, `Object.wait`) on the Vert.x
  event loop — must be dispatched to a worker thread (`@Blocking` or
  `executeBlocking`).
- `ThreadLocal` set in one context and read in another (e.g. across
  async boundaries).
- Hot-loop code added without a `// NOT thread-safe` comment.

### 🟡 Reproducibility (WARNING)

- New `HashMap` or `HashSet` used in build-time or bootstrap code where
  ordering matters — suggest `LinkedHashMap` / `TreeMap` instead.
- Non-deterministic iteration over collections in code that produces
  output consumed downstream.

### 🟡 Performance (WARNING in hot paths, NOTE elsewhere)

- `java.util.stream` chains in tight loops or per-request paths.
- Unnecessary boxing (e.g. `Integer` where `int` suffices, streams over
  primitives using boxed types).
- Excessive object allocation inside loops (e.g. `new String(...)`,
  `String.format` in a hot path).
- Reflection used where a simpler approach exists.

### 🟡 Testing (WARNING)

- New non-trivial logic added with no corresponding test.
- Test added that only duplicates existing integration test coverage
  with heavy mocking — suggest removing or replacing with a
  `@QuarkusComponentTest`.
- `@QuarkusTest` used where `@QuarkusComponentTest` would suffice
  (unnecessary full container startup).

### 🔵 Code clarity (NOTE)

- Missing `final` on parameters or local variables in new code.
- Unnecessary `this.` prefix.
- Fully qualified class names used where an import would be cleaner.
- Javadoc added on trivial methods, or missing on genuinely non-trivial
  ones.
- New `@author` tag introduced.

### 🔵 Minimize changes (NOTE)

- Existing method signatures altered without semantic need.
- Formatting or whitespace changed on lines not otherwise touched.
- Import order changed unnecessarily (formatter-maven-plugin and
  impsort-maven-plugin own this — don't manually reorder).

---

## Integration with java-git-commit

When `java-git-commit` is invoked and no `/code-review` has been run
in the current session, ask:
> "Would you like me to run a code review before committing? (Recommended)"

If the user says yes, run this skill in full before proceeding.
If the user says no, proceed directly to `java-git-commit`.
Do not ask again if a review was already completed this session.