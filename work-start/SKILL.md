---
name: work-start
description: >
  MUST be invoked at the start of every piece of work — user says "work-start",
  or it appears as the first instruction in a work-item prompt. Detects current
  branch state, creates a branch if needed, scaffolds .meta + JOURNAL.md, and
  runs pre-checks before any design or implementation begins. Replaces the
  former two-step "work-start + /epic begin" workflow — branch creation is now
  integrated. These checks are NOT optional and must NOT be skipped even for
  small changes.
---

# work-start

Single entry point for all work. Detects state, creates or resumes a branch,
runs pre-checks. **Never skip this skill — even for small changes.**

---

## Path Resolution (run first, always)

```bash
PROJECT=$(grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //')
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md | head -1 | sed 's/.*`\(.*\)`.*/\1/')
```

All file paths and git commands below use `$PROJECT` and `$WORKSPACE`. Never
use bare `git` without `-C <path>`. Never rely on CWD.

---

## Branch Switch Helper

Use any time both repos must switch branches together. Never switch one alone.

```bash
git -C "$PROJECT" checkout <branch>
git -C "$WORKSPACE" checkout <branch>

PROJECT_BEHIND=$(git -C "$PROJECT" rev-list HEAD..origin/<branch> --count 2>/dev/null || echo 0)
WORKSPACE_BEHIND=$(git -C "$WORKSPACE" rev-list HEAD..origin/<branch> --count 2>/dev/null || echo 0)
if [ "$PROJECT_BEHIND" -gt 0 ] || [ "$WORKSPACE_BEHIND" -gt 0 ]; then
  echo "Remote has new commits (+${PROJECT_BEHIND} project, +${WORKSPACE_BEHIND} workspace)."
  echo "Incorporate now with pull --rebase? (y/n)"
  # Wait — user may not be ready for upstream changes
fi

PROJECT_BRANCH=$(git -C "$PROJECT" branch --show-current)
WORKSPACE_BRANCH=$(git -C "$WORKSPACE" branch --show-current)
[ "$PROJECT_BRANCH" = "$WORKSPACE_BRANCH" ] \
  || { echo "⚠️ Mismatch after switch. Manual alignment required."; exit 1; }
echo "✅ Both repos on: $PROJECT_BRANCH"
```

If helper fails (branch absent in one repo, network error): hard stop with
instructions. Do not loop.

---

## Detection

Resolve paths first. Then read:

```bash
META_BRANCH=$(grep "^branch:" "$WORKSPACE/design/.meta" 2>/dev/null | sed 's/branch: //')
CURRENT_WORKSPACE=$(git -C "$WORKSPACE" branch --show-current)
CURRENT_PROJECT=$(git -C "$PROJECT" branch --show-current)
```

Check in order — first match wins:

```
1. $WORKSPACE/design/.paused exists in the working tree
   → Hard stop. "Paused branch detected. Invoke work-resume first."

2. $WORKSPACE/design/.meta exists, AND
   META_BRANCH == CURRENT_WORKSPACE == CURRENT_PROJECT (all three match)
   → Resume path.

3. $WORKSPACE/design/.meta exists, CURRENT_WORKSPACE == main
   (orphaned — .meta on main, regardless of project branch)
   → Hard stop. "Invoke work-end to complete or discard the abandoned branch."
   *** Checked BEFORE state 4 — orphaned also satisfies "branches misaligned"
   so state 4 would fire incorrectly and attempt to switch to a deleted branch. ***

4. $WORKSPACE/design/.meta exists, branches misaligned
   (META_BRANCH != CURRENT_WORKSPACE or CURRENT_PROJECT, and not orphaned)
   → Invoke Branch Switch Helper inline.
     If helper fails → hard stop with manual instructions (no loop).

5. CURRENT_WORKSPACE == main, no .meta, no .paused
   → New branch path (Steps 0–12 below).

6. On non-main branch, no .meta
   → "You are on <branch> with no branch scaffold.
      Continue here (y) or switch to main (n)?"
      y → run Steps 0, 2, 3, 11 only. No scaffold created. Skip Step 4 —
            no .meta exists to record the issue. This path is for hotfixes or
            docs-only work that will not use work-end. If work-end is needed
            later, create .meta manually first.
      n → Branch Switch Helper to main, re-run detection.
```

---

## New Branch Path

### Step 0 — Resolve paths

Read `$PROJECT` and `$WORKSPACE` from CLAUDE.md (see Path Resolution above).

### Step 1 — Work description

Use the invocation argument if provided. Otherwise prompt:
> "Describe the work in one sentence."

### Step 2 — Platform coherence

Locate the platform doc:

```bash
ls "$PROJECT/docs/PLATFORM.md" 2>/dev/null || ls ~/claude/casehub/parent/docs/PLATFORM.md 2>/dev/null
```

Read it. Run the five coherence questions against the work description:

1. **Does this already exist?** Is this capability already implemented somewhere?
2. **Is this the right repo?** Would this work more naturally live elsewhere?
3. **Does this create a consolidation opportunity?** Should existing similar code be unified?
4. **Is it consistent with platform patterns?** Module tier structure, naming conventions, architectural rules?
5. **Does it need a platform-level doc update?** Will PLATFORM.md or docs/repos/ need updating?

Surface any concerns to the user before proceeding.

### Step 3 — Relevant protocols

```bash
ls "$PROJECT/docs/protocols/" 2>/dev/null || ls ~/claude/casehub/parent/docs/protocols/ 2>/dev/null
```

Read any protocols applicable to the described work. Surface violations before proceeding.

Common signals:
- Maven coordinate changes → `maven-coordinate-standard.md`, `artifact-rename-propagation.md`
- Flyway migrations → `flyway-migration-rules.md`, `flyway-version-range-allocation.md`
- SPI changes → `ledger-spi-propagation.md`, `spi-blocking-reactive-parity.md`
- Module structure → `module-tier-structure.md`, `maven-submodule-folder-naming.md`

### Step 4 — Issue

If tracking enabled (CLAUDE.md `## Work Tracking` with `Issue tracking: enabled`):

```bash
gh issue list --state open --repo <owner/repo> --limit 10
```

- Search for an existing open issue matching the work description.
- If found: confirm — "Found #N: `<title>`. Use this? (y/n)"
- If not found: offer to create — wait for result.
- Record `ISSUE_N` and `ISSUE_TITLE` for Step 5.

If tracking disabled: skip silently.

Do not proceed without resolving this step.

### Step 5 — Branch name

Derive: `issue-NNN-<slug>` (title lowercased, special chars stripped, max 30 chars after prefix).

Show to user, allow override. Guards:
- Reject `main`, `HEAD`, or any existing branch name in either repo.
- The issue number (NNN) is the stable key — the slug is a convenience only.

### Step 6 — Flyway V scan

```bash
git -C "$PROJECT" fetch --all 2>/dev/null || echo "⚠️ No network — scan incomplete"
```

If network available: scan main + all remote branches for claimed V numbers. Compute
`next-safe-v = max + 1`. If conflict found: warn, show offending branches, block until acknowledged.

Only ask about Flyway if the user described migration work:
> "Will this branch include database migrations? (y/n)"
> - y → `FLYWAY_NEXT_V=<next-safe-v>`
> - explicit n → `FLYWAY_NEXT_V=none`
> - no answer (default) → `FLYWAY_NEXT_V=unknown`

### Step 7 — Create branches (atomic)

```bash
git -C "$PROJECT" checkout -b <branch-name>
# If fails → abort (nothing to clean up)
git -C "$WORKSPACE" checkout -b <branch-name>
# If fails → git -C "$PROJECT" branch -D <branch-name>, abort, report error
```

Confirm both commands succeeded before continuing.

### Step 8 — Resolve design routing and SHA baseline

Read routing config (3-layer cascade) for `design` artifact:

**Layer 1 (global default — `~/.claude/CLAUDE.md`):**
```bash
grep -A 5 "^## Routing$" "$HOME/.claude/CLAUDE.md" 2>/dev/null \
  | grep "^\*\*Default destination:\*\*" | sed 's/\*\*Default destination:\*\* *//'
```
Valid values: `workspace` or `project`. Anything else: warn, treat as absent.

**Layer 2 (workspace per-artifact — `$WORKSPACE/CLAUDE.md`):**
```bash
grep -A 30 "^## Routing$" "$WORKSPACE/CLAUDE.md" 2>/dev/null
```
Parse the markdown table for a `design` row. Valid values: `workspace`, `project`.

Layer 2 overrides Layer 1. If neither present: default is `project`.

Apply resolved routing:
- If `design → workspace`: `DESIGN_REPO="$WORKSPACE"`, baseline = `git -C "$WORKSPACE" rev-parse main`, `DESIGN_REPO_KEY=workspace`
- If `design → project` (default): `DESIGN_REPO="$PROJECT"`, baseline = `git -C "$PROJECT" rev-parse HEAD`, `DESIGN_REPO_KEY=project`

`DESIGN_REPO_KEY` is stored in `.meta` so work-end can recover it without re-deriving
from routing config — which may have changed between sessions.

Compute section hashes (single pipe-separated line):
```bash
HASHES=$(grep "^## " "$DESIGN_REPO/DESIGN.md" 2>/dev/null \
  | while read h; do printf "%s:%s|" "$(printf '%s' "$h" | shasum -a 256 | cut -c1-8)" "$h"; done)
```
Leave blank if `$DESIGN_REPO/DESIGN.md` does not exist yet.

### Step 9 — Scaffold

```bash
mkdir -p "$WORKSPACE/design"
```

Write `$WORKSPACE/design/JOURNAL.md`:
```markdown
# Design Journal — <branch-name>
```

Write `$WORKSPACE/design/.meta`:
```
branch: <branch-name>
project-sha: <baseline SHA from Step 8>
date: <YYYY-MM-DD>
issue: <N or blank>
flyway-next-v: <N | none | unknown>
design-repo: <workspace | project>
design-section-hashes: <pipe-separated hash:heading pairs, or blank>
```

### Step 10 — Commit and push scaffold

```bash
git -C "$WORKSPACE" add design/JOURNAL.md design/.meta
git -C "$WORKSPACE" commit -m "init(<branch-name>): scaffold workspace branch"
git -C "$WORKSPACE" push  # non-fatal if fails; warn and continue
```

### Step 11 — IntelliJ MCPs

Call `mcp__intellij-index__ide_index_status` and `mcp__intellij__get_project_modules`.

**If either is unavailable:**
- Stop immediately — tell the user which MCP is missing
- Do not proceed with any semantic operation
- Do not fall back to bash, grep, or sed as substitutes
- Wait for the user to reconnect via `/mcp`

IntelliJ can also drop mid-task. If a semantic operation fails because an MCP
is unavailable at any point, stop and tell the user rather than silently falling back.

### Step 12 — Offer brainstorming

> "Start a brainstorm? (y/n)"

If yes: invoke `superpowers:brainstorming`. Specs write to `$WORKSPACE/specs/<branch-name>/`.
Specs always route to `project` (`$PROJECT/docs/specs/`) at close — the three-layer
cascade covers blog/adr/snapshots/plans/design only.

---

## Resume Path (Detection state 2)

Surface `.meta`:
```
⚡ Resuming: <branch-name>  Issue: #<N>  Started: <date>
   Flyway V: <N | none | unknown>
   Project: <branch>  Workspace: <branch>
```

Run Steps 0, 2, 3, 11 only. Skip all branch creation steps.

---

## Done — Report

```
work-start complete.
Branch: <branch-name>  Issue: #<N>
Platform doc: [read / not found]
Coherence Protocol: [any concerns raised, or "clear"]
Protocols checked: [list any relevant ones read]
IntelliJ: ✅ both connected / ⚠️ [missing — stopped]

Proceeding to brainstorming.  (or: Ready for work.)
```
