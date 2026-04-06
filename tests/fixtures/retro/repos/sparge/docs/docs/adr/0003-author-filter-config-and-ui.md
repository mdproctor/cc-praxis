# 0003 — Author filter: config default + UI override

Date: 2026-04-05
Status: Accepted

## Context and Problem Statement

Sparge projects can contain posts from multiple authors. The existing
`filter.author` config already scoped ingest to one author, but the
browse/operate UI showed all posts regardless. For multi-author archives
users needed a way to work on one author at a time without creating a
separate project per author.

## Decision Drivers

* Config filter and display scope should be consistent by default
* Users should be able to temporarily widen or change the view without
  editing config
* Filtering must work correctly for projects with thousands of posts

## Considered Options

* **Option A** — Config filter only: `filter.author` restricts display as well as ingest
* **Option B** — UI filter only: dropdown in the UI, no config involvement
* **Option C** — Both: config sets default scope; UI dropdown overrides per session

## Decision Outcome

Chosen option: **Option C**, because the config and display scope should
be consistent (a project set up for one author should default to showing
that author), while the UI override gives operational flexibility without
config changes.

### Positive Consequences

* Consistent default — ingest and display use the same author scope
* Session flexibility — switch authors without touching config
* Server-side filtering scales correctly for large post counts
* Single `/api/posts?author=X` fetch on startup (no double-fetch)

### Negative Consequences / Tradeoffs

* Two mechanisms to understand (config default + UI override)
* UI must re-fetch posts on author change rather than filtering client-side

## Pros and Cons of the Options

### Option A — Config only

* ✅ Simple — one place to configure
* ❌ No in-session flexibility without editing config and restarting

### Option B — UI only

* ✅ Flexible per-session
* ❌ Config `filter.author` and display scope inconsistent out of the box
* ❌ No persistent default for multi-author projects

### Option C — Both (chosen)

* ✅ Consistent default from config
* ✅ Per-session flexibility via UI dropdown
* ✅ Server-side filtering scales to large archives
* ❌ Two mechanisms to understand

## Links

* Design snapshot: `docs/design-snapshots/2026-04-05-sparge-pipeline-and-storage.md`
* Spec: `docs/superpowers/specs/2026-04-05-author-filter-design.md`
