---
name: project-init
description: >
  Use when project setup needs to be verified or completed — invoked
  automatically at session start (via hook) and by work-start before
  any branch work begins. NOT invoked directly by users.
slash-command: false
---

# project-init

Normalised setup gateway. Both the session hook and `work-start` converge
here — so the entry point doesn't matter, every session hits the same
initialisation checks.

**Fast path:** if everything is already set up or previously declined, return
immediately with no output.

**Slow path:** detect what's missing, run setup steps in order, write decline
flags to CLAUDE.md when user says no so they are never asked again.

---

## IntelliJ MCP routing — always apply

Before any other check: if both `mcp__intellij-index__*` and `mcp__intellij__*` tools are
visible in this session, note this rule and apply it throughout the session:

- **`mcp__intellij-index__*`** — use for ALL code navigation, file search, diagnostics, and
  opening projects. Pass `project_path` to auto-open any closed project. Never ask the user
  to open a project manually.
- **`mcp__intellij__*`** — use only for build/run, terminal, and formatting. Cannot open projects.

This applies regardless of what work follows — spec writing, code review, implementation, or
exploration. The rule is in effect for the whole session once noted here.

---

## Fast-path exit

Run this first. If all conditions are met, return immediately — do nothing else.

```bash
python3 ~/.claude/skills/project-init/ctx.py
```

If `CLAUDE_OK=yes` AND `WORKSPACE_OK=yes` AND `ISSUES_STATUS` is not `absent` → return silently.

---

## Checks (run in order when fast path does not exit)

### Check 1 — CLAUDE.md with project type

Read `CLAUDE_OK` and `PROJECT_TYPE` from the ctx.py output (already run in fast-path).

Also check whether the file exists at all:
```bash
[ -f "CLAUDE.md" ] && echo "exists" || echo "missing"
```

| State | Action |
|-------|--------|
| CLAUDE.md missing | Ask user for project type, create CLAUDE.md inline |
| CLAUDE.md exists, `CLAUDE_OK=no` | Ask user to choose type, insert `## Project Type` section |
| `CLAUDE_OK=yes` | ✅ Continue |

**Project type choices:** `skills` · `java` · `blog` · `custom` · `generic`

When creating: use the minimal template — project type declaration plus
build/test commands if detectable from the repo (pom.xml, package.json,
pyproject.toml). Do not pad with boilerplate.

CLAUDE.md creation is required. If the user refuses, hard stop — no other
check can run without a project type.

---

### Check 2 — Workspace

Read `WORKSPACE_OK` and `WORKSPACE_DECLINED` from the ctx.py output (already run in fast-path).

| State | Action |
|-------|--------|
| `WORKSPACE_OK=yes` (symlinks present or declined) | ✅ Continue |
| `WORKSPACE_DECLINED=yes` | ✅ Skip silently |
| `WORKSPACE_OK=no` and `WORKSPACE_DECLINED=no` | Offer (see below) |

**Offer:**

> **No workspace configured for this project.**
>
> A workspace keeps methodology artifacts (plans, specs, handovers, blog
> entries) separate from the project repo. Set one up now? **(YES / n)**

- **YES** → invoke `workspace-init`. It handles git hooks, DESIGN.md stub,
  work tracking, and superpowers as part of its own flow. Once complete,
  skip Checks 3 and 4 — workspace-init already offered them.
- **n** → write `workspace: declined` to CLAUDE.md (see below), continue.

**Writing the decline flag:**

Add to CLAUDE.md under `## Project Type` (or append if section not found):

```
workspace: declined
```

This is a single-line property, not a section header. Place it directly
below the project type line:

```markdown
## Project Type

type: java
workspace: declined
```

---

### Check 3 — Work Tracking

Skip if: workspace was just set up this session (workspace-init offered it),
or `Issue tracking: declined` is already in CLAUDE.md.

Read `ISSUES_STATUS` from the ctx.py output (already run in fast-path). Values: `enabled` | `declined` | `absent`.

| State | Action |
|-------|--------|
| `enabled` | ✅ Continue |
| `declined` | ✅ Skip silently |
| `absent` | Offer (see below) |

**Offer:**

> **No issue tracking configured.**
>
> Links every commit to a GitHub issue — enforces issue creation before
> coding, enables commit split detection, generates release notes.
> Set it up now? **(YES / n)**

- **YES** → invoke `issue-workflow` (Phase 0 runs automatically)
- **n** → write `Issue tracking: declined` into `## Work Tracking` in CLAUDE.md:

```markdown
## Work Tracking

Issue tracking: declined
```

---

### Check 4 — Superpowers

Skip if: workspace was just set up this session (workspace-init offered it).

```bash
python3 -c 'import json,os; s=json.load(open(os.path.expanduser("~/.claude/settings.json"))); print("installed" if "superpowers@claude-plugins-official" in s.get("enabledPlugins",{}) else "missing")' 2>/dev/null || echo "missing"
```

| State | Action |
|-------|--------|
| Installed | ✅ Continue |
| Missing | Notify once, do not block |

**If missing:**

> **Superpowers not installed.** Install with: `/plugin install superpowers`
>
> Adds structured TDD, debugging, brainstorming, and code review workflows.

Do not write a decline flag for superpowers — it is advisory only and does
not affect workflow correctness. Show once per session, never block.

---

## Return states

| Outcome | What happens next |
|---------|-------------------|
| Fast path — all set up or declined | Return silently |
| Setup completed | Return silently |
| Workspace declined — flag written | Return, caller continues without workspace |
| Issue tracking declined — flag written | Return silently |
| CLAUDE.md creation refused | Hard stop |

---

## Resetting a decline

If a user changes their mind:
- **Workspace:** remove `workspace: declined` from CLAUDE.md — project-init
  will offer again next session, or they can say "set up workspace"
- **Issue tracking:** change `Issue tracking: declined` to `Issue tracking: enabled`
  in `## Work Tracking`, or say "set up issue tracking" to invoke the skill directly

---

## Integration points

### Session hook (`check_project_setup.sh`)

Output at session start:

```
🔧 Invoke the project-init skill to verify this project is set up before proceeding.
```

### work-start

Invoke project-init as Step 0 before path resolution. Only continue once
project-init returns. If workspace was declined, proceed in single-repo mode.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping fast-path check | Runs prompts on every session even when set up | Always check all three conditions first |
| Not writing decline flag | User gets asked every session forever | Write to CLAUDE.md on every decline |
| Blocking on superpowers | User must manually install it | Notify only, always continue |
| Running Checks 3+4 after workspace-init | workspace-init already offered them | Skip if workspace-init ran this session |

---

## Skill Chaining

**Invoked by:**
- Session hook (`check_project_setup.sh`) — every session start
- `work-start` — Step 0, before path resolution

**Invokes:**
- `workspace-init` — if workspace missing and user accepts
- `issue-workflow` (Phase 0) — if issue tracking missing and user accepts

**Does not invoke:**
- Any branch or commit skill — setup only
