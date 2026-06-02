---
name: write-content
description: >
  Use when writing any piece of content — project diary entry, blog post,
  article, note, brief, news item, technical documentation section, or essay.
  User says "write", "draft", "write a diary entry", "log what we built",
  "document this pivot", "blog all the work to date", "create a post",
  "write up", or provides a topic/subject to write about.
  Documentation types (tutorial, how-to, explanation, reference) are in scope.
  NOT for generating code (use java-dev, ts-dev etc.).
---

# Write Content

Universal content creation skill. Three-layer taxonomy: Form (what it is),
Mode (how it presents), Voice (how it sounds). Seven steps — do not skip.

---

## Step 0 — Load voice

Load personal style file if configured:
```bash
ls ~/claude-workspace/writing-styles/ 2>/dev/null
# Load the author's personal style file if present
```

If no personal style file: load `voice/common-voice.md`.

Always load `voice/anti-slop.md`, `voice/mandatory-rules.md`, and `mandatory-gates.md`.

---

## Step 1 — Determine form

**Encoder/decoder theory (routing basis):**
- Note = encoder-dominant — assume shared context, don't over-explain
- Article = decoder-dominant — cold reader, provide context
- Brief = reality-dominant — scanning IS the experience
- Technical documentation = reality-dominant, multi-mode, maintained alongside system

**Intent table:**

| Intent | Form |
|---|---|
| "I want to capture what I built / what happened in this project" | **Diary** |
| "I want to record what I did / what happened" | **Note/log** |
| "I want to share a quick thought or reaction" | **Note/musing** |
| "I want to propose something specific" | **Note/idea** |
| "I want you to learn by doing" | **Article/tutorial** |
| "I want you to complete a task" | **Article/how-to** |
| "I want you to understand why X works" | **Article/explanation** |
| "I want to share my take on something" | **Article/commentary** |
| "I want to argue a position to a conclusion" | **Article/essay** |
| "I want maximum information density, minimum prose" | **Brief** |
| "I want to announce a release / event / industry news" | **News** |
| "I want to write/update documentation that grows alongside a system" | **Technical documentation** |
| "I want to document how this component works for developers and Claude" | **Technical documentation** |
| "I want to write/update arc42stories / design doc / platform guide" | **Technical documentation** |

**Diary signals:** "write a diary entry", "log what we built today", "document this pivot",
"blog all the work to date", "catch the blog up", invoked with no argument when context
is a project diary.

**Technical documentation distinguishing note:** maintained, not published. If the
content will be updated as the system evolves → technical documentation. Written once
for an audience → article. When in doubt: does the subject evolve? If yes → technical documentation.

**If unclear:** ask one question — "Is this primarily informing, explaining, or arguing?"

**Note vs Article test:** written quickly without heavy audience shaping (Note), or
crafted for a wider audience who needs context (Article)?

**Cross-post primary type determination:**
1. Strip test — which type survives if the other is removed?
2. Intent test — what was the main goal?
3. Structure test — which type's conventions does it follow?

Format: `primary_type/subtype + secondary_type/subtype`. Cross-posts are rare.

---

## Step 2 — Load form file

Load from `write-content/forms/`:

| Form | File |
|---|---|
| Diary | `forms/diary.md` |
| Note (any sub-type) | `forms/note.md` |
| Article (any sub-type) | `forms/article.md` |
| Brief | `forms/brief.md` |
| News | `forms/news.md` |
| Technical documentation | `forms/technical-documentation.md` |

**For technical documentation:** before proceeding to Step 3, read
`forms/technical-documentation.md` and identify the target section and its mode
from the mode map. Mode selection happens here — not mid-generation.

---

## Step 3 — Determine mode

For single-mode forms, mode follows from form + sub-type:

| Form / sub-type | Mode | Mode file |
|---|---|---|
| Article/tutorial | Tutorial | `modes/tutorial.md` |
| Article/how-to | How-to/procedural | `modes/how-to.md` |
| Article/explanation | Explanation/discursive | `modes/explanations.md` |
| Article/commentary | (voice-dominant — no mode file; use voice files) | — |
| Article/essay | Argumentation/essay | `modes/argumentation.md` |
| Brief | Reference/lookup | `modes/reference.md` |
| News | (voice-dominant — no mode file; use voice files) | — |
| Diary | Explanation/discursive | `modes/explanations.md` |
| Note/log | (voice-dominant — no mode file; use voice files) | — |
| Note/musing | (voice-dominant — no mode file; use voice files) | — |
| Note/idea | (voice-dominant — no mode file; use voice files) | — |
| Technical documentation | See mode map in `forms/technical-documentation.md` | varies |

For technical documentation: the mode was identified in Step 2. Load the declared mode file.

---

## Step 4 — Load mode files

Always load `modes/_universal.md` first.

Then load the specific mode file determined in Step 3 (if one applies).
Voice-dominant forms (commentary, news, notes) use the voice files only —
no specific mode file.

---

## Step 5 — Pre-draft gate

`mandatory-gates.md` was loaded in Step 0. Before generating any prose, produce
this checklist output explicitly — do not skip, do not produce it silently:

```
Pre-draft gate:
☐ Voice classified — I/we/Claude register decided per section
☐ Content focus checked — process narration removed (build runs, test counts, methodology, agent counts)
☐ Factual accuracy checked — durations/counts verified against git log or session context
☐ Banned words scanned — anti-slop.md applied
```

Replace each `☐` with `✅` once verified. **Do not proceed to Step 6 until all
four show ✅ and the checklist is shown to the user.** Do not show a draft that
fails any item — fix first, then show.

**Voice classification:**
- For forms with author participation (diary, article, note, brief, news): decide
  I/we/Claude register for each section in advance
- For technical documentation: confirm target section, its mode from the mode map,
  and that the correct mode file is loaded

**Content focus check (from `mandatory-rules.md`):**
- Strip any sentence about: build passing, test counts, CI runs, methodology followed,
  number of agents/subagents, iteration counts, which skills or tools were invoked
- These are process narration — readers don't care how the code was produced

**Factual accuracy check:**
- Any duration, count, or magnitude claims? Verify against git log or session context
- If unverifiable: qualify as an estimate or remove

---

## Step 6 — Write

Generate content following:
1. Form file (structure, length, what's required, voice by sub-type)
2. Mode file (constraint set, voice texture)
3. Voice files (register, anti-slop)

*Generate raw, then edit ruthlessly. First pass captures content; editing pass
removes AI-naturalized filler, hedging, and false balance.*

---

## Step 7 — Quality check + third-party review

**Quality check:**
- Does it scan? Strip labels, read only those — complete factual skeleton with no gaps?
- Does it apply the correct mode? (Gotcha → Symptom/Cause/Fix; wiring → bold lead-in + 1–3 sentences)
- Does it sound human? (no banned words, no AI patterns from `voice/anti-slop.md`)
- Does it match the intent? (right form, right audience)
- Does it end when the point is made?

**Third-party review (from `mandatory-gates.md`):**
Scan draft for named persons or identifiable groups; flag each; wait for author
decision before writing to disk. See `mandatory-gates.md` for full procedure.

---

## Skill Chaining

**Invoked by:** User directly — "write a diary entry", "write an article about X",
"draft a brief", "log what we built today", "write the Gotchas section for layer X",
"update the What it adds section"; also automatically as part of the `handover`
wrap checklist (diary type).

**Loads:**
- `write-content/modes/_universal.md` — always
- `write-content/mandatory-gates.md` — always (Step 5, Step 7)
- `write-content/voice/anti-slop.md` — always
- `write-content/voice/mandatory-rules.md` — always
- `write-content/voice/common-voice.md` — fallback voice (if no personal style)
- `write-content/forms/<type>.md` — per content form
- `write-content/modes/<mode>.md` — per mode (if applicable)
- Personal style file from `~/claude-workspace/writing-styles/` — if configured

**Feeds into:** `publish-blog` — handles publishing mechanics when diary entries
are ready to go out.
