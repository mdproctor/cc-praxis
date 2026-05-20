---
layout: post
title: "Taxonomy, fingerprint, corpus"
date: 2026-05-20
type: phase-update
entry_type: note
subtype: log
projects: [cc-praxis]
tags: [write-content, taxonomy, corpus]
---

The taxonomy took longer than expected. Not because it's complicated — because every boundary kept revealing a new case that forced a clearer definition.

I started wanting to tighten my writing style. I ended up building a content classification framework with academic grounding spanning two centuries.

## Four types, not two

The core is encoder/decoder. Notes are encoder-dominant — I'm processing, and the reader gets access to that process. Articles are decoder-dominant — structure serves the reader's comprehension. That binary didn't last. I added InfoBrief (maximum density — proposition and evidence only, no scaffolding) and News (time-anchored announcements and events) before the session was out.

The subtypes did most of the work. Note splits into log (coding diary only), musing (quick observation or reaction), and idea (a specific proposal beyond a musing). Article covers tutorial, how-to, explanation, commentary, and essay — each with distinct intent and structural rules.

## InfoBrief was the surprise

I expected to find a reasonable cluster of InfoBrief-style posts in the historical corpus. There were three. In 570 posts. InfoBrief is nearly absent — which means it's an emerging form, not an overlooked one.

## Five frameworks reach the same four aims

I found Kinneavy (1969) "Basic Aims of Discourse" — the paper that sits at the centre of everything. Kinneavy himself noticed the convergence: his four aims, Newman (1827), and Britton (1970) show "almost fearful symmetry." The aims keep resolving to the same four: expressive (processing for the self), referential (informing about reality), persuasive (arguing to a position), literary (form as the point).

Add Diátaxis (2017) and the taxonomy here — five independent frameworks, across two centuries, all landing on the same territory.

What this means in practice: our four types map directly onto those aims. Note is expressive — encoder-first, no audience shaping. Article/essay is persuasive — argued to a conclusion. InfoBrief and News are referential — information-dominant, neither encoder nor decoder foregrounded. Article/explanation sits in the referential cluster too, oriented toward the reader's understanding.

The literature doesn't just support the taxonomy. It independently derived it. That's a different kind of confidence than "this felt like the right way to cut it."

Zero papers connect these five frameworks in any academic database. That's the article waiting to be written.

## Extracting the universal layer

write-blog was doing content-type reasoning it didn't need to own. I extracted it into write-content — a universal content creation skill: load writing style, determine content type, load the form guide, apply structure principles and anti-slop, write, quality check. write-blog now consumes it as a prerequisite layer.

Any future content skill starts at write-content, not blank.

## 570 posts, 91 labels

I brought Claude in to classify the historical corpus. We classified 570 posts by taxonomy, quality, and labels. Claude built a navigable index — by taxonomy across 12 sections and by 91 labels. The initial pass classified 217 posts as Note/log — most were news events, conference recaps, job postings. Log means coding diary only. The correct count is 32.

## The fingerprint

Claude drew the linguistic fingerprint from a 24-post stratified sample: Core Voice DNA, five Voice Archetype Rules, quantitative facts (sentence length, section count, ratio patterns), top canonical examples, phase evolution across 2006–2017. It lives at `~/claude-workspace/writing-styles/mark-proctor-voice.md`.

## Hook fix (#66)

The session-start hook kept reverting. I edited `install-skills/SKILL.md` — no effect. I patched `~/.claude/hooks/check_project_setup.sh` directly — sync-local overwrote it on the next run. I committed the fix to the SKILL.md — sync-local used the old hook anyway.

The canonical source is `hooks/check_project_setup.sh` at the repo root. sync-local copies it directly. The SKILL.md bash block is documentation only. Only way to find it was tracing the Python script.

## /work as the unified entry point

`/work` now routes the full lifecycle — detects current state and routes to work-start, work-end, work-pause, or work-resume automatically. One entry point instead of four.
