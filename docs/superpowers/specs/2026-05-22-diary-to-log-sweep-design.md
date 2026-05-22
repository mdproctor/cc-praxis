# Design: diary→log Subtype Sweep

**Date:** 2026-05-22
**Issue:** #96
**Branch:** issue-96-diary-to-log-sweep

## Context

The `note` subtype was renamed from `diary` to `log` during taxonomy work (refs #95). Skill files and the taxonomy definition were updated at that time. This sweep completes the rename by updating all remaining `subtype: diary` occurrences across the full `~/claude/` tree.

## Scope

### Frontmatter files (~275 files across 5 repos)

| Repo | Path | Approx count |
|------|------|-------------|
| `cc-praxis` | `docs/_posts/` | 15 |
| `mdproctor.github.io` | `_notes/` | ~236 |
| `drools` | `_posts/` | 3 |
| `hortora/hortora.github.io` | `_posts/` | 7 |
| `permuplate` | `_posts/` | 14 |

### Non-frontmatter targeted edits (10 files, all in `cc-praxis` unless noted)

| File | Nature of change |
|------|-----------------|
| `docs/blog/index.html:24` | Liquid filter `'diary'` → `'log'` |
| `tests/test_jekyll_pages.py` | 6 lines: descriptions + assertions |
| `tests/test_blog_frontmatter.py` | 4 valid-fixture lines + 1 intentionally-wrong fixture (`entry_type: log`) |
| `mdproctor.github.io/CLAUDE.md:43` | Example frontmatter block |
| `README.md:486` | Description text |
| `docs/guide.html:981` | Documentation prose |
| `scripts/validation/validate_blog_frontmatter.py:7` | Example comment |

### Do NOT change

- Descriptive uses of "diary voice", "diary entries", "write-blog as a diary skill" — these describe character, not taxonomy values
- `handover/SKILL.md` trigger description — "capture this session's work as a diary entry"
- `update-claude-md/SKILL.md` — "blog and diary entries"
- `docs/skills-catalog.md` trigger description — "add a diary entry"
- Archive documents: `docs/superpowers/specs/`, `docs/superpowers/plans/`, `adr/`, `_site/`
- `public/cc-praxis/plans/2026-04-14-*.md` — historical plan documents

## Implementation

### Phase 1: Batch script (frontmatter files)

A one-shot Python script at `/tmp/diary_to_log.py`:

**Algorithm:**
1. Walk `~/claude/` recursively, targeting `.md` files
2. Skip paths containing: `.git/`, `_site/`, `superpowers/specs/`, `superpowers/plans/`, `superpowers/snapshots/`, `adr/`
3. For each file:
   - Normalize CRLF → LF (guards against silent regex skip — GE-20260414-c12931)
   - Use `re.match(r'^---\n(.*?)\n---\n?(.*)', content, re.DOTALL)` to isolate frontmatter (guards against split-on-quoted-value — GE-20260521-df2a10)
   - Within frontmatter only: replace `^subtype: diary$` → `subtype: log` (whole-line match)
   - Write only if changed; preserve original line endings after write
4. Dry-run mode (default): print would-change list per repo, no writes
5. `--apply` flag: apply changes, print per-repo count

**Run sequence:**
```
python3 /tmp/diary_to_log.py          # dry-run: review list
python3 /tmp/diary_to_log.py --apply  # apply
```

### Phase 2: Targeted edits (non-frontmatter)

Direct edits to the 10 files listed above. All `diary` → `log` in value positions; descriptive prose left unchanged.

Key judgment call on `test_blog_frontmatter.py` line 75: change `'entry_type': 'diary'` to `'entry_type': 'log'` — demonstrates the same "subtype value in wrong field" mistake with the current valid subtype name.

### Phase 3: Test and commit

1. Run `python3 -m pytest tests/test_jekyll_pages.py tests/test_blog_frontmatter.py -v`
2. Commit per repo:
   - `cc-praxis`: `chore: sweep subtype diary→log (Closes #96)` — frontmatter + all targeted edits
   - `mdproctor.github.io`: `chore: sweep subtype diary→log (refs #96)`
   - `drools`: `chore: sweep subtype diary→log (refs #96)`
   - `hortora/hortora.github.io`: `chore: sweep subtype diary→log (refs #96)`
   - `permuplate`: `chore: sweep subtype diary→log (refs #96)`

## Garden GEs Applied

- **GE-20260414-c12931** — CRLF normalization before frontmatter regex: `content.replace('\r\n', '\n')`
- **GE-20260521-df2a10** — Use `re.match(r'^---\n(.*?)\n---\n?(...)', re.DOTALL)` not `str.split('---', 2)`

## Success Criteria

- [ ] Dry-run output reviewed and confirmed
- [ ] `grep -rn "subtype: diary" ~/claude/` returns only archive/descriptive hits
- [ ] `cc-praxis` tests pass
- [ ] All 5 repos committed
- [ ] Issue #96 closed
