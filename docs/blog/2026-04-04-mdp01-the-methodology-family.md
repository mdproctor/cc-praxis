# cc-praxis — The Methodology Family

**Date:** 2026-04-04
**Type:** phase-update

---

The original cc-praxis skills were all about working with code — reviews, commits, dependency updates, observability. But there's a whole class of work that isn't code: design decisions, ideas that aren't ready to act on, moments when the project pivots, hard-won knowledge that gets rediscovered by the next person.

I wanted skills for that.

## What we were trying to achieve: Capturing design thinking as it happens

A family of tools for the methodology of building, not just the mechanics. Not written after the fact — written in the moment.

At the same time, I wanted to properly review the web installer UX. We'd built it to work. Now I wanted it to be good.

## What we believed going in: Three skills would be enough

`adr` already existed. I'd add `design-snapshot` to freeze design state and `idea-log` to park undecided ideas, and that would probably cover it.

The UX review I expected to surface mostly small things — button placement, text clarity. That turned out to be true in volume but wrong in depth.

## The design thinking trio

Three skills, each with a clear role:

- `idea-log` — undecided possibilities. Park the "what if we..." thoughts before they evaporate. Mutable, informal.
- `adr` — individual decisions. Formal, immutable once written, structured for archival.
- `design-snapshot` — full design state at a moment. Immutable record of where the project is right now.

The relationship between them is what makes them a family rather than three independent tools. Ideas promote to ADRs when they're ready. Snapshots reference ADRs rather than duplicating them. A snapshot review can surface new ideas for the log.

When I reviewed the chaining, `design-snapshot` didn't mention `idea-log` at all. `adr` didn't point back to `idea-log` for pre-decision thinking. We rewired all seven methodology skills — adding `write-blog` and `garden` later — so they explicitly reference each other.

## write-blog

This came from a request to support writing that none of the other skills covered: an ongoing development diary written in the moment, not in hindsight. Not a polished retrospective. Not an ADR. The lived experience of building something — including the things you believed that turned out to be wrong.

The key principle: correction entries never edit the original. If the March 29th entry said "I believe X" and X turned out to be wrong, the April entry says "we were wrong about X, here's why" — but the March entry stands as written. The historical record matters.

## garden: synthesised from three sessions

Three separate Claude instances had each been asked to design and build a knowledge garden concept — a machine-wide library of hard-won technical gotchas. I reviewed all three designs and synthesised them.

The most important contribution: the *proactive trigger*. The reactive trigger ("add this to the garden") is easy. The proactive one — where the skill fires without being asked when a debugging session reveals something non-obvious — is what makes it genuinely valuable. Signs: multiple approaches tried before the fix, something works in JVM but fails silently in native image, "that took way too long."

The garden already existed at `~/claude/knowledge-garden/` with real entries. I created `GARDEN.md` with a dual index — by technology AND by symptom type. The same entry is findable by "I'm working with AppKit" and by "something is silently failing with no error."

## The UX review

We did a systematic review across ergonomics, aesthetics, and user flow. The issues ranged from trivial to structural:

- Stats on the About page were stale: "33 skills, 2 languages, 163 tests" when the real numbers were 43, 3, and 295+
- Python was showing as "COMING SOON" even though it shipped completely
- The "Install Now →" button on GitHub Pages silently redirected back to About
- Partial bundle state used amber — a warning colour — when partial install is just a status, not a problem
- No way to install a skill directly from the Browse tab; you had to switch to Install first

That last one changed the fundamental usage pattern. Adding Install/Uninstall buttons directly to Browse overview cards removed the need for a tab-switch just to act on a skill.

## The consistency audit

After adding the new skills, I asked a separate Claude to audit everything for consistency. It came back with five gaps:

- `cc-praxis-ui` was missing from ALL_SKILLS entirely — no overview card, no install row, not counted
- `idea-log` and `write-blog` were missing from the Extras bundle in the Install tab
- README Layer 7 said "7 skills" but had 8 rows
- Hero stats were out of date
- The `install-individual` config covered 8 skills instead of all 14

All five fixed in a single commit. The lesson: run the audit after every new skill addition, not as a separate pass afterward.

## What it is now

The methodology family — `idea-log`, `adr`, `design-snapshot`, `write-blog`, `garden` — is cc-praxis's most distinctive feature. The code-related skills exist in other forms elsewhere. The tools for capturing design thinking in real time, preserving what you believed before you knew better, building a cross-project library of hard-won knowledge — that's the part I haven't seen done this way before.

The web installer is genuinely useful, but it's only as correct as the state it reflects. Getting bundle counts, button visibility, and modal skill lists to accurately reflect real install state required more work than building the UI itself.

We're at 44 skills spanning Java, TypeScript, Python, and the methodology family. The next question is what gets added versus what gets refined — and whether the dual-repo idea for epic-scoped developer work becomes something more concrete.
