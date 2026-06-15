---
name: write-content
description: >
  Use when writing any piece of content — project diary entry, blog post,
  article, note, brief, README, news item, technical documentation section, or essay.
  User says "write", "draft", "write a diary entry", "log what we built",
  "document this pivot", "blog all the work to date", "create a post",
  "write up", "write the README", "rewrite the README", or provides a topic/subject to write about.
  Documentation types (tutorial, how-to, explanation, reference) are in scope.
  NOT for generating code (use java-dev, ts-dev etc.).
---

# Write Content

Universal content creation skill. Three-layer taxonomy: Form (what it is),
Mode (how it presents), Voice (how it sounds). Five steps — do not skip.

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

## Step 1 — Guided routing

Present questions in sequence. Single-letter answers. `←` marks the default — Enter accepts it.
Auto-route directly (skip Q1) when the invocation is unambiguous:
- "write the README", "update the README", "rewrite the README" → **README**
- "write a diary entry", "document this pivot", "blog all the work", invoked in project diary context → **Diary**
- "write the Gotchas section for X" → **Tech doc / How-to/diagnostic**
- "write the Pattern to replicate for X" → **Tech doc / Tutorial**

### Q1 — Form

```
What are you writing?

  [D] Diary                     ← default
  [N] Note
  [A] Article
  [B] Brief
  [R] README
  [T] Technical documentation
  [W] News / announcement
```

### Q2 — Sub-type or section

Show only when Q1 result has sub-types. Omit for Diary, Brief, README, News (fixed mode — go to Q3).

**README skips Q3 (voice).** Always system-centric. Personal style energy and anti-slop apply but not personal register.

**If Note:**
```
Note type?

  [M] Musing — quick reaction or observation   ← default
  [I] Idea — specific proposal
```

**If Article:**
```
Article type?

  [E] Explanation — understand why or how      ← default
  [T] Tutorial — learn by doing
  [H] How-to — complete a task
  [C] Commentary — personal take
  [S] Essay — argued position
```

**If Technical documentation:**
```
Which section?

  [1] "What it adds"          →  Explanation/comparative
  [2] Gotchas                 →  How-to/diagnostic
  [3] Key files               →  Reference/inventory
  [4] Key wiring              →  Reference/lookup
  [5] Pattern to replicate    →  Tutorial
  [6] Architectural decisions →  Argumentation/rationale
  [7] ADRs                    →  Argumentation/decision
  [8] Anti-patterns           →  How-to/diagnostic
  [9] Other section           →  (load forms/technical-documentation.md and check mode map)
```

### Q2b — Mode disambiguation

Show only for the two Article sub-types where mode sub-type needs a decision.

**If Article/Explanation:**
```
Explanation mode?

  [D] Discursive — concept, builds mental model, personal voice ok   ← default
  [C] Comparative — before/after change, system-centric, length-capped
```

**If Article/How-to:**
```
How-to mode?

  [P] Procedural — reader in working state, accomplishing a task   ← default
  [G] Diagnostic — reader in broken state, Symptom → Cause → Fix
```

### Q3 — Voice

```bash
ls ~/claude-workspace/writing-styles/ 2>/dev/null
```

If personal style files found:
```
Voice?

  [P] Personal — <detected-filename>   ← default
  [C] Common
```

If no personal style files:
```
Voice?

  [C] Common   ← default
```

### Load files and confirm

After all questions answered, load `modes/_universal.md` first, then:

| Selection | Form file | Mode file |
|---|---|---|
| Diary | `forms/diary.md` | `modes/explanations.md` |
| Note/musing or Note/idea | `forms/note.md` | — |
| Article/tutorial | `forms/article.md` | `modes/tutorial.md` |
| Article/how-to/procedural | `forms/article.md` | `modes/how-to.md` |
| Article/how-to/diagnostic | `forms/article.md` | `modes/how-to.md` |
| Article/explanation/discursive | `forms/article.md` | `modes/explanations.md` |
| Article/explanation/comparative | `forms/article.md` | `modes/explanations.md` |
| Article/commentary | `forms/article.md` | — |
| Article/essay | `forms/article.md` | `modes/argumentation.md` |
| Brief | `forms/brief.md` | `modes/reference.md` |
| README | `forms/readme.md` | mixed — see section mode map in form file |
| News | `forms/news.md` | — |
| Tech doc / "What it adds" | `forms/technical-documentation.md` | `modes/explanations.md` |
| Tech doc / Gotchas | `forms/technical-documentation.md` | `modes/how-to.md` |
| Tech doc / Key files | `forms/technical-documentation.md` | `modes/reference.md` |
| Tech doc / Key wiring | `forms/technical-documentation.md` | `modes/reference.md` |
| Tech doc / Pattern to replicate | `forms/technical-documentation.md` | `modes/tutorial.md` |
| Tech doc / Arch decisions | `forms/technical-documentation.md` | `modes/argumentation.md` |
| Tech doc / ADRs | `forms/technical-documentation.md` | `modes/argumentation.md` |
| Tech doc / Anti-patterns | `forms/technical-documentation.md` | `modes/how-to.md` |

Also load voice per Q3: personal style file or `voice/common-voice.md`.

**Routing confirmation — always show before proceeding:**
```
Writing:  <Form>/<sub-type> — <Mode>/<sub-type>
Voice:    <Personal (filename)> or <Common>
```

**Cross-post:** if content genuinely spans two types, classify primary first using:
1. Strip test — which type survives if the other is removed?
2. Intent test — what was the main goal?
3. Structure test — which type's conventions does it follow?
Format: `primary_type/subtype + secondary_type/subtype`. Cross-posts are rare.

---

## Step 2 — Pre-draft gate

`mandatory-gates.md` was loaded in Step 0. Routing was confirmed in Step 1. Before generating any prose, produce
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

## Step 3 — Write

Generate content following:
1. Form file (structure, length, what's required, voice by sub-type)
2. Mode file (constraint set, voice texture)
3. Voice files (register, anti-slop)

*Generate raw, then edit ruthlessly. First pass captures content; editing pass
removes AI-naturalized filler, hedging, and false balance.*

**Do not show the draft to the user before completing Step 4.**

---

## Step 4 — Quality check + third-party review

**Run before presenting the draft. Never show a draft that has not passed this gate.**

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
"update the What it adds section"; also automatically as part of `work-end` Step 3b
pre-close sweep and `handover` wrap checklist (diary type).

**Loads:**
- `write-content/modes/_universal.md` — always
- `write-content/mandatory-gates.md` — always (Step 2, Step 4)
- `write-content/voice/anti-slop.md` — always
- `write-content/voice/mandatory-rules.md` — always
- `write-content/voice/common-voice.md` — fallback voice (if no personal style)
- `write-content/forms/<type>.md` — per content form
- `write-content/modes/<mode>.md` — per mode (if applicable)
- Personal style file from `~/claude-workspace/writing-styles/` — if configured

**Feeds into:** `publish-blog` — handles publishing mechanics when diary entries
are ready to go out.
