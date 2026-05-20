# Anti-Slop Guidance

Apply to every piece of content. Avoiding AI-sounding prose is not about
dumbing down — it is about format awareness in a changed reading environment.

---

## The AI trigger problem

Dense connected prose is now a format signal, independent of content quality.
Readers associate long paragraphs, elaborate sentence structures, and flowing
connective prose with AI-generated output. They disengage before evaluating
whether the argument is good.

This is environmental, not the author's fault. But it must be addressed.

---

## Universal banned patterns

Never use these regardless of content type:

**Words:** delve, tapestry, realm, crucible, nuanced, intricate, game-changer,
groundbreaking, transformative, leverage (as verb), synergy, seamlessly,
holistic, robust, paradigm, cutting-edge, innovative, exciting journey

**Structural patterns:**
- Opening with "In this post/article/essay I will..."
- Closing with "In conclusion..." or "Thanks for reading"
- Hedging with "it's worth considering that" or "one might argue"
- Superlatives without evidence ("the best", "the most powerful")
- Theatrical dramatisation ("everything hung by a thread", "the moment everything changed")
- Starting consecutive sentences with "This" or "It"
- Generic AI filler: "It's important to note", "It's worth mentioning"

---

## The master anti-slop instruction

Add to every content generation prompt:

```
Write in a natural, human style. Avoid all AI-sounding patterns:
- No words like: delve, tapestry, realm, crucible, nuanced, intricate,
  game-changer, groundbreaking, transformative, leverage, synergy, seamlessly,
  holistic, robust, paradigm
- Vary sentence length. Mix short, punchy sentences with longer ones.
- Use specific, concrete details and numbers instead of vague abstractions.
- Sound like a sharp, opinionated human who has real experience with this topic.
- End when the point is made. No summary. No "thanks for reading."
```

---

## Per-type guidance

### Note/log
Should feel raw. High first-person. "I've just got this working", "Still not
sure whether". Allow fragments. Allow rough edges. Do not polish.
Typos and uncertainty are authentic signals of genuine work-in-progress.

### Note/musing
Quick, informal, encoder-dominant. Point at the external thing and react.
One or two sentences of actual opinion, then stop. No elaboration.

### Note/idea
Propose something specific. "We should do X because Y." Not a full essay —
just enough to capture the proposal before it evaporates.

### Article/tutorial
Include real friction points. "I got stuck here because..."
"What I wish I knew earlier." A tutorial with no stumbling blocks reads as
AI-generated. Sequential, hands-on, the reader does something.

### Article/how-to
Step-oriented. Assume some prior knowledge. Include "why this step, not that"
where non-obvious. Acknowledge what can go wrong. Real how-tos have warnings
and edge cases.

### Article/explanation
Use analogies from unexpected domains. Show the evolution of your own
understanding — "I used to think X, but it turns out Y." Not about doing
— about understanding.

### Article/commentary
Lean heavily into personal opinion and subjective experience. This is where
the practitioner voice is most important. State the position directly.
Often ends with an open question or ironic twist.

### Article/essay
Strong personal voice + clear stance. Engage counter-arguments naturally,
not formulaically. Mandate one surprising or contrarian point. The argument
is logos-first; passion is the human layer that makes evidence feel important.

### InfoBrief
Ruthless editing — make it denser and more telegraphic than a human would
naturally write. This ironically makes it feel more human. Experts write
densely. The InfoBrief should feel like it was written by someone who knows
exactly what matters and respects the reader's time.

### News
Fast, direct, with clear sourcing. Opinion clearly separated from fact.
No padding. No "this is an exciting development" — just what happened
and why it matters.

---

## Workflow

**Generate raw → edit ruthlessly:**
Use the first draft as raw material, not the product.
A heavy human editing pass removes what AI naturalises: the filler,
the hedging, the false balance.

**Staged generation:**
1. Quick musing/log in raw voice — thinking out loud, no editing
2. Expand into full Article/Essay — structure applied
3. Human revision pass — voice, specificity, anti-slop check

**Detection test:**
After generating, ask: "Does this read like typical AI slop? Be brutally honest."
Then fix flagged issues before showing the draft.
