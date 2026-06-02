# write-content

Universal content creation skill. Three orthogonal layers — Form, Mode, Voice — applied in sequence. Each layer answers a different question; none determines the others.

---

## The Three Layers

| Layer | Question answered | Directory | Examples |
|---|---|---|---|
| **Form** | What kind of content is this? | `forms/` | Note, Article, Brief, Diary, Technical documentation |
| **Mode** | How does it present information? | `modes/` | Tutorial, Explanation, Reference, How-to, Argumentation |
| **Voice** | How does it sound? | `voice/` | Mark Proctor's voice, common voice, anti-slop constraints |

**Form** and **mode** are orthogonal. A diary entry (form) uses Explanation/discursive mode. An arc42stories Gotcha section (technical documentation form) uses How-to/diagnostic mode. The form doesn't determine the mode.

**Mode** and **voice** are also orthogonal. How-to/diagnostic mode with a personal voice produces a different result than the same mode with common voice. The mode sets the structure; voice sets the register.

**This is the gap** that "writing style" had been filling without a name. Style was doing the work of all three layers simultaneously — which is why per-type anti-slop guidance felt both necessary and never quite right.

---

## Theoretical Foundation

The Form/Mode/Voice taxonomy didn't emerge from first principles. It converged independently with four established frameworks developed across 200 years, from completely different starting points, with no awareness of each other.

### The five independent arrivals

| Framework | Year | Starting point | Their term for mode |
|---|---|---|---|
| Newman | 1827 | Classical rhetoric | **modes** — narration, description, exposition, argumentation |
| Kinneavy | 1969 | Discourse theory; communication triangle | **aims** — expressive, referential, literary, persuasive |
| Britton | 1970 | Educational psychology; child development | **functions** — transactional, expressive, poetic |
| Anker | ~1998 | Pedagogical practice | **modes** — nine sub-modes of exposition |
| Diátaxis (Procida) | 2017 | Practical problem — Django docs disorganised | **types** — tutorial, how-to, reference, explanation |

Kinneavy, reading eight scholars in 1969, called the convergence "almost fearful symmetry." Procida, independently arriving at the same four-way split in 2017, had no knowledge of Newman, Kinneavy, or classical rhetorical theory. He was a philosopher solving a documentation problem.

The concept of *mode* — how information is structured and presented to the reader — converges across all five. The terminology doesn't converge: Kinneavy says "aim," Britton says "function," Diátaxis says "type," Newman and Anker say "mode." We use **mode** deliberately — it has the deepest lineage (Newman, 1827) and is already in our four-dimension framework under Anker.

### What each framework contributes

**Form** maps to Newman's intent dimension. What is the writing trying to do? Inform? Argue? Express? This is the top-level routing question.

**Mode** is Anker's dimension. Within the intent, how is information organised for the reader? Reference/lookup vs Reference/inventory are both informative (same form) but structurally different (different modes).

**Voice** maps to Kinneavy's encoder dimension — the writer's presence, register, and relationship with the reader. Personal voice vs common voice vs system-centric (no author) are voice choices, not form or mode choices.

### The anti-slop reframe

LLMs default to the prose end of the structure–prose spectrum:

```
JSON  Brief  Reference  How-to  Tutorial  Explanation  Essay  Narration  Novel
↑                                                                              ↑
machine-readable                                                         pure prose
```

The training corpus is prose-dominated. Anti-slop guidance corrects this by banning specific words and patterns — but those are symptoms. The root cause is mode mismatch: a Gotcha section is generated in Explanation mode when it needs How-to/diagnostic mode. Mode-first generation prevents the symptoms from appearing.

---

## Single-Mode vs Multi-Mode Documents

Every framework from Newman to Diátaxis treats mode as a property of the whole document. A text is a tutorial, or an explanation, or a reference. None of them address what may be the most common pattern in technical documentation: **documents that contain multiple modes across sections**.

### The gap in all five frameworks

A multi-mode document doesn't fit in any of the five frameworks. It's not a tutorial. It's not a reference. It's not an essay. It contains all of them in different sections, and which mode applies depends on the section being written.

Examples of multi-mode documents:
- **arc42stories** — six different modes across twelve section types
- **CLAUDE.md files** — conventions (Reference/lookup) + commands (How-to) + workflow narrative (Explanation)
- **Platform guides** — explanation + reference tables + anti-patterns (How-to/diagnostic)
- **Technical specifications** — requirements (Reference) + examples (Tutorial) + implementation notes (Explanation)

This may be the dominant pattern in technical documentation. None of the five frameworks have language for it.

### How write-content handles it

Single-mode forms (Note, Article, Brief, Diary) have one mode per document. The mode follows from the form sub-type.

Multi-mode forms (Technical documentation) declare a **mode map** — a table assigning a mode to every section type. Before writing any section, the mode is identified from the map. The correct mode file is loaded. The mode's structural constraints apply for that section only.

| Form | Mode handling |
|---|---|
| Note, Article, Brief, Diary, News | Single mode — follows from form sub-type |
| Technical documentation | Multi-mode — declared in `forms/technical-documentation.md` mode map |

---

## arc42stories as a Case Study

arc42stories is the reference implementation for multi-mode technical documentation. It has twelve distinct section types, six distinct modes.

### The mode map

| Section | Mode | Why |
|---|---|---|
| §8 Crosscutting pointer table | Reference/pointer | Points to authority; no inline content |
| §8 Anti-patterns | How-to/diagnostic | Reader is in a broken state; Symptom → Cause → Fix |
| §9.3 "What this delivers" | Explanation/comparative | Before/after contrast; user-visible outcome |
| §9.4 Key files | Reference/inventory | Enumerate what exists; path → one sentence |
| §9.4 Key wiring | Reference/lookup | Bold lead-in (the fact) + 1–3 sentences (the reasoning) |
| §9.4 "What it adds" | Explanation/comparative | Before/after contrast; system-centric; length-capped |
| §9.4 Gotchas | How-to/diagnostic | Symptom: observable. Cause: root mechanism. Fix: exact action. |
| §9.4 Pattern to replicate | Tutorial | Numbered steps; domain-agnostic; zero assumed context |
| §9.4 Architectural decisions | Argumentation/rationale | Why X rather than Y; named alternative; tradeoff accepted |
| §10 ADRs | Argumentation/decision | Context → Decision → Consequences; ADR format |
| §11–12 tables | Reference/lookup | Tables only; no prose narrative |
| §13 Glossary | Reference/lookup | Term → one-sentence definition |

### Why mode matters for "What it adds"

This section is the canonical example of prose drift — and why structural prescription prevents it.

The arc42stories spec gave the section a narrative instruction: *"teaching narrative, what this layer introduces, what gap it closes."* No structural prescription. Every implementation drifted to flowing prose.

Explanation/comparative mode prescribes:

```
**Before:** [previous state] — one clause.
**After:** [component @Annotation] — one clause.

What this layer adds:
- **[Named capability]** — [mechanism]; [what it prevents or enables]

Not closed here: [Layer N] ([what it still lacks]).
```

**Before this prescription:** prose paragraphs explaining the layer's history and design rationale — accurate but not scannable.

**After:** before/after contrast visible immediately; each addition labelled; scope boundary explicit. Scannable for humans; unambiguous for LLMs.

The prescription didn't change what was said. It changed how it was structured — which is mode, not voice, and not form.

### Sections that were already right

The Gotchas and Pattern to replicate sections in devtown's ARC42STORIES.MD were already in the correct mode before the taxonomy existed. The arc42stories spec prescribed their structure explicitly from the first commit: `Format: **Symptom** → Cause → Fix`, `numbered steps`. Following those constraints naturally produces content in the correct mode.

**The lesson:** structural prescription prevents mode drift. If you want a section to stay in How-to/diagnostic mode across every implementation, prescribe the structure. The mode follows.

---

## Mode Files

| File | Modes | Key constraint |
|---|---|---|
| `modes/_universal.md` | All | Scannability, heading test, element selection, sweet spot principle |
| `modes/explanations.md` | Discursive / Comparative | Discursive: author-centric, no length cap. Comparative: Before:/After:, length-capped, no personal voice |
| `modes/how-to.md` | Procedural / Diagnostic | Procedural: steps from working state. Diagnostic: Symptom → Cause → Fix from broken state |
| `modes/reference.md` | Lookup / Pointer / Inventory | No prose paragraphs. Each sub-type by reading behaviour. |
| `modes/argumentation.md` | Decision / Rationale / Essay/sustained | Decision: ADR format. Rationale: inline why. Essay: three appeals, hybrid headings. |
| `modes/tutorial.md` | Tutorial | Numbered steps; imperative sentences; zero assumed domain knowledge |

**Choosing between sub-types:**

*Explanation* — primary question: is the subject a **concept** (mental model → discursive) or a **change** (delta, before/after → comparative)?

*How-to* — primary question: what is the reader's starting state? **Working, trying to accomplish** (→ procedural). **Broken, trying to recover** (→ diagnostic).

---

## Form Files

| File | When to use |
|---|---|
| `forms/diary.md` | Capturing what happened in a project — personal voice, in-the-moment, not retrospective |
| `forms/note.md` | Quick record, reaction, or proposal — encoder-dominant, assumes shared context |
| `forms/article.md` | Full treatment for a wider audience — decoder-dominant, cold reader can follow |
| `forms/brief.md` | Maximum information density — scanning IS the experience |
| `forms/news.md` | External event worth sharing — reality-dominant, fast and direct |
| `forms/technical-documentation.md` | Maintained technical docs with dual audience (human + LLM) — multi-mode |

---

## Voice Files

| File | What it governs |
|---|---|
| `voice/anti-slop.md` | Universal banned words and patterns; master anti-slop instruction |
| `voice/common-voice.md` | Default fallback voice — peer-to-peer, opinionated, intellectually honest |
| `voice/mandatory-rules.md` | I/we/Claude register system; code block rules; image rules; content focus |

**Personal voice** lives in `~/claude-workspace/writing-styles/` — loaded when configured. Personal voice is a voice-layer file, not a form or mode file. It composes with any form and mode.

**Process gates** (pre-draft voice classification, factual accuracy, third-party reference review) live in `mandatory-gates.md` at the skill root — not in voice. They are control flow, not writing guidance.

---

## The Seven Steps

```
Step 0 — Load voice       (personal style or common-voice; anti-slop; mandatory-rules; mandatory-gates)
Step 1 — Determine form   (intent table; encoder/decoder theory; cross-post rules)
Step 2 — Load form file   (for technical documentation: identify mode from mode map here)
Step 3 — Determine mode   (from form + sub-type; or from mode map for technical documentation)
Step 4 — Load mode files  (_universal.md always; specific mode file if applicable)
Step 5 — Pre-draft gate   (voice classification; content focus; factual accuracy)
Step 6 — Write            (generate raw; edit ruthlessly)
Step 7 — Quality check    (scan test; mode check; human-sound check; third-party review)
```

For technical documentation, mode selection happens at **Step 2** — when the form file is loaded. The mode map in `forms/technical-documentation.md` identifies which mode applies to the target section. Steps 3–4 confirm and load the mode. This prevents mid-generation mode switching.

---

## This README is Multi-Mode

The structure of this document demonstrates the taxonomy it describes:

| Section | Mode used |
|---|---|
| "The Three Layers" table | Reference/lookup |
| "Theoretical Foundation" narrative | Explanation/discursive |
| "The five independent arrivals" table | Reference/lookup |
| "The anti-slop reframe" spectrum | Explanation/comparative |
| "arc42stories mode map" | Reference/lookup |
| "Why mode matters for 'What it adds'" | Explanation/comparative |
| "The Mode Files" table | Reference/inventory |
| "The Seven Steps" | Reference/lookup |
