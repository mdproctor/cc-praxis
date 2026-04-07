# Garden Submission Formats

Reference for all submission file formats. Used during CAPTURE Step 5 (draft)
and SWEEP Step 4 (submit confirmed entries).

---

## Filename Conventions

**New submissions:**
```
~/claude/knowledge-garden/submissions/YYYY-MM-DD-<project>-GE-XXXX-<slug>.md
```

**Revise submissions** — include "revise" in slug so MERGE Claude identifies it immediately:
```
~/claude/knowledge-garden/submissions/YYYY-MM-DD-<project>-GE-XXXX-revise-<entry-slug>.md
```

GE-ID is embedded for instant visibility. Assigned in CAPTURE Step 0.

**Version policy for the Stack field:**
- **Third-party libraries:** Always include version or range — `Quarkus 3.9.x`, `tmux 3.2+`, `GraalVM 25`. The gotcha may be fixed in a later version; future readers need to know if it applies to them.
- **"all versions"** — only use when you've verified the behaviour holds across versions, or when it's a fundamental language/protocol issue: `Java (all versions with lambda)`, `JEXL3 (all versions)`.
- **Own pre-1.0 projects** — omit version entirely; it isn't meaningful until the first public release. Revisit when 1.0 ships.

---

## Gotcha Template

Bug, silent failure, or workaround:

```markdown
# Garden Submission

**Date:** YYYY-MM-DD
**Submission ID:** GE-XXXX
**Type:** gotcha
**Source project:** project-name (or "cross-project")
**Session context:** One sentence on what was being worked on when this surfaced
**Suggested target:** `<directory>/<file>.md` *(hint for merge Claude; not binding)*

---

## [Short imperative title — describes the weird thing, not the fix]

**Stack:** Technology, Library, Version — e.g. `Quarkus 3.9.x`, `tmux 3.2+`, `GraalVM 25`
**Symptom:** What you observe — especially the misleading part. Quote exact
error messages. "No error" is important context.
**Context:** When/where this applies. What setup triggers it.

### What was tried (didn't work)
*(mandatory heading — do not inline or omit)*
- tried X — result
- tried Y — result

### Root cause
Why it happens. The underlying mechanism — WHY, not just WHAT.

### Fix *(or "None known — workaround: [X]" if unsolved)*
Code block or config. Be complete. Include what NOT to do alongside what works.
If no fix exists yet, describe the best available workaround — the entry is still worth capturing.
A REVISE submission can add a solution later.

### Why this is non-obvious
The insight. What makes this a gotcha? Why would a skilled developer be misled?

---

## Garden Score

| Dimension | Score (1–3) | Notes |
|-----------|-------------|-------|
| Non-obviousness | — | |
| Discoverability | — | |
| Breadth | — | |
| Pain / Impact | — | |
| Longevity | — | |
| **Total** | **—/15** | |

**Case for inclusion:** [why this belongs]
**Case against inclusion:** [reservations, or "None identified"]
```

---

## Technique Template

Specific how-to, strategic approach, design philosophy, or pattern — all non-obvious positive knowledge:

```markdown
# Garden Submission

**Date:** YYYY-MM-DD
**Submission ID:** GE-XXXX
**Type:** technique
**Source project:** project-name (or "cross-project")
**Session context:** One sentence on what was being worked on when this surfaced
**Suggested target:** `<directory>/<file>.md` *(hint for merge Claude; not binding)*
**Labels:** `#label1` `#label2` *(cross-cutting tags; see Tag Index in GARDEN.md for existing ones)*

---

## [Short active title — what you can do, not that it's clever]

**Stack:** Technology, Library, Version — e.g. `Claude Code CLI`, `JUnit 5`, `Maven 3.x`; omit version for own pre-1.0 projects
**What it achieves:** One sentence — the outcome this technique produces.
**Context:** When/where this applies. What problem it solves.

### The technique
Code block or concrete description. Complete and runnable.

### Why this is non-obvious
What would most developers do instead? Why wouldn't they reach for this?
What's the insight that makes it work?

### When to use it
Conditions where this applies. Any limitations or caveats.

---

## Garden Score

| Dimension | Score (1–3) | Notes |
|-----------|-------------|-------|
| Non-obviousness | — | |
| Discoverability | — | |
| Breadth | — | |
| Pain / Impact | — | |
| Longevity | — | |
| **Total** | **—/15** | |

**Case for inclusion:** [why this belongs]
**Case against inclusion:** [reservations, or "None identified"]
```

**Choosing labels:** Pick tags that describe the *cross-cutting character* of the technique — `#strategy` for broad design philosophy, `#testing` for test patterns, `#ci-cd` for pipeline concerns, `#performance`, `#debugging`, or technology tags like `#tmux`, `#llm-testing`. Check the Tag Index in GARDEN.md first; reuse existing tags before inventing new ones.

---

## Undocumented Template

Behaviour, feature, or option not in official docs:

```markdown
# Garden Submission

**Date:** YYYY-MM-DD
**Submission ID:** GE-XXXX
**Type:** undocumented
**Source project:** project-name (or "cross-project")
**Session context:** One sentence on what was being worked on when this surfaced
**Suggested target:** `<directory>/<file>.md` *(hint for merge Claude; not binding)*

---

## [Short title — describes what exists, not that it's undocumented]

**Stack:** Technology, Library, Version — e.g. `tmux 3.6`, `GraalVM 25`; version matters here as undocumented behaviour may appear/disappear across releases
**What it is:** One sentence — the feature, behaviour, or option that exists.
**How discovered:** Source code reading / trial and error / someone told me / commit history

### Description
Full description of what this does. Treat it as documentation that doesn't
exist yet. Be precise about conditions, defaults, edge cases.

### How to use it / where it appears
Code block or concrete example. Show it working.

### Why it's not obvious
Why would someone not know this exists? Is it in the source but not the docs?
Only mentioned in a GitHub issue? Only in an old commit message?

### Caveats
Any limitations, version constraints, or risks from relying on undocumented behaviour.

---

## Garden Score

| Dimension | Score (1–3) | Notes |
|-----------|-------------|-------|
| Non-obviousness | — | |
| Discoverability | — | |
| Breadth | — | |
| Pain / Impact | — | |
| Longevity | — | |
| **Total** | **—/15** | |

**Case for inclusion:** [why this belongs]
**Case against inclusion:** [reservations, or "None identified"]
```

---

## Revise Template

Enrichment for an existing entry — solution, alternative, variant, update, or status change:

```markdown
# Garden Revision Submission

**Date:** YYYY-MM-DD
**Submission ID:** GE-XXXX  *(this submission's own ID — assigned in CAPTURE Step 0)*
**Type:** revise
**Revision kind:** solution | alternative | variant | update | resolved | deprecated
**Target:** `<directory>/<file>.md` — `## Exact Entry Title`
**Target ID:** GE-YYYY      *(the existing entry being revised — required for REVISE)*
**Source project:** project-name (or "cross-project")
**Session context:** One sentence on what was being worked on when this surfaced

---

## What this adds
[1–2 sentences on what new knowledge this brings to the existing entry]

## Content
[The actual solution, alternative, update, or note — complete and runnable where code is involved]

## Why it belongs with the existing entry
[How it relates — is it a complete fix, an alternative approach, additional context?]

## Trade-offs / caveats
[Any limitations, constraints, or conditions under which this applies or doesn't]

---

## Garden Score

| Dimension | Score (1–3) | Notes |
|-----------|-------------|-------|
| Non-obviousness | — | |
| Discoverability | — | |
| Breadth | — | |
| Pain / Impact | — | |
| Longevity | — | |
| **Total** | **—/15** | |

**Case for inclusion:** [why this belongs]
**Case against inclusion:** [reservations, or "None identified"]
```

**Revision kind guide:**

| Kind | When to use |
|------|------------|
| `solution` | Gotcha had no fix / workaround only — now there's a real fix |
| `alternative` | Entry has one solution — found a different approach with different trade-offs |
| `variant` | Same pattern but different context, constraint, or technology |
| `update` | Additional context, edge cases, or discovery that enriches the entry |
| `resolved` | The library/tool fixed the bug — entry stays but notes the version |
| `deprecated` | Feature removed or approach obsolete — entry stays with a warning |

**Garden Score for REVISE submissions:** score the revision itself, not the original entry.

---

## Post-Merge Entry Format

After merge, the GE-ID is added to the entry header in the garden file:

```markdown
## Entry Title

**ID:** GE-0001
**Stack:** ...
```

And a compact score line is appended at the end of the entry:

```
*Score: 11/15 · Included because: [brief reason] · Reservation: [none / brief reason]*
```

This survives for future pruning decisions without interrupting reading.

---

## Scoring Dimensions

Rate each dimension 1–3:

| Dimension | 1 | 2 | 3 |
|-----------|---|---|---|
| **Non-obviousness** | Somewhat surprising; findable with effort | Would mislead most experienced devs | Would stump even experts; deeply counterintuitive |
| **Discoverability** | Buried in docs but findable | Source code / GitHub issues only | Trial and error; effectively invisible |
| **Breadth** | Narrow edge case or rare setup | Common pattern; many users will hit this | Affects almost anyone using this technology |
| **Pain / Impact** | Annoying but quickly diagnosed | Significant time loss; misleading symptoms | Silent failure, production risk, or data loss |
| **Longevity** | May be fixed or changed soon | Stable API; unlikely to change near-term | Fundamental behaviour; essentially permanent |
