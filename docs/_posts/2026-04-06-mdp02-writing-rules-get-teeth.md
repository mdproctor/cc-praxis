---
layout: post
title: "cc-praxis — The Writing Rules Get Teeth"
date: 2026-04-06
type: phase-update
entry_type: note
subtype: diary
projects: ["cc-praxis"]
---
# cc-praxis — The Writing Rules Get Teeth

**Date:** 2026-04-06
**Type:** phase-update

---

## What we were trying to achieve: making the writing rules actually work

The previous entry documented building the writing infrastructure — the style guide, the blog skill, the retrospective mode. What it didn't document is that the infrastructure wasn't working.

Another Claude wrote a blog post. It ignored the style guide entirely. When I asked why, the answer was honest: the instructions say what to do but don't require evidence that it was done. A Claude can read the guide and generate anyway. The gate was missing.

The day became about adding teeth to the rules.

## What we believed going in: enforcement was a few targeted fixes

I thought this would be specific additions — a pre-draft checklist here, a stronger warning there. Three files to touch, maybe an hour.

It turned out to be a full rearchitecture of how writing rules are structured, propagated, and enforced — and then a systematic review that found the rearchitecture had introduced bugs of its own.

## Four layers, mandatory rules, and a Claude that found what I missed

### The enforcement problem

The style guide said "hard constraint, not a suggestion." But there was nothing that stopped a Claude from generating prose before actually checking it. The fix was structural: move the classification gate to before any prose is generated, require evidence of compliance, and make verification mandatory before showing a draft.

Three places got updated simultaneously: the skill's Step 4 became a gate requiring pre-draft voice classification; the style guide got a pre-draft checklist at the top of the AI Collaboration Voice section; CLAUDE.md got an explicit mandatory requirement. All three have to be ignored simultaneously for the enforcement to fail.

### The layering question

Once I started thinking about enforcement, the deeper problem became clear. The style guide was one file doing three different jobs: mandatory craft rules (I/we/Claude registers, code blocks, headings), common voice defaults (tone, sentence targets), and Mark's personal style (corpus fingerprint, vocabulary, personality). These have different audiences and different overrideability.

I split it into a proper four-layer architecture:

1. **Mandatory rules** (`write-blog/defaults/mandatory-rules.md`) — always loaded, cannot be overridden. I/we/Claude registers, code block guidance, heading rules, pre-draft gate.
2. **CLAUDE.md scan** — always, for audience and topic inference. The project already says what it's building and for whom.
3. **Voice** — either the common voice (`common-voice.md`, the fallback) or the personal guide (loaded from `PERSONAL_WRITING_STYLES_PATH`). One or the other, never both.
4. **Invocation-time overrides** — explicit instructions at call time win everything.

`blog-technical.md` shrank from ~480 lines to personal-only content: audience, personality, corpus fingerprint, vocabulary, examples. Everything else moved to the mandatory or common layer.

### The systematic review that found two critical bugs

I asked a separate Claude to review the refactor systematically — no skipping, no assumptions, compare against the git diff. It came back with seven findings: two CRITICALs, two WARNINGs, three NOTEs.

The CRITICALs were real bugs. `PERSONAL_WRITING_STYLES_PATH` is a directory, not a file — but the refactored Step 0 said "load from that path" as if it were a file. A Claude with the env var set would try to read a directory, get nothing, and not fall back to common-voice.md because the variable IS set. The revision protocol in `blog-technical.md` still referenced "the Project Blog section" — a section that had been removed in the refactor.

Both fixed. Two register rules that had been dropped in the extraction (the "don't name Claude for routine execution" guard, the "we for team/community conventions" mistake) were restored. The flowchart got a Step 0 node. The Voice and Perspective Rules section got a note saying it's orientation only — mandatory-rules.md is binding.

### Propagation: other projects needed the rules too

Two more Claudes came back with follow-on findings. One noted that write-blog creates `docs/blog/` but never tells CLAUDE.md about the mandatory style guide — so new sessions in the same project would miss it. The fix: Step 0c now checks before drafting (not after writing), proposes adding the Writing Style Guide section to CLAUDE.md if it's absent, and gates on confirmation before proceeding.

The other noted that no other project's CLAUDE.md had the requirement either. All five project-type templates in `project-type-setup.md` now include the Writing Style Guide section. And `update-claude-md` gets a Step 4b that proposes adding the requirement whenever it detects `docs/blog/` in a project.

### The garden REVISE workflow

Separately: a Claude in another project had found a fix for a garden entry that previously had no solution — a TUI garbling bug in terminal replay, now solved by embedding dimensions in the WebSocket URL and calling `tmux resize-pane` in the right order. But the garden had no mechanism to submit just the solution to an existing entry.

We added a REVISE submission type: a submission file that points to an existing entry by path and title, declares a revision kind (`solution`, `alternative`, `variant`, `update`, `resolved`, `deprecated`), and carries the new content. The MERGE workflow handles them before processing new entries. When a second solution arrives for an entry that already has one, both get restructured into Solution 1 / Solution 2 with explicit pros/cons — but only then; single-solution entries stay untouched.

## What it is now

The writing rules are structural, not advisory. They're split into layers with clear ownership. They propagate to new projects automatically and to existing projects the moment they start a blog. They gate before prose is generated, not after.

The garden can evolve now. Entries that captured a problem without a fix can receive the fix later. Entries that had one approach can get a second. The knowledge compounds rather than sitting frozen.

Forty-five skills. The writing infrastructure is now the most carefully specified part of the collection.
