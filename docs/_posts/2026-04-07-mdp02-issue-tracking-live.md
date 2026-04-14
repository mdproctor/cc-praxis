---
layout: post
title: "cc-praxis — The Gap We Found While Testing What We Built"
date: 2026-04-07
type: phase-update
entry_type: note
subtype: diary
projects: ["cc-praxis"]
---
# cc-praxis — The Gap We Found While Testing What We Built

**Date:** 2026-04-07
**Type:** phase-update

---

## What I wanted: a real test of the Work Tracking feature I'd shipped

The handover from the last session said to test Work Tracking in a real
commit on a project without it configured. Pick remotecc or starcraft,
make a commit, see if the Step 0b prompt fires. I'd also decided to
bootstrap issue tracking for cc-praxis itself first — it had Work Tracking
enabled but zero issues. Both felt like quick tasks.

They weren't.

## What I believed going in: Step 0b was in all commit skills

I'd built the Work Tracking prompt — Step 0b — into `git-commit`. When it
detects no Work Tracking section in CLAUDE.md, it offers to set up issue
tracking. I thought that covered everything.

## The gap Claude found while we were testing

The first thing we did was run Phase 0 and Phase 1 of `issue-workflow` for
cc-praxis — labels created, CLAUDE.md updated, epic #30 (Cut v1.0.1 release)
created with five children. Then we moved to the real test: commit on
remotecc or starcraft and watch Step 0b fire.

Both repos are Java projects. That means `java-git-commit`, not `git-commit`.

Claude checked `java-git-commit/SKILL.md` for Step 0b. It wasn't there. The
prompt didn't exist in the specialised commit skills — only in the generic
root. Any Java, blog, custom, skills, or generic project would silently never see the Work
Tracking offer.

The fix was one block added to three files: `java-git-commit`,
`blog-git-commit`, and `custom-git-commit`. We updated the flowcharts too.
One commit, all three covered.

Then the test. Neither remotecc nor starcraft had a GitHub remote, so we
created both repos and added the origins first. The full flow ran on each:
`java-git-commit` fires, Step 0b detects no Work Tracking, user says YES,
Phase 0 completes, labels created, CLAUDE.md updated. It worked.

## Garden merge, two one-line fixes, and a surprise: 25 submissions

Issue #32 was merge the pending garden submissions — I'd noted five in
the handover. When Claude listed the directory, there were 25. Sessions
across four projects had been submitting without anyone merging.

We dispatched a subagent with full context budget — the garden skill's
own recommendation for merges. It integrated 31 entries, resolved a
three-way GE-0053 ID conflict where three simultaneous sessions had
claimed the same ID, assigned IDs to four files that had none, and
committed cleanly. Nine new garden files, nine updated.

The two smaller issues were genuinely small. The ADR skill's template left
`YYYY-MM-DD` as a literal placeholder with no instruction to fill it in —
Claude was leaving it blank. One sentence fixed it. The retro-issues skill
was silent about the proposal file after issues were created. We added the
answer: commit it as a permanent audit trail, never delete it.

## Twenty false gaps and nine real ones

Before tagging v1.0.1, I wanted to check that all post-v1.0.0 commits had
issue coverage. We ran `retro-issues` on the full 184-commit range. The
skill produced a proposal with 26 standalone issues.

Twenty were duplicates of the previous retro-issues run from 2026-04-06.
The subagent analysing git history doesn't know which GitHub issues already
exist — it just sees commits and groups them. The nine genuine gaps were
commits like the Graphviz-to-Mermaid conversion, the documentation audit,
author initials in blog filenames, and the mandatory bug fix workflow. We
created and immediately closed all nine as retrospective issues.

`gh release create v1.0.1 --generate-notes` pulled from 45 closed issues.
The notes look right.

## Where the garden stands

The drift counter hit 31 — above the 10-entry threshold that triggers a
DEDUPE recommendation. The next session that needs to merge garden
submissions should run a sweep first. The knowledge is there; it just
needs deduplication.

Epic #30 is closed. Issue #36 is the one open thread: designing
design-snapshot as an indexed folder with an INDEX.md, and a cross-tool
meta-index so session-handoff can point to garden entries, blog posts, and
snapshots without loading any of them. The methodology family is mature
enough now that the retrieval problem is starting to bite.
