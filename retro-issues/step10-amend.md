# Step 10 (Optional) — Amend Historical Commit Messages

Offered after Step 9. Rewrites git history to add `Refs #N` / `Closes #N`
footers to commits. Requires team coordination.

Ask:
> Would you also like to amend historical commit messages to reference their issues?
>
> ⚠️ This rewrites git history and requires a force push.
>    Safe only when all contributors can be coordinated to re-pull.
>
> YES — proceed | NO — skip

If NO: done. If YES, continue below.

---

**Check git-filter-repo:**
```bash
git filter-repo --version 2>/dev/null || echo "NOT INSTALLED"
```

If missing: `brew install git-filter-repo` or `pip3 install git-filter-repo`.

**Identify current branch:**
```bash
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Working from: $CURRENT_BRANCH"
```

**Create an amendment branch — do not touch the current branch:**
```bash
git checkout -b retro-amended
```

All rewriting happens on `retro-amended`. If anything goes wrong,
`git branch -D retro-amended` discards all changes cleanly — the original
branch is untouched.

**Generate mapping JSON:**
```bash
python3 ~/.claude/skills/retro-issues/scripts/retro-parse-mapping.py \
  docs/retro-issues.md > /tmp/retro-mapping.json
```

**Preview what will be amended:**

Show a table of commit → ref before running anything:
```
Commits to be amended:

  abc1234  2024-01-15  "Add java-dev skill"    → + Refs #12
  def5678  2024-01-18  "Add java-dev tests"    → + Closes #12

{N} commits will be amended. {M} excluded commits untouched.

Proceed? (YES / NO)
```

Wait for YES before running filter-repo.

**Run amendment on `retro-amended` only:**
```bash
python3 ~/.claude/skills/retro-issues/scripts/retro-amend-commits.py \
  /tmp/retro-mapping.json
```

**Verify — critical safety check:**
```bash
# Check messages have refs
git log retro-amended --oneline | head -10

# File content must be identical to original branch
git diff $CURRENT_BRANCH retro-amended
```

If `git diff` produces any output: abort immediately:
```bash
git checkout $CURRENT_BRANCH
git branch -D retro-amended
```

Tell the user what went wrong and stop. If `git diff` is empty, continue.

**Swap the branch labels:**
```bash
git branch -m $CURRENT_BRANCH ${CURRENT_BRANCH}-pre-retro
git branch -m retro-amended $CURRENT_BRANCH
```

Now:
- `$CURRENT_BRANCH` → rewritten history with issue refs (active)
- `${CURRENT_BRANCH}-pre-retro` → original history, untouched (backup)

**Force push with lease:**
```bash
git push --force-with-lease origin $CURRENT_BRANCH
```

**Coordinate team re-sync:**
> ⚠️ History rewritten and pushed.
>
> All contributors must re-sync:
>
>   git fetch origin
>   git checkout {branch}
>   git reset --hard origin/{branch}
>
> Do NOT use `git pull` — it creates a merge commit against the old history.

**Offer cleanup of backup:**
> The original history is preserved as `${CURRENT_BRANCH}-pre-retro`.
> Delete it now? **(YES / keep it for now)**

```bash
# If YES:
git branch -D ${CURRENT_BRANCH}-pre-retro
rm /tmp/retro-mapping.json
```
