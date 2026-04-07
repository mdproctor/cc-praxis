# cc-praxis — Teaching the Skills to Write About Themselves

**Date:** 2026-04-06
**Type:** phase-update

---

## What we were trying to achieve: a skill that could write its own history

The project had accumulated forty-plus skills for code review, commits, dependency updates, health checks. What it didn't have was a proper skill for writing about itself.

`project-blog` existed — it was how the five entries in `docs/blog/` got written. But the name was wrong, the skill was thin, and it had no way to look back at everything that had happened and propose a retrospective series from the git history.

The goal: fix all of that. And while we were there, tighten everything that supports good writing — the style guide, the session handoff, the garden.

## What we believed going in: mostly contained, one skill to update

I thought this would be a few targeted changes. Rename `project-blog` to `write-blog`, add a retrospective mode, make the command intent-driven. Maybe an hour.

The style guide had been updated in the previous session — two Claude instances had each contributed to it. I believed that work was done.

I was wrong about the second part.

## The writing layer took shape — and a different Claude caught what I missed

### write-blog: one command, two modes

The rename clarified the pipeline: `write-blog` is the writing step, `publish-blog` is the delivery step. Whatever platform entries eventually get published to, only `publish-blog` needs to change.

RETROSPECTIVE mode scans git history, groups commits into candidate phases, and presents a numbered `[x]` selection list — all ticked by default. The user types numbers to deselect or presses Enter to write all. Each entry goes through the full workflow: propose → confirm → write → commit. The style guide loads once and applies to all entries.

The command itself became intent-driven. `/write-blog` with no argument triggers the retrospective sweep. With context — `/write-blog the web installer phase` — it proposes a single entry from that starting point, asks for framing confirmation, then drafts.

### The style guide gap a different Claude found

A separate Claude had been working on writing style guidance in another session. It had added dual heading patterns, thematic heading principles, a heading smell check, and a revision protocol.

When that Claude reviewed the committed file, it said the additions weren't there. I disagreed — I'd read the git log and seen commit messages with plausible-sounding names. I reported the work as done.

Claude read the actual file. The sections were absent.

Commit messages describe intent. They aren't proof of content. Once I read the file myself, it was obvious — two specific sections were missing: a "Common register mistakes" subsection naming the editorial "we" failure modes and third-person protagonist patterns, and a voice-register audit step in the revision checklist. Both went in.

The write-blog skill itself was also misaligned with the style guide — the entry template still had bare structural slots, and `**Next:**` was listed as a pitfall to do better rather than one to avoid entirely. A systematic review found nine issues: two contradictions, four inconsistencies, three minor cleanups.

### session-handoff: wrap first, then hand over

A handoff is the natural time to do a full session wrap — write a blog entry, take a design snapshot, sync CLAUDE.md, sweep the garden. We added a checklist at the start of the handoff:

```
[x] 1  write-blog       capture this session's work as a diary entry
[x] 2  design-snapshot  freeze the current design state
[x] 3  update-claude-md sync any new workflow conventions
[x] 4  garden sweep     check for gotchas, techniques, undocumented
```

All on by default. Type numbers to toggle, "all" to flip everything.

The order matters and wasn't obvious. I initially proposed garden → blog → snapshot → CLAUDE.md. That's wrong. The correct order is determined by information flow: garden first while context is full, CLAUDE.md sync next so conventions are current, design-snapshot after so it reflects fresh conventions, write-blog last so it can reference the snapshot path, mention garden submissions, and synthesise everything. The artifact with the richest synthesis potential belongs at the end.

### garden: structured scoring instead of binary judgment

The garden had a recurring problem: a Claude would surface something potentially worthy and ask "is this worth adding?" I often didn't know.

We added a scoring system. Five dimensions rated 1–3 each: non-obviousness, discoverability, breadth, pain/impact, longevity. Submissions now carry an explicit "case for" and "case against". During SWEEP, the score is computed and shown at proposal time — before confirmation — so the decision is informed rather than gut feel.

The score survives into the garden file after merging: `*Score: 11/15 · Included because: ... · Reservation: ...*`. Future pruning sessions can read it.

### sync-local: the dev skill that shouldn't be in the marketplace

`python3 scripts/claude-skill sync-local --all -y` was always a bash command with no slash equivalent. That's now `/sync-local`.

The interesting part is the pattern it established. Some skills only make sense in a cloned repository — marketplace users don't have `scripts/claude-skill`. The solution: create the skill normally, exclude it from `marketplace.json`, don't mention it in README, mark it DEV-ONLY prominently. The web installer only surfaces skills in `marketplace.json`, so it stays invisible to marketplace users. CLAUDE.md now documents this as a reusable pattern with a checklist for the next dev-only skill.

## What it is now

The collection can write about itself. RETROSPECTIVE mode means a new Claude instance can open a project with git history but no blog entries, run `/write-blog`, and get a proposed series covering the whole journey.

The writing infrastructure is the part of cc-praxis I didn't anticipate needing. It turned out to be as much work as any other phase — and probably the part that ages best.
