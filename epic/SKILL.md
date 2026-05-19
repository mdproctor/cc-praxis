---
name: epic
description: >
  DEPRECATED. Use work-start (replaces /epic begin) and work-end (replaces
  /epic close). work-pause and work-resume are new. The workflows below are
  preserved for reference during migration only.
---

> ⚠️ **This skill is deprecated.** Use instead:
> - `work-start` — replaces `/epic begin` (branch creation is now integrated)
> - `work-end`   — replaces `/epic close`
> - `work-pause` — new: save context, switch to main
> - `work-resume` — new: restore context, return to branch
>
> The workflows below are preserved for reference during migration.
> Retire this skill once all sessions use the new commands.

# Epic (deprecated — see above)

Single entry point for the full epic lifecycle. Detects whether an epic is
currently active and routes to the appropriate workflow — start or close.

Requires CWD to be the workspace.

---

## Detection

```bash
current_branch=$(git branch --show-current)
meta_exists=$(test -f design/.meta && echo yes || echo no)
```

| State | Action |
|-------|--------|
| Not on a work branch, no `.meta` | Offer to start a new branch **or run branch hygiene scan** |
| On a work branch, `.meta` exists | Ask: close this branch, or start a new one? |
| On a work branch, no `.meta` | Warn: incomplete setup — offer to scaffold `.meta` and `design/JOURNAL.md`, then continue |
| **On main branch, `.meta` exists** | **Orphaned `.meta` — offer to complete close from here (see Workflow B-Orphaned below)** |

Epic branches and issue branches use identical workflow — the only difference is scope:
- **Epic branch** (`epic-<name>`): covers 1–N issues, multi-session design work
- **Issue branch** (`issue-<N>-<slug>`): covers 1 issue, typically single-session

Both get `.meta`, `JOURNAL.md`, artifact routing, journal merge at close. No exceptions.

**When no active branch:** always present the scan option alongside "start new branch":

```
No active branch. What next?

  [S] Start a new branch
  [H] Branch hygiene scan — find finished branches with unresolved issues
  [X] Nothing for now
```

If `[H]` → run Workflow C below.

---

## Workflow B-Orphaned — Closing from Main (orphaned .meta)

When `.meta` exists on the main branch, the epic branch was merged or deleted without going through epic close. The journal was never merged. Offer to complete the close:

```
⚠️  Orphaned epic detected: <epic-name> (started <date>)
   The project branch appears to have been merged without running epic close.
   The design journal may not have been merged into DESIGN.md.

Options:
  [C] Complete close — run journal merge and artifact promotion from here
  [D] Discard — remove .meta without closing (journal content will be lost)
  [S] Skip — leave as-is and proceed with something else
```

**If [C] — Complete close from main:**

The workspace epic branch may still exist. Check:
```bash
git branch -a | grep <epic-name>
```

- If workspace epic branch exists: switch to it (`git checkout <epic-name>`), then run Workflow B normally from Step B1.
- If workspace epic branch is gone: run journal merge directly from current `.meta` and the JOURNAL.md on main (if any content was committed there before branch deletion).

After close completes: remove `.meta` and commit on workspace main.

**If [D] — Discard:**
```bash
rm design/.meta design/JOURNAL.md 2>/dev/null
git add -A && git commit -m "chore: discard orphaned epic scaffold for <epic-name>"
```

---

## Workflow C — Branch Hygiene Scan

Finds epic branches that are finished but have unresolved issues: unmerged
journals, unpromoted artifacts, or branches past their scheduled deletion date.
Run from the workspace on `main`.

### Step C1 — Discover epic branches

Read project path from workspace CLAUDE.md:
```bash
grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //'
```

List all local epic-* branches in both repos:
```bash
# Workspace branches
git branch | grep 'epic-' | sed 's/^[* ]*//'

# Project branches
git -C <project-path> branch | grep 'epic-' | sed 's/^[* ]*//'
```

Union the two lists. For each branch name, check its status in the workspace repo.

### Step C2 — Assess each branch

**Flyway V-number conflict check:** Before checking code merge, scan for migration
version conflicts across all open epic branches. This catches the problem before
any branch attempts to merge.

```bash
# For each epic branch: extract its claimed V numbers from migration files
git -C <project-path> ls-tree <branch> --name-only -r \
  | grep -oP "V\d+(?=__)" | sort -n

# Also read flyway-next-v from .meta on that branch
git -C <workspace-path> show <branch>:design/.meta 2>/dev/null | grep "flyway-next-v"
```

Compare claimed V numbers across all open epic branches. Any overlap is a conflict
that must be resolved before either branch merges:

```
⚠️  V number conflict:
   epic-output-schema  claims V23, V24, V25
   epic-excluded-users also claims V23, V24
   → epic-excluded-users must renumber to V26, V27 before merging
```

Resolution: whichever branch merges second renumbers its migrations (file rename + commit).
Safe at any time while no production installations exist.

**Code merge check (most important):** Verify that implementation commits from the
epic branch have landed on project main. An epic with unmerged code was never shipped.

```bash
# How many commits on the epic branch are NOT in project main?
unmerged=$(git -C <project-path> log main..<branch> --oneline 2>/dev/null | wc -l)

# What are those commits? (show first 5)
git -C <project-path> log main..<branch> --oneline 2>/dev/null | head -5
```

If `unmerged > 0`: the implementation code was never merged to main — **Critical issue**.

If GitHub issue tracking is enabled, also check whether a PR was opened and merged:
```bash
# Check for a merged PR for this branch
gh pr list --repo <owner>/<repo> --state merged --head <branch> --json number,title,mergedAt 2>/dev/null
gh pr list --repo <owner>/<repo> --state open --head <branch> --json number,title 2>/dev/null
```

For each epic branch, also check workspace artifacts without switching branches:

```bash
# Does EPIC-CLOSED.md exist on this branch?
git show <branch>:EPIC-CLOSED.md 2>/dev/null

# Are there unremoved spec files for this epic?
git ls-tree <branch> specs/<branch>/ 2>/dev/null

# What is the scheduled deletion date (from EPIC-CLOSED.md)?
git show <branch>:EPIC-CLOSED.md 2>/dev/null | grep "Scheduled for deletion"
```

Also check the project repo for promoted artifacts:
```bash
# Was the spec promoted to docs/specs/ on the project's main?
ls <project-path>/docs/specs/ 2>/dev/null | grep -i <short-epic-name>

# Is there a plan in the attic?
ls plans/attic/<branch>/ 2>/dev/null
```

Build a status for each branch:

| Check | Good | Issue |
|-------|------|-------|
| **Code merged to project main** | ✅ Merged (0 unmerged commits) | 🚨 Code not merged — N commits unshipped |
| **PR merged** (if GitHub tracking) | ✅ PR merged / no PR needed | ⚠️ PR open or none found |
| `EPIC-CLOSED.md` exists | ✅ Closed | ⚠️ Never closed |
| Scheduled deletion date | shows date | ⚠️ No date — legacy marker |
| Scheduled deletion date passed | future | 🗑️ Eligible for deletion |
| `specs/<branch>/` is empty or absent | ✅ Clean | ⚠️ Unremoved specs |
| `docs/specs/` has promoted files | ✅ Promoted | ⚠️ Spec never promoted |
| `plans/attic/<branch>/` exists | ✅ Archived | ⚠️ Plan never archived |

**Do NOT offer deletion for any branch with 🚨 unmerged code** — those commits
would be permanently lost. Block deletion until the code merge issue is resolved.

### Step C3 — Present report

```
Branch hygiene scan — <N> epic branches found

  Branch                 Flyway  Code           Closed        Artifacts    Deletion
  ──────────────────────────────────────────────────────────────────────────────────
  epic-payments          ✅ V18   ✅ merged       ✅ 2026-04-01  ✅ clean     🗑️ overdue
  epic-auth-redesign     ✅ V19   ✅ merged       ✅ 2026-05-10  ✅ clean     ⏳ 2026-05-24
  epic-output-schema     ⚠️ V23↔V23  🚨 4 commits  ✅ 2026-05-17  ✅ clean     🔒 blocked
  epic-excluded-users    ⚠️ V23↔V23  🚨 4 commits  ✅ 2026-05-18  ✅ clean     🔒 blocked
  epic-old-feature       ✅ none  🚨 3 commits   ⚠️ never closed  ⚠️ no spec   🔒 blocked
```

Flyway conflicts (⚠️) and unmerged code (🚨) both **block deletion**. Flyway conflicts
are shown first since they must be resolved before a code merge is attempted.

### Step C4 — Offer fixes for each issue

**For branches with 🚨 unmerged code:**

```
epic-old-feature — 3 commits on project branch not in main:
  abc1234 feat: add payment validation
  def5678 test: payment validation tests
  ghi9012 docs: sync DESIGN.md for payment validation

Options:
  [M] Merge to main — switch to project epic branch, then merge/cherry-pick to main
  [P] Open PR — create a PR from this branch to main
  [S] Skip — leave for manual resolution (branch stays blocked for deletion)
```

**For branches with ⚠️ artifact issues (only if code is merged):**

```
epic-old-feature has artifact issues:
  ⚠️ Never closed — no EPIC-CLOSED.md found
  ⚠️ specs/epic-old-feature/design.md not removed from workspace
  ⚠️ Spec never promoted to docs/specs/

Options:
  [F] Fix — run epic close for this branch (switch to it, run Workflow B)
  [S] Skip — leave as-is
  [D] Discard — mark closed with today's date, no journal merge (data may be lost)
```

**For branches with 🗑️ Eligible for deletion (code merged + artifacts clean):**

```
epic-payments — closed 2026-04-01, deletion was due 2026-04-15 (N days overdue)
  Code: ✅ merged to main
  Artifacts: ✅ spec promoted, plan archived

Delete branches?
  workspace: epic-payments
  project:   epic-payments
  (y/n — or 'skip' to leave for later)
```

If `y`:
```bash
git -C <project-path> branch -d epic-payments
git branch -d epic-payments
```

If the branch cannot be deleted (`-d` fails because Git detects unmerged commits
despite the log check), use `--force` only after explicitly confirming with the
human that the code is safe to lose.

### Step C5 — Summary

After processing all branches, report what was done and what remains:

```
Hygiene scan complete:
  ✅ Deleted: epic-payments (both repos)
  ✅ Fixed: epic-old-feature (ran close workflow)
  ⏳ Retained: epic-auth-redesign (deletion due 2026-05-24)
  ⏳ Retained: epic-output-schema (deletion due 2026-05-31)
```

---

## Workflow A — Starting an Epic

### Step A0 — Validate state before starting

Read the project path from workspace CLAUDE.md:
```bash
grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //'
```

Check both repos are on the same branch:
```bash
project_branch=$(git -C <project-path> branch --show-current)
workspace_branch=$(git branch --show-current)
```

If they differ, stop:
```
⚠️ Branch mismatch: project is on '<project_branch>', workspace is on '<workspace_branch>'.
   Switch both repos to the same branch before starting an epic.
```

Check for orphaned `.meta` on main:
```bash
if [ "$workspace_branch" = "main" ] && [ -f design/.meta ]; then
  echo "⚠️ Orphaned design/.meta found on main — a previous epic may not have been cleanly closed."
  cat design/.meta
  echo "Remove design/.meta and design/JOURNAL.md to clean up? (y/n)"
fi
```

If the user confirms cleanup:
```bash
rm -f design/.meta design/JOURNAL.md
git add -A && git commit -m "chore: remove orphaned epic scaffold from main"
```

### Step A1 — Get epic name

Ask: "What's the branch name? (e.g. `epic-payments` or `issue-13-remove-workarounds`)"

Rules:
- Lowercase with hyphens
- Epic branches: prefix with `epic-` (e.g. `epic-payments`, `epic-auth-redesign`) — covers 1–N issues
- Issue branches: prefix with `issue-<N>-` (e.g. `issue-13-remove-workarounds`) — covers 1 issue
- Workflow is identical for both

If currently on a work branch (starting a new branch while one is active):

```
You're currently on <current-branch>. Starting a new branch requires
returning to main first. Switch to main on both repos and continue? (y/n)
```

If yes:
```bash
git -C <project-path> checkout main
git checkout main
```

If no → stop.

Read the project path from workspace CLAUDE.md `## Session Start` → `add-dir` line:

```bash
grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //'
```

### Step A2 — Create branches

```bash
# Create project branch
git -C <project-path> checkout -b <epic-name>

# Create workspace branch
git checkout -b <epic-name>
```

Confirm both commands succeeded before continuing. If either fails (branch
already exists, uncommitted changes), report the error and stop — do not
proceed with a partial setup.

### Step A3 — Scaffold workspace

```bash
mkdir -p design
```

Create `design/JOURNAL.md`:

```markdown
# Design Journal — <epic-name>
```

**Scan for the next safe Flyway V number** (before writing `.meta`) if this epic will add
migrations to the core sequential V1–V999 range:

```bash
# Highest V on main
v_main=$(git -C <project-path> log main --name-only --format="" \
  | grep -oP "(?<=V)\d+(?=__)" | sort -n | tail -1)

# Highest V on any remote epic branch
git -C <project-path> fetch --all 2>/dev/null
v_branches=$(git -C <project-path> log --remotes="*/epic-*" --name-only --format="" \
  | grep -oP "(?<=V)\d+(?=__)" | sort -n | tail -1)

# Next safe V = max(v_main, v_branches) + 1
echo "Next safe Flyway V: $(( [highest of v_main, v_branches] + 1 ))"
```

Record this as `flyway-next-v` in `.meta`. If the epic will not add any core runtime
migrations (optional-module-range epics, or non-schema epics), set `flyway-next-v: none`.

Create `design/.meta`:

```
epic: <epic-name>
project-sha: <output of: git -C <project-path> rev-parse HEAD>
date: <YYYY-MM-DD>
issue:
flyway-next-v: <N or none>
design-section-hashes: <see below>
```

**Record DESIGN.md section heading hashes** — these protect the journal merge from renamed or deleted sections:

```bash
# Extract all H2 headings from DESIGN.md and record their hashes
grep "^## " <design-repo>/DESIGN.md 2>/dev/null | md5 | head -c 8
# Or per-section:
grep "^## " <design-repo>/DESIGN.md 2>/dev/null | while read heading; do
  echo "$heading" | md5 | head -c 8 | tr -d '\n'; echo " $heading"
done
```

Write the result as `design-section-hashes:` in `.meta`, one hash+heading per line (indented). If DESIGN.md does not exist yet, leave `design-section-hashes:` empty.

**Routing-aware SHA baseline:** Before writing `project-sha`, read the workspace
`CLAUDE.md ## Routing` config (and global `~/.claude/CLAUDE.md ## Routing`). If the
resolved `design` destination is `workspace`, record the **workspace/main HEAD SHA**
instead of the project HEAD SHA:

```bash
# If design → workspace:
git -C <workspace-path> rev-parse main   # use this as the baseline SHA
# If design → project (default):
git -C <project-path> rev-parse HEAD     # use this (current behaviour)
```

This ensures the journal merge at epic-close compares against the right DESIGN.md
(workspace/main's, not the project's) when design artifacts live in the workspace.

### Step A4 — GitHub issue

If `## Work Tracking` with `Issue tracking: enabled` exists in CLAUDE.md:

1. Search for an existing open issue:
   ```bash
   gh issue list --repo <owner>/<repo> --state open --search "<epic-name>" --json number,title
   ```

2. If found → confirm with user:
   > "Found issue #N: `<title>`. Use this for the epic? (y/n)"
   - If yes: fill in `issue: <N>` in `design/.meta`

3. If not found → offer to create:
   > "No existing issue found. Create one? (y/n)"
   - If yes:
     ```bash
     gh issue create --repo <owner>/<repo> \
       --title "<epic-name>" \
       --body "Epic branch: \`<epic-name>\`"
     ```
     Record the returned issue number in `design/.meta` `issue:` field.

If issue tracking is not enabled in CLAUDE.md → skip silently.

### Step A5 — Commit workspace scaffold

```bash
git add design/JOURNAL.md design/.meta
git commit -m "init(<epic-name>): scaffold workspace branch"
```

### Step A6 — Offer brainstorming

Prompt: "Start a brainstorm for this epic? (y/n)"

- Yes → invoke `brainstorming` skill. Brainstorming output (specs) must be written to `specs/<epic-name>/` not `specs/` — pass the epic name as context so specs are scoped to this epic.
- No → done

> **Note on spec scoping:** Specs created during an epic must live in `specs/<epic-name>/` so epic close can promote only this epic's specs, not specs from previous epics. Brainstorming is responsible for writing to the correct subdirectory when an epic is active.

---

## Workflow B — Closing an Epic

### Step B1 — Read .meta and routing config

```bash
cat design/.meta
```

Extract: `epic`, `project-sha`, `issue` (may be empty).

Read project path from workspace CLAUDE.md:
```bash
grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //'
```

Read GitHub repo from workspace CLAUDE.md `## Work Tracking` → `GitHub repo:` line:
```bash
grep "GitHub repo:" CLAUDE.md | head -1 | sed 's/.*GitHub repo: *//'
```

#### Step B1a — Read Layer 2 (global routing default)

```bash
grep -A 5 "^## Routing$" "$HOME/.claude/CLAUDE.md" 2>/dev/null \
  | grep "^\*\*Default destination:\*\*" \
  | sed 's/\*\*Default destination:\*\* *//'
```

Valid values: `workspace` or `project` only. If the value is anything else, warn:
```
⚠️ Invalid global routing value '<X>' in ~/.claude/CLAUDE.md ## Routing.
   Valid values: project | workspace
   Ignoring Layer 2 — falling through to Layer 1.
```
If the `## Routing` section is absent or has no valid `**Default destination:**` line,
Layer 2 is considered absent.

#### Step B1b — Read Layer 3 (workspace per-artifact overrides)

```bash
grep -A 30 "^## Routing$" "$WORKSPACE/CLAUDE.md" 2>/dev/null
```

Parse the markdown table for per-artifact rows. Valid values per cell:
`workspace`, `project`, `alternative <path>`.

**Deprecated vocabulary check:** If the routing config (Layer 2 or Layer 3) contains
any of the following, warn before using the value:
- `base` — deprecated alias; use `project` or `workspace`
- `project repo` — deprecated phrase; use `project`
- A table key named `design-journal` — deprecated key; use `journal`

Warn for each deprecated value found:
```
⚠️ Routing config uses deprecated value '<X>'.
   Replace with: project | workspace | alternative <path>
   Falling through to next layer for this artifact.
```

If Layer 3 is absent or empty, skip to Layer 2.

#### Step B1c — Derive design repo

Apply the three-layer algorithm for the `design` artifact (same as Step B5) to resolve
the destination, then set `<design-repo>`:

- `design → workspace`: `<design-repo>` = `.` (workspace CWD)
- `design → project` (or Layer 1 default): `<design-repo>` = `<project-path>`

Use `<design-repo>` throughout B3, B7a, and B7b for all DESIGN.md operations.

### Step B2 — Inventory artifacts

```bash
ls adr/ 2>/dev/null | grep -v INDEX.md          # ADRs
ls blog/ 2>/dev/null | grep -v INDEX.md         # Blog entries
ls snapshots/ 2>/dev/null | grep -v INDEX.md    # Snapshots
ls specs/<epic-name>/ 2>/dev/null                 # Specs for this epic only
ls plans/ 2>/dev/null | grep -v "^attic$"        # Plans (exclude attic/)
cat design/JOURNAL.md 2>/dev/null               # Journal
```

### Step B3 — Generate journal merge preview

Retrieve baseline DESIGN.md at the recorded SHA (using `<design-repo>` from Step B1c):

```bash
git -C <design-repo> show <project-sha>:DESIGN.md 2>/dev/null || echo "(no DESIGN.md at baseline)"
```

Read current `<design-repo>/DESIGN.md`.

**If current DESIGN.md does not exist:**
```
⚠️ No DESIGN.md found in <design-repo>.

Options:
  [C] Create DESIGN.md from journal entries — journal becomes the initial design document
  [S] Skip journal merge entirely
```
If `C`: write journal entries as the initial `DESIGN.md` content, commit to `<design-repo>`, then mark journal merge as complete in the close plan.
If `S`: skip journal merge; note in final report.

**Check for section heading drift** — compare current DESIGN.md headings against the hashes recorded in `.meta` at epic start:

```bash
# Re-hash current headings
grep "^## " <design-repo>/DESIGN.md 2>/dev/null | while read heading; do
  echo "$heading" | md5 | head -c 8 | tr -d '\n'; echo " $heading"
done
```

Compare against `design-section-hashes:` in `.meta`. For each §Section anchor in JOURNAL.md, check the corresponding heading still exists in DESIGN.md with the same text.

If any headings were renamed or deleted since epic start:
```
⚠️  Section heading drift detected:
   Journal references §<Name> but DESIGN.md heading changed to "<NewName>" (or was removed).
   
   These journal entries will not merge correctly without manual intervention.
   
   Options:
     [U] Update journal anchors to match new heading names — then continue
     [S] Skip merge for drifted sections
     [A] Abort close — fix headings or journal anchors manually first
```

Wait for user decision before proceeding to anchor validation.

**Validate journal anchors before proceeding:**
```bash
# Count entries with §Section anchors
grep -c "^### .*·.*§" design/JOURNAL.md 2>/dev/null || echo 0
# Count all entries
grep -c "^### " design/JOURNAL.md 2>/dev/null || echo 0
```

If any entries lack `§SectionName` anchors, surface a warning before presenting the close plan:
```
⚠️ Journal anchor check: N of M entries have §Section anchors.
   Entries without anchors will be silently skipped during DESIGN.md merge.

   Unanchored entries:
   - <entry header>

   Options:
     [F] Fix anchors now — run java-update-design to tag missing entries
     [S] Skip journal merge entirely for this close
     [C] Continue anyway — accept that unanchored entries will not be merged
```

Wait for user decision before continuing to the merge preview.

Read `design/JOURNAL.md` — extract all `§Section` anchors from entry headers
(lines matching `^### .* · §`).

For each anchored section: note the baseline content, the current project content,
and the journal narrative. This forms the merge preview.

If `design/JOURNAL.md` has no `§Section` entries:

```
⚠️  Journal is empty — no design decisions were recorded during this epic.
   This usually means java-update-design was not called during development
   (e.g. commits were made directly without going through java-git-commit).

   Options:
     [W] Write a retrospective journal entry now — invoke java-update-design
         to capture the key design decisions before closing
     [S] Skip journal merge — accept that design narrative will not be captured
         in DESIGN.md (the DESIGN.md capability row added by implementation-doc-sync
         will still be present, but the design rationale will be missing)
```

**If [W]:** invoke `java-update-design` with a description of the key design decisions
made during the epic. After the entry is written and committed with a valid `§Section`
anchor, re-read `design/JOURNAL.md` and continue to the merge preview.

**If [S]:** skip journal merge; note in the final close report that the journal was
empty and no narrative was captured. This is a permanent loss — the git history will
not contain the design rationale for this epic.

### Step B4 — Ask user to select specs

If an issue number exists in `design/.meta` and issue tracking is enabled:

Present list of files in `specs/<epic-name>/`:

```
Select specs to post to GitHub issue #<N>:
  1. <filename>
  2. <filename>
  ...

Enter numbers (e.g. "1 2"), "all", or "none":
```

If no issue or tracking disabled → skip this step silently.

### Step B5 — Resolve destinations

Apply the three-layer routing algorithm for each artifact type with files present:

1. **Layer 3 check:** If a per-artifact row exists in the Layer 3 workspace CLAUDE.md
   `## Routing` table and the value is valid → use that value.
2. **Layer 2 check:** Else if Layer 2 is present and has a valid `**Default destination:**`
   line → use that value for this artifact.
3. **Layer 1 default:** Else → use `project`.

Edge cases:
- `alternative <path>` is valid at Layer 3 only; if seen at Layer 2, warn and fall to Layer 1.
- `alternative` without a path → invalid; warn and fall to next layer.
- Any deprecated vocabulary (see Step B1b) → warn and fall to next layer.

After resolving all artifacts, show the routing table and the layer source for each:

```
Resolved routing for this epic:
  adr       → workspace   (Layer 3 workspace override)
  blog      → project     (Layer 1 default)
  design    → workspace   (Layer 2 global default)
  snapshots → project     (Layer 1 default)

Proceed? (y/n)
```

Do not proceed until the user confirms. If the user says `n`, stop and let them fix
their routing config before re-running.

Detect destination capability for each resolved path:

```bash
detect_capability() {
  local dest="$1"
  if [ -d "$dest/.git" ]; then
    if git -C "$dest" remote get-url origin &>/dev/null 2>&1; then
      echo "remote-git"
    else
      echo "local-git"
    fi
  else
    echo "filesystem"
  fi
}
```

### Step B6 — Present close plan and prompt

```
Epic close plan — <epic-name>

  Artifact routing
  ├── adr/<N files>            → <destination>  [<capability>]
  ├── blog/<N files>           → <destination>  [<capability>]
  ├── specs/<N files>          → <destination>  [<capability>]
  └── design/JOURNAL.md        → <destination>  [<capability>]

  Plan archiving
  └── plans/<N files>          → plans/attic/<epic-name>/  [workspace main]

  Journal merge
  ├── §<Section1>              <one-line change summary>
  └── §<Section2>              <one-line change summary>

  GitHub issue #<N>
  ├── Post: <selected spec filenames>
  └── Close issue

  Branch cleanup
  └── <epic-name> (project + workspace) — prompt after

  (Skipped sections show "(skipped — nothing to do)")

Approve all, or go step by step? (all / step)
```

### Step B7a — "all" path

Execute all steps in order. On any failure: continue remaining steps, report at the end.

**Artifact promotion:**

The workspace epic branch is **not merged into workspace main**. Instead, each artifact is explicitly copied to its routing destination and committed there before the epic branch is deleted. This ensures every artifact that should survive lands on the correct main branch, and ephemeral scaffolding (`.meta`, `JOURNAL.md`) is cleanly discarded with the branch.

For each artifact file, resolve destination:
- `project` → copy to **project main** (or promote via the PR that merges the project epic branch)
- `workspace` → copy to **workspace main** — switch to main, copy, commit, switch back to epic branch

```bash
# For workspace-routed artifacts (blog, snapshots):
git stash
git checkout main
git -C <workspace-path> pull --rebase origin main
mkdir -p "<workspace-dest>"
git checkout <epic-name> -- <artifact-files>
git -C <workspace-path> add <workspace-dest>/
git -C <workspace-path> commit -m "feat: promote <artifact-type> from epic <epic-name>"
git -C <workspace-path> push
git checkout <epic-name>
git stash pop

# For project-routed artifacts (specs, adr):
mkdir -p "<project-dest>"
cp "<file>" "<project-dest>/"
git -C "<project-path>" add <project-dest>/
git -C "<project-path>" commit -m "feat: promote <artifact-type> from epic <epic-name>"
```

If `remote-git`:
```bash
git -C "<dest>" push
```

**Spec cleanup** (after promotion confirmed):
Remove the promoted spec copies from the workspace staging area:
```bash
rm specs/<promoted-files>
git add -A
git commit -m "chore(<epic-name>): remove promoted specs from workspace staging"
```

**Plan archiving** (plans always archive to workspace main):
Plans are moved to `plans/attic/<epic-name>/` on the workspace `main` branch so they survive branch deletion:
```bash
# Stash any uncommitted workspace changes
git stash

# Switch workspace to main and sync
git checkout main
git -C <workspace-path> pull --rebase origin main

# Copy plan files from the epic branch into attic
git checkout <epic-name> -- plans/<file1> plans/<file2> ...
mkdir -p plans/attic/<epic-name>
mv plans/<file1> plans/<file2> ... plans/attic/<epic-name>/
git add -A
git commit -m "archive(<epic-name>): move plans to attic"
git -C <workspace-path> push

# Return to epic branch
git checkout <epic-name>
git stash pop
```

**Journal merge:**
1. Read baseline: `git -C <design-repo> show <project-sha>:DESIGN.md` — extract the `§Section` content from the baseline
2. Read the same section from the current `<design-repo>/DESIGN.md` — note independent changes on main
3. Apply journal narrative to the current section, incorporating independent changes
4. Write the merged result back to `<design-repo>/DESIGN.md`
5. Re-read each updated `§Section` in `<design-repo>/DESIGN.md`; confirm it reflects the journal narrative. Report any section that looks wrong before continuing.
6. Commit:
   ```bash
   git -C <design-repo> add DESIGN.md
   git -C <design-repo> commit -m "docs(<epic-name>): apply design journal — <date>"
   ```

**Spec posting:**
For each selected spec:
```bash
SUMMARY=$(head -30 "<spec-file>" | grep -A5 "## Problem\|## Summary" | tail -5)
BODY=$(cat "<spec-file>")

gh issue comment <issue> --repo <owner>/<repo> --body "## Design Spec — <filename>

${SUMMARY}

<details>
<summary>Full spec (click to expand)</summary>

${BODY}

</details>"
```

**Close issue:**
```bash
gh issue close <issue> --repo <owner>/<repo>
```

**Offer publish-blog** (if any blog entries were promoted to workspace during this epic):
```
Blog entries were staged to workspace during this epic.
Publish them to mdproctor.github.io now? (y/n)
```
If yes → invoke `publish-blog` for the entries promoted in this epic.

**Final report:**
```
✅ <N> ADRs promoted → <destination>
✅ Journal merged → DESIGN.md (<design-repo>)
✅ Spec posted to #<N>, issue closed
❌ Push failed — <dest> has no network. Run: git -C <dest> push
```

### Step B7b — "step" path

**Phase 1 — Artifact routing**

Show what will be promoted where. Prompt: "Promote artifacts? (y/n)"

If yes: execute promotion for all artifact types (same logic as Step B7a).
Report results. Prompt: "Continue to journal merge? (y/n)"

**Phase 2 — Journal merge**

For each `§Section` in the journal, show:

```
§<SectionName> (journal — last updated <date>):
  <journal narrative>

Current §<SectionName> (<design-repo>):
  <current content>

Will update §<SectionName> with journal narrative,
preserving any independent main-branch changes.
```

Prompt: "Apply journal merge? (y/n)"

If yes:
1. Apply all section updates to `<design-repo>/DESIGN.md`
2. Post-merge verification: re-read each updated section, confirm it reflects the journal. Report any section that looks wrong.
3. Commit:
   ```bash
   git -C <design-repo> add DESIGN.md
   git -C <design-repo> commit -m "docs(<epic-name>): apply design journal — <date>"
   ```

Prompt: "Continue to GitHub posting? (y/n)"

**Phase 3 — GitHub posting and cleanup**

Post each selected spec as a comment (same format as Step B7a).
Close the issue.
Prompt: "Continue to branch cleanup? (y/n)"

### Step B8 — Mark closed and return to main

Branches are **never deleted automatically**. Instead, they are marked with a
14-day retention window. This allows verification that the workspace/journal
workflow produced correct results before data is discarded.

**Step 8.1 — Write EPIC-CLOSED.md on the workspace epic branch**

Calculate deletion date = today + 14 days. Create `EPIC-CLOSED.md`:

```markdown
# Epic Closed — <epic-name>
**Date:** <YYYY-MM-DD>
**Issue:** #<N>
**Status:** Closed
**Scheduled for deletion:** <YYYY-MM-DD + 14 days>

Branches `<epic-name>` retained in project and workspace repos.
Delete manually once the workspace/journal workflow has been verified,
or after the scheduled date, whichever comes first.
```

```bash
git add EPIC-CLOSED.md
git commit -m "docs(<epic-name>): mark epic closed, scheduled for deletion <date>"
```

**Step 8.2 — Switch both repos to main (prompt before doing so)**

```
Close complete. Return both repos to main?
  project:   <epic-name> → main
  workspace: <epic-name> → main
(y/n)
```

Wait for explicit confirmation. If `y`:

```bash
git -C <project-path> checkout main
git checkout main

# Check if remote main is ahead — prompt before incorporating upstream changes
PROJECT_BEHIND=$(git -C <project-path> rev-list HEAD..origin/main --count 2>/dev/null || echo 0)
if [ "$PROJECT_BEHIND" -gt 0 ]; then
  echo "Remote main has ${PROJECT_BEHIND} new commits since this epic started."
  echo "Incorporate now with pull --rebase? Upstream changes may conflict with epic work. (y/n)"
  # If yes: git -C <project-path> pull --rebase origin main
  # If no:  leave local main as-is; user handles sync separately
fi
```

If `n` (don't return to main): stop here. The human will switch manually.

**Do NOT offer to delete branches.** Deletion is a manual or scheduled operation
outside the epic close workflow. The `EPIC-CLOSED.md` file with its deletion date
is the signal for future cleanup.

---

## Edge Cases

| Situation | Behaviour |
|-----------|-----------|
| No `design/JOURNAL.md` entries | Skip journal merge step; mark `(skipped)` in plan |
| No files in `specs/` | Skip spec selection step |
| No issue in `.meta` or tracking disabled | Skip all GitHub steps silently |
| Destination path doesn't exist | `mkdir -p <dest>` before promoting |
| Push fails (no network) | Report failure with manual resolution command; continue |
| Project has no `DESIGN.md` | Offer to create from journal entries, or skip merge entirely |
| `design/JOURNAL.md` after close | Remains in workspace git history; not promoted to project repo |
| On epic branch, no `.meta` | Warn: incomplete setup — offer to scaffold `.meta` and `design/JOURNAL.md` |

---

## Success Criteria

### Starting an epic

- [ ] Project branch `<epic-name>` created
- [ ] Workspace branch `<epic-name>` created
- [ ] `design/JOURNAL.md` exists with stub header
- [ ] `design/.meta` exists with epic name, project SHA, date
- [ ] `design/.meta` `issue:` field populated (if tracking enabled and issue found/created)
- [ ] Workspace scaffold committed

### Closing an epic

- [ ] All artifacts promoted to declared destinations (or failures reported with resolution commands)
- [ ] Promoted spec copies removed from workspace `specs/` staging area
- [ ] Plans archived to `plans/attic/<epic-name>/` on workspace `main`
- [ ] Journal merged into `DESIGN.md` (or created from journal if DESIGN.md was absent), user confirmed
- [ ] Post-merge verification: each `§Section` anchor confirmed in updated doc
- [ ] Selected spec(s) posted to GitHub issue
- [ ] GitHub issue closed (if tracking enabled)
- [ ] `EPIC-CLOSED.md` created on workspace epic branch with 14-day deletion date
- [ ] Both repos switched to `main` (user confirmed)

---

## Skill Chaining

**Invoked by:** User directly via `/epic`

**Invokes (start):** `superpowers:brainstorming` — if user accepts the prompt in Step A6

**Reads output of (close):** [`java-update-design`] and [`update-primary-doc`] from `design/JOURNAL.md`
