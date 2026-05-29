# Entry Template and Tone Reference

Used by `write-blog` Step 4 when drafting an entry.

---

## Tone Calibration by Phase

Match the writing to the moment.

| Phase | Natural tone | Model after |
|-------|-------------|-------------|
| **Day Zero** | Exploratory, honest about assumptions, energetic | "I thought this would be..." |
| **Phase Update** | Problem-solution oriented, showing iteration | "We tried X — it failed because..." |
| **Phase Update (architecture focus)** | Introspective, constraint-focused, thinking out loud | Short punchy sentences, then longer technical explanations |
| **Pivot** | Honest about what was abandoned, clear about why | "We were wrong about X. Here's what actually happened." |
| **Phase Update (milestone)** | Forward-looking, pragmatic, naming what was validated | "This phase proved that..." |

**Signs the tone is wrong:**
- Past tense throughout — sounds like a report, not a diary
- "X was chosen because" — passive voice hides who decided
- "Future work will determine" — distance from uncertainty, not honest engagement
- Smooth narrative with no failed attempts — sanitised, not real

---

## Entry Template

```markdown
# <Project Name> — <Phase Title>

**Date:** YYYY-MM-DD
**Type:** day-zero | phase-update | pivot | correction
**Corrects:** [YYYY-MM-DD-entry](YYYY-MM-DD-entry.md) *(only for correction entries)*

---

## What I was trying to achieve: <specific goal for this phase>
*(or "What we were trying to achieve: ..." for collaborative phases)*

<Context at this point. Where are we? What's the goal right now?
Write for a reader who hasn't followed the project — 2–4 sentences.>

## What we believed going in: <the assumption that turned out to matter>

<Assumptions, expectations, what I thought would happen. Include things that
turned out to be wrong — that's the point. Write what you actually believed,
not what you wish you'd believed.>

## <Thematic heading for the bulk of the work — name what actually happened>
*(e.g. "Three install attempts and a taxonomy", "The --skills flag that didn't exist",
"Six pivots, zero architecture changes". If this section has distinct sub-stories,
use thematic H3s beneath it rather than one undifferentiated block.)*

<The actual work done. For planning sessions: decisions made and why.
For implementation: what was built, bugs found, unexpected constraints,
real vs expected behaviour. Be specific — include exact error messages,
command output, file paths. "No error" is important context.>

## What changed and why: <the pivot or constraint that forced it>

<If anything pivoted, was rejected, or turned out differently than expected —
explain what changed and what caused it. Include what was tried before.
Omit this section if nothing changed.>

## What it is now
*(or another thematic close — "The discipline is the work", "Where this leaves us")*

<Current state and thinking, knowing it may change again. Honest about remaining
uncertainty. Don't pretend to certainty you don't have. End naturally — no
summary of what was just said, no "Thanks for reading". If there's a
forward-looking note, integrate it as a sentence here, not as a footer.>
```

**These headings are starting points, not rigid slots.** If a heading already has thematic character — `## The Pivots (There Were Several)`, `## Six Pivots, Zero Architecture Changes` — keep it. The structural label (`What we tried:`) is additive scaffolding, not a replacement. If a section heading is already specific and interesting, adding a structural prefix is optional. If it's a bare slot with no content, pair it with a thematic description. Never trade a heading that has personality for one that doesn't.
