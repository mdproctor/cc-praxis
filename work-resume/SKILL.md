---
name: work-resume
description: >
  Use when returning to a paused branch — user says "work-resume", "resume",
  or "go back to that branch". Reads the pause stack on workspace main and
  lets the user pick which branch to resume. Rebases onto current main before
  restoring WIP. Must be invoked from main.
---

# work-resume

Resumes a paused branch from the stack: lets the user pick, rebases the branch
onto current main (picking up any work that landed since it was paused), resets
the WIP commit to restore working state, removes the entry from the stack.

---

## Path Resolution (run first, always)

```bash
PROJECT=$(grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //')
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md | head -1 | sed 's/.*`\(.*\)`.*/\1/')
```

---

## Step 0 — Resolve paths

Read `$PROJECT` and `$WORKSPACE` from CLAUDE.md (see Path Resolution above).

---

## Step 1 — Read pause stack

```bash
STACK_FILE="$WORKSPACE/design/.pause-stack"
[ -f "$STACK_FILE" ] || { echo "Nothing to resume — pause stack is empty."; exit 1; }
grep -q "^- branch:" "$STACK_FILE" || { echo "Nothing to resume — pause stack is empty."; exit 1; }
```

Parse all entries. Each entry has: `branch`, `issue`, `paused`, `wip_project`, `wip_workspace`.

---

## Step 2 — Pick branch (if stack depth > 1)

If only one entry: auto-select it, no prompt.

If multiple entries, show the stack (most recent last = shown at bottom):
```
Paused branches:
  1. issue-94-work-lifecycle   #94   paused 3 days ago   "WIP committed"
  2. issue-87-api-refactor     #87   paused 1 week ago   "WIP committed"

Resume which? (1 / 2)
```

Set `$RESUME_BRANCH`, `$RESUME_WIP_PROJECT`, `$RESUME_WIP_WORKSPACE` from selected entry.

---

## Step 3 — Verify branch exists

```bash
git -C "$PROJECT" rev-parse --verify "$RESUME_BRANCH" &>/dev/null \
  || { echo "⚠️ $RESUME_BRANCH not found in project repo."; exit 1; }
git -C "$WORKSPACE" rev-parse --verify "$RESUME_BRANCH" &>/dev/null \
  || { echo "⚠️ $RESUME_BRANCH not found in workspace repo."; exit 1; }
```

If missing from either:
- `[D]` Discard this stack entry and clean up
- `[A]` Abort — leave state as-is for manual investigation

---

## Step 4 — Remove entry from stack (on workspace main)

```bash
# Still on main — update the stack before switching branches
python3 -c "
import sys, re
stack = open('$STACK_FILE').read()
# Remove the selected branch block (- branch: NAME through next - branch: or EOF)
pattern = r'- branch: $RESUME_BRANCH\n(?:  .*\n)*'
stack = re.sub(pattern, '', stack)
open('$STACK_FILE', 'w').write(stack)
"

git -C "$WORKSPACE" add design/.pause-stack
git -C "$WORKSPACE" commit -m "chore: resume $RESUME_BRANCH — pop from pause stack"
git -C "$WORKSPACE" push
```

**If push fails: abort** — do not switch branches. The stack on main must be
updated before switching, to prevent a second session from also resuming the
same branch.

---

## Step 5 — Switch both repos to branch

```bash
git -C "$PROJECT" checkout "$RESUME_BRANCH"
git -C "$WORKSPACE" checkout "$RESUME_BRANCH"
```

Verify both are on the same branch after switching.

---

## Step 6 — Rebase branch onto current main

```bash
git -C "$PROJECT" rebase main
```

**If rebase succeeds:** continue to Step 7.

**If rebase fails (conflict):**
- Report conflicting files verbatim.
- **Stop. Do not proceed.**
- Instruct: resolve conflicts, `git rebase --continue`, then run `work-resume` again — it will detect the stack entry is already removed and skip Steps 1–5.
- The branch is now checked out; work can continue after manual resolution.

Workspace branch does not need rebasing — it holds methodology artifacts only,
not implementation code. Switch workspace to the branch but do not rebase it.

```bash
git -C "$WORKSPACE" rebase main 2>/dev/null || true  # best-effort only
```

---

## Step 7 — Reset WIP commit

```bash
if [ "$RESUME_WIP_PROJECT" = "true" ]; then
  git -C "$PROJECT" reset HEAD~1
  echo "✅ Project WIP commit reset — changes restored to working tree"
fi

if [ "$RESUME_WIP_WORKSPACE" = "true" ]; then
  git -C "$WORKSPACE" reset HEAD~1
  echo "✅ Workspace WIP commit reset — changes restored to working tree"
fi
```

The reset restores the working tree to exactly where it was when work was paused.

---

## Step 8 — Confirm

```
▶  Resumed: <branch-name>  Issue: #<N>
   Paused <duration> ago
   Rebased onto main  (+N commits incorporated)
   WIP restored: project=<yes|no>  workspace=<yes|no>
   Stack remaining: <N> paused branch(es)
```

---

## Step 9 — Run pre-checks

Run Steps 0, 2, 3, 11 from work-start:
- **Step 0**: Path resolution (already done)
- **Step 2**: Platform coherence — re-read platform doc, run five coherence questions
- **Step 3**: Relevant protocols — scan and read applicable rules
- **Step 11**: IntelliJ MCPs — call both; hard stop if unavailable

Skip all branch creation steps — the branch already exists.
