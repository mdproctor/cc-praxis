# 0011 — Revert subtype taxonomy value from 'log' back to 'diary'

Date: 2026-05-22
Status: Accepted

## Context and Problem Statement

The `note` entry subtype was renamed from `diary` to `log` in issue #95 for naming
consistency. The rename was partially applied across skill files and ~20 blog posts
before the word choice was reconsidered. "Log" implies dry, chronological, technical
records — the opposite of what write-blog produces: personal, in-the-moment, narrative
project writing. The mismatch created tension between the taxonomy value and all
descriptive language in the skills ("diary voice", "living diary"), making it
impossible to align them without corrupting either the taxonomy or the writing
philosophy.

## Decision Drivers

* The English word for the taxonomy value must match the actual character of the content
* "Diary voice" is a precise description of write-blog's output — changing it to "log voice" would be semantically wrong
* Descriptive language in skills should reinforce, not fight, the taxonomy

## Considered Options

* **Option A** — Keep `log`, update all descriptive language to match ("log voice", "living log")
* **Option B** — Revert to `diary`, update the ~20 files already changed to `log`
* **Option C** — Keep the split: `log` in machine-readable taxonomy, `diary` in user-facing language

## Decision Outcome

Chosen option: **Option B** — revert to `diary`, because "diary" is the correct English
word for personal narrative writing, and the rename was a mistake in word choice.
Option A would corrupt the skill's own philosophy (it explicitly says "don't write
like a technical log"). Option C is managed drift, not a solution.

### Positive Consequences

* All language — taxonomy, triggers, descriptions, "diary voice" — is consistent
* No split to document or explain to future sessions
* The skill's writing philosophy and the taxonomy value reinforce each other

### Negative Consequences / Tradeoffs

* Reverting required updating ~121 frontmatter files across 7 repos and 4 skill files
* A permanent idempotent cleanup script (`scripts/revert_diary_subtype.py`) is needed
  during the eventual-consistency period while active sessions pick up the corrected skills

## Pros and Cons of the Options

### Option A — Keep 'log', align descriptive language

* ✅ No frontmatter revert required
* ❌ "Log voice" is wrong for personal narrative writing — the skill explicitly forbids dry, retrospective prose
* ❌ Corrupts the write-blog philosophy to serve a naming convention

### Option B — Revert to 'diary'

* ✅ Correct English word for the content character
* ✅ Zero tension between taxonomy and descriptive language
* ❌ ~121 files needed reverting (handled by cleanup script)
* ❌ Eventual consistency period needed while running sessions catch up

### Option C — Split: 'log' in taxonomy, 'diary' in prose

* ✅ No frontmatter revert
* ❌ Creates permanent drift between taxonomy and language — next session will be confused
* ❌ Requires explicit documentation of the intentional split

## Links

* Issue #96 — sweep and revert
* Spec: `docs/superpowers/specs/2026-05-22-diary-to-log-sweep-design.md`
* Protocol PP-20260522-6e976f — taxonomy values reflect content character
* Supersedes decision made in issue #95 (partial — only the subtype rename portion)
