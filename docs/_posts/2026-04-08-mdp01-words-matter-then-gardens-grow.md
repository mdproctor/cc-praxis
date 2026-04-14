---
layout: post
title: "cc-praxis — Words Matter, Then Gardens Grow"
date: 2026-04-08
type: phase-update
entry_type: note
subtype: diary
projects: ["cc-praxis"]
---
# cc-praxis — Words Matter, Then Gardens Grow

**Date:** 2026-04-08
**Type:** phase-update

---

## What I came in to do: resume where the last session left off

The handoff said three things: register Hortora domains before the window closed, create GitHub issues and epics, and start migrating the garden to v2 structure. A few hours of housekeeping before the real design work.

It turned into something considerably more interesting.

## The terminology problem I didn't know I had

I opened by asking whether the session-handoff skill should be called "handover" or "handoff." I had used them interchangeably, and I wanted docs and filenames to be consistent. Claude's first recommendation was "handiff" — the skill was already named `session-handoff`, so everything should align to it.

Then I noticed: the skill's own prose used "handover" 68 times and "handoff" only 6. Claude had just recommended "handiff" while itself using "handover" in every response. When I pointed this out, the recommendation flipped immediately. The data had been there the whole time.

We ended up with something cleaner than either: a genuine semantic split. *Handover* is the act — what you do at session end. *Handoff* is the artifact — the `HANDOFF.md` file passed to the next session. Skills are named after what they *do*, so: `session-handover`. The file is the thing produced, so: `HANDOFF.md`. It holds up.

The rename touched 22 files, two file renames, and involved 116 locations across the codebase. We also added a structural naming consistency check to `project-health/check-categories.md` — if a skill named `session-handoff` generates `HANDOVER.md`, that's now a caught inconsistency.

## Hortora goes live

With that resolved, I bought `hortora.org` (`.com` was taken). We created the `hortora` GitHub org, three repos — `garden`, `spec`, `soredium` — and a GitHub Project for the roadmap.

The naming of `soredium` took its own detour. I wanted something horticultural for the tools repo. We worked through trowel, trellis, taproot, rhizome — then into fungi: hyphae, sporangium, soredia. A soredium is a lichen's dispersal unit: a self-contained bundle that carries everything needed to grow a new colony wherever it lands. That's exactly what the tools repo is — validators, CI, MCP server, Obsidian plugin, Claude skill. `hortora/soredium`. Done.

## Two founding blog entries, illustrated

The Hortora blog needed two entries. The first was the origin story — why the garden exists, how it started, the naming. The second was the design session itself — one fix, one afternoon, one project.

We wrote both, then added illustrations: SVG diagrams screenshotted via Playwright. Four for the first entry (the loop, the garden growing, the workflow, the vision rings), four thumbnails floating beside text in the second.

The concentric rings diagram produced the most iteration. I wanted the ring labels to sit below the arc line. Claude tried `dy="14"` on the textPath. The text stayed on the line regardless of the value. The fix turned out to be geometry, not attributes: define the arc path at a smaller radius than the visible ring, so the text baseline sits inside naturally. That's now a garden entry (GE-0106).

Claude also corrupted `tmux.md` mid-merge by matching a partial heading with `str.replace()`. The heading `## send-keys silently interprets "Enter"/"Escape" as key names without -l flag` got the ID inserted after the prefix, splitting it into two lines with the tail of the heading on the second. No error raised. Had to `git checkout` the file and redo with regex. That's GE-0107.

## Garden DEDUPE and MERGE

The garden's drift counter was at 31 — well past the threshold of 10. We ran a full DEDUPE sweep (24 pairs across 8 categories, zero duplicates found, five related pairs cross-referenced), then merged 22 pending submissions from five projects. Three new domain directories: `intellij-platform/rename-refactoring.md`, `intellij-platform/indexing.md`, `tools/html2text.md`. Ten existing entries got IDs assigned — they'd been in the garden since before the ID system existed.

We also migrated the garden from `~/claude/knowledge-garden/` to `~/claude/garden/` (now the `hortora/garden` repo), with a symlink back so every existing session that points at `knowledge-garden` keeps working without knowing anything changed.

## hortora.github.io

The landing page came together quickly — botanical aesthetic, Cormorant Garamond, animated SVG plant growing with knowledge-graph nodes, parchment background, three pillars, a pull quote from the first blog entry. Then the blog itself: diary index, two post pages, shared stylesheet.

We hit the obvious GitHub Pages gotcha: `href="blog/"` works on a web server (auto-serves `index.html`) but shows a directory listing when opening files locally. Fix is explicit `index.html` everywhere. That's GE-0114.

## Where this leaves things

Four open issues in the Hortora Roadmap: push the spec README, Phase 1 garden migration (78 entries to v2), soredium scaffold, and clean up the Hortora content still sitting in cc-praxis. The site is live at hortora.github.io. The garden skill stays in cc-praxis until the migration is done.

The `issue-workflow` skill got one addition: organise epics and issues by capability area, not timing. A phase-named issue becomes meaningless the moment it ships. A capability-named issue stays useful forever.
