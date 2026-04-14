---
layout: post
title: "cc-praxis — The Retrospective Runs on Itself"
date: 2026-04-07
type: phase-update
entry_type: note
subtype: diary
projects: ["cc-praxis"]
---
# cc-praxis — The Retrospective Runs on Itself

**Date:** 2026-04-07
**Type:** phase-update

---

## What I was trying to achieve: validate retro-issues against its own repo

The retro-issues skill had been through several refinements over the past two
sessions — epic coherence gates, scope-based clustering, related-scope merging.
The HANDOVER.md had one instruction: run /retro-issues on this repo and see if
it holds up. I wanted to know if the skill worked on a real codebase with real
scope patterns, not the contrived examples used during development.

## What we believed going in: probably no epics, clean groupings

cc-praxis had 285 commits over nine days. I expected the scope-based clustering
to group them neatly — `marketplace` commits together, `garden` together,
`validation` together. The repository uses conventional commits consistently,
so the scope field in `feat(garden): ...` would do the work.

I expected no epics. The repo was built in one sprint across many independent
feature areas — garden, marketplace, validation, write-blog, project-health —
all in parallel. No time window would contain only a handful of coherent scopes.

## The run: 285 commits, 0 epics, 27 standalones

Claude gathered all 285 commits in a single `git log` call — the 31.9KB output
hit the tool's display limit and landed in a temp file. The fix was the Read
tool on that path, not a second `cat` call. (A gotcha, submitted to the garden.)

We worked through the phase boundary analysis: v1.0.0 tag on 2026-03-31, eight
blog entries as candidate boundaries. Every candidate epic failed Gate 3 —
children spanning ≥ 4 distinct unrelated scopes means dissolve to standalones.
Our phase windows covered marketplace, validation, QA, testing, readme,
claude-md, philosophy. Eight scopes. Gate 3 requires ≤ 3. No epics, correct.

We produced 27 standalone issues. Related scopes collapsed as designed:
`java-dev` + `java-code-review` + `java-git-commit` → one issue;
`validation` + `qa` + `testing` → one. One commit excluded: the Mermaid diagram
conversion, matching the literal example in the skill's trivial exclusion list.
I opened `docs/retro-issues.md` in Typora, reviewed the groupings, said yes.

## Creating 27 issues: a bash function and a URL trick

`gh issue create` returns the full issue URL as its only output —
`https://github.com/owner/repo/issues/N`. We wrote a `create_and_close()` bash
function using `${url##*/}` to strip everything to the last `/` and get the
number. No jq, no `--json` flag, no intermediate files. Twenty-seven issues
created and closed in sequence, each with a proper body and label.

The garden got three submissions from this session: the bash display-limit
gotcha, the `${url##*/}` technique, and the observation that conventional commit
scopes are a stronger grouping signal than file paths when clustering commits
into issues.

## A clean history and a validated skill

The repo now has a complete closed issue history covering every significant
commit from day zero to yesterday. The skill validated correctly on its own
history — the gates fired where they should, groupings matched author intent,
and the exclusion table stayed short.

The implementation is done. The next question is what to run it on next —
a repo where the epic path actually fires.
