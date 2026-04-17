# Handover — 2026-04-14

**Branch:** main
**Head:** ae6c63e

---

## What Changed This Session

**Blog entry types** — article/note taxonomy shipped. New frontmatter fields (`entry_type`, `subtype`, `projects`, `tags`) on all 14 blog entries. `validate_blog_frontmatter.py` added (now 19 validators). `yaml_utils.py` upgraded from homemade parser to PyYAML.

**Workspace routing design** — three-layer routing config specced and implemented. Targets: `project`, `workspace`, `alternative <path>`. Global default in `~/.claude/CLAUDE.md ## Routing`. `epic-close` reads all three layers with routing preview before execution. Workspace-init template shows routing section. SHA baseline ratchet bug documented: when `design → workspace`, epic-start must record workspace/main HEAD SHA.

**Health sweeps (×2)** — fixed `garden`→`forage` in README (5 sections), web app stats bar (44→48, 17→19, 295→1016), blog INDEX.md (1→14 entries), CLAUDE.md tier list, validator counts across all primary docs.

**Test coverage: 446 → 1016** — 22 new test files across two passes. All 19 registered validators now covered. Key TDD findings captured to forage: `validate_links` uses `requests.get` not `requests.head`; `validate_cross_document` writes to stderr; `validate_examples` silently skips `{...}` JSON as template.

**Forage: 6 entries submitted** — PR [Hortora/garden#43](https://github.com/Hortora/garden/pull/43). Three gotchas (worktree cwd, enum identity, sed comment), one technique (TDD agents read source first), two undocumented (requests.get, json template skip).

**Issues:** `#57` closed (test coverage). Open: `#50` blog pipeline, `#52` publish-blog, `#53` Jekyll pages, `#54` workspace routing epic, `#56` epic-start SHA baseline.

---

## Immediate Next Step

**Smoke tests** (deferred since yesterday):
1. `/epic` (start) → verify `design/JOURNAL.md` + `design/.meta` created with SHA
2. `java-update-design` → verify journal entry written (not project DESIGN.md)
3. `/epic` (close, dry run) → verify three-layer routing preview shown correctly

Then: resume issue/epic creation from yesterday's interrupted flow (we got as far as creating epics #50 and #54 before the workspace routing insight interrupted).

---

## References

| Context | Where |
|---------|-------|
| Blog entry types spec | `docs/superpowers/specs/2026-04-14-blog-entry-types-design.md` |
| Workspace routing spec | `docs/superpowers/specs/2026-04-14-workspace-routing-design.md` |
| Blog entry (this session) | `docs/_posts/2026-04-14-mdp02-closing-gaps.md` |
| Open epics | GitHub: #50 (blog pipeline), #54 (workspace routing) |
| Previous handover | `git show HEAD~1:HANDOFF.md` |
