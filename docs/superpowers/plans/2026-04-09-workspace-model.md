# Workspace Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move all methodology artifacts (handovers, snapshots, ADRs, idea-log, blog) out of project repos and into dedicated workspace directories at `~/claude/private/<project>/` or `~/claude/public/<project>/`.

**Architecture:** Claude opens in the workspace (CWD), adds the project repo via `add-dir`. Skills write to CWD-relative paths (no `docs/` prefix). A new `workspace-init` skill bootstraps the workspace structure for any project. Existing skills get path-only updates — no workflow changes.

**Tech Stack:** Markdown skills, bash, Python validators, pytest

---

## File Map

**Create:**
- `workspace-init/SKILL.md`
- `workspace-init/commands/workspace-init.md`

**Modify (path updates only):**
- `idea-log/SKILL.md` — `docs/ideas/IDEAS.md` → `IDEAS.md`
- `adr/SKILL.md` — `docs/adr/` → `adr/`
- `design-snapshot/SKILL.md` — `docs/design-snapshots/` → `snapshots/`, `docs/adr/` → `adr/`
- `write-blog/SKILL.md` — `docs/blog/` → `blog/`
- `handover/SKILL.md` — `docs/design-snapshots/` → `snapshots/`, `docs/write-blog/` → `blog/`, `docs/adr/` → `adr/`

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
  invokes /workspace-init. Creates the workspace directory structure, CLAUDE.md,
  git repo, and GitHub remote. NOT for day-to-day workspace use — one-time setup only.
---

# Workspace Init

Creates a companion workspace for a project at `~/claude/private/<project>/`
or `~/claude/public/<project>/`. Run once per project, per machine.

After running, open Claude in the workspace directory and add the project via
`add-dir /path/to/project`.

---

## Workflow

### Step 1 — Gather inputs

Ask the user for:
1. **Project name** — used as the workspace directory name (e.g. `cc-praxis`)
2. **Privacy** — `private` or `public`
3. **Absolute path to project** — where the project lives or will live (e.g. `/Users/you/projects/cc-praxis`)
4. **GitHub remote URL** for the workspace repo — optional; skip if not ready yet

Then check the project path:

```bash
if [ -d "<project-path>" ]; then
  echo "Project directory exists"
  if [ -d "<project-path>/.git" ]; then
    echo "Git repo: yes"
  else
    echo "Git repo: no (that's fine — workspace-init doesn't require one)"
  fi
else
  echo "Project directory does not exist yet — recording intended path"
fi
```

Tell the user what was found and confirm before proceeding. The workspace can
be created regardless of whether the project directory or git repo exists yet —
the path in workspace CLAUDE.md is just a pointer.

### Step 2 — Create directory structure

```bash
BASE=~/claude/<privacy>/<project>
mkdir -p "$BASE/snapshots" "$BASE/adr" "$BASE/blog"
```

### Step 3 — Create INDEX.md in each subfolder

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

### Step 5 — Create workspace CLAUDE.md

```bash
cat > "$BASE/CLAUDE.md" << EOF
# <project> Workspace

**Project repo:** <absolute-path-to-project>
**Workspace type:** <private|public>

## Structure

- \`HANDOVER.md\` — session handover (single file, overwritten each session)
- \`IDEAS.md\` — idea log (single file)
- \`snapshots/\` — design snapshots with INDEX.md (auto-pruned, max 10)
- \`adr/\` — architecture decision records with INDEX.md
- \`blog/\` — project diary entries with INDEX.md

## Rules

- Always read HANDOVER.md at the start of each session
- All methodology artifacts go here, not in the project repo
- Promotion to project repo (e.g. ADRs at epic close) is always explicit — never automatic
- When committing workspace content, keep it separate from project commits
EOF
```

### Step 6 — Create .gitignore

```bash
cat > "$BASE/.gitignore" << 'EOF'
.DS_Store
EOF
```

### Step 7 — Initialise git and push

Always init git (the workspace is always a git repo):

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

If no remote URL was provided, tell the user:

> Remote not configured. When ready, run:
> ```bash
> git remote add origin <your-github-url>
> git push -u origin main
> ```

### Step 8 — Confirm

Tell the user:

> ✅ Workspace created at `~/claude/<privacy>/<project>/`
>
> **Next steps:**
> 1. Open Claude in `~/claude/<privacy>/<project>/`
> 2. Run `add-dir <absolute-path-to-project>` to make the project accessible
> 3. Claude will read `CLAUDE.md` automatically and know where to write artifacts

---

## Success Criteria

- [ ] Directory exists at `~/claude/private/<project>/` or `~/claude/public/<project>/`
- [ ] `CLAUDE.md` contains correct project path and workspace type
- [ ] `HANDOVER.md` and `IDEAS.md` exist as stubs
- [ ] `snapshots/INDEX.md`, `adr/INDEX.md`, `blog/INDEX.md` exist
- [ ] `.gitignore` exists
- [ ] Git repo initialised with initial commit
- [ ] Remote set and pushed

---

## Skill Chaining

**Invoked by:** User directly at project setup time

**Does not chain to anything** — one-time setup skill
```

- [ ] **Step 2: Write `workspace-init/commands/workspace-init.md`**

```markdown
---
description: Set up a workspace directory for a project — run once per project to create ~/claude/private/<project>/ or ~/claude/public/<project>/
---

Invoke the `workspace-init` skill to create a new project workspace.
```

- [ ] **Step 3: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

Expected: PASS (or only warnings unrelated to new skill)

- [ ] **Step 4: Commit**

```bash
git add workspace-init/
git commit -m "feat(workspace-init): add workspace setup skill"
```

---

## Task 2: Update `idea-log` paths

**Files:**
- Modify: `idea-log/SKILL.md`

The skill currently writes to `docs/ideas/IDEAS.md`. In workspace model, CWD is
the workspace, so the path becomes simply `IDEAS.md`.

- [ ] **Step 1: Replace all `docs/ideas/IDEAS.md` with `IDEAS.md`**

In `idea-log/SKILL.md`, replace every occurrence of `docs/ideas/IDEAS.md` with `IDEAS.md`:

Lines to change:
- Line ~40: `docs/ideas/IDEAS.md` → `IDEAS.md`
- Line ~87: `grep -i "<keyword>" docs/ideas/IDEAS.md 2>/dev/null` → `grep -i "<keyword>" IDEAS.md 2>/dev/null`
- Line ~94: `create docs/ideas/ if needed` — remove this parenthetical entirely (workspace-init creates IDEAS.md at setup)
- Line ~211: `docs/ideas/IDEAS.md` → `IDEAS.md`
- Line ~244: `docs/ideas/IDEAS.md` → `IDEAS.md`

- [ ] **Step 2: Remove `docs/ideas/` directory creation references**

Find and remove any `mkdir -p docs/ideas` lines — workspace-init handles setup.

- [ ] **Step 3: Verify with grep**

```bash
grep "docs/ideas" idea-log/SKILL.md
```

Expected: no output

- [ ] **Step 4: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

- [ ] **Step 5: Commit**

```bash
git add idea-log/SKILL.md
git commit -m "feat(idea-log): write to workspace IDEAS.md instead of docs/ideas/"
```

---

## Task 3: Update `adr` paths

**Files:**
- Modify: `adr/SKILL.md`

The skill currently writes to `docs/adr/`. In workspace model: `adr/`.

- [ ] **Step 1: Replace all `docs/adr/` with `adr/`**

```bash
grep -n "docs/adr" adr/SKILL.md
```

Use that output to find every occurrence. Change:
- `docs/adr/` → `adr/`
- `ls docs/adr/` → `ls adr/`
- `mkdir -p docs/adr` — remove (workspace-init creates `adr/`)
- References to `../adr/` in cross-reference links within snapshot files → `../adr/` stays (relative links within workspace are fine)

- [ ] **Step 2: Add INDEX.md maintenance to the write step**

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

- [ ] **Step 6: Commit**

```bash
git add adr/SKILL.md
git commit -m "feat(adr): write to workspace adr/ with INDEX.md maintenance"
```

---

## Task 4: Update `design-snapshot` paths

**Files:**
- Modify: `design-snapshot/SKILL.md`

The skill currently writes to `docs/design-snapshots/` and cross-references `docs/adr/`.
In workspace model: `snapshots/` and `adr/`.

- [ ] **Step 1: Replace `docs/design-snapshots/` with `snapshots/`**

```bash
grep -n "docs/design-snapshots" design-snapshot/SKILL.md
```

Change every occurrence:
- `docs/design-snapshots/` → `snapshots/`
- `ls docs/design-snapshots/` → `ls snapshots/`
- `mkdir -p docs/design-snapshots` → remove (workspace-init creates `snapshots/`)
- Filename pattern: `docs/design-snapshots/YYYY-MM-DD-<topic>.md` → `snapshots/YYYY-MM-DD-<topic>.md`

- [ ] **Step 2: Replace `docs/adr/` cross-references with `adr/`**

```bash
grep -n "docs/adr" design-snapshot/SKILL.md
```

Change `docs/adr/` → `adr/`

- [ ] **Step 3: Update snapshot auto-pruning reference**

Ensure the skill mentions the auto-prune behaviour (max 10, oldest removed,
each references predecessor). Add to the write step if not present:

```markdown
**Auto-pruning:** After writing, count files in `snapshots/` (excluding INDEX.md).
If count exceeds 10 (or the limit in workspace CLAUDE.md), delete the oldest file.
Update INDEX.md to remove the deleted entry.
```

- [ ] **Step 4: Update INDEX.md maintenance**

The skill should update `snapshots/INDEX.md` after writing each snapshot:

```markdown
After writing the snapshot file, append a row to `snapshots/INDEX.md`:
| [YYYY-MM-DD-topic.md](YYYY-MM-DD-topic.md) | YYYY-MM-DD | <one-line topic summary> |
```

- [ ] **Step 5: Verify**

```bash
grep "docs/design-snapshots\|docs/adr" design-snapshot/SKILL.md
```

Expected: no output

- [ ] **Step 6: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

- [ ] **Step 7: Commit**

```bash
git add design-snapshot/SKILL.md
git commit -m "feat(design-snapshot): write to workspace snapshots/ with auto-pruning and INDEX.md"
```

---

## Task 5: Update `write-blog` paths

**Files:**
- Modify: `write-blog/SKILL.md`

The skill currently writes to `docs/blog/`. In workspace model: `blog/`.
The CLAUDE.md style-guide pointer check should target workspace CLAUDE.md (already CWD).

- [ ] **Step 1: Replace `docs/blog/` with `blog/`**

```bash
grep -n "docs/blog" write-blog/SKILL.md
```

Change every occurrence:
- `docs/blog/` → `blog/`
- `ls docs/blog/` → `ls blog/`
- `mkdir -p docs/blog` → remove (workspace-init creates `blog/`)
- Filename pattern: `docs/blog/YYYY-MM-DD-<initials>NN-<title>.md` → `blog/YYYY-MM-DD-<initials>NN-<title>.md`
- Success criteria: `docs/blog/YYYY-MM-DD-...` → `blog/YYYY-MM-DD-...`
- Flowchart node: `Write to\ndocs/blog/` → `Write to\nblog/`

- [ ] **Step 2: Update the CLAUDE.md style guide check**

The check at Step 0c looks for the style guide pointer in CLAUDE.md. In the
workspace model, this is the workspace CLAUDE.md (already CWD). No path change
needed — `CLAUDE.md` without a prefix already resolves to CWD. Verify the
check uses no `docs/` prefix:

```bash
grep "CLAUDE.md" write-blog/SKILL.md | head -5
```

Expected: references to `CLAUDE.md` only (no `docs/CLAUDE.md`)

- [ ] **Step 3: Update blog INDEX.md maintenance**

After writing a blog entry, the skill should append to `blog/INDEX.md`:

```markdown
After writing the entry, append a row to `blog/INDEX.md`:
| [YYYY-MM-DD-initials-title.md](YYYY-MM-DD-initials-title.md) | YYYY-MM-DD | <one-line summary> |
```

- [ ] **Step 4: Verify**

```bash
grep "docs/blog" write-blog/SKILL.md
```

Expected: no output

- [ ] **Step 5: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

- [ ] **Step 6: Commit**

```bash
git add write-blog/SKILL.md
git commit -m "feat(write-blog): write to workspace blog/ with INDEX.md maintenance"
```

---

## Task 6: Update `handover` reference-building paths

**Files:**
- Modify: `handover/SKILL.md`

The skill's Step 4 builds a references table by listing `docs/design-snapshots/`,
`docs/write-blog/`, and `docs/adr/`. These become `snapshots/`, `blog/`, `adr/`.
The `HANDOFF.md` filename itself is already CWD-relative — no change needed there.

- [ ] **Step 1: Update Step 4 reference-building commands**

Find lines ~218-220 in `handover/SKILL.md`:

```bash
# Current (to remove):
ls docs/design-snapshots/ | sort | tail -1   # latest snapshot path
ls docs/write-blog/ | sort | tail -1       # latest blog entry path
ls docs/adr/ | sort | tail -3                # recent ADRs
```

Replace with:

```bash
ls snapshots/ | grep -v INDEX.md | sort | tail -1   # latest snapshot path
ls blog/ | grep -v INDEX.md | sort | tail -1         # latest blog entry path
ls adr/ | grep -v INDEX.md | sort | tail -3          # recent ADRs
```

- [ ] **Step 2: Update `handover/handover-reference.md` paths**

In `handover/handover-reference.md`, lines ~41-44 contain the routing table. Change:

```markdown
| Design state | `docs/design-snapshots/<latest>.md` | `cat` that file |
| Project narrative | `docs/write-blog/<latest>.md` | `cat` that file |
| Open ideas | `docs/ideas/IDEAS.md` | `cat` that file |
```

To:

```markdown
| Design state | `snapshots/<latest>.md` | `cat` that file |
| Project narrative | `blog/<latest>.md` | `cat` that file |
| Open ideas | `IDEAS.md` | `cat` that file |
```

- [ ] **Step 3: Verify no remaining `docs/` references**

```bash
grep "docs/" handover/SKILL.md handover/handover-reference.md
```

Expected: no output

- [ ] **Step 4: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

- [ ] **Step 5: Commit**

```bash
git add handover/SKILL.md handover/handover-reference.md
git commit -m "feat(handover): update reference-building paths to workspace layout"
```

---

## Task 7: Update metadata and tooling

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `tests/test_mockup_chaining.py`
- Modify: `scripts/generate_web_app_data.py`
- Modify: `scripts/validation/validate_web_app.py`

- [ ] **Step 1: Add `workspace-init` to marketplace.json**

Find the plugins array in `.claude-plugin/marketplace.json` and add:

```json
{
  "name": "workspace-init",
  "source": "./workspace-init",
  "description": "One-time workspace setup for a project — creates ~/claude/private/<project>/ or ~/claude/public/<project>/ with the full directory structure, CLAUDE.md, and git remote",
  "version": "1.0.0-SNAPSHOT"
}
```

- [ ] **Step 2: Add `workspace-init` to ALL_SKILLS in test file**

In `tests/test_mockup_chaining.py`, find the `ALL_SKILLS` set and add `'workspace-init'`.

- [ ] **Step 3: Add `workspace-init` to CHAINING_TRUTH in test file**

In `tests/test_mockup_chaining.py`, find `CHAINING_TRUTH` and add:

```python
'workspace-init': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []},
```

- [ ] **Step 4: Add `workspace-init` to generate_web_app_data.py and validate_web_app.py**

In both scripts, find the `ALL_SKILLS` set and add `'workspace-init'`.

- [ ] **Step 5: Generate slash command file**

```bash
python3 scripts/generate_commands.py
```

Verify `workspace-init/commands/workspace-init.md` exists (already created in Task 1).

- [ ] **Step 6: Run full test suite**

```bash
python3 -m pytest tests/ -v
```

Expected: all tests pass

- [ ] **Step 7: Commit**

```bash
git add .claude-plugin/marketplace.json tests/test_mockup_chaining.py \
  scripts/generate_web_app_data.py scripts/validation/validate_web_app.py
git commit -m "chore: register workspace-init in marketplace and test fixtures"
```

---

## Task 8: Update CLAUDE.md and README.md

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`

- [ ] **Step 1: Add `workspace-init` to Key Skills section in CLAUDE.md**

Find the `## Key Skills` section. Under "Skill manager:", add after `cc-praxis-ui`:

```markdown
**Workspace:**
- `workspace-init` — one-time setup skill; creates `~/claude/private/<project>/` or `~/claude/public/<project>/` with full directory structure, CLAUDE.md, and git remote
```

- [ ] **Step 2: Add workspace model overview to CLAUDE.md**

Find the `## Developer Workflow` section and add a note about the workspace model:

```markdown
## Workspace Model

Skills write methodology artifacts to a companion workspace, not the project repo.
See `docs/superpowers/specs/2026-04-09-workspace-model-design.md` for full design.

- Claude opens in the workspace (`~/claude/private/<project>/` or `~/claude/public/<project>/`)
- Project repo is added via `add-dir`
- Run `/workspace-init` once per project to create the workspace
```

- [ ] **Step 3: Add `workspace-init` to README.md skill listing**

Find the skills table in README.md. Add `workspace-init` in the appropriate section
(alongside other setup/lifecycle skills like `install-skills`, `cc-praxis-ui`).

- [ ] **Step 4: Run validators**

```bash
python3 scripts/validate_all.py --tier commit
```

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md README.md
git commit -m "docs: document workspace model and workspace-init skill"
```

---

## Task 9: Sync and verify end-to-end

- [ ] **Step 1: Sync all skills to ~/.claude/skills/**

```bash
python3 scripts/claude-skill sync-local --all -y
```

Expected: all skills synced including `workspace-init`

- [ ] **Step 2: Run full validation suite**

```bash
python3 scripts/validate_all.py --tier commit
python3 -m pytest tests/ -v
```

Expected: all pass

- [ ] **Step 3: Smoke test workspace-init**

In a new Claude session, open in a temp directory and invoke the `workspace-init`
skill. Verify:
- Directory created at `~/claude/private/<test-project>/`
- All subdirectories present: `snapshots/`, `adr/`, `blog/`
- All INDEX.md files present
- CLAUDE.md contains correct project path
- Git repo initialised

- [ ] **Step 4: Final commit if any fixups needed**

```bash
git add -A
git commit -m "chore: post-sync fixups"
```

---

## Out of Scope (This Plan)

- Migration of existing cc-praxis artifacts from `docs/` to workspace — separate task
- `design/` folder — blocked on issue-scoping question
- Garden path changes — deferred to later iteration
- Parent `~/claude/` workspace git repo setup — deferred
- Epic-close workflow skill — deferred
