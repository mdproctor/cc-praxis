# Universal Mode Principles

Applies to every piece of content regardless of form, mode, or voice.
Load this before any specific mode file.

---

## Scannability — the cross-cutting requirement

Every piece of content must be scannable. Structure surfaces enough for a reader
to decide whether to go deeper — before they commit to reading.

| Form | What scanning gives the reader |
|---|---|
| Brief | The complete picture — scanning IS the experience |
| Note | Enough to know if it's relevant |
| Article | The argument skeleton — enough to decide to read |
| Technical documentation | The fact skeleton — every label is a fact; scanning gives the inventory |
| News | The fact — enough to act on or ignore |

Scannability is not about dumbing down. It is about respecting the reader's time.

---

## The sweet spot — label is the fact, body is the reasoning

Every entry has a label that could stand alone as a fact.
The body adds reasoning, not more facts.

**Strip test:** remove all labels and read only those. The result should be
a complete factual skeleton with no gaps. If a fact only exists in the body —
not in any label — it is invisible to scanning.

**Brief** breaks this by having no body (loses the why).
**Explanation** breaks this by burying the label inside prose.
The sweet spot keeps both.

---

## Element selection

Choose the element that minimises reading effort for the reader:

| Use | When |
|---|---|
| **Bullet list** | Discrete, enumerable items that don't flow into each other |
| **Table** | Comparison across consistent attributes — almost never wrong |
| **Numbered list** | Sequential steps where order matters |
| **Bold lead-in** | Key claim or concept at the start of a paragraph |
| **Prose paragraph** | Connected reasoning where ideas build on each other |
| **SVG/diagram** | Flows, architecture, relationships |
| **Code block** | Only when code IS the explanation, not decoration |

**The test:** Would a reader understand this faster as a list or prose?
If list → use it. If the ideas connect and build → prose.

**Never:** force connected reasoning into bullet points. Bullets fragment
what needs to connect.

---

## The heading test

Before finalising any heading, apply two tests:

**Journey test:** Does the reader need to know where they are in the argument
to understand this section? If yes → hybrid heading (position + theme).
If no → theme alone is sufficient.

**Position test:** "If I read only this heading, do I know both where I am
AND what this section is about?" If both — hybrid. If only one — simplify.

**Never:** bare structural labels — `## Introduction`, `## Conclusion`, `## Section 3`

**Hybrid heading pattern** (essays, long articles, technical documentation with position):
- `## 1. At Generation Time: The Token Cost Argument` — number + context + theme
- `## 4. The Call to the Industry` — number + pure theme (when position is obvious)

**Pure theme** (short articles, notes, news, technical documentation sections):
- `## What the evidence shows` — no number needed

The hybrid heading pattern applies most strongly in argumentation/essay mode —
where the reader navigates a progressive argument — and in technical documentation
where section position in the mode map matters.

---

## Sentence and paragraph rules

- One idea per sentence where possible
- Short paragraphs — 1–3 sentences in most cases
- Lead with the conclusion, not the build-up
- No preamble ("In this article I will...")
- No summary ("In conclusion...")
- End when the point is made

---

## The AI sensor problem

LLMs default to the prose end of the structure–prose spectrum — dense, connected
paragraphs. This is statistical pressure from training on prose-dominant text.
The reader's pattern detection now associates this prose texture with AI-generated
output and disengages before evaluating whether the argument is good.

**The fix is mode-first generation, not word-level editing.** Identify the required
mode before generating. Generate to that mode's structural constraints. Banned words
are symptoms of wrong-mode generation — fixing the mode prevents them.

---

## Tutorial naming disambiguation

**"Tutorial mode"** names the writing constraint set: sequential numbered steps,
imperative sentences, zero assumed domain knowledge, reader does something.

**"Article/tutorial"** names the form sub-type: an Article written so the reader
acquires a capability.

These are the same concept at different layers. Article/tutorial always uses
tutorial mode. Technical documentation "Pattern to replicate" sections also use
tutorial mode though they are not Articles.
