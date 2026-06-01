# Mode: Argumentation

Three sub-types. All argue a position — the difference is scale and formality.

---

## Decision sub-type

Records a choice made and why. ADR (Architecture Decision Record) format.
Written after a decision is made, not while deliberating.

**Used by:** `docs/adr/`, §10 Architectural Decisions in arc42stories,
any formal record of a significant design choice.

**Structure:**
```
### [Short name for the decision]

**Date:** YYYY-MM-DD
**Context:** [Situation that required a decision. What forces were in play?]
**Decision:** [The choice made, stated directly.]
**Consequences:** [What follows from this choice — including unwanted consequences.]
**Source:** [Where the decision was worked out — design spec, layer entry, etc.]
```

**Rules:**
- Name the alternative considered — a decision without a rejected alternative
  is an assumption, not a decision
- State the tradeoff accepted — what was given up
- Name consequences including unwanted ones — honest records are usable records
- No hedging the decision — it was made; record it as made

**Voice texture — decision:**
Right: direct statement of the decision, named alternative, explicit tradeoff,
stated consequences (including negative).
Wrong: "we decided to go with X, which seems like it should work well", hedged
phrasing that leaves the decision uncertain, omitting what was rejected.

---

## Rationale sub-type

Inline reasoning within a larger document. Explains why this approach over
the alternatives considered. Shorter and less formal than a decision ADR.

**Used by:** Technical documentation "Architectural decisions" sections within
layer entries, design decisions embedded in code comments (rare), inline
justifications in specs.

**Rules:**
- State the alternative explicitly — "Why X rather than Y"
- Name the tradeoff accepted — what X costs vs. what Y would have cost
- One paragraph maximum — if it needs more, it's a decision-sub-type entry
- Does not hedge the conclusion — the choice was made; the rationale explains it
- Format: "**Why X rather than Y:** [reason]. Tradeoff: [what X costs]."

**Voice texture — rationale:**
Right: "Why `SlaBreachPolicy` in `casehub-work-api` rather than a new
`platform/apps-api` module: every consumer already has this on classpath;
the SPI is intrinsically work-bounded."
Wrong: "We considered putting it in a new module but felt that might add
unnecessary complexity, so we went with the current approach which seemed
more practical."

---

## Essay/sustained sub-type

Extended argument over numbered sections. Opens with a claim, earns it through
evidence and counter-arguments, closes without hedging.

**Core principle: structure navigates; prose argues.** Numbered sections tell
the reader where they are in the argument. The prose within each section carries
the reasoning. The structure is navigational, not argumentative — the argument
lives in the prose, not in the headings.

**Used by:** Article/essay (see `forms/article.md` for form-level structure
pattern), long-form technical arguments, position papers.

**The three appeals — in priority order:**

1. **Logos — argument and evidence (mandatory).** The essay stands or falls here.
   Logical, evidence-led, precise. If the argument doesn't hold, nothing else saves it.

2. **Ethos — credibility through expertise AND character.** Personal voice is
   part of ethos. Readers trust an argument more when they trust the person
   making it. Demonstrated through precision, naming disagreements directly,
   genuine enthusiasm, self-deprecation when warranted.

3. **Pathos — passion, not emotion.** Genuine engagement with the subject.
   Interesting, not bombastic. Passion strengthens the argument; it never
   substitutes for it.

**Argumentative, not persuasive.** Appeals to evidence and expertise, with
passion as the human layer. Never appeals to emotion to bypass critical thinking.

**Headings — the hybrid pattern:**

Every heading does double duty: number gives position, phrase gives meaning.

| Pattern | Example | When |
|---|---|---|
| Number + context + colon + theme | `## 2. At Review Time: Static Read-Through Reliability` | Section occupies a specific position in a progression |
| Number + theme | `## 4. The Call to the Industry` | Position alone is sufficient context |
| Pure thematic (no number) | `## What the Argument Establishes` | Position obvious from surrounding structure |

**The colon separator** (`context: theme`) is the strongest form — tells the
reader where they are AND what the argument claims there.

**Never:** `## Introduction`, `## Conclusion`, `## Summary`, `## Section 3`

**Prose mechanics:**

- **Bold lead-ins** announce key claims or counter-arguments:
  `**A fair counter:**`, `**The enterprise implication:**`
- **Counter-arguments** addressed inline — not deferred to a separate section
- **Data and citations** in sentences when part of the argument; tables when
  comparing multiple data points
- **Italic preambles** at the start of each part in a multi-part essay — orient
  the reader without requiring them to have read previous parts

**The hubris test:** Does the passion strengthen the argument, or substitute
for it? If the former — it belongs. If the latter — cut it.

**Voice texture — essay/sustained:**
Right: strong personal voice carrying the argument; logos-first (evidence and
expertise, not credential-listing); one surprising or contrarian point mandated;
passion reinforces evidence, never substitutes for it; conclusion states the
position directly.
Wrong: appeals to authority without evidence, emotional claims substituting
for argument, conclusions that hedge the position, argument that runs parallel
to the evidence rather than through it, bullet lists for main reasoning
(fragments what needs to connect).
