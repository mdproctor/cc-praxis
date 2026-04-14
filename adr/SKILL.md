---
name: adr
description: >
  Use when recording architectural decisions: user says "create an ADR",
  "document why we chose X", significant technical choices are made,
  maven-dependency-update proposes major version upgrades, or java-update-design
  captures new components.
---

# Architecture Decision Record (ADR) Helper

You are an expert at capturing architectural decisions clearly and concisely
using the MADR (Markdown Any Decision Records) format. ADRs live in
`adr/` alongside `DESIGN.md`.

## Core Rules

- ADRs are **append-only** — never delete or substantially rewrite an
  accepted ADR. If a decision is superseded, update its status to
  "Superseded by [ADR-NNNN]" and create a new ADR.
- Keep ADRs concise. The goal is to capture *why*, not to write an essay.
- Never write an ADR to a file without explicit user confirmation.
- Number ADRs sequentially: `NNNN-short-title.md` (e.g. `0001-use-quarkus-flow.md`).
- Titles use kebab-case, all lowercase.

## Workflow

### Step 1 — Check existing ADRs

```bash
ls adr/ 2>/dev/null || echo "No ADRs yet"
```

Determine the next sequence number. If no ADRs exist, start at `0001`.

### Step 2 — Gather context

If the user hasn't provided enough context, ask for:
- What decision was made?
- What problem does it solve?
- What alternatives were considered and why were they rejected?
- Any consequences or tradeoffs worth noting?

For decisions arising from **maven-dependency-update** or **java-update-design**,
extract context from those proposals automatically.

### Step 3 — Draft the ADR

Use this MADR template. **Always replace `YYYY-MM-DD` with today's date (available in session context) — never show the placeholder to the user.**

```markdown
# NNNN — <Short noun phrase title>

Date: YYYY-MM-DD
Status: Proposed | Accepted | Deprecated | Superseded by [ADR-NNNN]

## Context and Problem Statement

<1–3 sentences: what situation or problem prompted this decision?>

## Decision Drivers

* <Key constraint, requirement, or goal>
* <Another driver>

## Considered Options

* **Option A** — <one-line description>
* **Option B** — <one-line description>
* **Option C** — <one-line description>

## Decision Outcome

Chosen option: **Option X**, because <brief rationale>.

### Positive Consequences

* <Benefit>
* <Benefit>

### Negative Consequences / Tradeoffs

* <Tradeoff or risk>

## Pros and Cons of the Options

### Option A — <name>

* ✅ <Pro>
* ✅ <Pro>
* ❌ <Con>

### Option B — <name>

* ✅ <Pro>
* ❌ <Con>
* ❌ <Con>

### Option C — <name>

* ✅ <Pro>
* ❌ <Con>

## Links

* <Related ADR, issue, PR, or doc — optional>
```

### Step 4 — Propose for review

Show the full ADR draft and the target filename, then ask:
> "Does this look good? Reply **YES** to write it to
> `adr/NNNN-<title>.md`, or tell me what to adjust."

---

### Step 5 — Write and confirm

Only after explicit YES:
1. Write the file to `adr/NNNN-<title>.md`
2. Update `adr/INDEX.md`:
   - If `adr/INDEX.md` doesn't exist yet, create it with:
     ```markdown
     # ADR Index

     | ID | Title | Status | Date |
     |----|-------|--------|------|
     ```
   - Append a row:
     ```
     | NNNN | [Title](NNNN-title.md) | Accepted | YYYY-MM-DD |
     ```
3. Confirm: "✅ Written to `adr/NNNN-<title>.md`"

### Step 6 — Suggest an ADR when appropriate

Proactively suggest creating an ADR when you observe:

| Trigger | Example |
|---|---|
| Major version upgrade | Quarkus 3.x → 4.x |
| Adopting a new extension or library | Adding quarkus-flow, LangChain4j |
| Choosing between two viable patterns | Java DSL vs YAML workflow definitions |
| Deliberately deviating from a default | Choosing MockServer over Mockito |
| A decision with future maintainers in mind | Thread model choice, persistence strategy |
| Reversing or superseding a past decision | Changing from one messaging broker to another |

Don't suggest an ADR for routine decisions with no meaningful alternatives
(e.g. adding a utility method, bumping a patch version).

**Not decided yet?** If a significant question has surfaced but the team hasn't
reached a conclusion, suggest `idea-log` instead — park it until it's ready to
become a decision.

---

## ADR Lifecycle Decision Flow

```mermaid
flowchart TD
    Significant_decision_made((Significant decision made))
    Create_new_ADR[Create new ADR]
    Status__Accepted[Status: Accepted]
    Decision_still_valid_{Decision still valid?}
    Still_relevant_{Still relevant?}
    Better_approach_found_{Better approach found?}
    Mark_Superseded[Mark Superseded]
    Mark_Deprecated[Mark Deprecated]
    Create_new_ADR__replacement_["Create new ADR (replacement)"]
    Continue_using[Continue using]
    Significant_decision_made --> Create_new_ADR
    Create_new_ADR --> Status__Accepted
    Status__Accepted -->|time passes| Decision_still_valid_
    Decision_still_valid_ -->|"yes (still applies)"| Continue_using
    Decision_still_valid_ -->|no| Still_relevant_
    Still_relevant_ -->|yes| Better_approach_found_
    Still_relevant_ -->|"no (obsolete)"| Mark_Deprecated
    Better_approach_found_ -->|yes| Mark_Superseded
    Better_approach_found_ -->|no| Mark_Deprecated
    Mark_Superseded --> Create_new_ADR__replacement_
```

| Status | Meaning |
|---|---|
| **Proposed** | Draft, not yet agreed |
| **Accepted** | Decision agreed and in effect |
| **Deprecated** | No longer relevant but not replaced |
| **Superseded by [ADR-NNNN]** | Replaced by a newer decision |

When superseding an ADR:
1. Update the old ADR's status line to `Superseded by [ADR-NNNN]`
2. Create the new ADR referencing the old one in its Links section

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Deleting or rewriting accepted ADRs | Erases decision history | Mark as superseded, create new ADR |
| Writing essay-length ADRs | Too long to read, defeats purpose | Keep concise - capture why, not everything |
| Title includes solution | "ADR-001: Use PostgreSQL" is conclusion, not decision | "ADR-001: Database Selection" |
| Using UPPERCASE.md or CamelCase.md | Inconsistent naming conventions | Use `nnnn-kebab-case-title.md` |
| Skipping "Considered Options" section | Doesn't show what was evaluated | List 2-3 real alternatives considered |
| Creating ADR after implementing | Decision already made, ADR is theater | Write ADR when decision is made, not after |
| No consequences section | Hides tradeoffs and risks | Always list both positive and negative consequences |
| ADR documents routine decisions | Signal-to-noise ratio drops | Only for non-obvious decisions with alternatives |

## Success Criteria

ADR creation is complete when:

- ✅ User has confirmed ADR content with **YES**
- ✅ ADR written to `adr/NNNN-title.md`
- ✅ Status set to "Accepted" (or "Proposed" if needs review)
- ✅ All sections filled (Context, Decision, Consequences, Alternatives, Links)
- ✅ File committed (staged with related code changes)

**Not complete until** ADR file exists and is committed.

## Skill Chaining

**Invoked by:** [`maven-dependency-update`] when major version upgrades or new extensions are proposed, [`java-update-design`] when significant new components are captured, [`idea-log`] when a parked idea is promoted to a formal decision, [`design-snapshot`] when a snapshot reveals decisions without ADR coverage

**Invokes:** [`git-commit`] to stage and commit the ADR (routes to `java-git-commit`, `custom-git-commit`, etc. per CLAUDE.md project type)

**Not decided yet?** Use `idea-log` to park the question first; promote to `adr` when the decision is made.

**Can be invoked independently:** User can run `/adr` or say "create an ADR" directly when making architectural decisions
