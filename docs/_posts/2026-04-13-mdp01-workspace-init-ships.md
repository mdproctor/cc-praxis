---
layout: post
title: "cc-praxis — workspace-init Ships"
date: 2026-04-13
type: phase-update
entry_type: note
subtype: diary
projects: ["cc-praxis"]
---
# cc-praxis — workspace-init Ships

**Date:** 2026-04-13
**Type:** phase-update

---

The workspace model is live. The previous entry covered the design; this one is
about what it looks like in practice.

`/workspace-init` sets up a companion directory at `~/claude/private/<project>/`
(or `public/`). Run it once per project per machine. After that, Claude opens in
the workspace, not the project. Skills write methodology artifacts there — ADRs,
snapshots, blog entries, plans — rather than into the project repo.

The workspace gets a routing `CLAUDE.md` with one job: tell Claude to run
`add-dir <project-path>` at session start. From there, everything works the same
as before, except your project history stays clean.

## The upstream problem

The reason this matters: a lot of us work on projects we don't own. Drools,
Quarkus, any upstream open source project. Putting methodology notes in a repo
you're contributing to isn't an option — it modifies history you share with others.

The previous workaround was accepting that methodology artifacts either went
into your fork (git noise) or didn't get captured at all. The workspace model
removes that tradeoff.

## The `.git/info/exclude` trick

When `workspace-init` creates a `CLAUDE.md` symlink in the project, it records
it in `.git/info/exclude` rather than in `.gitignore`.

The difference: `.gitignore` is tracked — modifying it means a commit to a repo
you may not own. `.git/info/exclude` is local to your clone, never committed,
never visible to anyone else. Any pattern you add there behaves exactly like
`.gitignore` for your local checkout only.

The symlink is invisible to git, works in any project regardless of ownership,
and leaves no trace in the project's history.

## The accumulation problem

The workspace model also changed where design-snapshot writes: `snapshots/`
(workspace root) instead of `docs/design-snapshots/`. That change surfaced a
deeper question: what do you do with existing snapshots once you have a living
design document?

The snapshot model assumes you can read N dated files and reconstruct the current
design state. In practice, the "How We Got Here" in an older snapshot contradicts
the newer one on three decisions. You trust the newest. So why keep the rest?

The decision: a single authoritative design document, updated as things change.
Git history is the archive. Snapshots are a workaround for not having a living
document. `design-snapshot` still exists for explicit design freezes, but the
expectation is a single doc, not a growing chain.

## What the review caught

Merging multiple snapshots into one document is error-prone. The merged result
feels finished. It usually isn't. We ended up with an 8-point review checklist:
decision coverage, conflict scan, stale reference scan, gap check, redundancy,
non-goals audit, cross-reference integrity, readability pass.

The readability pass (Check 8) found a case where a Data Flow section called
`TmuxService.resizePane()` — the old, wrong API — while the Architecture section
two pages earlier explicitly documented that `resize-window` was the fix for a
specific bug. Both sections were accurate when written. Merged, they contradicted
each other. A conflict scan wouldn't catch it — both names are valid identifiers.
Reading sequentially, you notice it.

The gap check (Check 4) found that a `--mcp-config` decision — `mcpServers` key
required, omitting it produces a silent schema validation error — appeared in
snapshot decision tables but never made it into the primary doc.

The checklist is documented and paste-able. Each check catches a distinct class
of defect the others miss.

## One other change

write-blog's mandatory rules now explicitly prohibit theatrical prose —
heightened stakes, "the moment everything changed," that register. It was
implicit in the factual accuracy rule. Making it explicit gives the pre-draft
check something concrete to verify against.
