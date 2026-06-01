# Mode: Explanations

Two sub-types. Choose before writing — they have different structural constraints
and different voice signatures.

---

## Choosing between sub-types

**Primary question:** Is the subject a concept (timeless, needs a mental model)
or a change (delta, before/after state)?

- Concept → **discursive**
- Change → **comparative**

**Confirming test:** Does the author's experience of arriving at understanding
matter to the reader?
- Yes — the journey is content → **discursive**
- No — only the result matters → **comparative**

**Length check:** If it cannot fit in 2–4 sentences + bullets → probably discursive.
Comparative has a hard length cap; discursive does not.

**Edge case — explaining a design decision the author made:** If the author's
reasoning IS the content (the reader needs to follow the thought process) →
discursive. If the explanation would read the same with a different author →
comparative. The test: would stripping "I" leave the explanation intact?
If yes → comparative.

---

## Discursive sub-type

Author-centric. The subject is a concept the reader needs to build a mental model
of. The author's journey through understanding is part of the content.

**Used by:** Article/explanation, diary entries with teaching intent, commentary
that explains rather than argues.

**Rules:**
- Personal voice allowed — "I used to think X, but it turns out Y"
- Analogies from unexpected domains are valuable
- Show the evolution of understanding, not just the conclusion
- Acknowledge genuine uncertainty where it exists
- Reader arrives without a mental model; leaves with one
- Ends when the mental model is complete
- No length cap — ends when the concept is understood

**Voice texture:**
Right: personal honesty about uncertainty ("I still don't fully understand why
this works"); analogies that illuminate from unexpected domains; evolution of
understanding visible in the prose structure.
Wrong: clinical distance, passive voice ("this demonstrates"), treating the
reader as a stranger without prior relationship to the author, manufactured
objectivity.

---

## Comparative sub-type

System-centric. The subject is a change — a before/after state, a delta,
what this layer or component adds. The author's journey is irrelevant; only
the system state matters.

**Used by:** Technical documentation "What it adds" sections, design documents,
architecture descriptions, any section where the point is what changed, not why.

**Rules:**
- Lead with Before:/After: contrast — not context-setting prose
- Hard length cap: 2–4 sentences of prose + bullets for what was added
- No personal voice — "the system" or named classes/components, not "I"
- No process narration ("we found", "this led to", "during implementation")
- Active specific verbs: "displaces", "fires", "opens a CaseInstance" — never
  "is designed to", "allows for", "enables the system to"
- "This" and "It" may not open a sentence — forces specific subject nouns
- No chaining with dashes or semicolons — one idea per sentence
- "Not closed here" or equivalent scope boundary — tell the reader what this
  section does NOT address

**Voice texture:**
Right: specific nouns (class names, file paths, error messages), specific verbs,
explicit Before:/After: contrast, confident claims with no hedging.
Wrong: "in many ways", "it could be argued", "this is interesting because",
gerund openings ("introducing X allows..."), passive voice, chained clauses
with dashes, missing scope boundary.
