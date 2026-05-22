---
layout: post
title: "work-end fix, engine audit, pause stack"
date: 2026-05-21
type: phase-update
entry_type: note
subtype: diary
projects: [cc-praxis]
tags: [work-end, git, audit, pause-stack]
---

The session started as a bug report and turned into a full audit of everything that had been silently going wrong.

## work-end wasn't merging the code

The bug: `work-end` promotes artifacts, merges the journal, closes the issue — but never merges the project implementation branch onto local main. Every session I was ending work and then manually rebasing branches to main afterward, not realising it was the skill's job to do it.

We added Step 8j. After the journal merge, before marking closed: checkout project main, `git rebase $BRANCH_NAME`, push to fork remote (prompted), offer upstream PR if an `upstream` remote exists. Hard stop on conflict.

The upstream PR logic is topology-aware — no hardcoded remote names. If `git remote get-url upstream` returns a URL, it's a fork model and a PR is offered. If not, the push to origin is the final delivery.

## The engine three-way audit

Engine was more involved. Local, origin (mdproctor/engine), and upstream (casehubio/engine) were all in different states. Local had ~60 feat/* branches with 100–160 commits each, all showing "214 commits behind upstream."

The uniform number was the signal. When upstream merges PRs via squash or rebase, it creates new SHAs — git sees the branch commits as absent even though the work is there. All branches had forked from the same local main, so they were all equally behind. Checking one branch confirmed it: `feat/engine-221-message-type` had its work in upstream as `621ba7e feat: add MessageType... — engine#221`. Every branch was stale in the same way.

Upstream also had 4 treblereel commits local didn't have. Engine Claude pulled those in via `git rebase upstream/main`, resolved conflicts across 18 overlapping files (treblereel adding `$secret`/`$config` JQ scope variables, our side adding humanTask binding and deadline features), then submitted 6 PRs to casehubio covering all 28 local commits.

## Pause stack

The old `work-pause` wrote a `.paused` marker on workspace main — one slot, one branch at a time. The obvious question: why pause if you can't stack?

I wanted the full pattern: pause branch A, start branch B, end B, resume A — and on resume, automatically rebase A onto main to pick up whatever B contributed.

The redesign:
- **Pause**: commit all WIP as `WIP: paused $BRANCH at $TIMESTAMP` on the branch (no stash — commits are durable), append an entry to `.pause-stack` YAML on workspace main
- **Resume**: show stack picker if depth > 1, rebase selected branch onto main, then `git reset HEAD~1` to restore working state
- **Work router**: checks stack depth on main — auto-resumes if 1 entry, shows picker if 2+, starts new work only if stack is empty
- **Work-end**: can close a branch in the stack without resuming it; removes the entry in Step 9

Five skills updated: `work`, `work-pause`, `work-resume`, `work-start`, `work-end`. The WIP commit approach is cleaner than stash — no positional ref confusion, survives across sessions, visible in branch history.
