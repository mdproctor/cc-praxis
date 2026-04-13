# Design Journal — Design Spec

**Date:** 2026-04-13
**Status:** Approved

---

## Problem

The workspace model spec defines `design/DESIGN.md` as a full copy of the
project's `DESIGN.md`, updated during the epic and merged back at close. This
creates two problems:

1. **Hard merge** — two full documents evolved independently; Claude must figure
   out which changes came from the epic vs. main-branch changes.
2. **Duplication** — the workspace document is mostly redundant content from
   the project `DESIGN.md`, with no narrative value.

---

## Solution

Replace the full-copy model with a **design journal** (`design/JOURNAL.md`) —
a living narrative of design changes made during the current epic. It is not a
copy of the project `DESIGN.md`. It documents the design journey: what was
considered, what was decided, how the thinking evolved.

---

## Core Principle

> The project `DESIGN.md` is the authoritative reference document.
> `design/JOURNAL.md` is the working surface — a narrative of what this epic
> changes and why. Git history records the evolution; the document always
> reflects current intent.

---

## Document Identity

**File:** `workspace/design/JOURNAL.md`

**What it is:**
- A cohesive narrative of design changes during the current epic
- A living document — rewritten as the design evolves, not append-only
- Readable standalone — postable to the GitHub epic issue at close

**What it is not:**
- A copy of the project `DESIGN.md`
- A diff or patch file
- A replacement for ADRs (decisions that warrant ADRs still get them; the
  journal references them)

---

## Entry Format

One entry per affected section (not per date). If a section is revisited
during the epic, the entry is updated in place — the date in the header
reflects the last update. Git history shows how it evolved.

```markdown
# Design Journal — epic-payments

### 2026-04-15 · §Architecture · ADR-0042

We moved to an event-driven model: order service emits `OrderPlaced`, payment
service listens and responds. The synchronous approach created coupling that
complicated retry logic and made retry semantics ambiguous...

### 2026-04-12 · §Data Model

The payment record needs a `status` field with four states: `pending`,
`processing`, `completed`, `failed`. The transition model is...
```

**Header format:** `### YYYY-MM-DD · §Section1, §Section2 · ADR-N (optional)`

- **Date** — last updated date for this entry
- **§Sections** — exact section names from the project `DESIGN.md`; the merge
  algorithm uses these as its map
- **ADR reference** — included where the decision generated a formal ADR;
  gives the merge a sharper reference than prose alone

**Body:** free-form prose — the reasoning, the options considered, the decision,
the current state of that design area.

---

## Safeguards

| Safeguard | Mechanism |
|-----------|-----------|
| **SHA baseline** | `epic-start` records the project `HEAD` SHA in `design/.meta`. At merge time, retrieves the project `DESIGN.md` at that SHA — enables true three-way merge (base + journal + current project). |
| **Section anchors** | Every entry header names exact `§Section` targets from the project `DESIGN.md`. The merge algorithm uses these as its map — no guessing from prose. |
| **ADR cross-links** | Where a decision generated an ADR, the header includes the reference. Claude uses the ADR's precise decision record as a sharper reference when applying the change. |
| **Merge preview** | At epic close, before touching the project `DESIGN.md`, Claude generates proposed changes per anchored section. User reviews and approves before anything is written. |
| **Post-merge verification** | After applying, Claude reads the updated `DESIGN.md` and confirms each anchored section reflects the journal's current state. Nothing silently dropped. |

**`design/.meta` contents:**
```
epic: epic-payments
project-sha: a3f9c12
date: 2026-04-10
```

---

## Lifecycle

### At epic start (`epic-start` skill)

- Creates `design/JOURNAL.md` with stub: `# Design Journal — <epic-name>`
- Records project `HEAD` SHA in `design/.meta`

### During the epic

- `java-update-design`, `update-primary-doc`, and brainstorming outputs write
  or update entries in `JOURNAL.md`
- Entries updated in place when the design pivots — git history preserves the
  trail
- ADRs created as normal for significant decisions; journal entries reference
  them via the header anchor
- `handover` wrap checklist prompts: *"Any design changes this session not yet
  journaled?"* — fallback for design thinking that happened without a commit

### At epic close (`epic-close` skill)

1. Read `design/.meta` → retrieve project SHA recorded at epic start
2. `git -C <project> show <sha>:DESIGN.md` → baseline
3. Read current project `DESIGN.md` (may have evolved independently on main)
4. Read `design/JOURNAL.md` → extract all `§Section` anchors
5. For each anchored section: apply journal narrative, preserving independent
   main-branch changes
6. Present merge preview — proposed updated sections for user review
7. User approves (or requests adjustments)
8. Write updated project `DESIGN.md`
9. Post-merge verification — confirm each anchored section was addressed
10. Post `JOURNAL.md` to GitHub epic issue as the design narrative
11. `JOURNAL.md` is discarded after posting — ephemeral, not promoted to
    project repo

**What if the project `DESIGN.md` changed independently on main during the epic?**
The SHA baseline makes this visible — Claude sees what the project looked like
at epic start and what it looks like now, distinguishing independent main-branch
changes from epic changes before applying.

---

## Skill Wiring

| Trigger | Skill | Action |
|---------|-------|--------|
| Epic begins | `epic-start` | Creates `JOURNAL.md` stub, records SHA in `design/.meta` |
| Code committed with design implications | `java-update-design` / `update-primary-doc` | Writes or updates the relevant journal entry |
| Brainstorming produces a design decision | `brainstorming` | Outputs a journal entry stub alongside the spec; user confirms |
| Session end | `handover` | Wrap checklist: *"Any design changes this session not yet journaled?"* |
| Epic closes | `epic-close` | Reads journal, performs merge, posts to GitHub issue |

The shift for `java-update-design` and `update-primary-doc`: their job moves
from *"update the project document"* to *"explain what changed and why, with
section anchors."* The project `DESIGN.md` is untouched until epic close.

---

## Relation to Existing Workspace Model Spec

This document supersedes the `Design Document Lifecycle` section of
`2026-04-09-workspace-model-design.md`. All other sections of that spec remain
valid. The implementation plan (`2026-04-09-workspace-model.md`) Task 10b
should be updated to reflect this model — `java-update-design` and
`update-primary-doc` write to `design/JOURNAL.md` with the entry format
defined here, not to `design/DESIGN.md`.

---

## Out of Scope

- `epic-start` and `epic-close` full skill specs — see mdproctor/cc-praxis#49
- ADR and documentation routing when not desired in the project repo — separate epic
- Blog entry type differentiation (article vs. note) — see IDEAS.md
