# Handover — 2026-04-07

**Head commit:** `410be6e` — docs: add project blog entry 2026-04-07-mdp02-issue-tracking-live
**Previous handover:** `git show HEAD~1:HANDOVER.md` | diff: `git diff HEAD~1 HEAD -- HANDOVER.md`

## What Changed This Session

- **Issue tracking bootstrapped for cc-praxis** — Phase 0+1 of `issue-workflow` complete; labels created, CLAUDE.md updated, epic #30 (Cut v1.0.1 release) created and closed
- **Step 0b gap fixed** — `java-git-commit`, `blog-git-commit`, `custom-git-commit` now all include Step 0b; previously only `git-commit` offered the Work Tracking prompt
- **Step 0b tested end-to-end** — remotecc and starcraft created on GitHub, Work Tracking configured on both via the full Phase 0 flow
- **Garden merged** — 31 submissions integrated (GE-0042–GE-0073); 9 new files, 9 updated; GE-0053 3-way conflict resolved; last assigned ID: GE-0073
- **ADR date auto-populate fixed** — one instruction added to `adr/SKILL.md` Step 3
- **retro-issues.md retention defined** — skill now says commit as permanent audit trail, never delete
- **retro-issues gap analysis** — 184 commits checked; 9 genuine gaps found (20 false positives from previous run); issues #37–#45 created and closed
- **v1.0.1 tagged** — `gh release create v1.0.1 --generate-notes` from 45 closed issues

## State Right Now

- `main` clean, everything committed and pushed
- Garden: drift counter at 31 (threshold: 10) — DEDUPE recommended before next merge session
- Open issues: #36 (Design project memory architecture) — standalone, intentionally deferred
- remotecc and starcraft: Work Tracking configured, GitHub remotes set up, no open issues yet

## Immediate Next Step

Start #36 — design project memory architecture: (1) design-snapshot as indexed folder with `INDEX.md` modelled on GARDEN.md dual-index, (2) cross-tool meta-index for lazy referencing across garden/blog/snapshot. Create an ADR or design doc before touching any files.

## Open Questions / Blockers

- Garden DEDUPE overdue (31 entries since last sweep) — run before next garden merge session
- remotecc and starcraft have no open issues yet — next session in those repos should run `issue-workflow` Phase 1

## References

| Context | Where | Retrieve with |
|---------|-------|---------------|
| Design snapshot | `docs/design-snapshots/2026-04-07-issue-tracking-and-v1.0.1.md` | `cat` |
| Blog entry | `docs/blog/2026-04-07-mdp02-issue-tracking-live.md` | `cat` |
| retro-issues audit trail | `docs/retro-issues.md` | `cat` |
| v1.0.1 release | github.com/mdproctor/cc-praxis/releases/tag/v1.0.1 | `gh release view v1.0.1` |
| Previous handover | git history | `git show HEAD~1:HANDOVER.md` |
