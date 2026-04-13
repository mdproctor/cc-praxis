---
name: workspace-init
description: >
  Use when a project has no companion workspace yet — user says "init
  workspace", "set up workspace", "create workspace for <project>", or
  invokes /workspace-init. NOT for day-to-day workspace use — one-time
  only, each machine independently.
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

Draft the base CLAUDE.md content, then **show it to the user and ask for
acceptance before writing**. Never write CLAUDE.md without confirmation.

Draft:

```
# <project> Workspace

**Project repo:** <absolute-path-to-project>
**Workspace type:** <private|public>

## Session Start

Run `add-dir <absolute-path-to-project>` before any other work.

## Artifact Locations

| Skill | Writes to |
|-------|-----------|
| brainstorming (specs) | `specs/` |
| writing-plans (plans) | `plans/` |
| handover | `HANDOVER.md` |
| idea-log | `IDEAS.md` |
| design-snapshot | `snapshots/` |
| java-update-design / update-primary-doc | `design/DESIGN.md` |
| adr | `adr/` |
| write-blog | `blog/` |

## Structure

- `HANDOVER.md` — session handover (single file, overwritten each session)
- `IDEAS.md` — idea log (single file)
- `specs/` — brainstorming / design specs (superpowers output)
- `plans/` — implementation plans (superpowers output)
- `snapshots/` — design snapshots with INDEX.md (auto-pruned, max 10)
- `adr/` — architecture decision records with INDEX.md
- `blog/` — project diary entries with INDEX.md

## Rules

- All methodology artifacts go here, not in the project repo
- Promotion to project repo is always explicit — never automatic
- Workspace branches mirror project branches — switch both together
```

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

If the project directory does not exist yet, skip this step and tell the user:
> "Symlink skipped — project directory doesn't exist yet. Re-run
> `/workspace-init` after creating the project to add the symlink."

Otherwise, check whether CLAUDE.md is committed to git:

```bash
git -C "<project-path>" ls-files --error-unmatch CLAUDE.md 2>/dev/null && echo "committed" || echo "not committed"
```

**If CLAUDE.md is committed**, present:
> "CLAUDE.md is committed to git (`<size>` bytes). Migrate it to the workspace?
> This will append its content to `workspace/CLAUDE.md`, remove it from the
> project repo with `git rm`, commit the deletion, then create a symlink back.
> (YES / no)"

If YES:
```bash
# Append project CLAUDE.md content to workspace CLAUDE.md (below routing header)
echo -e "\n---\n" >> "$BASE/CLAUDE.md"
cat "<project-path>/CLAUDE.md" >> "$BASE/CLAUDE.md"

# Remove from project and commit
git -C "<project-path>" rm CLAUDE.md
git -C "<project-path>" commit -m "chore: migrate CLAUDE.md to workspace"

# Create symlink so opening Claude in the project still loads full config
ln -sf "$BASE/CLAUDE.md" "<project-path>/CLAUDE.md"
echo "CLAUDE.md" >> "<project-path>/.git/info/exclude"
```

If no: skip the symlink. Tell the user:
> "CLAUDE.md stays in the project repo. Open Claude in the workspace dir —
> `add-dir` will load the project including its CLAUDE.md."

**If CLAUDE.md is not committed**, create the symlink as normal:
```bash
ln -sf "$BASE/CLAUDE.md" "<project-path>/CLAUDE.md"
echo "CLAUDE.md" >> "<project-path>/.git/info/exclude"
```

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
# Root-level handovers
[ -f "<project-path>/HANDOFF.md" ]  && git -C "<project-path>" ls-files --error-unmatch HANDOFF.md  2>/dev/null && FOUND+=("HANDOFF.md → HANDOVER.md")
[ -f "<project-path>/HANDOVER.md" ] && git -C "<project-path>" ls-files --error-unmatch HANDOVER.md 2>/dev/null && FOUND+=("HANDOVER.md → HANDOVER.md")

# docs/ artifacts
[ -d "<project-path>/docs/design-snapshots" ]  && FOUND+=("docs/design-snapshots/ → snapshots/")
[ -d "<project-path>/docs/adr" ]               && FOUND+=("docs/adr/ → adr/")
[ -d "<project-path>/docs/blog" ]              && FOUND+=("docs/blog/ → blog/")
[ -d "<project-path>/docs/_posts" ]            && FOUND+=("docs/_posts/ → blog/")
[ -d "<project-path>/docs/handoffs" ]          && FOUND+=("docs/handoffs/ → handoffs/")
[ -f "<project-path>/docs/ideas/IDEAS.md" ]    && FOUND+=("docs/ideas/IDEAS.md → IDEAS.md")
[ -d "<project-path>/docs/superpowers/specs" ] && FOUND+=("docs/superpowers/specs/ → specs/")
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

If YES (or after selection is confirmed), for each item:
```bash
# 1. Copy to workspace (example for adr/)
cp -r "<project-path>/docs/adr/." "$BASE/adr/"

# 2. Remove from project
git -C "<project-path>" rm -r docs/adr

# ... repeat for each selected item
```

Then commit all removals in one go:
```bash
git -C "<project-path>" commit -m "chore: migrate methodology artifacts to workspace"
```

**Note on handovers:** If both `HANDOFF.md` and `HANDOVER.md` exist, use the
more recent file as `workspace/HANDOVER.md` and discard the older one.

### Step 10 — Confirm

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
- [ ] CLAUDE.md handled: migrated (symlink + .git/info/exclude) or left committed per user choice
- [ ] Claude session history and memory migrated to workspace-keyed path (`~/.claude/projects/`)
- [ ] Existing methodology artifacts offered for migration; selected ones copied and `git rm`'d with single commit
- [ ] Git repo initialised with initial commit
- [ ] Remote set and pushed (if URL provided)

---

## Skill Chaining

**Invoked by:** User directly at project setup time; session-start hook when
no workspace is detected

**Does not chain to anything** — one-time setup skill
