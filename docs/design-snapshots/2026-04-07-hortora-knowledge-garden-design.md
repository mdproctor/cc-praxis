# Hortora — Design Snapshot
**Date:** 2026-04-07
**Topic:** Knowledge garden v2 redesign — architecture, federation, and brand
**Supersedes:** *(none — parallel to 2026-04-06-writing-infrastructure-and-garden.md)*
**Superseded by:** *(leave blank)*

---

## Where We Are

Hortora is the name for a governed, federated knowledge garden for AI coding assistants — capturing non-obvious technical knowledge (gotchas, techniques, undocumented behaviours) in structured markdown files, optimised for AI retrieval without vector databases. A comprehensive design specification (3,300+ lines) has been written covering the full architecture: v2 filesystem structure (one-file-per-entry, YAML frontmatter, multi-level indexes), 3-tier retrieval algorithm, three-level deduplication system, quality lifecycle (Active→Suspected→Superseded→Retired), GitHub backend with CI automation, and a federation protocol (canonical/child/peer with private augmentation layers and watch CI). The design exists as a specification; implementation begins at Phase 1.

## How We Got Here

| Decision | Chosen | Why | Alternatives Rejected |
|---|---|---|---|
| Entry granularity | One file per entry (GE-XXXX.md) | File = retrieval unit; direct Read by path, no grep-within-file | Grouped domain files (growing overhead, bulk-load problem) |
| Metadata format | YAML frontmatter | Machine-readable, Obsidian-native, grep-precise (^field: can't match body) | Markdown headers **ID:**, **Stack:** (ambiguous grep) |
| Directory axis | Technology domain (quarkus/, tools/) | Claude knows the technology from the error — fastest first hop | Conceptual domain (backend/, terminals/) — too many cross-cutting tools |
| Conceptual domain | Label not directory | No entry duplication; web app/Obsidian renders domain views from labels | Top-level domain directories (would require duplicate entries) |
| Sub-directory threshold | ≥3 entries per sub-domain | Enough entries to justify the grouping signal | Flat per domain (loses sub-domain structure at scale) |
| ID assignment (Phase 1) | Sequential counter in GARDEN.md | Simple, no external dependency | GitHub Issues (Phase 2 — needs GitHub backend first) |
| ID assignment (Phase 2+) | GitHub Issues as GE-ID | Atomic, conflict-free in concurrent PR model | CI-assigned at merge (submitter can't track before merge) |
| Retrieval architecture | 3-tier: tech→domain INDEX → symptom→labels → full _summaries/ scan | Bounded token cost at every tier; no vectors needed | Vector RAG (requires infrastructure; loses "why?" reasoning — 0% vs 100% recall) |
| GitHub retrieval | git cat-file --batch (sparse blobless clone) | One network round-trip for multiple entries; object store = cache | GitHub Contents API (10s/request, rate limited) |
| Federation model | Canonical/child/peer with SCHEMA.md declaration | Three distinct governance contracts; parent unaware of child | Fork model (drift/merge conflicts); flat overlay (no deduplication governance) |
| Child augmentation | _augment/ directory (private YAML files per parent entry) | Private context without modifying parent; parent unaware | Fork and modify (breaks upstream sync) |
| Quality lifecycle | Active→Suspected→Superseded→Retired with staleness_threshold per entry | CI auto-flags stale entries; no silent degradation | No lifecycle (most existing systems — stale knowledge returned with full confidence) |
| Name | Hortora (hortus + -ora) | Clean across all registries; horticulture root immediately graspable; oracle echo | Sylvara (sylvara.ai active AI agency — Grok missed this); Mycelium (mycelium.to in same space); Cairn (active AI coding agent) |
| Phased roadmap | 9 phases, shallow-then-deep, explicit evergreen dimensions | Structure correct from Phase 1; sophistication grows over phases | Big bang (all phases before any value) |

## Where We're Going

**Immediate next steps:**
- Register GitHub org `hortora-org` (or `hortora`) before someone else does
- Register domains: `hortora.garden`, `hortora.dev`, `hortora.com`
- Create GitHub issues/epics in mdproctor/knowledge-garden and mdproctor/cc-praxis
- Execute Phase 1: migrate 78 entries to v2 structure (one-file-per-entry, YAML frontmatter, _summaries/, domain INDEX.md files, labels/, SCHEMA.md v2.0.0)
- Update garden skill (SKILL.md) to use 3-tier retrieval and new workflows

**Open questions:**
- **Open protocol vs. Claude-specific** — should SCHEMA.md and the federation protocol be published as a tool-agnostic open spec, or remain Claude-first? Must be resolved before the first public canonical garden launches.
- **cc-praxis skill migration** — does garden/SKILL.md stay in cc-praxis (thin stub pointing to hortora-engine) or does the full skill move to the hortora org?
- **GitHub org name** — is `hortora` available as a GitHub org name? `hortora-org` confirmed as unregistered.
- **Phase 2 sequencing** — should Phase 2 (GitHub backend) come immediately after Phase 1, or should Phase 1 be deepened (quality lifecycle, deduplication) first?
- **First canonical garden domain** — jvm-garden is the obvious first choice given existing entries; should it launch before or alongside the org?

## Linked ADRs

| ADR | Decision |
|---|---|
| [ADR-0011 — Index-and-Lazy-Reference Pattern](../adr/0011-index-and-lazy-reference-pattern.md) | Every methodology tool corpus gets a structured index; cross-tool references use file paths, not inline content |

## Context Links

- Design specification: [docs/superpowers/specs/2026-04-07-garden-rag-redesign-design.md](../superpowers/specs/2026-04-07-garden-rag-redesign-design.md)
- Visual diagrams: [docs/visuals/garden-diagrams.html](../visuals/garden-diagrams.html)
- Related snapshot: [2026-04-06-writing-infrastructure-and-garden.md](2026-04-06-writing-infrastructure-and-garden.md)
- Implements: mdproctor/cc-praxis#36 — Design project memory architecture
