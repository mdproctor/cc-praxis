---
name: dependency-update
description: >
  Use when the user says "bump a version", "upgrade dependencies", "check for
  newer versions", "add a dependency", or "run audit" — for Java/Maven,
  TypeScript/npm, or Python/pip projects. Routes to the correct package manager
  based on project type declared in CLAUDE.md.
---

# Dependency Update

Reads project type, then loads the package-manager-specific workflow.

## Step 1 — Detect project type

```bash
python3 ~/.claude/skills/project-init/ctx.py
```

Read `PROJECT_TYPE` from the output.

Extract: `java` | `ts` | `python`

If type is missing or `generic`, inspect files:
- `pom.xml` present → treat as `java`
- `package.json` present → treat as `ts`
- `pyproject.toml` or `requirements.txt` present → treat as `python`

## Step 2 — Load package manager workflow

| Project type | File to read |
|---|---|
| `java` | `~/.claude/skills/dependency-update/maven.md` |
| `ts` | `~/.claude/skills/dependency-update/npm.md` |
| `python` | `~/.claude/skills/dependency-update/pip.md` |

Read the file, then execute the workflow it describes.

## Skill Chaining

**Invoked by:** User directly — "bump versions", "check for updates", "add dependency"

**Invokes:** [`adr`] when major version upgrades warrant recording; [`git-commit`] after successful updates
