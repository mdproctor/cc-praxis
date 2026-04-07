# Hortora

### A governed, federated knowledge garden for AI coding assistants

**Date:** 2026-04-07 · **Status:** Vision document, phased implementation · **Author:** Mark Proctor

---

## Executive Summary

AI coding assistants are extraordinarily capable — until they hit something non-obvious. A bug that silently fails with no error. An API that contradicts its own documentation. A workaround that took three days to find and is discoverable nowhere. In these moments, the assistant guesses confidently from its training data, and it's usually wrong. The knowledge that would help it isn't there — not because it doesn't exist, but because nobody has built a way to capture, store, and retrieve it.

The Knowledge Garden is that system.

It captures exactly this class of knowledge — non-obvious technical gotchas, undocumented behaviours, surprising workarounds — in a structured, quality-gated format designed for AI retrieval rather than human search. Not documentation. Not Q&A. Not a vector database. A governed collection of hard-won knowledge, stored as plain markdown in a git repository, structured so that an AI can find the right entry in three tool calls and under 1,500 tokens.

**What makes it different:** an editorial bar (only what would genuinely surprise a skilled developer), a three-level deduplication system, automated quality lifecycle management, and — most distinctly — a federation protocol that lets teams run private gardens that extend public canonical ones, without the public garden ever knowing the private one exists.

**The nearest precedent** is Karpathy's LLM-wiki (April 2026), which proved that structured markdown outperforms vector RAG for high-signal technical knowledge. The garden goes further: governance, quality lifecycle, deduplication, and federation are all absent from Karpathy's sketch. The combination hasn't been built.

**The vision** is an ecosystem: an open specification, a reference implementation, and a network of canonical domain gardens — for JVM, Python, frontend, systems — that any team can extend privately and any AI assistant can query. Think Stack Overflow, but built from the ground up for AI consumption rather than human search.

*This document is the complete vision — from today's 78 entries through to fine-tuned models carrying garden knowledge in their weights. [Phase 1 Scope](#phase-1-scope) is at the end for readers who want to know what gets built first.*

---

---

---

## The Name: Hortora

**Hortora** — from *hortus*, Latin for garden, with the *-ora* ending that gives it the quality of both a sanctuary and an oracle. Something you tend. Something you consult.

### Etymology and Meaning

*Hortus* is the root of horticulture, horticulturist, and the English word garden (via Old French *jardin*, ultimately from Frankish *gard* — all sharing the Indo-European root for an enclosed, cultivated space). The connection is immediate for any developer who encounters it: this is something that grows, that is tended, that requires ongoing care.

The *-ora* ending does two things quietly. It evokes *aurora* — the light that arrives before you fully know why — and it echoes *oracle*: a source of answers to questions you couldn't answer alone. A Hortora is a garden that tells you things.

Pronounce it **Hor-TOR-uh**. Three syllables, no awkward consonant clusters, no ambiguous vowels. People say it right the first time.

### Why the Name Fits the Product

The name earns its place because every part of the product metaphor lives inside it:

- **Tending** — entries are captured, pruned, revised, retired. The garden is maintained.
- **Growing** — the corpus expands with every debugging session. Knowledge compounds.
- **Curating** — the editorial bar (scored 1-15) means not everything enters. Only what's worth growing.
- **Cultivating quality** — the lifecycle (Active → Suspected → Superseded → Retired) mirrors a gardener's work: not just planting but watching, adjusting, cutting back what's gone over.
- **Federating** — canonical domain gardens extend into private child gardens, exactly as an orchard propagates from root stock. One hortora becomes many.

### Why It's a Low-Risk, Clean Choice

The name emerged from a systematic validation process. Three rounds of candidate names were tested — covering portmanteaus, single words, tree names, and invented words — with independent web search validation for each. Names rejected in the process included: Cairn (active AI coding agent in the same space), Mycelium (live AI tool orchestrator for developers), Silt (funded AI knowledge product with identical positioning), Lore (dominant on lore.kernel.org and a Python ML framework), Grove (HashiCorp active product), and a dozen others.

**Hortora is confirmed clear** — independently validated across software products, AI tools, PKM apps, GitHub orgs, npm, PyPI, and domain registries:

- No software product, knowledge management tool, PKM app, AI assistant, or developer tool uses this name
- No dominant cultural association that creates confusion
- Adjacent name `Hortus AI` exists on GitHub but is clearly distinct — different word, different product
- The only related name found (`hortator` on npm) is a dormant clock library, 10 years old, zero dependents
- Domains `hortora.com`, `hortora.ai`, `hortora.io`, `hortora.garden` appear unregistered

**Importantly:** Grok's top pick — *Sylvara* — was independently found to have `sylvara.ai` as a live AI automation agency and `sylvaera.com` as a near-identical AI developer toolkit. Nemora was found to have `nemora.ai` as an active AI product with a multi-domain presence. Both were rejected. Hortora was the only name that cleared all checks.

**Recommended next step before launch:** file a USPTO trademark search in Class 042 (software services) and register `hortora.ai`, `hortora.com`, and `hortora.garden` promptly.

The approach taken — Latin root with a purposeful suffix — produces a name that feels meaningful without requiring explanation. *Hortus* is graspable by anyone who's heard the word horticulture. The full word Hortora rewards the reader who notices the oracle echo without demanding they notice it.

### The Brand in Practice

```
Hortora          ← the product
hortora.garden   ← the home
github.com/hortora-org          ← the org
  hortora-spec   ← the open protocol
  hortora-engine ← the reference implementation
  jvm-garden     ← first canonical domain garden
  tools-garden   ← second canonical domain garden
```

Tagline candidates: *Tend your knowledge.* / *The garden that teaches the machine.* / *Accumulated lore, structured for AI.*

---

## Table of Contents

**Recommended reading order for new readers:** start with [Why This Redesign](#why-this-redesign) → [Competitive Landscape](#competitive-landscape) → [Strategic Ecosystem Vision](#strategic-ecosystem-vision), then the technical sections in order.

### The Name
- [The Name: Hortora](#the-name-hortora) — etymology, rationale, and namespace validation

### Part I — The Case
- [Why This Redesign](#why-this-redesign) — the problem this solves
- [Competitive Landscape](#competitive-landscape) — what exists and why it falls short
- [Strategic Ecosystem Vision](#strategic-ecosystem-vision) — the long-term destination

### Part II — The Architecture
- [Research Foundation](#research-foundation) — the evidence behind design choices
- [Design Decisions](#design-decisions) — key trade-offs and why
- [Complete Structure Specification](#complete-structure-specification)
- [File Format Specifications](#file-format-specifications)
- [The 3-Tier Retrieval Algorithm](#the-3-tier-retrieval-algorithm)
- [Trigger Model](#trigger-model)
- [Schema Versioning](#schema-versioning)

### Part III — The Workflows
- [Workflow Changes](#workflow-changes)
- [Label Taxonomy](#label-taxonomy)
- [Migration Plan](#migration-plan)
- [Web App and Plugin Interface Contract](#web-app-and-plugin-interface-contract)
- [Maintenance and Health Checks](#maintenance-and-health-checks)
- [Success Criteria](#success-criteria)
- [Future Directions](#future-directions)
- [GitHub Backend Architecture](#github-backend-architecture)
- [Federation Architecture](#federation-architecture)
- [Implementation Roadmap](#implementation-roadmap)
- [Phase 1 Scope](#phase-1-scope)

---

## Strategic Ecosystem Vision

*The long-term destination, independent of implementation timeline.*

![The Garden Ecosystem — three layers from open protocol to community knowledge to private extension](../../visuals/screenshots/diagram-1-ecosystem.png)

The knowledge garden is not a feature. It is a platform — and ultimately, an ecosystem. The vision has three layers:

### Layer 1: The Protocol / Specification

A **tool-agnostic open specification** defining:
- Garden entry format (YAML frontmatter schema, entry types, scoring rubric)
- Multi-level index structure (global index, domain index, summaries, labels)
- Federation protocol (canonical/child/peer relationships, ID namespacing, submission routing)
- Quality lifecycle states (Active, Suspected, Superseded, Retired)
- SCHEMA.md versioning convention (SchemaVer: MODEL.REVISION.ADDITION)

**The strategic question: Claude-specific or open protocol?**

This is unresolved and consequential. Two paths:

| Path | Approach | Implication |
|------|----------|-------------|
| **Claude-first** | Design for Claude Code's Grep/Read/Glob constraints | Simpler to build, limits ecosystem adoption |
| **Open protocol** | Design so Cursor, Copilot, Gemini CLI, Windsurf can all implement it | Harder to specify, potentially very large ecosystem |

The current design is Claude-first but the protocol is not inherently Claude-specific. The SCHEMA.md format, federation rules, and entry format could be implemented by any AI assistant. **The decision to formalise this as an open spec should be made before the first public release of canonical gardens.**

### Layer 2: The Engine / Reference Implementation

The **garden-engine** repository: the reference implementation of the spec.

- Validation scripts (`validate_garden.py`, `validate_pr.py`, `integrate_entry.py`)
- GitHub Actions workflows (PR validation, index maintenance, freshness scanning)
- Web app (domain/label/graph views over the garden filesystem)
- MCP server (exposes the garden to any AI assistant via the MCP protocol)
- Federation tooling (`_watch/` CI, augmentation layer, submission routing)
- Migration scripts (v1 → v2 structure migration)

### Layer 3: The Canonical Knowledge Gardens

A **GitHub organisation** housing canonical community-curated domain gardens:

```
github.com/<org-name>/
  ├── garden-spec          ← The open protocol specification
  ├── garden-engine        ← Reference implementation (validators, CI, web app, MCP)
  │
  ├── tools-garden         ← git, docker, bash, CI/CD, regex, ai-tools            (GE-)
  ├── jvm-garden           ← Java, Kotlin, Quarkus, Maven, Gradle, Spring, Drools  (JE-)
  ├── python-garden        ← Python, pip, Django, FastAPI, pandas, pytest           (PE-)
  ├── frontend-garden      ← TypeScript, React, CSS, Vite, Playwright               (FE-)
  ├── systems-garden       ← Rust, Go, C++, Linux, WASM, containers                (SE-)
  └── mobile-garden        ← Android, iOS, Flutter, React Native, Swift             (ME-)
```

Individual users and enterprises:
```
mdproctor/knowledge-garden   ← personal child garden (child of jvm-, tools-)
enterprise/private-garden    ← private child garden (child of org canonical gardens)
team/specialist-garden       ← peer garden for a specialised domain
```

**Org naming:** Unresolved. Should capture: open knowledge, AI-first, community, developer focus. Should NOT be Claude-specific if the protocol becomes tool-agnostic. Candidates to evaluate: `devgardens`, `knowledge-gardens`, `aigardens`, `garden-protocol`, or similar.

### Repository Structure Decision

**What stays in `cc-praxis` (this repo):**
- `garden/SKILL.md` — the behavioral skill that tells Claude how to CAPTURE, MERGE, SWEEP, etc.
- The skill is a thin behavioral guide; it references the engine for tooling but does not contain it.
- `systematic-debugging/SKILL.md` — with the garden Step 0 consultation

**What moves to the garden ecosystem org:**
- The garden data (currently at `~/claude/knowledge-garden/`)
- The platform tooling (validators, CI scripts, GitHub Actions)
- The web app, MCP server, Obsidian plugin
- The design specification (this document, ultimately)
- The canonical domain garden repos

**The skill stays small. The platform grows independently.**

### The Obsidian Plugin Opportunity

Our garden's YAML frontmatter schema is already Obsidian-native — by design, not coincidence:

| Garden structure | Obsidian equivalent | Effort to bridge |
|---|---|---|
| YAML `labels:` field | Obsidian tags (`#label`) | Zero — identical format |
| `See also: GE-0033` cross-refs | Obsidian `[[wikilinks]]` | Minimal — transform on read |
| Domain directory structure | Obsidian folder structure | Zero — same filesystem |
| `status: suspected` field | Obsidian properties | Zero — YAML is YAML |
| `_summaries/` files | Dataview queries | Medium — query on frontmatter |
| `verified:` and `staleness_threshold:` | Dataview staleness views | Medium |

A minimal Obsidian plugin (backed by the garden repo via Obsidian Git) provides human-readable views that require no structural changes to the garden. The plugin reads what's already there. This is the **lowest-effort human browsability path** — far simpler than a custom web app, and available to the whole Obsidian user community.

---

## Why This Redesign

![Three Entry Types — the garden captures exactly these, nothing else](../../visuals/screenshots/visual-a-entry-types.png)

### The Core Problem

The knowledge garden's value proposition is: *a Claude that hits a non-obvious bug or technique should find the relevant entry faster than searching the web or re-reading conversation history.*

It currently fails this in two ways:

**Retrieval fails silently.** The SEARCH workflow reads `GARDEN.md` (titles + GE-IDs only), then loads a full domain file to find the entry. Those domain files are growing: `appkit-panama-ffm.md` is 411 lines, `tmux.md` is 220 lines. As entries accumulate, loading a domain file wastes tokens proportional to how much irrelevant content it contains. Worse, `GARDEN.md` index entries carry only titles — not enough semantic content for Claude to judge relevance without loading the file. So Claude either loads everything speculatively (wasteful) or misses relevant entries (useless).

**Retrieval is never triggered proactively.** The garden is only searched when the user explicitly says "search the garden" or invokes SEARCH. When Claude gets stuck debugging, it doesn't automatically reach for the garden. It reasons from training data and guesses — even when the garden contains the exact answer, already hard-won.

### What "Good" Looks Like

![Before & After — v1 GARDEN.md-based retrieval vs v2 indexed approach](../../visuals/screenshots/visual-f-before-after.png)

When Claude encounters an unfamiliar symptom during debugging:

1. It recognises the trigger pattern and consults the garden automatically
2. It reads a compact routing table (~80 tokens) to identify the relevant domain
3. It greps a domain index (~50 tokens per entry) for keyword matches
4. It loads the 1-3 matching entries (~300 tokens each) directly by path
5. Total cost: under 1,200 tokens for a targeted retrieval, regardless of garden size

When Claude doesn't know the technology:

1. It reads the label index for a matching symptom type
2. It loads a label file with candidate GE-IDs and paths
3. It loads those entries directly
4. Total cost: 2 reads + N targeted reads, bounded

When Claude is genuinely lost:

1. It scans `_summaries/` — 100-token distillations of every entry
2. At 300 entries: 30,000 tokens to scan the whole garden (still within budget)
3. It loads 2-4 matching full entries
4. Total cost: bounded regardless of garden size

---

## Research Foundation

This design is grounded in three parallel research tracks:

### Production PKM Systems

Every major knowledge management system (Obsidian Dataview, Logseq, zk, org-roam, Dendron, SiYuan) converges on the same retrieval pattern:

1. Query a metadata index — no file I/O
2. Filter/rank candidates in memory
3. Load only matching files for content
4. Inject only retrieved content into context

No system loads all files. zk uses SQLite + FTS5 with BM25 scoring. org-roam uses SQLite with pure SQL joins and delegates text search to ripgrep. Obsidian Dataview uses an in-memory `PrefixIndex` (prefix tree over file paths) for O(log n) folder-scoped queries. SiYuan stores every paragraph/heading as a separate database row — more granular than we need, but confirming that the entry-as-atomic-unit is the right design.

**For our constraint** (Claude uses Grep/Read/Glob, no database): the filesystem itself is the database. Directory hierarchy = prefix tree. Domain `INDEX.md` = metadata table. `_summaries/` = content cache. Grep = FTS query.

### RAG Engineering Practice

From Anthropic engineering, LlamaIndex, Weaviate, and LangChain documentation:

- **Parent-child chunking**: store a summary chunk (~100 tokens) for retrieval and a full chunk (~300-500 tokens) for reading. Pre-screening summaries reduces retrieval token cost 30-40%.
- **Metadata-first filtering**: grep frontmatter fields before reading body content. Reduces token consumption by 30-40% and avoids loading irrelevant content. Metadata filters must use OR-style matching to prevent recall loss.
- **"Lost in the middle"** (Anthropic, 2024): information in the middle of a large context is less effectively used. Load max 3-4 targeted entries, never bulk-load a domain file.
- **Structured text beats vectors for "why?" reasoning** (DEV Community, 2025): a direct comparison of structured ontology vs. markdown+RAG for AI agent reasoning found 100% vs. 0% recall for "why?" questions — questions about the reasoning behind decisions, not just facts. Vector RAG finds documents that *mention* a decision but not the reasoning chain. Structured text with explicit fields (root cause, why non-obvious) preserves the reasoning chain intact. This directly validates the garden's schema design: the `root_cause` and `why_non_obvious` sections are exactly the "why?" content that vectors lose.
- **Contextual retrieval** (Anthropic): chunk-prepended context + BM25 reduces retrieval failure by 49% vs. naive chunking.
- **Index works up to ~200 entries** before Grep becomes primary navigation. Garden is at 78, heading toward 200. The design supports both.
- **RAPTOR cluster summaries**: at 100+ entries, thematic cluster summaries become an intermediate index level.

### Repository Versioning

From research on AI context files (CLAUDE.md, AGENTS.md, GEMINI.md) and schema versioning practice:

- **ETH Zurich (2026)**: bloated context files hurt agents — 3% task drop, 20% cost increase. The `SCHEMA.md` layout contract must be short and machine-readable, not prose narrative.
- **Context debt**: 2% structural misalignment introduced early → 40% failure rate by end of a reasoning chain. The schema version must be the canonical truth.
- **SchemaVer** (Snowplow): `MODEL.REVISION.ADDITION` — the right versioning scheme for filesystem layout changes.
- **Per-directory README.md** is the dominant navigation pattern in large repos. Every domain directory gets one.

---

## Competitive Landscape

*Does this exist? What's the closest competition?*

**Short answer: no system combines all of what we're building.** Adjacent systems share individual characteristics but none assembles them into a coherent whole. The closest spiritual predecessor is Stack Overflow — curated, community-contributed, quality-gated technical knowledge — but Stack Overflow is human-to-human: structured for human search, human reading, human answers. The garden is the equivalent built end-to-end for AI: AI captures it, AI indexes it, AI retrieves it, AI uses it.

---

### Comparison Table

| System | Editorial bar | Text-based RAG (no vectors) | Deduplication governance | Quality lifecycle | Federation | Git-backed filesystem |
|--------|--------------|----------------------------|--------------------------|------------------|------------|----------------------|
| **What we're building** | ✅ Non-obvious only (scored 1-15) | ✅ Multi-level indexes, Grep/Read/Glob | ✅ Three levels (L1/L2/L3) | ✅ Active→Suspected→Superseded→Retired | ✅ Canonical/child/peer protocol | ✅ Plain markdown |
| **Karpathy LLM-wiki** (Apr 2026) | ❌ No filter — ingests anything | ✅ Git + markdown, LLM maintains index | ❌ Linting pass only, no governance | ❌ None | ❌ Personal wiki only | ✅ |
| **infinite-context / claude-infinite-context** | ❌ Claude writes anything | ✅ Grep/Read from Obsidian vault | ❌ None — duplicates accumulate | ❌ None | ❌ Single project, single user | ✅ |
| **Stack Internal** (Stack Overflow, 2025) | ⚠️ Community votes, not surprise bar | ❌ Vector-based + MCP | ⚠️ Duplicate flagging only | ⚠️ Closed/locked states | ❌ None | ❌ SaaS |
| **GitHub Copilot Spaces** (successor to KB) | ❌ Any markdown | ❌ Vector-based | ❌ None | ❌ None | ❌ None | ✅ |
| **MemGPT / Letta** | ❌ Personal agent memory | ❌ Vector archival storage | ❌ None | ❌ None | ❌ None | ❌ |
| **Obsidian + Smart Connections** | ❌ Any notes | ❌ Vector-based | ❌ None | ❌ None | ❌ None | ✅ |
| **CLAUDE.md / .cursorrules** | ❌ Instructions only | ❌ Not retrieval | ❌ None | ❌ None | ⚠️ Via git | ✅ |
| **Microsoft GraphRAG** | ❌ Any documents | ❌ Vector + graph | ❌ None | ❌ None | ❌ None | ❌ |

---

### The Nearest Neighbors in Detail

**`infinite-context` / `claude-infinite-context`** (GitHub, early 2026) — The closest implementation to the gotcha capture concept. Uses Obsidian as Claude Code's persistent memory: a `Gotchas.md` file, `_ERRORS.md`, `_DECISIONS.md`, session logs. Plain markdown, git-backed, grep/read accessible. Demonstrates that the instinct is right — developers independently discovered the need for gotcha capture in AI sessions. Gaps: single project, single user, no editorial bar (Claude writes anything it discovers), no deduplication (the same gotcha can appear in multiple sessions), no quality lifecycle, no sharing across teams.

**Stack Internal** (Stack Overflow, 2025) — The most serious competitor by framing: "verified knowledge for AI assistants," with MCP integration so Copilot/Cursor/ChatGPT can query it. Launched as an enterprise product. Gaps: captures Q&A (not curated non-obvious knowledge specifically), editorial bar is community votes not surprise-score, backed by a proprietary database (not git + markdown), vector-based retrieval, no federation protocol, enterprise-priced and vendor-locked. Validates the market; doesn't solve the right problem.

**Federated AI knowledge as a protocol: does not exist.** Searching specifically for "federated knowledge base AI coding distributed protocol" returns only federated learning research (privacy-preserving ML model training) — a completely different concept. No public design, no specification, no implementation of a canonical/child/peer federation protocol for developer knowledge gardens exists anywhere.

---

### What Is Genuinely Novel

**1. The editorial bar with a specific semantic filter**

No existing system filters knowledge at the semantic level of *"would a skilled developer be surprised by this?"* Stack Overflow has community voting, but that measures popularity, not non-obviousness. Our garden score (1-15) enforces an editorial bar that explicitly excludes documented behaviour, routine bugs, and general best practices — admitting only what genuinely saves hours.

**2. Text-based RAG architecture designed for AI tool constraints**

Every production RAG system uses vectors. We use Grep/Read/Glob — the only tools available to a Claude Code session. The multi-level index architecture (`_index/global.md` → domain `INDEX.md` → `_summaries/` → entry files) is designed around these constraints. No existing system structures a knowledge base specifically for this retrieval pattern.

**3. The submission + three-level deduplication governance model**

The write-first/deduplicate-later pattern (submissions queue → L1 submitter check → L2 integration check → L3 periodic sweep) combined with CHECKED.md pair tracking is purpose-built for a knowledge base where the same non-obvious bug is independently discovered by many developers. No existing system has this governance model.

**4. Quality lifecycle with automated staleness detection**

The Active → Suspected → Superseded → Retired state machine, driven by CI scanning `verified` dates against per-entry `staleness_threshold` values, and checking library version strings against package registries — this does not exist in any knowledge management system we found. Most systems have no staleness model at all; they return stale knowledge with equal confidence.

**5. The federation protocol (canonical/child/peer)**

Federated knowledge sharing with defined governance contracts per relationship type — strict non-duplication for child→parent, advisory for peer↔peer — combined with domain-based submission routing and the augmentation layer has no direct precedent. The closest analogy is how DNS zones own their namespace, but DNS has no knowledge content or quality governance.

**6. The private augmentation layer**

A child garden adding private context (keywords, labels, notes) on top of public parent entries without modifying them — so a private session retrieves public knowledge *enriched* with private context — appears to be completely novel. No annotation system, overlay system, or PKM tool implements this pattern in the context of AI knowledge retrieval.

---

### Novelty Assessment (Research-Verified)

| Differentiator | Closest existing work | Gap |
|---|---|---|
| Editorial bar (surprise score 1-15, threshold enforced) | Nothing | **Genuinely novel** |
| Text-based multi-level RAG (indexes, summaries, domain keywords) | Karpathy pattern + fragmentary "vectorless RAG" writing | Combination is novel; pieces exist separately |
| Submission queue + integration governance | Nothing in this domain | **Genuinely novel** |
| Quality lifecycle (Active → Suspected → Superseded → Retired) | Nothing in this domain | **Genuinely novel** |
| Three-level deduplication discipline | Nothing in this domain | **Genuinely novel** |
| Federation protocol (canonical/child/peer, private augmentation, watch CI) | Nothing — "federated learning" is a different concept entirely | **Genuinely novel** |
| Plain markdown + git, no database, no vectors | Karpathy + Obsidian projects | Not novel on its own |
| Retrieval success feedback (`retrieval_count` × `helpfulness_score`) | Nothing — Stack has votes, not success rate | **Genuinely novel** |
| External library change monitoring (repo events → staleness flags) | Copilot Spaces auto-syncs but not for staleness | Combination is novel |
| Session core memory (Trigger D — promote hot entries to context) | Letta has core memory concept | Application to garden retrieval is novel |
| Priority-gated known-gap entries (`priority: critical`) | Nothing — most systems have no "help wanted" signal | **Genuinely novel** |

The individual storage choice (git + markdown) has precedent. The "no vectors" intuition is shared with Karpathy and is gaining community traction. Everything else — the editorial bar with a numeric threshold, the governance workflow, the quality lifecycle, the three-level deduplication, and especially the federation protocol — has no public implementation or even public design anywhere in the ecosystem.

**The market is clearly forming around this problem** (Stack Internal, Letta Code, `infinite-context`, Obsidian memory systems), which validates the need. None of them solve the right problem with the right constraints.

---

### The Stack Overflow Analogy

Stack Overflow is the most instructive comparison. It solved the community-curated technical knowledge problem for humans: editorial quality (voting, accepted answers, duplicate detection, moderation), lifecycle management (closed, locked, deleted), and domain structure (tags). It succeeded because it had the right combination of governance and community.

The garden addresses the same fundamental problem but for a different consumer and at a different layer:

| Dimension | Stack Overflow | Knowledge Garden |
|-----------|---------------|-----------------|
| Consumer | Human developers searching for answers | AI coding assistants retrieving context |
| Capture | Human writes a question + answer | AI captures from a debugging/coding session |
| Quality signal | Community votes, accepted answer | Editorial bar (non-obvious only) + lifecycle |
| Retrieval | Full-text search, human reads | Grep/Read/Glob, injected into AI context |
| Format | Q&A thread | Structured entry: symptom + root cause + fix |
| Federation | One canonical site | Distributed canonical gardens by domain |
| Freshness | Answered years ago, may be stale | Staleness threshold + lifecycle transitions |

Stack Overflow captured community knowledge in the era of human search. The garden is the equivalent for the era of AI-assisted development — capturing the knowledge that AI *doesn't* already have, structured so AI can find and use it at the right moment.

---

### Karpathy LLM-wiki: The Closest Predecessor

Karpathy's LLM-wiki (published April 3–4 2026, days before this document) is the closest conceptual ancestor: plain markdown in a git repo, an LLM maintaining a self-built index, no vector database. It validates the core architectural choice. But it is a sketch for individual knowledge compilation, not a system for:

- Community curation with an editorial bar
- Multi-contributor governance and deduplication
- Quality lifecycle management
- Federation across organisations and domains
- Private augmentation of shared public knowledge
- Automated staleness detection

The garden is what LLM-wiki becomes when it needs to scale from one person to a community.

---

### Conclusion

This design occupies an empty space in the current landscape. The components exist individually — git-backed markdown stores, RAG systems, community knowledge bases, annotation layers — but no system assembles them with the specific combination of:

- Editorial bar optimised for AI knowledge gaps
- Retrieval architecture optimised for AI tool constraints (no vectors)
- Governance model (deduplication, lifecycle, staleness)
- Federation protocol for distributed community knowledge

*Note: competitive landscape section written 2026-04-07. To be updated as the field evolves — this area is moving fast.*

---

## Design Decisions

### D1: One file per entry

**Decision:** Each garden entry is a separate file (`GE-0066.md`), not grouped with other entries in a domain file.

**Rationale:** The file is the retrieval unit. A direct `Read` path is O(1) and loads exactly one entry. Grep-within-a-file is slower, error-prone, and loads all preceding entries as overhead. As domain files grow, the overhead grows. The web app provides human-friendly grouped views from the file metadata — human browsability is not a filesystem constraint.

**Rejected alternative:** Grouped domain files (e.g. `cdi.md` containing 3 entries). Rejected because loading any entry requires loading all entries in that file.

### D2: YAML frontmatter as the metadata layer

**Decision:** Every entry file carries YAML frontmatter with structured fields (`id`, `type`, `stack`, `labels`, `keywords`, `symptom`, `context`).

**Rationale:** YAML frontmatter is universal in PKM systems (Obsidian, Logseq, Jekyll, Hugo) because it cleanly separates metadata from content. `grep ^labels:` across files is precise — cannot accidentally match body content. The web app and Obsidian plugin read YAML frontmatter natively. Summary files are generated from frontmatter at MERGE time, never hand-edited.

**Rejected alternative:** Markdown header fields (`**ID:** GE-0066`). Rejected because grep can match these fields anywhere in the document body, and there is no structural distinction between metadata and content.

### D3: Domain as primary filesystem axis, domain-type as label

**Decision:** The primary directory grouping is technology domain (`quarkus/`, `tools/`, `java-panama-ffm/`). The conceptual domain (backend, frontend, mobile, terminals) is a label, not a directory level.

**Rationale:** When Claude is stuck, it knows the technology immediately (from the error, the stack trace, the import statements). Technology is the most precise first-narrowing axis. Conceptual domain (backend/mobile/frontend) is a secondary filter useful when the technology isn't yet known. Implementing domain as a directory level would require either duplicate entries or complex cross-reference management — both add maintenance burden without retrieval benefit. The web app provides domain-based views from labels without any structural change.

**Exception:** If a technology accumulates 5+ entries that only exist in one conceptual domain context (e.g. `quarkus-mobile/` once Quarkus mobile patterns emerge as a distinct body of knowledge), that becomes its own technology domain directory. The label and the directory are not mutually exclusive at that threshold.

**Rejected alternative:** Top-level domain directories (`backend/`, `terminals/`). Rejected because cross-domain tools (git, Claude Code, regex) have no clean home, tools categorized as "backend" from one perspective are "devops" from another, and most gotchas are technology-specific not context-specific.

### D4: Sub-directories within domains at ≥3 entries per sub-domain

**Decision:** Sub-directories are created within a domain when a sub-domain accumulates 3 or more entries.

**Rationale:** Sub-directories provide a free narrowing level. `quarkus/cdi/` tells Claude at path-read time that these are CDI-specific entries. Below 3 entries, the overhead of an extra directory level isn't justified.

**Example:** `quarkus/` currently has CDI (3 entries), config (1), maven (2), profiles (1), webauthn (2), quarkus-flow (4). Sub-directories created for CDI (3) and quarkus-flow (4); others remain flat until they reach the threshold.

### D5: Both gotchas and techniques carry labels

**Decision:** Labels are mandatory on all entry types (gotcha, technique, undocumented). The current restriction of labels to techniques only is removed.

**Rationale:** Cross-cutting retrieval by symptom type (`#symptom:silent-failure`) is most valuable for gotchas, not techniques. A gotcha with no labels is invisible to cross-domain symptom-based search. Techniques already have labels; gotchas need them equally.

### D6: Trigger model is A+C with lightweight B

See [Trigger Model](#trigger-model) section.

---

## Complete Structure Specification

```
~/claude/knowledge-garden/
│
├── SCHEMA.md                      ← Layout contract. Version marker. Navigation guide.
│                                     Claude reads this FIRST on any garden interaction.
├── GARDEN.md                      ← Metadata ONLY: last ID, drift counter, last sweep.
│                                     No index content. No entry listings.
├── CHECKED.md                     ← Duplicate check pair log (unchanged role)
├── DISCARDED.md                   ← Discard log with conflict GE-IDs (unchanged role)
│
├── submissions/                   ← Incoming entries (unchanged role)
│   └── YYYY-MM-DD-<project>-GE-XXXX-<slug>.md
│
├── _index/                        ← Retrieval infrastructure. Always cheap to read.
│   └── global.md                 ← Domain routing table. 8-12 rows. First navigation hop.
│
├── _summaries/                    ← 50-100 token distillations. One file per entry.
│   ├── GE-0001.md                ← Frontmatter fields + path pointer. No body content.
│   ├── GE-0033.md
│   └── GE-NNNN.md               ← Auto-generated by MERGE. Never hand-edited.
│
├── labels/                        ← Cross-cutting label index files.
│   ├── INDEX.md                  ← Label catalog: label | file | count | description
│   ├── domain-backend.md         ← GE-ID | path | one-liner (for all backend entries)
│   ├── domain-frontend.md
│   ├── domain-terminals.md
│   ├── domain-mobile.md
│   ├── domain-devops.md
│   ├── domain-tooling.md
│   ├── symptom-silent-failure.md
│   ├── symptom-startup-ordering.md
│   ├── symptom-native-vs-jvm.md
│   ├── symptom-version-drift.md
│   ├── pattern-strategy.md
│   ├── pattern-testing.md
│   ├── pattern-automation.md
│   ├── pattern-performance.md
│   └── pattern-token-budget.md
│
├── quarkus/
│   ├── README.md                 ← What's in this domain. Sub-domains listed.
│   ├── INDEX.md                  ← Domain retrieval table: GE-ID | type | subdomain | keywords | symptom
│   ├── cdi/                      ← ≥3 entries → own subdirectory
│   │   ├── GE-0033.md
│   │   ├── GE-0062.md
│   │   └── GE-0066.md
│   ├── maven/
│   │   ├── GE-0031.md
│   │   └── GE-0065.md
│   ├── quarkus-flow/             ← ≥3 entries → own subdirectory
│   │   ├── GE-0068.md
│   │   ├── GE-0069.md
│   │   ├── GE-0070.md
│   │   └── GE-0071.md
│   ├── GE-0047.md               ← config: only 1 entry, stays flat
│   ├── GE-0052.md               ← profiles: only 1 entry, stays flat
│   ├── GE-0045.md               ← webauthn: 2 entries, stays flat
│   └── GE-0046.md
│
├── tools/
│   ├── README.md
│   ├── INDEX.md
│   ├── git/                      ← 3 entries → subdirectory
│   │   ├── GE-0002.md
│   │   ├── GE-0043.md
│   │   └── GE-0050.md
│   ├── claude-code/              ← 4 entries → subdirectory
│   │   ├── GE-0013.md
│   │   ├── GE-0048.md
│   │   ├── GE-0054.md
│   │   └── GE-0055.md
│   ├── GE-0044.md               ← adr: 1 entry, flat
│   ├── GE-0049.md               ← github-cli: 1 entry, flat
│   └── GE-0042.md               ← regex: 1 entry, flat
│
├── java/
│   ├── README.md
│   ├── INDEX.md
│   ├── GE-0058.md               ← generics: 1 entry, flat
│   ├── GE-0064.md               ← maven: 2 entries, flat
│   └── GE-0067.md
│
├── java-panama-ffm/
│   ├── README.md
│   ├── INDEX.md
│   ├── pty/                      ← 5 entries → subdirectory
│   │   ├── GE-0038.md
│   │   ├── GE-0039.md
│   │   ├── GE-0053.md
│   │   ├── GE-0060.md
│   │   └── GE-0061.md
│   └── [native-image entries flat or subdirected per existing content]
│
├── macos-native-appkit/
│   ├── README.md
│   ├── INDEX.md
│   ├── GE-0051.md               ← 3 entries total, no sub-domains yet → flat
│   ├── GE-0072.md
│   └── GE-0073.md
│
├── drools/
│   ├── README.md
│   ├── INDEX.md
│   ├── GE-0056.md
│   ├── GE-0057.md
│   └── GE-0063.md
│
└── [future domains follow same pattern]
```

### Structural Rules

| Rule | Detail |
|------|--------|
| Sub-directory threshold | ≥3 entries sharing a sub-domain → create sub-directory |
| Flat files | Entries without sufficient peers stay at domain level |
| README.md | Every domain directory has one — describes contents, lists sub-domains |
| INDEX.md | Every domain directory has one — keyword retrieval table |
| New domains | Create `<tech-name>/` with `README.md` + `INDEX.md` before adding first entry |
| New sub-domains | Create `<subdomain>/` subdirectory when 3rd entry arrives — migrate earlier entries |

---

## File Format Specifications

![The Garden Score — every candidate scored before submission; below 8 is never submitted](../../visuals/screenshots/visual-b-score.png)

![Anatomy of a Garden Entry — every section has a purpose](../../visuals/screenshots/visual-c-entry-anatomy.png)

### Entry File (`quarkus/cdi/GE-0066.md`)

```markdown
---
id: GE-0066
type: gotcha
stack: [Quarkus 3.x, Quarkus Arc]
labels: [symptom-startup-ordering, domain-backend]
keywords: [UnlessBuildProfile, Unsatisfied dependency, CDI, injection, profile, exclusion]
symptom: "@UnlessBuildProfile on bean A → Unsatisfied dependency in all unguarded consumers"
context: "Profile-based CDI exclusion where excluded bean is directly injected by consumer"
score: 13
---

## @UnlessBuildProfile on a bean causes "Unsatisfied dependency" in any bean that injects it without a matching profile guard

**ID:** GE-0066
**Stack:** Quarkus 3.x, Quarkus Arc (all versions with profile-based CDI)
**Labels:** `#symptom:startup-ordering` `#domain:backend`

**Symptom:** Adding `@UnlessBuildProfile("X")` to bean `A` causes every other bean
that injects `A` directly (not via `Instance<A>`) to fail at startup in profile `X`
with: `Unsatisfied dependency for type A and qualifiers [@Default]`.

**Context:** Any Quarkus application using profile-based CDI exclusion where the
excluded bean is injected by profile-unguarded consumers.

### What was tried (didn't work)
- ...

### Root cause
...

### Fix
...

### Why this is non-obvious
...

*Score: 13/15 · Included because: ... · Reservation: none*
```

**YAML frontmatter field rules:**

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | string | yes | `GE-NNNN` format, matches filename |
| `type` | enum | yes | `gotcha`, `technique`, `undocumented` |
| `stack` | list | yes | Third-party libs include version (`Quarkus 3.x`). Own pre-1.0 projects omit version. |
| `labels` | list | yes | All entry types. At least one label required. From controlled vocabulary. |
| `keywords` | list | yes | 5-10 terms. Include error message fragments, API names, config keys. |
| `symptom` | string | yes | One sentence. The misleading or surprising observable fact. |
| `context` | string | yes | One sentence. When/where this applies. |
| `score` | integer | yes | Garden score 1-15. Retained for future pruning decisions. |
| `captured` | date | yes | ISO date when entry was first written. Never changes. |
| `verified` | date | yes | ISO date of last human or Agent verification. Updated on every REVISE or coherence review. |
| `staleness_threshold` | integer | yes | Days before entry is flagged as Suspected. See table below. |
| `status` | enum | no | Omit for Active entries. Set to `suspected`, `superseded`, or `retired` when applicable. |
| `superseded_by` | string | conditional | Required when `status: superseded`. GE-ID of the replacement entry. |
| `resolved_in` | string | conditional | Required when the bug/issue was fixed upstream. Format: `"LibraryName X.Y"` |
| `discovery_count` | integer | no | Number of times this problem has been independently discovered. Starts at 1 on CAPTURE; MERGE increments when a duplicate submission is discarded (the submitter independently found the same thing). High count = stronger signal of genuine non-obviousness. |
| `source_url` | string | no | For IMPORT entries: URL of the external source (GitHub issue, changelog, CVE). |
| `source_type` | enum | no | For IMPORT entries: `github-issue`, `changelog`, `cve`, `documentation`, `community`. |
| `priority` | enum | no | For `status: known-gap` entries only: `critical`, `high`, `normal` (default). Signals urgency — which gaps most need filling. Surfaces in coverage review and contributor dashboards. |
| `retrieval_count` | integer | no | Incremented by the garden skill each time this entry is retrieved and injected into context. Combined with `discovery_count`, creates a full picture: discovery_count = how many found the problem; retrieval_count = how often the solution is consulted. High retrieval_count = high-value entry worth protecting from staleness. |

**Staleness threshold guidelines:**

| Entry type | Condition | Threshold |
|------------|-----------|-----------|
| Gotcha | Version-pinned (specific library bug) | 90 days |
| Gotcha | Behaviour-based (not version-specific) | 180 days |
| Undocumented | Any | 180 days — undocumented things change without notice |
| Technique | Version-pinned | 180 days |
| Technique | General approach | 365 days |

When `verified` date + `staleness_threshold` days < today → CI sets `status: suspected` automatically.

### Summary File (`_summaries/GE-0066.md`)

Auto-generated by MERGE from entry frontmatter. Never hand-edited.

```
id: GE-0066 | type: gotcha | score: 13
stack: Quarkus 3.x, Arc
labels: symptom-startup-ordering, domain-backend
keywords: UnlessBuildProfile, Unsatisfied dependency, CDI, injection, profile
symptom: @UnlessBuildProfile on bean A → Unsatisfied dependency in all unguarded consumers
context: Profile-based CDI exclusion where excluded bean is directly injected
path: quarkus/cdi/GE-0066.md
```

Format is deliberately NOT markdown tables or YAML — it is a compact key-value format optimised for human scanning at 100 tokens per file. Claude reads `_summaries/GE-0066.md` faster than parsing a YAML file.

### Global Index (`_index/global.md`)

```markdown
# Knowledge Garden — Global Index
# Schema: 2.0.0

| Domain | Sub-index | Entries | Technologies |
|--------|-----------|---------|--------------|
| quarkus | quarkus/INDEX.md | 12 | Quarkus 3.x, Arc, CDI, SmallRye, Hibernate, Maven |
| tools | tools/INDEX.md | 14 | git, GitHub CLI, Claude Code, tmux, regex, ADR tooling |
| java | java/INDEX.md | 3 | Java, Maven, generics |
| java-panama-ffm | java-panama-ffm/INDEX.md | 7 | Panama FFM, jextract, PTY, native image, GraalVM |
| macos-native-appkit | macos-native-appkit/INDEX.md | 3 | AppKit, GCD, NSTextField, WKWebView, NSSplitView |
| drools | drools/INDEX.md | 3 | Drools, Quarkus testing, OOPath, DSL |
| labels | labels/INDEX.md | 15 labels | cross-cutting: domain, symptom, pattern |
| _summaries | _summaries/ | 78 | all entries — use for cross-domain keyword scan |
```

**Rules:**
- One row per technology domain
- `Entries` count kept current by MERGE (automated)
- `Technologies` column is keyword-rich — this is what Claude greps in Tier 1 retrieval when the exact domain name isn't obvious
- `_summaries` row always last — it's the fallback, not the first hop

### Domain Index (`quarkus/INDEX.md`)

```markdown
# Quarkus — Domain Index

| GE-ID | Type | Location | Keywords | Symptom |
|-------|------|----------|----------|---------|
| GE-0033 | technique | cdi/ | UnlessBuildProfile, CDI, production exclusion, dev-only bean, build time | Strips dev-only beans from production at build time — no runtime check |
| GE-0062 | gotcha | cdi/ | HttpAuthenticationMechanism, StartupEvent, CDI startup, @Observes | Auth mechanism resolves before StartupEvent fires |
| GE-0066 | gotcha | cdi/ | UnlessBuildProfile, Unsatisfied dependency, CDI, injection, profile | Profile-excluded bean causes Unsatisfied dependency in consumers |
| GE-0047 | gotcha | . | MicroProfile, config, property names, silently ignored, wrong key | Config keys silently ignored when using incorrect MicroProfile names |
| GE-0031 | gotcha | maven/ | quarkus:dev, build goal, pom.xml, silently skips | quarkus:dev silently does nothing when build goal is absent |
| GE-0065 | gotcha | maven/ | quarkus:dev, maven plugin, extension | Dev mode silently skips if quarkus-maven-plugin lacks build goal |
| GE-0068 | gotcha | quarkus-flow/ | consume step, deserialization, mutation lost | Flow consume re-deserializes input — mutations are lost |
| GE-0069 | gotcha | quarkus-flow/ | POJO, FAIL_ON_EMPTY_BEANS, Jackson, serialization | Plain POJO input causes Jackson serialization failure at runtime |
| GE-0070 | gotcha | quarkus-flow/ | listen task, SmallRye, channel, event bus | Listen task doesn't receive SmallRye in-memory channels |
| GE-0071 | pattern | quarkus-flow/ | integration pattern, Flow, REST | Integration pattern for wiring Flow workflows to REST endpoints |
| GE-0045 | gotcha | . | WebAuthn, config keys, silently ignored | WebAuthn config properties silently ignored with wrong key names |
| GE-0046 | gotcha | . | WebAuthn, registration, runtime error | WebAuthn registration fails silently without specific config |
```

**`Location` column rules:**
- `cdi/` — entry is in the `cdi/` subdirectory
- `.` — entry is flat in the domain root (no subdirectory yet)
- Path is relative to the domain directory

**Grep target:** Claude greps this file for keywords. Any matching row gives GE-ID + Location → full path is `quarkus/<location>/<GE-ID>.md` (or `quarkus/<GE-ID>.md` if location is `.`).

### Label File (`labels/symptom-silent-failure.md`)

```markdown
# Label: symptom-silent-failure

Entries where the system produces no error, warning, or visible signal — the failure
is only detectable by observing what *didn't* happen. The most time-consuming class
of bugs because normal debugging tools show nothing.

| GE-ID | Domain | Symptom | Path |
|-------|--------|---------|------|
| GE-0048 | tools/claude-code | Large Bash output saves to temp file; cat loops forever | tools/claude-code/GE-0048.md |
| GE-0065 | quarkus/maven | quarkus:dev completes without building anything | quarkus/maven/GE-0065.md |
| GE-0060 | java-panama-ffm/pty | tput reports 0 with no error when TERM env var absent | java-panama-ffm/pty/GE-0060.md |
| GE-0045 | quarkus | WebAuthn config silently ignored with wrong key names | quarkus/GE-0045.md |
```

**Rules:**
- One paragraph description of what this label means and when to use it
- Table has `Domain` column for cross-domain visibility
- `Path` is relative to garden root (not domain-relative)
- Both gotchas and techniques can appear in the same label file

### Label Catalog (`labels/INDEX.md`)

```markdown
# Labels Index

## Symptom Labels (gotchas)
| Label | File | Entries | Description |
|-------|------|---------|-------------|
| symptom-silent-failure | labels/symptom-silent-failure.md | 8 | System fails with no error or warning |
| symptom-startup-ordering | labels/symptom-startup-ordering.md | 3 | Race between initialization phases |
| symptom-native-vs-jvm | labels/symptom-native-vs-jvm.md | 5 | Works in JVM mode, silently fails in native |
| symptom-version-drift | labels/symptom-version-drift.md | 2 | Behaviour differs across library versions |

## Domain Labels (all types)
| Label | File | Entries | Description |
|-------|------|---------|-------------|
| domain-backend | labels/domain-backend.md | 24 | Server-side, APIs, databases, message queues |
| domain-frontend | labels/domain-frontend.md | 0 | Browser, UI components, CSS, bundlers |
| domain-terminals | labels/domain-terminals.md | 9 | Terminal emulators, PTY, shell, tmux |
| domain-mobile | labels/domain-mobile.md | 0 | Android, iOS, cross-platform |
| domain-devops | labels/domain-devops.md | 4 | CI/CD, containers, deployment |
| domain-tooling | labels/domain-tooling.md | 14 | Developer tools, IDEs, CLIs |

## Pattern Labels (techniques)
| Label | File | Entries | Description |
|-------|------|---------|-------------|
| pattern-strategy | labels/pattern-strategy.md | 5 | Design philosophy, architectural choices |
| pattern-testing | labels/pattern-testing.md | 4 | Testing approaches, test doubles, assertions |
| pattern-automation | labels/pattern-automation.md | 3 | Scripts, workflows, tooling automation |
| pattern-performance | labels/pattern-performance.md | 2 | Speed, memory, throughput optimization |
| pattern-token-budget | labels/pattern-token-budget.md | 4 | LLM token efficiency, context management |
```

### Domain README (`quarkus/README.md`)

```markdown
# Quarkus Knowledge

Garden entries for Quarkus 3.x, Quarkus Arc (CDI), SmallRye, Hibernate,
and the Quarkus Maven plugin.

## Sub-domains

| Sub-domain | Directory | Entries | What's Here |
|------------|-----------|---------|-------------|
| CDI / Arc | cdi/ | 3 | Dependency injection, bean lifecycle, profile-based exclusion |
| Maven | maven/ | 2 | quarkus-maven-plugin configuration, dev mode |
| Quarkus Flow | quarkus-flow/ | 4 | Flow workflow engine, consume/listen tasks, serialization |
| Config | (flat) | 1 | MicroProfile config, property resolution |
| WebAuthn | (flat) | 2 | WebAuthn extension configuration |
| Profiles | (flat) | 1 | Build profiles, @IfBuildProfile, @UnlessBuildProfile |

## Cross-references

Related domains: `java/` (Maven fundamentals), `drools/` (Quarkus + Drools testing)
```

---

## The 3-Tier Retrieval Algorithm

![How Retrieval Works — bounded token cost at every tier, no vector database required](../../visuals/screenshots/diagram-2-retrieval.png)

### Tier 1 — Technology Known

*Use when: Claude knows or can infer the technology from the error, stack trace, imports, or conversation context.*

```
1. Read _index/global.md
   → Grep for technology name(s) in Technologies column
   → Get domain sub-index path(s)

2. Read <domain>/INDEX.md
   → Grep for keywords from the error/symptom
   → Get matching GE-IDs and Locations

3. Construct full path:
   → If Location is "." : <domain>/<GE-ID>.md
   → If Location is "subdir/" : <domain>/<subdir>/<GE-ID>.md

4. Read matching entry files (max 3-4)
   → Apply knowledge before proceeding

Token cost: ~150 tokens (global index) + ~600 tokens (domain index)
           + ~300-500 tokens per entry loaded
Typical total: 1,000-1,500 tokens
```

### Tier 2 — Symptom Known, Technology Unknown

*Use when: Claude can describe what it observes (silent failure, startup error, serialization issue) but doesn't yet know which technology is responsible.*

```
1. Read labels/INDEX.md
   → Identify matching symptom or pattern label
   → Get label file path

2. Read labels/<label>.md
   → Scan entries by symptom one-liner
   → Identify 2-4 candidate GE-IDs and paths

3. Read matching entry files by path (direct, no grep)
   → Cross-domain retrieval complete

Token cost: ~200 tokens (labels index) + ~200 tokens (label file)
           + ~300-500 tokens per entry loaded
Typical total: 800-1,400 tokens
```

### Tier 3 — Unknown (Full Scan)

*Use when: Claude cannot identify the technology or symptom type. The entry might be there but retrieval axes are exhausted.*

```
1. Glob _summaries/
   → List all summary file paths

2. Read all summary files
   → Each is ~100 tokens
   → At 100 entries: ~10,000 tokens total
   → At 300 entries: ~30,000 tokens total

3. Identify matches by keyword overlap
   → Select 2-4 most relevant GE-IDs

4. Read full entry files by path (from path field in summary)

Token cost: N × 100 tokens (summaries) + M × 400 tokens (full entries)
Upper bound at 300 entries: ~30,000 + 1,600 = ~32,000 tokens
This is the safety net — not the first choice.
```

### Algorithm Selection Flowchart

```
┌─────────────────────────────────────┐
│ Do I know the technology?           │
│ (Quarkus, Java, tmux, Claude Code…) │
└──────────────┬──────────────────────┘
               │
        YES ───┼─── NO
               │         │
               ▼         ▼
          TIER 1    Do I know the symptom type?
                    (silent failure, startup ordering…)
                         │
                  YES ───┼─── NO
                         │         │
                         ▼         ▼
                    TIER 2      TIER 3
                              (full summary scan)
```

### Critical Constraints

- **Load max 3-4 full entries per query.** "Lost in the middle" (Anthropic 2024): information in the middle of context is less effectively used.
- **Never load a full domain file.** Even if a domain has only 5 entries, always go through the index.
- **Prefer Tier 1 over Tier 2 over Tier 3** — lower tiers cost significantly more tokens.
- **Return the entry path to the user** when reporting findings, so they can navigate directly.

---

## Trigger Model

### Three Complementary Triggers

**Trigger A — Explicit debug hook** (systematic-debugging skill)

The `systematic-debugging` skill receives a Step 0 addition:

> Before any other analysis: check if the garden contains knowledge relevant to this symptom.
> 1. Identify the technology from the error/context
> 2. Apply Tier 1 retrieval (read global index → domain index → load matching entries)
> 3. If relevant entries found: incorporate before proceeding with debugging
> 4. If no match: note it and continue

This fires on every debugging session. Cost is bounded: Tier 1 retrieval costs ~1,000-1,500 tokens — acceptable as overhead on a debugging session that may last thousands of tokens.

**Trigger C — Session start preload** (session routing)

`_index/global.md` (~150 tokens) is cheap enough to read at the start of any coding session in a known technology context. The garden skill (or CLAUDE.md in the relevant project) includes: *"At session start, read `_index/global.md` and keep domain paths in context."* No content loaded — just the routing table. When a symptom is encountered, Tier 1 retrieval is already primed.

**Trigger B — Ambient CSO matching** (garden skill description)

The garden skill's CSO description is updated to include symptom-pattern language:

> Also triggers when Claude encounters a symptom it cannot explain, a failure with no visible error, or a behaviour that contradicts its training knowledge — offer to search the garden before reasoning from first principles.

This fires without explicit user request. Claude pattern-matches "I don't understand why this fails" against the CSO and offers to check the garden. The offer is two sentences; the search runs only if the user confirms.

### Trigger D — Session Core Memory (Domain Deep-Work)

When Claude is doing extended work in a single domain (e.g., a whole session on Quarkus CDI), it can actively promote specific entries to "session-resident" — keeping them in the context window for the duration rather than re-retrieving on each sub-question.

```
Trigger condition: 3 or more retrievals from the same domain sub-domain in a session
Action: Read the top 3-5 most-retrieved entries from that sub-domain into context
         and keep them resident until the session ends or the domain changes.
Cost: One-time load (~1,500 tokens) instead of repeated retrieval costs.
```

This is inspired by MemGPT/Letta's **core memory** concept — a small set of always-in-context items distinct from the archival store that's retrieved on demand. For garden sessions doing deep domain work, promoting a handful of high-`retrieval_count` entries to core memory saves repeated retrieval round-trips and gives Claude richer context throughout.

**Promotion criteria:** prefer entries with high `retrieval_count` in the current domain, entries with `status: active` (not suspected/superseded), and entries whose `keywords` overlap most with the current session's error terms.

### Trigger Priority

| Priority | Trigger | Cost | Reliability |
|----------|---------|------|-------------|
| 1 | A — systematic-debugging step 0 | ~1,200 tokens | High — fires on every debug session |
| 2 | C — session-start global index | ~150 tokens | High — primes retrieval for session |
| 3 | D — session core memory (deep domain work) | ~1,500 tokens one-time | High — fires after 3+ same-domain retrievals |
| 4 | B — ambient CSO matching | 0 tokens until confirmed | Medium — depends on Claude pattern recognition |

---

## Schema Versioning

### SCHEMA.md at Garden Root

```yaml
---
schema-version: 2.0.0
date: 2026-04-07
---
```

Body contains the navigation guide — what each directory/file is for, which retrieval tier to use when. This is what Claude reads first on any garden interaction. It must remain SHORT (under 300 words) — every line competes against task context budget.

The garden skill always reads SCHEMA.md first. The schema version determines which navigation pattern the skill applies. If a future restructure changes the layout, the schema version bumps and the skill is updated to handle both old and new versions during a transition period.

### SchemaVer Rules (Snowplow convention)

| Increment | When | Example |
|-----------|------|---------|
| MODEL | Breaking layout change — directories moved, file format changed, index structure replaced | `1.x.x` → `2.0.0` |
| REVISION | Index restructured, non-breaking to entry files | `2.0.x` → `2.1.0` |
| ADDITION | New label files, new domain added, new index column | `2.1.x` → `2.1.1` |

### What the Garden Skill Does With the Version

```
On any garden interaction:
  1. Read SCHEMA.md
  2. Check schema-version in frontmatter
  3. If version matches expected: proceed normally
  4. If MODEL version differs: warn user — garden structure may have changed,
     skill may need updating
  5. If REVISION or ADDITION differs: proceed normally (backwards compatible)
```

### Keeping SCHEMA.md Current

- Any commit that changes directory structure → must update SCHEMA.md version
- Any commit that changes index file format → must update SCHEMA.md version
- Any commit that adds a new domain → ADDITION bump + update global index row count
- SCHEMA.md changes are validated in the garden's pre-commit check

---

## Workflow Changes

![The Submission Pipeline — write first, deduplicate later; the submitting Claude never loads garden files](../../visuals/screenshots/visual-e-pipeline.png)

### CAPTURE — Changes

**Step 0 (unchanged):** Assign GE-ID from GARDEN.md counter.

**Step 1b (enhanced) — Light duplicate check:**
Read `_index/global.md` → identify relevant domain → read `<domain>/INDEX.md` (not GARDEN.md). The domain index is smaller and faster to scan. GARDEN.md no longer contains index content.

**Step 4 (enhanced) — Determine suggested target:**
Express as: `<domain>/<subdomain>/GE-XXXX.md` or `<domain>/GE-XXXX.md` (flat). The merge Claude decides final placement.

**Step 6 (enhanced) — Write the submission file:**
Submission file now includes the YAML frontmatter block (all fields populated). The merge Claude validates frontmatter at integration time.

**New Step 6b — Propose labels:**
Propose at least one label from the controlled vocabulary in each axis where applicable: at least one `domain-*` label, and for gotchas one `symptom-*` label if the symptom pattern matches an existing label. The user confirms or adjusts. Merge Claude applies the final labels.

### MERGE — Changes

**Step 3 (changed) — Load index:**
Read `_index/global.md` (not GARDEN.md). Read `<domain>/INDEX.md` for relevant domains.

**Step 6 (enhanced) — Integrate new entries:**

For each accepted submission:

1. Write the entry file to its final path (`<domain>/[<subdomain>/]GE-XXXX.md`)
2. Generate the summary file (`_summaries/GE-XXXX.md`) from entry frontmatter
3. Add a row to `<domain>/INDEX.md`
4. Add GE-ID + path to each referenced label file in `labels/`
5. Update entry count in `_index/global.md`
6. Update `GARDEN.md` metadata header (drift counter, last ID)

**Sub-directory creation at merge time:**

Before writing an entry to a domain directory, check if the sub-domain now has ≥3 entries:
- If yes and no sub-directory exists: create `<domain>/<subdomain>/`, move the ≥3 entries, update `<domain>/INDEX.md` Location column for all moved entries, update `_summaries/` path fields for all moved entries, update all label files with new paths.
- This is the "automatic sub-directory promotion" rule.

**Step 7 (unchanged):** Remove processed submissions.

**Step 8 (enhanced) — Commit:**
Stage: entry file(s) + `_summaries/` updates + `<domain>/INDEX.md` + `labels/` updates + `_index/global.md` + `GARDEN.md`.

### DEDUPE — Changes

**Step 1:** Read `_index/global.md` + `labels/INDEX.md` (not GARDEN.md).

**Step 3 (enhanced):** Load entries by direct path from domain INDEX.md — no grep-within-file.

**Step 5 (enhanced):** Update `CHECKED.md`. If an entry is discarded, also remove it from `_summaries/`, `<domain>/INDEX.md`, all label files, and `_index/global.md` entry count.

### SEARCH — Replaced by 3-Tier Retrieval Algorithm

The old SEARCH workflow (read GARDEN.md → follow file link → grep if not found) is replaced entirely by the 3-tier retrieval algorithm described above.

### IMPORT — Ingesting External Sources *(Phase 2+)*

**Use when:** Ingesting non-obvious knowledge from external sources rather than from a debugging session. Sources: library changelogs, GitHub issues/PRs discussing non-obvious fixes, CVE databases, documentation buried in source code comments, community discussions that surface gotchas.

This workflow addresses the Karpathy-inspired pattern: raw external material compiled into structured garden entries. It is distinct from CAPTURE (which extracts from a live session) — IMPORT extracts from external documents.

```
Step 1 — Assess the source
  → Is this a primary source (library changelog, GitHub issue, CVE) or secondary (blog post)?
  → Primary sources are preferred; secondary may duplicate content
  → Is the content cross-project? (Not project-specific logic)

Step 2 — Extract candidate entries
  → Read the source (changelog section, issue body, CVE description)
  → Identify garden-worthy knowledge using the same editorial bar as CAPTURE
  → Apply Garden Score; only proceed for score ≥ 8

Step 3 — Classify and map
  → Classify as gotcha / technique / undocumented
  → Map to domain (which technology domain does this belong to?)
  → Check if an existing entry already covers this (Level 1 duplicate check)

Step 4 — Draft and submit
  → Draft using CAPTURE workflow (Step 3 onward)
  → In submission frontmatter, add source attribution:
     source_url: https://github.com/quarkusio/quarkus/issues/12345
     source_type: github-issue  # or: changelog | cve | documentation | community
  → Submit as normal

Step 5 — Report
  → Tell user: N candidates extracted, M submitted, K below threshold
```

**Source attribution fields** (added to YAML frontmatter for IMPORT entries):

```yaml
source_url: https://github.com/...
source_type: github-issue   # github-issue | changelog | cve | documentation | community
source_date: 2026-03-15
```

**Automation potential (future):** A GitHub Action that monitors watched repositories for merged PRs containing non-obvious fixes, and auto-offers IMPORT. The action detects PRs tagged with "bug" or "fix" that have multi-paragraph descriptions, and surfaces them to the garden maintainer as IMPORT candidates.

### QUERY-BACK — Filing Explorations Into the Garden *(Phase 2+)*

*The "queries compound knowledge" pattern.*

When a garden search session produces useful synthesis — Claude answers a question by combining multiple garden entries in a non-obvious way, or discovers a gap the garden doesn't cover — that synthesis can be filed back into the garden as a new entry or REVISE.

**Trigger:** At the end of a session where the garden was consulted, Claude offers:
> "The combination of GE-0033 + GE-0066 reveals a pattern not captured in either entry individually: [synthesis]. Worth adding as a technique entry?"

If yes: run CAPTURE with the synthesised knowledge as the content. The entry is real, valuable knowledge — the fact that it came from combining existing entries doesn't make it less valid.

**Why this matters:** The garden compounds over time. Each exploration adds to it. This is Karpathy's key insight applied to the garden's governance model: "explorations compound in the knowledge base just like ingested sources do."

---

## Three-Level Duplication System

Duplication checking runs at three distinct levels with increasing depth, decreasing frequency, and increasing cost. Each level is assigned to the appropriate automation tier (CI/Code, Agent, Human) to minimise token spend.

```
Level 1 ── Submitter light check ── at capture time ── cheap, fast
Level 2 ── Integration check ────── at merge time ──── moderate, catches overlaps
Level 3 ── Systematic review ─────── periodic ──────── expensive, comprehensive
```

### Level 1 — Submitter Light Check (at CAPTURE)

**Actor:** Submitting Claude (or the CI validate step in GitHub mode as a supplement)
**Goal:** Catch obvious duplicates before drafting a full submission — avoid wasting a PR on something that already exists.
**Cost:** Index reads only. Entry body files are never read at this level.

**Algorithm:**

```
1. Is the knowledge already in context from this session?
   → YES, and it's an existing entry → pivot to REVISE, not CAPTURE
   → YES, already submitted this session → skip

2. Read _index/global.md
   → Identify the relevant domain row(s)

3. Read <domain>/INDEX.md
   → Scan keywords column and symptom column for the new entry's keywords
   → Flag any existing entry with symptom similarity > 70% (keyword overlap)

4. If flagged: read the _summaries/ file for each flagged GE-ID (cheap, always materialised)
   → Compare summaries to the new entry
   → If clearly the same thing → offer REVISE instead
   → If different angle → note the GE-IDs checked, proceed with CAPTURE

5. Log which GE-IDs were scanned (for CHECKED.md update at MERGE)
```

**Outcomes:**
- **Proceed** — no significant overlap found; submit as new entry
- **Pivot to REVISE** — submission enriches an existing entry; use that GE-ID as Target ID
- **Skip** — obvious duplicate already in context; do not submit

**What v2 improves:**
- Old: scan GARDEN.md for title similarity only
- New: scan domain INDEX.md keywords + symptom columns → semantic richness without reading entry bodies
- `_summaries/` available for the flagged subset → quick confirm/reject before any full entry load

**What Level 1 cannot catch:** Two entries with different titles and different keywords that describe the same underlying problem from different angles. That requires Level 2.

---

### Level 2 — Integration Check (at MERGE)

**Actor:** MERGE Claude (local mode) — or CI Python for mechanically detectable overlaps, then Claude for judgment (GitHub mode)
**Goal:** Catch overlaps before an entry is permanently integrated. Handles the 1..n overlap case where a single submission may partially overlap with multiple existing entries.
**Cost:** Moderate — reads portions of candidate entry files. Bounded by how many candidates Level 1 flagged.

**Algorithm:**

```
1. Load submission YAML frontmatter
   → Extract domain, keywords, symptom, type

2. Run Python pre-screen (CI/Code tier — zero tokens)
   → Exact GE-ID collision → CRITICAL (shouldn't reach MERGE)
   → Check DISCARDED.md → if submission's content was already discarded, discard again
   → Keyword Jaccard overlap > 0.6 with same-domain entries → flag candidate list

3. For each flagged candidate (Agent/Claude tier)
   → Read _summaries/GE-XXXX.md for the candidate (cheap, materialised)
   → Initial relevance: does the summary suggest the same problem?
   → If yes: load full entry file via git cat-file or Read
   → Compare: symptom, root cause, context

4. Classify each candidate relationship
   → DUPLICATE: same symptom, same root cause, same context → discard submission
   → ENRICHMENT: submission adds solution/alternative/context to existing entry → REVISE
   → RELATED: same technology area, different problem → note cross-reference only
   → DISTINCT: superficially similar keywords, genuinely different problem → proceed

5. Handle 1..n overlaps
   → Submission overlaps with entry A (enrichment) AND entry B (related)
   → Action: pivot to REVISE for A, add See-also cross-reference to B in the submission
   → Submission overlaps with entries A, B, C (all duplicates from different sessions)
   → Action: discard submission, log all three GE-IDs in DISCARDED.md
```

**Outcomes (per overlap):**

| Relationship | Action | Files updated |
|---|---|---|
| **Duplicate** | Discard submission | `DISCARDED.md` + CHECKED.md |
| **Enrichment (1 entry)** | Pivot to REVISE workflow | Existing entry + `_summaries/` + domain INDEX.md |
| **Enrichment (n entries)** | Discard; submitter files targeted REVISE per entry | `DISCARDED.md` with note |
| **Related (cross-ref)** | Accept new entry; add `See also` to both | Both entry files + CHECKED.md |
| **Distinct** | Accept and integrate | Normal MERGE path |

**Log every comparison to CHECKED.md** — even pairs classified as distinct. The pair is recorded so Level 3 doesn't re-check it.

**What v2 improves:**
- Old: `grep -A 30 "## Entry Title"` within a grouped file — loads other entries as overhead
- New: `Read <domain>/cdi/GE-0066.md` — loads exactly the candidate, nothing else
- `_summaries/` pre-screening at step 3 eliminates most full entry reads

---

### Level 3 — Systematic Review (DEDUPE)

**Actor:** Dedicated Claude session (local mode) — or scheduled GitHub Actions job combining Python pre-screen with Claude judgment session (GitHub mode)
**Goal:** Find near-duplicates that slipped through Levels 1 and 2 individually — two entries submitted months apart with different keywords but describing the same underlying problem.
**When:** Drift threshold exceeded (`Entries merged since last sweep ≥ 10`) OR explicit user request.
**Cost:** Expensive — O(N²) pairs within domains. Bounded by the within-domain constraint and CHECKED.md exclusion.

**Algorithm:**

```
1. Read _index/global.md → enumerate all technology domains

2. For each domain:
   → Read <domain>/INDEX.md → list all GE-IDs in this domain
   → Generate all within-domain pairs: (GE-0033, GE-0066), (GE-0033, GE-0062), ...
   → Read CHECKED.md → exclude already-verified pairs
   → Remaining pairs = unchecked candidates for this sweep

3. Cross-domain pairs: NEVER generated — skip entirely
   (quarkus/ entries cannot duplicate tools/ entries; the domain boundary is the check boundary)

4. Python pre-screen (CI/Code tier — zero tokens)
   For each unchecked pair:
   → Read both _summaries/ files (cheap, always materialised)
   → Compute keyword Jaccard: intersection / union of keywords lists
   → Jaccard < 0.35 → classify DISTINCT immediately, log to CHECKED.md, skip full read
   → Jaccard ≥ 0.35 → promote to Agent review

5. Agent review for promoted pairs (Claude — tokens spent only here)
   For each high-Jaccard pair:
   → Load both full entry files (git cat-file --batch for efficiency)
   → Compare: symptom description, root cause mechanism, context, fix approach
   → Classify: distinct / related / duplicate

6. Resolve each classified pair:
   → DISTINCT: log to CHECKED.md as `distinct | <date>`
   → RELATED: add `**See also:** GE-XXXX [title]` to both entries; log as `related | <date>`
   → DUPLICATE: present both to user; keep more complete entry; discard the other

7. For discarded duplicates:
   → Remove entry file, _summaries/ file, domain INDEX.md row, labels/ entries
   → Add to DISCARDED.md: `| GE-XXXX | GE-YYYY | duplicate-discarded | <date>`
   → Log pair to CHECKED.md as `duplicate-discarded | <date>`

8. Reset drift counter in GARDEN.md:
   → `Last full DEDUPE sweep: YYYY-MM-DD`
   → `Entries merged since last sweep: 0`
```

**CHECKED.md structure (unchanged role, updated format):**

```markdown
| Pair | Result | Date | Notes |
|------|--------|------|-------|
| GE-0033 × GE-0066 | distinct | 2026-04-07 | same tech, different problem |
| GE-0062 × GE-0066 | related | 2026-04-07 | cross-referenced |
| GE-0068 × GE-0069 | distinct | 2026-04-07 | |
| GE-0031 × GE-0065 | duplicate-discarded | 2026-05-01 | GE-0065 kept (more complete) |
```

Pairs are always written `lower-ID × higher-ID` so lookups are deterministic.

**What v2 improves:**
- Old: `grep -A 40 "## Entry Title"` to read each candidate → loads other entries as overhead
- New: `git cat-file --batch` with two paths → one network round-trip, exactly two entries loaded
- `_summaries/` pre-screening at step 4 eliminates full entry reads for ~60% of pairs (those with Jaccard < 0.35)
- Domain INDEX.md keywords column feeds Python Jaccard without ANY entry file reads

**Scale projections for Level 3:**

| Garden size | Within-domain pairs | After CHECKED.md exclusion | Pre-screened out (Jaccard < 0.35) | Full reads needed |
|-------------|--------------------|-----------------------------|----------------------------------|-------------------|
| 78 entries | ~200 | ~50 (first sweep) | ~30 | ~20 pairs (40 entry reads) |
| 300 entries | ~3,000 | ~300 (typical sweep) | ~200 | ~100 pairs (200 entry reads) |
| 1,000 entries | ~30,000 | ~1,000 (typical sweep) | ~700 | ~300 pairs (600 entry reads) |

At 300 entries, a typical Level 3 sweep (after pre-screening) reads ~200 summary files (20,000 tokens) + ~200 full entries (80,000 tokens) = ~100,000 tokens total. This is large but bounded and infrequent (run every 10 new entries, not daily).

---

### Three-Level System: Automation Assignment

| Level | Trigger | CI/Code does | Agent does | Human does |
|-------|---------|-------------|------------|------------|
| **L1 — Submitter** | Every CAPTURE | Jaccard on keywords (GitHub mode only) | Index scan, summary compare, proceed/REVISE decision | — |
| **L2 — Integration** | Every MERGE | Exact match, Jaccard > 0.6 flag | Semantic comparison of flagged pairs, 1..n overlap resolution | Confirm discard of borderline cases |
| **L3 — Systematic** | Drift threshold | Pre-screen all pairs via Jaccard on summaries | Judgment on high-Jaccard pairs, resolve duplicates | Approve deletion of duplicated entries |

**The guiding principle:** Each level passes work upward only when it cannot make the decision mechanically. Level 3 reads full entries only for pairs that Level 1 (Python Jaccard) flagged as high-overlap. The token cost is proportional to how many genuine near-duplicates exist, not to the total garden size.

---

## Quality and Bit Rot Prevention

**The garden's value degrades in two independent dimensions: individual entries becoming wrong, and the collective system becoming less findable and coherent.** Structural checks catch the first. A continuous quality cycle catches the second.

> **Phase 1 scope within this section:** Only the [Automated Integrity Checks](#automated-integrity-checks-cicode-level) and the [Entry Lifecycle](#entry-lifecycle) states (Active/Suspected/Superseded/Retired) are Phase 1 deliverables. The Periodic Coherence Review, Coverage Review, health score, and most of the Known Open Problems are Phase 2+. The full quality system is documented here as the target state.

This section defines the quality model, the failure taxonomy, the automated gates, the periodic review process, the entry lifecycle, and the health metrics. Not all of this is immediately implementable — some items are documented now so they can be built incrementally as the garden grows. The continuous quality cycle means these concerns are revisited at every milestone, not resolved once and forgotten.

### The Three-Level Automation Principle (Applied to Quality)

The same principle that governs duplication governs quality: push every check as low as possible.

| Level | Who | For quality: |
|-------|-----|-------------|
| **CI/Code** | Python, GitHub Actions | Structural integrity — index sync, cross-references, vocabulary compliance, summary freshness |
| **Agent (Claude)** | Periodic session | Content accuracy, coherence, keyword effectiveness, coverage gaps |
| **Human** | On-demand | Retirement decisions, major quality policy changes, judgment calls flagged by Agent |

---

### Failure Mode Taxonomy

**Four categories of rot, each with distinct causes and mitigations.**

#### 1. Structural Rot (always detectable mechanically)

The indexes, summaries, and cross-references diverge from the actual entry files. Individual entries may be correct, but the infrastructure that makes them findable is broken.

| Failure | Symptom | Cause |
|---------|---------|-------|
| Missing index row | Entry file exists, no row in domain INDEX.md | Entry added directly, bypassing MERGE |
| Summary drift | `_summaries/GE-XXXX.md` keywords diverge from entry frontmatter | Entry updated but summary not regenerated |
| Broken cross-reference | `See also: GE-0033` points to merged or moved entry | DEDUPE merge without updating referencing entries |
| Label vocabulary drift | Entry frontmatter references label not in `labels/INDEX.md` | Label renamed or removed without updating entries |
| Orphaned entry | Entry file exists in directory with no INDEX.md row | Domain directory restructured, INDEX.md not updated |
| Global count mismatch | `_index/global.md` entry count ≠ actual file count | Entries added or removed without updating global index |
| SCHEMA.md stale | `schema-version` doesn't match actual structure | Structure changed without version bump |

**Mitigation:** CI runs `validate_garden.py --structural` on every push to main. All structural checks are binary. Zero tolerance — non-zero exit blocks the push.

#### 2. Freshness Rot (partially automated, partly Agent)

Entries were accurate when written but have since been superseded. The entry's Fix section may now describe the wrong approach, or the bug may have been resolved upstream.

| Failure | Symptom | Cause |
|---------|---------|-------|
| Version obsolescence | "Quarkus 3.x" but Quarkus 5.x is now current | Library releases outpace garden maintenance |
| Resolved but unlabelled | Bug was fixed in a newer version; no `resolved-in:` field | Nobody filed a REVISE when the fix shipped |
| Deprecated technique | Fix section recommends an approach the library has since deprecated | API evolution |
| Stale context | `context:` field describes conditions that no longer exist | Framework or tool behaviour changed |

**Mitigation (CI level — scheduled weekly):** Scan all entries with version strings in `stack` frontmatter. Check PyPI, Maven Central, and npm for current stable major version. Flag entries where the referenced version is 2+ major versions behind current. Note: per-entry staleness thresholds (90 days for version-pinned gotchas, 365 days for general techniques) are defined in the `staleness_threshold` frontmatter field — see [File Format Specifications](#file-format-specifications).

**Mitigation (Agent level — on DEDUPE sweep):** Review flagged entries for actual staleness. Recommend: add `resolved-in:` field, update Fix section, or open a REVISE submission.

#### 3. Coherence Rot (Agent only)

No single entry is wrong, but the garden as a whole tells an inconsistent or confusing story. Entries contradict each other, cross-references form poor clusters, or the same problem is described from incompatible angles in different entries.

| Failure | Symptom | Cause |
|---------|---------|-------|
| Contradictory entries | GE-A says "always use X"; GE-B says "never use X" | Both correct in different contexts, but context not specified |
| Missing cross-references | GE-A and GE-B clearly related, no `See also` link | Each was added in a separate session, no DEDUPE yet |
| Redundant vocabulary | Three entries use different keywords for the same concept | No keyword normalisation at capture |
| Keyword effectiveness degradation | Retrieval misses known relevant entries | Keywords chosen at capture don't match how problems are actually described |
| Sub-domain incoherence | 15 entries in `quarkus/cdi/` tell overlapping stories with no clear structure | Grew organically without a coherence review |

**Mitigation (Agent level — periodic coherence sweep):** See [Periodic Coherence Review](#periodic-coherence-review).

#### 4. Coverage Rot (Agent only)

Important knowledge is missing from the garden. The capture habit is working for some domains but not others. Known important problems are unrecorded.

| Failure | Symptom | Cause |
|---------|---------|-------|
| Domain underrepresentation | Technology is heavily used but has very few entries | Capture habit not triggered in those sessions |
| Label with zero entries | A label in `labels/INDEX.md` has no entries | Label created speculatively, never used |
| Forgotten gotchas | A known non-obvious problem recurs in multiple sessions | Entry was never captured |
| Entry type imbalance | 90% gotchas, 0% techniques | The technique capture trigger isn't firing |

**Mitigation (Agent level — periodic coverage review):** See [Periodic Coverage Review](#periodic-coverage-review).

---

### Automated Integrity Checks (CI/Code Level)

**Runs on every push to main. All checks are binary. Structural rot is zero-tolerance.**

```python
# validate_garden.py --structural
# Exit 0 = clean. Non-zero = blocked.

def check_structural_integrity(garden_root):
    entries = glob_all_entries(garden_root)       # all GE-*.md files
    index_ids = load_all_index_ids(garden_root)   # all GE-IDs in domain INDEX.md files
    summary_ids = glob_summary_ids(garden_root)   # all GE-IDs in _summaries/
    label_vocab = load_label_vocab(garden_root)   # labels/INDEX.md

    for entry in entries:
        fm = parse_frontmatter(entry)
        geid = fm['id']

        # 1. Every entry has an index row
        assert geid in index_ids,           f"CRITICAL: {geid} missing from domain INDEX.md"

        # 2. Every entry has a summary file
        assert geid in summary_ids,         f"CRITICAL: {geid} missing from _summaries/"

        # 3. Summary frontmatter matches entry frontmatter (key fields)
        summary = parse_summary(geid)
        assert summary['keywords'] == fmt_keywords(fm['keywords']),  \
                                            f"CRITICAL: {geid} summary keywords diverge from entry"
        assert summary['labels'] == fmt_labels(fm['labels']),        \
                                            f"CRITICAL: {geid} summary labels diverge from entry"
        assert summary['path'] == relative_path(entry),              \
                                            f"CRITICAL: {geid} summary path is wrong"

        # 4. All labels in controlled vocabulary
        for label in fm['labels']:
            assert label in label_vocab,    f"CRITICAL: {geid} uses unknown label: {label}"

        # 5. All See-also cross-references are valid GE-IDs
        for ref in extract_see_also(entry):
            assert ref in index_ids,        f"CRITICAL: {geid} has broken See-also: {ref}"

    # 6. Global index counts match actual file counts per domain
    for domain, count in load_global_counts(garden_root).items():
        actual = count_domain_entries(garden_root, domain)
        assert count == actual,             f"CRITICAL: {domain} count {count} ≠ actual {actual}"

    # 7. No orphaned files (entry in directory with no INDEX.md row)
    for entry in entries:
        domain = infer_domain(entry)
        domain_index_ids = load_domain_index(garden_root, domain)
        geid = parse_frontmatter(entry)['id']
        assert geid in domain_index_ids,    f"CRITICAL: {geid} is orphaned in {domain}/"

    # 8. SCHEMA.md version present and well-formed
    schema = parse_schema(garden_root)
    assert 'schema-version' in schema,      f"CRITICAL: SCHEMA.md missing schema-version"
    assert 'backend' in schema,             f"CRITICAL: SCHEMA.md missing backend field"
```

**Runs weekly (scheduled CI):**

```python
# validate_garden.py --freshness
# Exit 0 = clean. Non-zero = WARNING (advisory, not blocking).

def check_freshness(garden_root):
    for entry in glob_all_entries(garden_root):
        fm = parse_frontmatter(entry)

        # 1. Entries with version strings: check for major version lag
        for lib, version in extract_versioned_stack(fm['stack']):
            current = fetch_current_major_version(lib)   # PyPI / Maven / npm
            if current and major(version) < current - 1:
                warn(f"{fm['id']}: {lib} {version} is {current - major(version)} major versions behind")

        # 2. Entries with no REVISE submissions in > 24 months
        last_touched = git_last_modified(entry)
        if months_since(last_touched) > 24 and 'resolved-in' not in fm:
            warn(f"{fm['id']}: no REVISE in 24 months — review for staleness")

        # 3. Entries flagged resolved: check resolved version vs current
        if 'resolved-in' in fm:
            lib, version = parse_resolved_in(fm['resolved-in'])
            current = fetch_current_major_version(lib)
            if current and major(version) < current:
                info(f"{fm['id']}: resolved in {version}, current is {current}.x — entry may be archivable")
```

---

### Entry Lifecycle

![Entry Lifecycle — quality degrades over time; the lifecycle makes that explicit rather than hiding it](../../visuals/screenshots/diagram-4-lifecycle.png)

Entries move through defined states. **Entries are almost never deleted** — the git history is the archive. Only entries that are actively misleading (wrong Fix, dangerous advice) are removed; all others are retained through Superseded or Retired states where they carry forward pointers and historical context.

Research finding: marking something Superseded without immediately removing it is a feature, not a bug. Engineers encountering old code that references the entry need to understand the historical context before finding the replacement.

```
SUBMISSION
    │
    ├─ Level 1 check ──► (discard if obvious duplicate)
    │
PENDING (submissions/ directory)
    │
    ├─ Level 2 check ──► (discard / REVISE / accept)
    │
KNOWN-GAP              ← status: known-gap
    │                    We know something non-obvious exists here but haven't
    │                    captured it yet. A placeholder that makes the gap visible.
    │                    symptom describes what we know; Fix says "Unknown — under investigation"
    │                    Retrieval returns it with a "help wanted" caveat
    │                    priority field signals urgency: critical | high | normal (default)
    │                    Promoted to ACTIVE when the knowledge is captured
    │
ACTIVE                 ← status omitted from frontmatter (default)
    │                    verified: date is current
    │
    ├─ staleness_threshold exceeded ──► SUSPECTED  (status: suspected)
    │                                   CI sets this automatically
    │                                   Entry still readable but shows caveat
    │                                   Agent/human review pending
    │                         │
    │                         ├─ Reviewed, still accurate ──► back to ACTIVE
    │                         │                               (verified: updated)
    │                         │
    │                         ├─ Bug fixed upstream ──► SUPERSEDED  (status: superseded)
    │                         │                          superseded_by: GE-XXXX (or resolved_in: version)
    │                         │                          Entry retained; points to replacement
    │                         │
    │                         └─ Tech obsolete / entry wrong ──► RETIRED  (status: retired)
    │                                                              Entry hidden from retrieval
    │                                                              Retained in git history
    │
    └─ Actively dangerous (wrong fix, bad advice) ──► REMOVED  (git rm, very rare)
                                                       Recorded in DISCARDED.md
```

**How each state affects retrieval:**

| Status | Appears in domain INDEX.md | Returned by retrieval | Shown with caveat |
|--------|---------------------------|----------------------|-------------------|
| Active | ✅ Yes | ✅ Yes | No |
| Suspected | ✅ Yes | ✅ Yes — with staleness warning | ⚠️ Yes |
| Superseded | ⚠️ Dimmed row with pointer | ⚠️ Only if no active replacement matches | ⚠️ Yes — with forward pointer |
| Retired | ❌ Removed from index | ❌ No | — |
| Removed | ❌ Removed from index | ❌ No | — |

**Suspected state in practice:**

The Suspected state prevents silent trust. When CI flags an entry as Suspected, it:
1. Sets `status: suspected` in the entry frontmatter
2. Regenerates the `_summaries/` file to include the status
3. Appends `⚠️ SUSPECTED STALE` to the domain INDEX.md row
4. Does NOT remove the entry from retrieval — it is still returned but with a visible warning

When a Suspected entry is retrieved during debugging, Claude notes the caveat and suggests verification before relying on the Fix section.

**Staleness threshold is per entry, not per type:**

A gotcha about a specific Quarkus 3.8 CDI bug (version-pinned) needs a 90-day threshold. A technique for using sparse checkout in git (tool-stable) can tolerate 365 days. The `staleness_threshold` frontmatter field makes this explicit per entry rather than relying on a global policy.

**The "capture triggers review" pattern:**

When a new entry is added to domain X, the MERGE workflow includes a step: *re-read existing entries in the same sub-domain and check if any should be updated, cross-referenced, or have their `verified` date refreshed.* This makes maintenance a side effect of capture — sustainable without dedicated review sessions.

---

### Periodic Coherence Review

**Trigger:** User request ("coherence review", "quality sweep") OR after Level 3 DEDUPE finds > 3 related pairs in a domain. **Actor:** Claude (Agent level).

```
For each domain with ≥ 5 entries:

1. Read domain INDEX.md + all entry files in the domain (one focused read session)

2. Check for contradictions
   → Does any entry say "always do X" while another says "avoid X"?
   → If yes: flag both, assess whether context clauses distinguish them
   → If genuinely contradictory: flag for human resolution

3. Check cross-reference completeness
   → For each pair of related entries (assessed semantically): do they cross-reference each other?
   → Missing See-also links: add them

4. Check keyword normalisation
   → Are the same concepts described with different vocabulary across entries?
   → Example: one entry uses "CDI injection" another uses "dependency injection" — normalise to preferred term
   → Update keywords fields in affected entries
   → Update domain INDEX.md keywords column

5. Check sub-domain structure
   → If domain has > 10 entries in a flat directory (no sub-dirs): does sub-division make sense?
   → Propose sub-directory reorganisation if natural groupings exist

6. Produce coherence report:
   → N contradictions found (K resolved, M flagged for human)
   → N cross-references added
   → N keyword normalisations applied
   → Sub-directory reorganisation proposed: yes/no
```

---

### Periodic Coverage Review

**Trigger:** User request ("coverage review") OR quarterly. **Actor:** Claude (Agent level).

```
1. Load _index/global.md + all domain INDEX.md files

2. Domain coverage analysis
   → Which domains have ≥ 1 entry per 20 hours of estimated usage? (rough heuristic)
   → Which domains used heavily in projects but have < 3 entries?
   → Flag potential coverage gaps

3. Label coverage analysis
   → Which labels have 0 entries? → candidate for removal from vocabulary
   → Which labels have 1 entry? → possibly too specific; merge with broader label
   → Which entries have no symptom label (gotchas)? → flag for label addition

4. Known-gap priority review
   → List all `status: known-gap` entries sorted by `priority` (critical → high → normal)
   → `priority: critical` gaps are flagged to maintainers immediately — not deferred to next review
   → For each critical gap: who is best placed to capture it? (based on domain ownership and contributor history)
   → Coverage report opens with known-gaps at the top if any are critical

4. Entry type balance
   → What is the gotcha / technique / undocumented ratio?
   → If techniques < 20% of entries: the technique capture trigger may not be firing
   → If undocumented < 5%: may be under-capturing discovered-but-undocumented behaviours

5. Recency distribution
   → What is the distribution of entry ages?
   → If > 30% of entries are > 18 months old with no REVISE: freshness risk
   → If most entries are < 3 months old: garden is young, staleness not yet a concern

6. Search analytics (future — requires instrumentation)
   → Log every garden query and whether it returned a match
   → Queries with no match across all tiers → flag as coverage gap candidates
   → Repeated no-match queries on the same topic → strong signal for KNOWN-GAP entry
   → This closes the loop: queries that fail become `status: known-gap` entries;
     CAPTURE eventually promotes them to ACTIVE

6. Produce coverage report:
   → Domains flagged for potential gaps: [list]
   → Labels recommended for removal: [list]
   → Entry type balance: [ratio]
   → Recency risk: [low / medium / high]
   → Recommended actions: [ordered list]
```

---

### Health Metrics

The garden's health is measurable. These metrics feed the coverage and coherence reviews and provide an at-a-glance quality signal.

| Metric | Healthy | Warning | Critical | Measured by |
|--------|---------|---------|----------|-------------|
| **Index sync gap** | 0 | 1-2 | ≥ 3 | CI structural check |
| **Summary drift** | 0 entries | 1-3 | ≥ 4 | CI structural check |
| **Broken cross-references** | 0 | 1-2 | ≥ 3 | CI structural check |
| **Label vocabulary drift** | 0 | 1 | ≥ 2 | CI structural check |
| **Suspected entries** | 0-3 | 4-10 | > 10 | CI freshness check (weekly) |
| **Superseded entries (unreviewed > 6 months)** | 0 | 1-3 | ≥ 4 | CI freshness check |
| **Version lag (2+ majors behind)** | 0 flagged | 1-5 | ≥ 6 | CI freshness check (weekly) |
| **Empty labels** | 0 | 1-2 | ≥ 3 | Coverage review |
| **DEDUPE drift** | < 5 | 5-9 | ≥ 10 | GARDEN.md counter |
| **Level 3 Jaccard > 0.5 pairs per sweep** | 0-3 | 4-10 | > 10 | DEDUPE report |
| **Entries with no `verified` date update in 12 months** | 0-10% | 10-25% | > 25% | CI freshness check |
| **Known-gap entries with `priority: critical`** | 0 | 1-2 | ≥ 3 | Coverage review — critical gaps need urgent capture |
| **High `retrieval_count`, low `helpfulness_score`** | 0 | 1-3 | ≥ 4 | MCP instrumentation — retrieved but not useful → keyword mismatch |

**Anti-metric warning:** Retrieval hit count is a vanity metric. An entry accessed frequently may be accessed *because it is wrong* and developers keep second-guessing it. Do not treat high access count as a signal of quality. Treat it as a signal worth investigating.

**DORA quality dimensions** (applied to garden entries): The DORA framework defines documentation quality by clarity, findability, and reliability. For the garden this maps to: *"Did following this entry's Fix section produce the expected result without additional research?"* This is the ultimate quality test — not whether the entry is internally consistent, but whether it works.

**Garden health score** — a single number computed from the above:

```python
def garden_health_score(metrics):
    """Returns 0 (broken) to 100 (perfect). Advisory only."""
    deductions = 0
    deductions += metrics['index_sync_gap'] * 10          # each missing row = -10
    deductions += metrics['broken_cross_refs'] * 8        # each broken ref = -8
    deductions += metrics['summary_drift_count'] * 5      # each stale summary = -5
    deductions += metrics['version_lag_count'] * 2        # each lagging version = -2
    deductions += metrics['stale_pct'] * 50               # 10% stale = -5
    deductions += metrics['empty_label_count'] * 3        # each empty label = -3
    return max(0, 100 - deductions)
```

Score ≥ 90: healthy. Score 70-89: review recommended. Score < 70: quality sweep required before next major use.

---

### Quality Gates at Each Workflow Step

Every workflow interaction is a quality gate opportunity.

| Workflow | CI/Code gate | Agent gate | Human gate |
|----------|-------------|------------|------------|
| **CAPTURE** | — | L1 duplicate check, score threshold | — |
| **PR open (GitHub)** | Format, vocabulary, Jaccard duplicate, injection scan | — | — |
| **MERGE** | Exact duplicate, index update, summary generation | L2 semantic duplicate, 1..n overlap resolution | Confirm borderline discards |
| **DEDUPE** | Jaccard pre-screen of all pairs | L3 semantic judgment, coherence fixes | Approve entry deletion |
| **Push to main** | `validate_garden.py --structural` (blocks if non-zero) | — | — |
| **Weekly scheduled** | `validate_garden.py --freshness` (advisory) | — | — |
| **Coherence review** | — | Domain coherence, keyword normalisation | Resolve contradictions |
| **Coverage review** | — | Domain gaps, label cleanup, type balance | Policy decisions |

---

### The Continuous Quality Cycle

Quality is not a milestone — it is a recurring rhythm. This diagram is the intended operational cadence:

```
Every CAPTURE/MERGE ──► Structural CI gate (seconds, always)
        │
Every 10 merges ────────► Level 3 DEDUPE sweep (offered automatically)
        │
Weekly (scheduled) ─────► Freshness check (CI, advisory)
        │
Every 3 months ─────────► Coherence review (Agent session)
Every 6 months ─────────► Coverage review (Agent session)
        │
As needed ──────────────► Entry lifecycle updates (REVISE, resolved-in, deprecated)
        │
Annually ───────────────► Quality policy review (Human)
                           — Is the score threshold still right?
                           — Does the label taxonomy need pruning?
                           — Are the health metric thresholds appropriate?
```

### Known Open Problems

**These are documented here so they are not forgotten. They are not blocking — the garden is useful without solving them — but each represents a known quality risk that should be revisited as the garden matures.**

| Problem | Risk | Current mitigation | Future direction |
|---------|------|--------------------|-----------------|
| Keyword effectiveness is not measured | Retrieval misses known entries | Periodic Agent keyword review | Track retrieval hit rates per entry; entries with 0 hits over N sessions are candidates for keyword update |
| Dead link detection not implemented | Fix sections reference URLs that return 4xx | Manual review when encountered | Add `scripts/check_links.py` to weekly CI — scan all URLs in body text, flag 4xx responses as WARNING |
| Quality score self-reporting | Submitter scores their own entry | CI enforces range (1-15), not accuracy | Periodic Agent re-scoring of older entries against current rubric |
| Content accuracy not validated | Fix section may become wrong after library changes | Freshness CI flags old versions; human reviews flagged entries | Automated regression testing of Fix sections (feasible for code-based fixes) |
| Coverage gaps are passive | We don't know what we don't know | Coverage review surfaces domains with suspiciously few entries | Session-end prompting: "any non-obvious knowledge from today that isn't in the garden yet?" |
| Coherence review is reactive | Incoherence accumulates between reviews | Level 3 DEDUPE surfaces related entries | Proactive: flag when a new entry's domain has > 10 entries with no recent coherence review |
| Summary keyword drift | _summaries/ can diverge silently after REVISE | CI summary drift check | Auto-regenerate summaries on every MERGE — never allow manual editing of summary files |
| Label taxonomy evolution | Labels grow stale as new patterns emerge | Annual human policy review | Formal label lifecycle: proposed → accepted → deprecated → removed |

### Controlled Vocabulary

All labels must come from this list. New labels require explicit addition to the list and to `labels/INDEX.md`.

**Symptom labels** (for gotchas — what Claude observes):

| Label | When to Use |
|-------|-------------|
| `symptom-silent-failure` | System fails with no error, warning, or visible signal |
| `symptom-startup-ordering` | Race between initialisation phases; resolves before/after expected |
| `symptom-native-vs-jvm` | Works in JVM mode, silently fails or behaves differently in native image |
| `symptom-version-drift` | Behaviour changes across library/tool versions without clear changelog |
| `symptom-config-ignored` | Configuration properties silently have no effect |
| `symptom-misleading-error` | Error message points to wrong cause; real problem is elsewhere |

**Domain labels** (all entry types — where you're building):

| Label | When to Use |
|-------|-------------|
| `domain-backend` | Server-side: APIs, services, databases, message queues, batch |
| `domain-frontend` | Browser-side: UI components, CSS, bundlers, client JS |
| `domain-terminals` | Terminal emulators, PTY, shell, tmux, headless terminal |
| `domain-mobile` | Android, iOS, cross-platform mobile |
| `domain-devops` | CI/CD, containers, deployment, infrastructure |
| `domain-tooling` | Developer tools, IDEs, CLIs, build tools, AI assistants |

**Pattern labels** (for techniques — solution character):

| Label | When to Use |
|-------|-------------|
| `pattern-strategy` | Design philosophy, architectural choices, trade-off navigation |
| `pattern-testing` | Testing approaches, test doubles, assertion strategies |
| `pattern-automation` | Scripts, workflows, tool automation, CI patterns |
| `pattern-performance` | Speed, memory, throughput, latency optimization |
| `pattern-token-budget` | LLM token efficiency, context management, cost reduction |
| `pattern-workaround` | Necessary workaround for a bug or limitation; not the ideal fix |
| `pattern-integration` | Connecting systems, event bridges, adapter patterns |

### Label Assignment Rules

- Every entry must have **at least one domain label**
- Gotchas should have **at least one symptom label** if the symptom matches a known pattern
- Techniques should have **at least one pattern label**
- Undocumented entries use domain labels; symptom/pattern labels if applicable
- Maximum 4 labels per entry — more labels dilute retrieval signal

---

## Migration Plan

### Phase 1 — Structural migration (one focused session)

**Estimated scope:** 78 entries, ~15 domain files, ~8 technology directories.

1. Create `_index/`, `_summaries/`, `labels/` directories
2. Write `SCHEMA.md` (version 2.0.0)
3. For each existing domain file:
   a. Split into individual `GE-XXXX.md` files
   b. Add YAML frontmatter to each entry (extract from existing markdown headers)
   c. Generate `_summaries/GE-XXXX.md` for each entry
   d. Create `<domain>/INDEX.md` with all entries listed
   e. Create `<domain>/README.md`
   f. Create sub-directories for sub-domains with ≥3 entries, move entries
4. Build `_index/global.md` from domain INDEX.md counts
5. Assign labels to all existing entries; populate `labels/` files
6. Update `GARDEN.md` to metadata-only (remove all index content)
7. Run validation; commit as `migrate(garden): restructure to schema v2.0.0`

**Migration is safe because:** the git history preserves the old structure. The new structure can be compared to the old. Any entry lost in migration is recoverable.

### Phase 2 — Skill update

Update `garden/SKILL.md`:
- Replace SEARCH workflow with 3-tier retrieval algorithm
- Update CAPTURE Step 1b, Step 4, Step 6 per workflow changes above
- Update MERGE Steps 3, 6, 8 per workflow changes above
- Update DEDUPE Steps 1, 3, 5 per workflow changes above
- Add label taxonomy and label assignment rules
- Update submission format to include YAML frontmatter

### Phase 3 — Trigger integration

Update `superpowers/systematic-debugging/SKILL.md`:
- Add Step 0: garden consultation before any other analysis

Update garden skill CSO description:
- Add symptom-pattern trigger language for ambient B-trigger

### Phase 4 — Web app / Obsidian plugin (future)

The migration creates the interface contract the web app needs. See [Web App and Plugin Interface Contract](#web-app-and-plugin-interface-contract).

---

## Web App and Plugin Interface Contract

**The filesystem structure IS the API.** The web app reads the garden directly; it does not need a separate data format. This is the interface contract:

| Data needed | Source | Format |
|-------------|--------|--------|
| All entries | `Glob **/<domain>/**/*.md` filtered for `id:` in frontmatter | YAML frontmatter |
| Domain listing | `_index/global.md` | Markdown table |
| Entries by domain | `<domain>/INDEX.md` | Markdown table |
| Entries by label | `labels/<label>.md` | Markdown table |
| Entry full content | Individual entry file | YAML frontmatter + markdown body |
| Entry summary | `_summaries/GE-XXXX.md` | Key-value compact format |
| Label catalog | `labels/INDEX.md` | Markdown table |

### Views the Web App Provides

The filesystem structure is technology-first. The web app provides additional views from label data without any structural change:

| View | How Built |
|------|-----------|
| By technology domain | Read from directory structure |
| By conceptual domain (backend/frontend/terminals) | Filter entries by `domain-*` label |
| By symptom type | Filter entries by `symptom-*` label |
| By pattern type | Filter entries by `pattern-*` label |
| Full-text search | Client-side Fuse.js over loaded entries |
| Graph view | Build from `See also` cross-references in entry body |

### Obsidian Plugin Contract

Obsidian's native YAML frontmatter support means the plugin reads entry files directly. The `labels` field maps to Obsidian tags. The `path` in `_summaries/` files maps to Obsidian links. No plugin-specific transformation needed — the format is already Obsidian-native.

---

## Validation Quick Reference

*Operational checklists. For the full quality design rationale see [Quality and Bit Rot Prevention](#quality-and-bit-rot-prevention).*

**Before any MERGE commit:**
- [ ] YAML frontmatter valid and all required fields present (`id`, `type`, `stack`, `labels`, `keywords`, `symptom`, `context`, `score`, `captured`, `verified`, `staleness_threshold`)
- [ ] `id` matches filename; `labels` all from controlled vocabulary; `keywords` has 5–10 entries
- [ ] Summary file generated → `_summaries/GE-XXXX.md`
- [ ] Row added to `<domain>/INDEX.md` and all referenced label files
- [ ] `_index/global.md` entry count updated

**At DEDUPE or on demand:**
- [ ] Every domain INDEX.md GE-ID has a corresponding entry file
- [ ] Every entry file has a corresponding `_summaries/` file
- [ ] No GE-ID appears in two different domain INDEX.md files
- [ ] `_index/global.md` counts match actual file counts
- [ ] SCHEMA.md version matches actual structure

```bash
python3 scripts/validate_garden.py --full   # exits 0 if clean
```

### Drift Detection

The `GARDEN.md` drift counter (`Entries merged since last sweep`) **field** is unchanged from v1 — only this metadata field is retained. In v2, GARDEN.md is otherwise metadata-only (last ID, drift counter, last sweep date); all index content moved to domain INDEX.md files and `_index/global.md`. The counter itself triggers DEDUPE when drift accumulates past the threshold (default 10).

A second drift metric is introduced: `Index sync gap` — the number of entries whose `_summaries/` file is missing or whose domain INDEX.md row is absent. This is checked at every MERGE run. A non-zero sync gap blocks the MERGE commit.

---

## Success Criteria

The redesign is complete and working when:

- ✅ All 78 existing entries migrated to individual files with YAML frontmatter
- ✅ All entries have at least one `domain-*` label and the appropriate `symptom-*` or `pattern-*` label
- ✅ `_summaries/` contains one file per entry
- ✅ All domain directories have `INDEX.md` and `README.md`
- ✅ `_index/global.md` accurately reflects all domains
- ✅ `labels/INDEX.md` accurately reflects all labels and entry counts
- ✅ `SCHEMA.md` at version 2.0.0 with correct navigation guide
- ✅ Garden validator passes with zero errors
- ✅ Garden skill updated to use 3-tier retrieval
- ✅ systematic-debugging skill has Step 0 garden consultation
- ✅ **Retrieval test:** given a symptom description for any existing entry, Claude can find the entry in ≤3 tool calls without loading irrelevant content
- ✅ **Token test:** finding a specific entry costs ≤1,500 tokens via Tier 1, ≤1,500 via Tier 2, ≤32,000 via Tier 3 (full scan at 300 entries — 300 × 100 token summaries + up to 4 × 400 token entries)
- ✅ **Proactive test:** systematic-debugging session on a problem matching an existing entry retrieves that entry before the user asks

---

## Future Directions

### RAPTOR Cluster Summaries (at 100+ entries)

When the garden exceeds 100 entries, add thematic cluster summary files:

```
_clusters/
  async-concurrency.md    ← 200-token summary of all async/concurrency entries
  build-tooling.md
  native-image.md
```

Cluster files are LLM-generated summaries of all entries in a theme, with a list of their GE-IDs and paths. Retrieval at scale: read all cluster summaries (~20 clusters × 200 tokens = 4,000 tokens), pick 1-2 relevant clusters, then narrow within those.

### Incremental Index Updates

Current: MERGE rewrites index files. Future: implement checksum-gated incremental updates (zk pattern) — only regenerate index rows for entries whose content has changed since last MERGE.

### Automated Label Suggestions

At CAPTURE time, use Claude to propose labels from the controlled vocabulary based on entry content. Already part of the current skill design (Step 6b in CAPTURE). Future: validate proposals against the controlled vocabulary automatically.

### Cross-Reference Graph

Entries currently reference each other via `**See also:** GE-XXXX` in the body. Future: extract these into a `_graph/edges.md` file that maps GE-ID → related GE-IDs. Enables the web app to render a dependency/relationship graph without parsing all entry bodies.

### Knowledge Garden MCP Server

A future MCP server that wraps the garden for any Claude instance (not just Claude Code). Uses the same 3-tier retrieval algorithm but exposed as MCP tools:

```
garden_search(query: str, technology: str?, symptom_type: str?) → Entry[]
garden_capture(entry: EntryDraft) → SubmissionResult
garden_status() → GardenMetadata
garden_suggest_revise(geid: str, context: str) → ReviseDraft
```

The filesystem structure defined here is the data contract the MCP server reads. The MCP server uses `git cat-file --batch` internally for on-demand entry loading from a sparse blobless clone — the same pattern as the GitHub backend.

**Multi-tool significance:** Once the MCP server exists, Cursor, Copilot, Gemini CLI, and any MCP-compatible AI assistant can read from and contribute to the same garden ecosystem. This is the mechanism that makes the federation protocol tool-agnostic in practice. The cyanheads/obsidian-mcp-server (exposes an Obsidian vault via MCP) is the closest existing precedent.

### Fine-Tuning on Garden Content

**Long-term direction (Karpathy pattern applied to the garden).**

The garden's structured entries — symptom, root cause, fix, why non-obvious — form high-quality training pairs for fine-tuning a coding assistant model. Two uses:

1. **Domain-specific model fine-tuning:** Fine-tune a smaller, faster model on the garden so the knowledge lives in model weights, not just context. A Quarkus-specialized assistant trained on the JVM garden would handle CDI gotchas without any RAG retrieval.

2. **Synthetic training data generation:** Each gotcha entry is a labelled training scenario: input (symptom + context) → output (root cause + fix). The garden at 1,000+ entries becomes a synthetic training dataset for "non-obvious bug diagnosis" that doesn't exist elsewhere.

**Prerequisite:** Sufficient volume of high-quality entries (estimate: 500+ entries per domain for effective fine-tuning). This is a long-term direction, not Phase 1.

### Background Autonomous Improvement Agents

**Long-term direction.**

Rather than periodic human-triggered DEDUPE and coherence reviews, autonomous background agents that run continuously:

- **Freshness agent:** monitors library release feeds; when a major version releases, identifies affected garden entries and updates their `status` to `suspected` if the fix version matches
- **Cross-reference agent:** scans new entries for relationships to existing entries and proposes `See also` additions
- **Coherence agent:** periodically scans a domain for contradictions and proposes resolutions
- **Coverage agent:** monitors which queries return no garden hits; creates `known-gap` entries for recurring misses

Each agent runs as a GitHub Action on a schedule, opening PRs for human review rather than making changes directly.

### PR/Issue-Linked Automatic Capture

**Future direction.**

A GitHub Action on watched repositories that monitors merged PRs tagged `bug` or `fix`:

1. Reads the PR body and linked issues
2. Applies the Garden Score heuristic (length of "why", number of alternatives tried, etc.)
3. If score ≥ 8: posts a comment on the merged PR: "This fix looks garden-worthy — would you like to submit it as a knowledge garden entry? [Submit] [Dismiss]"
4. If the author clicks Submit: pre-fills a CAPTURE submission from the PR content

This closes the loop between open-source bug fixes and the garden. High-value gotchas that get fixed and merged without anyone knowing about the non-obvious cause become visible.

### External Library Change Monitoring

**Future direction.** Distinct from `_watch/` CI (which monitors parent gardens for duplicate submissions) and from PR-linked capture (which catches specific merged PRs). This watches external library release feeds continuously.

When a watched library publishes a major version (e.g. Quarkus 4.0):

1. GitHub Action fetches the release notes and changelog
2. Extracts breaking changes, deprecated APIs, and behaviour changes
3. Greps all garden entries for references to that library and affected version strings
4. For each matching entry: opens a private issue — "Quarkus 4.0 released — GE-0033 may be affected by [specific change]"
5. Flagged entries are set `status: suspected` automatically

This is the inverse of staleness-by-age detection: instead of waiting for time to pass, the garden reacts to upstream events. A Quarkus CDI entry is flagged the day Quarkus 4.0 ships — not 90 days later when the CI timer expires.

**Watched repos** are declared per-garden in a `_watch/external.yaml`:

```yaml
watch_repos:
  - repo: quarkusio/quarkus
    tracks: [quarkus/, quarkus/cdi/, quarkus/maven/]
    on: [major-release, security-advisory]
  - repo: smallrye/smallrye-reactive-messaging
    tracks: [quarkus/quarkus-flow/]
    on: [major-release]
```

### Retrieval Success Feedback

**Future direction (requires instrumentation).**

`discovery_count` tracks how many Claude sessions independently discovered a problem. `retrieval_count` (frontmatter field) tracks how often an entry has been retrieved. But neither tracks whether the entry *actually helped*.

When the MCP server (or garden skill) retrieves an entry and injects it into context, it can track:

- Was the retrieved entry used? (did Claude reference it in its response)
- Was the session's problem resolved? (user confirmed, commit was made, or Claude declared it solved)
- Was the retrieved entry the right one, or did the user then ask to search again?

**Usage quality score** (future frontmatter field `helpfulness_score`): average success rate across all retrievals. Entries with low helpfulness despite high retrieval count → keyword mismatch or wrong problem formulation → flag for review.

**Why it matters:** `discovery_count` measures the supply side — how many people hit the problem. `retrieval_count` × `helpfulness_score` measures the demand side — how useful the entry is once found. The combination gives a two-dimensional quality signal missing from all current knowledge systems, including Stack Overflow (which has votes but not "did following this answer solve your problem").

### Search Analytics and Coverage Gap Detection

**Future direction (requires instrumentation).**

Currently there is no feedback loop from retrieval failures to coverage. With instrumentation:

- Every garden query is logged (query terms, which tier was used, whether a match was found)
- Repeated no-match queries on similar terms → create `status: known-gap` entry
- Match quality scoring: entries that are retrieved but rarely followed (low dwell time) → may be wrong keywords
- Discovery heat maps: which domains get the most queries? Which get the fewest? Informs contributor attention

The MCP server is the natural instrumentation point — it sees every query and every result.

### Backlink Graph

`_graph/edges.md` — a formal bidirectional link registry extracted from `See also:` fields across all entries:

```markdown
| Source | Target | Relationship |
|--------|--------|-------------|
| GE-0066 | GE-0033 | see-also |
| GE-0062 | GE-0033 | related |
| PE-0047 | GE-0033 | private-extends |
```

Enables:
- Web app graph view (visual mind-map of garden entries)
- "What links here?" — inbound references for any entry
- Cluster detection — entries that form tight groups indicate a sub-domain worth creating
- Orphan detection — entries with zero inbound or outbound references may be isolated knowledge

Maintained by MERGE (adds edges when new entries have `See also:` fields) and DEDUPE (removes edges when entries are merged or retired).

### Multi-Language Support

Currently the garden is English-only by convention, not by design. The YAML frontmatter fields (`symptom:`, `keywords:`, `context:`) are language-agnostic strings. A non-English garden is structurally possible with minimal changes:

- Add `language: en` (or `ja`, `de`, etc.) to SCHEMA.md
- Domain indexes and label files would need language-specific variants or a `lang` column
- The garden engine would need language-aware retrieval (keyword matching is language-sensitive)
- Federation: a Japanese JVM garden could be a peer of the English JVM garden

**Known limitation:** The current design does not accommodate multi-language gardens. This is flagged as a future design consideration, not a Phase 1 concern.

### Entry Version History

Every garden entry has full version history via git — this is a first-class feature of the git-backed design, not an afterthought. When an entry is updated via REVISE:

```bash
git log -- quarkus/cdi/GE-0066.md   # full history of changes to this entry
git diff HEAD~3 -- quarkus/cdi/GE-0066.md  # what changed in a specific revision
git blame quarkus/cdi/GE-0066.md    # who changed what line when
```

The web app and Obsidian plugin can expose "revision history" for any entry by reading git log. This is the audit trail and provenance mechanism — no additional infrastructure needed.

### Discovery Count as a Quality Signal

`discovery_count` in entry frontmatter tracks how many times a problem has been independently discovered. When MERGE discards a duplicate submission (someone independently found the same gotcha), it increments the original entry's `discovery_count` rather than discarding the information entirely.

High discovery count = stronger evidence that this is genuinely non-obvious and widely encountered. A gotcha discovered independently by 5 different developers is more valuable than one discovered once. This signal can inform:

- Garden score re-evaluation (high discovery count → raise score)
- Contribution-back prioritisation (high-count entries are more valuable to upstream community)
- Fine-tuning data weighting (high-count entries are stronger training signals)

---

## GitHub Backend Architecture

*This section extends the local filesystem design to a distributed, multi-contributor, enterprise-ready architecture backed by a GitHub repository.*

### Context and Validation

This architecture is independently validated by Andrej Karpathy's "LLM-wiki" pattern (published April 3–4 2026), which proposes exactly the same foundation: plain Markdown files in a git repo, an LLM maintaining a self-built index, no vector database. Multiple implementations appeared within days. The key difference: Karpathy's pattern is for individual knowledge compilation; this design adds **multi-contributor governance, structured capture, automated CI validation, and security controls** — the unsolved multi-user problem.

GitHub Copilot's "Knowledge Bases" feature (team-shared Markdown repos as RAG backends) was sunset November 2025 and replaced by Copilot Spaces. The concept worked; the lack of governance and staleness detection was the failure mode. This design solves both.

---

### Design Axiom: Three Levels of Operation

![The Three Operation Levels — CI/Code, Agent, Human; push every check as low as possible](../../visuals/screenshots/visual-d-three-levels.png)

Every operation in this architecture is assigned to exactly one level:

| Level | Who/What | Cost | Latency | Use For |
|-------|----------|------|---------|---------|
| **CI/CD/Code** | Python, Bash, GitHub Actions | Zero tokens | Seconds | Format validation, schema checks, vocabulary compliance, duplicate detection (exact + fuzzy), injection heuristics, index maintenance, ID assignment |
| **Agent (Claude)** | Claude API in a bot or session | Tokens | Minutes | Semantic quality judgment, Fix section correctness, borderline score review, near-duplicate resolution |
| **Human** | PR reviewer | Slow | Hours | Final approval, sensitive content review, security judgment on flagged entries |

**The principle:** Push every check as low as possible. If it can be done by Python, it must not be done by Claude. If it can be done by Claude, it must not require a human. Human review is reserved for decisions that genuinely require human judgment.

---

### Garden Identity: One Repo, Forkable

```
github.com/mdproctor/knowledge-garden       ← public, community-contributed
github.com/<enterprise>/knowledge-garden    ← private fork, internal entries only
```

An enterprise forks the public garden. Their fork contains all public entries (pulled via upstream sync) plus private internal entries that never leave the fork. They can contribute back to the public garden selectively via PR.

```
upstream (public) ──────────────────────────────────────────
        │                                                   ↑
        │  git fetch upstream                               │  PR (selective)
        ▼                                                   │
enterprise fork ──── private entries not pushed upstream ───┘
```

This maps exactly to how enterprises consume open source: fork, extend privately, contribute back what isn't sensitive.

---

### GE-ID: GitHub Issues as the ID Source

Sequential IDs stored in files do not survive concurrent PRs. Two contributors both read "Last assigned ID: GE-0078" and both submit GE-0079 — the second PR has a merge conflict. This is confirmed unsolvable without taking ID assignment out of contributor control.

**Solution: GitHub issue number = GE-ID.**

```bash
# Step 1: submitter creates a GitHub issue
gh issue create \
  --title "Quarkus CDI: @UnlessBuildProfile causes Unsatisfied dependency in consumers" \
  --label "garden-submission" \
  --body "Type: gotcha | Score: 13/15 | Domain: quarkus/cdi"
# → Issue #123 created by GitHub (conflict-free, atomic)

# Step 2: entry file named after the issue number
GE-0123.md

# Step 3: PR references the issue
gh pr create --title "submit(GE-0123): @UnlessBuildProfile Unsatisfied dependency" \
  --body "Closes #123"

# Step 4: on merge, CI closes the issue automatically
```

**Why GitHub Issues:**
- GitHub assigns issue numbers atomically — no race condition possible
- The issue becomes the permanent discussion thread for that entry (corrections, revisions, disputes)
- `Refs GE-0123` in commit messages links to the issue
- GitHub's search finds entries by issue title, label, or comment
- Closed issues = integrated entries; open issues = pending submissions

**The submitting Claude's workflow (CAPTURE) becomes:**
1. Draft the entry content
2. `gh issue create` — get the issue number (GE-XXXX)
3. Write entry file as `GE-XXXX.md` with YAML frontmatter
4. `gh pr create` referencing the issue
5. Done — CI handles everything from here

---

### Sparse Checkout: Index-Present, Content-On-Demand

Every Claude session that uses the garden clones it once with a **blobless partial clone** + sparse checkout. Index files are always materialised in the working tree. Entry body files are fetched on demand via `git cat-file` — no working tree modification, no sparse checkout update needed.

#### Initial Setup (done once per machine)

```bash
# Blobless clone: full tree structure downloaded, blobs deferred
git clone --filter=blob:none --no-checkout \
  git@github.com:org/knowledge-garden.git \
  ~/claude/knowledge-garden
cd ~/claude/knowledge-garden

# Sparse checkout: materialise only index files
git sparse-checkout init
git sparse-checkout set \
  SCHEMA.md \
  GARDEN.md \
  "_index/" \
  "_summaries/" \
  "labels/" \
  "*/INDEX.md" \
  "*/README.md"

git checkout main
```

After this: SCHEMA.md, all index files, all summary files, all domain README.md and INDEX.md files are in the working tree. Entry body files (`GE-XXXX.md`) are absent from the working tree but their tree entries are known (blobless clone has all tree objects).

#### Session Start (fast, no network if up to date)

```bash
# Pull latest index changes only (metadata, no entry blobs)
git -C ~/claude/knowledge-garden pull --filter=blob:none
```

This updates SCHEMA.md, `_index/global.md`, domain INDEX.md files, and `_summaries/` with any new entries merged since last session. Cost: only changed tree objects and blobs in the sparse checkout paths.

#### On-Demand Entry Read (per retrieval)

```bash
# Read a single entry blob — fetches from remote if not cached, local object store otherwise
git -C ~/claude/knowledge-garden cat-file blob HEAD:quarkus/cdi/GE-0123.md

# Read multiple entries in ONE network round-trip (batch mode)
printf 'HEAD:quarkus/cdi/GE-0123.md\nHEAD:quarkus/cdi/GE-0066.md\nHEAD:tools/git/GE-0043.md\n' \
  | git -C ~/claude/knowledge-garden cat-file --batch
```

`git cat-file --batch` is the efficiency key: Tier 1 or Tier 2 retrieval typically identifies 2-4 candidate entries. `--batch` fetches all of them in a single network call. Subsequent reads of the same blob (same session or future sessions) are served from `.git/objects/` — no network. The git object store is the persistent local cache.

#### Caching Model

| Cache level | Mechanism | Scope |
|-------------|-----------|-------|
| L1 — in-session | Blob already read this conversation | Conversation only |
| L2 — local object store | `.git/objects/` — written on first blob fetch | Persistent across sessions, per machine |
| L3 — not needed | Object store is already persistent | — |

Once an entry blob is in the local object store, it is never fetched from the remote again (unless the entry is modified — a new blob hash is written on the next `git pull`). Teams working primarily in one domain (e.g., Quarkus) accumulate a warm local cache for that domain automatically.

#### Treeless Clone: Do Not Use

A treeless clone (`--filter=tree:0`) defers tree objects. Path-based lookups (`HEAD:path/to/file`) become expensive because git must reconstruct trees on demand. `git cat-file blob HEAD:quarkus/cdi/GE-0123.md` would require fetching the full tree lineage. Use blobless, not treeless.

#### GitHub Contents API: Do Not Use

The GitHub Contents API returns base64-encoded file content over HTTPS. It is significantly slower than `git cat-file` (research reports up to 10s/request) and subject to rate limits (60 req/hr unauthenticated, 5,000/hr authenticated). For an agent reading 3-4 entries per retrieval across many sessions, rate limits become a real constraint. `git cat-file` is the correct approach.

---

### PR Submission Workflow

```
Claude (submitter)          GitHub                    CI                     Human/Bot
       │                       │                       │                         │
       │── gh issue create ───►│                       │                         │
       │◄── issue #123 ────────│                       │                         │
       │                       │                       │                         │
       │── write GE-0123.md ──►│                       │                         │
       │── gh pr create ──────►│                       │                         │
       │                       │── trigger validate ──►│                         │
       │                       │                       │── format check ─────────│ (Python)
       │                       │                       │── vocabulary check ──────│ (Python)
       │                       │                       │── duplicate scan ────────│ (Python)
       │                       │                       │── injection scan ────────│ (Python)
       │                       │                       │── score threshold ───────│ (Python)
       │                       │◄── post PR comment ───│                         │
       │                       │                       │                         │
       │                       │  [score ≥ 12, clean]  │                         │
       │                       │── request review ─────────────────────────────►│
       │                       │                       │                         │── approve
       │                       │◄── merge ─────────────────────────────────────│
       │                       │── trigger integrate ──►│                         │
       │                       │                       │── generate _summaries ───│ (Python)
       │                       │                       │── update domain INDEX ───│ (Python)
       │                       │                       │── update labels/ ────────│ (Python)
       │                       │                       │── update global index ───│ (Python)
       │                       │                       │── close issue #123 ──────│ (Python)
       │                       │                       │── commit index updates ──│ (Python)
       │                       │                       │── run validate_garden ───│ (Python)
```

**Auto-reject (CI, no human needed):** CRITICAL format errors, score < 8, prompt injection detected.
**Auto-approve eligible (CI):** score ≥ 12, no CRITICAL findings, no WARNING flags.
**Human/bot review required:** score 8-11, any WARNING, code in Fix section, sensitive content patterns.

---

### CI Automation Specification

All checks run in GitHub Actions. None require Claude. Implementation lives in `scripts/validate_pr.py` and `scripts/integrate_entry.py` in the garden-engine repo.

#### On PR Open: `validate_pr.py` — what it checks

**CRITICAL checks** (blocks merge — binary, no judgment):

| Check | Rule |
|-------|------|
| YAML parseable | `yaml.safe_load()` must not throw |
| Required fields present | `id`, `type`, `stack`, `labels`, `keywords`, `symptom`, `context`, `score` |
| `id` matches filename | `GE-0123.md` → `id: GE-0123` |
| `type` is valid enum | `gotcha` / `technique` / `undocumented` |
| `score` in range | Integer 1–15 |
| All labels in controlled vocabulary | Compare against `labels/INDEX.md` |
| Prompt injection patterns in body | Regex scan for `ignore previous instructions`, `[INST]`, `system prompt`, etc. |
| GE-ID not already in garden | No duplicate IDs in existing domain INDEX.md files |
| Score ≥ 8 | Score < 8 → auto-reject |

**WARNING checks** (flag for review, don't block):

| Check | Rule |
|-------|------|
| Keywords count | Should be 5–10 |
| Stack version strings | Third-party libs should include version numbers |
| Symptom fuzzy similarity | rapidfuzz token_sort_ratio > 80% against same-domain entries |
| Keyword Jaccard overlap | > 65% overlap with same-domain entry → possible duplicate |
| Sensitive data patterns | IP addresses, credential patterns, base64 blobs |

#### On Merge: `integrate_entry.py` — what it does

Runs on push to main. Fully automated. Zero tokens.

1. Generate `_summaries/GE-XXXX.md` from entry frontmatter
2. Append row to `<domain>/INDEX.md`
3. Append to each referenced label file in `labels/`
4. Update entry count in `_index/global.md`
5. Update `GARDEN.md` last-assigned-ID
6. Check sub-directory promotion threshold (≥3 entries in a sub-domain → create sub-dir)
7. Close the corresponding GitHub issue
8. Run `validate_garden.py --full` — blocks commit if non-zero
9. Commit and push all index updates

#### GitHub Actions: Two Workflows

`on: pull_request paths: ['**/GE-*.md']` → runs `validate_pr.py` (sparse checkout of index files only), posts results as PR comment, auto-approves if eligible, auto-closes if rejected.

`on: push branches: [main] paths: ['**/GE-*.md']` → runs `integrate_entry.py` (full checkout needed to write index files).

      - name: Post validation comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const results = require('./validation-results.json')
            github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.issue.number,
              body: results.comment
            })

      - name: Auto-approve if score ≥ 12 and no findings
        if: steps.validate.outputs.eligible == 'true'
        run: gh pr review ${{ github.event.pull_request.number }} --approve --body "CI auto-approved: score ${{ steps.validate.outputs.score }}/15, no findings."

      - name: Auto-close if score < 8 or CRITICAL
        if: steps.validate.outputs.reject == 'true'
        run: gh pr close ${{ github.event.pull_request.number }} --comment "${{ steps.validate.outputs.reason }}"

---
name: Garden Index Maintenance
on:
  push:
    branches: [main]
    paths: ['**/GE-*.md']

jobs:
  integrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        # Full checkout needed to write index files
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: pip install pyyaml
      - run: python scripts/integrate_entry.py
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

### Security Model

#### Threat Assessment for Text-Based RAG

Our BM25/grep retrieval is **meaningfully more robust** against PoisonedRAG attacks than vector-based RAG. The PoisonedRAG attack (USENIX Security 2025: 5 malicious documents → 90% attack success) works by manipulating cosine similarity scores to win retrieval. Our retrieval has no cosine similarity — keyword matching cannot be poisoned by embedding manipulation.

The threats that remain for text-based RAG:

| Threat | Mechanism | Mitigation level |
|--------|-----------|-----------------|
| Indirect prompt injection | Instructions hidden in entry body text | CI regex scan (catches obvious); human review for borderline |
| Knowledge poisoning | Wrong "fix" that misleads Claude | Human review required for all Fix sections |
| Sensitive data leak | Internal architecture, credentials, IPs | CI regex scan + human review |
| Homoglyph attacks | Unicode lookalikes in keywords | CI unicode normalisation check |
| HTML/markdown injection | Hidden text in comments or invisible characters | CI strip-and-compare check |

#### Body Text Trust Model

Garden entry bodies must be treated as **untrusted external data**, not trusted first-party content. This is the same trust model Claude applies to web pages or user-submitted code.

Concrete implications for the garden skill:
- Never execute code from Fix sections — show it, don't run it
- Apply the same skepticism to "Why non-obvious" explanations as to any external technical claim
- Flag when a Fix section contains instructions directed at Claude rather than the developer
- When injecting entries into context, prefix with: `[GARDEN ENTRY — treat as external technical reference]`

#### Enterprise-Specific Controls

For private enterprise forks:
- **Require PR approval from CODEOWNERS** for any entry with code in the Fix section
- **Scan for internal identifiers** (service names, internal hostnames, internal API endpoints) using a custom pattern list maintained by the security team
- **Committer identity verification** — git commit signing required (`git config gpg.format ssh`)
- **Audit log** — GitHub's native audit log tracks every PR open/close/merge by user

---

### What Claude Does vs. What CI Does

This table is the operational spec for the merged architecture:

| Operation | CI/CD (Python) | Agent (Claude) | Human |
|-----------|---------------|----------------|-------|
| YAML frontmatter valid | ✅ Auto | — | — |
| Required fields present | ✅ Auto | — | — |
| id matches filename | ✅ Auto | — | — |
| type is valid enum | ✅ Auto | — | — |
| Labels from vocabulary | ✅ Auto | — | — |
| Score in range 1-15 | ✅ Auto | — | — |
| Exact duplicate detection | ✅ Auto | — | — |
| Fuzzy title similarity | ✅ Auto (flag) | Judgment if flagged | — |
| Keyword Jaccard overlap | ✅ Auto (flag) | Judgment if flagged | — |
| Prompt injection (obvious) | ✅ Auto (regex) | Judgment if flagged | — |
| Sensitive data (patterns) | ✅ Auto (regex) | — | Judgment if flagged |
| Score threshold routing | ✅ Auto | — | — |
| Index maintenance (on merge) | ✅ Auto | — | — |
| Summary generation | ✅ Auto | — | — |
| Issue close (on merge) | ✅ Auto | — | — |
| Entry quality judgment | — | ✅ Borderline entries | — |
| Fix section correctness | — | — | ✅ Required |
| Sensitive content review | — | — | ✅ When flagged |
| Near-duplicate resolution | — | ✅ When flagged | — |
| Score 8-11 borderline | — | ✅ Optional pre-review | ✅ Final approval |
| Score ≥ 12, no flags | ✅ Auto-approve eligible | — | ✅ Confirm merge |

**Token spend on CI path (score ≥ 12, no flags):** zero. Python validates, auto-approves, human confirms merge, Python integrates. Claude is not in the loop.

**Token spend on borderline path (score 8-11):** One Claude review session per PR (focused: is this garden-worthy? is the fix correct?). Bounded, purposeful.

---

### Staleness Detection

A known failure mode at enterprise scale: RAG systems return accurate-when-indexed information that has since changed. Mitigations for the garden:

**Library version deprecation (CI, scheduled):** A nightly GitHub Actions job scans all entries for version strings and checks against PyPI/Maven Central/npm for newer major versions. Flags entries where the referenced version is EOL or has a major successor.

**Resolved flag (manual):** When a gotcha is fixed in a newer library version, a REVISE submission adds `resolved-in: Quarkus 3.15` to the frontmatter. CI validates this field's presence. The summary file is updated. The entry is retained (older versions still need it) but the summary shows the resolved version.

**Drift threshold (existing):** GARDEN.md `Entries merged since last sweep` counter triggers DEDUPE when drift exceeds the threshold. Unchanged.

---

### MCP Server: The Long-Term Integration Target

The filesystem structure defined in this document is the interface contract for a future MCP server. The MCP server exposes the garden to any AI tool (Claude, Cursor, Copilot, etc.) via the standard MCP protocol, removing the need for Claude Code specifically.

Tool surface:

```
garden_search(query: str, technology: str?, symptom_type: str?) → Entry[]
garden_capture(entry: EntryDraft) → SubmissionResult
garden_status() → GardenMetadata
```

The server uses `git cat-file --batch` internally for on-demand entry loading, exactly as described in the sparse checkout model. The local git object store is the cache layer. Remote is the GitHub-backed garden repo.

Community implementations of the Karpathy LLM-wiki already include MCP servers (`llm-wiki-kit` by iamsashank09) and Obsidian integrations (`obsidian-wiki` by Ar9av). The Obsidian MCP server (`cyanheads/obsidian-mcp-server`) exposes a vault backed by a GitHub repo via MCP. These are direct predecessors for the garden MCP server.

The garden MCP server, once built, means:
- Any Claude instance (not just Claude Code) can use the garden
- Cursor, Copilot, and other tools can query the same garden
- The garden becomes a shared enterprise knowledge asset, not a Claude Code feature

---

## Federation Architecture

*Gardens can federate. A single garden is already useful; a network of gardens that share, extend, and govern knowledge without duplicating it is the long-term model.*

![Federation Topology — knowledge flows down, contributions flow up, peers share without hierarchy](../../visuals/screenshots/diagram-3-federation.png)

---

### The Three Relationship Types

Every garden declares its role in SCHEMA.md. There are exactly three roles:

**Canonical** — the root authority. No upstream. What it covers, it owns. Accepts PRs from children and contributions from the community. Unaware of which children exist.

**Child** — extends a parent with a strong non-duplication contract. Defers to the parent on content the parent covers. Adds only what the parent doesn't have. Can augment parent entries with private context. Monitors the parent for incoming content that would duplicate local entries. May be completely private — the parent does not know the child exists.

**Peer** — equals that share knowledge without hierarchy. No deference. Overlapping entries on the same topic are acceptable — different teams may have different versions, different contexts, different workarounds. Retrieval synthesises across peers. Cross-references are encouraged but overlaps are not blocked.

---

### Capability Matrix

| Capability | Canonical | Child | Peer |
|---|---|---|---|
| Retrieves from parent chain | — | ✅ Full chain | — |
| Non-duplication contract | — | ✅ Strict | Advisory |
| Augments parent index locally | — | ✅ `_augment/` layer | ❌ |
| Monitors parent for incoming duplicates | — | ✅ `_watch/` | ❌ |
| Contributes entries back upstream | — | ✅ Natural obligation | Possible, no obligation |
| Accepts PRs from children | ✅ | ✅ (from its own children) | — |
| Parent knows child exists | N/A | ❌ Not required | Mutual awareness |
| Overlapping entries with peer | — | — | ✅ Acceptable |

A garden can hold multiple roles simultaneously: child of one garden, peer of another. Enterprise garden is a child of the community canonical (strict non-duplication) and a peer of a research garden (overlaps fine, cross-references encouraged).

---

### SCHEMA.md Federation Declaration

Every garden declares its federation configuration in SCHEMA.md:

```yaml
---
schema-version: 2.0.0
backend: github          # or: local
id-prefix: PE            # GE = community, PE = private enterprise, TE = team, IE = individual

federation:
  role: child            # canonical | child | peer

  # For child: list of parent gardens, walked in order
  upstream:
    - url: https://github.com/community/knowledge-garden
      id-prefix: GE
      local-path: ~/gardens/public
      non-duplication: strict     # strict | advisory
      search-order: fallback      # fallback = only if local has no match
                                  # always = always include parent results

  # For peer: list of peer gardens, searched in parallel
  peers:
    - url: https://github.com/research-org/garden
      id-prefix: RE
      local-path: ~/gardens/research
      non-duplication: advisory   # overlaps are flagged but not blocked
---
```

A community canonical garden:

```yaml
---
schema-version: 2.0.0
id-prefix: GE
federation:
  role: canonical
  upstream: []
  peers: []
---
```

A three-level team garden (child of enterprise, which is child of community):

```yaml
---
id-prefix: TE
federation:
  role: child
  upstream:
    - url: https://github.com/enterprise/private-garden
      id-prefix: PE
      local-path: ~/gardens/enterprise
      non-duplication: strict
      search-order: fallback
    - url: https://github.com/community/knowledge-garden
      id-prefix: GE
      local-path: ~/gardens/public
      non-duplication: strict
      search-order: fallback
---
```

---

### GE-ID Namespacing

Without namespacing, `GE-0001` in two different gardens are indistinguishable. Each garden declares its own prefix. The prefix appears in every ID, filename, and cross-reference.

| Garden type | Prefix | Example |
|-------------|--------|---------|
| Community canonical | `GE-` | `GE-0033` |
| Enterprise private | `PE-` | `PE-0001` |
| Team extension | `TE-` | `TE-0001` |
| Individual | `IE-` | `IE-0001` |
| Research org | `RE-` | `RE-0001` |

When resolving a cross-reference, the prefix determines which sparse clone to look in:

```
See also: GE-0033    → ~/gardens/public/quarkus/cdi/GE-0033.md
See also: PE-0047    → ~/gardens/private/quarkus/cdi/PE-0047.md
See also: RE-0012    → ~/gardens/research/tools/RE-0012.md
```

The prefix is also embedded in filenames (`GE-0033.md`, `PE-0047.md`) so directory listings are always unambiguous.

---

### Capability 1: Retrieval Across the Federation

The core 3-tier retrieval algorithm (Tier 1: technology known → domain index; Tier 2: symptom known → label index; Tier 3: full summary scan) is defined in [The 3-Tier Retrieval Algorithm](#the-3-tier-retrieval-algorithm). Federation adds the following extensions:

**Child retrieval** runs each tier against own garden first, then walks the upstream chain if no match is found. Each parent is queried in order until a match is found or the chain is exhausted. This means a child garden automatically benefits from all parent knowledge without duplicating it.

**Peer retrieval** runs Tier 1 and Tier 3 against all peer gardens in parallel, then merges results with provenance labels (`[own]`, `[peer: research-org]`). Peers are searched simultaneously, not sequentially.

**Mixed (child + peer):** Walk child chain first for domain-specific authority; search peers in parallel for supplementary knowledge. Present own/parent entries first; peer entries as additional context.

**Priority:** Own entries outrank parent entries outrank grandparent entries. Peer entries are additive — supplementary, not competing. When a parent entry and a peer entry match the same query, the parent entry is preferred (child defers to parent) with the peer entry shown as a cross-reference.

---

### Capability 2: Child Augments Parent Indexing

The child adds a private layer on top of parent entries without modifying parent files. The parent entry is unchanged. The child's augmentation is local and private.

**Augmentation directory:**

```
private-garden/
  _augment/
    GE-0033.yaml    ← private augmentation of community entry GE-0033
    GE-0066.yaml
    PE-0022.yaml    ← augmentation of enterprise-parent entry PE-0022
```

**Augmentation file format:**

```yaml
# _augment/GE-0033.yaml
augments: GE-0033
source: community-garden
additional_keywords: [keycloak, enterprise-sso, internal-auth-service, okta]
additional_labels: [domain-enterprise-backend, symptom-enterprise-auth]
context_note: |
  In enterprise stacks with Keycloak SSO, this technique requires an additional
  @IfBuildProfile("keycloak") guard alongside @UnlessBuildProfile("prod").
  Without it, the auth mechanism resolves before the SSO client initialises.
  See PE-0047 for the full enterprise CDI pattern.
child_cross_refs: [PE-0047, PE-0052]
confidence: production-verified      # production-verified | tested | theoretical
overrides: false                     # true = suppress parent entry from retrieval
                                     # (use when child entry fully supersedes parent)
```

**What augmentation enables:**

| Use | How |
|-----|-----|
| Enterprise-specific keywords | `additional_keywords` — parent entry becomes findable via private terms |
| Enterprise context note | `context_note` — appended when entry is injected into Claude context |
| Private cross-references | `child_cross_refs` — resolved to local private entries |
| Production confidence signal | `confidence` — tells Claude how battle-tested this entry is in this context |
| Suppress parent entry | `overrides: true` — hides parent entry when local entry fully supersedes it |

**Retrieval with augmentation:**

```python
def load_entry_with_augmentation(geid, garden_root):
    # 1. Determine which garden the entry lives in (by prefix)
    source_garden = resolve_garden_by_prefix(geid)

    # 2. Load the entry blob
    entry = git_cat_file(source_garden.local_path, geid)

    # 3. Check for augmentation in own private garden
    augment_path = garden_root / '_augment' / f'{geid}.yaml'
    if augment_path.exists():
        aug = parse_yaml(augment_path)

        # Merge additional keywords (already used in retrieval scoring)
        entry.keywords.extend(aug.get('additional_keywords', []))

        # Append context note
        if aug.get('context_note'):
            entry.body += f"\n\n**Enterprise context:** {aug['context_note']}"

        # Resolve additional cross-references
        entry.see_also.extend(aug.get('child_cross_refs', []))

    return entry
```

**Index-level augmentation** — the private domain INDEX.md includes parent entries with enriched keywords:

```markdown
# Quarkus — Private Domain Index (includes parent entries with augmentation)

| ID | Source | Location | Keywords | Symptom |
|----|--------|----------|---------|---------|
| GE-0033 | upstream | quarkus/cdi/ | UnlessBuildProfile, CDI, keycloak, enterprise-sso | Strips dev-only beans at build time |
| GE-0066 | upstream | quarkus/cdi/ | UnlessBuildProfile, Unsatisfied dependency, CDI | Profile-excluded bean breaks consumers |
| PE-0047 | local | quarkus/cdi/ | keycloak, CDI, profile-guard, enterprise-auth | Keycloak + @UnlessBuildProfile full pattern |

```

Note `GE-0033` appears with private keywords (`keycloak, enterprise-sso`) that the community garden index doesn't carry. Private Tier 1 retrieval on "Keycloak CDI" finds GE-0033 via the private index — even though the community index would not.

---

### Capability 3: Child Watches Parent, Flags Incoming Duplicates

The child monitors the parent for new entries that would duplicate existing child content. The parent is unaware of the child. The child acts without revealing its private content.

**Watch configuration:**

```yaml
# private-garden/_watch/config.yaml
parents:
  - url: https://github.com/community/knowledge-garden
    id-prefix: GE
    local-path: ~/gardens/public
    check-interval: 6h
    duplicate-threshold: 0.6      # Jaccard overlap that triggers private flag
    supersede-threshold: 0.85     # Jaccard overlap that triggers drop recommendation
    action-on-duplicate: private-issue
    action-on-supersede: private-issue
    anonymous-parent-comment: true   # post a generic flag on parent PR (no content revealed)
```

**The watch CI job:**

```python
def watch_parent_for_duplicates(config, garden_root):
    """Runs on schedule. Zero tokens. Pure Python."""

    # 1. Fetch latest parent index (no blob download)
    git_fetch_filter_blob_none(config.local_path)

    # 2. Detect new parent entries since last check
    new_entries = get_entries_newer_than(config.local_path, config.last_checked)

    # 3. Load all private _summaries/ (always materialised — cheap)
    private_summaries = load_all_summaries(garden_root)

    for parent_entry in new_entries:
        for private_summary in private_summaries:
            overlap = jaccard(
                set(parent_entry.keywords),
                set(private_summary.keywords)
            )

            if overlap >= config.supersede_threshold:
                # Parent entry may make private entry redundant
                open_private_issue(
                    title=f"[Watch] {parent_entry.id} ({overlap:.0%} overlap) "
                          f"may supersede {private_summary.id}",
                    body=format_supersede_issue(parent_entry, private_summary)
                )
                if config.anonymous_parent_comment:
                    post_anonymous_parent_comment(parent_entry.pr_url)

            elif overlap >= config.duplicate_threshold:
                # Moderate overlap — worth reviewing
                open_private_issue(
                    title=f"[Watch] Review: {parent_entry.id} overlaps "
                          f"{private_summary.id} ({overlap:.0%})",
                    body=format_overlap_issue(parent_entry, private_summary)
                )
```

**The private issue body (supersede case):**

```markdown
## Parent entry may supersede private entry

**Parent entry:** GE-0234 — "@UnlessBuildProfile full CDI pattern" (87% keyword overlap)
**Private entry:** PE-0047 — "Keycloak + @UnlessBuildProfile enterprise pattern"

### Options

- [ ] **Retire PE-0047** — parent now covers this. Move enterprise-specific context
      to `_augment/GE-0234.yaml`. Set `PE-0047 status: superseded, superseded_by: GE-0234`.

- [ ] **Keep PE-0047** — it covers distinct enterprise context the parent doesn't have.
      Add `child_cross_refs: [GE-0234]` to PE-0047. Add `_augment/GE-0234.yaml` 
      with additional enterprise keywords.

- [ ] **Contribute PE-0047 upstream** — generalise it, submit PR to parent as GE-XXXX.
      Retire PE-0047 locally when merged. Add `_augment/GE-XXXX.yaml` for 
      enterprise-specific context.

*Posted automatically by watch CI — no private content sent to parent.*
```

**Anonymous parent comment (when enabled):**

```
This PR appears to overlap with knowledge that exists in at least one federated 
downstream garden. Community review recommended before merging to confirm uniqueness.

[Automated notice from a private federated garden — no private content shared]
```

The parent sees a governance signal. The child's content remains hidden. The parent community can investigate or ignore.

---

### The Contribution-Back Flow

The child non-duplication contract creates a natural upstream contribution pathway. When private knowledge is generalised, it should move to the parent.

```
PE-0047 (private) ──► generalise ──► PR to community ──► GE-0234 (public)
                                                              │
                                              PE-0047 status: superseded
                                              superseded_by: GE-0234
                                                              │
                                          _augment/GE-0234.yaml created
                                          (preserves enterprise context privately)
```

**The full contribution workflow:**

```bash
# 1. Generalise the private entry — strip enterprise-specific details
#    that shouldn't be public. Create a public-safe version.

# 2. Submit PR to the community garden
gh pr create \
  --repo community/knowledge-garden \
  --title "submit(GE-PENDING): @UnlessBuildProfile full CDI pattern" \
  --body "..."     # generic version, no enterprise details

# 3. On merge: GE-0234 is created in the community garden

# 4. Retire the private entry
# In PE-0047.md frontmatter:
#   status: superseded
#   superseded_by: GE-0234

# 5. Create augmentation to preserve enterprise context
# _augment/GE-0234.yaml:
#   additional_keywords: [keycloak, enterprise-sso]
#   context_note: "In enterprise stacks with Keycloak SSO..."
#   child_cross_refs: [PE-0052]
```

After this, the community benefits from the knowledge. The enterprise retains the enterprise-specific context privately via the augmentation. Neither side carries duplicate content.

---

### N-Level Chain Topology

```
community/knowledge-garden (canonical, GE-)
         │
         ├── enterprise-a/garden (child, PE-)
         │         │
         │         ├── team-x/garden (child, TE-)
         │         │         │
         │         │         └── developer-y/garden (child, IE-)
         │         │
         │         └── team-z/garden (child, TE-)
         │
         └── enterprise-b/garden (child, BE-)

research-org/garden (peer of community, RE-)
    ↔ community/knowledge-garden
```

**Retrieval for developer-y walks the full chain:**

```
IE- (own) → TE-x (parent) → PE-a (grandparent) → GE (great-grandparent)
```

**Non-duplication check for developer-y searches the full chain:**

```
Before capturing: check IE-, TE-x, PE-a, GE
If any level has it: contribute to that level (or augment) rather than duplicate
```

**The chain is bounded by what's declared in SCHEMA.md.** developer-y's SCHEMA.md lists team-x and enterprise-a and community as upstream. The chain depth is explicit, not infinite.

**Keeping sparse clones current across the chain:**

```bash
# Session start: pull latest indexes for all declared upstreams
for upstream in $(read_upstream_paths_from_schema); do
    git -C $upstream pull --filter=blob:none
done
# Cost: one lightweight fetch per upstream, index files only
# Typical chain of 3: < 1 second, < 1MB transferred
```

---

### Privacy and Asymmetry

The child relationship is deliberately asymmetric:

| Direction | What is shared |
|-----------|----------------|
| Parent → Child | All public entries, indexes, summaries |
| Child → Parent | Nothing automatically. Only what the child explicitly PRs. |
| Child → Parent (governance) | Anonymous "overlap detected" comment on PRs (optional, no content) |

**The parent's garden files are never modified by the child.** The child only reads from the parent. Augmentation files (`_augment/`) live entirely in the child's private repo. Watch CI runs in the child's GitHub Actions — the parent never knows it exists.

**A private child can be completely invisible:**

- Private GitHub repo (parent cannot see it)
- No anonymous comments (turn off in watch config)
- Sparse clones are local (no network trace visible to parent)
- Contribution-back is the only moment the child becomes visible — and that is the child's choice

---

### Federated Governance Summary

The federation model creates a self-organising knowledge governance structure:

```
Content flows upward:    Child contributes generalisable entries to parent
Knowledge flows downward: Child retrieves from parent chain
Context stays private:   Child augments parent entries without modifying them
Quality is distributed:  Each garden maintains its own structural integrity
Duplication is governed: Child contract prevents redundant entries across levels
Overlap is acceptable:   Peer contract allows diverse perspectives on same topics
```

No central registry is required. Each garden knows its own role and its declared relationships. A new child garden bootstraps by:
1. Creating a private GitHub repo
2. Writing `SCHEMA.md` with `role: child` and the upstream URL
3. Setting up the sparse clones for own garden and all upstream gardens
4. Running the watch CI to start monitoring the parent

The parent does nothing. The child self-declares, self-governs, and contributes back when it chooses.

---

### Submission Routing

Federation is **client-orchestrated**. The gardens themselves don't communicate at runtime — the Claude instance's local config knows all gardens and decides where to route each submission. This keeps gardens as passive, self-contained stores.

#### Where the Config Lives

```yaml
# ~/.claude/garden-config.yaml  (client-side — not in any garden repo)

gardens:
  - url: https://github.com/me/jvm-garden
    id-prefix: JE
    local-path: ~/gardens/jvm
    role: primary                          # my main garden — default for unrouted entries
    domains: [java, jvm, maven, gradle, quarkus, kotlin, drools]

  - url: https://github.com/org/python-garden
    id-prefix: PE
    local-path: ~/gardens/python
    role: peer
    domains: [python, pip, poetry, django, fastapi, sqlalchemy, pandas]

  - url: https://github.com/community/tools-garden
    id-prefix: TE
    local-path: ~/gardens/tools
    role: peer
    domains: [git, docker, github-actions, bash, regex, ci-cd, ai-tools]
```

Retrieval queries all declared gardens. Submission routes to the garden that *owns* the entry's domain. The gardens do not know about each other — the client config is the only entity that holds the full picture.

#### Domain Ownership: The Routing Key

Each garden declares which domains it owns. Domains should be **non-overlapping between peers** — this is what makes routing unambiguous and what makes the child non-duplication contract coherent.

```python
def route_submission(entry, gardens):
    # Find gardens that own this entry's domain
    owners = [g for g in gardens if entry.domain in g.domains]

    if len(owners) == 1:
        return owners[0]                   # clean — unambiguous routing

    if len(owners) == 0:
        return primary_garden              # nobody claims it — goes to primary
                                           # may define a new domain

    if len(owners) > 1:
        # Domain overlap — ambiguous
        # Prefer the most specialised (fewest total claimed domains)
        ranked = sorted(owners, key=lambda g: len(g.domains))
        if ranked[0] is clearly more specific:
            return ranked[0]
        else:
            ask_user(f"This fits {[g.name for g in owners]} — which garden?")
```

**Domain overlap is a design smell.** If two peer gardens both claim `testing`, either:
- The domain is too broad (split into `java-testing` and `python-testing`)
- One garden should be a child of the other, not a peer

The ideal peer structure partitions the domain space cleanly:

```
community/tools-garden     → git, docker, bash, regex, ci-cd, github-actions, ai-tools
community/jvm-garden       → java, jvm, kotlin, maven, gradle, quarkus, spring, drools
community/python-garden    → python, pip, poetry, django, fastapi, pandas, pytest
community/frontend-garden  → typescript, javascript, react, css, webpack, vite, playwright
community/mobile-garden    → android, ios, react-native, flutter, swift
community/systems-garden   → rust, go, c, c++, wasm, linux, containers
```

No entry belongs to two domains. A Quarkus CDI gotcha goes to `jvm-garden`. A GitHub Actions bug goes to `tools-garden`. The client never has to ask.

#### Do Peers Know About Each Other?

**Optional.** Bilateral peer awareness can be declared in SCHEMA.md for *discovery* — so someone finding garden A can find garden B. But this doesn't affect operation. The client config is authoritative.

```yaml
# Optional bilateral declaration in jvm-garden's SCHEMA.md
federation:
  role: canonical
  peers:
    - url: https://github.com/community/tools-garden
      id-prefix: TE
      domains: [git, docker, ci-cd]        # what they own — no overlap with us
```

A client that doesn't have `tools-garden` in its config can discover it by reading `jvm-garden`'s SCHEMA.md and choose to add it. But the federation works without this — as long as the client config is complete.

#### What "Federated" Actually Means

| Layer | What it is | Who controls it |
|-------|-----------|-----------------|
| Storage | N independent GitHub repos, each complete | Garden maintainers |
| Client config | `~/.claude/garden-config.yaml` — lists all gardens + domains | Claude user |
| Retrieval | Client queries all gardens, synthesises with provenance | Garden skill |
| Submission routing | Client checks domain ownership, routes to owner | Garden skill |
| Bilateral peer awareness | Optional SCHEMA.md declaration — discovery only | Garden maintainers |
| Child→Parent awareness | Child SCHEMA.md declares upstream — required for child contract | Child maintainer |

**The gardens are passive.** They store, index, and serve. The client orchestrates.

---

### Known Open Problems in Federation

| Problem | Risk | Current mitigation | Future direction |
|---------|------|--------------------|-----------------|
| Augmentation drift | `_augment/GE-0033.yaml` references keywords the parent entry has since dropped | Weekly CI check: compare augmentation keywords against current parent entry | Auto-suggest augmentation update when parent entry changes |
| Prefix collision | Two gardens independently choose the same prefix (`PE-`) | Convention only — no registry | A public prefix registry (simple GitHub gist) that gardens optionally register with |
| Watch false positives | High Jaccard on keyword overlap but genuinely different problems | Threshold tuning + human review of private issues | Agent pre-screening of flagged pairs before opening private issues |
| Chain depth performance | N sparse clone fetches on session start | Bounded by explicit SCHEMA.md declaration | Lazy fetch: only pull upstream index if own Tier 1 finds no match |
| Circular peer references | Garden A peers with B, B peers with A — retrieval loops | Not currently prevented | Detect cycles in SCHEMA.md validation |
| Augmentation for retired parent entries | Parent entry is retired; `_augment/` file becomes orphaned | Watch CI detects parent entry status change | Auto-flag augmentation files whose target entry is retired or removed |

---

## Implementation Roadmap

### How to Read This Roadmap

Three kinds of work exist in this project:

**Shallow-then-deep:** Some capabilities are implemented at minimum viable depth in an early phase, then deepened in later phases. The structure is correct from the start; the sophistication grows. This is intentional — getting the right skeleton in place early is more valuable than perfecting one subsystem before moving on.

**Phase-bounded:** Some work has a clear completion state and will not be revisited after its phase. Structure migration, GitHub setup, the Obsidian plugin — these have done/not-done answers.

**Evergreen:** Some areas are never finished. The canonical gardens grow with every debugging session. The quality lifecycle gets smarter with every release. The federation network expands with every team that adopts the garden. These are product dimensions, not engineering tasks. They are listed in each phase where they first appear and then managed as ongoing investment forever after.

---

### Phase 1 — Foundation

**Goal:** Claude can find garden entries in ≤ 3 tool calls, under 1,500 tokens. The structure is correct and everything that follows can build on it.

| Area | What's built | Depth |
|------|-------------|-------|
| **Structure migration** | 78 entries → one-file-per-entry with YAML frontmatter | Complete |
| **Multi-level indexes** | `_index/global.md`, domain `INDEX.md`, `_summaries/`, `labels/` | Complete |
| **SCHEMA.md** | v2.0.0, local backend | Complete |
| **Garden skill** | 3-tier retrieval, updated CAPTURE/MERGE/DEDUPE | Complete |
| **Systematic-debugging** | Step 0 garden consultation | Complete |
| **Quality lifecycle** | Active state only; `verified` date tracked | Shallow — Suspected/Superseded/Retired in Phase 3 |
| **Deduplication** | L1 (domain INDEX.md check at CAPTURE) | Shallow — L2/L3 in Phase 4 |
| **Label taxonomy** | Controlled vocabulary established, entries labelled | Complete; vocabulary grows over time |

**Not started:** GitHub backend, federation, web app, MCP, canonical org, CI automation.

---

### Phase 2 — GitHub Backend & Automation

**Goal:** Contributions are automated through GitHub. No manual file management. CI validates quality before anything reaches the garden.

| Area | What's built | Depth |
|------|-------------|-------|
| **GitHub repo** | knowledge-garden as GitHub-backed repo | Complete |
| **Sparse blobless clone** | `git cat-file --batch` retrieval model | Complete |
| **GitHub Issues as GE-IDs** | Conflict-free ID assignment | Complete |
| **CI validation** | `validate_pr.py` — format, vocabulary, Jaccard, injection scan | Complete |
| **CI integration** | `integrate_entry.py` — index maintenance on merge | Complete |
| **GitHub Actions** | validate-on-PR, integrate-on-merge workflows | Complete |
| **Quality lifecycle** | `status: suspected` CI auto-flagging, `staleness_threshold` | Deepened from Phase 1 |
| **Deduplication** | L2 Jaccard at CI level (Python, on PR open) | Deepened from Phase 1 |
| **Security** | Basic injection pattern scan in CI | Shallow — contributor credibility in Phase 9 |

**Not started:** federation, web app, MCP, canonical org.

---

### Phase 3 — Quality System

**Goal:** Entries age gracefully. Claude knows when to trust an entry and when to doubt it.

| Area | What's built | Depth |
|------|-------------|-------|
| **Full lifecycle** | Suspected → Superseded → Retired; `resolved-in`, `deprecated` | Deepened from Phase 2 |
| **Staleness CI** | Weekly scan — library version lag, `verified` age threshold | Complete |
| **`validate_garden.py --structural`** | Blocking pre-commit check | Complete |
| **`validate_garden.py --freshness`** | Advisory weekly check | Complete |
| **IMPORT workflow** | Ingest from changelogs, GitHub issues, CVEs | Initial implementation |
| **`discovery_count` tracking** | Incremented when a duplicate submission is discarded | Complete |
| **Known-gap entries** | `status: known-gap`, `priority: critical/high/normal` | Complete |
| **Coverage review** | Agent session, periodic, surfaces priority gaps | First pass; deepened every phase |
| **Coherence review** | Agent session, periodic, within domain | First pass; deepened every phase |

**Evergreen from this phase:** The quality lifecycle, coverage review, and coherence review are never finished. Each release makes them smarter. The goal is a garden that self-heals — entries degrade visibly rather than silently, and the gaps fill faster than new ones appear.

---

### Phase 4 — Duplication System (Full)

**Goal:** The garden stays lean as it grows. The same knowledge is never captured twice.

| Area | What's built | Depth |
|------|-------------|-------|
| **L2 full** | 1..n overlap handling, `_summaries/` pre-screen, MERGE session | Deepened from Phase 2 |
| **L3 DEDUPE** | Jaccard pre-screen via `_summaries/`, CHECKED.md, periodic sweep | Complete |
| **CHECKED.md governance** | All comparison pairs logged; pairs not re-checked | Complete |
| **DISCARDED.md** | Full discard log with conflict GE-IDs | Complete |
| **Cross-garden duplication** | When federation is live, L2 checks across parent chain | Blocked on Phase 6 |

**Evergreen from this phase:** The deduplication thresholds and algorithms are tuned continuously. As the garden grows and entry types diversify, the Jaccard thresholds and the semantic similarity detection improve. This is permanently in the background.

---

### Phase 5 — Ecosystem Foundation (Org + First Canonical Garden)

**Goal:** The garden stops being a personal tool and becomes a community resource.

| Area | What's built | Depth |
|------|-------------|-------|
| **GitHub org** | `<org-name>` created; governance model established | Complete |
| **`garden-spec` repo** | The open specification document published | v1.0; refined over time |
| **`garden-engine` repo** | All tooling migrated from personal repo | Complete |
| **First canonical garden** | `jvm-garden` (JE-) — existing entries migrated | First entries; evergreen |
| **Second canonical garden** | `tools-garden` (TE-) | First entries; evergreen |
| **Contribution model** | PR-based, CI-validated, public | Complete |
| **Open protocol decision** | Claude-specific vs. tool-agnostic — must be resolved | Strategic decision |

**Evergreen from this phase:** The canonical gardens grow with every debugging session, every REVISE, every IMPORT. They are the product. Phase 5 plants the seeds; the gardens grow indefinitely.

---

### Phase 6 — Federation (Shallow)

**Goal:** Personal and enterprise gardens can extend canonical ones. Knowledge flows down; contributions flow up.

| Area | What's built | Depth |
|------|-------------|-------|
| **SCHEMA.md federation config** | `role: child/peer/canonical`, upstream chain | Complete |
| **Client config** | `~/.claude/garden-config.yaml`, domain ownership | Complete |
| **Multi-garden retrieval** | Child chain walk (Tier 1/2/3 across parents) | Initial implementation |
| **Peer retrieval** | Parallel search across peer gardens | Initial implementation |
| **Submission routing** | Domain ownership → route to correct garden | Complete |
| **`_augment/` layer** | Private augmentation of parent entries | Shallow — deepened in Phase 9 |
| **Non-duplication enforcement** | Level 1 check spans full upstream chain | Complete |

**Not started:** `_watch/` CI, external library monitoring, contributor credibility.

---

### Phase 7 — Human Interfaces

**Goal:** Humans can browse, contribute to, and understand the garden without touching the CLI.

| Area | What's built | Depth |
|------|-------------|-------|
| **Obsidian plugin** | Native YAML → tags, See-also → wikilinks, staleness view | Low effort; native format |
| **Web app** | Domain view, label view, search, entry detail | Initial implementation |
| **Web app graph view** | `_graph/edges.md` → visual network | Phase 7b or 8 |
| **Export** | Garden entries → PDF, slide deck | Future |

---

### Phase 8 — MCP Server

**Goal:** Any AI assistant — not just Claude Code — can query and contribute to the garden.

| Area | What's built | Depth |
|------|-------------|-------|
| **`garden_search()` tool** | 3-tier retrieval via MCP | Complete |
| **`garden_capture()` tool** | Submit to garden from any MCP-compatible assistant | Complete |
| **`garden_status()` tool** | Garden metadata, health summary | Complete |
| **Protocol formalisation** | If open-protocol decision went that way: publish spec for other implementors | Complete or deferred |

**Evergreen from this phase:** The MCP tool surface grows with every new capability. Retrieval success feedback, session core memory management, and the helpfulness scoring all become MCP-accessible features over time.

---

### Phase 9 — Federation (Deep) & Advanced Quality

**Goal:** Private gardens are fully sovereign. The quality system is self-reinforcing.

| Area | What's built | Depth |
|------|-------------|-------|
| **`_watch/` CI** | Parent monitoring for incoming duplicates | Complete |
| **External library monitoring** | `_watch/external.yaml`, release feed watching | Initial |
| **Retrieval success feedback** | `retrieval_count` tracking, `helpfulness_score` | Initial |
| **Session core memory (Trigger D)** | Promote hot entries to session-resident | Complete |
| **Contributor credibility** | Reputation signal from git provenance + contribution history | Initial |
| **Cross-domain contradiction detection** | Agent checks for entries that contradict across domains | Initial |
| **Fine-tuning pipeline** | Garden entries → training data → model fine-tune | Initial |

---

### Evergreen — Ongoing Investment Forever

These are not phases. They are dimensions of the product that are refined in every release, indefinitely.

| Dimension | What "progress" looks like | Never done because |
|-----------|--------------------------|-------------------|
| **Canonical gardens** | New entries, REVISE submissions, new domain gardens | New knowledge surfaces every day |
| **Quality lifecycle** | Better staleness heuristics, smarter coherence detection, deeper helpfulness scoring | Developer ecosystems change continuously |
| **Duplication system** | Lower false-positive rate, smarter semantic matching, cross-garden awareness | The knowledge surface always grows |
| **Federation network** | New canonical domain gardens, new enterprise forks, new peer relationships | Every team that adopts the garden extends the network |
| **The specification** | Each major architecture decision gets formalised, edge cases clarified | The system evolves; the spec follows |
| **Retrieval quality** | Session core memory, helpfulness scoring, keyword effectiveness tuning | Retrieval can always be faster and more accurate |
| **Known-gap filling** | Critical gaps get captured; new gaps discovered at same rate or faster | New technologies, new non-obvious behaviours, forever |

---

## Phase 1 Scope

*What gets built first. Everything else in this document is later.*

Phase 1 is the foundational restructure — without it, nothing else in this document is buildable. It delivers a working v2 garden that Claude can use immediately, with the correct structure for everything that follows.

**ID assignment in Phase 1:** The GitHub Issues as GE-ID model (described in GitHub Backend Architecture) is a Phase 2 concern. In Phase 1, GE-IDs continue to be assigned via the sequential counter in GARDEN.md — the same mechanism as today. The GitHub backend section describes the target state, not the Phase 1 state.

**Personal garden as a legitimate use case:** `mdproctor/knowledge-garden` is not merely a temporary stepping stone to the community ecosystem — it is a valid, permanent configuration. A solo developer's private garden (local mode, sequential IDs, manual merge) is a first-class deployment. The ecosystem org and canonical domain gardens are the community layer that develops on top, not a replacement for personal gardens.

### Phase 1 Deliverables

**In `mdproctor/knowledge-garden` (the garden data and platform repo):**

- [ ] Migrate all 78 existing entries to individual files with YAML frontmatter (one-file-per-entry)
- [ ] Add all mandatory frontmatter fields (`id`, `type`, `stack`, `labels`, `keywords`, `symptom`, `context`, `score`, `captured`, `verified`, `staleness_threshold`)
- [ ] Create `_summaries/` directory — one auto-generated summary file per entry
- [ ] Create domain `INDEX.md` files in all existing domains (`quarkus/`, `tools/`, `java/`, etc.)
- [ ] Create sub-directories within domains at ≥3 entry threshold (`quarkus/cdi/`, `quarkus/quarkus-flow/`, etc.)
- [ ] Create `labels/` directory with the controlled vocabulary taxonomy and initial label files
- [ ] Create `_index/global.md` (domain routing table)
- [ ] Shrink `GARDEN.md` to metadata-only; move index content to domain INDEX.md files
- [ ] Write `SCHEMA.md` v2.0.0
- [ ] Add `README.md` to every domain directory
- [ ] Assign initial labels to all existing entries (at least one `domain-*` label, one `symptom-*` for gotchas)
- [ ] Validate with `validate_garden.py --structural` (exits clean before declaring done)

**In `mdproctor/cc-praxis` (the skills repo):**

- [ ] Update `garden/SKILL.md`: replace SEARCH with 3-tier retrieval algorithm
- [ ] Update `garden/SKILL.md`: update CAPTURE workflow (Level 1 check using domain INDEX.md + `_summaries/`)
- [ ] Update `garden/SKILL.md`: update MERGE workflow (Level 2 check, summary pre-screening, index maintenance)
- [ ] Update `garden/SKILL.md`: update DEDUPE workflow (Level 3, Jaccard pre-screen via `_summaries/`)
- [ ] Update `garden/SKILL.md`: add IMPORT and QUERY-BACK workflows
- [ ] Update `garden/SKILL.md`: add lifecycle frontmatter fields, known-gap status, discovery_count
- [ ] Update `systematic-debugging/SKILL.md`: add Step 0 garden consultation

### Explicitly Out of Phase 1

The following are designed and documented but not built in Phase 1:

- GitHub backend (sparse blobless clone, GitHub Issues as GE-IDs, PR submission workflow)
- CI/CD automation (validate_pr.py, integrate_entry.py, GitHub Actions)
- Federation architecture (canonical/child/peer, `_augment/`, `_watch/`)
- Web app or Obsidian plugin
- MCP server
- Fine-tuning, synthetic data generation
- Background autonomous agents
- Multi-language support
- Backlink graph
- Search analytics
- GitHub org creation and canonical domain gardens

### Phase 1 Success Test

After Phase 1, a Claude session debugging a Quarkus CDI problem should:
1. Consult the garden automatically (via systematic-debugging Step 0)
2. Find the relevant entry in ≤ 3 tool calls without loading irrelevant content
3. The total token cost of the garden consultation should be ≤ 1,500 tokens

If this test passes, Phase 1 is complete.
