---
name: work-end
description: >
  Use when the current branch is complete and ready to close — user says
  "work-end", "close this branch", or "wrap up this issue". Must be invoked
  from the working branch, not main. Replaces "epic close".
---

# work-end

Closes the current branch cleanly. Promotes artifacts, merges the journal,
closes the issue, rebases the project branch onto the project base branch, marks the
branch closed, returns to the workspace base (main).

---

## Path Resolution (run first, always)

```bash
PROJECT=$(grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //')
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md | head -1 | sed 's/.*`\(.*\)`.*/\1/')
PROJECT_BASE_BRANCH=$(grep "^\*\*Project base branch:\*\*" CLAUDE.md 2>/dev/null | head -1 | sed 's/.*`\(.*\)`.*/\1/')
[ -z "$PROJECT_BASE_BRANCH" ] && PROJECT_BASE_BRANCH="main"
```

`PROJECT_BASE_BRANCH` is the project's base branch — read from `**Project base branch:** \`<name>\``
in CLAUDE.md; defaults to `main`. The workspace always uses `main` as its base branch.

---

## Pre-conditions

Resolve paths and read current branch, then check in order:

```bash
PROJECT=$(grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //')
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md | head -1 | sed 's/.*`\(.*\)`.*/\1/')
CURRENT_WORKSPACE=$(git -C "$WORKSPACE" branch --show-current)
```

1. **If `$WORKSPACE/design/.pause-stack` exists and has entries** — check whether
   the target branch is in the stack:
   - **Current branch is in the stack** (ending a paused branch without resuming it):
     allowed. After all close steps complete, remove this branch from the stack
     (Step 9 will handle it — see "Stack cleanup on end" below).
   - **Current branch is NOT in the stack but stack is non-empty**: inform the user
     the stack has N other paused branches. Continue — this is normal when ending
     the active branch while others are paused.

2. **`$WORKSPACE/design/.meta` must exist on the current branch** → proceed.

3. **If `$WORKSPACE/design/.meta` exists but `$CURRENT_WORKSPACE == main`** (orphaned)
   → hard stop. Offer to switch to the surviving branch and close from there, or discard.

---

## Step 0 — Resolve paths

```bash
PROJECT=$(grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //')
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md | head -1 | sed 's/.*`\(.*\)`.*/\1/')
OWNER_REPO=$(grep "GitHub repo:" CLAUDE.md | head -1 | sed 's/.*GitHub repo: *//')
PROJECT_BASE_BRANCH=$(grep "^\*\*Project base branch:\*\*" CLAUDE.md 2>/dev/null | head -1 | sed 's/.*`\(.*\)`.*/\1/')
[ -z "$PROJECT_BASE_BRANCH" ] && PROJECT_BASE_BRANCH="main"
```

---

## Step 1 — Read context and extract variables

```bash
cat "$WORKSPACE/design/.meta"

BRANCH_NAME=$(grep "^branch:" "$WORKSPACE/design/.meta" | sed 's/branch: //')
PROJECT_SHA=$(grep "^project-sha:" "$WORKSPACE/design/.meta" | sed 's/project-sha: //')
ISSUE_N=$(grep "^issue:" "$WORKSPACE/design/.meta" | sed 's/issue: //')
ISSUE_REPO_GITHUB=$(grep "^issue-repo:" "$WORKSPACE/design/.meta" | sed 's/issue-repo: //')
```

`$BRANCH_NAME`, `$PROJECT_SHA`, and `$ISSUE_N` are used throughout Steps 3–10.
Extract once here — never re-read from `.meta` in later steps.

---

## Step 2 — Flyway V re-scan

Re-scan at close time — another branch may have claimed the same V numbers since
branch creation.

```bash
git -C "$PROJECT" fetch --all 2>/dev/null || echo "⚠️ No network — scan skipped"
```

If conflict detected: offer `[R]` renumber affected migration files, `[A]` abort.
Block close until resolved.

---

## Step 3 — Resolve routing and set DESIGN_REPO

Read three-layer routing cascade for each artifact type. Warn on deprecated
vocabulary (`base`, `project repo`, `design-journal`). Show resolved table;
user confirms before proceeding.

**Capability detection** — for each resolved destination:
```bash
detect_capability() {
  local dest="$1"
  if [ -d "$dest/.git" ]; then
    git -C "$dest" remote get-url origin &>/dev/null 2>&1 \
      && echo "remote-git" || echo "local-git"
  else
    echo "filesystem"
  fi
}
```

**Specs routing is non-configurable** — specs always route to `project`
(`$PROJECT/docs/specs/`). If the cascade resolves `specs → workspace`, override
with a warning: "Specs routing overridden to project — not user-configurable."

**`$DESIGN_REPO` — read from `.meta`, do NOT re-derive from routing config:**
```bash
DESIGN_REPO_KEY=$(grep "^design-repo:" "$WORKSPACE/design/.meta" | sed 's/design-repo: //')
case "$DESIGN_REPO_KEY" in
  workspace)
    DESIGN_REPO="$WORKSPACE" ;;
  project)
    DESIGN_REPO="$PROJECT" ;;
  cross-repo:*)
    CROSS_REPO_NAME="${DESIGN_REPO_KEY#cross-repo:}"
    CANDIDATE="$(dirname "$PROJECT")/$CROSS_REPO_NAME"
    if [ -d "$CANDIDATE/.git" ]; then
      DESIGN_REPO="$CANDIDATE"
    else
      echo "⚠️ Cross-repo path not found at $CANDIDATE — cannot merge journal."
      echo "Options: [S]kip journal merge  [A]bort close"
      # Wait for user response before continuing
    fi ;;
  *)
    echo "⚠️ Unknown design-repo key '$DESIGN_REPO_KEY' — defaulting to project."
    DESIGN_REPO="$PROJECT" ;;
esac
```

`$DESIGN_REPO` must remain available through Step 8d. Do not recalculate it in
subsequent steps.

---

## Step 3b — Pre-close sweep

Before inventorying artifacts, verify the branch leaves nothing behind. Present
this checklist:

```
Pre-close sweep — create before presenting the close plan?

[x] 1  write-blog     capture any work on this branch worth a diary entry
[x] 2  adr            record any significant architectural decisions without a formal ADR
[x] 3  protocol sweep formalise any project rules established or re-enforced this branch
[x] 4  forage sweep   check for gotchas, techniques, or undocumented behaviours

Type numbers to toggle, "all" to toggle all, or "go" to proceed:
```

Defaults: all four on. The user may deselect any that clearly don't apply (e.g. "go"
immediately if the branch was a one-line typo fix). Do not auto-skip — the point is
to make the decision explicit.

Run checked items in this order:
1. **Forage sweep** — while context is full; findings may feed the blog entry
2. **Protocol sweep** — while context is full (invoke `protocol` skill with `SWEEP` operation)
3. **adr** — invoke `adr` skill for each candidate identified
4. **write-blog** — last, so it can synthesise the full branch narrative including any forage/protocol submissions

**Why this step exists:** Step 4 inventories artifacts that *were written*. Without this
sweep, the close plan accurately reports "blog: no new entries" when it should say "blog:
no new entries (and none were considered)." The sweep converts the inventory from a
snapshot into a verified statement. Only after this step is complete does the close plan
accurately reflect what the branch leaves behind.

After all checked items complete, proceed to Step 4.

---

## Step 4 — Inventory artifacts

```bash
ls "$WORKSPACE/adr/" 2>/dev/null | grep -v INDEX.md
ls "$WORKSPACE/blog/" 2>/dev/null | grep -v INDEX.md
ls "$WORKSPACE/snapshots/" 2>/dev/null | grep -v INDEX.md
ls "$WORKSPACE/specs/$BRANCH_NAME/" 2>/dev/null
ls "$WORKSPACE/plans/" 2>/dev/null | grep -v "^attic$"
cat "$WORKSPACE/design/JOURNAL.md"
```

Compute and store the blog count. This variable drives the close plan and the
publish step — treat it as a first-class output of Step 4, not a footnote:

```bash
BLOG_COUNT=$(ls "$WORKSPACE/blog/" 2>/dev/null | grep -v INDEX.md | grep "\.md$" | wc -l | tr -d ' ')
echo "BLOG_COUNT=$BLOG_COUNT"   # surface it explicitly — do not silently swallow
```

---

## Step 5 — Journal validation

**5a — DESIGN.md existence**
If `$DESIGN_REPO/DESIGN.md` is missing:
- `[C]` Create from journal entries — journal becomes the initial DESIGN.md content
- `[S]` Skip merge entirely

**5b — Section heading drift**
Re-hash H2 headings in `$DESIGN_REPO/DESIGN.md`. Compare against `design-section-hashes`
in `.meta`. For each `§Section` anchor in JOURNAL.md, verify its heading still exists
unchanged in DESIGN.md.
```bash
STORED=$(grep "^design-section-hashes:" "$WORKSPACE/design/.meta" | sed 's/design-section-hashes: //')
CURRENT=$(grep "^## " "$DESIGN_REPO/DESIGN.md" 2>/dev/null \
  | while read h; do printf "%s:%s|" "$(printf '%s' "$h" | shasum -a 256 | cut -c1-8)" "$h"; done)
```
If drift: `[U]` update journal anchors, `[S]` skip drifted sections, `[A]` abort.

**5c — Anchor validation**
Count `^### .*·.*§` lines vs total `^### ` lines in JOURNAL.md.
If any entries lack anchors: `[F]` fix via java-update-design, `[S]` skip merge,
`[C]` continue accepting loss.

**5d — Empty journal**
If no entries at all:
- `[W]` Write retrospective via java-update-design
- `[S]` Skip and accept permanent loss

---

## Step 6 — Select specs for GitHub posting

If tracking enabled: list `$WORKSPACE/specs/$BRANCH_NAME/`, ask which to post as
collapsible comments on the GitHub issue. Skip silently if tracking disabled.

---

## Step 7 — Present close plan

Before presenting, if `$BLOG_COUNT > 0`, output this acknowledgement on its own
line so it cannot be missed:

> ⚠️ **BLOG_COUNT=$BLOG_COUNT** — publish-blog will run as part of workspace-main
> operations (8a). It is not optional and will not be skipped.

Then present the plan:

```
work-end close plan — <branch-name>

  Flyway V check     ✅ no conflicts
  Artifact routing
  ├── adr/<N>        → project      [remote-git]
  ├── blog/<N>       → workspace    [remote-git]
  ├── specs/<N>      → project      [remote-git]
  └── snapshots/<N>  → workspace    [remote-git]
  Plan archiving     → plans/attic/<branch-name>/  [workspace main]
  Journal merge      → DESIGN.md  (<N> sections)
  Spec posting       → #<N>  (<filenames>)
  Issue              → close #<N>
  Publish blog       → publish-blog ($BLOG_COUNT entries)   ← "skipped (no entries)" if BLOG_COUNT=0
                       runs during workspace-main operations (8a), before returning
                       to epic branch

Approve all, or step by step? (all / step)
```

**The Publish blog line is always shown** — never omitted. When BLOG_COUNT=0,
write "skipped (no entries)". When BLOG_COUNT>0, write the count and confirm it
runs during 8a. A plan that lists blog entries in artifact routing but shows
"skipped" for Publish blog is an error — stop and fix it.

---

## Step 8 — Execute

Failures are reported but do not stop remaining steps, **except**: journal merge
failure prompts the user before continuing to issue close.

### 8a — Batch workspace-main operations (single main-visit)

```bash
# Capture stash ref if workspace has uncommitted changes
WS_STASH_8A=none
if git -C "$WORKSPACE" status --short | grep -q .; then
  stash_out=$(git -C "$WORKSPACE" stash)
  echo "$stash_out" | grep -q "Saved working" && WS_STASH_8A="stash@{0}"
fi

git -C "$WORKSPACE" checkout main
git -C "$WORKSPACE" pull --rebase origin main

# Promote workspace-routed artifacts (blog, snapshots, etc.)
# For each artifact file in the Step 4 inventory where routing destination = workspace:
for each workspace-routed artifact:
  mkdir -p "$WORKSPACE/<dest>/"
  git -C "$WORKSPACE" checkout "$BRANCH_NAME" -- <artifact-files>
  git -C "$WORKSPACE" add "<dest>/"
  git -C "$WORKSPACE" commit -m "feat: promote <type> from $BRANCH_NAME"

# Archive plans to attic
if plans exist:
  git -C "$WORKSPACE" checkout "$BRANCH_NAME" -- plans/<files>
  mkdir -p "$WORKSPACE/plans/attic/$BRANCH_NAME"
  mv "$WORKSPACE/plans/<files>" "$WORKSPACE/plans/attic/$BRANCH_NAME/"
  git -C "$WORKSPACE" add -A
  git -C "$WORKSPACE" commit -m "archive($BRANCH_NAME): move plans to attic"

# WORKSPACE DESIGN REPO CASE: journal merge must happen here on main, not on the epic branch.
# Commits to the epic branch are discarded at close — the merge must land on workspace main.
if [ "$DESIGN_REPO_KEY" = "workspace" ]; then
  # Cherry-pick JOURNAL.md from the epic branch, then run the journal merge sub-procedure
  # (same steps as 8d below: baseline read, current read, apply journal, verify, commit)
  git -C "$WORKSPACE" checkout "$BRANCH_NAME" -- design/JOURNAL.md
  # [execute 8d merge steps here — baseline=$PROJECT_SHA, target=$WORKSPACE/DESIGN.md]
  git -C "$WORKSPACE" add DESIGN.md
  git -C "$WORKSPACE" commit -m "docs($BRANCH_NAME): apply design journal"
  # 8d is now complete for the workspace case — skip the 8d block when DESIGN_REPO_KEY=workspace
fi

git -C "$WORKSPACE" push  # single push for all workspace-main commits

# ─── PUBLISH BLOG (runs here, while workspace is on main) ─────────────────────
# Blog entries are now on workspace main. Publish immediately — do not defer
# to a later step. If BLOG_COUNT=0 this block is a no-op.
if [ "$BLOG_COUNT" -gt 0 ]; then
  echo "Publishing $BLOG_COUNT blog entries from workspace main..."
  # invoke publish-blog skill
  # After publish-blog returns, VERIFY the destination actually received the entries.
  # Read ~/.claude/blog-routing.yaml to find the notes destination path and subdir,
  # then count .md files there and compare with BLOG_COUNT.
  #
  # After publish-blog returns, VERIFY every workspace blog entry exists at the
  # destination. Count-comparison is wrong (destination has entries from all projects).
  # Instead check each filename individually. Run as inline Python:
  #
  #   python3 - "$WORKSPACE" <<'VERIFY'
  #   import yaml, pathlib, sys
  #   workspace = pathlib.Path(sys.argv[1])
  #   cfg = yaml.safe_load(open(pathlib.Path("~/.claude/blog-routing.yaml").expanduser()))
  #   # check all configured destinations (notes + articles)
  #   dest_dirs = []
  #   for dest in cfg["destinations"].values():
  #       p = pathlib.Path(dest["path"]).expanduser() / dest.get("subdir", "")
  #       dest_dirs.append(p)
  #   blog_dir = workspace / "blog"
  #   source_files = {f.name for f in blog_dir.glob("*.md") if f.name != "INDEX.md"}
  #   missing = []
  #   for name in source_files:
  #       if not any((d / name).exists() for d in dest_dirs):
  #           missing.append(name)
  #   if missing:
  #       print(f"PUBLISH FAILED: {len(missing)} entries not at any destination:")
  #       for m in missing:
  #           print(f"  {m}")
  #       sys.exit(1)
  #   print(f"PUBLISH VERIFIED: all {len(source_files)} entries confirmed at destination")
  #   VERIFY
  #
  # If verification exits non-zero: HARD STOP. Do NOT proceed to 8b.
  # Tell the user publish-blog failed and which entries are missing.
  # The branch is not closed until every entry is confirmed at destination.
fi
# ─────────────────────────────────────────────────────────────────────────────

git -C "$WORKSPACE" checkout "$BRANCH_NAME"
# Use the captured ref, not bare stash pop
if [ "$WS_STASH_8A" != "none" ]; then
  git -C "$WORKSPACE" stash pop "$WS_STASH_8A" 2>/dev/null \
    || echo "⚠️ Workspace stash pop failed ($WS_STASH_8A) — resolve manually"
fi
```

### 8b — Project-routed artifact promotion (ADRs, specs)

```bash
for each project-routed artifact:
  mkdir -p "$PROJECT/<dest>/"
  cp "$WORKSPACE/<artifact-file>" "$PROJECT/<dest>/"
  git -C "$PROJECT" add "<dest>/"
  git -C "$PROJECT" commit -m "feat: promote <type> from $BRANCH_NAME"
  git -C "$PROJECT" push  # non-fatal if fails; report exit code
```

### 8c — Spec cleanup (only if 8b push exit code was 0)

If 8b push failed, skip entirely — workspace copy is the only remaining copy.

```bash
rm -rf "$WORKSPACE/specs/$BRANCH_NAME/"
git -C "$WORKSPACE" add -A
git -C "$WORKSPACE" commit -m "chore($BRANCH_NAME): remove promoted specs from staging"
git -C "$WORKSPACE" push
```

### 8d — Journal merge

Uses `$DESIGN_REPO` (set in Step 3) and `$PROJECT_SHA` (set in Step 1).

**⚠️ Branch context matters:** When `$DESIGN_REPO_KEY = workspace`, the merge MUST
happen during the 8a main-visit (see 8a above) — not here. For `$DESIGN_REPO_KEY = project`,
run the full merge below on the project epic branch (committed before the rebase in Step 8j).

Steps:
1. Read baseline: `git -C "$DESIGN_REPO" show "$PROJECT_SHA":DESIGN.md`
2. Read current `$DESIGN_REPO/DESIGN.md`
3. Apply journal narrative per `§Section`, preserving independent main-branch changes
4. Write merged result
5. Post-merge verification: re-read each `§Section`; present to user (`[A]` accept,
   `[R]` redo, `[X]` abort) before committing
6. Commit and push:
   ```bash
   git -C "$DESIGN_REPO" add DESIGN.md
   git -C "$DESIGN_REPO" commit -m "docs($BRANCH_NAME): apply design journal"
   git -C "$DESIGN_REPO" push
   ```

If journal merge fails: prompt user before continuing to issue close.

### 8e — Spec posting

Post selected specs (from Step 6) as collapsible comments on the GitHub issue.

### 8f — Issue close

Only if tracking enabled and `$ISSUE_N` is non-empty:
```bash
CLOSE_REPO="${ISSUE_REPO_GITHUB:-$OWNER_REPO}"
[ -n "$ISSUE_N" ] && gh issue close "$ISSUE_N" --repo "$CLOSE_REPO"
```

### 8g — Publish blog (runs inside 8a — not a separate step)

Blog publishing now runs **inside 8a**, immediately after `git push` and before
returning to the epic branch. See the `# PUBLISH BLOG` block in 8a above.

This section exists only to document the decision: publish-blog was moved into 8a
because positioning it as a separate step created a reliable skip vector — Claude
would complete 8a (which lists blog in artifact routing), then proceed to 8f/8j
without circling back to 8g. Moving it inside 8a eliminates the gap.

**Verification:** the 8h final report must include a "Blog published" line when
BLOG_COUNT > 0. If the report is missing this line, publish-blog was not run —
stop, go back to workspace main, and run it before proceeding to 8i/8j.

### 8h — Final report

```
✅ ADRs → project
✅ Specs → project
✅ Blog → workspace
✅ Plans → attic
✅ Journal merged → DESIGN.md (N sections)
✅ Specs posted to #N, issue closed
✅ Blog published → <destination path> (N entries)   ← "skipped (no entries)" if BLOG_COUNT=0
❌ Push failed — <path>. Run: git -C <path> push
```

**The `Blog published` line is always present.** When BLOG_COUNT=0, write
"skipped (no entries)". When BLOG_COUNT>0, write the count and destination path.

**If you are generating this report and the Blog published line shows anything
other than a confirmed count with destination path when BLOG_COUNT > 0:**
— stop. Do not proceed to 8i or 8j. Go back to workspace main and run
`publish-blog` now. The report must reflect reality, not intention.

### 8i — Offer hygiene scan

"Run branch hygiene scan? Checks Flyway conflicts, unmerged code, stale branches. (y/n)"

### 8j — Rebase project branch onto project base branch, push, offer upstream PR

**This step is mandatory.** Implementation commits on the project branch must land on `$PROJECT_BASE_BRANCH` before the branch is marked closed.

**Detect remote topology first:**

```bash
FORK_REMOTE=$(git -C "$PROJECT" remote get-url origin 2>/dev/null && echo "origin" || echo "")
BLESSED_REMOTE=$(git -C "$PROJECT" remote get-url upstream 2>/dev/null && echo "upstream" || echo "")
# If no upstream remote exists, origin is the blessed repo — no fork in play
```

| Topology | Meaning |
|----------|---------|
| `upstream` remote exists | Fork model — `origin` is the fork, `upstream` is the blessed repo |
| No `upstream` remote | Single-remote model — `origin` is the blessed repo |

**Rebase:**

```bash
git -C "$PROJECT" fetch "$FORK_REMOTE" "$PROJECT_BASE_BRANCH" 2>/dev/null || echo "⚠️  No network — using local $PROJECT_BASE_BRANCH"
git -C "$PROJECT" checkout "$PROJECT_BASE_BRANCH"
git -C "$PROJECT" rebase "$BRANCH_NAME"
```

**If rebase fails (conflict):**
- Report the conflicting files verbatim.
- **Stop. Do not proceed to Step 9.**
- Instruct the user: resolve conflicts on `$PROJECT_BASE_BRANCH`, then re-run `work end` to complete the close.

**Push to fork remote:**

> "Push `$PROJECT_BASE_BRANCH` to `$FORK_REMOTE`? (y/n)"

```bash
git -C "$PROJECT" push "$FORK_REMOTE" "$PROJECT_BASE_BRANCH"
```

**Offer upstream PR (fork model only):**

If `$BLESSED_REMOTE` is non-empty:
> "Open a PR from `$FORK_REMOTE/$PROJECT_BASE_BRANCH` → `$BLESSED_REMOTE/$PROJECT_BASE_BRANCH`? (y/n)"

If yes:
```bash
gh pr create --base "$PROJECT_BASE_BRANCH" --head "$(git -C "$PROJECT" remote get-url "$FORK_REMOTE" \
  | sed 's|.*github.com[:/]\(.*\)\.git|\1|'):$PROJECT_BASE_BRANCH" \
  --title "<issue title>" --body "Closes #$ISSUE_N"
```

If no `$BLESSED_REMOTE`: no PR step — the push to `origin/$PROJECT_BASE_BRANCH` is the final delivery.

**Why rebase and not merge --no-ff?** Rebase keeps the project base branch history linear and avoids a merge commit that references a branch consumers never saw. Fast-forward is a safe subset — `git rebase` fast-forwards when possible, replays commits otherwise.

### Step path (alternative to all-at-once)

If user chose "step" in Step 7:

- Phase 1: Artifact routing (8a including publish-blog if BLOG_COUNT > 0), 8b, 8c — confirm, execute, report → "Continue to journal merge? (y/n)"
- Phase 2: Journal merge (8d) — show each `§Section` before/after, confirm → "Continue to GitHub posting? (y/n)"
- Phase 3: Spec posting (8e), issue close (8f) → "Continue to branch merge? (y/n)"
- Phase 4: Merge project branch to `$PROJECT_BASE_BRANCH` (8j), EPIC-CLOSED.md, return workspace to main.

Note: publish-blog is part of Phase 1 (runs inside 8a), not Phase 3. It is not
an "offer" — it is mandatory when BLOG_COUNT > 0.

---

## Step 9 — Mark closed

`EPIC-CLOSED.md` lives in `$WORKSPACE/design/` alongside `.meta` and `JOURNAL.md`.
This is committed to the workspace **epic branch** (not main), so the hygiene scan
must traverse epic branches to find it — which it already does to check for `.meta`.

```bash
CLOSE_DATE=$(date +%Y-%m-%d)
DELETE_DATE=$(date -v +14d +%Y-%m-%d 2>/dev/null || date -d "+14 days" +%Y-%m-%d)

cat > "$WORKSPACE/design/EPIC-CLOSED.md" << EOF
# Branch Closed — $BRANCH_NAME
**Date:** $CLOSE_DATE
**Issue:** #$ISSUE_N
**Scheduled for deletion:** $DELETE_DATE
EOF

git -C "$WORKSPACE" add design/EPIC-CLOSED.md
git -C "$WORKSPACE" commit -m "docs($BRANCH_NAME): mark closed, deletion due $DELETE_DATE"
git -C "$WORKSPACE" push
```

Branches are **not deleted**. `EPIC-CLOSED.md` is the signal for hygiene scan cleanup.

**Stack cleanup on end:** If this branch was in the pause stack (detected in Pre-conditions),
remove it now that the branch is closed:

```bash
STACK_FILE="$WORKSPACE/design/.pause-stack"
if grep -q "branch: $BRANCH_NAME" "$STACK_FILE" 2>/dev/null; then
  python3 -c "
import re
stack = open('$STACK_FILE').read()
pattern = r'- branch: $BRANCH_NAME\n(?:  .*\n)*'
stack = re.sub(pattern, '', stack)
open('$STACK_FILE', 'w').write(stack)
"
  git -C "$WORKSPACE" add design/.pause-stack
  git -C "$WORKSPACE" commit -m "chore: remove $BRANCH_NAME from pause stack (branch closed)"
  git -C "$WORKSPACE" push
fi
```

---

## Step 10 — Return to base branches

Project is already on `$PROJECT_BASE_BRANCH` from Step 8j. Switch workspace to main:

```bash
git -C "$WORKSPACE" checkout main
```

Check remote ahead; prompt before `pull --rebase`. Not automatic.
