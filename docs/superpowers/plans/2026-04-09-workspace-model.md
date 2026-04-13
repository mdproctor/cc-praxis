# Workspace Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move all methodology artifacts out of project repos into dedicated workspace directories. Claude opens in the workspace (CWD). Skills write to CWD-relative paths. A CLAUDE.md symlink in the project gives full config when someone opens there by mistake.

**Architecture:**
- CWD = workspace (`~/claude/private/<project>/` or `~/claude/public/<project>/`)
- Project accessible via `add-dir` — instructed automatically by workspace CLAUDE.md session-start
- CLAUDE.md in project = gitignored symlink → workspace CLAUDE.md (one source of truth)
- `.git/info/exclude` hides the symlink (never touches tracked `.gitignore`)
- `workspace-init` creates everything: dirs, routing CLAUDE.md, symlink, exclude entry, git init
- All skills (cc-praxis + superpowers + any third-party) write to CWD = workspace universally

**Tech Stack:** Markdown skills, bash, Python validators, pytest

---

## File Map

**Create:**
- `workspace-init/SKILL.md`
- `workspace-init/commands/workspace-init.md`

**Modify (path updates — remove `docs/` prefix):**
- `idea-log/SKILL.md` — `docs/ideas/IDEAS.md` → `IDEAS.md`
- `adr/SKILL.md` — `docs/adr/` → `adr/`
- `design-snapshot/SKILL.md` — `docs/design-snapshots/` → `snapshots/`, `docs/adr/` → `adr/`
- `write-blog/SKILL.md` — `docs/blog/` → `blog/` *(already updated for images — verify paths only)*
- `handover/SKILL.md` — `snapshots/`, `blog/`, `adr/` *(already updated — verify)*
- `handover/handover-reference.md` — `snapshots/`, `blog/`, `IDEAS.md` *(already updated — verify)*

**Modify (hook):**
- `~/.claude/hooks/check_project_setup.sh` — add HANDOVER.md prompt + workspace check

**Update (metadata):**
- `.claude-plugin/marketplace.json` — add `workspace-init`
- `tests/test_mockup_chaining.py` — add `workspace-init` to ALL_SKILLS and CHAINING_TRUTH
- `scripts/generate_web_app_data.py` — add `workspace-init`
- `scripts/validation/validate_web_app.py` — add `workspace-init`
- `CLAUDE.md` — add `workspace-init` to Key Skills section
- `README.md` — add `workspace-init` to skill listing

---

## Task 1: Create `workspace-init` skill

**Files:**
- Create: `workspace-init/SKILL.md`
- Create: `workspace-init/commands/workspace-init.md`

- [ ] **Step 1: Write `workspace-init/SKILL.md`**

```markdown
---
name: workspace-init
description: >
  Use when setting up a workspace for a project for the first time — user says
  "init workspace", "set up workspace", "create workspace for <project>", or
  invokes /workspace-init. Creates the workspace directory structure, routing
  CLAUDE.md, gitignored CLAUDE.md symlink in the project, and git repo.
  NOT for day-to-day workspace use — one-time setup per project per machine.
---

# Workspace Init

Creates a companion workspace at `~/claude/private/<project>/` or
`~/claude/public/<project>/`. Run once per project, per machine.

After running, open Claude in the workspace — CLAUDE.md instructs Claude to
`add-dir` the project automatically at session start.

---

## Workflow

### Step 1 — Gather inputs

Ask the user for:
1. **Project name** — workspace directory name (e.g. `cc-praxis`)
2. **Privacy** — `private` or `public`
3. **Absolute path to project** — where it lives or will live
4. **GitHub remote URL** for the workspace repo — optional; can add later

Check the project path state:

```bash
if [ -d "<project-path>" ]; then
  echo "Project directory exists"
  if [ -d "<project-path>/.git" ]; then
    echo "Git repo: yes"
  else
    echo "Git repo: no (fine — workspace-init does not require one)"
  fi
else
  echo "Project directory does not exist yet — recording intended path only"
fi
```

Confirm with the user before proceeding. The workspace can be created
regardless of whether the project directory or git repo exists.

### Step 2 — Create directory structure

```bash
BASE=~/claude/<privacy>/<project>
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

### Step 3b — Copy project DESIGN.md into workspace (if it exists)

```bash
if [ -f "<project-path>/DESIGN.md" ]; then
  cp "<project-path>/DESIGN.md" "$BASE/design/DESIGN.md"
  echo "Copied project DESIGN.md to workspace/design/DESIGN.md"
else
  cat > "$BASE/design/DESIGN.md" << 'EOF'
# Design

*Design document for this project. Updated during the epic; merged back to
the project at epic close. Git history records every change — no separate
delta files needed.*
EOF
  echo "Created design/DESIGN.md stub (project has no DESIGN.md yet)"
fi
```

### Step 4 — Create HANDOVER.md and IDEAS.md stubs

```bash
cat > "$BASE/HANDOVER.md" << 'EOF'
# Handover

No sessions yet.
EOF

cat > "$BASE/IDEAS.md" << 'EOF'
# Idea Log

Undecided possibilities — things worth remembering but not yet decided.
Promote to an ADR when ready to decide; discard when no longer relevant.
EOF
```

### Step 5 — Create workspace CLAUDE.md (routing hub)

```bash
cat > "$BASE/CLAUDE.md" << EOF
# <project> Workspace

**Project repo:** <absolute-path-to-project>
**Workspace type:** <private|public>

## Session Start

Run \`add-dir <absolute-path-to-project>\` before any other work.

## Artifact Locations

| Skill | Writes to |
|-------|-----------|
| brainstorming (specs) | \`specs/\` |
| writing-plans (plans) | \`plans/\` |
| handover | \`HANDOVER.md\` |
| idea-log | \`IDEAS.md\` |
| design-snapshot | \`snapshots/\` |
| java-update-design / update-primary-doc | \`design/DESIGN.md\` |
| adr | \`adr/\` |
| write-blog | \`blog/\` |

## Structure

- \`HANDOVER.md\` — session handover (single file, overwritten each session)
- \`IDEAS.md\` — idea log (single file)
- \`specs/\` — brainstorming / design specs (superpowers output)
- \`plans/\` — implementation plans (superpowers output)
- \`snapshots/\` — design snapshots with INDEX.md (auto-pruned, max 10)
- \`adr/\` — architecture decision records with INDEX.md
- \`blog/\` — project diary entries with INDEX.md

## Rules

- All methodology artifacts go here, not in the project repo
- Promotion to project repo is always explicit — never automatic
- Workspace branches mirror project branches — switch both together
EOF
```

### Step 6 — Create gitignored CLAUDE.md symlink in project

```bash
# Create the symlink
ln -sf "$BASE/CLAUDE.md" "<project-path>/CLAUDE.md"

# Hide it from git — ALWAYS use .git/info/exclude, never .gitignore
# Works for any project regardless of ownership (Drools, upstream repos, etc.)
echo "CLAUDE.md" >> "<project-path>/.git/info/exclude"
```

If the project directory does not exist yet, skip this step and tell the user:
> "Symlink skipped — project directory doesn't exist yet. Re-run
> `/workspace-init` after creating the project to add the symlink."

### Step 7 — Create .gitignore for workspace

```bash
cat > "$BASE/.gitignore" << 'EOF'
.DS_Store
EOF
```

### Step 8 — Initialise git and push

```bash
cd "$BASE"
git init
git add .
git commit -m "init: workspace for <project>"
```

If the user provided a GitHub remote URL:

```bash
git remote add origin <github-remote-url>
git push -u origin main
```

If no remote URL provided, tell the user:
> Remote not configured. When ready:
> ```bash
> git remote add origin <your-github-url>
> git push -u origin main
> ```

### Step 9 — Confirm

> ✅ Workspace created at `~/claude/<privacy>/<project>/`
>
> **To start working:**
> 1. Open Claude in `~/claude/<privacy>/<project>/`
> 2. CLAUDE.md will instruct Claude to run `add-dir` on the project automatically
>
> **Symlink status:** CLAUDE.md in the project points to this workspace CLAUDE.md.
> Opening Claude in the project by mistake will still load full config.

---

## Success Criteria

- [ ] Directory exists at correct path with all subdirs
- [ ] `CLAUDE.md` contains session-start `add-dir` instruction and artifact locations table
- [ ] `HANDOVER.md` and `IDEAS.md` exist as stubs
- [ ] `snapshots/INDEX.md`, `adr/INDEX.md`, `blog/INDEX.md` exist
- [ ] `specs/` and `plans/` directories exist
- [ ] `.gitignore` exists
- [ ] CLAUDE.md symlink exists in project (if project dir existed)
- [ ] `CLAUDE.md` in `.git/info/exclude` of project (if project dir existed)
- [ ] Git repo initialised with initial commit
- [ ] Remote set and pushed (if URL provided)

---

## Skill Chaining

**Invoked by:** User directly at project setup time; session-start hook when
no workspace is detected

**Does not chain to anything** — one-time setup skill
```

- [ ] **Step 2: Write `workspace-init/commands/workspace-init.md`**

```markdown
---
description: One-time workspace setup for a project — creates ~/claude/private/<project>/ with full structure, routing CLAUDE.md, and gitignored project symlink
---

Invoke the `workspace-init` skill to set up a new project workspace.
```

- [ ] **Step 3: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add workspace-init/
git commit -m "feat(workspace-init): add workspace setup skill"
```

---

## Task 2: Update `idea-log` paths

**Files:**
- Modify: `idea-log/SKILL.md`

- [ ] **Step 1: Replace all `docs/ideas/IDEAS.md` occurrences with `IDEAS.md`**

```bash
grep -n "docs/ideas" idea-log/SKILL.md
```

Change every occurrence. Also remove any `mkdir -p docs/ideas` lines —
workspace-init creates IDEAS.md at setup.

- [ ] **Step 2: Verify**

```bash
grep "docs/ideas" idea-log/SKILL.md
```

Expected: no output

- [ ] **Step 3: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

- [ ] **Step 4: Commit**

```bash
git add idea-log/SKILL.md
git commit -m "feat(idea-log): write to workspace IDEAS.md instead of docs/ideas/"
```

---

## Task 3: Update `adr` paths

**Files:**
- Modify: `adr/SKILL.md`

- [ ] **Step 1: Replace all `docs/adr/` occurrences with `adr/`**

```bash
grep -n "docs/adr" adr/SKILL.md
```

Change every occurrence. Remove `mkdir -p docs/adr` — workspace-init creates `adr/`.

- [ ] **Step 2: Add INDEX.md maintenance after write step**

After the step that writes the ADR file, add:

```markdown
After writing the ADR file, append a row to `adr/INDEX.md`:
| NNNN | [Title](NNNN-title.md) | Accepted | YYYY-MM-DD |
```

- [ ] **Step 3: Verify**

```bash
grep "docs/adr" adr/SKILL.md
```

Expected: no output

- [ ] **Step 4: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

- [ ] **Step 5: Commit**

```bash
git add adr/SKILL.md
git commit -m "feat(adr): write to workspace adr/ with INDEX.md maintenance"
```

---

## Task 4: Update `design-snapshot` paths

**Files:**
- Modify: `design-snapshot/SKILL.md`

- [ ] **Step 1: Replace `docs/design-snapshots/` with `snapshots/`**

```bash
grep -n "docs/design-snapshots" design-snapshot/SKILL.md
```

Change every occurrence. Remove `mkdir -p docs/design-snapshots`.
Filename pattern: `snapshots/YYYY-MM-DD-<topic>.md`

- [ ] **Step 2: Replace `docs/adr/` cross-references with `adr/`**

```bash
grep -n "docs/adr" design-snapshot/SKILL.md
```

- [ ] **Step 3: Add snapshot auto-pruning to write step**

After writing the snapshot file:

```markdown
**Auto-pruning:** Count files in `snapshots/` (excluding INDEX.md).
If count exceeds 10 (or the limit declared in workspace CLAUDE.md):
- Delete the oldest file
- Update INDEX.md to remove the deleted entry
Each snapshot should reference its predecessor for git chain navigation.
```

- [ ] **Step 4: Add INDEX.md maintenance to write step**

```markdown
After writing the snapshot, append a row to `snapshots/INDEX.md`:
| [YYYY-MM-DD-topic.md](YYYY-MM-DD-topic.md) | YYYY-MM-DD | <one-line summary> |
```

- [ ] **Step 5: Verify**

```bash
grep "docs/design-snapshots\|docs/adr" design-snapshot/SKILL.md
```

Expected: no output

- [ ] **Step 6: Run validators and commit**

```bash
python3 scripts/validate_all.py --tier commit
git add design-snapshot/SKILL.md
git commit -m "feat(design-snapshot): write to workspace snapshots/ with auto-pruning and INDEX.md"
```

---

## Task 5: Verify `write-blog` paths

**Files:**
- Verify: `write-blog/SKILL.md` *(updated this session for images — confirm all paths)*

- [ ] **Step 1: Verify no remaining `docs/blog` references**

```bash
grep "docs/blog" write-blog/SKILL.md
```

Expected: no output (these were already updated)

- [ ] **Step 2: Verify image path is `blog/images/`**

```bash
grep "images" write-blog/SKILL.md | head -5
```

Expected: references to `blog/images/` not `docs/blog/images/`

- [ ] **Step 3: Add INDEX.md maintenance if missing**

After the write step, ensure INDEX.md is updated:

```markdown
After writing the entry, append a row to `blog/INDEX.md`:
| [YYYY-MM-DD-initials-title.md](YYYY-MM-DD-initials-title.md) | YYYY-MM-DD | <one-line summary> |
```

- [ ] **Step 4: Run validators and commit if changed**

```bash
python3 scripts/validate_all.py --tier commit
git add write-blog/SKILL.md
git commit -m "feat(write-blog): verify workspace paths and add INDEX.md maintenance"
```

---

## Task 6: Verify `handover` paths

**Files:**
- Verify: `handover/SKILL.md`
- Verify: `handover/handover-reference.md` *(updated this session)*

- [ ] **Step 1: Verify no `docs/` references remain in either file**

```bash
grep "docs/" handover/SKILL.md handover/handover-reference.md
```

Expected: no output

- [ ] **Step 2: If any found, fix and commit**

```bash
git add handover/SKILL.md handover/handover-reference.md
git commit -m "feat(handover): verify workspace paths complete"
```

---

## Task 7: Update session-start hook

**Files:**
- Modify: `~/.claude/hooks/check_project_setup.sh`

- [ ] **Step 1: Read current hook**

```bash
cat ~/.claude/hooks/check_project_setup.sh
```

- [ ] **Step 2: Add HANDOVER.md prompt after project type check**

Insert after the project-type block, before the Work Tracking check:

```bash
# Check for HANDOVER.md and prompt to read it
if [ -f "HANDOVER.md" ]; then
  LAST_UPDATED=$(git log -1 --format="%ar" -- HANDOVER.md 2>/dev/null || echo "unknown age")
  echo "📋 HANDOVER.md found (last updated: $LAST_UPDATED)."
  echo "Before starting: ask the user 'Read your session handover? (y/n)' — if yes, read and briefly summarise HANDOVER.md."
  # Check staleness
  DAYS=$(git log -1 --format="%ct" -- HANDOVER.md 2>/dev/null | awk -v now="$(date +%s)" '{print int((now-$1)/86400)}')
  if [ -n "$DAYS" ] && [ "$DAYS" -gt 7 ]; then
    echo "⚠️ Handover is $DAYS days old — flag as potentially stale before summarising."
  fi
fi
```

- [ ] **Step 3: Add workspace check**

Insert after the HANDOVER.md block:

```bash
# Check for workspace CLAUDE.md session-start instruction
if grep -q "## Session Start" CLAUDE.md 2>/dev/null; then
  : # Workspace configured — session-start add-dir will handle project access
elif grep -q "Project Type" CLAUDE.md 2>/dev/null; then
  echo "ℹ️  No workspace configured for this project."
  echo "Run /workspace-init to create ~/claude/private/<project>/ and set up the companion workspace."
  echo "(Keeps methodology artifacts out of the project repo)"
fi
```

- [ ] **Step 4: Test the hook**

```bash
bash ~/.claude/hooks/check_project_setup.sh
```

Expected: runs without errors; output reflects current project state

- [ ] **Step 5: Sync hook to repo**

The hook lives at `~/.claude/hooks/` and is managed by `install-skills`. Check
whether `install-skills/SKILL.md` needs updating to reflect the new hook content.

```bash
grep -n "check_project_setup" install-skills/SKILL.md | head -10
```

If the hook script is embedded in `install-skills/SKILL.md`, update it there too
and run sync-local.

- [ ] **Step 6: Commit**

```bash
git add install-skills/SKILL.md  # if updated
git commit -m "feat(hook): add HANDOVER.md read prompt and workspace check to session-start"
```

---

## Task 8: Update metadata and tooling

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `tests/test_mockup_chaining.py`
- Modify: `scripts/generate_web_app_data.py`
- Modify: `scripts/validation/validate_web_app.py`

- [ ] **Step 1: Add `workspace-init` to marketplace.json**

```json
{
  "name": "workspace-init",
  "source": "./workspace-init",
  "description": "One-time workspace setup — creates ~/claude/private/<project>/ with routing CLAUDE.md, gitignored project symlink, and full directory structure",
  "version": "1.0.0-SNAPSHOT"
}
```

- [ ] **Step 2: Add `workspace-init` to ALL_SKILLS and CHAINING_TRUTH in test file**

In `tests/test_mockup_chaining.py`:

```python
# In ALL_SKILLS set:
'workspace-init',

# In CHAINING_TRUTH dict:
'workspace-init': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []},
```

- [ ] **Step 3: Add `workspace-init` to both scripts**

In `scripts/generate_web_app_data.py` and `scripts/validation/validate_web_app.py`,
find the `ALL_SKILLS` set and add `'workspace-init'`.

- [ ] **Step 4: Generate slash command file**

```bash
python3 scripts/generate_commands.py
```

- [ ] **Step 5: Run full test suite**

```bash
python3 -m pytest tests/ -v
```

Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/marketplace.json tests/test_mockup_chaining.py \
  scripts/generate_web_app_data.py scripts/validation/validate_web_app.py
git commit -m "chore: register workspace-init in marketplace and test fixtures"
```

---

## Task 9: Update CLAUDE.md and README.md

- [ ] **Step 1: Add `workspace-init` to Key Skills in CLAUDE.md**

Under `## Key Skills`, add a new **Workspace** group:

```markdown
**Workspace:**
- `workspace-init` — one-time setup; creates `~/claude/private/<project>/` or
  `~/claude/public/<project>/` with routing CLAUDE.md, gitignored project symlink
  via `.git/info/exclude`, and all subdirectories
```

- [ ] **Step 2: Add workspace model note to CLAUDE.md**

Add a brief `## Workspace Model` section pointing to the spec:

```markdown
## Workspace Model

Skills write methodology artifacts to a companion workspace, not the project repo.
Full design: `docs/superpowers/specs/2026-04-09-workspace-model-design.md`

- Claude opens in the workspace (`~/claude/private/<project>/`)
- Project added automatically via `add-dir` (instructed by workspace CLAUDE.md)
- Run `/workspace-init` once per project to create the workspace
```

- [ ] **Step 3: Add `workspace-init` to README.md**

Find the skills listing table. Add `workspace-init` alongside setup/lifecycle skills.

- [ ] **Step 4: Run validators and commit**

```bash
python3 scripts/validate_all.py --tier commit
git add CLAUDE.md README.md
git commit -m "docs: document workspace model and workspace-init skill"
```

---

## Task 10: Sync and verify end-to-end

- [ ] **Step 1: Sync all skills**

```bash
python3 scripts/claude-skill sync-local --all -y
```

Expected: 47 skills synced (46 existing + workspace-init)

- [ ] **Step 2: Run full validation**

```bash
python3 scripts/validate_all.py --tier commit
python3 -m pytest tests/ -v
```

Expected: all pass

- [ ] **Step 3: Smoke test workspace-init manually**

In a new Claude session, invoke `/workspace-init` with a test project name.
Verify:
- All directories created
- CLAUDE.md contains session-start `add-dir` instruction and artifact table
- CLAUDE.md symlink created in project (if project exists)
- `CLAUDE.md` line in `.git/info/exclude`
- Git repo initialised

---

## Task 10b: Update `java-update-design` and `update-primary-doc` paths

**Files:**
- Modify: `java-update-design/SKILL.md`
- Modify: `update-primary-doc/SKILL.md`

Both skills currently write to the project's `DESIGN.md` directly. In the
workspace model they write to `design/DESIGN.md` in the workspace (CWD).
At epic close, Claude merges workspace `design/DESIGN.md` back into the
project's `DESIGN.md` — one merge of two documents, user-confirmed.

- [ ] **Step 1: Update `java-update-design` to write to `design/DESIGN.md`**

Change every reference from project-root `DESIGN.md` to `design/DESIGN.md`.
Add a note: "At epic close, ask Claude to merge `design/DESIGN.md` into the
project's `DESIGN.md`."

- [ ] **Step 2: Update `update-primary-doc` similarly**

The primary doc path comes from CLAUDE.md Sync Rules. Redirect writes to
`design/DESIGN.md` during the epic; note the epic-close merge step.

- [ ] **Step 3: Validate and commit**

```bash
python3 scripts/validate_all.py --tier commit
git add java-update-design/SKILL.md update-primary-doc/SKILL.md
git commit -m "feat(design): write to workspace design/DESIGN.md instead of project root"
```

---

## Migration Task (Handled in workspace-init Step 9)

**Historical ADRs and blog entries stay in the project repo** — they are already
in the right long-term home. Only routing config and active in-progress work move.

`workspace-init` Step 9 detects and offers (with automated git rm + commit):

| Artifact | From | To |
|----------|------|----|
| `CLAUDE.md` (committed) | project root | workspace `CLAUDE.md` (appended); symlink back |
| `HANDOFF.md` / `HANDOVER.md` | project root | workspace `HANDOVER.md` (most recent wins) |
| Active specs/plans | `docs/superpowers/` or `.superpowers/` | workspace `specs/` or `plans/` |
| Design snapshots | `docs/design-snapshots/` | workspace `snapshots/` |

**Not migrated (stays in project repo):**
- `docs/adr/` — permanent project record
- `docs/blog/` / `docs/_posts/` — published diary
- `docs/ideas/IDEAS.md` — if project-scoped

---

## Out of Scope (This Plan)

- Garden path changes — deferred
- Parent `~/claude/` workspace git repo setup — deferred
- `epic-start` and `epic-close` skills — separate epic, see mdproctor/cc-praxis#49
