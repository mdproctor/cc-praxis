---
name: retro-issues
description: >
  Use when mapping an existing git repository's history to GitHub epics and
  issues — user says "map our history to issues", "retrospectively create
  issues", "backfill GitHub from git log", or invokes /retro-issues.
  One-off, on-demand only. Never auto-triggered.
---

# Retro Issues

Maps a repository's git history to a structured set of GitHub epics and issues.
Run once per repository when issue tracking is being introduced retrospectively.

**This skill is invoked only explicitly.** It is never auto-triggered by
Work Tracking or any other automatic behaviour. Use `issue-workflow` for
ongoing lifecycle enforcement.

## Safety contract

All git operations are read-only until the user confirms with YES.
Git history is never modified by the main flow.
The optional commit-amendment step (Step 10) is separate, gated, and
requires explicit team coordination acknowledgement before proceeding.

---

## Step 1 — Check prerequisites

```bash
git remote get-url origin   # needs a GitHub remote
gh auth status              # needs gh CLI authenticated
```

Extract `owner/repo`. If either fails, stop and tell the user.

Check for a very large history and offer to scope it:
```bash
git rev-list --count HEAD
```

If > 500 commits:
> This repo has {N} commits. Analysing all of them may produce too many
> groupings to review comfortably.
>
> Scope options:
> - **Date range** — e.g. "from 2024-01-01"
> - **Last N commits** — e.g. "last 200 commits"
> - **All** — proceed with full history

Wait for user choice before continuing.

Check for existing closed issues to avoid duplication:
```bash
gh issue list --state closed --limit 10 --repo {owner/repo}
```

If closed issues exist, warn:
> This repo already has {N} closed issues. The retrospective will propose new
> issues alongside them — review carefully to avoid duplicates.

---

## Step 2 — Gather inputs

**Git history:**
```bash
git log --no-merges \
  --format="%H|%ad|%s" \
  --date=short
```

For each commit hash, get changed files:
```bash
git diff-tree --no-commit-id -r --name-only {hash}
```

**Tags (phase boundary signals):**
```bash
git tag -l --sort=version:refname
```

**Documents (read each that exists):**
```bash
ls docs/adr/ 2>/dev/null
ls docs/diary/ blog/ 2>/dev/null
cat DESIGN.md 2>/dev/null
```

For each ADR: extract its date and title.
For each blog/diary entry: extract date and any milestone language
("complete", "shipped", "done", "phase", "v1").

---

## Step 3 — Identify phase boundaries

Build a timeline from commit dates. Mark boundary candidates:

| Signal | How to detect |
|--------|--------------|
| ADR created | ADR file date within ±3 days of commits |
| Blog milestone | Blog entry date + milestone language near commit cluster |
| Git tag | Tag date |
| Commit gap | >7 days with no commits between clusters |

Group commits into time windows between boundaries. Each window is a candidate
epic. Name it from the dominant document context (ADR title, blog phase name)
or from the most-changed directory within it.

If no boundaries are found: skip the epic layer entirely — create issues and
standalones only.

---

## Step 4 — Classify commits

For each commit, classify before grouping:

**Trivial (no ticket — excluded table only):**
- Message matches: "typo", "whitespace", "indent", "trailing", "format", "formatting", "spelling"
- Is a merge commit
- Note: "formats" (plural noun) does NOT match — `format` and `formatting` are exact targets

**Dependency bump (standalone ticket):**
- Message contains: "bump" or "upgrade" (reliable signals)
- Note: "update X to" is NOT a bump — general "update description to..." commits are functional

**Functional (cluster into issues):**
- Everything else

---

## Step 5 — Cluster functional commits into issues

Within each time window, group functional commits using this priority order:

**Primary: conventional commit scope**

Extract the scope from the commit subject using the pattern `type(scope): description`.
Commits sharing the same scope form a cluster regardless of which files they touch.

```
feat(garden): add knowledge garden skill  → scope: garden
fix(garden): fix garden indexing           → scope: garden
docs(garden): add examples                 → scope: garden
feat(marketplace): add plugin install      → scope: marketplace
```

This is a much stronger signal than file paths for repos using conventional commits —
it reflects the author's own intent about what feature the commit belongs to.

**Fallback: top-level directory**

If no scope is present in a commit, group it by the top-level directory of its
changed files. This applies to older commits or repos that don't use conventional
commits.

**Merge small clusters:**
- A cluster with < 2 commits and a low-signal message ("fix", "wip", "update", "misc")
  → promote to standalone, don't create a dedicated issue

**Split large clusters:**
- A single scope with commits clearly spanning two unrelated feature areas
  → split into two issues if the work is independently releasable

**Naming issues from clusters:**
- Scope-based cluster: title reflects the scope feature area ("Add {scope} skill/feature")
- Directory-based cluster: title reflects the directory's purpose

---

## Step 6 — Validate epics

For each candidate epic:
- Children ≥ 2 → keep as epic
- Children = 1 → dissolve; child becomes standalone
- Children = 0 → discard (only trivials in window)

**Never create a single-child epic.**

---

## Step 7 — Write the proposal document

Write `docs/retro-issues.md` (create `docs/` if needed).

Use `#TBD` as the issue number placeholder — replaced with real numbers
after creation. Structure:

```
# Retrospective Issue Mapping
Generated: {date}
Repo: {owner/repo}
Scope: {earliest-date} → {latest-date} | {N} commits analysed

---

## Epics and Child Issues

### Epic: "{title}" [enhancement]
Period: {start-date} → {end-date}
References: {ADR-NNNN / blog entry date / none}

#### Issue #TBD: "{child title}" [enhancement]
Commits:
- `{short-hash}` {date} — {message}
- `{short-hash}` {date} — {message}
Primary area: `{directory/}`

#### Issue #TBD: "{child title}" [{label}]
Commits:
- `{short-hash}` {date} — {message}
Primary area: `{directory/}`

---

## Standalone Issues

### Issue #TBD: "{title}" [{label}]
Commits:
- `{short-hash}` {date} — {message}
Primary area: `{directory/}`

---

## Excluded Commits (no ticket created)

| Hash | Date | Message | Reason |
|------|------|---------|--------|
| `{hash}` | {date} | {message} | Formatting/whitespace only |
| `{hash}` | {date} | {message} | Typo fix |
| `{hash}` | {date} | {message} | Merge commit |
```

Tell the user:
> Proposal written to `docs/retro-issues.md`.
> Review and edit it directly — adjust groupings, rename, merge, split,
> or remove sections as needed.
> When satisfied, say **YES** to create all issues on GitHub.

Wait. Accept:
- **YES** → read current `docs/retro-issues.md` state and proceed to Step 8
- Any edit instruction → apply to the file, confirm, wait again

---

## Step 8 — Create issues on GitHub

Read `docs/retro-issues.md` as the authoritative source. Create in this order —
never create in parallel, order matters for issue numbers.

**8a. Create epics:**
```bash
gh issue create \
  --title "{epic title}" \
  --label "epic,{type-label}" \
  --repo {owner/repo} \
  --body "$(cat <<'EOF'
## Overview
{Inferred from doc references and commit summary. 2–4 sentences.}

## Motivation
{What drove this phase of work.}

## Scope
{Filled in after child issues are created.}

## Definition of Done
{Inferred from what was actually delivered — observable outcomes.}

---
*Retrospectively created. Covers {start-date} → {end-date}.*
EOF
)"
```

Record each epic number. Update `#TBD` placeholders in `docs/retro-issues.md`.

**8b. Create child issues:**
```bash
gh issue create \
  --title "{child title}" \
  --label "{type-label}" \
  --repo {owner/repo} \
  --body "$(cat <<'EOF'
## Context
Part of epic #{epic-number} — {epic title}.
Retrospectively created. Covers {start-date} → {end-date}.
Key commits: {3–5 short hashes and messages}.

## What
{Inferred from commit messages and changed files. Outcome-focused.}

## Acceptance Criteria
- [ ] {Observable outcome inferred from what was delivered}

## Notes
{ADR / blog entry / design doc reference if relevant. Primary file paths changed.}
EOF
)"
```

Close immediately:
```bash
gh issue close {number} --comment "Completed. Retrospectively created from git history."
```

**8c. Update each epic's Scope checklist** with real child issue numbers:
```bash
gh issue edit {epic-number} --body "..." --repo {owner/repo}
```

**8d. Create standalone issues:**
```bash
gh issue create \
  --title "{title}" \
  --label "{type-label}" \
  --repo {owner/repo} \
  --body "$(cat <<'EOF'
## Context
Retrospectively created. Standalone — not part of any epic.
Covers {date}. Key commits: {short hashes}.

## What
{Inferred from commit messages.}

## Notes
{Primary file paths changed.}
EOF
)"
gh issue close {number} --comment "Completed. Retrospectively created from git history."
```

---

## Step 9 — Summarise

```
✅ Retrospective mapping complete.

Created {N} epics, {N} child issues, {N} standalone issues.
All issues closed with retrospective note.

Epic summary:
  #{N} — {title} ({N} children)
  #{N} — {title} ({N} children)

Run `gh issue list --state closed --label epic` to review.
```

Then offer the optional commit-amendment step (Step 10).

---

## Step 10 (Optional) — Amend historical commit messages

Offered after Step 9. Rewrites git history to add `Refs #N` / `Closes #N`
footers to commits. Requires team coordination.

Ask:
> Would you also like to amend historical commit messages to reference their issues?
>
> ⚠️ This rewrites git history and requires a force push.
>    Safe only when all contributors can be coordinated to re-pull.
>
> YES — proceed | NO — skip

If NO: done. If YES:

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

---

## Edge Cases

| Situation | Handling |
|-----------|---------|
| No ADRs, blog, or design doc | Pure gap-based analysis; note lower confidence in groupings |
| All commits in one time window | Skip epics; create issues and standalones only |
| Existing closed GitHub issues | Warn about potential duplicates before creating |
| Very large history (>500 commits) | Ask for date range before Step 2 |
| Commits with no useful message ("wip", "fix") | Use file paths as primary grouping signal; note low-confidence title in proposal |
| Monorepo with many unrelated areas | Ask which top-level directories to include before analysing |

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Creating issues before user approves proposal | Permanent GitHub records from wrong groupings | Always write retro-issues.md first; never create until YES |
| Single-child epic | No value over a standalone issue | Enforce 2-child minimum; dissolve during Step 6 |
| Treating trivial commits as issues | Noise in issue tracker | Classify first; trivials go to Excluded table only |
| Amending commits directly on main | If filter-repo fails mid-run, main is in unknown state | Always work on `retro-amended`; swap labels only after `git diff` confirms files identical |
| Amending without team coordination | Others' local history diverges silently | Show force-push warning; require explicit YES; give `reset --hard` instructions |

---

## Success Criteria

Retrospective mapping is complete when:
- ✅ `docs/retro-issues.md` written and user confirmed with YES
- ✅ All epics created with 2+ children (none with fewer)
- ✅ All child issues created, closed, and linked in epic Scope checklists
- ✅ All standalones created and closed
- ✅ All trivial commits listed in Excluded table with reasons
- ✅ If commit amendment chosen: `retro-amended` branch verified with `git diff`, labels swapped, `${branch}-pre-retro` backup retained until team re-synced

**Not complete** until all GitHub issues confirmed closed in `gh issue list`.

---

## Skill Chaining

**Invoked by:** User directly via `/retro-issues`, or says "map history to issues",
"backfill GitHub from git log", "retrospectively create issues".

**Prerequisite:** Run `issue-workflow` Phase 0 (Setup) first to configure standard
labels including `epic`. If labels are missing, the `--label "epic,..."` calls
will fail.

**Invokes:** Nothing — terminal skill.

**Never invoked automatically by:** `issue-workflow`, `git-commit`, Work Tracking,
or any session-start behaviour. Explicitly on-demand only.
