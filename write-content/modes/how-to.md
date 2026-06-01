# Mode: How-to

Two sub-types. The distinction is the reader's starting state — not the
structure of the fix steps.

---

## Choosing between sub-types

**Primary question:** What is the reader's starting state?

- Working state, trying to accomplish something → **procedural**
- Broken or wrong state, trying to recover → **diagnostic**

**The Symptom → Cause → Fix structure is the diagnostic marker.** If a section
opens with a symptom → diagnostic, even if fix steps use imperative syntax.
The mode is determined by the entry condition (broken state), not by how the
fix steps are written.

**Procedural** ends when the task is accomplished.
**Diagnostic** ends when the broken state is resolved.

---

## Procedural sub-type

Steps to accomplish a task from a working state. The reader starts from zero
or from a known good state and wants to reach a goal.

**Used by:** Article/how-to, onboarding steps, setup instructions, deployment
guides, configuration walkthroughs.

**Rules:**
- Goal stated clearly upfront — reader knows what they'll have when done
- Steps in logical sequence — one action per step
- Include warnings and edge cases — real how-tos acknowledge what can go wrong
- "Why this step, not that" where non-obvious — don't make the reader guess
- Assume some prior knowledge — not a tutorial (reader is working, not studying)
- Ends when the task is complete

**Structure:**
```
Goal: [what the reader will have accomplished]
Prerequisites: [what must be true before starting]

1. [Action — one verb, one outcome]
   ⚠ [Warning if relevant]
2. [Next action]
   ...
[Success condition — how the reader knows it worked]
```

**Voice texture:**
Right: direct imperatives ("Run X", "Set Y to Z"), explicit success conditions,
warnings stated before the reader reaches the failure point.
Wrong: explaining why the task matters (assumed), restating the goal at each
step, passive voice ("X should be set"), vague outcomes ("configure it
appropriately").

---

## Diagnostic sub-type

Symptom → Cause → Fix. The reader starts from a broken or wrong state.

**Used by:** Technical documentation Gotchas, anti-patterns sections,
troubleshooting guides, FAQ entries about failures.

**Rules:**
- **Symptom** is observable — what the reader actually sees in logs, tests,
  IDE, or runtime. Not "the system behaves unexpectedly" — the exact error
  message, the specific wrong output, the observed state.
- **Cause** is the root mechanism — not the symptom restated. Explains WHY
  this failure mode occurs. One level deeper than the symptom.
- **Fix** is the exact action — not a direction. The specific file, class,
  command, or configuration change. "Might", "could", "generally" are
  forbidden in Fix statements.
- No hedging anywhere. The reader is in a broken state; they need precision.

**Structure:**
```
- **[Short name for the failure mode]**
  - **Symptom:** [Exactly what the reader sees]
  - **Cause:** [Root mechanism — one level deeper]
  - **Fix:** [Exact action — file, class, command, config value]
```

**Voice texture:**
Right: Symptom names what the reader will actually see (exact error text or
exact wrong output). Fix gives the specific thing to change, not a direction.
Wrong: "you might see", "this could indicate", "consider doing X", symptoms
that describe the wrong state abstractly rather than observably.
