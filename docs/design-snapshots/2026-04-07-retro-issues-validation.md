# cc-praxis — Design Snapshot: Retrospective Issue Mapping Validation
**Date:** 2026-04-07
**Topic:** First live run of retro-issues against cc-praxis; complete GitHub issue backfill
**Supersedes:** *(none)*
**Superseded by:** *(leave blank — filled in if this snapshot is later superseded)*

---

## Where We Are

The retro-issues skill completed its first live validation run against this
repository. All 285 commits (2026-03-29 → 2026-04-06) were mapped to 27
standalone GitHub issues, all created and closed on mdproctor/cc-praxis.
One commit excluded (Mermaid diagram conversion). The skill's epic coherence
gates fired correctly — all three time windows failed Gate 3 (scope spread
≥ 4 distinct unrelated scopes), producing an all-standalones result with no
epics. This is the correct outcome for a repo developed across many parallel
feature areas in one sprint.

## How We Got Here

| Decision | Chosen | Why | Alternatives Rejected |
|---|---|---|---|
| All-standalones result | No epics created | Every time window contained 4+ unrelated scopes; Gates 2 and 3 enforce coherence | Forcing epics around date boundaries would have created collection buckets, not feature epics |
| 27 issues from 285 commits | Scope-based clustering + related-scope merging | Conventional commit scopes are a stronger signal than file paths; collapses facets of the same feature | Per-commit issues (285 tickets) or file-path grouping (noisier, less author-intent-aware) |
| 1 excluded commit | Mermaid diagram conversion only | Matches the "convert to Mermaid format" trivial exclusion example in the skill | Could have been included under a formatting/docs ticket |
| Sequential issue creation in bash | `create_and_close()` function + `${url##*/}` | Cleanest pattern for bulk sequential creation; no temp files; issue number extracted from URL | `gh issue create --json number` + jq; Python script |

## Where We're Going

The skill is validated and working. The next focus areas are:

**Next steps:**
- Run `git-commit` to commit `docs/retro-issues.md` (currently untracked)
- Write session handover (in progress)
- Optional: Step 10 (amend commit messages to add `Refs #N` footers) — not yet attempted

**Open questions:**
- Should `docs/retro-issues.md` be kept long-term or deleted after issue creation? (currently it's a permanent record of the mapping)
- Would the retro-issues output look different run against a repo with conventional commits *and* coherent epics? (this repo's wide scope prevented validation of the epic path)
- Is the `create_and_close()` bash pattern the right default in the skill, or should it offer a dry-run mode?

## Linked ADRs

*(No ADRs directly relevant to the retro-issues skill implementation — the skill was built incrementally without formal ADRs.)*

## Context Links

- Retrospective mapping: [docs/retro-issues.md](../retro-issues.md)
- Skill implementation: [skills/retro-issues/SKILL.md](../../skills/retro-issues/SKILL.md)
- GitHub issues created: mdproctor/cc-praxis#1–#27 (all closed)
