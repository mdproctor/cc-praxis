# 0001 — Three-stage immutable pipeline

Date: 2026-04-05
Status: Accepted

## Context and Problem Statement

Sparge converts blog posts from raw HTML to Jekyll Markdown. The conversion
involves fetching content, fixing embeds and code blocks, and generating MD.
We needed a pipeline design that would allow re-running any stage safely
without corrupting earlier work.

## Decision Drivers

* Original HTML must never be modified — it is the ground truth
* Each stage must be re-runnable independently (idempotent)
* Fixes (embed replacement, class normalisation) should be separable from
  both ingestion and MD generation
* Users should be able to inspect intermediate state (enriched HTML before MD)

## Considered Options

* **Option A** — Single-pass: fetch, fix, and generate MD in one operation
* **Option B** — Two-stage: Ingest (fetch + fix), then Generate MD
* **Option C** — Three-stage: Ingest (pure download), Scan/Enrich (fixes → enriched/), Generate MD (reads enriched)

## Decision Outcome

Chosen option: **Option C**, because it gives each stage a single responsibility
and makes the pipeline fully re-runnable at any stage without side effects.

### Positive Consequences

* Original HTML preserved unchanged — safe to re-ingest if needed
* Scan can be re-run to apply new fixes to existing posts without re-fetching
* Generate MD always works from the best available HTML (enriched if present, original as fallback)
* Intermediate enriched HTML is inspectable and debuggable

### Negative Consequences / Tradeoffs

* More disk usage (original + enriched + MD per post)
* Three separate operations to run a post through the full pipeline

## Pros and Cons of the Options

### Option A — Single-pass

* ✅ Simple — one operation end-to-end
* ❌ Re-running overwrites or corrupts earlier work
* ❌ Cannot re-apply fixes without full re-fetch

### Option B — Two-stage (fetch+fix, then MD)

* ✅ Separates fetch from generation
* ❌ Ingest is no longer a pure download — fixing logic entangled with fetching
* ❌ Cannot re-apply fixes without re-ingesting

### Option C — Three-stage (chosen)

* ✅ Pure separation of concerns
* ✅ Each stage independently re-runnable
* ✅ Original HTML immutable
* ❌ Extra disk usage for enriched copies

## Links

* Design snapshot: `docs/design-snapshots/2026-04-05-sparge-pipeline-and-storage.md`
* Pipeline reference: `docs/pipeline.md`
