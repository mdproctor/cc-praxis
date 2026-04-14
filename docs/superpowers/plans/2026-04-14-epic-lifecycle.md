# Epic Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement JOURNAL.md integration into existing design skills, and create the `epic-start` and `epic-close` skills that complete the workspace branch lifecycle.

**Architecture:** Design skills write structured journal entries to `design/JOURNAL.md` instead of the project `DESIGN.md` directly. `epic-start` scaffolds the branch + journal + SHA baseline. `epic-close` routes artifacts per declarative config, merges the journal into the project `DESIGN.md`, posts to GitHub, and handles branch cleanup.

**Tech Stack:** Markdown skills, bash, `gh` CLI, Python validators, pytest

**Specs:**
- `docs/superpowers/specs/2026-04-13-design-journal-design.md`
- `docs/superpowers/specs/2026-04-13-artifact-routing-design.md`
- `docs/superpowers/specs/2026-04-14-epic-lifecycle-design.md`

---

## File Map

**Create:**
- `epic-start/SKILL.md`
- `epic-start/commands/epic-start.md`
- `epic-close/SKILL.md`
- `epic-close/commands/epic-close.md`

**Modify:**
- `java-update-design/SKILL.md` — write journal entry to `design/JOURNAL.md` instead of rewriting `design/DESIGN.md`
- `update-primary-doc/SKILL.md` — same change
- `handover/SKILL.md` — add JOURNAL.md prompt to wrap checklist
- `.claude-plugin/marketplace.json` — add epic-start, epic-close
- `tests/test_mockup_chaining.py` — add epic-start, epic-close to ALL_SKILLS and CHAINING_TRUTH
- `scripts/generate_web_app_data.py` — add epic-start, epic-close
- `scripts/validation/validate_web_app.py` — add epic-start, epic-close
- `CLAUDE.md` — add epic-start, epic-close to Key Skills
- `README.md` — add epic-start, epic-close to skill listing

---

## Task 1: Update `java-update-design` for JOURNAL.md

**Files:**
- Modify: `java-update-design/SKILL.md`

- [ ] **Step 1: Read the current skill**

```bash
cat java-update-design/SKILL.md
```

- [ ] **Step 2: Replace the "Hardcoded Primary Document" line**

Find:
```
- Hardcoded Primary Document: `design/DESIGN.md`
```

Replace with:
```
- Hardcoded Primary Document: `design/JOURNAL.md` (the epic design journal — not the project DESIGN.md)
```

- [ ] **Step 3: Replace Step 1 (Locate DESIGN.md) with Step 1 (Locate JOURNAL.md)**

Find the step that reads `design/DESIGN.md` and does discovery. Replace the locate/read step with:

```markdown
### Step 1: Locate or create JOURNAL.md

```bash
ls design/JOURNAL.md 2>/dev/null || echo "not found"
```

- If found → proceed; this is the design journal for the current epic.
- If not found → this session is not on an epic branch, or epic-start was not run.
  Prompt: "No design/JOURNAL.md found. Create one? (y/n)"
  If yes:
  ```bash
  mkdir -p design
  echo "# Design Journal — $(git branch --show-current)" > design/JOURNAL.md
  ```
  If no → skip design documentation this session.

Read `design/JOURNAL.md` to understand which sections have already been journalled
during this epic before adding a new entry.
```

- [ ] **Step 4: Replace the "write/update DESIGN.md" step with a "write journal entry" step**

Find the step where the skill writes updated sections to `design/DESIGN.md`. Replace with:

```markdown
### Step N: Write or update journal entry

For each section affected by the committed changes, add or update an entry
in `design/JOURNAL.md`.

**Entry format:**
```markdown
### YYYY-MM-DD · §SectionName · ADR-N (optional)

[Prose narrative: what changed in this section, why, what decision was made.
Focus on reasoning and context — not implementation details. 2-6 sentences.]
```

**Rules:**
- Use the exact section name from the project `DESIGN.md` in the `§` anchor
  (e.g. `§Architecture`, `§Data Model`) — this is the merge map at epic close
- If an entry for this `§Section` already exists in `JOURNAL.md` → update it
  in place (the journal is a living document; git history preserves the evolution)
- If this is a new section affected → append a new entry at the end
- If the change generated an ADR → include it in the header: `· ADR-0042`
- Do not summarise the code change — explain the *design reasoning*

**Example:**
```markdown
### 2026-04-15 · §Architecture · ADR-0042

We moved to an event-driven model: order service emits `OrderPlaced`, payment
service listens and responds. The synchronous REST approach created coupling
between services that complicated retry logic and made failure semantics
ambiguous at the API boundary.
```
```

- [ ] **Step 5: Remove the `validate_document.py` call on `design/DESIGN.md`**

Find:
```bash
python scripts/validate_document.py design/DESIGN.md
```

Replace with:
```bash
python scripts/validate_all.py --tier commit
```

(JOURNAL.md does not need document-level validation — it is a narrative, not a structured reference doc.)

- [ ] **Step 6: Update the "Epic close" note**

Find the note about epic close and merging `design/DESIGN.md`. Replace with:

```markdown
**Epic close:** When the epic completes, `epic-close` reads `design/JOURNAL.md`,
generates a three-way merge preview (base + current project + journal), and
applies the changes to the project `DESIGN.md` with user confirmation.
The journal itself is posted to the GitHub epic issue, then discarded.
```

- [ ] **Step 7: Update "Common Pitfalls" table**

Add row:
```
| Writing to design/DESIGN.md directly | Bypasses the journal; merge at epic close loses context | Always write to design/JOURNAL.md with §Section anchors |
```

- [ ] **Step 8: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add java-update-design/SKILL.md
git commit -m "feat(java-update-design): write to design/JOURNAL.md with structured entry format"
```

---

## Task 2: Update `update-primary-doc` for JOURNAL.md

**Files:**
- Modify: `update-primary-doc/SKILL.md`

- [ ] **Step 1: Read the current skill**

```bash
cat update-primary-doc/SKILL.md
```

- [ ] **Step 2: Update primary doc target**

Find all references to the primary document write target (the doc path defined
in CLAUDE.md Sync Rules). Add a note:

```markdown
**In workspace mode:** When a `design/JOURNAL.md` exists in CWD (i.e. Claude is
operating on an epic branch with a workspace), write to `design/JOURNAL.md` using
the journal entry format instead of syncing to the primary doc directly. The
primary doc is updated at epic close via `epic-close`.

Detect workspace mode:
```bash
ls design/JOURNAL.md 2>/dev/null && echo "workspace-mode" || echo "direct-mode"
```

In direct mode: proceed with existing Sync Rules workflow (unchanged).
In workspace mode: write a journal entry per the java-update-design entry format,
using the §Section name matching the primary doc section affected.
```

- [ ] **Step 3: Run validators and commit**

```bash
python3 scripts/validate_all.py --tier commit
git add update-primary-doc/SKILL.md
git commit -m "feat(update-primary-doc): write to design/JOURNAL.md in workspace mode"
```

---

## Task 3: Update `handover` wrap checklist

**Files:**
- Modify: `handover/SKILL.md`

- [ ] **Step 1: Find the wrap checklist in SKILL.md**

```bash
grep -n "write-blog\|design-snapshot\|update-claude-md\|forage" handover/SKILL.md | head -10
```

- [ ] **Step 2: Add JOURNAL.md prompt to Step 0**

In the wrap checklist display, add a new item (default OFF — only relevant on epic branches):

```markdown
[ ] 5  journal-entry    document any design changes this session not yet in design/JOURNAL.md
```

Add to the checklist rules:

```markdown
- **journal-entry is off by default** — only tick if `design/JOURNAL.md` exists
  (i.e. Claude is on an epic branch). If it exists and there were design decisions
  this session not yet journalled, tick it and write the entry before the handover.
```

In the "Run checked items in this order" list, add:
```
5. journal-entry — write any missing JOURNAL.md entries before the handover
```

- [ ] **Step 3: Run validators and commit**

```bash
python3 scripts/validate_all.py --tier commit
git add handover/SKILL.md
git commit -m "feat(handover): add JOURNAL.md entry prompt to wrap checklist"
```

---

## Task 4: Create `epic-start` skill

**Files:**
- Create: `epic-start/SKILL.md`
- Create: `epic-start/commands/epic-start.md`

- [ ] **Step 1: Create `epic-start/SKILL.md`**

```markdown
---
name: epic-start
description: >
  Use when starting a new epic — user says "start epic", "begin epic",
  "create epic branch", or invokes /epic-start. Creates matching project and
  workspace branches, scaffolds design/JOURNAL.md and design/.meta with the
  project HEAD SHA, optionally links or creates a GitHub issue, and optionally
  invokes brainstorming. NOT for day-to-day work — one-time per epic.
---

# Epic Start

Creates the branch infrastructure and workspace scaffolding for a new epic.
Run once at the start of each epic. Requires CWD to be the workspace.

---

## Workflow

### Step 1 — Get epic name

Ask: "What's the epic name? (e.g. `epic-payments`)"

Rules:
- Lowercase with hyphens
- Prefix with `epic-` (e.g. `epic-payments`, `epic-auth-redesign`)

Read the project path from workspace CLAUDE.md `## Session Start` → `add-dir` line.

### Step 2 — Create branches

```bash
# Create project branch
git -C <project-path> checkout -b <epic-name>

# Create workspace branch
git checkout -b <epic-name>
```

Confirm both commands succeeded before continuing. If either fails (branch
already exists, uncommitted changes), report the error and stop — do not
proceed with a partial setup.

### Step 3 — Scaffold workspace

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

### Step 4 — GitHub issue

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

### Step 5 — Commit workspace scaffold

```bash
git add design/JOURNAL.md design/.meta
git commit -m "init(<epic-name>): scaffold workspace branch"
```

### Step 6 — Offer brainstorming

Prompt: "Start a brainstorm for this epic? (y/n)"

- Yes → invoke `brainstorming` skill
- No → done

---

## Success Criteria

- [ ] Project branch `<epic-name>` created
- [ ] Workspace branch `<epic-name>` created
- [ ] `design/JOURNAL.md` exists with stub header
- [ ] `design/.meta` exists with epic name, project SHA, date
- [ ] `design/.meta` `issue:` field populated (if tracking enabled and issue found/created)
- [ ] Workspace scaffold committed

---

## Skill Chaining

**Invoked by:** User directly at epic start via `/epic-start`

**Invokes:** [`brainstorming`] — if user accepts the prompt in Step 6

**Chains to:** [`epic-close`] — at the end of the epic
```

- [ ] **Step 2: Create `epic-start/commands/epic-start.md`**

```markdown
---
description: Start a new epic — creates project and workspace branches, scaffolds design/JOURNAL.md with SHA baseline, optionally links a GitHub issue, and optionally invokes brainstorming
---

Invoke the `epic-start` skill to begin a new epic.
```

- [ ] **Step 3: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add epic-start/
git commit -m "feat(epic-start): add epic branch lifecycle start skill"
```

---

## Task 5: Create `epic-close` skill

**Files:**
- Create: `epic-close/SKILL.md`
- Create: `epic-close/commands/epic-close.md`

- [ ] **Step 1: Create `epic-close/SKILL.md`**

```markdown
---
name: epic-close
description: >
  Use when closing an epic — user says "close epic", "finish epic", "wrap up
  epic", or invokes /epic-close. Presents a full close plan showing artifact
  routing, journal merge preview, and GitHub posting. User approves all at once
  or goes step by step. Routes artifacts per workspace CLAUDE.md ## Routing
  config, merges design/JOURNAL.md into project DESIGN.md, posts specs to
  GitHub issue, and handles branch cleanup.
---

# Epic Close

Closes the current epic: routes artifacts to declared destinations, merges
the design journal into the project DESIGN.md, posts specs to the GitHub
issue, and handles branch cleanup.

Requires CWD to be the workspace and `design/.meta` to exist (created by
`epic-start`).

---

## Workflow

### Step 1 — Read .meta and routing config

```bash
cat design/.meta
```

Extract: `epic`, `project-sha`, `issue` (may be empty).

Read workspace CLAUDE.md `## Routing` section. If absent, all artifacts
default to project repo.

Read project path from workspace CLAUDE.md `## Session Start` → `add-dir` line.
Read GitHub repo from workspace CLAUDE.md `## Work Tracking` → `GitHub repo:` line.

### Step 2 — Inventory artifacts

```bash
ls adr/ 2>/dev/null | grep -v INDEX.md      # ADRs
ls blog/ 2>/dev/null | grep -v INDEX.md     # Blog entries
ls snapshots/ 2>/dev/null | grep -v INDEX.md  # Snapshots
ls specs/ 2>/dev/null                        # Specs (user selects)
cat design/JOURNAL.md 2>/dev/null            # Journal
```

### Step 3 — Generate journal merge preview

Retrieve baseline project DESIGN.md at the recorded SHA:

```bash
git -C <project-path> show <project-sha>:DESIGN.md 2>/dev/null || echo "(no DESIGN.md at baseline)"
```

Read current `<project-path>/DESIGN.md` (may have evolved on main since epic start).

Read `design/JOURNAL.md` — extract all `§Section` anchors from entry headers
(lines matching `^### .* · §`).

For each anchored section, note: what the baseline had, what the current project
has, what the journal says. This forms the merge preview.

If `design/JOURNAL.md` has no entries → skip journal merge in the plan.

### Step 4 — Ask user to select specs

Present list of files in `specs/`:

```
Select specs to post to GitHub issue #<N>:
  1. 2026-04-13-design-journal-design.md
  2. 2026-04-13-artifact-routing-design.md
  3. (none)

Enter numbers (e.g. "1 2"), "all", or "none":
```

If no issue number in `.meta` or tracking disabled → skip this prompt.

### Step 5 — Resolve destinations

For each artifact type with files present, determine destination:
- Read `## Routing` from CLAUDE.md (if present)
- Apply: `base` = base destination + artifact subdirectory; explicit path = use as-is; `project repo` or absent = project repo default

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

### Step 6 — Present close plan

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

Approve all, or go step by step? (all / step)
```

If any section is skipped (no journal entries, no specs, no issue), mark it
as `(skipped — nothing to do)` in the plan.

### Step 7a — "all" path

Execute in order. On any failure, continue and report at the end:

**Artifact promotion:**
For each artifact file and its resolved destination:
```bash
mkdir -p "<dest>"
cp "<file>" "<dest>/"

# if local-git or remote-git:
git -C "<dest>" add .
git -C "<dest>" commit -m "feat: promote <artifact-type> from <project> epic <epic-name>"

# if remote-git only:
git -C "<dest>" push
```

**Journal merge:**
For each `§Section` in the journal:
1. Read baseline: `git -C <project-path> show <project-sha>:DESIGN.md` — extract the `§Section` content from the baseline document
2. Read the same section from the current project `DESIGN.md` — note any changes made independently on main since epic start
3. Apply journal narrative to the current project section, incorporating any independent main-branch changes
4. Write the merged result back to `<project-path>/DESIGN.md` for that section
5. Commit: `git -C <project-path> commit -am "docs(<epic-name>): apply design journal"`

**Spec posting:**
For each selected spec:
```bash
SUMMARY=$(head -20 "<spec-file>" | grep -A5 "## Problem" | tail -5)
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
✅ Spec posted to #<N>
❌ Push failed — <dest> has no network. Run: git -C <dest> push
```

### Step 7b — "step" path

**Phase 1 — Artifact routing**

Show what will be promoted where. Prompt: "Promote artifacts? (y/n)"

If yes: execute promotion for all artifact types using the same logic as Step 7a.
Report results. Prompt: "Continue to journal merge? (y/n)"

**Phase 2 — Journal merge**

For each `§Section` in the journal, show:

```
§Architecture (journal — last updated 2026-04-15):
  We moved to an event-driven model because...

Current project §Architecture:
  [current section content]

Will update §Architecture with journal narrative,
preserving independent main-branch changes.
```

Prompt: "Apply journal merge? (y/n)"

If yes:
1. Apply all section updates to `<project-path>/DESIGN.md`
2. Post-merge verification: re-read each updated section, confirm it reflects
   the corresponding journal entry. If any section looks wrong, report it.
3. Commit:
   ```bash
   git -C <project-path> add DESIGN.md
   git -C <project-path> commit -m "docs(<epic-name>): apply design journal — <date>"
   ```

Prompt: "Continue to GitHub posting? (y/n)"

**Phase 3 — GitHub posting and cleanup**

Post each selected spec as a comment on the issue (same format as Step 7a).
Close the issue.
Prompt: "Continue to branch cleanup? (y/n)"

### Step 8 — Branch cleanup (both paths)

```
Delete epic branches?
  project: <project-path> branch <epic-name>
  workspace: branch <epic-name>

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

---

## Success Criteria

- [ ] All artifacts promoted to declared destinations (or failures reported with resolution commands)
- [ ] Journal merged into project `DESIGN.md`, user confirmed
- [ ] Post-merge verification: each `§Section` anchor confirmed in updated doc
- [ ] Selected spec(s) posted to GitHub issue
- [ ] GitHub issue closed (if tracking enabled)
- [ ] Branch cleanup resolved — both branches deleted or `EPIC-CLOSED.md` created
- [ ] Workspace and project both on `main`

---

## Skill Chaining

**Invoked by:** User directly at epic close via `/epic-close`

**Chains from:** [`epic-start`] — which created `design/.meta` and `design/JOURNAL.md`

**Reads:** [`java-update-design`] and [`update-primary-doc`] output in `design/JOURNAL.md`
```

- [ ] **Step 2: Create `epic-close/commands/epic-close.md`**

```markdown
---
description: Close the current epic — routes artifacts per routing config, merges design/JOURNAL.md into project DESIGN.md, posts specs to GitHub issue, handles branch cleanup. Presents full plan with approve-all or step-by-step option.
---

Invoke the `epic-close` skill to close the current epic.
```

- [ ] **Step 3: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add epic-close/
git commit -m "feat(epic-close): add epic branch lifecycle close skill"
```

---

## Task 6: Metadata and tooling

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `tests/test_mockup_chaining.py`
- Modify: `scripts/generate_web_app_data.py`
- Modify: `scripts/validation/validate_web_app.py`

- [ ] **Step 1: Add epic-start and epic-close to marketplace.json**

In `.claude-plugin/marketplace.json`, add to the plugins array:

```json
{
  "name": "epic-start",
  "source": "./epic-start",
  "description": "One-time setup per epic — creates project and workspace branches, scaffolds design/JOURNAL.md with SHA baseline, links or creates a GitHub issue, optionally invokes brainstorming",
  "version": "1.0.0-SNAPSHOT"
},
{
  "name": "epic-close",
  "source": "./epic-close",
  "description": "Close an epic — routes artifacts per routing config, merges design/JOURNAL.md into project DESIGN.md, posts specs to GitHub issue, handles branch cleanup with approve-all or step-by-step option",
  "version": "1.0.0-SNAPSHOT"
}
```

- [ ] **Step 2: Add to ALL_SKILLS and CHAINING_TRUTH in test file**

In `tests/test_mockup_chaining.py`, find the `ALL_SKILLS` set and add:
```python
'epic-start',
'epic-close',
```

Find `CHAINING_TRUTH` dict and add:
```python
'epic-start': {
    'chains_to': ['brainstorming'],
    'invoked_by': [],
    'builds_on': [],
    'extended_by': []
},
'epic-close': {
    'chains_to': [],
    'invoked_by': [],
    'builds_on': [],
    'extended_by': []
},
```

- [ ] **Step 3: Add to generate_web_app_data.py and validate_web_app.py**

In each file, find the `ALL_SKILLS` set (or equivalent list) and add:
```python
'epic-start',
'epic-close',
```

- [ ] **Step 4: Generate slash command files**

```bash
python3 scripts/generate_commands.py
```

Expected: generates `epic-start/commands/epic-start.md` and `epic-close/commands/epic-close.md`
(already created in Tasks 4 and 5 — verify the generated version matches).

- [ ] **Step 5: Run full test suite**

```bash
python3 -m pytest tests/ -v
```

Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/marketplace.json tests/test_mockup_chaining.py \
  scripts/generate_web_app_data.py scripts/validation/validate_web_app.py
git commit -m "chore: register epic-start and epic-close in marketplace and test fixtures"
```

---

## Task 7: Update CLAUDE.md and README.md

- [ ] **Step 1: Add epic-start and epic-close to CLAUDE.md Key Skills**

Under `## Key Skills`, find the **Workflow integrators** group and add:

```markdown
- `epic-start` — one-time per epic; creates project + workspace branches, scaffolds `design/JOURNAL.md` with SHA baseline, links or creates GitHub issue, optionally invokes brainstorming
- `epic-close` — closes an epic; routes artifacts per `## Routing` config, merges `design/JOURNAL.md` into project `DESIGN.md`, posts specs to GitHub issue, handles branch cleanup
```

- [ ] **Step 2: Add to README.md**

Find the skill listing section in README.md. Add epic-start and epic-close alongside workspace-init in the workspace/lifecycle group.

- [ ] **Step 3: Run validators and commit**

```bash
python3 scripts/validate_all.py --tier commit
git add CLAUDE.md README.md
git commit -m "docs: add epic-start and epic-close to Key Skills and README"
```

---

## Task 8: Sync and end-to-end verify

- [ ] **Step 1: Sync all skills**

```bash
python3 scripts/claude-skill sync-local --all -y
```

- [ ] **Step 2: Run full validation**

```bash
python3 scripts/validate_all.py --tier commit
python3 -m pytest tests/ -v
```

Expected: all pass

- [ ] **Step 3: Smoke test epic-start**

In a new Claude session (workspace CWD), invoke `/epic-start` with a test name
(e.g. `epic-test-lifecycle`). Verify:
- Project branch created
- Workspace branch created
- `design/JOURNAL.md` stub exists
- `design/.meta` contains epic name, SHA, date

- [ ] **Step 4: Smoke test java-update-design**

On the test epic branch, invoke `java-update-design` with a mock code change.
Verify:
- Entry written to `design/JOURNAL.md` with structured header `### date · §Section`
- Project `DESIGN.md` unchanged

- [ ] **Step 5: Smoke test epic-close (dry run)**

Invoke `/epic-close` on the test branch with no real artifacts. Verify:
- Close plan is presented
- "all / step" prompt appears
- "all" path reports `(skipped)` for empty sections
- Branch cleanup prompt appears

- [ ] **Step 6: Clean up test branch**

```bash
git -C <project-path> checkout main && git -C <project-path> branch -D epic-test-lifecycle
git checkout main && git branch -D epic-test-lifecycle
```
