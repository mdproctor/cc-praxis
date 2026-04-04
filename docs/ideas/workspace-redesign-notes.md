# Workspace Redesign — Design Notes

*Running notes for the workspace redesign conversation. Updated as we go.*

---

## Core Concept (session 2026-04-04)

Replace the current model (content scattered in project repos + `~/claude/knowledge-garden/`) with a two-workspace model:

- **Private workspace** — global, personal, not committed to any project repo
- **Public workspace** — global, shareable/publishable

All content-creating skills (`idea-log`, `session-handoff`, `design-snapshot`, `garden`, `adr`, `project-blog`) should work *from within* these workspaces rather than inside individual project repos.

---

## Starting Point: What Exists Today

| Skill | Where content lives today |
|-------|--------------------------|
| `garden` | `~/claude/knowledge-garden/` — already global, its own git repo |
| `session-handoff` | `HANDOVER.md` in project repo; references garden globally |
| `idea-log` | `docs/ideas/IDEAS.md` in project repo |
| `design-snapshot` | `docs/design-snapshots/` in project repo |
| `adr` | `docs/adr/` in project repo |
| `project-blog` | `docs/project-blog/` in project repo |

The `garden` already established the `~/claude/` precedent. Others don't follow it yet.

---

## Open Questions (to resolve as we go)

- Where exactly do the workspace repos live locally? (`~/workspaces/`?)
- Does `writing-style/` get its own repo as a subtree, or is it just a folder in private-workspace?
- Which skills write where — mapping each skill to its workspace target folder
- What happens to existing per-project `docs/` content — migrated or coexisting?

---

## Structure

```
workspaces/
  private-workspace/           ← git repo (GitHub: private)
    writing-style/             ← permanently private, not a subtree
    cc-praxis-workspace/       ← git subtree → own GitHub repo
    <other-project>-workspace/ ← git subtree → own GitHub repo
  public-workspace/            ← git repo (GitHub: public)
    garden/                    ← git subtree → own GitHub repo (replaces ~/claude/knowledge-garden/)
    cc-praxis-workspace/       ← git subtree → own GitHub repo (if public)
    <other-project>-workspace/ ← git subtree → own GitHub repo (if public)
```

**Subtree model:**
- Each `<project>-workspace/` is its own GitHub repo AND a subtree of the workspace repo
- Global view: open workspace repo to see all projects together
- Isolated view: each companion repo is independently cloneable/pushable
- Commit to workspace repo; use `git subtree push` to sync back to companion repo
- A project workspace lives in either private OR public workspace, not both
- Garden also becomes a subtree of public-workspace (replaces standalone `~/claude/knowledge-garden/`)

---

## Decisions Made

- **All work stays in the workspace — nothing written to project repos during development**
  - `idea-log`, `session-handoff`, `design-snapshot`, `project-blog`, `adr` — all go to workspace
  - Project repos stay clean of WIP methodology noise
  - Workspace is the working surface; project repo is the destination

- **Promotion to project repo happens at natural completion points — not during development**
  - Trigger: explicit user decision — at PR merge, epic close, or any other time
  - No automatic or prompted promotion — user decides what moves and when
  - Guiding principle: keep target repos free of WIP noise
  - What promotes: ADRs confirmed so far; potentially others at epic close
  - What stays in workspace forever: handoffs, blog entries, snapshots (record of journey, not useful to other contributors)

- **Both workspaces are git repos backed up to GitHub**
  - Private workspace → private GitHub repo
  - Public workspace → public GitHub repo
  - Neither is ephemeral; both are durable, versioned, and remote-backed

- **Private → public promotion is optional, not automatic**
  - Some content can move from private to public when ready (ideas, ADRs, blog entries)
  - Some content is permanently private by nature (e.g. writing style guide, personal preferences)
  - The private workspace is not a staging area — it's a permanent home for some content

---

## Implementation Tasks (for final implementation doc)

- [ ] Rename `knowledge-garden` → `garden` everywhere: skill name, directory (`~/claude/knowledge-garden/` → new workspace path), all references in other skills, CLAUDE.md, README.md, docs/

---

## Key Tensions to Resolve

- Some content is inherently project-specific (design snapshot for a specific codebase)
  vs cross-project (knowledge garden gotchas). Workspaces need to handle both.
- Public workspace implies curation — not everything in private should auto-publish.
- Session handoff is ephemeral/operational; design snapshots are archival.
  Do they belong in the same workspace?
