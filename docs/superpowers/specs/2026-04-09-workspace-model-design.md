# Workspace Model — Design Spec

**Date:** 2026-04-09
**Status:** Approved — pending implementation plan

---

## Problem

All cc-praxis skills currently write methodology artifacts (handovers, snapshots,
ADRs, idea-log, blog entries) directly into the project repo. This creates two
problems:

1. **Noise in project history** — WIP artifacts pollute the main repo with
   mid-epic methodology churn that other contributors don't need to see.
2. **Co-worker friction** — multiple developers working the same epic have no
   clean way to maintain independent working contexts and reconcile at integration time.

The knowledge garden already lives outside project repos at
`~/claude/knowledge-garden/`. This design extends that principle to all
methodology artifacts.

---

## Core Principle

**The workspace is the working surface for all methodology documents related to
a project. Project repos only receive finished, deliberate output.**

---

## Structure

```
~/projects/cc-praxis/            ← PROJECT REPO (code, CLAUDE.md, etc.)

~/claude/
  private/
    cc-praxis/                   ← WORKSPACE (methodology artifacts)
      CLAUDE.md                  ← workspace config + absolute path to project
      HANDOVER.md                ← session handover (single file)
      IDEAS.md                   ← idea log (single file, for now)
      snapshots/                 ← design snapshots + INDEX.md (auto-pruned, default 10)
      adr/                       ← ADRs + INDEX.md
      blog/                      ← blog entries + INDEX.md
      design/                    ← not in first iteration (see Open Questions)
    other-project/
  public/
    cc-praxis/                   ← PUBLIC WORKSPACE (if project is public)
    other-project/
  knowledge-garden/              ← unchanged (first iteration)
```

A project workspace lives in either `private/` or `public/` — not both.

---

## How Claude Works With the Workspace

**Claude always opens in the workspace, never in the project repo.**

- Working directory: `~/claude/private/<project>/` (or `public/`)
- Project repo accessible via: `add-dir ~/projects/<project>/`
- Workspace `CLAUDE.md` contains the absolute project path — skills use this
  when they need to read or write to the project repo

No symlink at the project root is needed. The workspace is the CWD; the project
is a named directory Claude can reach.

---

## Workspace CLAUDE.md

The workspace `CLAUDE.md` is a behavioral rulebook, not just an orientation doc:

```markdown
# <Project> Workspace

**Project repo:** /absolute/path/to/<project>/
**Workspace type:** private | public

## Structure
- HANDOVER.md — session handover
- IDEAS.md — idea log
- snapshots/ — design snapshots (max 10, auto-pruned)
- adr/ — architecture decision records
- blog/ — project diary entries

## Rules
- Always read HANDOVER.md at session start
- All methodology artifacts go here, not in the project repo
- Promotion to project repo is always explicit — never automatic
```

---

## Parent Workspace (`~/claude/`)

A git repo for cross-workspace operations:

- Discovers all project workspaces by listing `private/` and `public/` — no
  registry file or submodules needed
- Parent Claude opens in `~/claude/`, uses `add-dir` for specific project
  workspaces when doing cross-workspace work
- Stores cross-workspace artifacts: aggregated diary entries, cross-project notes,
  cross-project dependency ordering
- Each project workspace is its own git repo — their commits do not appear in
  the parent's history

---

## Co-Worker Model

Each workspace is a git repo backed by GitHub (private or public):

- Co-workers clone to the same path convention: `~/claude/private/<project>/`
- Branch-per-epic: workspace branch mirrors the project code branch
- Developers work independently on their local clone
- At epic close: PR and merge the workspace branch — same process as code
- Design doc conflicts resolved by asking Claude to synthesise both versions
  into a coherent document (human-directed, no automated merge skill needed)

---

## Knowledge Routing — Keeping Handover Lean

The handover skill already runs a garden sweep per session. The discipline to
enforce:

| Knowledge type | Goes to |
|---------------|---------|
| Technical discoveries | Garden — per-session sweep |
| Significant decisions | ADR — immediately, not at epic close |
| Process changes | CLAUDE.md |
| Everything else | Discard — git history preserves it |

**If HANDOVER.md is growing fat with general knowledge, routing is failing
mid-epic.** Epic close should be cleanup, not archaeology.

---

## Skills Affected (First Iteration)

| Skill | Change |
|-------|--------|
| `handover` | Write to `HANDOVER.md` in CWD (workspace), not project root |
| `idea-log` | Write to `IDEAS.md` in CWD, not `docs/ideas/` |
| `design-snapshot` | Write to `snapshots/` in CWD, not `docs/design-snapshots/` |
| `adr` | Write to `adr/` in CWD, not `docs/adr/` |
| `write-blog` | Write to `blog/` in CWD, not `docs/blog/` |
| `garden` | **Unchanged** (first iteration) |
| `workspace-init` | **New skill** — creates workspace structure, CLAUDE.md, git repo, GitHub remote |

Promotion to the project repo (e.g. ADRs at epic close) is always explicit
and user-directed — no skill auto-promotes anything.

---

## Snapshot Auto-Pruning

When snapshot count exceeds the configurable limit (default: 10):
- Oldest snapshot removed from disk
- Each snapshot references its predecessor for git chain navigation
- Git history retains all snapshots indefinitely

---

## Open Questions / Deferred

| Topic | Status |
|-------|--------|
| `design/` folder format | Deferred — single `DESIGN-DELTA.md` vs per-issue files unresolved |
| `GARDEN.md` → `INDEX.md` rename | Deferred to later iteration |
| Garden merge trigger (session-start hook) | Deferred to later iteration |
| `knowledge-garden/` relocation to `public/garden/` | Deferred to later iteration |

---

## Out of Scope (This Iteration)

- Automated design doc merge tooling — handled by asking Claude directly
- Agent Teams integration for parent Claude cross-workspace operations
- `design/` folder — blocked on issue-scoping question
