# Handover — 2026-04-07

**Head commit:** `22a31aa` — docs: add project blog entry 2026-04-07-mdp03-hortora-garden-grows-up
**Previous handover:** `git show HEAD~1:HANDOVER.md` | diff: `git diff HEAD~1 HEAD -- HANDOVER.md`

## What Changed This Session

- **Hortora designed** — complete vision document for the governed, federated knowledge garden; 3,300 lines, 10 embedded diagrams, committed at `696ed44`
- **Name validated** — Hortora (hortus + -ora); three rounds of independent validation; Grok's pick Sylvara rejected (sylvara.ai is a live AI agency)
- **Design spec covers:** v2 filesystem structure, 3-tier retrieval, three-level deduplication, quality lifecycle (Active→Suspected→Superseded→Retired), GitHub backend with CI, federation protocol (canonical/child/peer with augmentation + watch CI), 9-phase implementation roadmap, competitive landscape
- **Garden submissions:** GE-0091 (validate_document.py false positive in fenced blocks), GE-0092 (Playwright .all() vs .nth() for multi-element screenshots)
- **Design snapshot and blog entry** committed

## State Right Now

- `main` clean, everything committed and pushed
- Garden: drift counter now at 33 (threshold 10) — DEDUPE overdue, run before next merge
- Open issue: #36 (Design project memory architecture) — this session delivered the design; implementation not started

## Immediate Next Steps

1. **Register now** — `hortora-org` GitHub org; `hortora.garden`, `hortora.dev`, `hortora.com` — window may be short
2. **Phase 1** — migrate 78 garden entries to v2 structure; see Phase 1 Scope checklist in design spec
3. **Create issues/epics** — `mdproctor/knowledge-garden` for platform work; `mdproctor/cc-praxis` for skill updates

## Open Questions

- Open protocol vs. Claude-specific — must resolve before first public canonical garden launches
- GitHub org name — `hortora` or `hortora-org`?
- cc-praxis garden skill — thin stub pointing to hortora-engine, or full migration?
- Phase 2 sequencing — GitHub backend immediately after Phase 1, or deepen Phase 1 first?

## References

| Context | Where | Retrieve with |
|---------|-------|---------------|
| Design spec (complete) | `docs/superpowers/specs/2026-04-07-garden-rag-redesign-design.md` | `cat` |
| Design snapshot | `docs/design-snapshots/2026-04-07-hortora-knowledge-garden-design.md` | `cat` |
| Blog entry | `docs/blog/2026-04-07-mdp03-hortora-garden-grows-up.md` | `cat` |
| Diagram HTML sources | `docs/visuals/garden-diagrams.html`, `docs/visuals/garden-small-visuals.html` | browser |
| ADR-0011 (foundational pattern) | `docs/adr/0011-index-and-lazy-reference-pattern.md` | `cat` |
| Previous handover | git history | `git show HEAD~1:HANDOVER.md` |
