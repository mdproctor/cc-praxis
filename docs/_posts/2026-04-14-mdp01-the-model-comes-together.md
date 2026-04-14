---
layout: post
title: "cc-praxis — The Model Comes Together"
date: 2026-04-14
type: phase-update
entry_type: note
subtype: diary
projects: ["cc-praxis"]
---
# cc-praxis — The Model Comes Together

**Date:** 2026-04-14
**Type:** phase-update

---

The original workspace model had `design/DESIGN.md` as a full copy of the project's
design document, updated in the workspace during an epic and merged back at close.
The idea seemed clean. The merge wasn't.

Two independently-evolved full documents arriving at epic close aren't a merge
problem — they're a "which changes came from the epic" problem. Without a baseline,
there's no way to tell what the epic changed from what main evolved independently.

I scrapped the full-copy model. The replacement is `design/JOURNAL.md` — a narrative
of design changes made during the epic. Not a copy, not a diff. Each entry has a
structured header:

```
### 2026-04-15 · §Architecture · ADR-0042
```

The date, the affected section (exact name from the project DESIGN.md), and an ADR
reference where applicable. The body is prose — what was decided, why, how the
thinking shifted. At epic close, that header gives Claude a map of what sections
changed.

Three safeguards close the gap between "I read a narrative" and "I made an accurate
merge": `epic-start` records the project HEAD SHA when the branch begins, so epic-close
can retrieve the baseline DESIGN.md for a three-way merge rather than two-way; the
section anchors are explicit rather than inferred from prose; and epic-close generates
a diff preview before touching the project DESIGN.md, then verifies each section after
applying.

The journal is also readable standalone — good enough to post to the GitHub epic issue
at close as the design narrative.

## epic-start and epic-close

With the model settled, we built the two lifecycle skills. `epic-start` creates matching
branches in the project and workspace, scaffolds the journal and `.meta` file with the
SHA, and optionally links or creates a GitHub issue. `epic-close` reads the meta, builds
a full close plan — artifact routing, journal merge preview, spec posting, branch cleanup
— and presents it with an approve-all or step-by-step option.

The approve-all path executes everything in order and reports failures without stopping.
The step-by-step path gates at each phase. The journal merge is the step where that gate
matters most — it requires Claude to exercise judgment about which sections to update and
how, and a checkpoint before touching the project DESIGN.md is worth having.

## The two-stage review

We implemented using subagent-driven development: implementer, then spec reviewer, then
quality reviewer in sequence. The quality reviewer — dispatched fresh, with no spec context
— caught something the spec reviewer missed: Steps 5 and 6 of `java-update-design`'s
direct-mode workflow weren't excluded when workspace mode was active. The Success Criteria
said workspace mode completed with a journal entry. The steps said do the DESIGN.md work
first. Silent contradiction.

This wasn't in the spec because the spec didn't describe internal step routing. The spec
reviewer had no reason to look for it. The quality reviewer, reading fresh, noticed the
instructions contradicted themselves.

Two separate reviewers catch different things. Worth the extra invocations.

## Path updates close the loop

All skills now write to workspace-relative paths — `adr/`, `blog/`, `snapshots/`,
`IDEAS.md` — rather than `docs/` subdirectories. The session-start hook prompts to read
HANDOVER.md and nudges toward workspace setup if missing. INDEX.md maintenance landed in
`adr`, `design-snapshot`, and `write-blog` — each appends a row after writing.
`workspace-init` no longer copies the project DESIGN.md into the workspace; that directory
is now `epic-start`'s territory.

Issue #49 is closed. The workspace model is complete, pending smoke tests in a real
workspace session.
