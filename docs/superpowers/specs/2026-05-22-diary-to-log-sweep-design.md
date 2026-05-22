# Design: Revert log→diary Subtype (issue #96)

**Date:** 2026-05-22 (revised same day)
**Issue:** #96
**Branch:** issue-96-diary-to-log-sweep

## Decision

The rename of `subtype: diary` → `subtype: log` (refs #95) was a mistake. "Log" implies
dry, chronological, technical records. Write-blog produces personal, narrative,
in-the-moment writing — that is a diary, not a log. The taxonomy value should match
the character of the content and the natural English word for it.

This issue now reverts the partial rename rather than completing it.

## Eventual Consistency

Active Claude sessions that loaded the skills before this fix will continue generating
`subtype: log` entries until they reload. The revert script must therefore be:
- **Kept** in `scripts/` (not a throwaway `/tmp/` script)
- **Re-run periodically** on posts directories until all sessions have picked up the updated skills
- **Idempotent** — files already at `subtype: diary` are untouched

## Scope

### Frontmatter files to revert (~108 files, `subtype: log` → `subtype: diary`)

| Repo / path | Count |
|---|---|
| `mdproctor.github.io/_notes/` | 54 |
| `public/casehub/engine/blog/` | 8 |
| `public/casehub/work/blog/` | 6 |
| `public/casehub/qhorus/blog/` | 6 |
| `public/quarkmind/blog/` | 5 |
| `public/casehub/ledger/blog/` | 5 |
| `public/casehub/clinical/blog/` | 4 |
| `drools/blog/` | 4 |
| `public/casehub/claudony/blog/` | 3 |
| `public/casehub/blog/` | 3 |
| `public/casehub/devtown/blog/` | 2 |
| `public/casehub/aml/blog/` | 2 |
| `hortora/hortora.github.io/_posts/` | 2 |
| `cc-praxis/docs/_posts/` | 2 |
| `public/cc-praxis/blog/` | 1 |

### Skill and doc files to revert (4 files in `cc-praxis`)

| File | What reverts |
|---|---|
| `write-blog/SKILL.md` | 3 lines: `subtype: log` → `subtype: diary` in frontmatter examples and success criteria |
| `publish-blog/SKILL.md` | 1 line: subtype enumeration |
| `docs/skills-catalog.md` | 1 line: subtype field description |
| `docs/content-taxonomy-article-notes.md` | 1 line: taxonomy table |

### Do NOT change

- Everything already at `subtype: diary` — untouched
- "diary voice", "diary entries", "living diary" throughout skill files — correct as-is
- `public/cc-praxis/HANDOFF.md` — prose reference to the old sweep direction, not frontmatter
- Archive documents: `specs/`, `plans/`, `adr/`, `_site/`

## Implementation

### Phase 1: Revert script (`scripts/revert_diary_subtype.py`)

Permanent script in `scripts/` for re-running until sessions reach eventual consistency.

**Algorithm:**
1. Walk `~/claude/` recursively, targeting `.md` files
2. Skip paths containing: `.git/`, `_site/`, `superpowers/specs/`, `superpowers/plans/`,
   `superpowers/snapshots/`, `adr/`, `HANDOFF.md`
3. For each file:
   - Normalize CRLF → LF (GE-20260414-c12931)
   - Use `re.match(r'^---\n(.*?)\n---\n?(.*)', content, re.DOTALL)` to isolate frontmatter (GE-20260521-df2a10)
   - Within frontmatter only: replace `^subtype: log$` → `subtype: diary` (whole-line)
   - Write only if changed
4. Dry-run (default): print would-change list per repo, no writes
5. `--apply`: apply changes, print per-repo count

**Run sequence:**
```bash
python3 scripts/revert_diary_subtype.py          # dry-run
python3 scripts/revert_diary_subtype.py --apply  # apply
```

**Re-run as needed** on posts directories while sessions reach eventual consistency:
```bash
python3 scripts/revert_diary_subtype.py --apply  # idempotent, safe to repeat
```

### Phase 2: Skill and doc targeted edits

Direct edits to the 4 files listed above. These are the source of truth — once updated
and synced, new sessions will generate `subtype: diary` correctly.

Sync skills immediately after editing:
```bash
python3 scripts/claude-skill sync-local --all -y
```

### Phase 3: Test and commit

1. Run `python3 -m pytest tests/test_jekyll_pages.py tests/test_blog_frontmatter.py -v`
   (tests already expect `diary` — no test changes needed)
2. Commit per git repo — identify repo roots from the path list above
3. Commit message: `chore: revert subtype log→diary (refs #96)` per repo;
   `cc-praxis` commit: `chore: revert subtype log→diary (Closes #96)`

## Garden GEs Applied

- **GE-20260414-c12931** — CRLF normalization before frontmatter regex
- **GE-20260521-df2a10** — Use `re.match(r'^---\n(.*?)\n---\n?(...)', re.DOTALL)` not `str.split('---', 2)`

## Success Criteria

- [ ] Dry-run output reviewed and confirmed
- [ ] Skill files updated and synced via `sync-local`
- [ ] `grep -rn "subtype: log" ~/claude/` returns only HANDOFF.md and archive hits
- [ ] `cc-praxis` tests pass without modification
- [ ] All affected git repos committed
- [ ] Issue #96 closed
- [ ] Script retained in `scripts/` for re-runs during eventual consistency period
