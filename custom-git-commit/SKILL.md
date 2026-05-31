---
name: custom-git-commit
description: >
  Use when the user says "commit" in a type: custom project (working groups,
  research, documentation, etc.). Only applies to type: custom — all other
  project types route elsewhere.
slash-command: false
---

# Custom Project Commit

Conventional commit workflow for type: custom projects. Follows the same
conventions as `git-commit` with CLAUDE.md sync.

## Prerequisites

**This skill builds on [`git-commit`]**.

Apply all rules from:
- **`git-commit`**: Subject line format (imperative mood, max 50 chars), Conventional Commits 1.0.0 specification, always wait for explicit user confirmation before committing, never add attribution unless user explicitly requests it

---

## Workflow

### Step 0 — Verify type: custom

```bash
grep "type:\|Type:" CLAUDE.md 2>/dev/null | head -1
```

If CLAUDE.md is missing or declares a different type → stop and redirect to
the correct commit skill.

---

### Step 0b — Offer issue tracking (when absent)

```bash
grep -q "Issue tracking.*enabled" CLAUDE.md 2>/dev/null && echo "exists" || echo "absent"
```

If absent, offer to enable via `issue-workflow` (Phase 0). If declined, continue.

---

### Step 1 — Inspect staged changes

```bash
git diff --staged --stat
git diff --staged
```

If nothing staged → stop and ask the user to stage files first.

---

### Step 2 — Generate commit message

Analyze staged changes and draft a conventional commit message. Hold it.

---

### Step 3 — Sync CLAUDE.md

Invoke `update-claude-md`, passing the staged diff. Hold any proposals.

---

### Step 4 — Present and confirm

```
## Staged files
<git diff --staged --stat>

## Proposed commit message
<type>[scope]: <description>

## Proposed CLAUDE.md updates (if any)
<update-claude-md output>
```

> "Does this look good? Reply **YES** to commit, or tell me what to adjust."

---

### Step 5 — Commit (only after YES)

Apply CLAUDE.md changes if proposed, then:

```bash
git commit -m "<subject>" -m "<body if any>"
git log --oneline -1
```

---

## Skill Chaining

**Invoked by:** `git-commit` when `type: custom` declared; [`adr`], [`idea-log`], [`write-content`] to commit their artifacts

**Invokes:** [`update-claude-md`] — automatic if CLAUDE.md exists; [`issue-workflow`] — if Work Tracking not yet configured
