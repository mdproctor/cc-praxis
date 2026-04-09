# Workspace Model — Critical Analysis

**Date:** 2026-04-09
**Related spec:** `2026-04-09-workspace-model-design.md`
**Status:** All major concerns resolved — see resolution notes per problem

---

## Summary

The original design made the workspace the CWD but kept project as the place to
open Claude — then tried the reverse. Both had problems. The resolved design:

- **CWD = workspace** (all skills write here universally, including third-party)
- **CLAUDE.md symlink** in project (gitignored via `.git/info/exclude`)
- **`add-dir` instruction** in workspace CLAUDE.md (session-start, not manual)
- **`workspace-init`** generates the routing CLAUDE.md that wires everything up

---

## Problem 1 — "Always Open In Workspace" Is Unenforceable

**Original concern:** No enforcement, IDE integration fights you, muscle memory
fights you. One wrong open = drift.

**Resolution:** The CLAUDE.md symlink in the project means opening in the project
directory is a safe fallback — you still get full project config. It's not ideal
(skills write to project CWD) but it doesn't cause silent drift of methodology
artifacts because the workspace CLAUDE.md's routing table is what redirects
output. If someone opens in the project regularly they'll notice things aren't
going to the workspace; the symlink doesn't make the wrong behavior invisible.

The discipline is still preferred, but the failure mode is visible and recoverable.

**Status:** ✅ Substantially mitigated

---

## Problem 2 — Project CLAUDE.md Not Auto-Loaded

**Original concern:** CWD = workspace → workspace CLAUDE.md loads, not project's.
Project type, build commands, conventions all invisible.

**Resolution:** The workspace CLAUDE.md IS the project CLAUDE.md — same file via
symlink. It contains all project config (type, build commands, conventions) AND
workspace routing config. One file, two access paths.

**Status:** ✅ Solved

---

## Problem 3 — `add-dir` Every Session

**Original concern:** `add-dir` doesn't persist, requires manual typing every
session.

**Resolution:** Workspace CLAUDE.md contains a `## Session Start` section:

```markdown
## Session Start
Run `add-dir /absolute/path/to/project` before any other work.
```

Claude reads CLAUDE.md on open and follows it. Effectively automatic.

**Status:** ✅ Solved

---

## Problem 4 — Every Git Command In Every Skill Breaks

**Original concern:** If CWD = workspace, `git log`, `git add`, `git commit`
operate on the workspace repo, not the project.

**Resolution:** Skills that do code git operations use the project path from
CLAUDE.md. This is a real change to skills — they need to qualify project git
commands. However, this is limited to skills that do coding git work
(`git-commit`, `java-git-commit`, etc.). Methodology skills (handover,
idea-log, adr, etc.) commit to the workspace, which IS the CWD — no change
needed for those.

The coding-focused skills need to read the project path from CLAUDE.md for
git operations. This is explicit rather than implicit, which is arguably clearer.

**Status:** ⚠️ Partially resolved — coding skills need project-path-aware git
commands. Contained to git-commit family, not all skills.

---

## Problem 5 — Two Git Repos, Cognitive Split

**Original concern:** Two repos, two `git log`, two branch states, easy to
lose track of which is which.

**Resolution:** Workspace commits are deliberate — skills explicitly commit to
workspace. Project commits are normal CWD operations. The split is real but
intentional. Branch mirroring is a documented convention; enforcement via hook
is deferred.

**Status:** ⚠️ Accepted — managed complexity, not eliminated

---

## Problem 6 — Design Conflates Two Separate Concerns

**Original concern:** "Claude opens in workspace" bundled WHERE Claude works
with WHERE artifacts are stored.

**Resolution:** The symlink approach separates them cleanly. Workspace is
artifact storage. Project is accessible via add-dir. Workspace CLAUDE.md is
the routing config that connects them. Concerns are separated.

**Status:** ✅ Solved

---

## Problem 7 — Git Worktrees Not Addressed

**Original concern:** Project worktrees don't automatically get matching
workspace branches.

**Resolution:** Documented as a manual convention — when creating a project
worktree, also branch the workspace. A post-checkout hook that warns about
branch mismatch is future work.

**Status:** 🔜 Deferred — convention documented, hook enforcement future work

---

## Problem 8 — Parent `~/claude/` Repo Can't See Child History

**Original concern:** Nested git repos, parent can't track child commits without
submodules (rejected).

**Resolution:** By design. Parent lists `private/` and `public/` by filesystem,
discovers workspaces, reads their files directly. Parent's own commits are
cross-workspace artifacts only. This is the intended model, not a defect.

**Status:** ✅ By design

---

## Problem 9 — Quick Tasks Are Expensive

**Original concern:** Quick `cd project && claude` becomes
navigate-to-workspace → open → add-dir → ask.

**Resolution:** The CLAUDE.md symlink means `cd project && claude` still works
and loads full project config. For quick tasks where you don't need workspace
artifacts, this is fine. For sessions where you'll write artifacts, opening in
the workspace is preferred but the CLAUDE.md symlink makes the project a
viable entry point.

**Status:** ✅ Substantially mitigated

---

## The Third-Party Skill Problem (New — Key Insight)

**Concern surfaced during analysis:** Third-party skills (superpowers brainstorming,
writing-plans, any future skill) write to CWD-relative paths. If CWD = project,
they pollute the project repo. Only skills that explicitly support path overrides
can be redirected via CLAUDE.md — we can't guarantee future skills have this.

**Resolution:** CWD = workspace means ALL skills write to workspace by default,
universally, regardless of whether they support path overrides. This is the
strongest argument for workspace-as-CWD and the reason the "project-as-CWD with
overrides" approach was rejected.

Superpowers skills additionally support CLAUDE.md path overrides as
belt-and-suspenders. Future third-party skills that don't support overrides
still land correctly because CWD is the workspace.

**Status:** ✅ Solved — this is the primary reason CWD = workspace

---

## Remaining Open Issue

**Git-commit family of skills** need to qualify project git operations with the
project path from CLAUDE.md. This is real implementation work and a genuine
change to how those skills operate. Contained to coding-workflow skills, not
methodology skills. Acceptable for first iteration.
