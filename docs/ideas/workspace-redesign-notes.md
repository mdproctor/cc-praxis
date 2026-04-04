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

- Where exactly do the private and public workspaces live? (`~/claude/private/`? `~/workspace/`?)
- What is the relationship between a workspace and a project? (workspace *contains* projects? workspace is *alongside* projects?)
- Does content move between private → public, or are they separate from creation?
- What happens to existing per-project `docs/` content — migrated or coexisting?
- Which skills write to private, which to public, which to both?

---

## Structure

```
private-workspace/          ← private GitHub repo
  cc-praxis-workspace/      ← content for cc-praxis project (if private)
  my-other-project-workspace/
  writing-style/            ← permanently private, not project-specific

public-workspace/           ← public GitHub repo
  cc-praxis-workspace/      ← content for cc-praxis project (if public)
  my-other-project-workspace/
```

- Each project gets a `<project>-workspace/` folder
- A project's workspace lives in **either** private **or** public — not both (for now)
- The choice of private vs public is made per project
- Non-project content (e.g. writing style) lives directly in the private workspace

---

## Decisions Made

- **Both workspaces are git repos backed up to GitHub**
  - Private workspace → private GitHub repo
  - Public workspace → public GitHub repo
  - Neither is ephemeral; both are durable, versioned, and remote-backed

- **Private → public promotion is optional, not automatic**
  - Some content can move from private to public when ready (ideas, ADRs, blog entries)
  - Some content is permanently private by nature (e.g. writing style guide, personal preferences)
  - The private workspace is not a staging area — it's a permanent home for some content

---

## Key Tensions to Resolve

- Some content is inherently project-specific (design snapshot for a specific codebase)
  vs cross-project (knowledge garden gotchas). Workspaces need to handle both.
- Public workspace implies curation — not everything in private should auto-publish.
- Session handoff is ephemeral/operational; design snapshots are archival.
  Do they belong in the same workspace?
