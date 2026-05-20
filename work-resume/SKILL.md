---
name: work-resume
description: >
  Use when returning to a paused branch — user says "work-resume", "resume",
  or "go back to that branch". Requires a .paused marker on workspace main
  (created by work-pause). Must be invoked from main.
---

# work-resume

Resumes a paused branch: switches both repos back, removes the pause marker,
restores stashed changes, runs pre-checks.

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

## Step 1 — Check .paused

```bash
cat "$WORKSPACE/design/.paused" 2>/dev/null \
  || { echo "Nothing to resume — no .paused found."; exit 1; }

RESUME_BRANCH=$(grep "^branch:" "$WORKSPACE/design/.paused" | sed 's/branch: //')
PAUSED_AT=$(grep "^paused-at:" "$WORKSPACE/design/.paused" | sed 's/paused-at: //')
```

---

## Step 2 — Stale check

Verify the branch still exists in both repos:

```bash
# Use rev-parse --verify for exact match — grep would match partial branch names
git -C "$WORKSPACE" rev-parse --verify "$RESUME_BRANCH" &>/dev/null \
  || echo "⚠️ $RESUME_BRANCH not found in workspace"
git -C "$PROJECT" rev-parse --verify "$RESUME_BRANCH" &>/dev/null \
  || echo "⚠️ $RESUME_BRANCH not found in project"
```

If missing from either repo:
- `[D]` Discard `.paused` and clean up — remove the marker file and commit
- `[A]` Abort — leave state as-is for manual investigation

---

## Step 3 — Switch both repos to epic branch

Use Branch Switch Helper with `$RESUME_BRANCH`. Prompt before remote pull.

```bash
git -C "$PROJECT" checkout "$RESUME_BRANCH"
git -C "$WORKSPACE" checkout "$RESUME_BRANCH"

PROJECT_BEHIND=$(git -C "$PROJECT" rev-list HEAD..origin/"$RESUME_BRANCH" --count 2>/dev/null || echo 0)
WORKSPACE_BEHIND=$(git -C "$WORKSPACE" rev-list HEAD..origin/"$RESUME_BRANCH" --count 2>/dev/null || echo 0)
if [ "$PROJECT_BEHIND" -gt 0 ] || [ "$WORKSPACE_BEHIND" -gt 0 ]; then
  echo "Remote has new commits (+${PROJECT_BEHIND} project, +${WORKSPACE_BEHIND} workspace)."
  echo "Incorporate now with pull --rebase? (y/n)"
fi
```

---

## Step 4 — Remove .paused from workspace main

```bash
# Capture stash ref if workspace has uncommitted changes on the epic branch
STEP4_STASH=none
if git -C "$WORKSPACE" status --short | grep -q .; then
  stash_out=$(git -C "$WORKSPACE" stash)
  echo "$stash_out" | grep -q "Saved working" && STEP4_STASH="stash@{0}"
fi

git -C "$WORKSPACE" checkout main
git -C "$WORKSPACE" pull --rebase origin main
rm "$WORKSPACE/design/.paused"
git -C "$WORKSPACE" add -A
git -C "$WORKSPACE" commit -m "chore: resume $RESUME_BRANCH, remove pause marker"
git -C "$WORKSPACE" push

git -C "$WORKSPACE" checkout "$RESUME_BRANCH"
# Use the recorded ref, not bare stash pop (consistent with Step 5 principle)
if [ "$STEP4_STASH" != "none" ]; then
  git -C "$WORKSPACE" stash pop "$STEP4_STASH" 2>/dev/null \
    || echo "⚠️ Workspace stash pop failed ($STEP4_STASH) — resolve manually"
fi
```

---

## Step 5 — Restore stashed changes

Read stash references from `.meta` and pop each using its recorded position:

```bash
STASH_PROJECT=$(grep "^stash-project:" "$WORKSPACE/design/.meta" | sed 's/stash-project: //')
STASH_WORKSPACE=$(grep "^stash-workspace:" "$WORKSPACE/design/.meta" | sed 's/stash-workspace: //')

# Use the recorded stash reference — do NOT use bare stash pop (pops wrong
# stash if the stack shifted since pause time)
if [ "$STASH_PROJECT" != "none" ]; then
  if ! git -C "$PROJECT" stash pop "$STASH_PROJECT" 2>/dev/null; then
    echo "⚠️ Project stash pop failed ($STASH_PROJECT) — resolve manually"
  fi
fi

if [ "$STASH_WORKSPACE" != "none" ]; then
  if ! git -C "$WORKSPACE" stash pop "$STASH_WORKSPACE" 2>/dev/null; then
    echo "⚠️ Workspace stash pop failed ($STASH_WORKSPACE) — resolve manually"
  fi
fi
```

If stash pop fails: warn and continue. Do not abort — the branch is already restored
and the user can resolve stash conflicts manually.

---

## Step 6 — Clear pause flags from .meta

```bash
sed -i '' \
  '/^paused:/d; /^paused-at:/d; /^paused-issue:/d; /^stash-project:/d; /^stash-workspace:/d' \
  "$WORKSPACE/design/.meta"
git -C "$WORKSPACE" add design/.meta
git -C "$WORKSPACE" commit -m "chore($RESUME_BRANCH): clear pause flags from .meta"
git -C "$WORKSPACE" push
```

---

## Step 7 — Surface context

```bash
# Extract issue number from .meta (read once here, not re-derived later)
ISSUE_N=$(grep "^issue:" "$WORKSPACE/design/.meta" | sed 's/issue: //')
# $PAUSED_AT read from .paused in Step 1
```

```
▶  Resumed: <branch-name>  Issue: #<N>  Paused <duration> ago
   Stash restored: <yes | no | conflict — resolve manually>
```

---

## Step 8 — Run pre-checks

Run Steps 0, 2, 3, 11 from work-start:
- **Step 0**: Path resolution (already done)
- **Step 2**: Platform coherence — re-read platform doc, run five coherence questions
- **Step 3**: Relevant protocols — scan and read applicable rules
- **Step 11**: IntelliJ MCPs — call both; hard stop if unavailable

Skip all branch creation steps — the branch already exists.
