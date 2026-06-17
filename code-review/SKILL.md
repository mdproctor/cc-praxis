---
name: code-review
description: >
  Use when the user says "review the code", "check these changes", "review
  this", "look at staged changes", or invokes /code-review. Also invoked
  automatically by git-commit skills if no review has been done this session.
  Applies to Java/Quarkus, TypeScript, and Python projects.
---

# Code Review

Reads the project type, then loads the appropriate language-specific
review checklist. Universal review principles apply to all types.

## Step 0 — Load universal principles

**Load `~/.hortora/garden/approaches/code-review.md`** before proceeding.
All review severity models, reporting formats, and workflow steps are defined there.

## Step 1 — Detect project type

```bash
python3 ~/.claude/skills/project-init/ctx.py
```

Read `PROJECT_TYPE` from the output.

Extract: `java` | `ts` | `python` | `generic`

If type is missing or `generic`, inspect staged files:
- `.java` files or `pom.xml` changed → treat as `java`
- `.ts` / `.tsx` files changed → treat as `ts`
- `.py` files changed → treat as `python`
- Mixed → flag and ask user which review to run

## Step 2 — Load language-specific checklist

| Project type | File to read |
|---|---|
| `java` | `~/.claude/skills/code-review/java.md` |
| `ts` | `~/.claude/skills/code-review/typescript.md` |
| `python` | `~/.claude/skills/code-review/python.md` |

Read the file, then execute the review workflow it describes.

## Skill Chaining

**Invoked by:** [`java-dev`], [`ts-dev`], [`python-dev`] before committing; [`java-git-commit`] when no review has been run this session

**Invokes:** [`security-audit`] for auth/payment/PII code (offered, not automatic); [`git-commit`] after approval if user wants to commit
