# cc-praxis — Workspace Model Design Snapshot
**Date:** 2026-04-09
**Topic:** Workspace model — where Claude artifacts live and how they're accessed
**Supersedes:** *(none)*
**Superseded by:** *(leave blank — filled in if this snapshot is later superseded)*

---

## Where We Are

The workspace model is fully designed and documented, with an implementation plan written. The model moves all methodology artifacts (handovers, snapshots, ADRs, idea-log, blog, design docs) out of project repos and into companion workspace directories at `~/claude/private/<project>/` or `~/claude/public/<project>/`. Claude always opens in the workspace; the project is added via `add-dir` (instructed automatically by workspace CLAUDE.md). No implementation has been executed yet — this is design-complete, implementation-pending.

## How We Got Here

Key decisions made to reach the current design.

| Decision | Chosen | Why | Alternatives Rejected |
|---|---|---|---|
| Claude opens in workspace (CWD) | Workspace is CWD | Only way to make ALL skills (including third-party like superpowers) write to workspace universally | Project as CWD — third-party skills would still pollute the project repo |
| CLAUDE.md in project | Gitignored symlink → workspace CLAUDE.md | One source of truth; full project config loads regardless of where Claude opens | Copy (drift risk); no project CLAUDE.md (IDE integration breaks) |
| Gitignore mechanism | `.git/info/exclude` always | Local-only, never committed, works for upstream repos you don't own (Drools, any open source) | `.gitignore` — can't commit to it on projects you don't own |
| Parent workspace discovery | Filesystem listing of `~/claude/private/` and `~/claude/public/` | Always sees live state; no staleness | Git submodules — always stale between explicit syncs; designed for pinned-version dependencies, not live workspaces |
| `design/` folder format | Single `design/DESIGN.md`; git is the delta | No complex multi-document merge; same principle as HANDOVER.md — git history already IS the delta | Per-issue delta files — unnecessary overhead; accumulating deltas requires ordered merge at epic close |
| Co-worker model | Branch-per-epic in shared workspace GitHub repo | Reuses existing git collaboration knowledge | Per-developer separate repos — complex sync; submodules — staleness |

## Where We're Going

**Next steps:**
- Execute implementation plan — Task 1: `workspace-init` skill; Tasks 2–6: path updates to 5 skills; Task 7: hook extension (HANDOVER.md read prompt + workspace check); Task 8–10: metadata, CLAUDE.md/README, `java-update-design`/`update-primary-doc`
- After workspace-init exists: migrate existing cc-praxis artifacts from `docs/` to workspace
- Delete remote branch `claude/identify-non-coding-docs-vkAAd` — other Claude's design work absorbed into main

**Open questions:**
- Does Claude Code follow a CLAUDE.md **symlink** specifically for session initialisation? File access via symlinks is confirmed; CLAUDE.md auto-loading via symlink needs a quick empirical test before implementation starts
- Git worktrees: creating a project worktree does not automatically branch the workspace — convention documented, hook enforcement deferred
- Garden relocation (`~/claude/knowledge-garden/` → `~/claude/public/garden/`) — deferred to later iteration

## Linked ADRs

*(No ADRs created for workspace model decisions — all captured in spec and implementation plan)*

## Context Links

- Design spec: `docs/superpowers/specs/2026-04-09-workspace-model-design.md`
- Critique (resolved): `docs/superpowers/specs/2026-04-09-workspace-model-critique.md`
- Implementation plan: `docs/superpowers/plans/2026-04-09-workspace-model.md`
