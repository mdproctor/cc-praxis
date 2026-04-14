# Getting Started Guide — Design Spec

**Date:** 2026-04-14
**Status:** Approved
**Scope:** Java developer audience; single-page HTML guide at `/guide/`

---

## Problem

cc-praxis has 48 skills and a detailed README, but no guided path for a developer starting from zero. The README is reference material — it tells you what each skill does, not when to install it or how the skills fit together. New users face the "which 5 skills do I install first?" problem and can't see the workflow arc (write code → review → commit → design sync → epic lifecycle → handover).

---

## Solution

A single-page getting started guide at `docs/guide.html` (Jekyll permalink `/guide/`), with a sticky numbered sidebar navigation that tracks scroll position. Covers 12 skills in the order a Java developer would naturally encounter them, from CLAUDE.md setup through to session handover and the project diary.

**Audience:** Java/Quarkus developers who have Claude Code installed and have added the cc-praxis marketplace, but have not yet installed any skills or set up a project.

---

## File and Placement

- **File:** `docs/guide.html`
- **Permalink:** `/guide/`
- **Layout:** Jekyll `default` layout, with all CSS and JS self-contained inside the page
- **Nav update:** Add "Guide" link to `docs/_layouts/default.html` header nav, active when `page.url contains '/guide/'`

---

## Layout Design

Two-column layout with sticky sidebar:

```
┌─────────────────────────────────────────────────────┐
│ cc-praxis     Guide   Diary   Articles   GitHub ↗   │  ← site nav
├──────────────┬──────────────────────────────────────┤
│              │  Step 3 of 12  ████░░░░░░░░░░░░░░░░  │  ← progress bar
│  GETTING     │                                       │
│  STARTED     │  Java Development                     │
│              │  Your safety-first development rules  │
│  ● Java Dev  │                                       │
│  ○ Code Rev  │  ┌─ WHAT THIS DOES ─────────────────┐│
│  ○ Commits   │  │ Loads safety, concurrency, and   ││
│  ...         │  │ testing rules for every Java file ││
│              │  └──────────────────────────────────┘│
│              │                                       │
│              │  Explanation prose...                 │
│              │                                       │
│              │  ┌─ PROMPT TO TRY ──────────────────┐│
│              │  │  "Review this class for safety"  ││
│              │  └──────────────────────────────────┘│
│              │                                  Next→│
└──────────────┴──────────────────────────────────────┘
```

**Sidebar details:**
- Width: 220px, sticky (stays put while content scrolls)
- Header label: "GETTING STARTED" (small caps, grey)
- Each step: numbered circle (22px) + title + subtitle (for active step only)
- Active step: purple filled circle, bold title, subtitle visible
- Future steps: grey circle, muted title, no subtitle
- Completed steps: purple outline circle with checkmark (optional — see open questions)
- IntersectionObserver watches each section `<h2>` with threshold 0.3; updates active circle on scroll

**Content area details:**
- Progress bar: thin (3px), purple fill, animates as sections enter view
- Section template (every section uses same structure):
  1. Step N of 12 label + progress bar
  2. `<h2>` heading + subtitle paragraph
  3. "WHAT THIS DOES" box (indigo left border, purple tinted background)
  4. Explanation prose (2–4 paragraphs)
  5. "PROMPT TO TRY" block (dark background, monospace, actual paste-able text)
  6. Code excerpt (dark indigo background, syntax-highlighted by colour)
  7. "Next: [Section name] →" transition hint

---

## Prerequisites Preamble (before Section 1)

A brief intro block above the numbered sections — not a numbered step itself:

- Claude Code installed (link to claude.ai/code)
- cc-praxis marketplace added: `/plugin marketplace add github.com/mdproctor/cc-praxis`
- Skills are installed individually as you work through the guide — each section tells you which skill to install

**Installation callout pattern** (appears near the top of every section):
```
┌─ INSTALL THIS SKILL ──────────────────────────────────┐
│  scripts/claude-skill install <name>                  │
│  or: /install-skills → pick from the list             │
└───────────────────────────────────────────────────────┘
```
This box appears once per section, immediately after the "WHAT THIS DOES" box. Sections 1 (CLAUDE.md) and 2 (Workspace) do not have it since those are setup steps, not installable skills.

---

## The 12 Sections

### 1 · CLAUDE.md Setup
**Subtitle:** Your configuration hub — Claude reads this at the start of every session.

**What this does:** Creates the file that every cc-praxis skill reads first. Sets project type, GitHub repo, and work tracking preferences. Without it, skills can't route correctly.

**Key content:**
- What CLAUDE.md is and when Claude reads it
- The `type: java` field — how it routes skills to Java-specific workflows
- `GitHub repo: owner/repo` — enables issue tracking throughout
- `## Work Tracking` section with `Issue tracking: enabled`
- Prompt: *"Set up a CLAUDE.md for my Java project. It's a Quarkus REST API on GitHub at owner/repo."*
- Resulting excerpt showing the minimal valid CLAUDE.md

---

### 2 · Workspace Setup
**Subtitle:** Separate methodology artifacts from your project code.

**What this does:** Creates a companion git repo alongside your project that stores ADRs, design docs, snapshots, and session handovers — keeping the project repo clean.

**Key content:**
- Three modes: project-only (simplest start), project+workspace (recommended), alternative path
- What the workspace contains: `adr/`, `snapshots/`, `blog/`, `specs/`, `design/JOURNAL.md`, `HANDOFF.md`, `IDEAS.md`
- The three routing destinations: `project` · `workspace` · `alternative ~/path/`
- The `## Routing` table in workspace CLAUDE.md — configure before first epic
- Note: workspace-init reads routing config at epic-start time; set routing first
- Prompt: *"/workspace-init"*
- Diagram: project repo ↔ workspace, showing which artifacts go where

---

### 3 · Java Development
**Subtitle:** Safety-first rules for every Java file you write.

**What this does:** Loads development rules covering safety, concurrency, performance, and code quality — in that priority order. Triggers automatically when editing `.java` files.

**Key content:**
- Priority order explicitly: **Safety > Concurrency > Performance > Code Quality** — never compromise on safety for performance
- Safety: resource leaks (try-with-resources), ThreadLocal cleanup, deadlock avoidance
- Concurrency: document thread ownership, avoid shared mutable state without explicit sync
- Common anti-patterns table (rationalization → consequence):
  - "Resource will close automatically" → file descriptor exhaustion
  - "This is single-threaded" → undocumented thread model risk
  - "Synchronized is too slow" → silent data corruption
- Testing: behaviour not implementation, real databases not mocks, test edge cases and error paths
- Quarkus patterns: CDI, reactive streams, native compilation concerns
- Prompt: *"Implement a Quarkus REST endpoint to fetch orders."*

---

### 4 · Code Review
**Subtitle:** Catches problems before they reach the repository.

**What this does:** Reviews staged changes against safety, concurrency, performance, and testing checklists. Triggers automatically before `java-git-commit` if no review has been done in the session.

**Key content:**
- Automatic trigger: if you invoke `java-git-commit` without having reviewed this session, `java-code-review` runs first
- What it checks: safety violations, concurrency bugs, silent data corruption, performance anti-patterns, test coverage gaps
- Security-critical code: auth, payments, PII — automatically escalates to `java-security-audit`
- Review output: CRITICAL (blocks commit) / WARNING (review recommended) / NOTE (informational)
- Prompt: *"Review my changes."* or *"/java-code-review"*

---

### 5 · Smart Commits
**Subtitle:** Commits that keep your design document in sync automatically.

**What this does:** Routes commits through DESIGN.md sync, enforces Java-specific conventional commit scopes, and links to the active GitHub issue. On an epic branch, writes to JOURNAL.md instead of DESIGN.md directly.

**Key content:**
- Invoked as `/java-git-commit` — never plain `git commit` in Java projects
- Step 1: stages changes, checks DESIGN.md is synced (runs `java-update-design` automatically)
- Step 2: proposes a conventional commit message with Java-specific scopes: `rest`, `repository`, `service`, `migration`, `config`, `test`
- Active issue linking: includes `Refs #N` or `Closes #N` automatically (when Work Tracking enabled)
- **Epic branch behaviour:** `java-update-design` writes to `design/JOURNAL.md` (not project DESIGN.md) — the journal accumulates throughout the epic
- **Non-epic behaviour:** `java-update-design` updates project DESIGN.md directly and stages it with the commit
- Prompt: *"/java-git-commit"*
- Example commit: `feat(service): add order validation with retry — Refs #42`

---

### 6 · Brainstorming & Specs
**Subtitle:** Design before you code. Every feature, every time.

**What this does:** Guides a collaborative design conversation that produces a written spec in `specs/`. Explores requirements, proposes 2–3 approaches with trade-offs, presents design sections for approval, then hands off to a written implementation plan.

**Key content:**
- Why design-before-code matters: examined assumptions, shared understanding, spec as contract
- The hard gate: no code is written until the spec is approved — this applies even to "simple" features
- Flow: context → clarifying questions (one at a time) → 2–3 approaches → design sections → spec doc → plan
- Spec lands in `specs/` (workspace if configured, project otherwise)
- `writing-plans` follows brainstorming and produces a step-by-step implementation plan
- The plan is the input to TDD and implementation — everything flows from the spec
- Prompt: *"Let's brainstorm the order validation feature."*
- Visual companion: offer to show mockups/diagrams in browser during design sessions

---

### 7 · Ideas & Decisions
**Subtitle:** Park undecided thoughts. Record decided ones.

**What this does:** Two skills working at different decision readiness levels. `idea-log` captures possibilities before they're decided. `adr` records the decision once made — immutably, with status lifecycle.

**Key content:**

**idea-log:**
- `IDEAS.md` — newest ideas at top, each with status: `active` / `promoted` / `discarded`
- Five operations: CAPTURE, REVIEW, PROMOTE, DISCARD, UPDATE
- Promote to ADR (architectural decision) or issue (implementation work)
- Stale ideas (active, >90 days) flagged during REVIEW
- Prompt: *"Log this idea: cache order lookups in Redis — not decided yet."*

**adr (Architecture Decision Records):**
- MADR format in `adr/` directory
- Triggered automatically when: major version upgrade, new extension/library, choosing between viable patterns, deviating from defaults
- Status lifecycle: Proposed → Accepted → Deprecated → Superseded (by ADR-NNNN)
- Append-only — never delete or rewrite accepted ADRs; create a new one to supersede
- Linked in design snapshots; referenced in JOURNAL.md entries
- Prompt: *"Create an ADR for choosing Panache over plain JPA."*

---

### 8 · Issues & Epics
**Subtitle:** Four-phase tracking that runs automatically once enabled.

**What this does:** Wires GitHub issue tracking into every session. Phase 0 is one-time setup. After that, Phases 1–3 fire automatically at the right moments without user prompting.

**Key content:**
- **Phase 0 (one-time setup):** Creates standard GitHub labels (including `epic`), writes `## Work Tracking` to CLAUDE.md, optionally reconstructs issues from git history
- **Phase 1 (pre-implementation):** When a plan is ready, creates an epic + child issues before any code is written. Each issue: Context / What / Acceptance Criteria / Notes
- **Phase 2 (task intake, automatic):** Before writing code, checks for active issue; if none, drafts one and assesses epic placement — active epic → fits DoD → other open epics → standalone
- **Phase 3 (pre-commit, automatic):** Fallback; verifies issue linkage on staged changes, suggests splitting if changes span multiple concerns
- Cross-cutting detection: one commit should only serve one issue — Phase 3 catches mixed-concern commits
- Specs from brainstorming are posted to the GitHub issue at epic close (not here — done by epic-close)
- Prompt: *"/issue-workflow"* for Phase 0 setup; *"We're starting the auth epic — set up the issue structure."* for Phase 1

---

### 9 · Design Documentation
**Subtitle:** Two records for two purposes: the living journal and the immutable snapshot.

**What this does:** Explains the two design artifact types that are distinct from the project DESIGN.md — JOURNAL.md (mutable, epic-scoped, merges at close) and design-snapshot (immutable, point-in-time, never edited after creation).

**Key content:**

**JOURNAL.md (via java-update-design):**
- Created by `epic-start` in `design/JOURNAL.md` on the workspace branch
- `java-git-commit` appends entries automatically after each commit
- Entries use `§SectionName` anchors that match DESIGN.md section headings — this is the merge key
- Accumulates through the entire epic; merged into project DESIGN.md at `epic-close`
- Sample journal entry showing `§Architecture` anchor and narrative content

**design-snapshot:**
- Immutable dated record: `snapshots/YYYY-MM-DD-<topic>.md`
- Five mandatory sections: Where We Are, How We Got Here, Where We're Going, Open Questions, Linked ADRs
- Never edited after creation — if design moves on, create a new snapshot
- Superseded snapshots: update `Superseded by:` field on old one, create new
- Auto-pruned to 10 most recent
- When to use: before a major pivot, at end of a phase, when starting an epic on unfamiliar territory
- Prompt: *"/design-snapshot"*

---

### 10 · Closing an Epic
**Subtitle:** Branch cleanup, design merge, artifact routing — all in one confirmed workflow.

**What this does:** Closes the epic branch: routes artifacts per your routing config, merges JOURNAL.md into project DESIGN.md via three-way merge, posts specs to the GitHub issue, closes the issue, and cleans up branches. Everything is shown as a plan before anything executes.

**Key content:**
- Step 1: reads `design/.meta` for epic name, project SHA, issue number
- Reads routing config (three-layer: workspace table → global default → built-in `project`)
- Shows resolved routing table before doing anything: `adr → workspace · blog → project · design → workspace`
- JOURNAL.md merge: baseline = SHA recorded by `epic-start`; current = project DESIGN.md; journal = entries from the epic → three-way merge with user confirmation per section
- `§Section` anchor system: each journal entry targets the matching DESIGN.md section by name
- Spec posting: selected specs posted as comments to the GitHub issue
- GitHub issue closed
- Branch cleanup: delete both project and workspace branches, return to main; or keep with `EPIC-CLOSED.md` marker
- Prompt: *"/epic-close"*

---

### 11 · Session Handover
**Subtitle:** End every session with a handoff. Resume any session in one message.

**What this does:** Produces a committed `HANDOFF.md` — a concise pointer document (< 500 tokens) that gives the next session enough context to resume immediately. Git history is the archive; HANDOFF.md is just the delta since last session.

**Key content:**
- **The wrap checklist** (shown at session end before writing HANDOFF.md):
  - [x] write-blog — capture session as diary entry
  - [x] update-claude-md — sync any new workflow conventions
  - [x] forage sweep — check three categories (gotchas, techniques, undocumented) from memory before context is lost
  - [ ] design-snapshot — off by default; only for intentional design freezes
  - [ ] journal-entry — only on epic branches
- **Forage sweep:** happens *before* writing the handover, while context is full. Checks gotchas (silent failures, misleading symptoms), techniques (non-obvious approaches), and undocumented (features found only through trial). Findings submitted to the cross-project knowledge garden.
- **HANDOFF.md delta-first principle:** only changed sections written in full; unchanged sections reference git: `*Unchanged — git show HEAD~1:HANDOFF.md*`
- **Freshness check:** `git log -1 --format="%ar" -- HANDOFF.md` — if >7 days, flag before using
- **Session renaming:** before committing handover, Claude suggests `/rename <Descriptive Name>` — a human-readable title for the session
- **Resuming:** read HANDOFF.md + `git log --oneline -6` — enough to pick up in the next message
- Show a real minimal HANDOFF.md example
- Prompt: *"Create a handover."* or *"/handover"*

---

### 12 · The Project Diary
**Subtitle:** Honest in-the-moment writing. Not a polished retrospective.

**What this does:** Writes diary entries in the author's personal voice — capturing what was believed at the time, including failed attempts, rejected approaches, and mid-build pivots. Entries are never edited after writing; corrections become new entries.

**Key content:**
- **Entry types:** `article` (topic-driven, standalone) vs `note/diary` (session narrative) — chosen at Step 1
- **Voice:** configured from `$PERSONAL_WRITING_STYLES_PATH` (directory of `.md` style guides); falls back to bundled `common-voice.md`
- **Frontmatter metadata:** `entry_type`, `subtype: diary`, `projects: [cc-praxis]`, `tags: [quarkus]`
- **Blog routing:** entries carry metadata; `blog-routing.yaml` resolves which external platforms they're published to when `publish-blog` runs
- **Two pages on the site:** `/blog/` shows only `subtype: diary` entries; `/articles/` shows only `entry_type: article`
- **What makes entries credible:** exact error messages, specific file paths, what was tried before the fix, numbers ("48 false positives"), code blocks for the interesting parts
- **Immutability:** if a belief was wrong, write a Correction entry referencing the original — never edit
- **Sample entry excerpt:** 150-word sample showing honest in-the-moment voice, including a failed first approach and the actual fix
- Prompt: *"Write a blog entry for today's session."* or *"/write-blog"*

---

## Technical Implementation

**File:** `docs/guide.html`
- Jekyll frontmatter: `layout: default`, `title: Getting Started`, `permalink: /guide/`
- All CSS and JS embedded inline (no external deps beyond what default.html already loads)
- CSS: two-column grid, sticky sidebar, section template classes
- JS: IntersectionObserver on each section `h2[data-section]`; on intersection, update sidebar active circle and progress bar width

**Sidebar active state JS (sketch):**
```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      // update active circle to entry.target.dataset.section
    }
  });
}, { threshold: 0.3 });
document.querySelectorAll('h2[data-section]').forEach(el => observer.observe(el));
```

**Nav addition** (`docs/_layouts/default.html`):
```html
<a href="{{ '/guide/' | relative_url }}" {% if page.url contains '/guide/' %}class="active"{% endif %}>Guide</a>
```

---

## Testing

Structural tests in `tests/test_guide_page.py`:
- File exists at `docs/guide.html`
- Jekyll frontmatter present with correct permalink
- All 12 section IDs/data-section attributes present
- All 12 sections appear in sidebar nav
- "PROMPT TO TRY" blocks: 12 present (one per section)
- "WHAT THIS DOES" blocks: 12 present
- Navigation in `default.html` includes `/guide/` link
- IntersectionObserver script present
- No `TBD` or `TODO` placeholder text in content

---

## Open Questions

1. **Completed step indicators:** Resolved — yes, completed steps (scrolled past) show a purple outline circle with a checkmark. Small JS cost, meaningfully improves orientation for a 12-step guide.

2. **Section 2 diagram:** Workspace routing diagram — ASCII art in the page or a small SVG? Recommendation: inline SVG, consistent with the existing site aesthetic.

3. **Sample diary entry:** Should the sample in Section 12 be about a real cc-praxis session (authentic) or a fictional Java project (neutral)? Recommendation: fictional Java project — keeps it universally relatable, avoids meta self-reference.

---

## Success Criteria

- [ ] Guide exists at `/guide/` and is linked from site nav
- [ ] All 12 sections present with correct IDs
- [ ] Sidebar active state updates correctly on scroll (manual test)
- [ ] Progress bar advances as sections enter view
- [ ] All "PROMPT TO TRY" blocks contain paste-able Claude prompts
- [ ] Structural test suite passes (12+ tests)
- [ ] No TBD or placeholder content
- [ ] Sample diary entry reads as authentic diary voice (not polished retrospective)
