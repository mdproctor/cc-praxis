---
layout: post
title: "cc-praxis — Teaching the Garden to Remember Itself"
date: 2026-04-06
type: phase-update
entry_type: note
subtype: diary
projects: ["cc-praxis"]
---
# cc-praxis — Teaching the Garden to Remember Itself

**Date:** 2026-04-06
**Type:** phase-update

---

## What we were trying to achieve: a garden that scales

Thirty-two submissions were pending — the most ever at once. Before merging, I wanted to review what was queued and find any patterns worth fixing in the skill first.

What started as a pre-merge review turned into a full rethink of how the garden manages its own identity over time.

## What we believed going in: scoring was the main gap

I expected the review to find a handful of missing scores — the April 5 batch predated the scoring system. Add scores, fix one incomplete fix section, then merge.

The deeper issue took longer to surface: the garden had no stable way to identify its own entries.

## IDs, pairs, and the cost of growing up

### The review revealed the April 5 gap

A separate Claude reviewed all 32 submissions systematically. The finding: all 9 submissions from April 5 were missing Garden Scores entirely — submitted before the scoring system existed. The April 6 batch was mostly clean. Claude added scores to all 9, verified the math, confirmed case-for and case-against for each.

One submission (`starcraft-ocraft-no-precise-resource-debug`) had a Fix section with a commented-out placeholder — unverified code. The section was rewritten to scope the confirmed workarounds honestly and mark the raw protobuf path as an open gap.

### Why IDs needed to move to submission time

The original design: IDs assigned at merge time. The problem: a submitter has no way to track their entry between submission and merge. REVISE submissions had to target entries by fragile path+title — if the title changed, the link broke.

The fix was clear once stated: assign the ID when the submission is written. The counter lives in GARDEN.md. CAPTURE reads it, increments, updates it, and embeds the ID in both the filename (`YYYY-MM-DD-project-GE-XXXX-slug.md`) and the submission header. Two independent ways to find the ID. The commit stages the submission and the GARDEN.md counter update atomically.

Race condition: if two Claudes submit simultaneously, one git commit will fail on GARDEN.md. The loser rebases, re-reads the counter, takes the next ID. Git's append-only history makes this safe.

### Three checks, one sparse log, and a drift counter

Duplicate detection at scale has a nasty cost structure: comparing every new entry against every existing entry is O(N²). As the garden grows, that becomes prohibitive. The solution is three tiers:

1. **Light (CAPTURE):** scan the GARDEN.md index for same-category entries. Title comparison only, no file reads. Flag if suspicious.
2. **Medium (MERGE):** read the first 30 lines of same-category candidates. Symptom + root cause. User decides: duplicate / related / distinct.
3. **Exhaustive (DEDUPE):** full content comparison across the category. Run periodically, not every merge.

The key to making DEDUPE tractable is CHECKED.md — a sparse log of pairs already compared. On each sweep: enumerate all within-category pairs, subtract the already-checked set, process only the remainder. Each pair is checked once and never again unless one entry is revised. O(N) per new batch rather than O(N²) total.

When should DEDUPE run? Not on a fixed schedule — quiet periods waste effort, bursts of activity may miss consistency gaps. Instead: a counter tracks entries merged since last sweep. When it hits the threshold (default 10), the next MERGE session offers to run DEDUPE first. Activity-based triggering matches cost to actual need.

When MERGE discards a submission as a duplicate, DISCARDED.md records the submission's GE-ID alongside the canonical GE-ID it conflicted with. The submitter reads it, understands their submission was already covered, and can write a REVISE targeting the correct entry instead.

### A validator to catch it when we're wrong

The system has many moving parts: GARDEN.md index, CHECKED.md pair log, DISCARDED.md, garden content files with IDs, submission files with IDs. Any of these can drift.

Claude built a Python validation script (`~/claude/knowledge-garden/scripts/validate_garden.py`) that checks seven properties: entry ID uniqueness, counter consistency, index/entry cross-referencing, CHECKED.md pair validity, DISCARDED.md reference validity, and submission ID presence. Exit codes: 0 = clean, 1 = errors, 2 = warnings only. After retroactively assigning IDs to all 33 existing submissions, the validator ran clean.

Six test scenarios document the happy paths and edge cases: first submission, sequential submissions, CAPTURE-time duplicate catch, MERGE-time duplicate catch with DISCARDED.md, REVISE by ID, and drift threshold triggering DEDUPE.

## What it is now

The garden has 35 submissions ready to merge (GE-0001 through GE-0035), a working validator, and a duplicate detection system designed to scale. The first merge session will be the real test — it assigns IDs to all existing entries, runs the light duplicate checks, and populates CHECKED.md for the first time.

The DEDUPE sweep hasn't run yet. CHECKED.md is empty. The drift counter starts from zero. In ten merges, the system will ask whether it's time for a full sweep — and that will be the first real test of whether the design holds.
