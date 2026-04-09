# Workspace Model — Design Spec

**Date:** 2026-04-09
**Status:** Approved — pending implementation plan update

---

## Problem

All cc-praxis skills currently write methodology artifacts (handovers, snapshots,
ADRs, idea-log, blog entries) directly into the project repo. Third-party skills
(superpowers brainstorming, writing-plans) do the same. This creates two problems:

1. **Noise in project history** — WIP artifacts pollute the main repo with
   mid-epic methodology churn that other contributors don't need to see.
2. **Co-worker friction** — multiple developers working the same epic have no
   clean way to maintain independent working contexts and reconcile at integration time.

The knowledge garden already lives outside project repos at
`~/claude/knowledge-garden/`. This design extends that principle to all
methodology artifacts, including third-party skill output.

---

## Core Principle

**The workspace is the working surface for all methodology documents related to
a project. Project repos only receive finished, deliberate output.**

---

## Structure

```
~/projects/drools/               ← PROJECT REPO (code, gitignored CLAUDE.md symlink)
  CLAUDE.md → ~/claude/private/drools/CLAUDE.md   (symlink, never committed)
  src/...

~/claude/
  private/
    cc-praxis/                   ← WORKSPACE (methodology artifacts)
      CLAUDE.md                  ← source of truth; routing hub for all skills
      HANDOVER.md                ← session handover (single file)
      IDEAS.md                   ← idea log (single file, for now)
      specs/                     ← brainstorming/design specs (superpowers output)
      plans/                     ← implementation plans (superpowers output)
      snapshots/                 ← design snapshots + INDEX.md (auto-pruned, max 10)
      adr/                       ← ADRs + INDEX.md
      blog/                      ← blog entries + INDEX.md
      design/
        DESIGN.md                ← single living design doc; git is the delta history
    drools/
  public/
    cc-praxis/                   ← PUBLIC WORKSPACE (if project is public)
  knowledge-garden/              ← unchanged (first iteration)
```

A project workspace lives in either `private/` or `public/` — not both.

---

## How Claude Works With the Workspace

**Claude opens in the workspace. The workspace CLAUDE.md instructs Claude to
add the project repo at session start.**

```
Working directory:  ~/claude/private/<project>/
Project access:     add-dir /absolute/path/to/project   (instructed by CLAUDE.md)
```

The workspace CLAUDE.md contains `## Session Start` with the `add-dir` command.
Claude reads this on open and runs it before any other work. No manual step required.

**Why workspace as CWD, not project:**
All skills — cc-praxis, superpowers, and any future third-party skill — write
artifacts relative to CWD by default. If CWD is the workspace, all artifact
output lands in the workspace universally, with no per-skill configuration needed.
If CWD were the project, only skills that explicitly support path overrides could
be redirected; skills without that mechanism would still pollute the project repo.

---

## The CLAUDE.md Symlink

Each project has a gitignored `CLAUDE.md` symlink pointing to its workspace CLAUDE.md:

```bash
~/projects/drools/CLAUDE.md → ~/claude/private/drools/CLAUDE.md
```

**Why:**
- If someone opens Claude in the project directory (mistake, or IDE integration),
  they still get full project config — project type, build commands, conventions
- The symlink is the project's CLAUDE.md in content, but lives in the workspace
- One source of truth — no sync required

**Gitignore mechanism:**
Never touch the project's tracked `.gitignore`. Always use `.git/info/exclude`:

```bash
echo "CLAUDE.md" >> /path/to/project/.git/info/exclude
```

This is:
- Local-only (never committed, never shared)
- Works for projects you own and projects you don't (Drools, upstream repos)
- Consistent — workspace-init always does this, no decisions required

---

## Workspace CLAUDE.md — The Routing Hub

The workspace CLAUDE.md is the configuration that makes everything work.
`workspace-init` generates it. It contains:

```markdown
# <project> Workspace

**Project repo:** /absolute/path/to/project
**Workspace type:** private | public

## Session Start

Run `add-dir /absolute/path/to/project` before any other work.

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

## Rules
- All methodology artifacts go here, not in the project repo
- Promotion to project repo is always explicit — never automatic
- Workspace branches mirror project branches — switch both together
```

New skills that support path overrides get a new row in the table and a new
directory. `workspace-init` is the living registry of where things go.

---

## Design Document Lifecycle (`design/DESIGN.md`)

`design/DESIGN.md` is a single living working copy of the project's design
document. **Git is the delta** — individual changes are not stored as separate
files; every commit is implicitly a delta. Same principle as `HANDOVER.md`.

**Lifecycle:**

1. **`workspace-init`** — copies the project's `DESIGN.md` into
   `workspace/design/DESIGN.md` as the starting point. If the project has no
   `DESIGN.md`, creates an empty stub.
2. **During the epic** — `java-update-design`, `update-primary-doc`, and any
   design-producing skill write to `workspace/design/DESIGN.md`. The project's
   `DESIGN.md` is untouched during active development.
3. **Epic close** — Claude merges `workspace/design/DESIGN.md` back into the
   project's `DESIGN.md`. This is a single merge of two documents — Claude reads
   both and produces a coherent current-state document, resolving any
   contradictions. Explicit, user-confirmed, not automatic.

**Why one file:** Multiple delta files would require a complex ordered merge at
epic close. One file with git history gives the same audit trail at zero merge
complexity. `git log -- design/DESIGN.md` shows every change; the file itself
always reflects current intent.

**Migration:** Existing projects with design artifacts scattered in `docs/`
(design-snapshots, ADRs, DESIGN.md) need systematic migration to workspace.
See migration task in the implementation plan.

---

## Parent Workspace (`~/claude/`)

A git repo for cross-workspace operations:

- Discovers all project workspaces by listing `private/` and `public/`
- Parent Claude opens in `~/claude/`, uses `add-dir` for specific workspaces
- Stores cross-workspace artifacts: aggregated diary, cross-project notes,
  cross-project dependency ordering
- Each project workspace is its own git repo — commits don't appear in parent

---

## Session-Start Hook

The existing `check_project_setup.sh` hook is extended to cover workspace setup.
Hook checks run in order and stop at the first actionable item. Each check fires
**once** — after setup, it goes quiet permanently.

```
1. In a git repo?                     → if not, exit silently
2. CLAUDE.md + project type?          → if missing, prompt to create (existing behaviour)
3. HANDOVER.md found?                 → "Read your session handover? (y/n)"
                                         if >7 days old, flag as potentially stale
4. Workspace configured?              → if not, offer /workspace-init
5. Workspace branch ≠ project branch? → warn, suggest switching
6. Work Tracking in CLAUDE.md?        → if missing, suggest /issue-workflow (existing behaviour)
```

**Pattern:** Hook = one-time setup nudge. Ongoing behaviour = CLAUDE.md instructions
(always auto-loaded). Once configured, the hook goes quiet; CLAUDE.md drives
the session behaviour.

**Harvesting is excluded** — garden submissions are merged in a dedicated Claude
session with full context budget, not surfaced at project session start.

---

## Co-Worker Model

Each workspace is a git repo backed by GitHub (private or public):

- Co-workers clone to the same path convention: `~/claude/private/<project>/`
- Branch-per-epic: workspace branch mirrors the project code branch
- At epic close: PR and merge workspace branch — same process as code
- Design doc conflicts: ask Claude to synthesise both versions (human-directed)

---

## Knowledge Routing — Keeping Handover Lean

| Knowledge type | Goes to |
|---------------|---------|
| Technical discoveries | Garden — per-session sweep |
| Significant decisions | ADR — immediately |
| Process changes | CLAUDE.md |
| Everything else | Discard — git history preserves it |

If HANDOVER.md is growing fat, routing is failing mid-epic.
Epic close should be cleanup, not archaeology.

---

## Skills Affected (First Iteration)

| Skill | Change |
|-------|--------|
| `handover` | Already writes to CWD — no path change needed |
| `idea-log` | `docs/ideas/IDEAS.md` → `IDEAS.md` in CWD |
| `design-snapshot` | `docs/design-snapshots/` → `snapshots/` in CWD |
| `adr` | `docs/adr/` → `adr/` in CWD |
| `write-blog` | `docs/blog/` → `blog/` in CWD |
| `garden` | **Unchanged** (first iteration) |
| `workspace-init` | **New skill** — creates full workspace, generates routing CLAUDE.md, creates project symlink, writes .git/info/exclude |

**Superpowers skills** (brainstorming, writing-plans): write to CWD by default,
which is the workspace. Existing path override support in their CLAUDE.md
instructions (`specs/`, `plans/`) is belt-and-suspenders.

---

## Snapshot Auto-Pruning

When snapshot count exceeds configurable limit (default: 10):
- Oldest snapshot removed from disk
- Each snapshot references its predecessor for git chain navigation
- Git history retains all snapshots indefinitely

---

## Open Questions / Deferred

| Topic | Status |
|-------|--------|
| `design/` folder format | ✅ Resolved — single `DESIGN.md`, git is the delta |
| Git worktrees | Deferred — document convention (branch workspace with project), enforcement via hook is future work |
| `GARDEN.md` → `INDEX.md` rename | Deferred |
| Garden merge trigger | Deferred |
| `knowledge-garden/` relocation | Deferred |

---

## Out of Scope (This Iteration)

- Agent Teams integration for parent Claude
- Epic-close workflow skill (though the design lifecycle section describes the merge)

## Migration (Separate Task)

Existing projects have design artifacts in `docs/` within the project repo.
These need systematic migration to workspace directories:

| Artifact | Current location | Workspace location |
|----------|-----------------|-------------------|
| Design snapshots | `docs/design-snapshots/` | `snapshots/` |
| ADRs | `docs/adr/` | `adr/` |
| Blog entries | `docs/blog/` | `blog/` |
| Ideas | `docs/ideas/IDEAS.md` | `IDEAS.md` |
| Specs | `docs/superpowers/specs/` | `specs/` |
| Plans | `docs/superpowers/plans/` | `plans/` |
| DESIGN.md | project root | `design/DESIGN.md` (working copy) |

Migration is per-project, run once when `workspace-init` is first run on an
existing project. `workspace-init` should detect existing `docs/` artifacts
and offer to migrate them.
