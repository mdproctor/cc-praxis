# 0011 — Index-and-Lazy-Reference Pattern for Methodology Tools

Date: 2026-04-07
Status: Accepted

## Context and Problem Statement

The cc-praxis methodology family (garden, design-snapshot, write-blog,
session-handoff, idea-log, adr, update-claude-md) has grown to seven tools,
each producing a corpus of artifacts. Two tools already solved the retrieval
problem: GARDEN.md acts as a dual index never loaded in full — only the index,
then specific entries on demand. session-handoff references file paths rather
than loading content. These patterns haven't been universally applied: other
tools (design-snapshot, blog, idea-log) produce flat artifact directories with
no index, making them hard to reference selectively without loading everything.
As the corpora grow, this gap is increasingly a practical token problem.

## Decision Drivers

* Token budget: loading full artifact corpora is expensive and grows over time
* Composability: session-handoff and future tools need to reference artifacts
  across tools without loading them
* Scalability: corpora grow (garden already at GE-0073, blog at ~10 entries,
  design-snapshots accumulating)
* Discoverability: "what exists?" should be answerable from the index alone,
  without opening any artifact

## Considered Options

* **Option A — Index + lazy reference universally** — every methodology tool
  that produces a corpus gets a structured INDEX.md; cross-tool references use
  file paths, never inline content
* **Option B — Load on demand without a formal index** — keep current flat
  directories; callers use `ls` and read files as needed
* **Option C — External retrieval system** — vector DB, semantic search, or
  an MCP server for artifact lookup

## Decision Outcome

Chosen option: **Option A**, because the GARDEN.md pattern is already proven
to work at scale, the token savings are concrete and measurable, and it
composes naturally with the existing lazy-reference principle in session-handoff.
Option B doesn't scale: `ls` gives paths but no semantics, requiring reads
to decide relevance. Option C is premature infrastructure for problems that
structured indexes already solve within the context window.

### Positive Consequences

* Each tool's corpus is selectable in two hops: load INDEX.md, then load the
  one relevant artifact
* session-handoff can reference any tool's artifacts without loading them —
  pass the index path, not the content
* New methodology tools are designed index-first by default
* Future tooling (cross-tool search, meta-index) can be built on top of
  consistent index structure

### Negative Consequences / Tradeoffs

* Requires design and implementation work per tool (tracked in #36)
* INDEX.md files must be kept current as artifacts are added — another
  maintenance surface
* Index format needs standardisation to be useful cross-tool (part of #36)

## Pros and Cons of the Options

### Option A — Index + lazy reference universally

* ✅ Proven: GARDEN.md dual-index and session-handoff lazy references already work
* ✅ Token-efficient at any corpus size
* ✅ Composable: any tool can reference any other tool's index
* ❌ Upfront design work per tool
* ❌ Index drift risk if not maintained

### Option B — Load on demand without a formal index

* ✅ No design work needed now
* ❌ `ls` gives paths, not semantics — still need reads to decide relevance
* ❌ Doesn't compose across tools
* ❌ Worsens as corpora grow

### Option C — External retrieval system

* ✅ Potentially powerful for large corpora
* ❌ Infrastructure complexity far exceeds the problem size
* ❌ Requires MCP or external service; breaks offline/simple sessions
* ❌ Premature optimisation

## Links

* Implementing issue: mdproctor/cc-praxis#36 — Design project memory architecture
* Prior art: `garden/SKILL.md` § GARDEN.md structure (dual index by technology + symptom)
* Prior art: `session-handoff/SKILL.md` § "Read nothing just to reference it"
* Related idea: `docs/ideas/IDEAS.md` — "Holistic project-memory architecture" (2026-04-04)
