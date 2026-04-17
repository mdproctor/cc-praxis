---
name: epic
description: >
  Use when a development epic needs to begin or wrap up — user says "begin
  epic", "new epic", "close epic", "finish epic", or invokes /epic. Detects
  whether an epic is currently active and routes accordingly.
---

# Epic

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
| Not on epic branch, no `.meta` | Offer to start a new epic |
| On epic branch, `.meta` exists | Ask: close this epic, or start a new one? |
| On epic branch, no `.meta` | Warn: incomplete setup — offer to scaffold `.meta` and `design/JOURNAL.md`, then continue |

---

## Workflow A — Starting an Epic

### Step A1 — Get epic name

Ask: "What's the epic name? (e.g. `epic-payments`)"

Rules:
- Lowercase with hyphens
- Prefix with `epic-` (e.g. `epic-payments`, `epic-auth-redesign`)

If currently on an epic branch (starting a second epic while one is active):

```
You're currently on <current-branch>. Starting a new epic requires
returning to main first. Switch to main on both branches and continue? (y/n)
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

Create `design/.meta`:

```
epic: <epic-name>
project-sha: <output of: git -C <project-path> rev-parse HEAD>
date: <YYYY-MM-DD>
issue:
```

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

- Yes → invoke `brainstorming` skill
- No → done

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

### Step B2 — Inventory artifacts

```bash
ls adr/ 2>/dev/null | grep -v INDEX.md      # ADRs
ls blog/ 2>/dev/null | grep -v INDEX.md     # Blog entries
ls snapshots/ 2>/dev/null | grep -v INDEX.md  # Snapshots
ls specs/ 2>/dev/null                        # Specs (user selects)
cat design/JOURNAL.md 2>/dev/null            # Journal
```

### Step B3 — Generate journal merge preview

Retrieve baseline project DESIGN.md at the recorded SHA:

```bash
git -C <project-path> show <project-sha>:DESIGN.md 2>/dev/null || echo "(no DESIGN.md at baseline)"
```

Read current `<project-path>/DESIGN.md`.

Read `design/JOURNAL.md` — extract all `§Section` anchors from entry headers
(lines matching `^### .* · §`).

For each anchored section: note the baseline content, the current project content,
and the journal narrative. This forms the merge preview.

If `design/JOURNAL.md` has no `§Section` entries → skip journal merge in the plan.

### Step B4 — Ask user to select specs

If an issue number exists in `design/.meta` and issue tracking is enabled:

Present list of files in `specs/`:

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
  └── design/JOURNAL.md        → <destination>  [<capability>]

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
For each artifact file and its resolved destination:
```bash
mkdir -p "<dest>"
cp "<file>" "<dest>/"
```

If `local-git` or `remote-git`:
```bash
git -C "<dest>" add .
git -C "<dest>" commit -m "feat: promote <artifact-type> from <project> epic <epic-name>"
```

If `remote-git`:
```bash
git -C "<dest>" push
```

**Journal merge:**
1. Read baseline: `git -C <project-path> show <project-sha>:DESIGN.md` — extract the `§Section` content from the baseline
2. Read the same section from the current project `DESIGN.md` — note independent changes on main
3. Apply journal narrative to the current section, incorporating independent changes
4. Write the merged result back to `<project-path>/DESIGN.md`
5. Re-read each updated `§Section` in the project `DESIGN.md`; confirm it reflects the journal narrative. Report any section that looks wrong before continuing.
6. Commit:
   ```bash
   git -C <project-path> add DESIGN.md
   git -C <project-path> commit -m "docs(<epic-name>): apply design journal — <date>"
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

**Final report:**
```
✅ <N> ADRs promoted → <destination>
✅ Journal merged → project DESIGN.md
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

Current project §<SectionName>:
  <current content>

Will update §<SectionName> with journal narrative,
preserving any independent main-branch changes.
```

Prompt: "Apply journal merge? (y/n)"

If yes:
1. Apply all section updates to `<project-path>/DESIGN.md`
2. Post-merge verification: re-read each updated section, confirm it reflects the journal. Report any section that looks wrong.
3. Commit:
   ```bash
   git -C <project-path> add DESIGN.md
   git -C <project-path> commit -m "docs(<epic-name>): apply design journal — <date>"
   ```

Prompt: "Continue to GitHub posting? (y/n)"

**Phase 3 — GitHub posting and cleanup**

Post each selected spec as a comment (same format as Step B7a).
Close the issue.
Prompt: "Continue to branch cleanup? (y/n)"

### Step B8 — Branch cleanup (both paths)

Prompt:
```
Delete epic branches?
  project: <epic-name>
  workspace: <epic-name>

  y → delete both, return to main
  n → keep both; mark epic as closed
```

If `y`:
```bash
git -C <project-path> checkout main
git -C <project-path> branch -d <epic-name>
git checkout main
git branch -d <epic-name>
```

If `n`: create `EPIC-CLOSED.md` in workspace branch root:
```markdown
# Epic Closed — <epic-name>
**Date:** <today>
**Issue:** #<N>
**Status:** Closed — branch retained for inspection
```

```bash
git add EPIC-CLOSED.md
git commit -m "docs(<epic-name>): mark epic as closed"
```

---

## Edge Cases

| Situation | Behaviour |
|-----------|-----------|
| No `design/JOURNAL.md` entries | Skip journal merge step; mark `(skipped)` in plan |
| No files in `specs/` | Skip spec selection step |
| No issue in `.meta` or tracking disabled | Skip all GitHub steps silently |
| Destination path doesn't exist | `mkdir -p <dest>` before promoting |
| Push fails (no network) | Report failure with manual resolution command; continue |
| Project has no `DESIGN.md` | Skip journal merge; note in summary |
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
- [ ] Journal merged into project `DESIGN.md`, user confirmed
- [ ] Post-merge verification: each `§Section` anchor confirmed in updated doc
- [ ] Selected spec(s) posted to GitHub issue
- [ ] GitHub issue closed (if tracking enabled)
- [ ] Branch cleanup resolved — both branches deleted or `EPIC-CLOSED.md` created
- [ ] Workspace and project both on `main`

---

## Skill Chaining

**Invoked by:** User directly via `/epic`

**Invokes (start):** `superpowers:brainstorming` — if user accepts the prompt in Step A6

**Reads output of (close):** [`java-update-design`] and [`update-primary-doc`] from `design/JOURNAL.md`
