# Form: InfoBrief (Informative Brief)

Maximum information density, minimum prose. Fully scannable — scanning IS the
experience. There is no deeper layer to pull the reader into. What you see
on scan is all there is.

**Academic grounding:** Kinneavy's referential/informative aim.
Newman's description. Diátaxis's Reference type.

**Canonical example:** casehubio/devtown#24 (compact version, not the deep dive)

---

## Core principle

Structure first, prose second. If content can be a table or bullet list, it
should be. Prose is for reasoning that genuinely requires it — where ideas
connect and build. Everything else: structure.

**Ruthless editing:** make it denser and more telegraphic than a human would
naturally write. This ironically makes it feel more human. Experts write densely.

---

## Format rules

| Element | When to use |
|---------|-------------|
| **Problem statement** | 1–2 sentences. What's broken or missing. |
| **Bullet list** | Discrete items — options, constraints, steps, requirements |
| **Table** | Comparisons, status tracking, scoring, attributes across items |
| **Bold lead-in** | Key concept at the start of a paragraph; replaces a topic sentence |
| **Status table** | `✅ done` / `🔲 to build` — what exists vs what's needed |
| **Open questions** | Flat list; no answers yet |
| **`<details>` toggle** | Deep dive content for readers who want more; never required reading |

---

## Structure pattern

1. **Problem** — 1–2 sentences. What's broken or missing.
2. **Idea / solution** — what it does, in plain terms
3. **How it works** — tables and bullets; no narrative
4. **What's already built** — status table with ✅ / 🔲
5. **What still needs building** — bullet list
6. **Open questions** — flat list; no answers yet
7. **Deep dive** (optional) — `<details>` toggle for elaboration

Not every piece needs all sections. Use what's needed; omit the rest.

---

## Sentence and paragraph rules

- One idea per sentence
- One point per paragraph — or use a bullet list instead
- Lead with the conclusion, not the build-up
- No preamble ("In this brief I will...")
- No summary ("In conclusion...")

---

## The navigation layer (optional)

When a longer form exists (an article or essay), the InfoBrief can link its
sections, paragraphs, and bullets to the corresponding deeper content.
The InfoBrief becomes the TLDR with links throughout — a navigable entry point.

Each section of the InfoBrief links to the relevant section of the article.
The reader who is satisfied by the scan stops there.
The reader who wants more clicks through to exactly what they need.

**The navigation layer is opt-in, not a requirement.** A standalone InfoBrief
is complete on its own — no deeper layer needed.

**Cross-post format:** `InfoBrief + Article/explanation` or `InfoBrief + Article/essay`

---

## Deep dive toggle

Use `<details><summary>📄 Full specification</summary>` for content that:
- Explains the underlying model or mathematics in full
- Provides narrative examples or scenario walk-throughs
- Covers edge cases and threat models in depth

The main document must stand without it. The toggle is for readers who want
to go further — never required reading.

---

## What to avoid

- Narrative storytelling in the main body (move to deep dive)
- Long prose paragraphs where a table would do
- Elaborate setup before the point
- Rhetorical flourishes
- Hedging ("it might be the case that", "one could argue")
- Re-explaining things the audience already knows

---

## Historical note

InfoBrief is nearly absent from the historical corpus (3 instances in 577 posts).
It is a new form — not in the historical writing style. Do not force posts
into InfoBrief. Only use when maximum density is the actual goal.
