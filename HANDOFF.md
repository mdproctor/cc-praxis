# Handover — 2026-04-09

**Head commit:** `7e68bd3` — docs: log idea — marketplace aggregation for external skill repos
**Previous handover:** `git show HEAD~1:HANDOFF.md` | diff: `git diff HEAD~1 HEAD -- HANDOFF.md`

## What Changed This Session

- **Hortora decommissioned from cc-praxis** — blog posts, design docs, ADR, images removed (all confirmed in `Hortora/spec` first); issue #47 closed
- **Garden DEDUPE** — 100 pairs checked, 18 related, 82 distinct, drift counter reset; cross-refs added to rename-refactoring.md, tmux.md, playwright.md, cdi.md, profiles.md
- **GARDEN.md deleted** — was always empty since v1→v2 migration; superseded by Hortora
- **git-commit skill** — added Step 3b: squash check for consecutive same-type unpushed commits
- **Marketplace aggregation idea** logged — `docs/ideas/IDEAS.md`
- **Repo renamed** — `~/claude/skills` → `~/claude/cc-praxis`; CLAUDE.md updated; project memory migrated; `settings.local.json` paths updated via sed
- **Hortora org sorted** — `soredium`, `spec`, `hortora.github.io` all local+GitHub; `spec` pushed for first time; `Hortora/spec/HANDOFF.md` written as Hortora entry point
- **Hortora/soredium issues** — #1 (scaffold), #2 epic (forage+harvest), #3 (marketplace), #4 (forage skill), #5 (harvest skill)
- **GE-0124 submitted** — `settings.local.json` stale paths on project rename

## State Right Now

- `cc-praxis` main clean, pushed, no open issues
- `knowledge-garden`: 11 submissions pending (unmerged), GARDEN.md gone
- `hortora/spec`: pushed, HANDOFF.md at root — start Hortora Claude here
- `hortora/soredium`: scaffold only, issues #1–#5 open
- `hortora/hortora.github.io`: live, complete, no work needed

## Immediate Next Steps

1. **New topic (not yet started)** — coworker collaboration model and separating CLAUDE.md from project repos into workspace repos
2. **Hortora work** — open Claude in `~/claude/hortora/spec/`, read HANDOFF.md, begin soredium #3
3. **Knowledge garden** — merge 11 pending submissions when convenient

## Open Questions

- Coworker collaboration + CLAUDE.md workspace separation (next topic)
- cc-praxis marketplace aggregation of soredium — idea logged, not decided

## References

| Context | Where |
|---------|-------|
| Hortora full context | `~/claude/hortora/spec/HANDOFF.md` |
| Marketplace aggregation idea | `docs/ideas/IDEAS.md` |
| Latest blog | `docs/blog/2026-04-08-mdp01-words-matter-then-gardens-grow.md` |
| Knowledge garden submissions | `~/claude/knowledge-garden/submissions/` (11 pending) |
