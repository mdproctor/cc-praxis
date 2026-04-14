# Epic Lifecycle — Design Spec

**Date:** 2026-04-14
**Status:** Approved
**Issue:** mdproctor/cc-praxis#49

---

## Problem

The workspace model defines `epic-start` and `epic-close` as the skills that
open and close the workspace branch lifecycle. Their workflows were outlined
in the original spec but not fully designed — especially in light of two new
specs written 2026-04-13:

- `2026-04-13-design-journal-design.md` — `JOURNAL.md` replaces full-copy
  `DESIGN.md` model; epic-start must scaffold it and record the project SHA
- `2026-04-13-artifact-routing-design.md` — declarative routing config;
  epic-close must read and apply it

This spec defines the complete workflow for both skills.

---

## epic-start

### Inputs

- Epic name (e.g. `epic-payments`)

### Workflow

**Step 1 — Create branches**

```bash
git -C <project> checkout -b <epic-name>
git -C <workspace> checkout -b <epic-name>
```

**Step 2 — Scaffold workspace**

Create `design/JOURNAL.md` stub:

```markdown
# Design Journal — <epic-name>
```

Create `design/.meta`:

```
epic: <epic-name>
project-sha: <git -C <project> rev-parse HEAD>
date: <today>
issue:
```

**Step 3 — GitHub issue**

If issue tracking is enabled in workspace CLAUDE.md:
- Search for an existing open issue matching the epic name
- If found → use it; record issue number in `design/.meta`
- If not found → offer to create one; if accepted, create and record number

If issue tracking is not enabled → skip silently.

**Step 4 — Brainstorming**

Prompt: *"Start a brainstorm for this epic? (y/n)"*

- Yes → invoke `brainstorming` skill
- No → done; user proceeds manually

### Success Criteria

- [ ] Project branch created
- [ ] Workspace branch created with matching name
- [ ] `design/JOURNAL.md` stub exists
- [ ] `design/.meta` exists with epic name, project SHA, date
- [ ] Issue number recorded in `design/.meta` (if tracking enabled)

---

## epic-close

### Workflow

**Step 1 — Build the close plan**

Before presenting anything to the user, Claude assembles the full picture:

- Reads `design/.meta` → epic name, project SHA, issue number
- Reads `## Routing` from workspace CLAUDE.md → destination per artifact
- Lists contents of `adr/`, `blog/`, `snapshots/`, `specs/`, `design/JOURNAL.md`
- Generates journal merge preview (three-way: base at project SHA + current
  project `DESIGN.md` + `design/JOURNAL.md`)
- Asks user to select which spec(s) from `specs/` to post to the GitHub issue
  (one file per topic — no old versions)

**Step 2 — Present close plan**

```
Epic close plan — epic-payments

  Artifact routing
  ├── adr/0042-events.md        → ~/docs/team-wiki/adr/   [local git]
  ├── blog/2026-04-14-mp-...    → project repo
  └── design/JOURNAL.md         → project repo + GitHub issue #52

  Journal merge
  ├── §Architecture             updated (event-driven model)
  └── §Data Model               updated (status field added)

  GitHub issue #52
  ├── Post spec: 2026-04-13-design-journal-design.md
  └── Close issue

  Branch cleanup
  └── epic-payments (project + workspace) — prompt after

Approve all, or go step by step? (all / step)
```

**Step 3a — "all" path**

Executes all steps in order. On any failure: continues remaining steps,
reports at the end:

```
✅ ADR promoted → ~/docs/team-wiki/adr/
✅ Blog promoted → project repo
✅ Journal merged → project DESIGN.md
✅ Spec posted to #52, issue closed
❌ Push failed — ~/docs/team-wiki/ has no network. Push manually when ready.
```

Failed steps are logged with the manual resolution command. Successful
promotions are not rolled back.

**Step 3b — "step" path**

Three phases, one confirmation each:

- **Phase 1 — Artifact routing**
  Show what will be promoted where → user confirms → execute → report

- **Phase 2 — Journal merge**
  Show merge preview per `§Section` → user confirms → apply → post-merge
  verification (confirm each anchored section was addressed)

- **Phase 3 — GitHub + cleanup**
  Post selected spec(s) to issue → close issue → branch prompt (see Step 4)

**Step 4 — Branch cleanup** (both paths)

```
Delete epic-payments branches? (project + workspace)
  y → delete both, switch workspace and project to main
  n → keep both; mark epic as closed
```

If kept, create `EPIC-CLOSED.md` in workspace branch root:

```markdown
# Epic Closed — <epic-name>
**Date:** <today>
**Issue:** #<N>
**Status:** Closed — branch retained for inspection
```

### Edge Cases

| Situation | Behaviour |
|-----------|-----------|
| No `JOURNAL.md` entries | Skip journal merge step; note in summary |
| No files in `specs/` | Skip spec selection and posting step |
| No GitHub issue (tracking disabled) | Skip all GitHub steps silently |
| Destination path doesn't exist | Create it before promoting |
| Push fails (no network) | Report failure with manual resolution command; continue |

### Success Criteria

- [ ] All artifacts routed to declared destinations (or failures reported)
- [ ] Journal merged into project `DESIGN.md`, user confirmed
- [ ] Post-merge verification passed
- [ ] Selected spec(s) posted to GitHub issue
- [ ] Issue closed (if tracking enabled)
- [ ] Branch cleanup resolved — deleted or `EPIC-CLOSED.md` created
- [ ] Workspace and project both on `main`

---

## Skill Chaining

| Event | Skill | Chains to |
|-------|-------|-----------|
| User invokes `/epic-start` | `epic-start` | Optionally → `brainstorming` |
| User invokes `/epic-close` | `epic-close` | Reads routing config; invokes capability detection per destination |
| Design decision during epic | `java-update-design` / `update-primary-doc` | Writes to `design/JOURNAL.md` |
| Session end during epic | `handover` | Prompts for unjournalled design changes |

---

## Relation to Existing Specs

This spec supersedes the `Epic Lifecycle` section of
`2026-04-09-workspace-model-design.md`. Specifically:

- `design/DESIGN.md` → `design/JOURNAL.md` (see `2026-04-13-design-journal-design.md`)
- Artifact routing via `## Routing` in workspace CLAUDE.md (see `2026-04-13-artifact-routing-design.md`)
- Merge mechanic is three-way (base SHA + journal + current project) not two-way

---

## Out of Scope

- Blog article vs. note type differentiation and complex blog routing — see IDEAS.md; separate epic
- `workspace-init` — already specced and implemented
- Parent `~/claude/` workspace git repo setup — deferred
