---
name: sync-local
description: >
  Use when the user wants to sync installed skills to the latest version from
  the cloned repository — says "sync skills", "update installed skills",
  "sync local", or invokes /sync-local. DEV-ONLY: requires a cloned
  repository with scripts/claude-skill on PATH. Not available to marketplace
  plugin installs.
---

# Sync Local Skills

**Developer skill — cloned repository only.**

Copies all skills (or a named subset) from this repository into
`~/.claude/skills/` so the installed versions match the current source.
Run this after editing any skill.

This skill is intentionally excluded from `marketplace.json` and the web
installer. Marketplace users do not have `scripts/claude-skill` and will
never see this skill. It is only available to developers working from a
clone of this repository.

---

## Workflow

### Sync all skills

```bash
python3 scripts/claude-skill sync-local --all -y
```

### Sync a specific skill

```bash
python3 scripts/claude-skill sync-local <skill-name> -y
```

Example: `python3 scripts/claude-skill sync-local write-blog -y`

### After syncing

The updated skills are immediately available to Claude Code — no restart
needed. Confirm with:

```bash
ls ~/.claude/skills/
```

---

## When to run

- After editing any `SKILL.md` file
- After adding a new skill
- After pulling changes from the remote that include skill edits

The `git-commit` workflow for this repository calls sync automatically as
part of the pre-commit checklist. Running `/sync-local` manually is useful
mid-session when you want to test a skill edit without committing first.

---

## Skill Chaining

**Invoked by:** User directly after editing skills; also referenced in the
pre-commit checklist in CLAUDE.md

**Invokes:** Nothing

**Dev-only:** Not in any bundle, not in marketplace.json, not in README.md.
Only available in cloned repository environments.
