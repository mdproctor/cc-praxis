# Diary Form Guide

A living diary of a project as it evolves — written in the moment, not in
hindsight. Each entry captures what the developer believed and intended at
that point, including aspirations that later changed, approaches that were
rejected, and pivots that happened mid-build.

Entries are written in the author's personal voice from the first draft.
They are intended to be published once a phase or project reaches a natural
point. The raw honesty is the value: readers see how decisions actually get
made, not a sanitised retrospective.

The `publish-blog` skill handles restructuring for publication when entries
are ready — front matter, platform formatting, final polish.

---

## What This Is Not

- **Not a design snapshot** — Snapshots are formal and capture full design state. The diary is informal, written phase by phase.
- **Not an ADR** — ADRs record one decision formally. The diary narrates the story including everything considered and rejected.
- **Not the idea log** — The idea log parks undecided possibilities. The diary records what happened and why.
- **Not a retrospective** — Never written after the fact. If a belief was wrong, a new entry corrects it — the old entry is never revised.
- **Not a technical spec** — Diary voice only.
- **Not a finished article** — `publish-blog` restructures entries for publication. Voice and style are consistent; formatting differs.
- **Not a session log** — a pure sequence of actions (ran X, found Y, fixed Z) with no decision, observation, reflection, or insight attached. If nothing surprised you, changed your understanding, or is worth reading independently of what the commits record, don't write the entry.

---

## Voice and Perspective Rules

The **complete and authoritative register rules** are in
`write-content/voice/mandatory-rules.md` — loaded as part of Step 4 (draft).

**The rule in brief:** "I" for what I thought, believed, wanted, or decided.
"we" for what we actually built, tried, found, or fixed together with Claude.
Never third-person for the developer.

---

## Tone Calibration by Phase

Match tone to the phase — see **[diary-template.md](diary-template.md)** for the full table and signs the tone is wrong.

---

## Entry Types

| Type | When to use |
|------|------------|
| **Day Zero** | Before any work begins — initial vision, first approach, known unknowns |
| **Phase Update** | At a natural milestone — phase completed, significant work done |
| **Pivot** | When direction changes — what was considered, rejected, what forced the change |
| **Correction** | When something believed in an earlier entry proves wrong — honest about it, never edits the original |
| **Retrospective** | Covering all work to date in one pass — scans git history, proposes phases, confirms selection, writes in sequence |

---

## File Location

```
<BLOG_DIR>/YYYY-MM-DD-<initials>NN-phase-title.md
```

`<BLOG_DIR>` resolved in Step 0 below. Default: `blog/`.

One file per entry. `<initials>` is the author's 2–4 letter identifier, read
from `~/.claude/settings.json` § `initials`. `NN` is a two-digit per-author
sequence number starting at `01`. Kebab-case title, ≤30 chars.

Previous entries are never edited — new entries reference them if needed.

---

## Entry Template

Full template and heading guidance: **[diary-template.md](diary-template.md)**

---

## What Makes an Entry Credible

**Include:**
- Specific error messages verbatim
- Exact file paths
- What was tried before the fix, and why each attempt failed
- Numbers: "48 false positives," "17 validators," "six days"
- Code blocks for the interesting parts
- The moment something surprised you
- Screenshots for any UI work — **mandatory**; clip to the relevant area
- A closing insight, if the work genuinely surfaces one (see below)

**Avoid:**
- Smooth narratives with no failed attempts
- "We decided to use X" without saying what else was considered
- Vague future commitment: "we'll address this later"
- Describing a UI without showing it
- Forcing a closing insight when there's nothing genuine to say

---

## Closing insight — optional, not a section

After the main narrative, if the work surfaces something worth thinking about,
include 1–3 sentences woven into the closing prose. **Not a headed section.
Not a task list. Only when there's something genuine.**

Use these forms as the filter — if what you'd write doesn't fit one, leave it out:

1. **What it might lead to** — a direction the work opens that isn't obvious from the commits
2. **An insight the reader might not be aware of** — a non-obvious implication or cross-project connection
3. **Related things worth looking into** — a pointer to something adjacent the work illuminates
4. **This looks similar to what we did elsewhere** — pattern recognition across sessions or projects
5. **We made a decision here without realising it** — an implicit architectural choice worth naming so it can be consciously owned
6. **The reason this works is non-obvious** — explains WHY something works when it doesn't look like it should; useful for anyone tempted to simplify it later
7. **We're drifting toward X without having decided to** — names an emergent direction that hasn't been articulated as a goal yet
8. **The risk here is...** — a non-obvious failure mode not visible from the code

**Examples of the right texture:**

> *"The ctx.py pattern probably has further to run — there's a whole class of shell operations in the remaining skills that are one permission check away from the same problem."*

> *"Between ctx.py, stack.py, and discover-repos.py, project-init is quietly becoming a Python runtime for the whole skill ecosystem. That's a meaningfully different thing than it started as."*

> *"Fixing work-pause surfaces a broader question: how many of the lifecycle commands have implicit ordering assumptions that aren't enforced anywhere?"*

The test: would a developer reading this entry think "I hadn't considered that" or "that's worth knowing"? If yes, include it. If it reads like scaffolding or obligation, cut it.

---

## Visual Elements

Three kinds: code blocks, illustrations, screenshots (mandatory for UI work).

Full rules: **[diary-visual-elements.md](diary-visual-elements.md)**

---

## Diary Workflow

### Step 0 — Orientation

**Resolve blog directory** (first match wins):

1. **`~/.claude/blog-routing.yaml`** — derive `<BLOG_DIR>` from routing config
2. **`Blog directory:` in CLAUDE.md** — explicit path override
3. **`## Routing` table in CLAUDE.md** — `blog → workspace` or `blog → project`
4. **Default**: `blog/` relative to CWD

Resolve to an **absolute path**.

**Scan CLAUDE.md** for audience and topics:
```bash
cat CLAUDE.md 2>/dev/null | head -80
```

**Resolve canonical project name:**

Read the `**Name:**` field from the loaded CLAUDE.md. Then look it up in `~/.claude/project-names.yaml`:

```python
import yaml, re
from pathlib import Path

registry_path = Path.home() / ".claude" / "project-names.yaml"
raw_name = "<value from **Name:** field>"

if registry_path.exists():
    registry = yaml.safe_load(registry_path.read_text())
    canonical = (registry.get("aliases", {}).get(raw_name)
                 or registry.get("canonical", {}).get(raw_name))
    if canonical:
        project_label = canonical
    else:
        # Not in registry — use raw name but warn
        project_label = raw_name
        print(f"⚠️  Project name '{raw_name}' not in ~/.claude/project-names.yaml — using as-is. Add it to prevent label drift.")
else:
    project_label = raw_name
```

Use `project_label` (not `raw_name`) as the value in `projects: [<project_label>]` frontmatter.

**Load voice (one of two, never both):**

```bash
echo "$PERSONAL_WRITING_STYLES_PATH"
```

If set → list `.md` files there, select the blog/diary style guide, read in full.  
If not set → load `write-content/voice/common-voice.md`.

**Resolve author initials:**

```bash
python3 -c "import json; d=json.load(open('$HOME/.claude/settings.json')); print(d.get('initials',''))" 2>/dev/null
```

If not set → prompt once and save to `~/.claude/settings.json`.

**Determine mode:**

- **No argument** → load [diary-retrospective.md](diary-retrospective.md) and follow that workflow. Skip Steps 1–7 below.
- **With context** → propose entry type before asking anything, then continue with Step 1.

**Check for prior entries in this series:**

If a workspace `.meta` file exists (mid-branch session), read the branch name:
```bash
grep "^branch:" <WORKSPACE>/design/.meta 2>/dev/null
```

Use the branch name as the series key. Scan `<BLOG_DIR>/` for entries with matching `series:` frontmatter:
```bash
grep -rl "^series:.*<branch-name>" <BLOG_DIR>/ 2>/dev/null | sort
```

If prior entries exist: note their filenames and titles. They will be referenced in the new entry's opening (Step 4) and included in the frontmatter `series:` field (Step 6). If no prior entries and no `.meta`: this is a standalone entry — omit `series:` from frontmatter.

**Ensure CLAUDE.md has style guide pointer** (gate, not offer):

```bash
grep -l "blog-technical\|writing style guide" CLAUDE.md 2>/dev/null
```

If missing: propose adding the Writing Style Guide section via `update-claude-md`, get confirmation, apply, then proceed.

---

### Step 1 — Confirm entry type and voice

Ask or infer:

```
Article or note?
  [A] Article — topic-driven, standalone
  [N] Note / diary — session narrative  (default: N)

Projects: [<name from CLAUDE.md>]
Tags (optional):
```

Set frontmatter: `entry_type: article|note`, `subtype: diary` (for notes), `projects: [...]`.

If invoked with context, the type was already proposed — confirm or adjust, don't ask again.

Infer type from context: first entry → Day Zero; milestone → Phase Update; direction change → Pivot; belief wrong → Correction.

---

### Step 2 — Check existing entries

```bash
ls <BLOG_DIR>/ 2>/dev/null | sort
```

For all types except Day Zero: read the most recent entry to understand where the project left off.  
For Correction: identify which entry is being corrected. Never edit the original.

---

### Step 3 — Gather the story

**Entry worthiness check — before gathering anything:**

Does this session contain at least one of:
- A decision and its reasoning (software, process, methodology, or other)
- An observation or discovery about how something works
- A conceptual or theoretical exploration
- An industry reflection or opinion
- A future idea beginning to crystallise
- Anything that would be worth reading independently of the action sequence

If the session was a pure action sequence — tasks completed, branches closed, commits landed, cleanup done — with none of the above: **do not write this entry.** Ask first: does the insight actually belong in a different project's diary (e.g. methodology work → cc-praxis diary, tooling discovery → garden entry)?

If worthiness is confirmed, extract from conversation context. Only ask for what's genuinely unclear:
- What was the goal?
- What was believed going in?
- What was built/tried/found? What failed before the fix?
- What changed direction, if anything?

---

### Step 4 — Draft with correct voice, tone, and style

**Gate — do not draft until both parts complete:**

**Part A:** Read `write-content/voice/mandatory-rules.md` in full. Cannot be overridden.
Load `write-content/mandatory-gates.md` — the pre-draft gate (voice classification, factual accuracy, style guide check) applies here.

**Part B — Pre-draft classification:**
1. Is Claude a participant? Identify "I" vs "we" vs "Claude [verb]" for each section.
2. Which moments are Claude-naming moments?
3. Tone check: which entry type? What does the tone calibration table say?

Draft only after this classification.

**After drafting:** go through the style guide's "What to Avoid" line by line. Fix before showing. Do not show a failing draft.

Present the full draft. **Do NOT write to disk until the user confirms.**

---

### Step 5 — Confirm

> Here is the draft entry. Review it carefully — once committed, it is
> immutable (corrections go in a new entry, not an edit).
>
> [draft content]
>
> Confirm to write? **(YES / adjust)**

---

### Step 6 — Write to disk

```bash
ls <BLOG_DIR>/YYYY-MM-DD-<initials>*.md 2>/dev/null | wc -l  # count same-day entries
# NN = count + 1, zero-padded
```

File name: `YYYY-MM-DD-<initials>NN-<kebab-case-title>.md`

Frontmatter:
```yaml
---
layout: post
title: "<title>"
date: YYYY-MM-DD
type: <day-zero|phase-update|pivot|correction>   # omit for articles
entry_type: <article|note>
subtype: diary                                     # omit for articles
projects: [<project>, ...]
tags: [<tag>, ...]                               # omit if empty
series: <branch-name>                            # omit if no prior entries in this series
---
```

**If `series:` is set and prior entries exist**, open the entry body with a brief continuity note before any other content:

```markdown
*Part of a series on [#<issue> — <issue title>](<link-to-issue>). Previous: [<prior-entry-title>](<filename>).*
```

Keep it to one line — it's a navigation aid, not an introduction. Omit if this is the first entry in the series (no prior entries found in Step 0).

After writing, update `<BLOG_DIR>/INDEX.md` (create if absent):
```markdown
| [YYYY-MM-DD-initialsNN-title.md](...) | YYYY-MM-DD | <one-line summary> |
```

---

### Step 7 — Offer related actions

1. Significant decision? → offer `adr`
2. Major milestone? → offer `design-snapshot`
3. Commit via `git-commit`:
   ```
   docs: add project blog entry YYYY-MM-DD-<title>
   ```

---

## Retrospective Workflow

See [diary-retrospective.md](diary-retrospective.md) — loaded when invoked with no argument.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Using third-person for the developer | Creates distance; this is their diary | Change to "I" |
| "we" for everything including solo thinking | Dilutes the collaboration signal | "I" for internal thinking; "we" for actual collaboration |
| Writing in past tense throughout | Sounds retrospective, not diary | Mix present-tense thinking: "I believed," "the question is" |
| Smooth narrative with no failed attempts | Value is in the iteration | Include what was tried first, specifically why it failed |
| Vague errors: "X didn't work" | Useless to future readers | Include exact error messages, commands, file paths |
| Editing an earlier entry when beliefs change | Destroys the historical record | Write a Correction entry instead |
| Using a "Next:" footer | Sounds like scaffolding | Integrate forward-looking note naturally, or end on the last real point |
| Forcing a closing insight | Reads as obligation, not thought | Only include if it passes one of the eight forms — otherwise end on the last real point |

---

## Before Committing

Run the five checks in **[diary-heading-checks.md](diary-heading-checks.md)**.

---

## Success Criteria

- ✅ File at `<BLOG_DIR>/YYYY-MM-DD-<initials>NN-<title>.md`
- ✅ `entry_type` in frontmatter
- ✅ `projects` non-empty in frontmatter
- ✅ `subtype: diary` for note entries; omitted for articles
- ✅ Voice correct: "I" for developer perspective, "we" for collaboration, no third-person protagonist
- ✅ Headings thematic — none replaced with bare structural slots
- ✅ Specific details: error messages, file paths, failed attempts documented
- ✅ Code blocks present where implementation detail is the story
- ✅ UI work: at least one clipped screenshot in `blog/images/`
- ✅ User confirmed before writing
- ✅ Committed to git
