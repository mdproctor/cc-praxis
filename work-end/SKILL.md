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

4. **Workspace must have a clean working tree** — run before any other work:
   ```bash
   git -C "$WORKSPACE" status --short
   ```
   If any output appears, hard stop:
   > "Workspace has uncommitted changes on `$BRANCH_NAME`. Commit or discard them
   > before running work-end — stash is not used in this workflow."
   Do not proceed until the working tree is clean. Never stash automatically.

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
    git -C "$dest" remote get-url origin &>/dev/null 2>&1 && echo "remote-git" || echo "local-git"
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

[x] 1  write-content     capture any work on this branch worth a diary entry
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
4. **write-content** — last, so it can synthesise the full branch narrative including any forage/protocol submissions

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

Check whether the blog directory has any entries at all. This only determines
whether to run `publish-blog` — the skill itself handles the "what's new" check
by comparing the workspace blog against the destination:

```bash
BLOG_HAS_ENTRIES=$(ls "$WORKSPACE/blog/" 2>/dev/null | grep -v INDEX.md | grep -q "\.md$" && echo yes || echo no)
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
CURRENT=$(grep "^## " "$DESIGN_REPO/DESIGN.md" 2>/dev/null | while read h; do printf "%s:%s|" "$(printf '%s' "$h" | shasum -a 256 | cut -c1-8)" "$h"; done)
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

Present the plan:

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
  Publish blog       → 8g (N unpublished entries → destination)
  Project rebase     <branch> → <base-branch>
  Squash             <blessed-remote>/main..HEAD (mandatory before any push)
  Fork push          → origin/main (mandatory, no skip — fork is always updated first)
  Blessed repo       → prompt: push / PR / skip  (upstream remote, if present)

Approve all, or step by step? (all / step)
```

**The Publish blog line is always shown.** `publish-blog` compares the workspace
blog against the destination and publishes only what's missing — it handles the
"what's new" check. Do not attempt to pre-count new entries here.

---

## Step 8 — Execute

Failures are reported but do not stop remaining steps, **except**: journal merge
failure prompts the user before continuing to issue close.

### 8a — Batch workspace-main operations (single main-visit)

```bash
# Pre-condition: clean working tree verified in Pre-conditions step 4.
# Never stash — if the tree is dirty, work-end should have stopped already.

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

git -C "$WORKSPACE" checkout "$BRANCH_NAME"
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

### 8g — Publish blog

**Run on workspace main** (switch if needed — workspace must be on main when this runs).

Resolve the blog destination from `~/.claude/blog-routing.yaml`. For each workspace blog
entry not yet present at the destination, copy and commit:

```bash
BLOG_DEST=$(python3 -c "
import yaml, os
cfg = yaml.safe_load(open(os.path.expanduser('~/.claude/blog-routing.yaml')))
dest = cfg['destinations'][cfg['defaults']['destinations'][0]]
print(os.path.expanduser(dest['path'] + dest.get('subdir', '')).rstrip('/'))
")

# Find unpublished entries (filename comparison — count comparison is wrong because
# destination accumulates entries from all projects)
comm -23 <(ls "$WORKSPACE/blog/" | grep "\.md$" | grep -v INDEX | sort) \
  <(ls "$BLOG_DEST/" | sort) | while read entry; do
      cp "$WORKSPACE/blog/$entry" "$BLOG_DEST/$entry"
      git -C "$(dirname "$BLOG_DEST")" add "${BLOG_DEST##*/}/$entry"
    done

# Commit and push only if new entries were added
if git -C "$(dirname "$BLOG_DEST")" diff --cached --quiet; then
  echo "Blog: 0 new entries (all already published)"
else
  git -C "$(dirname "$BLOG_DEST")" commit -m "chore: publish blog entries from $BRANCH_NAME"
  git -C "$(dirname "$BLOG_DEST")" push
fi
```

**Hard stop if blog directory has entries and publish fails.** Do not proceed to 8h until
every workspace blog entry exists at the destination. Verify with the same `comm` check.

### 8h — Final report

```
✅ ADRs → project
✅ Specs → project
✅ Blog → workspace
✅ Plans → attic
✅ Journal merged → DESIGN.md (N sections)
✅ Specs posted to #N, issue closed
✅ Blog published → <destination path> (N new entries)   ← "0 new (all current)" if nothing to publish
❌ Push failed — <path>. Run: git -C <path> push
```

**The `Blog published` line is always present** — 0 new entries is a valid outcome,
not a skip. If the line is absent entirely, 8g was not run — stop and run it before
proceeding to 8i/8j.

### 8i — Hygiene scan

Always run — not an offer. Checks:

**1. Blog published** — verify every workspace blog entry exists at the destination:

```bash
UNPUBLISHED=$(comm -23 <(ls "$WORKSPACE/blog/" | grep "\.md$" | grep -v INDEX | sort) \
  <(ls "$BLOG_DEST/" | sort))

if [ -n "$UNPUBLISHED" ]; then
  echo "⚠️ Unpublished blog entries:"
  echo "$UNPUBLISHED"
  echo "→ Return to 8g and publish before proceeding."
fi
```

If any unpublished entries are found, stop and return to 8g. Do not proceed to 8j.

**2. Flyway conflicts** — check for V-number collisions with other branches (if Flyway
was involved on this branch).

**3. Stale workspace branches** — list open branches (no `design/EPIC-CLOSED.md` in
`design/`) with no commits in the last 7 days. Report only; do not act.

### 8j — Rebase project branch onto project base branch, push to fork, prompt for blessed repo

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

**Squash before fork push (fork model only — mandatory):**

Squash runs BEFORE the fork push so both fork and blessed repo receive identical history.
Run git-squash on the range `$BLESSED_REMOTE/$PROJECT_BASE_BRANCH..HEAD`. This is not optional
and must not be bypassed with `--no-verify`. The pre-push hook firing is the signal to run
git-squash, not to skip it. Noise commits (chore, docs follow-ons, journal applies, CI fixups)
must be compacted before the range is shared anywhere.

```bash
# Show the commit range that will reach the blessed repo (and therefore the fork too)
git -C "$PROJECT" log --oneline "$BLESSED_REMOTE/$PROJECT_BASE_BRANCH"..HEAD
```

Invoke `/git-squash` with the range `$BLESSED_REMOTE/$PROJECT_BASE_BRANCH..HEAD`.
Wait for the squash plan, user approval, and execution before proceeding.

If the user explicitly says "skip squash" or "no squash needed": accept and note it,
then proceed. Never silently skip.

**Push to fork remote (mandatory — no skip option):**

The fork push is always required. There is no [N]skip. The blessed repo can never receive
commits that the fork has not already received.

```bash
git -C "$PROJECT" push "$FORK_REMOTE" "$PROJECT_BASE_BRANCH"
```

If the fork push fails: stop. Do not proceed to blessed repo delivery. The fork must be
updated first — casehubio never gets ahead of mdproctor.

**Blessed repo delivery (fork model only):**

If `$BLESSED_REMOTE` is non-empty, always prompt — three choices:

> "Deliver to `$BLESSED_REMOTE/$PROJECT_BASE_BRANCH`?
>   [P] Push directly   [R] Open PR   [N] Skip"

- **P — Push directly:**
  ```bash
  git -C "$PROJECT" push "$BLESSED_REMOTE" "$PROJECT_BASE_BRANCH"
  ```
- **R — Open PR:**
  ```bash
  gh pr create --base "$PROJECT_BASE_BRANCH" --head "$(git -C "$PROJECT" remote get-url "$FORK_REMOTE" \
      | sed 's|.*github.com[:/]\(.*\)\.git|\1|'):$PROJECT_BASE_BRANCH" --title "<issue title>" --body "Closes #$ISSUE_N"
  ```
- **N — Skip:** leave casehubio delivery for later; note it in the 8h report. Fork already has the commits.

If no `$BLESSED_REMOTE`: no prompt — fork push is the final delivery.

**Why rebase and not merge --no-ff?** Rebase keeps the project base branch history linear and avoids a merge commit that references a branch consumers never saw. Fast-forward is a safe subset — `git rebase` fast-forwards when possible, replays commits otherwise.

### 8k — Final build verification (Java / Maven projects only)

**Run after 8j. Skip for non-Java projects.**

Check project type:
```bash
grep -i "^type:\|^\*\*Type:\*\*" "$PROJECT/CLAUDE.md" 2>/dev/null | head -1
```

If type is `java`, prompt with a single choice:

> **Build verification level?**
> **[F]** fast — `mvn install -DskipTests -DskipITs` (default)
> **[U]** unit tests — `mvn install -DskipITs`
> **[I]** integration tests — `mvn install -DskipTests`
> **[A]** all tests — `mvn install`
> **[S]** skip

Map the answer to a command:
- F or Enter: `mvn install -DskipTests -DskipITs`
- U: `mvn install -DskipITs`
- I: `mvn install -DskipTests`
- A: `mvn install`
- S: skip step entirely

Run from project root:
```bash
mvn install [flags] -C "$PROJECT"
# or: mvn -f "$PROJECT/pom.xml" install [flags]
```

If the build **fails** → stop. Do not proceed to Step 9 (mark closed).
Report the failure and ask the user to fix it before closing.

If the build **passes** → add `✅ Build verified (mvn install)` to the 8h report and continue.

---

### Step path (alternative to all-at-once)

If user chose "step" in Step 7:

- Phase 1: Artifact routing (8a including publish-blog if blog/ has entries), 8b, 8c — confirm, execute, report → "Continue to journal merge? (y/n)"
- Phase 2: Journal merge (8d) — show each `§Section` before/after, confirm → "Continue to GitHub posting? (y/n)"
- Phase 3: Spec posting (8e), issue close (8f) → "Continue to branch merge? (y/n)"
- Phase 4: Merge project branch to `$PROJECT_BASE_BRANCH` (8j), build verification (8k if Java), EPIC-CLOSED.md, return workspace to main.

Note: publish-blog (8g) runs after issue close (8f), before 8i hygiene scan. It is not
an "offer" — it always runs. 8i then verifies the result; any unpublished entries block 8j.

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
