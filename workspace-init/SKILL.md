---
name: workspace-init
description: >
  Use when explicitly creating a new companion workspace from scratch —
  user invokes /workspace-init or says "init workspace for [project]" or
  "create workspace for [project]". NOT for questions about workspaces, NOT
  for ongoing use, NOT for modifying existing workspaces. One-time setup only.
---

# Workspace Init

Creates a companion workspace at `~/claude/private/<project>/` or
`~/claude/public/<project>/`. If the project belongs to a family of
related projects, the workspace can be nested under a shared parent folder
(e.g. `~/claude/private/casehub/claudony/`). Run once per project, per machine.

After running, open Claude in the workspace — CLAUDE.md instructs Claude to
`add-dir` the project automatically at session start.

---

## Workflow

### Step 1 — Detect context (no questions yet)

Run all detection silently first. Do not ask the user anything in this step.

```bash
PROJECT_PATH=$(pwd)
PROJECT_NAME=$(basename "$PROJECT_PATH")
PROJECT_PARENT_DIR=$(dirname "$PROJECT_PATH")
INFERRED_PARENT=$(basename "$PROJECT_PARENT_DIR")

case "$PROJECT_NAME" in
  parent|bom|build|root|aggregator) MAVEN_STRUCTURAL_NAME=true ;;
esac

case "$INFERRED_PARENT" in
  src|projects|code|repos|dev|home|Users|claude|private|public|workspace|workspaces|".")
    INFERRED_PARENT="" ;;
esac

GITHUB_OWNER=$(git -C "$PROJECT_PATH" remote get-url origin 2>/dev/null | sed 's|.*github.com[:/]\([^/]*\)/.*|\1|')
```

### Step 1 — Input collection (single AskUserQuestion batch)

**Use a SINGLE `AskUserQuestion` tool call with all four questions below.**
This produces the step-wizard header UI (e.g. `☒ Name  ☒ Privacy  ☒ Tag  ☐ Position`).
Do NOT ask questions one at a time — that loses the wizard UI.

Also run the family detection bash (Step 1a) before this call so the family
grouping question can be included if a family is detected.

**The four questions to batch:**

**Q1 — Workspace name:**
- If `MAVEN_STRUCTURAL_NAME=true`: "This folder is named `<name>` — a Maven convention. Inferred workspace name: `<INFERRED_PARENT>`. Confirm or type a different name."
- Otherwise: "Workspace name: `<PROJECT_NAME>` — confirm or type a different name."
- Options: `<INFERRED_NAME>` (Recommended), Other

**Q2 — Privacy:**
- "Where should the workspace live?"
- Options: private, public

**Q3 — Workspace repo tag:**
- "Tag to distinguish workspace repos from project repos on GitHub (e.g. wsp-casehub vs casehub)."
- Options: wsp (Recommended), ws, wrk, Custom

**Q4 — Tag position:**
- "Prefix or postfix?"
- Options: prefix → wsp-casehub / wsp-casehub-work (Recommended), postfix → casehub-wsp / casehub-work-wsp

After collecting all four answers, set:
- `WORKSPACE_NAME` from Q1
- `PRIVACY_FLAG=--private` or `PRIVACY_FLAG=--public` from Q2 — use in ALL `gh repo create` calls
- `TAG` from Q3, position from Q4
- `REPO_NAME` pattern: prefix → `<TAG>-<family>` / `<TAG>-<family>-<child>`; postfix → `<family>-<TAG>` / `<family>-<child>-<TAG>`

Then run Step 1a (family detection) if not already done, then ask the second batch below.

### Step 1 — Second AskUserQuestion batch (family scope + GitHub URL)

**Use a second single `AskUserQuestion` call with these two questions.**

**Q5 — Family grouping** (only if family detected in Step 1a):
- Show the sibling list and ask scope.
- Options: All repos, Select repos, Just this one, Flat (no family grouping)

**Q6 — GitHub remote URL:**
- "GitHub remote URL for the workspace repo (optional). Suggested: `github.com/<GITHUB_OWNER>/<REPO_NAME>`"
- Options: Yes use suggested URL, Skip — add later, Custom URL

After Q6: if URL confirmed or provided, check whether the GitHub repo already exists:
```bash
gh repo view <owner>/<REPO_NAME> --json name,description 2>/dev/null && echo "exists" || echo "not found"
```
- Doesn't exist → create at Step 8
- Exists + workspace markers → offer to clone and reuse
- Exists + NOT workspace → offer delete+recreate or exit

### Step 1 — Third AskUserQuestion batch (CLAUDE.md handling per repo)

**Use a third single `AskUserQuestion` call for this question.**

**Q7 — CLAUDE.md handling:**

For each repo in scope, detect its CLAUDE.md status:
Check each repo individually with separate commands — no loop:
```bash
git -C /concrete/path/to/repo1 ls-files --error-unmatch CLAUDE.md 2>/dev/null && echo "committed" || echo "not committed"
git -C /concrete/path/to/repo2 ls-files --error-unmatch CLAUDE.md 2>/dev/null && echo "committed" || echo "not committed"
```

Present one question showing all repos and their status, asking for the handling
decision. The user can set one default for all, or override per repo:

> "How should existing CLAUDE.md files be handled?
>
> | Repo     | Status    | Default decision |
> |----------|-----------|-----------------|
> | engine   | committed | A — migrate to workspace + symlink back |
> | work     | committed | A — migrate to workspace + symlink back |
> | ledger   | untracked | C — symlink only |
> | qhorus   | missing   | init — create with /init first |
>
> A = migrate content to workspace CLAUDE.md, git rm from project, symlink back
> B = keep in project, workspace CLAUDE.md @includes it
> C = untracked — create workspace CLAUDE.md, symlink project→workspace
> init = missing — run /init to create, then treat as A or B
>
> Accept defaults, or specify overrides (e.g. 'engine=B, work=B, rest=A'):"

Record the decision per repo as `CLAUDE_MD_DECISION[repo]`. These decisions
are used during execution — no further confirmation needed per repo.

### Step 1a — Detect project family

Run immediately after Step 1 context detection. The detection already has
`PROJECT_PARENT_DIR` and `INFERRED_PARENT` from Step 1.

**Infer the potential parent name from the project path:**

```bash
# Already computed in Step 1:
# PROJECT_PARENT_DIR, INFERRED_PARENT
```

If `INFERRED_PARENT` is non-empty, run two checks in order:

**Check A — Existing family workspace folder:**

Use Python to list subdirectories — avoids `find -exec` and shell variable expansion:
```bash
python3 /tmp/ws_family_check.py
```

Write `/tmp/ws_family_check.py` with the Write tool before running:
```python
import os, sys
from pathlib import Path

family_path = Path.home() / "claude" / "<privacy>" / "<INFERRED_PARENT>"
project_parent = Path("<PROJECT_PARENT_DIR>")

# List existing child workspaces
if family_path.is_dir():
    members = sorted(d.name for d in family_path.iterdir() if d.is_dir())
    print("FAMILY_MEMBERS:", ", ".join(members) if members else "")
else:
    print("FAMILY_MEMBERS:")

# Find git repos in project parent without a workspace
missing = []
for d in sorted(project_parent.iterdir()):
    if d.is_dir() and (d / ".git").is_dir() and not (family_path / d.name).is_dir():
        missing.append(d.name)
print("MISSING:", ", ".join(missing) if missing else "")
```

Substitute concrete values for `<privacy>`, `<INFERRED_PARENT>`, and `<PROJECT_PARENT_DIR>` before writing.

Present:

> "Found an existing family workspace at `~/claude/<privacy>/<INFERRED_PARENT>/` containing: `<FAMILY_MEMBERS>`.
>
> Repos without a workspace yet: `<MISSING>` (or "all accounted for" if none)
>
> 1. **All missing** — create workspaces for all repos not yet set up
> 2. **Just this one** — add `<project>/` to the family
> 3. **Flat** — no family grouping"

If 1 → set `BATCH_REPOS=<MISSING repos>`, set `BASE=~/claude/<privacy>/<INFERRED_PARENT>/<project>`, run batch.
If 2 → set `BASE=~/claude/<privacy>/<INFERRED_PARENT>/<project>` and proceed to Step 1b.
If 3 → use flat path `BASE=~/claude/<privacy>/<project>` and proceed to Step 2.

**Check B — Sibling git repos in same parent directory (no existing family workspace):**

Only run Check B if Check A did not trigger (no existing family folder found).

List what's already cloned locally AND check GitHub for repos in the family that
haven't been cloned yet. The goal is always "clone missing peers" — whether that's
all of them or just a few.

Use separate commands — no shell variables or loops:
```bash
ls -d /concrete/project/parent/dir/*/
```
and:
```bash
gh repo list <GITHUB_OWNER> --json name --jq '.[].name' 2>/dev/null
```

Compute LOCAL_SIBLINGS, GITHUB_REPOS, UNCLONED, and their counts manually from the output — do not use shell variables or pipes between these commands.

If `$LOCAL_COUNT` is greater than 1 OR `$UNCLONED_COUNT` is greater than 0, present:

> "Found family `<INFERRED_PARENT>` in `<PROJECT_PARENT_DIR>`:
>
> **Already cloned locally:** `<LOCAL_SIBLINGS listed>`
> **On GitHub, not yet cloned:** `<UNCLONED listed>` (or "none" if all present)
>
> How would you like to set up workspaces?
>
> 1. **All** — clone any missing peers + create workspaces for the whole family
> 2. **Select** — choose which repos to include (cloning as needed)
> 3. **Just this one** — create only `<project>/`, nest it under the family folder
> 4. **Flat** — no family grouping, use `~/claude/<privacy>/<project>/`"

**If 1 (All):**
Clone each uncloned repo with a separate git clone command per repo — no loop:
```bash
git clone git@github.com:<GITHUB_OWNER>/<repo1>.git /concrete/project/parent/<repo1>
git clone git@github.com:<GITHUB_OWNER>/<repo2>.git /concrete/project/parent/<repo2>
```
Then set `BATCH_REPOS=<all local siblings including current project>`. Set `BASE=~/claude/<privacy>/<INFERRED_PARENT>/<project>`. Run Step 1b to create the family root, then run the full workspace-init workflow (Steps 2–10) for each repo in `BATCH_REPOS` **one repo at a time, in strict sequence**. Complete all steps (including Step 5 CLAUDE.md gate and Step 6 CLAUDE.md decision) for one repo before starting the next. Never parallelise across repos — each repo's CLAUDE.md decision must be individually confirmed. Skip any repo that already has a workspace.

**If 2 (Select):**
Show numbered list of siblings, user picks. Set `BATCH_REPOS=<selected + current project>`. Proceed as per option 1 for the selected set.

**If 3 (Just this one):**
Set `BASE=~/claude/<privacy>/<INFERRED_PARENT>/<project>` and proceed to Step 1b then Step 2.

**If 4 (Flat):**
Use flat path `BASE=~/claude/<privacy>/<project>` and proceed to Step 2.

**If neither check triggers:** proceed directly to Step 1.5 with `BASE=~/claude/<privacy>/<project>`.

### Step 1.5 — Show plan and confirm before executing anything

**This step always runs before any files are created, moved, or committed.**

Scan each repo in `BATCH_REPOS` (or just the current project if no batch) for
methodology artifacts using the Step 9 detection logic — but do NOT execute
anything yet. Build the full plan and present it to the user.

Present the plan in this format:

```
WORKSPACE INIT PLAN
══════════════════════════════════════════════════════════════════

FAMILY ROOT  ~/claude/<privacy>/<INFERRED_PARENT>/    (new git repo)
  CLAUDE.md      family workspace hub
  .gitignore     excludes child workspace dirs
  adr/  blog/  snapshots/  specs/  plans/

CHILD WORKSPACES  (one git repo each)
  ~/claude/<privacy>/<INFERRED_PARENT>/engine/
  ~/claude/<privacy>/<INFERRED_PARENT>/work/
  ~/claude/<privacy>/<INFERRED_PARENT>/ledger/
  ...

CLAUDE.md HANDLING  (decisions collected in Q7 — shown here for confirmation)
┌──────────┬───────────────┬──────────────────────────────────────────────┐
│ Repo     │ Status        │ Decision (from Q7)                            │
├──────────┼───────────────┼──────────────────────────────────────────────┤
│ engine   │ committed     │ A — migrate to workspace + symlink back       │
│ work     │ committed     │ A — migrate to workspace + symlink back       │
│ ledger   │ untracked     │ C — symlink project→workspace                 │
│ qhorus   │ missing       │ init — run /init first, then A               │
│ ...      │ ...           │ ...                                           │
└──────────┴───────────────┴──────────────────────────────────────────────┘
  These decisions were set in Q7. "adjust" can change any row before YES.

FILE MOVES  (copied to workspace, then git rm'd and committed in project)
┌──────────┬──────────────────────────────────┬──────────────────────────────┬────────┐
│ Repo     │ Source (project)                 │ Destination (workspace)      │ Files  │
├──────────┼──────────────────────────────────┼──────────────────────────────┼────────┤
│ work     │ HANDOFF.md                       │ work/HANDOFF.md              │ 1      │
│ work     │ blog/                            │ work/blog/                   │ 17     │
│ work     │ docs/superpowers/plans/          │ work/plans/                  │ 13     │
│ ledger   │ HANDOFF.md                       │ ledger/HANDOFF.md            │ 1      │
│ ledger   │ IDEAS.md                         │ ledger/IDEAS.md              │ 1      │
│ ledger   │ blog/                            │ ledger/blog/                 │ 20     │
│ ...      │ ...                              │ ...                          │ ...    │
└──────────┴──────────────────────────────────┴──────────────────────────────┴────────┘
  Each move: git rm in project → commit "chore: migrate methodology artifacts to workspace"

SESSION HISTORY MIGRATION
  ~/.claude/projects/<old-project-path>/ → ~/.claude/projects/<new-workspace-path>/
  (one migration per repo)

══════════════════════════════════════════════════════════════════
Total: <N> workspaces · <M> file moves · <K> git commits across <J> repos

Proceed with this plan? (YES / adjust / no)
```

- **YES** → execute per the decisions collected in Q7 and confirmed here.
  No additional per-repo confirmations during execution — all decisions
  were made in Q7.
- **adjust** → user edits any draft or changes any action. Re-show updated plan, ask again.
- **no** → abort, nothing written.

**Do not create any directories, move any files, run any git commands,
or create any GitHub repos (`gh repo create`) until the user confirms with YES.**
Nothing touches the filesystem or GitHub until the plan is approved.

**During execution: implement `CLAUDE_MD_DECISION[repo]` for each repo exactly
as recorded in Q7. Do not re-ask or re-confirm — decisions were made in Q7
and confirmed in the plan.**

### Step 1b — Create or update family workspace root

**Only runs when Step 1a resolved to a nested path (user said YES to family grouping).**

The family root `~/claude/<privacy>/<INFERRED_PARENT>/` is itself a workspace — opening
Claude there gives cross-repo context. It has its own CLAUDE.md distinct from the
per-repo child workspaces.

```bash
FAMILY_ROOT=~/claude/<privacy>/<INFERRED_PARENT>
FAMILY_CLAUDE="$FAMILY_ROOT/CLAUDE.md"
```

**If `FAMILY_CLAUDE` does not exist — create it:**

List sibling git repos using ls (concrete path, no variables):
```bash
ls -d /concrete/project/parent/dir/*/
```
Filter to those containing `.git/` manually from the output.

Draft the family CLAUDE.md and show to user for acceptance before writing:

```
# <INFERRED_PARENT> Family Workspace

**Workspace type:** <private|public>

## Member Repos

| Repo | Local path | Child workspace |
|------|-----------|-----------------|
| <project> | <project-path> | `<INFERRED_PARENT>/<project>/` |
<one row per sibling found, marking those without a child workspace as "—">

Note: repos without a child workspace can still be loaded with add-dir on demand.

## Session Start

Open Claude here for cross-repo work. Load the repos relevant to your session:
  add-dir <path-to-repo-1>
  add-dir <path-to-repo-2>

## Shared Artifacts

Family-level artifacts (cross-repo ADRs, plans, design docs) accumulate here.
Per-repo artifacts live in each child workspace.

| Skill | Writes to |
|-------|-----------|
| adr | `adr/` |
| design-snapshot | `snapshots/` |
| write-content | `blog/` |
| handover | `HANDOFF.md` |
| idea-log | `IDEAS.md` |
```

Create the standard artifact directories at the family root too:
```bash
mkdir -p "$FAMILY_ROOT/adr" "$FAMILY_ROOT/snapshots" "$FAMILY_ROOT/blog" "$FAMILY_ROOT/specs" "$FAMILY_ROOT/plans"
```

Write the family root `.gitignore` — ignores all child workspace directories so
the family repo tracks only family-level artifacts, not the nested repos:

Write `.gitignore` using the Write tool with the concrete sibling names derived from the ls output above — no shell variables or heredoc expansion:

```
# Child workspace repos — each has its own git history
/<sibling1>
/<sibling2>
/<sibling3>

# OS / editor noise
.DS_Store
*.swp
```

This prevents git from seeing child workspace directories as untracked content
or accidentally registering them as submodules. Each child repo commits to its
own history independently.

**If `FAMILY_CLAUDE` already exists — update the member repos table:**

Add the new repo to the table if not already listed. Show the proposed change and
ask for acceptance before writing. Never overwrite the whole file — only update the
member repos table row.

### Step 2 — Create directory structure

```bash
# BASE is set in Step 1a (flat or nested under parent)
mkdir -p "$BASE/snapshots" "$BASE/adr" "$BASE/blog" "$BASE/specs" "$BASE/plans" "$BASE/design"
```

### Step 3 — Create INDEX.md in multi-file folders

```bash
cat > "$BASE/snapshots/INDEX.md" << 'EOF'
# Snapshots Index

| File | Date | Topic |
|------|------|-------|
EOF

cat > "$BASE/adr/INDEX.md" << 'EOF'
# ADR Index

| ID | Title | Status | Date |
|----|-------|--------|------|
EOF

cat > "$BASE/blog/INDEX.md" << 'EOF'
# Blog Index

| File | Date | Title |
|------|------|-------|
EOF
```

(`specs/`, `plans/`, and `design/` need no INDEX.md — superpowers and design skills manage them directly.)

The `design/` directory is intentionally left empty at workspace init. `work-start`
creates `design/JOURNAL.md` and `design/.meta` when a work branch begins.

### Step 4 — Create HANDOFF.md and IDEAS.md stubs

```bash
cat > "$BASE/HANDOFF.md" << 'EOF'
# Handoff

No sessions yet.
EOF

cat > "$BASE/IDEAS.md" << 'EOF'
# Idea Log

Undecided possibilities — things worth remembering but not yet decided.
Promote to an ADR when ready to decide; discard when no longer relevant.
EOF
```

### Step 5 — Create workspace CLAUDE.md (routing hub)

Write the workspace CLAUDE.md using the exact content approved in Step 1.5.
Do not re-draft or ask again — the content was shown and approved in the plan.
The only exception: if the user said "init" for this repo (no CLAUDE.md existed),
run /init now to create the project CLAUDE.md, then write the workspace CLAUDE.md
incorporating the newly created content.

Draft:

```
# <project> Workspace

**Name:** <project>
**Project repo:** <absolute-path-to-project>
**Workspace type:** <private|public>

## Session Start

Run `add-dir <absolute-path-to-project>` and `add-dir <absolute-path-to-workspace>` before any other work.

## Artifact Locations

| Skill | Writes to |
|-------|-----------|
| brainstorming (specs) | `specs/` |
| writing-plans (plans) | `plans/` |
| handover | `HANDOFF.md` |
| idea-log | `IDEAS.md` |
| design-snapshot | `snapshots/` |
| java-update-design / update-primary-doc | `design/JOURNAL.md` (created by `work-start`) |
| adr | `adr/` |
| write-content | `blog/` |

## Structure

- `HANDOFF.md` — session handover (single file, overwritten each session)
- `IDEAS.md` — idea log (single file)
- `specs/` — brainstorming / design specs (superpowers output)
- `plans/` — implementation plans (superpowers output)
- `snapshots/` — design snapshots with INDEX.md (auto-pruned, max 10)
- `adr/` — architecture decision records with INDEX.md
- `blog/` — project diary entries with INDEX.md

## Git Discipline

Two git repositories are active in every session:
- **Workspace** (`<absolute-path-to-workspace>`) — plans, blog (staging), snapshots, handover
- **Project repo** (`<absolute-path-to-project>`) — source code, ADRs (`docs/adr/`), specs

Never rely on CWD for git operations — the session may have started in either repo. Always use explicit paths:
```bash
git -C <absolute-path-to-workspace> add <file>    # workspace artifacts
git -C <absolute-path-to-project> add <file>      # project artifacts
```
The file path determines the repo: if the file lives under the workspace path, use the workspace; if under the project path, use the project.

## Rules

- All methodology artifacts go here, not in the project repo
- Promotion to project repo is always explicit — never automatic
- Workspace branches mirror project branches — switch both together

## Routing

Per-artifact routing destinations (optional). If absent, all artifacts route to the project repo.

| Artifact   | Destination | Notes |
|------------|-------------|-------|
| adr        | project     | lands in `docs/adr/` — promoted at work end |
| specs      | project     | lands in `docs/specs/` — promoted at work end |
| blog       | workspace   | staged here; published to mdproctor.github.io via publish-blog at work end |
| plans      | workspace   | stay in workspace permanently |
| design     | workspace   | epic journal stays in workspace |
| snapshots  | workspace   | stay in workspace permanently |
| handover   | workspace   | |

**Blog directory:** `<absolute-path-to-workspace>/blog/`

Valid destinations: `project` · `workspace` · `mdproctor.github.io` · `alternative ~/path/to/repo/`

`mdproctor.github.io` — blog publishing destination, resolved via `~/.claude/blog-routing.yaml`.

To set a global default across all workspaces, add to `~/.claude/CLAUDE.md`:
\`\`\`markdown
## Routing
**Default destination:** workspace
\`\`\`
Global valid values: `workspace` or `project` only (no alternative at global level).
```

> **Note:** `work-start` reads the routing config at branch creation time. If `design → workspace`,
> it records the workspace/main HEAD SHA as the design baseline instead of the project HEAD SHA.
> Configure routing before starting your first work branch.

Present to the user:
> "Here is the proposed workspace CLAUDE.md. Accept, or tell me what to change:
> (YES / edit)"

Apply the accepted or tailored version. Only write the file once confirmed.

### Step 5b — Offer optional CLAUDE.md additions

After the base CLAUDE.md is confirmed, offer each optional addition
individually. Show the proposed content, ask for acceptance or tailoring.
Never add anything without confirmation.

**Option 1 — Proactive handover on context pressure:**

> "Add proactive handover suggestion? When the conversation gets long, Claude
> will suggest writing a handover before context is lost.
>
> Proposed addition to workspace CLAUDE.md:
> ```
> ## Context Management
>
> If the conversation is getting very long or you notice context pressure,
> proactively suggest writing a handover before continuing.
> ```
> (YES / no / edit)"

If accepted (or tailored), append to workspace CLAUDE.md.

**Pattern for future options:** add new options here following the same
show-and-confirm pattern. Each option is independent — accepting one does
not imply accepting others.

### Step 6 — Handle CLAUDE.md in project

**This step has three distinct cases. Identify which applies and handle it —
do not skip or collapse this step.**

If the project directory does not exist yet, skip this step and tell the user:
> "Symlink skipped — project directory doesn't exist yet. Re-run
> `/workspace-init` after creating the project to add the symlink."

Otherwise, run two checks:

```bash
# Check 1: does CLAUDE.md exist at all?
[ -f "<project-path>/CLAUDE.md" ] && echo "exists" || echo "missing"

# Check 2: if it exists, is it committed?
git -C "<project-path>" ls-files --error-unmatch CLAUDE.md 2>/dev/null && echo "committed" || echo "not committed"
```

---

**CASE 1 — CLAUDE.md does not exist in the project**

The project has no CLAUDE.md. It must be initialised before a placement
decision can be made.

Tell the user:
> "No CLAUDE.md found in `<project-path>`. It needs to be created first.
> Run `/init` in the project directory to initialise it, then re-run
> `/workspace-init` to complete the setup — or reply **init** now and
> I will invoke `/init` for you before continuing."

If user replies **init**: invoke the `init` skill for the project, wait for
it to create CLAUDE.md, then continue to Case 2 or 3 as appropriate.

---

**CASE 2 — CLAUDE.md exists and is committed to git**

This is the main decision. Present both options — **this question must be
asked and answered before proceeding**:

> "CLAUDE.md is committed to git (`<size>` bytes). Where should it live?
>
> **A — Migrate to workspace** *(recommended)*
>    Content moves to workspace CLAUDE.md. Removed from project with `git rm`.
>    Symlink created: `project/CLAUDE.md → workspace/CLAUDE.md`
>    Opening Claude anywhere loads the same config.
>
> **B — Keep in project repo**
>    CLAUDE.md stays committed in the project. Workspace CLAUDE.md gets
>    `@<project-path>/CLAUDE.md` so both locations load the full config.
>
> Reply **A** or **B** — this cannot be skipped:"

**If A (migrate to workspace):**
```bash
# Append project CLAUDE.md content to workspace CLAUDE.md
echo -e "\n---\n" >> "$BASE/CLAUDE.md"
cat "<project-path>/CLAUDE.md" >> "$BASE/CLAUDE.md"

# Remove from project and commit
git -C "<project-path>" rm CLAUDE.md
git -C "<project-path>" commit -m "chore: migrate CLAUDE.md to workspace"

# Create symlink so opening Claude in the project still loads full config
ln -sf "$BASE/CLAUDE.md" "<project-path>/CLAUDE.md"
echo "CLAUDE.md" >> "<project-path>/.git/info/exclude"
```

**If B (keep in project repo):**
```bash
# Add @include of the project CLAUDE.md to the workspace CLAUDE.md
echo "" >> "$BASE/CLAUDE.md"
echo "@<project-path>/CLAUDE.md" >> "$BASE/CLAUDE.md"
```
Tell the user:
> "CLAUDE.md stays in the project repo. The workspace CLAUDE.md now includes
> it via `@<project-path>/CLAUDE.md` — opening Claude in either location
> loads the full config."

---

**CASE 3 — CLAUDE.md exists but is not committed (untracked)**

Create the symlink pointing to the workspace CLAUDE.md so config is shared,
and exclude the symlink from git tracking:
```bash
ln -sf "$BASE/CLAUDE.md" "<project-path>/CLAUDE.md"
echo "CLAUDE.md" >> "<project-path>/.git/info/exclude"
```

### Step 6b — Write Project Artifacts to project CLAUDE.md

After CLAUDE.md handling (Step 6) is complete, add a `## Project Artifacts` section
to the **project** CLAUDE.md if it doesn't already have one. This section tells
skills like git-squash which paths are project content (not workspace noise), so they
never filter or drop commits that touch those paths.

**Check first:**
```bash
grep -q "^## Project Artifacts" "<project-path>/CLAUDE.md" 2>/dev/null && echo "exists" || echo "missing"
```

If already present → skip this step silently.

**If missing, derive the table from what's staying in the project:**

Start with standard project-knowledge paths:
- `CLAUDE.md` — project conventions (build commands, test patterns, naming)
- `docs/adr/` — architecture decision records (always project knowledge)

**Create DESIGN.md stub if missing (java / typescript / python projects only):**

Read the project type from CLAUDE.md:
```bash
grep -E "^\*\*Type:\*\*|^type:" "<project-path>/CLAUDE.md" 2>/dev/null | head -1
```

If type is `java`, `typescript`, or `python` AND `docs/DESIGN.md` does not exist:

```bash
mkdir -p "<project-path>/docs"
```

Write a minimal stub suited to the project type. For **java**:

```markdown
# [Repo Name] — Design

## Architecture

_To be documented._

## Module Structure

| Module | Type | Purpose |
|--------|------|---------|
| _(add modules)_ | | |

## Key Abstractions

_To be documented._

## SPI Contracts

_To be documented._

## Data Model

_To be documented._

## Configuration

_To be documented._
```

For **typescript** or **python**:

```markdown
# [Repo Name] — Design

## Architecture

_To be documented._

## Module Structure

_To be documented._

## Key Abstractions

_To be documented._

## Data Flow

_To be documented._

## Configuration

_To be documented._
```

Replace `[Repo Name]` with the actual repo name (read from the project directory name or CLAUDE.md).

Commit the stub to the project repo:
```bash
git -C "<project-path>" add docs/DESIGN.md
git -C "<project-path>" commit -m "chore: add DESIGN.md stub"
```

Do not create DESIGN.md for `custom`, `blog`, or `skills` project types — those are either self-documenting (skills) or use a different primary doc structure (custom/blog).

**Then detect additional project-knowledge paths:**
```bash
# Check for common project docs
[ -f "<project-path>/docs/DESIGN.md" ]     && echo "docs/DESIGN.md"
[ -d "<project-path>/docs/specs/" ]         && echo "docs/specs/"
[ -f "<project-path>/docs/RESEARCH.md" ]   && echo "docs/RESEARCH.md"
[ -f "<project-path>/docs/CAPABILITIES.md" ] && echo "docs/CAPABILITIES.md"
```

**What NOT to include** (these route to workspace or are workspace noise):
- `HANDOFF.md` — session handovers → workspace
- `blog/` or `docs/_posts/` — blog entries → workspace or external
- `plans/`, `snapshots/` — methodology artifacts → workspace

**Check blog-routing.yaml** (at project, workspace, or `~/.claude/` level). If any
level has external routing for blog entries, blogs are external and must not appear
in Project Artifacts:
```bash
find "<project-path>" -maxdepth 2 -name "blog-routing.yaml" 2>/dev/null
cat ~/.claude/blog-routing.yaml 2>/dev/null
```

**Write the section** to the project CLAUDE.md, placed before `## Work Tracking`
(or at the end if Work Tracking is absent):

```markdown
## Project Artifacts

Paths that are project content (not workspace noise). Skills use this to avoid
filtering or dropping commits that touch these paths.

| Path | What it is |
|------|------------|
| `CLAUDE.md` | Project conventions (build, test, naming) |
| `docs/adr/` | Architecture decision records |
| `docs/DESIGN.md` | Design document |
```

Do not show this section to the user or ask for confirmation — it is derived
mechanically from what was already decided in Steps 6 and 9. If the user wants
to customise it later, they can edit the section directly.

### Step 7 — Create .gitignore for workspace

```bash
cat > "$BASE/.gitignore" << 'EOF'
.DS_Store
proj
EOF
```

### Step 7b — Create bidirectional navigation symlinks

Create a `proj` symlink in the workspace pointing to the project, and a `wksp`
symlink in the project pointing to the workspace. These let you `cd proj` or
`cd wksp` to jump between the two without remembering the full path.

```bash
# workspace/proj → project directory
ln -sf "<project-path>" "$BASE/proj"

# project/wksp → workspace directory
ln -sf "$BASE" "<project-path>/wksp"
```

Add `wksp` to the project `.gitignore` so the symlink is never accidentally
staged. Use the committed `.gitignore`, not `.git/info/exclude`, so the
convention is visible to anyone working on the repo:

```bash
# Add wksp to project .gitignore (append if not already present)
grep -q "^wksp$" "<project-path>/.gitignore" 2>/dev/null || echo "wksp" >> "<project-path>/.gitignore"

# Stage and commit .gitignore update
git -C "<project-path>" add .gitignore
git -C "<project-path>" diff --cached --quiet || git -C "<project-path>" commit -m "chore: ignore wksp symlink"
```

`proj` is already covered by the workspace `.gitignore` written in Step 7.
Neither symlink is tracked by git in either repo.

### Step 7c — Install git hooks in project repo

Check which hooks are available and offer to install them into `.githooks/`
(committed, survives clones). Both hooks go in a single commit if both are installed.

```bash
GITHOOKS_DIR="<project-path>/.githooks"
PREPUSH_SRC="$HOME/.claude/skills/git-squash/hooks/pre-push"
COMMITMSG_SRC="$HOME/.claude/skills/issue-workflow/hooks/commit-msg"

HAS_PREPUSH=false
HAS_COMMITMSG=false
[ -f "$PREPUSH_SRC" ] && [ ! -f "$GITHOOKS_DIR/pre-push" ]   && HAS_PREPUSH=true
[ -f "$COMMITMSG_SRC" ] && [ ! -f "$GITHOOKS_DIR/commit-msg" ] && HAS_COMMITMSG=true

# Also check if Work Tracking is enabled for commit-msg
WORK_TRACKING=$(grep -q "Issue tracking.*enabled" "<project-path>/CLAUDE.md" 2>/dev/null && echo yes || echo no)
[ "$WORK_TRACKING" = "no" ] && HAS_COMMITMSG=false
```

**If both `$HAS_PREPUSH` and `$HAS_COMMITMSG` are false** → skip silently (nothing to install or already present).

**Otherwise**, offer:

> "Install git hooks into `.githooks/` (committed to repo)?
>
> `pre-push` — squash candidate detection (git-squash) `[available / already installed / skill missing]`
> `commit-msg` — require issue ref on every commit (issue-workflow) `[available / already installed / skill missing / Work Tracking not enabled]`
>
> Both are committed so all clones get them. `core.hooksPath` activated on this machine. (YES / n)"

If YES:
```bash
mkdir -p "$GITHOOKS_DIR"

if $HAS_PREPUSH; then
  cp "$PREPUSH_SRC" "$GITHOOKS_DIR/pre-push"
  chmod +x "$GITHOOKS_DIR/pre-push"
  git -C "<project-path>" add .githooks/pre-push
fi

if $HAS_COMMITMSG; then
  cp "$COMMITMSG_SRC" "$GITHOOKS_DIR/commit-msg"
  chmod +x "$GITHOOKS_DIR/commit-msg"
  git -C "<project-path>" add .githooks/commit-msg
fi

git -C "<project-path>" config core.hooksPath .githooks
git -C "<project-path>" commit -m "chore: add git hooks — squash detection and issue ref enforcement"
```

> **New machine setup:** hook files ship in `.githooks/` but `core.hooksPath`
> must be set per machine: `git config core.hooksPath .githooks`

If n → skip. Do not ask again this session.

### Step 8 — Initialise git and push

```bash
cd "$BASE"
git init
git add .
git commit -m "init: workspace for <project>"
```

If the user provided a GitHub remote URL, create the repo and push:

```bash
gh repo create <owner>/<REPO_NAME> $PRIVACY_FLAG --description "Workspace for <workspace-name>" 2>/dev/null || true
git remote add origin git@github.com:<owner>/<REPO_NAME>.git
git push -u origin main
```

If no remote URL provided, tell the user:
> Remote not configured. When ready (using your chosen tag `<REPO_NAME>`):
> ```bash
> gh repo create <owner>/<REPO_NAME> $PRIVACY_FLAG
> git remote add origin git@github.com:<owner>/<REPO_NAME>.git
> git push -u origin main
> ```

### Step 9b — Migrate Claude session history and memory

Claude Code stores per-project conversation history and auto-memory keyed to
the working directory path. Without migration, opening Claude in the workspace
loses all previous sessions.

Derive the old and new project data paths from the directory paths:

```bash
OLD_KEY=$(echo "$PROJECT_PATH" | sed 's|^/||' | tr '/' '-')
NEW_KEY=$(echo "$BASE" | sed 's|^/||' | tr '/' '-')
OLD_DIR="$HOME/.claude/projects/$OLD_KEY"
NEW_DIR="$HOME/.claude/projects/$NEW_KEY"
```

If old data exists and new location is empty, migrate it:

```bash
if [ -d "$OLD_DIR" ] && [ ! -d "$NEW_DIR" ]; then
  mv "$OLD_DIR" "$NEW_DIR"
  echo "Migrated Claude session history and memory to workspace path."
elif [ ! -d "$OLD_DIR" ]; then
  echo "No existing Claude project data found — nothing to migrate."
elif [ -d "$NEW_DIR" ]; then
  echo "Workspace project data already exists at $NEW_DIR — skipping migration."
fi
```

This step runs unconditionally — session continuity is not optional.

### Step 9 — Detect and offer to migrate existing artifacts

Scan for existing methodology artifacts across the project:

```bash
FOUND=()
# Root-level handovers and ideas
[ -f "<project-path>/HANDOFF.md" ]  && git -C "<project-path>" ls-files --error-unmatch HANDOFF.md  2>/dev/null && FOUND+=("HANDOFF.md → HANDOFF.md")
[ -f "<project-path>/HANDOVER.md" ] && git -C "<project-path>" ls-files --error-unmatch HANDOVER.md 2>/dev/null && FOUND+=("HANDOVER.md → HANDOFF.md")
[ -f "<project-path>/IDEAS.md" ]    && git -C "<project-path>" ls-files --error-unmatch IDEAS.md    2>/dev/null && FOUND+=("IDEAS.md → IDEAS.md")

# Root-level artifact directories (common in repos that predate docs/ convention)
# Note: adr/ excluded — project knowledge, stays in repo.
# Note: specs/ excluded — design specs are project knowledge; they explain why the
#   code is shaped the way it is and are useful for future contributors. New specs
#   are written to the workspace during active work, then merged to the project repo
#   via work-end when the work ships.
[ -d "<project-path>/blog" ]        && FOUND+=("blog/ → blog/")
[ -d "<project-path>/plans" ]       && FOUND+=("plans/ → plans/")
[ -d "<project-path>/snapshots" ]   && FOUND+=("snapshots/ → snapshots/")

# docs/ artifacts
# Note: docs/adr/ and docs/specs/ excluded — both are project knowledge, not workspace artifacts.
[ -d "<project-path>/docs/design-snapshots" ]  && FOUND+=("docs/design-snapshots/ → snapshots/")
[ -d "<project-path>/docs/blog" ]              && FOUND+=("docs/blog/ → blog/")
[ -d "<project-path>/docs/_posts" ]            && FOUND+=("docs/_posts/ → blog/")
[ -d "<project-path>/docs/handoffs" ]          && FOUND+=("docs/handoffs/ → handoffs/")
[ -f "<project-path>/docs/ideas/IDEAS.md" ]    && FOUND+=("docs/ideas/IDEAS.md → IDEAS.md")
[ -d "<project-path>/docs/superpowers/plans" ] && FOUND+=("docs/superpowers/plans/ → plans/")

# Hidden directories
[ -d "<project-path>/.superpowers/brainstorm" ] && FOUND+=(".superpowers/brainstorm/ → specs/")
```

If any found, present the list and ask:
> "Found existing methodology artifacts:
> - [list items]
>
> Migrate them to the workspace? This will copy each to the workspace,
> remove it from the project repo with `git rm`, and commit the deletion.
> (YES / no / select)"

**Merge warning:** If both a root-level and a `docs/` location map to the same
workspace destination (e.g. `adr/` AND `docs/adr/` both → `adr/`), flag this
before copying:
> "⚠️ Both `adr/` and `docs/adr/` exist and both map to `adr/` in the workspace.
> Files with the same name will be overwritten by the second copy.
> Review for filename collisions before proceeding? (YES / no)"

Copy root-level first, then `docs/` so that `docs/` content takes precedence
in any collision. After copying, report any files that were overwritten.

If YES (or after selection is confirmed), for each item:
```bash
# 1. Copy to workspace (merges into destination dir)
cp -r "<project-path>/adr/." "$BASE/adr/"

# 2. Remove from project
git -C "<project-path>" rm -r adr

# ... repeat for each selected item, root-level before docs/
```

Then commit all removals in one go:
```bash
git -C "<project-path>" commit -m "chore: migrate methodology artifacts to workspace"
```

**Note on handovers:** If both `HANDOFF.md` and `HANDOVER.md` exist, use the
more recent file as `workspace/HANDOFF.md` and discard the older one.

### Step 10 — Confirm

> ✅ Workspace created at `~/claude/<privacy>/<project>/`
>
> **To start working:**
> 1. Open Claude in `~/claude/<privacy>/<project>/`
> 2. CLAUDE.md will instruct Claude to run `add-dir` on the project automatically
>
> **Navigation symlinks:**
> - In workspace: `proj/` → project directory (`cd proj` to jump to the project)
> - In project: `wksp/` → workspace directory (`cd wksp` to jump to the workspace)
>
> **CLAUDE.md:** workspace CLAUDE.md symlinks to the project's committed CLAUDE.md.
> Opening Claude in either location loads the same config.
>
> **Tip:** This skill is large and one-off. Run `/clear` now to free up context
> before starting real work.

### Step 10b — Offer issue tracking setup

Check if Work Tracking is already configured:

```bash
grep -q "Issue tracking.*enabled" CLAUDE.md 2>/dev/null && echo "configured" || echo "not configured"
```

If already configured → skip silently.

If not configured, ask:

> **Set up GitHub issue tracking? (YES / n)**
>
> Links all commits to GitHub issues automatically — clean release notes,
> enforced issue creation before coding starts, commit split detection.
>
> Default: **YES** — type **YES** to enable, type **n** to skip.

If YES → invoke the `issue-workflow` skill (Phase 0 runs automatically).
If n → skip. Do not ask again this session.

### Step 10c — Offer superpowers installation

Check if superpowers is already installed:

```bash
python3 -c "
import json, os
s = json.load(open(os.path.expanduser('~/.claude/settings.json')))
enabled = s.get('enabledPlugins', {})
print('installed' if 'superpowers@claude-plugins-official' in enabled else 'not installed')
"
```

If already installed → skip silently.

If not installed, ask:

> **Install superpowers? (YES / n)**
>
> Superpowers adds structured workflows for TDD, debugging, brainstorming,
> code review, and more — loaded automatically when relevant.
>
> Default: **YES** — type **YES** to install, type **n** to skip.

If YES:

> To install superpowers, run this slash command in Claude Code:
> ```
> /plugin install superpowers
> ```
> This installs from the official Claude Code plugin marketplace. Once installed,
> superpowers skills are available immediately — no restart needed.

If n → skip. Do not ask again this session.

---

## Success Criteria

- [ ] Project family detection ran (Step 1a): existing family folder checked, sibling repos checked
- [ ] `BASE` path is correct: flat (`~/claude/<privacy>/<project>/`) or nested (`~/claude/<privacy>/<parent>/<project>/`) per user choice
- [ ] Family root CLAUDE.md created or updated (Step 1b) if nested path chosen: member repos table includes new repo, artifact dirs exist at family root
- [ ] Family root `.gitignore` written with all sibling repo names — child workspaces excluded from family repo tracking
- [ ] Directory exists at correct path with all subdirs
- [ ] `CLAUDE.md` contains session-start `add-dir` instruction and artifact locations table
- [ ] `HANDOFF.md` and `IDEAS.md` exist as stubs
- [ ] `snapshots/INDEX.md`, `adr/INDEX.md`, `blog/INDEX.md` exist
- [ ] `specs/` and `plans/` directories exist
- [ ] `.gitignore` exists and includes `proj`
- [ ] `proj` symlink in workspace → project directory
- [ ] `wksp` symlink in project → workspace directory
- [ ] `wksp` added to project `.gitignore` (committed)
- [ ] CLAUDE.md handled: migrated (symlink + .git/info/exclude) or left committed per user choice
- [ ] `## Project Artifacts` section written to project CLAUDE.md (Step 6b): derived from project-knowledge paths; skipped if section already present
- [ ] Claude session history and memory migrated to workspace-keyed path (`~/.claude/projects/`)
- [ ] Existing methodology artifacts offered for migration; selected ones copied and `git rm`'d with single commit
- [ ] Git repo initialised with initial commit
- [ ] Remote set and pushed (if URL provided)
- [ ] Git hooks offered (Step 7c): `pre-push` (git-squash) and/or `commit-msg` (issue-workflow, if Work Tracking enabled) copied to `.githooks/`, committed in one commit, `core.hooksPath` set; skipped silently if skills absent or hooks already present
- [ ] Issue tracking offered; configured via `issue-workflow` Phase 0 if accepted
- [ ] Superpowers offered; install command shown if not already installed

---

## Skill Chaining

**Invoked by:** User directly at project setup time; session-start hook when
no workspace is detected

**Invokes (optional):** `issue-workflow` Phase 0 — if user accepts the offer in Step 10b; superpowers install command shown (user must run `/plugin install superpowers` manually) — if user accepts the offer in Step 10c
