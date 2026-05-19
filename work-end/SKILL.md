---
name: work-end
description: >
  Close the current working branch. Promotes artifacts per routing config,
  merges the design journal into DESIGN.md, closes the GitHub issue, and
  returns both repos to main. Replaces "epic close". Must be invoked from
  the working branch (not main).
---

# work-end

Closes the current branch cleanly. Promotes artifacts, merges the journal,
closes the issue, marks the branch closed, returns to main.

---

## Path Resolution (run first, always)

```bash
PROJECT=$(grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //')
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md | head -1 | sed 's/.*`\(.*\)`.*/\1/')
```

---

## Pre-conditions

Check in order before proceeding:

1. **If `$WORKSPACE/design/.paused` exists** → hard stop.
   "You have a paused branch. Invoke `work-resume` first, then `work-end`."

2. **`$WORKSPACE/design/.meta` must exist on the current branch** → proceed.

3. **If `$WORKSPACE/design/.meta` exists but `$CURRENT_WORKSPACE == main`** (orphaned)
   → hard stop. Offer to switch to the surviving branch and close from there, or discard.

---

## Step 0 — Resolve paths

```bash
PROJECT=$(grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //')
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md | head -1 | sed 's/.*`\(.*\)`.*/\1/')
OWNER_REPO=$(grep "GitHub repo:" CLAUDE.md | head -1 | sed 's/.*GitHub repo: *//')
```

---

## Step 1 — Read context and extract variables

```bash
cat "$WORKSPACE/design/.meta"

BRANCH_NAME=$(grep "^branch:" "$WORKSPACE/design/.meta" | sed 's/branch: //')
PROJECT_SHA=$(grep "^project-sha:" "$WORKSPACE/design/.meta" | sed 's/project-sha: //')
ISSUE_N=$(grep "^issue:" "$WORKSPACE/design/.meta" | sed 's/issue: //')
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
[ "$DESIGN_REPO_KEY" = "workspace" ] && DESIGN_REPO="$WORKSPACE" || DESIGN_REPO="$PROJECT"
```

`$DESIGN_REPO` must remain available through Step 8d. Do not recalculate it in
subsequent steps.

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
  Publish blog       → offer after (N entries staged)

Approve all, or step by step? (all / step)
```

---

## Step 8 — Execute

Failures are reported but do not stop remaining steps, **except**: journal merge
failure prompts the user before continuing to issue close.

### 8a — Batch workspace-main operations (single main-visit)

```bash
# Stash any uncommitted workspace changes
git -C "$WORKSPACE" status --short | grep -q . && git -C "$WORKSPACE" stash

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

# If DESIGN_REPO = workspace: perform journal merge here while on workspace main
# (see 8d note — merge must happen on main, not on epic branch)
if [ "$DESIGN_REPO_KEY" = "workspace" ]:
  git -C "$WORKSPACE" checkout "$BRANCH_NAME" -- design/JOURNAL.md
  # Run journal merge steps (see 8d below)
  # Commit merge result to workspace main
  # Mark 8d as complete — skip the 8d block below

git -C "$WORKSPACE" push  # single push for all workspace-main commits

git -C "$WORKSPACE" checkout "$BRANCH_NAME"
git -C "$WORKSPACE" stash pop  # only if stashed above
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
run the full merge below on the project epic branch (included in the PR).

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
[ -n "$ISSUE_N" ] && gh issue close "$ISSUE_N" --repo "$OWNER_REPO"
```

### 8g — Offer publish-blog

If blog entries were staged to workspace, offer: "Publish blog entries now? (y/n)"

### 8h — Final report

```
✅ ADRs → project
✅ Specs → project
✅ Blog → workspace
✅ Plans → attic
✅ Journal merged → DESIGN.md (N sections)
✅ Specs posted to #N, issue closed
❌ Push failed — <path>. Run: git -C <path> push
```

### 8i — Offer hygiene scan

"Run branch hygiene scan? Checks Flyway conflicts, unmerged code, stale branches. (y/n)"

### Step path (alternative to all-at-once)

If user chose "step" in Step 7:

- Phase 1: Artifact routing — confirm, execute, report → "Continue to journal merge? (y/n)"
- Phase 2: Journal merge — show each `§Section` before/after, confirm → "Continue to GitHub posting? (y/n)"
- Phase 3: Spec posting, issue close, publish-blog offer → "Continue to branch cleanup? (y/n)"
- Phase 4: EPIC-CLOSED.md and return to main.

---

## Step 9 — Mark closed

```bash
CLOSE_DATE=$(date +%Y-%m-%d)
DELETE_DATE=$(date -v +14d +%Y-%m-%d 2>/dev/null || date -d "+14 days" +%Y-%m-%d)

cat > "$WORKSPACE/EPIC-CLOSED.md" << EOF
# Branch Closed — $BRANCH_NAME
**Date:** $CLOSE_DATE
**Issue:** #$ISSUE_N
**Scheduled for deletion:** $DELETE_DATE
EOF

git -C "$WORKSPACE" add EPIC-CLOSED.md
git -C "$WORKSPACE" commit -m "docs($BRANCH_NAME): mark closed, deletion due $DELETE_DATE"
git -C "$WORKSPACE" push
```

Branches are **not deleted**. `EPIC-CLOSED.md` is the signal for hygiene scan cleanup.

---

## Step 10 — Return to main

```
Return both repos to main? (y/n)
```

If y:
```bash
git -C "$PROJECT" checkout main
git -C "$WORKSPACE" checkout main
```

Check remote ahead; prompt before `pull --rebase`. Not automatic.
