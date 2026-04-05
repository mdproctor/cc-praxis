---
name: session-handoff
description: >
  Use when ending a session and wanting to preserve context for resumption —
  says "create a handoff", "end of session", "update the handover", or
  "write a handoff". Generates a concise HANDOVER.md with lazy references
  to deeper context, not the context itself. NOT for design records (use
  design-snapshot) or project narrative (use write-blog).
---

# Session Handoff

Generates a concise `HANDOVER.md` — a pointer document that gives the next
Claude session enough context to resume immediately. References are read on
demand; the handover itself stays small. Git history is the archive.

**Token budget:** HANDOVER.md should be readable in under 500 tokens. If it's
longer, trim — it has become a document, not a handover.

---

## What This Is Not

- **Not a design snapshot** — design-snapshot freezes design state as an
  immutable archival record. The handover is operational, mutable, overwritten
  each session.
- **Not a project blog entry** — the blog captures narrative for posterity.
  The handover captures operational context for the next 24–48 hours.
- **Not a knowledge-garden entry** — cross-project technical gotchas go in
  the garden. Session-specific context goes in the handover.
- **Not a replacement for CLAUDE.md** — CLAUDE.md is already auto-loaded
  and covers permanent conventions. Don't duplicate it here.

---

## Core Principles

### 1. Write only deltas — reference the rest

If something hasn't changed since the previous handover, **don't restate it**.
Write `*Unchanged — retrieve with: `git show HEAD~1:HANDOVER.md`*` for that
section and move on. Only sections that actually changed get written in full.

This keeps the current handover minimal. The git history holds everything else.

### 2. Git history is the archive

HANDOVER.md is a single file, overwritten each session and **always committed**.
Previous versions are free — they live in git. No separate archive directory
needed.

```bash
# How many handovers exist?
git log --oneline -- HANDOVER.md

# When was the last one written?
git log -1 --format="%ar" -- HANDOVER.md

# Read the previous handover (whole file)
git show HEAD~1:HANDOVER.md

# What changed between the last two handovers?
git diff HEAD~1 HEAD -- HANDOVER.md

# Read just one section of a previous handover (surgical)
git show HEAD~1:HANDOVER.md | grep -A 10 "## Open Questions"

# Find a handover from a specific date
git log --before="2026-04-03" -1 --format="%H" -- HANDOVER.md \
  | xargs -I{} git show {}:HANDOVER.md
```

These commands are cheap — use them rather than loading full files when only
part of the historical context is needed.

### 3. Commit is required, not optional

An uncommitted HANDOVER.md is invisible to git history — the archive doesn't
exist. Always commit. No exceptions.

### 4. Freshness check before reading

When starting a session, check how old the handover is before loading it:

```bash
git log -1 --format="%ar" -- HANDOVER.md   # → "3 days ago"
```

If it's more than a week old, flag it before using the context:
> "HANDOVER.md is 9 days old — some context may be stale. Verify key
> assumptions before building on it."

The next session can then choose to load a more recent intermediate handover
from git history if one exists.

### 5. Read nothing just to reference it

If a file is already in context from this session, summarise from memory.
If it isn't, write the path — the next session reads it only if the task
requires it. This is the knowledge-garden GARDEN.md approach applied to
session continuity.

---

## Workflow

### Step 1 — Check previous handover (cheap)

```bash
git log --oneline -3 -- HANDOVER.md
```

If a previous handover exists, get the diff to know what changed:

```bash
git diff HEAD -- HANDOVER.md 2>/dev/null || git show HEAD:HANDOVER.md 2>/dev/null
```

This tells you what sections are unchanged — don't rewrite those. Work from
the diff, not from loading the full previous file.

### Step 2 — Recall from context (free)

From the current session, recall:
- What changed from the last handover? (only write these)
- What decisions were made? What was tried and didn't work?
- What's blocking or uncertain?
- What's the single most important next action?

Do NOT read any project files to answer these. Work from conversation memory.

### Step 2b — Garden sweep (while context is still full)

This is the optimal moment to capture garden entries — the session is
fully in context and hasn't been discarded yet. Sweep all three categories:

**Gotchas** — anything that went wrong in a non-obvious way?
- Bugs whose symptom misled about root cause
- Silent failures with no error
- Things that required multiple failed attempts before the fix
- Workarounds for things that "should" work

**Techniques** — any non-obvious approaches that worked well?
- Solutions a skilled developer wouldn't naturally reach for
- Combinations of tools or APIs used in undocumented ways
- Patterns that solved a problem more elegantly than expected

**Undocumented** — anything discovered that isn't in the official docs?
- Flags, options, or behaviours only findable via source code
- Features that work but have no documentation
- Things only discoverable through trial and error or commit history

For each category, ask: *"Is there anything from this session worth
submitting to the garden?"* If yes — invoke the `garden` skill to write
a submission before continuing. If nothing surfaces, proceed.

> **Why here:** The context window is full. After the handover is written
> and the session ends, this knowledge is lost. A 2-minute sweep now
> preserves knowledge that would otherwise require rediscovery.

The garden sweep is **always done** (even if it finds nothing) — the
cost of checking is near-zero from context; the cost of missing an entry
is rediscovery time in a future session.

### Step 3 — Gather cheap orientation

```bash
git log --oneline -6        # recent commits
git status --short          # any uncommitted state
```

### Step 4 — Build the references table (locate, don't read)

```bash
ls docs/design-snapshots/ | sort | tail -1   # latest snapshot path
ls docs/write-blog/ | sort | tail -1       # latest blog entry path
ls docs/adr/ | sort | tail -3                # recent ADRs
```

Run `ls` only — do not open the files. CLAUDE.md is auto-loaded; omit it.

### Step 5 — Write HANDOVER.md (delta-first)

For each section: has it changed since last handover?
- **Changed** → write it in full
- **Unchanged** → write `*Unchanged — `git show HEAD~1:HANDOVER.md`*`
- **Doesn't exist yet** (first handover) → write all sections in full

Overwrite the previous HANDOVER.md completely.

### Step 6 — Commit (required)

```bash
git add HANDOVER.md
git commit -m "docs: session handover YYYY-MM-DD"
```

Committing is mandatory. It's what makes git history the archive.

---

## HANDOVER.md Template

```markdown
# Handover — YYYY-MM-DD

**Head commit:** `<hash>` — <subject line>
**Previous handover:** `git show HEAD~1:HANDOVER.md` | diff: `git diff HEAD~1 HEAD -- HANDOVER.md`

## What Changed This Session

- <only things that changed — not a general summary>
- <if nothing changed in a section, say so and skip it>

## State Right Now

<Write only if changed from previous handover.>
<If unchanged: *Unchanged — `git show HEAD~1:HANDOVER.md`*>

## Immediate Next Step

<Always write this explicitly — it changes every session.>
<Be specific: not "continue work" but "run X and update section Y".>

## Open Questions / Blockers

<Write only if changed. If unchanged: *Unchanged — see previous handover.*>

## References

Read only what the task requires. Use git show / grep for surgical reads.

| Context | Where | Retrieve with |
|---------|-------|---------------|
| Design state | `docs/design-snapshots/<latest>.md` | `cat` that file |
| Project narrative | `docs/write-blog/<latest>.md` | `cat` that file |
| Technical gotchas | `~/claude/knowledge-garden/GARDEN.md` | index only; detail on demand |
| Open ideas | `docs/ideas/IDEAS.md` | `cat` that file |
| Previous handover | git history | `git show HEAD~1:HANDOVER.md` |
| Specific section of prev | git history | `git show HEAD~1:HANDOVER.md \| grep -A 10 "## Section"` |

## Environment

<Only if non-obvious and changed since CLAUDE.md. Omit if nothing unusual.>
```

---

## Surgical git Reads for the Next Session

When the next session needs context from a previous handover, use targeted
git commands rather than loading the whole file:

```bash
# Just the "Open Questions" section from two sessions ago
git show HEAD~2:HANDOVER.md | grep -A 15 "## Open Questions"

# What the "State Right Now" section said last week
git log --before="7 days ago" -1 --format="%H" -- HANDOVER.md \
  | xargs -I{} git show {}:HANDOVER.md | grep -A 10 "## State"

# Did anything change in the References table between sessions?
git diff HEAD~1 HEAD -- HANDOVER.md | grep "^[+-]" | grep "References" -A 20
```

The principle: prefer `grep -A N` over reading entire files. Git diffs show
only changed lines. Section reads are cheaper than full-file reads.

---

## When to Load a Previous Handover

Load `git show HEAD~1:HANDOVER.md` when:
- The current handover marks several sections as "Unchanged" and the task
  requires that context — retrieve only the relevant section
- The current handover is stale (>7 days) and an intermediate one might
  have more recent state

Do NOT preemptively load previous handovers at session start. Check freshness
first; load only when a specific task demands the missing context.

---

## What Goes in HANDOVER.md vs Other Files

| Information | Where it belongs |
|-------------|-----------------|
| What changed this session | HANDOVER.md — write in full |
| What didn't change this session | HANDOVER.md — reference previous via git |
| Why a design decision was made | write-blog or adr |
| Current architecture | design-snapshot (reference from handover) |
| Cross-project technical gotcha | garden (reference from handover) |
| Undecided possibilities | idea-log (reference from handover) |
| Permanent conventions | CLAUDE.md (auto-loaded, don't repeat) |

---

## Decision Flow

```mermaid
flowchart TD
    Trigger((Session ending))
    CheckHistory[git log --oneline -3\n-- HANDOVER.md]
    HasPrevious{Previous\nhandover exists?}
    GetDiff[git diff HEAD -- HANDOVER.md\nidentify unchanged sections]
    Recall[Recall from context:\nwhat changed, decisions,\nnext step — zero cost]
    GardenSweep[Garden sweep:\ncheck gotchas / techniques /\nundocumented — all 3 categories]
    GardenFound{Anything\nworth submitting?}
    SubmitGarden[Invoke garden skill\nto write submission]
    GitStatus[git log --oneline -6\ngit status --short]
    BuildRefs[ls to locate file paths\ndo not open files]
    Draft[Write HANDOVER.md:\nchanged sections in full,\nunchanged sections as references]
    TokenCheck{Over 500 tokens?}
    Trim[Mark more sections\nas unchanged references]
    Confirm[Show to user]
    UserApproves{Approved?}
    Refine[Adjust]
    Write[Write HANDOVER.md]
    Commit[git add HANDOVER.md\ngit commit — required]
    Done((Done))

    Trigger --> CheckHistory
    CheckHistory --> HasPrevious
    HasPrevious -->|yes| GetDiff
    HasPrevious -->|no| Recall
    GetDiff --> Recall
    Recall --> GardenSweep
    GardenSweep --> GardenFound
    GardenFound -->|yes| SubmitGarden
    GardenFound -->|no| GitStatus
    SubmitGarden --> GitStatus
    GitStatus --> BuildRefs
    BuildRefs --> Draft
    Draft --> TokenCheck
    TokenCheck -->|yes| Trim
    Trim --> Draft
    TokenCheck -->|no| Confirm
    Confirm --> UserApproves
    UserApproves -->|yes| Write
    UserApproves -->|adjust| Refine
    Refine --> Draft
    Write --> Commit
    Commit --> Done
```

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Restating unchanged context verbatim | Wastes tokens; the previous handover already has it | Write `*Unchanged — git show HEAD~1:HANDOVER.md*` |
| Skipping the commit | Makes git history useless as an archive | Commit is mandatory, not optional |
| Loading previous handover to check what's unchanged | Wastes tokens; use `git diff` instead | `git diff HEAD -- HANDOVER.md` shows only what changed |
| Loading GARDEN.md detail files | Index is enough; details load on demand | Always reference GARDEN.md (index), never sub-files |
| Copying CLAUDE.md content | Auto-loaded; pure duplication | Omit entirely |
| Skipping the freshness check | Old handover misleads the next session | `git log -1 --format="%ar" -- HANDOVER.md` before using |
| Writing "continue work" as next step | Too vague to act on | Be specific — name the file, command, or section |

---

## Success Criteria

Handover is complete when:

- ✅ Garden sweep performed — all three categories checked (gotchas, techniques, undocumented)
- ✅ Any garden-worthy entries submitted before writing the handover
- ✅ HANDOVER.md exists at project root
- ✅ Readable in under 500 tokens
- ✅ Unchanged sections reference git history, not repeated content
- ✅ Immediate next step is specific enough to act on without asking
- ✅ References table uses paths only — no file content inline
- ✅ Nothing from CLAUDE.md is duplicated
- ✅ User confirmed before writing
- ✅ Committed to git (required — this is the archive mechanism)

**The test:** Could a fresh Claude reading only CLAUDE.md and HANDOVER.md
pick up the work in the next message, with git history available for any
context marked as "unchanged"? If yes — done.

---

## Skill Chaining

**Invoked by:** User directly at end of a session ("create a handover",
"end of session", "write a handoff")

**Invokes:** [`garden`] — during the garden sweep (Step 2b) to submit any gotchas, techniques, or undocumented items before context is lost; `git commit` directly for the handover itself

**Reads from (surgical, not upfront):**
- `git diff HEAD -- HANDOVER.md` — what changed from last handover
- `git log --oneline -6` — recent commits for orientation
- `ls` on docs/ directories — locate paths without reading files
- `~/claude/knowledge-garden/GARDEN.md` — only when including garden reference

**Complements:**
- `design-snapshot` — archival design state the handover points to
- `write-blog` — narrative context the handover points to
- `garden` — technical gotcha index the handover references
- `idea-log` — undecided possibilities the handover references

**Does NOT replace:** CLAUDE.md (auto-loaded), `--resume`/`--continue` flags
(restore conversation history for same-machine continuation)
