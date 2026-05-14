# Idea Log

Undecided possibilities — things worth remembering but not yet decided.
Promote to an ADR when ready to decide; discard when no longer relevant.

---

## 2026-04-13 — Blog entry types: article vs. note, with routing metadata

**Priority:** medium
**Status:** active

Differentiate write-blog output into two types: `note` (current diary/journal
entries — session narrative, informal) and `article` (traditional topic or
summary post — polished, standalone readable). Each entry carries metadata
declaring target destinations: project blog, author's personal blog, one or
more group/syndication blogs. Cross-posting to multiple targets is supported.
Routing strategy at epic close: notes go to the project repo; articles route
per their metadata targets.

**Context:** Surfaced during brainstorm on DESIGN.md interaction model.
The current write-blog skill only produces diary-style notes. Articles serve
a different audience and need different routing — author blogs, group blogs,
and syndication targets beyond the project repo.

**Promoted to:** `docs/superpowers/specs/2026-04-14-blog-entry-types-design.md` (implemented 2026-04-14)

---

## 2026-05-13 — Command to toggle exhaustive note-taking mode

**Priority:** medium
**Status:** active

A cc-praxis skill or Claude Code command that toggles between two note-taking modes:

- **Selective (default):** Claude synthesises and summarises, capturing conclusions and key points. Fast, but loses nuance and detail from conversation.
- **Exhaustive:** Claude transcribes before synthesising — captures full reasoning chains, all findings, verbatim quotes worth preserving, and recent session content that hasn't been written up yet. Nothing is assumed to be recoverable later.

**Trigger:** User says "exhaustive notes on" / "exhaustive notes off" or invokes a command like `/notes-exhaustive`. Could also be triggered automatically when the user says "take notes" or "capture this."

**Why this matters:** The default synthesis mode consistently loses detail when note-taking spans a long session. The gap is hardest to recover at the end of a session when context is full but the most recent material hasn't been captured yet. An explicit toggle lets the user signal "I need everything, not a summary."

**Possible implementation:** A skill that sets a session flag and prepends an instruction to all note-writing actions. Or a CLAUDE.md convention that Claude checks before writing to any notes file.

---

## 2026-05-13 — Structured essay as default voice

**Priority:** medium
**Status:** active

Hypothesis: structured essay (numbered sections, hybrid thematic+structural headings,
dense prose carrying the argument) is the preferred default form for all communication
that naturally breaks into sections — not just long multi-part series. The 6-part
"When the Machine Codes" series is the canonical example.

If true, the taxonomy becomes: structured essay is the baseline; article-prose,
article-structured, brief, note-prose, note-structured are specialisations for
specific contexts. The README and style files should reflect this once validated
against real content.

**Deferred:** validate against new content before changing anything. Do not overwrite
existing style files until the preference is confirmed in practice.

---

## 2026-05-13 — Revisit existing content in middle and brief forms

**Priority:** low
**Status:** active

Most existing articles and notes were written in full narrative form. A middle
form exists between the current article (prose-led, narrative) and the brief
(pure data density) — structured prose where headers and bullets scaffold the
content but reasoning still lives in sentences. Hypothesis: much of the existing
content would be more readable in this middle form, and some would benefit from
being rewritten as a brief.

**Deferred:** revisit when there's time for a content audit. When ready: pick a
representative sample of existing posts, rewrite in middle and brief forms, compare.
Use the result to decide whether the middle form needs its own style file or is
just the updated article guide applied more aggressively.
