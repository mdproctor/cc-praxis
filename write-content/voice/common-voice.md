# Blog Writing — Common Voice

This is the default voice for authors who haven't created a personal style guide.
It gives you prose that is clear, direct, and credible — without prescribing a
specific personality. To add your voice, create a personal style guide at
`~/claude-workspace/writing-styles/` and set `PERSONAL_WRITING_STYLES_PATH`.

Note: audience and topic are inferred from the project's CLAUDE.md — this guide
covers *how* to write, not *what* to write about or *who* to write for.

---

## Tone

**Peer to peer.** You are a practitioner talking to other practitioners. Not a teacher
simplifying for beginners, not an executive speaking from altitude. The reader is
technically capable — treat them as an equal.

**Opinionated and direct.** State positions clearly. Don't hedge with "it might be
the case that..." or "one could argue...". If you have a view, say it.

**Intellectually honest.** Include failed attempts, wrong turns, and genuine
uncertainty. The iteration is what makes it credible. Smooth narratives with no
failed attempts read as sanitised retrospectives — not real development diaries.

**Not deferential about Claude.** Claude is a capable collaborator that also sometimes
goes its own way and needs reining in. Neither party is infallible. Write it as it
actually happened — Claude's mistakes and the author's wrong assumptions alike.

---

## Prose Style

**Sentence length:** target ~17 words. Mix short punchy statements with longer
technical explanations. Avoid monotonous rhythm in either direction.

**Paragraph density:** 1–2 sentences. Single-sentence paragraphs are fine and normal
for key points. Don't pad short paragraphs; don't bury key points in long ones.

**Specific over vague.** "Claude came back immediately: `sync-local: unrecognized arguments: --skills`" is more valuable than "the install command didn't work as expected."
Keep exact error messages, file paths, command names, and numbers.

**Numbers used confidently.** "48 false positives", "17 validators", "six days".
Precise, not rounded.

---

## What to Avoid

- Explaining what you're about to do before doing it
- Summarising at the end what you just said
- Generic AI filler: "In conclusion", "To summarise", "It's important to note",
  "delve into", "exciting", "powerful", "innovative", "game-changing"
- Excessive hedging: "it's worth considering that", "one might argue", "potentially"
- Passive voice where active is natural
- "X was chosen because" — passive voice hides who decided
- "Future work will determine" — distance from uncertainty, not honest engagement
- Starting consecutive sentences with "This" or "It"
- Superlatives without evidence: "the best", "the most powerful"
- Theatrical stakes: "everything hung by a thread", "the moment everything changed", "this broke everything" — unless clearly a joke
- Melodramatic emotional reactions: "I was devastated", "finally, relief" — keep emotional register measured

---

## Audience Calibration from CLAUDE.md

The project's CLAUDE.md tells you who the audience is. Use it:

| CLAUDE.md signal | Audience assumption |
|-----------------|---------------------|
| `type: java` or Java/Maven/Quarkus in stack | JVM practitioners — assume Maven, annotations, dependency injection are known |
| `type: python` or Python tools | Python practitioners — assume pip, virtualenv, type hints are known |
| `type: skills` or Claude Code skills | AI tool users — assume familiarity with LLM workflows, prompting, Claude Code |
| AI/LLM tools mentioned | AI-literate — don't explain what an LLM is |
| TypeScript/Node.js | Frontend/fullstack practitioners |
| Specific frameworks (Quarkus, React, Django...) | Assume familiarity with that framework |

Don't over-explain domain fundamentals the CLAUDE.md signals the audience already knows.
Don't under-explain if the topic is genuinely novel even to an expert audience.

---

## Personal Guide Note

This common voice gives you functional prose. It won't sound like a specific person —
that's intentional. To add your voice: what do you find yourself saying? What do you
never say? What makes your writing recognisably yours? Put those answers in a personal
style guide and the common voice recedes behind them.
