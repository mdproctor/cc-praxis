# Anti-Slop Guidance

Universal rules. Apply to every piece of content regardless of form, mode, or voice.

Per-mode voice texture lives in each mode file (`modes/`) — load the relevant mode
file to get mode-specific voice guidance.
Per-form voice guidance lives in each form file (`forms/`).

---

## The AI trigger problem

Dense connected prose is now a format signal, independent of content quality.
Readers associate long paragraphs, elaborate sentence structures, and flowing
connective prose with AI-generated output. They disengage before evaluating
whether the argument is good.

This is a spectrum mismatch: content requiring How-to or Reference mode gets
generated in Explanation or Narration mode. **The fix is mode-first generation**
— identify the required mode before generating, generate to that mode's structural
constraints. The banned words below are symptoms of wrong-mode generation, not the
root cause. Fixing the mode prevents them from appearing.

---

## Universal banned words

Never use regardless of content type:

delve, tapestry, realm, crucible, nuanced, intricate, game-changer,
groundbreaking, transformative, leverage (as verb), synergy, seamlessly,
holistic, robust, paradigm, cutting-edge, innovative, exciting journey

---

## Universal banned patterns

- Opening with "In this post/article/essay I will..."
- Closing with "In conclusion..." or "Thanks for reading"
- Hedging with "it's worth considering that" or "one might argue"
- Superlatives without evidence ("the best", "the most powerful")
- Theatrical dramatisation ("everything hung by a thread", "the moment everything changed")
- Starting consecutive sentences with "This" or "It"
- Generic filler: "It's important to note", "It's worth mentioning", "Needless to say"

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
