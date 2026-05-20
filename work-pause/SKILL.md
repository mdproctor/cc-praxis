---
name: work-pause
description: >
  Use when interrupting current branch work to switch to something else — user
  says "work-pause", "pause this work", or "switch to a different issue". Only
  one paused branch at a time. Pair with work-resume to restore.
---

# work-pause

Saves context, stashes any uncommitted changes, records a pause marker on
workspace main, and switches both repos to main.

**Only one paused branch at a time.** If `.paused` already exists, this skill
stops immediately.

---

## Path Resolution (run first, always)

```bash
if [ -L "proj" ]; then
  WORKSPACE=$(git rev-parse --show-toplevel 2>/dev/null)
  PROJECT=$(readlink -f proj)
else
  WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md 2>/dev/null | head -1 | sed 's/.*`\(.*\)`.*/\1/')
  PROJECT=$(grep "^Run \`add-dir" CLAUDE.md 2>/dev/null | head -1 | sed "s/.*add-dir //; s/\`.*//")
fi
```

---

## Step 0 — Resolve paths

Read `$PROJECT` and `$WORKSPACE` from CLAUDE.md (see Path Resolution above).

---

## Step 1 — Validate state

```bash
ls "$WORKSPACE/design/.meta" 2>/dev/null || { echo "No .meta found — not on a working branch."; exit 1; }
ls "$WORKSPACE/design/.paused" 2>/dev/null && { echo "⚠️ Already paused. Use work-resume first."; exit 1; }

BRANCH_NAME=$(grep "^branch:" "$WORKSPACE/design/.meta" | sed 's/branch: //')
```

Must be on a branch where `$WORKSPACE/design/.meta` exists.
If `.paused` already exists: hard stop — only one paused branch at a time.

---

## Step 2 — Handle uncommitted changes

```bash
# Use wc -l — grep -c exits 1 on no-match and outputs "0", causing || echo 0 to produce "0\n0"
PROJECT_DIRTY=$(git -C "$PROJECT" status --short | wc -l | tr -d ' ')
WORKSPACE_DIRTY=$(git -C "$WORKSPACE" status --short | wc -l | tr -d ' ')
```

If either is dirty:
```
Uncommitted changes found in:
  project:   <N files>
  workspace: <N files>
Stash them? (y/n)
  n → abort (commit or discard changes first)
```

If y:
```bash
STASH_PROJECT=none
STASH_WORKSPACE=none

if [ "$PROJECT_DIRTY" -gt 0 ]; then
  stash_out=$(git -C "$PROJECT" stash)
  echo "$stash_out" | grep -q "Saved working" && STASH_PROJECT="stash@{0}"
fi

if [ "$WORKSPACE_DIRTY" -gt 0 ]; then
  stash_out=$(git -C "$WORKSPACE" stash)
  echo "$stash_out" | grep -q "Saved working" && STASH_WORKSPACE="stash@{0}"
fi
```

The stash output is checked to confirm something was actually saved before recording
`stash@{0}` — `git stash` exits 0 even when there is nothing to stash ("No local changes
to save"), which would otherwise record a stale reference pointing to a previous stash.

**Warning to user:** If you run `git stash` or `git stash pop` manually on either
repo before resuming, the recorded stash position will shift and restoration will
fail. Use `work-resume` before any manual stash operations on these repos.

---

## Step 3 — Record pause in .meta (atomic with Step 4)

```bash
PAUSE_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

cat >> "$WORKSPACE/design/.meta" << EOF
paused: true
paused-at: $PAUSE_TS
stash-project: $STASH_PROJECT
stash-workspace: $STASH_WORKSPACE
EOF

git -C "$WORKSPACE" add design/.meta
git -C "$WORKSPACE" commit -m "chore($BRANCH_NAME): pause"
git -C "$WORKSPACE" push
```

**If push fails: abort before Step 4.** Do not write `.paused` to main.
This ensures `.paused` on main always corresponds to a committed pause record
in `.meta` on the branch.

---

## Step 4 — Write .paused to workspace main

```bash
# Do NOT stash again — workspace stash already on stack from Step 2 if applicable
git -C "$WORKSPACE" checkout main
git -C "$WORKSPACE" pull --rebase origin main

mkdir -p "$WORKSPACE/design"
cat > "$WORKSPACE/design/.paused" << EOF
branch: $BRANCH_NAME
paused-at: $PAUSE_TS
EOF

git -C "$WORKSPACE" add design/.paused
git -C "$WORKSPACE" commit -m "chore: pause marker for $BRANCH_NAME"
git -C "$WORKSPACE" push
```

---

## Step 5 — Switch project repo to main

```bash
git -C "$PROJECT" checkout main
```

Check if remote is ahead — prompt before pulling. Not automatic.

---

## Step 6 — Confirm

```
⏸  Paused: <branch-name>  Both repos now on main.
   Stash: project=<stash@{N} | none>  workspace=<stash@{N} | none>

Resume with: work-resume
```
