---
name: code-review-principles
description: >
  Universal code review principles covering safety, concurrency, performance,
  testing philosophy, and review workflow. Provides language-agnostic
  checklist and severity assignment guidance for catching critical issues
  before they reach production. Use as foundation for language-specific
  code review skills.
---

# Code Review Principles

Universal principles for catching critical issues before they reach production,
with focus on safety violations, concurrency bugs, and silent data corruption
that compilers cannot detect.

## Why Code Review Matters

**Caught in review vs. caught in production:**
- Resource leak found in review: 2-minute fix
- Resource leak in production: 3-hour incident, emergency patch, postmortem

**What code review prevents:**
- **Deadlocks** between locks that would hang production under load
- **Memory leaks** holding resources that would crash after multiple deployments
- **Blocking operations** that would freeze concurrent requests during slowdowns
- **Mock/real divergence** where tests pass but real integration fails

**What code review is not:**
- Not style police (formatters handle that)
- Not architecture redesign (that's during design phase)
- Not performance tuning (profilers do that better)

**What code review is:**
- Safety net for critical issues compilers can't detect
- Second pair of eyes on concurrency correctness
- Verification that tests actually test what they claim

## Workflow

### Step 1 — Collect changes

Examine the code changes to be reviewed (staged commits, pull request diff, or
specified files).

### Step 2 — Run the review checklist

Work through each category below. For every finding, assign a severity:

| Severity | Meaning |
|---|---|
| 🔴 CRITICAL | Must be fixed before deploying. Blocks merge/commit. |
| 🟡 WARNING | Should be addressed; advisory only, does not block. |
| 🔵 NOTE | Minor observation or improvement suggestion. |

### Step 3 — Present findings

Group findings by severity, then by location. Format:

```
🔴 CRITICAL — [file/location]
[Description of issue and impact]

Suggested fix:
[Concrete fix suggestion]
```

After all findings, show summary:
```
Review complete: X CRITICAL, Y WARNING, Z NOTES
```

### Step 4 — Conclude

**If CRITICAL findings exist:**
> "🔴 There are CRITICAL issues that must be resolved before deploying.
> Fix them and re-run the review, or let me help you address them."

**If no CRITICAL findings:**
> "✅ No critical issues found. [N warnings / notes listed above.]
> Ready to proceed."

---

## Review Checklist

### 🔴 Safety (always check — any violation is CRITICAL)

**Resource leaks** - streams, connections, handles, executors must be closed:
- Files, sockets, database connections opened but not closed
- Missing cleanup in exception paths
- Resources allocated but cleanup deferred beyond safe scope

**Memory leaks** - references that prevent garbage collection:
- Thread-local storage not cleaned up
- Listeners/callbacks registered but never unregistered
- Caches without eviction policies

**Silent data corruption** - exceptions silently swallowed:
- Empty catch blocks discarding exceptions
- Catch-and-log without propagation where failure should bubble up
- State mutations succeeding despite operation failures

**Deadlock risk** - multiple locks acquired without documented ordering:
- Nested lock acquisition without clear ordering rules
- Locks held while calling external code
- Lock acquisition in inconsistent order across call sites

**Null safety** - unchecked nullable values:
- Return values from external calls used without null-check
- Optional values unwrapped without presence verification
- Dependency injection points that could yield null

### 🔴 Concurrency (CRITICAL if in shared/multi-threaded code)

**Blocking on async threads** - I/O or blocking operations on event-loop threads:
- Database queries on async handler threads
- File I/O on event-loop threads
- Thread.sleep() or blocking waits on async paths

**Non-thread-safe collections** - shared mutable state without synchronization:
- HashMap, ArrayList, HashSet shared across threads
- Mutable state in singleton/shared services without synchronization
- Race conditions on shared counters or flags

**Thread-local across async boundaries** - context loss in async code:
- Thread-local values expected to propagate across thread switches
- Request context assumed available after async boundary
- User/session data accessed after CompletableFuture/callback

**Missing thread safety documentation**:
- Shared mutable state without `// NOT thread-safe` comment
- Concurrency assumptions not documented

### 🟡 Reproducibility (WARNING)

**Non-deterministic ordering** - iteration order affects output:
- Hash-based collections used in build/bootstrap code where order matters
- Non-sorted output consumed by downstream systems
- Test assertions relying on unspecified iteration order

### 🟡 Performance (WARNING in hot paths, NOTE elsewhere)

**Hot path inefficiencies** - performance issues in frequently-called code:
- Functional/stream overhead in per-request paths
- Excessive allocations inside tight loops
- Unnecessary boxing/unboxing in hot code

**Reflection overuse** - reflection where direct calls would work:
- Reflection for simple method calls
- Dynamic lookup where static typing available

### 🟡 Testing (WARNING)

**Mocks hiding real issues** - mocked dependencies masking integration problems:
- Database operations mocked instead of using real/in-memory DB
- External APIs mocked without contract tests
- Tests passing with mocks but failing with real implementations

**Missing test coverage** - new logic without corresponding tests:
- Non-trivial business logic added without tests
- Error handling paths untested
- Integration points untested

**Wrong test scope** - heavyweight tests for lightweight needs:
- Full application startup for unit-level tests
- Integration tests where component tests would suffice

### 🔵 Code Clarity (NOTE)

**Immutability** - unnecessary mutability:
- Parameters and variables declared mutable when immutable would work
- Missing const/final/readonly markers on values that don't change

**Unnecessary qualification** - redundant prefixes:
- this./self. prefix where disambiguation unnecessary
- Fully qualified names where imports would be cleaner

**Documentation mismatch** - missing or excessive documentation:
- Trivial methods over-documented
- Non-obvious logic under-documented
- Comments explaining what instead of why

### 🔵 Minimize Changes (NOTE)

**Unnecessary changes** - modifications unrelated to stated purpose:
- Signature changes without semantic need
- Formatting/whitespace changed on untouched lines
- Import order changed unnecessarily

## Severity Decision Flow

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

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping safety checks for "simple" changes | Simple code has critical bugs too | Always check safety, even for one-liners |
| Approving without understanding the change | Can't catch issues in code you don't understand | Read and understand before approving |
| Focusing only on style/formatting | Misses critical safety and concurrency issues | Safety first, style last |
| Accepting "I tested it manually" | Manual tests don't catch edge cases or regressions | Require automated tests for non-trivial changes |
| Letting CRITICAL issues through | Critical issues cause production incidents | Never approve with unresolved CRITICAL findings |
| Over-focusing on performance in cold paths | Premature optimization adds complexity | Focus performance review on actual hot paths |

---

## Skill Chaining

Language-specific review skills (`java-code-review`, `python-code-review`, etc.)
implement these principles with language-specific examples and tooling.
