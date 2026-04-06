# 0004 — Enrichment applied at Scan, not Ingest

Date: 2026-04-05
Status: Accepted

## Context and Problem Statement

HTML fixes (YouTube thumbnail replacement, Gist inlining, code class
normalisation, embed fallbacks) need to be applied before Markdown generation.
The question was where in the pipeline these transformations belong.

## Decision Drivers

* Ingest should be a pure, repeatable download — no transformation logic
* Fixes should be re-applicable without re-fetching from the network
* New fix types should be addable without touching ingest code
* Users should be able to re-run fixes on already-ingested posts

## Considered Options

* **Option A** — Enrich during Ingest: fetch and fix in one pass
* **Option B** — Enrich during Generate MD: apply fixes just before conversion
* **Option C** — Enrich at Scan: dedicated stage writes `enriched/` copies

## Decision Outcome

Chosen option: **Option C**, because it keeps Ingest as a pure network
operation and makes fixes independently re-runnable without re-fetching.
Generate MD reads the enriched copy (falling back to original), so
conversion always uses the best available HTML.

### Positive Consequences

* Ingest has no transformation logic — simple, testable, stable
* Re-running Scan re-applies all fixes to existing posts
* New fix types added to `enrich.py` without touching ingest or MD generation
* Enriched HTML inspectable before committing to MD generation
* Scan validation runs on enriched HTML — fixed embeds don't appear as issues

### Negative Consequences / Tradeoffs

* Extra disk usage for `enriched/` copies
* Posts ingested before enrichment was built need a re-scan to get fixes applied

## Pros and Cons of the Options

### Option A — Enrich during Ingest

* ✅ Single network operation fetches and fixes
* ❌ Re-applying fixes requires re-fetching from network
* ❌ Ingest logic becomes complex and hard to test in isolation

### Option B — Enrich during Generate MD

* ✅ No extra files
* ❌ Fixes applied at generation time — can't inspect enriched HTML separately
* ❌ Scan validation still runs on un-enriched HTML, showing false positives

### Option C — Enrich at Scan (chosen)

* ✅ Ingest stays pure
* ✅ Fixes re-runnable without network access
* ✅ Scan validates enriched HTML
* ❌ Extra disk for enriched copies

## Links

* ADR-0001: three-stage pipeline this decision implements
* Design snapshot: `docs/design-snapshots/2026-04-05-sparge-pipeline-and-storage.md`
* Pipeline reference: `docs/pipeline.md`
