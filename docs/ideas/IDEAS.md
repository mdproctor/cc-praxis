# Idea Log

Undecided possibilities — things worth remembering but not yet decided.
Promote to an ADR when ready to decide; discard when no longer relevant.

---

## 2026-04-04 — Semantically-ordered merge of workspace design docs into target DESIGN.md

**Priority:** high
**Status:** active

When promoting a workspace design document into a target project's DESIGN.md,
a clean git merge is not sufficient. Design documents are order-sensitive prose:
a technically conflict-free merge can produce a document that is incoherent if
sections arrive out of sequence (e.g. a conclusion merged before its premises,
or an architectural evolution described before the baseline it evolved from).

This is distinct from code merges where order-independence is more common.
A solution needs to handle:
- Multiple parallel workspace contributors merging into the same DESIGN.md
- Sequential evolution within a single workspace (sections written at different
  times that must land in narrative order, not commit order)
- The fact that "no conflicts" is a false signal of correctness for prose docs

No solution designed yet — this is a hard, important TODO before workspace
promotion is considered complete. Possible directions: section-level ordering
metadata, a merge coordinator skill that reviews and reorders before committing,
or a structured DESIGN.md format that makes ordering explicit and checkable.

**Context:** Raised during workspace redesign (2026-04-04) when discussing
promotion of workspace artifacts to target project repos. The design-snapshot →
DESIGN.md promotion path is the primary trigger, but applies to any prose
document with narrative structure.

**Promoted to:** *(leave blank)*

---

## 2026-04-04 — Consistent index-first pattern across all workspace content

**Priority:** high
**Status:** active

Every folder in a workspace (project or global) should have a lightweight index
file that gives Claude enough orientation to decide what to load next — without
loading the detail files themselves. Pattern already proven by `garden/GARDEN.md`
(dual index by technology + symptom). Should apply consistently to
`<project>-workspace/` folders too: handoffs, snapshots, ideas, blog entries
all get an index so any session can orient cheaply.

**Context:** Surfaced during workspace redesign discussion (2026-04-04).
Garden's index-first design was noted as the right model for the whole workspace,
not just the garden. If every folder follows this pattern, session-handoff and
other skills can navigate the workspace without loading every file.

**Promoted to:** *(leave blank)*

---

## 2026-04-04 — Holistic project-memory architecture: indexed folders not flat files

**Priority:** high
**Status:** active

The cc-praxis methodology family (design-snapshot, project-blog, knowledge-garden,
idea-log, adr, session-handoff, CLAUDE.md) has grown organically but lacks a
coherent cross-tool indexing strategy. Two specific improvements worth exploring:

1. **design-snapshot as a categorised folder** — instead of flat dated files,
   use subdirectories by topic (architecture/, decisions/, state/) with an
   INDEX.md modelled on GARDEN.md's dual-index approach (by category AND by
   date). This lets a future session find "what did we decide about the web
   installer?" without reading all snapshots.

2. **Cross-tool findability** — each tool currently indexes only its own
   content. A light meta-index (or agreed naming conventions) would let
   session-handoff point to the right snapshot, blog entry, or garden section
   without loading any of them. The lazy-reference principle from
   session-handoff should propagate to how all tools reference each other.

**Context:** Surfaced while designing session-handoff — the skill needs to
reference design-snapshot, project-blog, and knowledge-garden without loading
them. The knowledge-garden's GARDEN.md dual-index (by technology + by symptom
type) proved that this pattern works. design-snapshot has no equivalent index,
making it harder to reference selectively. Discussed alongside the observation
that DESIGN.md is current-state only, not historical, so snapshots carry the
historical burden but aren't structured for retrieval.

**Promoted to:** *(leave blank)*

---

## 2026-04-04 — Dual-repo model for epic-scoped developer work

**Priority:** medium
**Status:** active

A developer working on a long-running epic uses two repos: the main project
repo (code + finalized artifacts) and a personal session repo (WIP snapshots,
idea-log entries, in-flight ADRs, DESIGN-DELTA.md). At epic close, curated
artifacts are published to the main project; noise stays in the session repo.
The DESIGN-DELTA.md evolves throughout the epic as a draft of changes planned
for the main DESIGN.md.

**Context:** Arose during a review of the 7 methodology skills (idea-log, adr,
design-snapshot, update-claude-md, java-update-design, update-primary-doc,
issue-workflow) — noticed that all of them write directly into the project repo,
creating noise during exploratory/WIP phases. Also prompted by thinking about
co-worker collaboration: multiple developers on the same epic could each have
their own session repo and reconcile at integration time. Revisit alongside
issue/epic grouping work and co-worker collaboration model.

**Promoted to:** *(leave blank — fill if promoted to ADR or task)*
