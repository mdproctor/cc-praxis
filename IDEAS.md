# Idea Log

Undecided possibilities — things worth remembering but not yet decided.
Promote to an ADR when ready to decide; discard when no longer relevant.

---

## 2026-04-13 — Blog entry types: article vs. note, with routing metadata

**Priority:** medium
**Status:** active

Differentiate write-blog output into two types: `note` (current diary/journal
entries — session narrative, informal) and `article` (traditional topic or
summary post — polished, standalone readable). Each entry carries metadata
declaring target destinations: project blog, author's personal blog, one or
more group/syndication blogs. Cross-posting to multiple targets is supported.
Routing strategy at epic close: notes go to the project repo; articles route
per their metadata targets.

**Context:** Surfaced during brainstorm on DESIGN.md interaction model.
The current write-blog skill only produces diary-style notes. Articles serve
a different audience and need different routing — author blogs, group blogs,
and syndication targets beyond the project repo.

**Promoted to:**
