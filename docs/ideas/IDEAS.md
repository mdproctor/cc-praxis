# Idea Log

Undecided possibilities — things worth remembering but not yet decided.
Promote to an ADR when ready to decide; discard when no longer relevant.

---

## 2026-04-06 — Periodically evolve the personal writing style guide

**Priority:** low
**Status:** active

The personal guide (`blog-technical.md`) was built from a 577-post corpus spanning 2006–2017 — solo technical writing for the Drools/KIE community. The current writing context is different: collaborative work with Claude, a development diary format, and potentially a broader audience. Some rules carry forward perfectly; others may need revisiting for the new context. Worth doing a deliberate review periodically — comparing what the guide says against what's actually being written — and asking which rules still fit and which should evolve.

**Context:** Arose from questioning the "no preamble" rule — which is solidly grounded in the corpus but may have legitimate exceptions in longer series or for broader audiences. The I/we/Claude register system was invented for this context, not derived from the corpus; other adaptations might similarly be worth making deliberately rather than discovered after the fact.

**Promoted to:**

---

## 2026-04-04 — Holistic project-memory architecture: indexed folders not flat files

**Priority:** high
**Status:** active

The cc-praxis methodology family (design-snapshot, project-blog, knowledge-garden,
idea-log, adr, session-handover, CLAUDE.md) has grown organically but lacks a
coherent cross-tool indexing strategy. Two specific improvements worth exploring:

1. **design-snapshot as a categorised folder** — instead of flat dated files,
   use subdirectories by topic (architecture/, decisions/, state/) with an
   INDEX.md modelled on GARDEN.md's dual-index approach (by category AND by
   date). This lets a future session find "what did we decide about the web
   installer?" without reading all snapshots.

2. **Cross-tool findability** — each tool currently indexes only its own
   content. A light meta-index (or agreed naming conventions) would let
   session-handover point to the right snapshot, blog entry, or garden section
   without loading any of them. The lazy-reference principle from
   session-handover should propagate to how all tools reference each other.

**Context:** Surfaced while designing session-handover — the skill needs to
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
