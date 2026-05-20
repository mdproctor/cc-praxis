---
name: write-content
description: >
  Use when writing any piece of content — blog post, article, note, brief,
  news item, or essay. User says "write", "draft", "create a post", "write up",
  or provides a topic/subject to write about. Routes to the correct content
  type and applies structure principles, form-specific guidance, and anti-slop
  rules. Documentation types (tutorial, how-to, explanation, reference) are
  in scope. NOT for generating code (use java-dev, ts-dev etc.).
---

# Write Content

Universal content creation skill. Determines content type, applies structure
principles, loads form-specific guidance, and writes content that is scannable,
human-sounding, and appropriate for the intended audience.

---

## Step 0 — Load writing style

If a personal style file exists for the author, load it:

```bash
ls ~/claude-workspace/writing-styles/ 2>/dev/null
# Load: mark-proctor-voice.md (if writing as Mark Proctor)
# Load: common-voice.md (if no personal style configured)
```

Always load `structure-principles.md` (this skill's defaults).

---

## Step 1 — Determine content type

Use the intent test to classify what is being written:

| Intent | Type |
|--------|------|
| "I want to record what I did / what happened" | **Note/log** |
| "I want to share a quick thought or reaction" | **Note/musing** |
| "I want to propose something specific" | **Note/idea** |
| "I want you to learn by doing" | **Article/tutorial** |
| "I want you to complete a task" | **Article/how-to** |
| "I want you to understand why X works" | **Article/explanation** |
| "I want to share my take on something" | **Article/commentary** |
| "I want to argue a position to a conclusion" | **Article/essay** |
| "I want maximum information density, minimum prose" | **InfoBrief** |
| "I want to announce a release / event / industry news" | **News** |

**If unclear:** ask one question — "Is this primarily informing, explaining, or arguing?"

**Note vs Article test:** Did you write this quickly without heavy audience shaping (Note), or is it crafted for a wider audience who needs context (Article)?

**Primary type determination for cross-posts:**
1. Strip test — which type survives if the other is removed?
2. Intent test — what was the main goal?
3. Structure test — which type's conventions does it follow?

---

## Step 2 — Load form guide

Load the appropriate form file from `write-content/forms/`:

| Type | Form file |
|------|-----------|
| Note (any subtype) | `forms/note.md` |
| Article (any subtype) | `forms/article.md` |
| Article/essay specifically | also load `forms/essay.md` |
| Brief | `forms/infobrief.md` |
| News | `forms/news.md` |

---

## Step 3 — Apply structure principles

Always apply `defaults/structure-principles.md`:
- Scannability as the top-level requirement
- Heading test (journey test, position test)
- Element selection (when bullets/tables/prose)
- Encoder/decoder framework (Note vs Article)

---

## Step 4 — Apply anti-slop guidance

Always apply `defaults/anti-slop.md`:
- Universal banned words and patterns
- Per-type human texture
- The master anti-slop instruction

---

## Step 5 — Write

Generate the content following:
1. Form guide (structure, length, what's required)
2. Structure principles (scannability, headings)
3. Anti-slop guidance (voice, texture)
4. Personal style file (if loaded)

**Before showing the draft:** verify against "What to Avoid" in the style file. Fix first, show after.

---

## Step 6 — Quality check

Before presenting:
- Does it scan? (key information visible without reading every word)
- Does it sound human? (no banned words, no AI patterns)
- Does it match the intent? (right type, right audience)
- Does it end when the point is made? (no padding, no summary)

---

## Skill Chaining

**Consumed by:**
- `write-blog` — invokes write-content for content type and writing, adds blog-specific publishing rules
- Future: write-paper, write-post — same pattern (not yet implemented)

**Loads:**
- `write-content/defaults/structure-principles.md` — always
- `write-content/defaults/anti-slop.md` — always
- `write-content/forms/<type>.md` — per content type
- Personal style file from `~/claude-workspace/writing-styles/` — if configured

**See also:**
- `publish-blog` — for publishing after writing
- `write-blog` — for blog-specific workflow
