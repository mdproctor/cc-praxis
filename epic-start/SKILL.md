---
name: epic-start
description: >
  Use when the user wants to begin a new development epic — says "begin
  epic", "new epic", or "create epic branch". One-time setup only; not
  for day-to-day work within an epic.
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

Read the project path from workspace CLAUDE.md `## Session Start` → `add-dir` line:

```bash
grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //'
```

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
