# cc-praxis — Design Snapshot: Issue Tracking Infrastructure & v1.0.1
**Date:** 2026-04-07
**Topic:** Work Tracking fully wired across all commit skills; v1.0.1 shipped
**Supersedes:** *(none)*
**Superseded by:** *(leave blank — filled in if this snapshot is later superseded)*

---

## Where We Are

cc-praxis now has full GitHub issue tracking infrastructure operational end-to-end. Work Tracking is configured in cc-praxis, permuplate, sparge, remotecc, and starcraft. Step 0b (prompt for issue tracking when absent) now exists in all four commit skills (git-commit, java-git-commit, blog-git-commit, custom-git-commit). v1.0.1 is tagged with auto-generated release notes from 45 closed issues.

## How We Got Here

Key decisions made to reach this point:

| Decision | Chosen | Why | Alternatives Rejected |
|---|---|---|---|
| Step 0b in all commit skills | Duplicate the step across java/blog/custom | Each skill is independent; no inheritance mechanism in skill system | Single place in git-commit only (gap: java repos never saw the prompt) |
| retro-issues.md retention | Commit as permanent audit trail, never delete | GitHub issues record outcomes; the file records grouping rationale | Deleting after issue creation (loses the why) |
| ADR date auto-populate | Explicit instruction in Step 3, no user prompt | Date always available in session context; prompting adds no value | Leave YYYY-MM-DD placeholder (was broken) |
| v1.0.1 release notes | `gh release create --generate-notes` | Auto-generates from closed issues; zero maintenance | Manual CHANGELOG.md |

## Where We're Going

**Next steps:**
- #36 Design project memory architecture (design-snapshot as indexed folder + cross-tool meta-index)
- Run retro-issues on remotecc and starcraft when those projects have real work to map
- Garden DEDUPE sweep — 31 entries merged since last sweep, drift threshold exceeded

**Open questions:**
- Should `issue-workflow` Phase 1 fire automatically at session start (when no active epic exists) or only when user explicitly starts implementation? Currently triggers on implementation signals — right threshold?
- Does the `When Work Tracking Is Configured` guidance section in cc-praxis CLAUDE.md need to reference Phase 1/2/3 explicitly, or is it appropriately kept as a simplified summary?

## Linked ADRs

*(No ADRs created this session — all changes were workflow fixes, not architectural decisions.)*

## Context Links

- Epic closed: mdproctor/cc-praxis#30
- Release: https://github.com/mdproctor/cc-praxis/releases/tag/v1.0.1
- Related snapshot: [2026-04-07-retro-issues-validation](2026-04-07-retro-issues-validation.md)
