---
name: work-pause
description: >
  Use when interrupting current branch work to switch to something else — user
  says "work-pause", "pause this work", or "switch to a different issue".
  Supports a stack of paused branches. Pair with work-resume to restore.
---

# work-pause

Commits all work-in-progress, pushes an entry onto the pause stack on workspace
main, and switches both repos to their base branch. Supports multiple paused branches.

Uncommitted changes are always committed as a `WIP:` commit on the branch —
no stash used. On resume, the WIP commit is reset so work continues cleanly.

---

## Path Resolution (run first, always)

Run the bundled context script — no shell variable assignments, no CLAUDE.md scanning:
```bash
python3 ~/.claude/skills/project-init/ctx.py
```

Use `WORKSPACE`, `PROJECT`, `BASE_BRANCH`, `CURRENT_BRANCH` from the output as concrete strings.
`BASE_BRANCH` defaults to `main` if not declared in the project CLAUDE.md.

---

## Step 0 — Resolve paths

Read `$PROJECT` and `$WORKSPACE` from CLAUDE.md (see Path Resolution above).

---

## Step 1 — Validate state

```bash
ls "$WORKSPACE/design/.meta" 2>/dev/null || { echo "No .meta found — not on a working branch."; exit 1; }
BRANCH_NAME=$(grep "^branch:" "$WORKSPACE/design/.meta" | sed 's/branch: //')
ISSUE_N=$(grep "^issue:" "$WORKSPACE/design/.meta" | sed 's/issue: //')
```

Must be on a branch where `$WORKSPACE/design/.meta` exists.

---

## Step 2 — Commit WIP on project branch

```bash
PROJECT_DIRTY=$(git -C "$PROJECT" status --short | wc -l | tr -d ' ')
```

If `$PROJECT_DIRTY > 0`:
```bash
PAUSE_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
git -C "$PROJECT" add -A
git -C "$PROJECT" commit -m "WIP: paused $BRANCH_NAME at $PAUSE_TS"
WIP_COMMITTED=true
```

If clean: `WIP_COMMITTED=false` — no commit needed.

---

## Step 3 — Commit WIP on workspace branch

```bash
WORKSPACE_DIRTY=$(git -C "$WORKSPACE" status --short | grep -v "design/.pause-stack" | wc -l | tr -d ' ')
```

If `$WORKSPACE_DIRTY > 0`:
```bash
git -C "$WORKSPACE" add -A
git -C "$WORKSPACE" commit -m "WIP: paused $BRANCH_NAME at $PAUSE_TS"
WORKSPACE_WIP_COMMITTED=true
```

If clean: `WORKSPACE_WIP_COMMITTED=false`.

---

## Step 4 — Push branch state to remote

```bash
git -C "$PROJECT" push origin "$BRANCH_NAME" 2>/dev/null || echo "⚠️  Project push failed — continuing (WIP commit is local)"
git -C "$WORKSPACE" push origin "$BRANCH_NAME" 2>/dev/null || echo "⚠️  Workspace push failed — continuing"
```

Push failures are non-fatal — the WIP commit is safely on the local branch.

---

## Step 5 — Push pause entry onto stack (on workspace main)

```bash
git -C <WORKSPACE> checkout main
git -C <WORKSPACE> pull --rebase origin main
```

Push the entry using the stack script — no shell variable assignments or heredocs:
```bash
python3 ~/.claude/skills/project-init/stack.py push <WORKSPACE>/design/.pause-stack branch=<BRANCH_NAME> issue=<ISSUE_N> wip_project=<WIP_COMMITTED> wip_workspace=<WORKSPACE_WIP_COMMITTED>
```

Read `STACK_DEPTH` from output. Then commit and push:
```bash
git -C <WORKSPACE> add design/.pause-stack
git -C <WORKSPACE> commit -m "chore: pause <BRANCH_NAME> — stack depth <STACK_DEPTH>"
git -C <WORKSPACE> push
```

**If push fails: abort.** Remove the stack entry with:
```bash
python3 ~/.claude/skills/project-init/stack.py pop <WORKSPACE>/design/.pause-stack <BRANCH_NAME>
```
Then switch back to the branch. The pause stack on main must always be committed and pushed — it is the source of truth across sessions.

---

## Step 6 — Switch project repo to base branch

```bash
git -C "$PROJECT" checkout "$PROJECT_BASE_BRANCH"
```

Prompt before `pull --rebase` — not automatic.

---

## Step 7 — Confirm

```
⏸  Paused: <branch-name>  Issue: #<N>
   WIP committed: project=<yes|no>  workspace=<yes|no>
   Stack depth: <N>

You're on main — type work to resume this branch or start new work.
```

If stack depth > 3, add: `⚠️  Stack has <N> paused branches — consider closing some.`
