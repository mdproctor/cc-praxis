---
name: garden
description: >
  Use when non-obvious technical knowledge surfaces — bugs whose symptoms
  mislead about root cause, tools that contradict their documentation, silent
  failures with no error, workarounds found only via multiple failed approaches,
  or behaviour and features that exist but are simply not documented anywhere.
  Also triggered proactively when debugging reveals something a skilled developer
  would find genuinely surprising. NOT for expected errors, how-to content,
  ideas (use idea-log), or project-specific application logic.
---

# Knowledge Garden

A cross-project, machine-wide library of hard-won technical knowledge —
three kinds of entries:

- **Gotchas** — bugs that silently fail, behaviours that contradict
  documentation, and workarounds that took hours to find
- **Techniques** — genuinely novel tricks, approaches, and patterns that
  work in non-obvious ways; things a skilled developer wouldn't naturally
  reach for but would immediately value once shown
- **Undocumented** — behaviours, options, or features that exist and work
  but simply aren't written down anywhere; only discoverable via source
  code, trial and error, or word of mouth

Stored at `~/claude/knowledge-garden/` so any Claude instance on this
machine can read and contribute to it.

**The bar for gotchas:** Would a skilled developer, familiar with the
technology, still have spent significant time on this problem? If yes —
it belongs.

**The bar for techniques:** Would a skilled developer be surprised this
approach exists, or would they have reached for something more complex?
If yes — it belongs.

**The bar for undocumented:** Does it exist, does it work, and would you
have no reasonable way to discover it from the official docs? If yes —
it belongs.

---

## What This Is Not

- **Not an idea log** — ideas go in `idea-log`
- **Not an ADR** — architecture decisions go in `adr`
- **Not how-to content** — step-by-step tutorials for standard documented APIs don't belong; the distinction is *non-obvious* knowledge vs *documented* knowledge
- **Not project-specific** — if it says "in ProjectX, the foo() method..." skip it;
  if it says "JavaParser's getByName() only searches top-level types..." it does
- **Not expected errors** — if it's in the docs with the fix, skip it
- **Not transient issues** — network flakes, temporary rate limits
- **Not general best practices** — "always validate input" isn't a technique; "you can use X to avoid Y in context Z in a way most people don't know about" is
- **Not documented behaviour presented as undocumented** — if it's in the official docs (even buried), it's not undocumented; the bar is genuinely absent from any documentation

---

## Garden Structure

```
~/claude/knowledge-garden/
├── GARDEN.md                   ← dual index (loaded into context, never detail)
├── submissions/                ← incoming entries from any Claude session
│   ├── 2026-04-04-cccli-gcd-dispatch.md
│   └── 2026-04-05-sparge-html-quirk.md
├── macos-native-appkit/
│   └── appkit-panama-ffm.md
├── java-panama-ffm/
│   └── native-image-patterns.md
├── graalvm-native-image/
├── quarkus/
└── <tech-category>/
    └── <topic>.md
```

**`submissions/`** is how all Claude sessions contribute. Submissions are
written without reading the main garden files. A separate MERGE operation
integrates them, handling deduplication with its full context budget.

---

## The Submission Model

**Why submissions instead of direct writes:**

Reading garden files to check for duplicates costs the submitting Claude's
context window — the same window needed for the actual work that surfaced the
knowledge. Worse, the garden grows over time; checking every existing file
before each addition gets more expensive with every entry.

The solution: **write first, deduplicate later.**

- **Submitting Claude** writes a self-contained submission file. Cheap.
  No garden files read unless already in context for another reason.
- **Merging Claude** is a dedicated session whose whole job is reading
  submissions and integrating them. It has full budget for the merge.

**The only exception:** If the submitting Claude already has a garden file in
context (because it searched the garden earlier in the same session, or already
submitted the same entry this session), it should use that existing awareness
to avoid an obvious duplicate — but it must not read garden files *specifically*
to perform the duplicate check.

---

## Submission File Format

```
~/claude/knowledge-garden/submissions/YYYY-MM-DD-<project>-<slug>.md
```

**Gotcha entry** (bug, silent failure, workaround):

```markdown
# Garden Submission

**Date:** YYYY-MM-DD
**Type:** gotcha
**Source project:** project-name (or "cross-project")
**Session context:** One sentence on what was being worked on when this surfaced
**Suggested target:** `<directory>/<file>.md` *(hint for merge Claude; not binding)*

---

## [Short imperative title — describes the weird thing, not the fix]

**Stack:** Technology, Library, Version (be specific)
**Symptom:** What you observe — especially the misleading part. Quote exact
error messages. "No error" is important context.
**Context:** When/where this applies. What setup triggers it.

### What was tried (didn't work)
- tried X — result
- tried Y — result

### Root cause
Why it happens. The underlying mechanism — WHY, not just WHAT.

### Fix
Code block or config. Be complete. Include what NOT to do alongside what works.

### Why this is non-obvious
The insight. What makes this a gotcha? Why would a skilled developer be misled?
```

**Technique entry** (novel approach, non-obvious pattern, clever trick):

```markdown
# Garden Submission

**Date:** YYYY-MM-DD
**Type:** technique
**Source project:** project-name (or "cross-project")
**Session context:** One sentence on what was being worked on when this surfaced
**Suggested target:** `<directory>/<file>.md` *(hint for merge Claude; not binding)*

---

## [Short active title — what you can do, not that it's clever]

**Stack:** Technology, Library, Version (be specific)
**What it achieves:** One sentence — the outcome this technique produces.
**Context:** When/where this applies. What problem it solves.

### The technique
Code block or concrete description. Complete and runnable.

### Why this is non-obvious
What would most developers do instead? Why wouldn't they reach for this?
What's the insight that makes it work?

### When to use it
Conditions where this applies. Any limitations or caveats.
```

**Undocumented entry** (behaviour/feature/option not in official docs):

```markdown
# Garden Submission

**Date:** YYYY-MM-DD
**Type:** undocumented
**Source project:** project-name (or "cross-project")
**Session context:** One sentence on what was being worked on when this surfaced
**Suggested target:** `<directory>/<file>.md` *(hint for merge Claude; not binding)*

---

## [Short title — describes what exists, not that it's undocumented]

**Stack:** Technology, Library, Version (be specific)
**What it is:** One sentence — the feature, behaviour, or option that exists.
**How discovered:** Source code reading / trial and error / someone told me / commit history

### Description
Full description of what this does. Treat it as documentation that doesn't
exist yet. Be precise about conditions, defaults, edge cases.

### How to use it / where it appears
Code block or concrete example. Show it working.

### Why it's not obvious
Why would someone not know this exists? Is it in the source but not the docs?
Only mentioned in a GitHub issue? Only in an old commit message?

### Caveats
Any limitations, version constraints, or risks from relying on undocumented behaviour.
```

The **Suggested target** is a hint to the merge Claude — which garden file this
likely belongs in. The merge Claude decides final placement after checking for
duplicates and related entries.

---

## Workflows

### CAPTURE (write a submission — default operation)

**Step 1 — Quality, type, and project filter**

First, classify the type:
- **gotcha** — something that went wrong in a non-obvious way
- **technique** — a non-obvious approach that worked
- **undocumented** — something that exists and works but isn't in the docs

For gotchas: would a skilled developer have spent significant time on this?
For techniques: would a skilled developer be surprised this approach exists,
or would they have reached for something more complex or less elegant?
For undocumented: does it exist, work, and have no reasonable path to discovery
through official documentation?

Is it cross-project? (Not tied to one specific codebase's logic.)

If uncertain, offer: "Worth adding to the garden? Would go under [category]
as '[short title]' — it's a [gotcha / technique / undocumented]." — confirm before proceeding.

**Step 2 — Duplicate awareness check (context only, no reads)**

Ask: is any garden content already in context from this session?
- Searched the garden earlier → you know what's there; skip obvious duplicates
- Already submitted this entry this session → skip it
- Neither → proceed without reading anything; let the merge handle it

Do NOT run `grep -r` across the garden. Do NOT read garden files. The token
cost is not justified here; the merge Claude handles deduplication.

**Step 3 — Extract the 8 fields from conversation context**

Work from what's already known. Ask only for what's genuinely unclear.

| Field | Extract from |
|-------|-------------|
| Title | The surprising thing itself |
| Stack | Tools, libraries, versions mentioned |
| Symptom | What was observed / error messages |
| Context | When it occurs, what setup triggers it |
| What was tried | Failed approaches in the session |
| Root cause | The diagnosis reached |
| Fix | The working solution with code |
| Why non-obvious | Why the obvious approach failed |

**Step 4 — Determine the suggested target (don't read, just reason)**

Based on the technology stack, suggest the likely destination:

| Technology | Suggested target |
|-----------|-----------------|
| AppKit, WKWebView, NSTextField, GCD | `macos-native-appkit/appkit-panama-ffm.md` |
| Panama FFM, jextract, upcalls | `java-panama-ffm/native-image-patterns.md` |
| GraalVM native image | `graalvm-native-image/<topic>.md` |
| Quarkus | `quarkus/<topic>.md` |
| Git, tmux, Docker, CLI tools | `tools/<tool>.md` |
| Doesn't fit existing | `<new-descriptive-dir>/<topic>.md` |

This is a hint only — the merge Claude decides final placement.

**Step 5 — Draft and confirm**

Draft the submission. Show it to the user:
> "Does this capture it accurately?"

Wait for confirmation before writing.

**Step 6 — Write the submission file**

```bash
mkdir -p ~/claude/knowledge-garden/submissions
# write YYYY-MM-DD-<project>-<slug>.md
```

**Step 7 — Commit**

```bash
cd ~/claude/knowledge-garden
git add submissions/
git commit -m "submit(<project>): '<short title>'"
```

**Step 8 — Report back**

Tell the user the submission file path and that it will be merged into the
garden in the next MERGE session.

---

### MERGE (integrate submissions into the garden)

Run this as a dedicated operation — ideally a session whose primary purpose is
merging, with full context budget available for reading.

**When to run MERGE:**
- User says "merge the garden", "process garden submissions"
- There are several pending submissions (check: `ls ~/claude/knowledge-garden/submissions/`)
- Before a session that will need to search the garden for existing knowledge

**Step 1 — List pending submissions**

```bash
ls ~/claude/knowledge-garden/submissions/
```

**Step 2 — Read each submission** (small, targeted)

Read all submission files. They're compact by design.

**Step 3 — Load GARDEN.md index**

```bash
cat ~/claude/knowledge-garden/GARDEN.md
```

Scan both sections (By Technology, By Symptom Type) for entries similar to
each submission.

**Step 4 — For likely duplicates: surgical read of relevant section**

If a submission looks similar to an existing entry, read only the relevant
section of the relevant file:

```bash
grep -A 30 "## <existing title>" ~/claude/knowledge-garden/<file>.md
```

Don't load entire garden files — read only the sections that might overlap.

**Step 5 — Classify each submission**

For each submission:
- **New** — no matching entry exists; place in garden
- **Duplicate** — identical to an existing entry; discard submission
- **Related** — overlaps with an existing entry; enrich or note the variant

**Step 6 — Integrate new and related entries**

For new entries: append to the appropriate garden file, update GARDEN.md in
both index sections (By Technology + By Symptom Type).

For related entries: add a note under the existing entry, or create a
"Variant" sub-section.

**Step 7 — Remove processed submissions**

```bash
git rm ~/claude/knowledge-garden/submissions/<processed-file>.md
```

**Step 8 — Commit**

```bash
git add .
git commit -m "merge: integrate N submissions — <brief summary>"
```

**Step 9 — Report**

Tell the user how many submissions were merged, how many were duplicates,
how many were related entries, and which garden files were updated.

---

### SEARCH (retrieving entries)

1. Read `GARDEN.md` — check both By Technology and By Symptom Type sections
2. Follow the file link for full detail
3. If not in the index:
   ```bash
   grep -r "keywords" ~/claude/knowledge-garden/ --include="*.md" \
     --exclude-dir=submissions
   ```
4. Return the full entry (Symptom + Root Cause + Fix + Why Non-obvious)
5. If the user just fixed something related, offer to submit the new knowledge

---

### IMPORT (from project-level docs)

When importing from `BUGS-AND-ODDITIES.md` or similar:

1. Read the source document
2. For each entry, classify CROSS-PROJECT or PROJECT-LOCAL
3. Show classifications, ask for confirmation
4. For cross-project entries: write a submission file per entry (CAPTURE flow)
5. Report: N submissions written, M skipped as project-specific
6. Suggest running MERGE when convenient

---

## Proactive Trigger

Fire **without being asked** when:

**For gotchas:**
- Multiple approaches were tried before the fix was found
- The documented approach didn't work
- Something works in one context but silently fails in another
- The fix required knowledge no reasonable developer would find in the docs
- The user says: "that took way too long", "I'd never have guessed that",
  "weird behaviour"

**For techniques:**
- A non-obvious approach was used that solved a problem more elegantly than expected
- Something was discovered that most developers would do the hard way
- A combination of tools or APIs was used in a way the documentation doesn't describe
- The user says: "that's a neat trick", "I didn't know you could do that",
  "this should be documented somewhere", "that's clever"

**For undocumented:**
- A flag, option, or behaviour was found by reading source code, not docs
- Something works but there's no official explanation of why or how
- A feature was discovered through trial and error or a GitHub issue comment
- The user says: "this isn't in the docs", "I only found this in the source",
  "there's no documentation for this", "I had to dig through commits to find it"

Offer, don't assume — and name the type:
> "This was non-obvious — want me to submit it to the garden as a [gotcha /
> technique / undocumented]? Would go under [category] as '[short title]'."

---

## Decision Flow

```mermaid
flowchart TD
    Trigger((Knowledge surfaces))
    IsNonObvious{Skilled developer\nwould be surprised?}
    IsCrossProject{Cross-project?}
    Skip[Skip]
    ContextCheck{Already in context\nfrom this session?}
    SkipDupe[Skip — obvious duplicate\nfrom existing context]
    Extract[Extract 8 fields\nfrom session context]
    Draft[Draft submission,\nshow to user]
    UserApproves{Confirmed?}
    Refine[Refine]
    WriteSubmission[Write to\nsubmissions/YYYY-MM-DD-slug.md]
    Commit[git commit\nsubmit format]
    Report[Report submission path,\nnote: merge when convenient]
    Done((Done))

    Trigger --> IsNonObvious
    IsNonObvious -->|no| Skip
    IsNonObvious -->|yes| IsCrossProject
    IsCrossProject -->|no| Skip
    IsCrossProject -->|yes| ContextCheck
    ContextCheck -->|duplicate already known| SkipDupe
    ContextCheck -->|not a duplicate| Extract
    SkipDupe --> Done
    Extract --> Draft
    Draft --> UserApproves
    UserApproves -->|yes| WriteSubmission
    UserApproves -->|adjust| Refine
    Refine --> Draft
    WriteSubmission --> Commit
    Commit --> Report
    Report --> Done
```

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Reading garden files to check for duplicates during CAPTURE | Burns the submitting Claude's context budget; garden grows, cost grows | Write the submission; let MERGE handle deduplication |
| Skipping the submission and writing directly to garden files | Reintroduces the read-for-dedup problem | Always use submissions/ for new entries |
| Not including "Suggested target" in submission | Merge Claude has to infer from scratch | Include the likely destination as a hint |
| Not including **Type: gotcha / technique / undocumented** in submission | Merge Claude can't categorise correctly | Always declare the type |
| Undocumented: calling it undocumented when it's just buried in docs | Pollutes the undocumented category | Check the docs thoroughly first; the bar is genuinely absent from any documentation |
| Gotcha: title describes the fix not the weird thing | Can't find it by symptom | Title = the surprising behaviour, not the solution |
| Gotcha: fix has no code | Useless in 6 months | Complete, runnable code or config required |
| Gotcha: root cause says WHAT not WHY | Doesn't prevent misdiagnosis | Explain the mechanism, not just the outcome |
| Technique: title says "clever trick to..." | Condescending and unsearchable | Title = what it achieves: "Use X to avoid Y in context Z" |
| Technique: no "why non-obvious" section | Just becomes documentation | Must explain what developers would normally do instead |
| Adding general best practices as techniques | Not garden-worthy — it's well-known advice | The bar is: skilled developer would be surprised this exists |
| Forgetting to run MERGE periodically | Submissions accumulate, garden stays stale | MERGE after 3–5 submissions, or before a search-heavy session |
| Deleting entries when a fix is released | Older versions still need it | Add "Resolved in: vX.Y" note; never delete |

---

## Success Criteria

CAPTURE is complete when:
- ✅ Submission file written to `~/claude/knowledge-garden/submissions/`
- ✅ No garden files were read specifically for duplicate detection
- ✅ User confirmed the draft before writing
- ✅ Committed with `submit(<project>): '<title>'` format

MERGE is complete when:
- ✅ All submissions classified (new / duplicate / related)
- ✅ New entries appended to appropriate garden files
- ✅ GARDEN.md updated in both index sections
- ✅ Processed submissions removed
- ✅ Committed with `merge:` format

SEARCH is complete when:
- ✅ Full entry returned for any matching bugs
- ✅ grep run (excluding submissions/) if topic not in index

**The garden is useful if:** Six months from now, a Claude can find the
relevant entry faster than searching the web or rereading conversation history.

---

## Skill Chaining

**Invoked by:** `superpowers:systematic-debugging` — offered proactively when
a debugging session reveals something non-obvious; user directly ("submit to
the garden", "add this to the garden", "merge garden submissions")

**Invokes:** Nothing — handles its own git commits to `~/claude/knowledge-garden/`

**Reads from:**
- `~/claude/knowledge-garden/GARDEN.md` — for SEARCH and MERGE only
- `~/claude/knowledge-garden/submissions/` — for MERGE only
- Garden detail files — MERGE only, surgical section reads

**Complements:** `idea-log`, `adr`, `write-blog` — the garden holds
reusable cross-project technical gotchas none of those capture
