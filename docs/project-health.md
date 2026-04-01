# project-health — Design Document

**Status:** Design phase — not yet implemented as a skill
**Skill name (planned):** `project-health`
**Slash command (planned):** `/project-health`

This document tracks the design and scope of the `project-health` skill. It is a working document — update it as the skill evolves.

---

## Purpose

A single skill that covers all the systematic verification, validation, and improvement checks that get asked for repeatedly during development. Instead of asking Claude ad-hoc, the user invokes a named, configurable, consistent check.

It replaces:
- "do a deep analysis of our work"
- "make sure docs and code are in sync"
- "check for duplications, conflicts, gaps"
- "look for potential bugs or poor UX"
- pre-release system reviews

Other skills can reference specific check categories when they need things verified.

---

## Invocation

```bash
# Interactive — presents menu of categories to select
/project-health

# Run specific categories
/project-health docs-sync cross-refs

# Run all categories for this project type
/project-health --all

# Run categories configured as default in CLAUDE.md
/project-health --defaults

# Predefined groups (see Suggested Invocation Groups)
/project-health --commit
/project-health --prerelease
/project-health --refine
/project-health --setup
```

---

## CLAUDE.md Configuration

Stored in `## Health Check Configuration`:

```markdown
## Health Check Configuration

**Default checks:** docs-sync, cross-refs, consistency, coverage, quality
**Skip:** git, effectiveness
**Performance budget:** 400 lines max per SKILL.md
**Additional doc paths:** wiki/, design/
```

If no section is present, built-in defaults are used.

---

## Document Scanning Scope

When running any check that involves reading documentation, build the scan list in this order:

### 1. Universal baseline (always included)

All `.md` files (recursive) in any folder named `doc/`, `docs/`, or `documentation/` (case-insensitive), plus any root-level `.md` file matching these well-known names (case-insensitive):

| Group | Filenames |
|-------|-----------|
| Entry points | `readme`, `overview`, `summary`, `index` |
| Process | `contributing`, `governance`, `code_of_conduct`, `support`, `maintainers` |
| Change tracking | `changelog`, `history`, `release`, `release-notes`, `release_notes` |
| Architecture & design | `architecture`, `design`, `decisions`, `vision`, `philosophy`, `principles` |
| Technical | `api`, `schema`, `glossary`, `security`, `deployment`, `install`, `installation`, `usage`, `troubleshooting` |
| Project management | `roadmap`, `thesis`, `spec`, `specification`, `requirements` |

Any root `.md` file not on this list is still scanned — the list simply guarantees they are never skipped.

### 2. Inline documentation (always included)

Some projects keep docs alongside their code. Always scan:
- Any `README.md` anywhere in the directory tree (per-module, per-package docs)
- Any `CHANGELOG.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md` found anywhere in the tree
- For Java: `package-info.java` and Javadoc comments in source files

### 3. Per project type (included automatically)

| Type | Additional scan targets |
|------|------------------------|
| `skills` | All `SKILL.md` files in repo root subdirectories |
| `java` | `pom.xml` / `build.gradle`; Javadoc in `src/` |
| `blog` | `_config.yml`, `_posts/`, `_layouts/`, `_includes/` |
| `custom` | The Primary Document path declared in CLAUDE.md |

### 4. User-configured locations (from CLAUDE.md)

Declared in `## Health Check Configuration` as `Additional doc paths:` — useful for wiki directories, generated resource files, non-standard architecture folders, etc.

### 5. Non-markdown files (scanned where relevant)

- `.claude-plugin/marketplace.json` — skill registry and versions
- `hooks/` — hook scripts
- `scripts/` — what scripts actually do (for logic and docs-sync checks)
- `tests/` — what is tested (for coverage and code checks)

**Principle:** scan broadly rather than miss a stale reference. If a file is irrelevant, the check simply finds nothing of interest there.

---

## Category Overview

Each category covers two dimensions:
- **Quality** — is it correct, complete, and compliant? (pass/fail)
- **Refinement** — could it be clearer, smaller, or better structured? (judgment)

**Type key:** Mechanical — scriptable, low ambiguity · Judgment — Claude must reason about intent · Mixed — some of each

---

### Universal Checks

*Apply to every project type. Specific items within a category may vary by type — see per-type notes below.*

| Category | Quality focus | Refinement focus | Type | When to run |
|----------|--------------|-----------------|------|-------------|
| `docs-sync` | Code matches docs, no stale language, correct counts and URLs | Over-explanation, mismatched detail level, mergeable sections | Mechanical | Every commit, pre-release |
| `consistency` | No contradictions, no duplicate content, consistent terminology | Consolidation into single source of truth, terminology glossary | Judgment | Pre-release, deep review |
| `logic` | Workflows executable, UX unblocked, exit codes correct | Simplify steps, reduce confirmations, plain-language errors | Judgment | Pre-release, deep review |
| `config` | CLAUDE.md complete for project type, required sections present | CLAUDE.md overloaded, Sync Rules oversimplifiable | Mechanical | On setup, pre-release |
| `security` | No secrets, safe shell patterns, correct permissions | Simpler scripts reduce attack surface; shell vs Python tradeoffs | Mechanical | Pre-release |
| `release` | Versions consistent, labels set up, no SNAPSHOT for release | Release notes coherent, issue titles useful, versioning simplified | Mixed | Release only |
| `user-journey` | Onboarding works, errors recoverable, no dead ends | Automate setup steps, shorten onboarding, better prompt timing | Judgment | Pre-release, major changes |
| `git` | Clean state, no stale worktrees, tags match versions | Branching strategy, tag naming, dead branches | Mechanical | On demand |
| `refine` | — (refinement is the purpose of this category) | Docs structure, code deduplication, test grouping, universal bloat | Judgment | On demand, periodic review |

---

### type: skills

*Additional checks for skill collection repositories.*

| Category | Quality focus | Refinement focus | Type | When to run |
|----------|--------------|-----------------|------|-------------|
| `cross-refs` | Bidirectional chaining, all references resolve, table complete | Chain depth, table grouping, merge candidates | Mechanical | Every commit |
| `coverage` | New skills in marketplace + README + commands/ + chaining | Manual steps that could be automated | Mechanical | Every commit |
| `quality` | CSO compliance, required sections, flowchart syntax, token budget | Fewer steps, simpler flowcharts, redundant pitfall rows | Mixed | Pre-release |
| `naming` | Skill name consistent across directory, frontmatter, marketplace, README, commands/ | Discoverability, intuitive vs accurate names | Mechanical | Every commit |
| `infrastructure` | All validators wired at correct tier, hook registered, gitignore | Overlapping validators, tier misassignment, dead scripts | Mechanical | Pre-release |
| `dependencies` | Prerequisites exist, no circular chains, versions consistent | Chain depth, skill absorption, optional complexity | Mechanical | Pre-release |
| `performance` | SKILL.md within token budget (~400 lines) | Reference file extraction, duplicate content, lean sections | Mixed | Pre-release |
| `effectiveness` | No redundant skills, descriptions trigger correctly | Skills that should be absorbed, wrappable workflows | Judgment | Deep review only |

---

### type: java

*Additional items within universal categories for Java/Maven/Gradle projects.*

| Category | Quality additions | Refinement additions |
|----------|------------------|---------------------|
| `docs-sync` | DESIGN.md exists and reflects current architecture; no stale entity/service references | Could DESIGN.md be split into focused modules? |
| `config` | `docs/DESIGN.md` present; BOM strategy documented | Could BOM strategy be expressed more concisely? |
| `logic` | No blocking JDBC on Vert.x event loop in examples; @Blocking annotations correct | Could concurrency guidance be simplified? |

---

### type: blog

*Additional items within universal categories for GitHub Pages / Jekyll blogs.*

| Category | Quality additions | Refinement additions |
|----------|------------------|---------------------|
| `docs-sync` | Post filenames follow `YYYY-MM-DD-title.md`; no broken Jekyll front matter | Could post metadata be standardised for better navigation? |
| `config` | `_posts/` exists; `_config.yml` present; Jekyll conventions in CLAUDE.md | Is CLAUDE.md's blog section concise and up to date? |
| `quality` | Blog commits use valid types (post/edit/draft/asset/config); 72-char limit | Could commit type guidance be expressed more briefly? |

---

### type: custom

*Additional items within universal categories for custom projects.*

| Category | Quality additions | Refinement additions |
|----------|------------------|---------------------|
| `config` | Sync Rules configured; Primary Document path exists; milestone current | Could Sync Rules be simplified without losing fidelity? |
| `docs-sync` | Primary document reflects current project state; sync rules match file structure | Is the primary document the right size, or should it be modularised? |

---

### Refinement Domains (within `refine`)

*The `refine` category is organised by domain rather than correctness — everything here is an improvement opportunity, not a failure.*

| Domain | What it looks for | Bloat score applies? |
|--------|------------------|---------------------|
| `docs` | Structure re-evaluation, modularisation, consolidation, readability, dead content | Yes |
| `code` | Repeated patterns, copy-paste with variation, missing abstractions, dead code | Yes |
| `tests` | Scattered coverage, repeated setup, file bloat, grouping inconsistency | Yes |
| `universal` | File budget overruns, deep nesting, over-engineering, excessive commentary | Yes — primary source of bloat score |

---

### Suggested Invocation Groups

| Group | Categories | Use when |
|-------|-----------|----------|
| `--commit` | `docs-sync`, `cross-refs`*, `coverage`*, `naming`* | Fast checks after every significant change |
| `--prerelease` | All mechanical + mixed categories for the project type | Before tagging a release |
| `--deep` | All categories for the project type | Periodic deep review, after major refactors |
| `--refine` | `refine` only | Dedicated improvement session |
| `--setup` | `config`, `infrastructure`*, `coverage`* | After initial project setup |

*\* type: skills only — skipped automatically for other project types*

---

## Check Categories

Each category below covers both **Quality** (is it correct?) and **Refinement** (could it be better?). Quality items are declarative pass/fail checks. Refinement items are judgment questions — there is no single right answer.

---

### `docs-sync` — Documentation Accuracy

**Quality** — Does documentation accurately reflect the current state of the code?
- [ ] Code behaviour matches what docs describe
- [ ] No "planned" / "not yet implemented" language for things that exist
- [ ] Skill counts and validator counts are correct everywhere
- [ ] Version numbers consistent (marketplace.json, plugin.json, docs)
- [ ] URLs and GitHub repo references are correct
- [ ] No stale "TODO" or "coming soon" references
- [ ] Release status language matches actual state

**Refinement** — Could the documentation communicate the same information more effectively?
- [ ] Are there over-explained sections where the code is self-evident?
- [ ] Is the detail level appropriate for the intended audience?
- [ ] Could any prose be replaced with a table or example that's easier to scan?
- [ ] Are there sections whose purpose overlaps enough to merge?

---

### `cross-refs` — Cross-Reference Integrity

**Quality** — Are all links between skills and documents complete and bidirectional?
- [ ] Every skill mentioned in the chaining table exists
- [ ] Chaining is bidirectional where required (A→B means B mentions A)
- [ ] Skill Chaining Reference table covers all skills including new additions
- [ ] Prerequisites sections reference skills that exist
- [ ] All markdown links to other `.md` files resolve

**Refinement** — Could the reference structure be simpler or more navigable?
- [ ] Are any chains unnecessarily long (A→B→C→D where A→C would suffice)?
- [ ] Could the chaining table be reorganised to group related skills more intuitively?
- [ ] Do the number of cross-references between two skills suggest they should merge?

---

### `consistency` — Internal Consistency

**Quality** — Does everything agree with itself?
- [ ] No contradictions between any two documents on the same topic
- [ ] No duplicate information that could drift (same content in 2+ places)
- [ ] Section naming conventions followed (Skill Chaining, not Skill chaining)
- [ ] Common Pitfalls tables use consistent column format
- [ ] Severity levels (CRITICAL/WARNING/NOTE) used consistently
- [ ] Terminology is consistent (e.g. "invoke" not mixed with "call" or "use")

**Refinement** — Could duplicated or scattered information be consolidated?
- [ ] Could scattered terminology be unified in a glossary or shared reference?
- [ ] Are there sections that say the same thing in different words that should be merged?
- [ ] Could inconsistent formatting be standardised to reduce cognitive load?

---

### `coverage` — Integration Coverage

**Quality** — Are new skills and features fully wired into the broader system?
- [ ] Every skill has a `commands/<skill-name>.md` slash command file
- [ ] Every skill is in `.claude-plugin/marketplace.json` plugins list
- [ ] Every skill appears in README.md § Skills section
- [ ] New skills appear in README.md § Skill Chaining Reference table
- [ ] New skills appear in CLAUDE.md § Key Skills
- [ ] Every validator is wired into `scripts/validate_all.py` at the correct tier
- [ ] New project types added to all required locations

**Refinement** — Are there integration points that could be automated or simplified?
- [ ] Are any manual integration steps (README update, chaining table entry) candidates for automation?
- [ ] Are there steps that are consistently forgotten, suggesting a better workflow?

---

### `logic` — Workflow Logic & UX

**Quality** — Do the described workflows actually work?
- [ ] No skill step references a script that doesn't exist
- [ ] No skill step requires a tool (`gh`, `mvn`, etc.) without checking it's available
- [ ] Hook outputs are directive (ACTION REQUIRED) not just informational
- [ ] Hook doesn't fire on non-git directories
- [ ] No skill blocks progress without giving the user a way forward
- [ ] Error messages include recovery steps
- [ ] No redundant checks (same thing checked twice in the same flow)
- [ ] Skill chaining doesn't create infinite loops
- [ ] Exit codes in validators match what calling skills expect

**Refinement** — Could workflows be simpler or more intuitive?
- [ ] Are there steps that could be combined without losing clarity?
- [ ] Are any prompts or confirmations asked more times than necessary?
- [ ] Could any multi-step flow be reduced by inferring the answer from context?
- [ ] Are any error messages technical where plain language would serve the user better?

---

### `quality` — Skill Craft Quality

**Quality** — Are skills well-written and will they trigger and execute correctly?
- [ ] All descriptions start with "Use when..." (CSO compliance)
- [ ] No descriptions summarise the workflow (only trigger conditions)
- [ ] No first/second person in descriptions ("I", "you")
- [ ] All major skills have: Prerequisites (if layered), Common Pitfalls, Success Criteria
- [ ] Flowcharts use `flowchart TD` with semantic labels (not step1, step2)
- [ ] Flowcharts only used where decision points are non-obvious
- [ ] No skill is excessively long (rough budget: ~400 lines)
- [ ] Token-heavy content extracted to reference files where appropriate

**Refinement** — Could skills be made more concise or easier to follow?
- [ ] Are there skills where the workflow could be expressed in fewer steps without losing precision?
- [ ] Are any flowcharts earning their complexity, or would a numbered list be clearer?
- [ ] Could any Common Pitfalls rows be removed because they're obvious or never occur?
- [ ] Are there skills short enough to be absorbed into their caller?

---

### `naming` — Naming Consistency

**Quality** — Are names consistent across all the places they appear?
- [ ] Skill name in frontmatter matches directory name
- [ ] Skill name in marketplace.json matches directory name
- [ ] Command file named `commands/<skill-name>.md` (matches skill name)
- [ ] Skill name in README matches actual name
- [ ] No drift between any of the above
- [ ] New language skills follow established naming patterns (`lang-dev`, `lang-code-review`)

**Refinement** — Are names clear and discoverable, not just consistent?
- [ ] Would a new user guess the right skill name without reading the docs?
- [ ] Are any names technically accurate but unintuitive?
- [ ] Could any names better reflect what the skill does rather than its structural role?

---

### `dependencies` — Skill Dependencies

**Quality** — Do skill dependency chains actually work?
- [ ] All skills listed as Prerequisites exist
- [ ] No circular dependency chains (A depends on B depends on A)
- [ ] plugin.json dependency names match actual skill names
- [ ] Skills that build on others explicitly reference them in Prerequisites
- [ ] Marketplace dependency resolution would succeed for all skills

**Refinement** — Could dependency chains be simplified?
- [ ] Are any chains deeper than necessary (A→B→C where A→C suffices)?
- [ ] Could any skill with only one dependent be absorbed into that dependent?
- [ ] Are there optional dependencies that create complexity without commensurate value?

---

### `config` — Project Configuration Health

**Quality** — Is the project properly configured for its type?
- [ ] CLAUDE.md exists and has `## Project Type`
- [ ] Project type is one of: skills, java, blog, custom, generic
- [ ] For type: java — `docs/DESIGN.md` exists
- [ ] For type: custom — Sync Rules configured
- [ ] For type: blog — `_posts/` directory exists or is planned
- [ ] `## Commit Messages` section present (no-AI-attribution rule)
- [ ] `## Work Tracking` present if team collaboration is needed (advisory)
- [ ] `## Document Structure` threshold configured if doc nudge is desired

**Refinement** — Is the configuration easy to understand and maintain?
- [ ] Is CLAUDE.md overloaded with sections that could be removed or consolidated?
- [ ] Are any sections so rarely changed they could be documented once and simplified?
- [ ] Could the Sync Rules table (for type: custom) be expressed more concisely?

---

### `security` — Security & Safety

**Quality** — Are there security or safety issues in scripts and hooks?
- [ ] No hardcoded tokens, passwords, or API keys in any file
- [ ] Shell scripts quote variables to prevent word splitting
- [ ] No `rm -rf` without explicit path validation
- [ ] No `eval` of untrusted input
- [ ] Hook scripts have correct permissions (executable, not world-writable)
- [ ] No secrets in git history (check recent commits)
- [ ] Scripts validate inputs before acting on them

**Refinement** — Could scripts be made safer by being simpler?
- [ ] Are any scripts doing more than they need to (smaller attack surface = less code)?
- [ ] Could complex shell logic be replaced with Python that's easier to audit?
- [ ] Are permission checks and input validation in the most readable location?

---

### `infrastructure` — Tooling Infrastructure

**Quality** — Is the supporting infrastructure correct?
- [ ] All validators in `scripts/validation/` are wired into `validate_all.py`
- [ ] Each validator is in the correct tier (COMMIT: <2s, PUSH: <30s, CI: <5min)
- [ ] Session-start hook is registered in `~/.claude/settings.json`
- [ ] Hook script matches the template in `hooks/check_project_setup.sh`
- [ ] Generated files are in `.gitignore` (`*.pyc`, `skill.json`, `.doc-cache.json`)
- [ ] `scripts/claude-skill` installer correctly targets `~/.claude/skills/`

**Refinement** — Could the infrastructure be leaner or more maintainable?
- [ ] Are any two validators doing overlapping checks that could be merged?
- [ ] Are any validators in a higher tier than their speed justifies?
- [ ] Could any scripts be removed because the problem they solve no longer exists?

---

### `release` — Release Readiness

**Quality** — Is the project ready for a versioned release?
- [ ] No `SNAPSHOT` version suffixes in marketplace.json for release
- [ ] All skill versions consistent and intentional
- [ ] GitHub labels set up for release note generation
- [ ] `gh release create --generate-notes` would produce meaningful output
- [ ] RELEASE.md reflects current versioning strategy
- [ ] No obviously incomplete skills (stubs, empty sections)
- [ ] All tests passing

**Refinement** — Would the release be meaningful and well-presented?
- [ ] Would the generated release notes tell a coherent story?
- [ ] Are the GitHub issue titles good enough to serve as changelog entries?
- [ ] Could the versioning strategy be simplified (e.g. fewer SNAPSHOT states)?

---

### `user-journey` — End User Experience

**Quality** — Would a first-time user have a coherent experience?
- [ ] Installation path is documented and works (`/plugin marketplace add` → `/install-skills`)
- [ ] First commit flow is guided (CLAUDE.md created, project type set)
- [ ] Session-start hook provides helpful prompt on first open
- [ ] `/issue-workflow` offer is clear and skippable
- [ ] Error messages explain what went wrong and how to recover
- [ ] No dead ends (every failure state has a next step)
- [ ] Slash commands autocomplete correctly (`/java-git-commit`, etc.)

**Refinement** — Could the experience be faster or less friction-heavy?
- [ ] Could any required setup step be inferred or automated rather than prompted?
- [ ] Is the onboarding sequence longer than it needs to be?
- [ ] Are any optional prompts surfaced too early in the flow?

---

### `effectiveness` — Skill Effectiveness

**Quality** — Are skills correctly scoped and triggered?
- [ ] No two skills overlap significantly in purpose
- [ ] No skills with descriptions so generic they trigger on everything
- [ ] No skills with descriptions so specific they never trigger
- [ ] Obvious use cases for the project type are covered
- [ ] Skills that are never invoked (advisory — would need telemetry)

**Refinement** — Are skills as useful as they could be?
- [ ] Are any skills doing so little they'd be better absorbed into their caller?
- [ ] Are there common workflows requiring 3+ skills that could be wrapped in one?
- [ ] Could any skill description be sharpened to trigger more accurately?

---

### `git` — Repository State

**Quality** — Is the git repository in a healthy state?
- [ ] No uncommitted changes that should be committed
- [ ] No stale git worktrees
- [ ] Tags consistent with marketplace versions (for release)
- [ ] No merge conflict markers in tracked files
- [ ] Branch is up to date with remote

**Refinement** — Could the git workflow itself be simpler?
- [ ] Is the branching strategy more complex than the team size justifies?
- [ ] Could tag naming be more consistent or informative?
- [ ] Are there branches or worktrees that outlived their purpose?

---

### `performance` — Token & Runtime Performance

**Quality** — Are skills and validators within their budgets?
- [ ] No SKILL.md over ~400 lines (token budget)
- [ ] Validators in COMMIT tier run in <2s
- [ ] Validators in PUSH tier run in <30s
- [ ] No validator doing the same check as another (redundancy)

**Refinement** — Could things be made leaner without losing value?
- [ ] Is heavy reference material extracted to separate files?
- [ ] Is there duplicate content across skills inflating token cost on every load?
- [ ] Are there validators whose findings could fold into an existing validator?
- [ ] Are there skill sections that add length without adding guidance?

---

### `refine` — Improvement Opportunities

Unlike other categories, `refine` has no Quality dimension — everything here is a refinement opportunity in what already works. Findings are rated with a **bloat score** (see Output Format) to help prioritise.

**Documentation** — Could docs be better structured, smaller, or easier to read?
- [ ] Would a different grouping or ordering of sections improve navigation?
- [ ] Are there docs over ~400 lines with multiple distinct topics that would be clearer as separate linked files?
- [ ] Are there multiple small files covering closely related topics that would read better merged?
- [ ] Are there readability issues — passive voice, unexplained jargon, walls of text, sentences over 25 words?
- [ ] Are there sections that restate what was just said, or introductory paragraphs that add no information?
- [ ] Are there sections describing plans, history, or context that are no longer relevant?

**Code** — Could code be deduplicated, abstracted, or simplified?
- [ ] Are there the same blocks of logic appearing 3+ times? (high risk: fix one, miss others)
- [ ] Are there similar but not identical blocks that should be parameterised and shared?
- [ ] Are there functions over ~30 lines combining multiple distinct concerns?
- [ ] Are there literal values (strings, numbers, paths) repeated in multiple places?
- [ ] Are there repeated sequences of calls that always appear together and belong in a helper?
- [ ] Is there commented-out code? (remove it — git history preserves it)

**Tests** — Could tests be better grouped, modularised, or deduplicated?
- [ ] Are there tests for one feature spread across multiple files without clear ownership?
- [ ] Is the same fixture or arrangement code copy-pasted across multiple test methods?
- [ ] Are there test files over ~300 lines testing multiple unrelated concerns?
- [ ] Do test names follow a consistent pattern, making it easy to see what's covered?
- [ ] Would any tests benefit from being grouped into classes or modules?

**Universal bloat** — What is oversized or over-engineered across docs, code, and tests?
- [ ] Are there files >50% larger than the guideline for their type?
- [ ] Are there logic or document sections nested >3 levels deep that could be flattened?
- [ ] Are there functions with >4 parameters that could be grouped into a config object?
- [ ] Are there complex solutions for problems that have a simpler answer?
- [ ] Are there more comment lines than code lines explaining obvious things?

---

## Output Format

### Quality and other categories

Findings grouped by severity:

```
## project-health report — [categories run]

### CRITICAL (must fix)
- [docs-sync] docs/PROJECT-TYPES.md says blog-git-commit "not yet implemented" — it is
- [coverage] issue-workflow missing from README § Skill Chaining Reference

### HIGH (should fix)
- [cross-refs] git-commit description omits blog-git-commit routing

### MEDIUM (worth fixing)
- [naming] issue-workflow not in Workflow integrators section of CLAUDE.md

### LOW (nice to fix)
- [quality] issue-workflow SKILL.md is 287 lines — within budget but growing

### PASS
✅ consistency, security, infrastructure, release
```

---

### `refine` output — bloat score

Refinement findings are presented as **opportunities** not failures, rated on two axes:

**Size reduction potential:** 🔴 HIGH (>30% reduction possible) · 🟡 MEDIUM (10–30%) · 🟢 LOW (<10%)
**Impact of fixing:** A (navigation/readability/maintenance) · B (noticeable improvement) · C (cosmetic)

```
## refine — Opportunities Found

### 🔴A — High impact, significant size reduction
- scripts/validate_all.py (lines 45–89): run_validator() logic repeated
  for each tier; extract to a shared helper. Est. -40 lines.

### 🟡B — Medium impact
- update-primary-doc/SKILL.md (312 lines): Steps 4–7 cover two unrelated
  concerns; splitting would improve navigation. Est. -20 lines.

### 🟢C — Low impact, cosmetic
- java-dev/SKILL.md: "Code duplication" and "Code clarity" are adjacent
  and both cover style; could merge. Est. -5 lines.
```

---

## Commit-time Subset

Some checks are fast and important enough to run after every significant commit. The full set is TBD — marked here as a placeholder.

**Candidates:**
- `docs-sync` — "planned" language, wrong counts
- `cross-refs` — new chaining without bidirectional update
- `coverage` — new skill added but not integrated
- `naming` — skill name drift

**Not suitable for every commit:**
- `refine` — judgment-heavy, designed for periodic sessions
- `user-journey` — expensive
- `effectiveness` — subjective
- `git` — stateful
- `release` — milestone only

---

## Calling from Other Skills

When a skill needs a specific check, it references this skill rather than duplicating the check list:

```
After staging a new skill, run:
  python scripts/validate_all.py --tier commit

Or for a full integration check:
  /project-health coverage cross-refs naming
```

Skills that should reference project-health:
- `git-commit` — suggest `coverage` check when new SKILL.md staged
- Pre-commit checklist in CLAUDE.md — reference `project-health --defaults` before releases

---

## Open Questions

- [ ] Should checks be purely Claude-driven, or should more have Python validator scripts?
- [ ] Should `project-health` offer to auto-fix mechanical issues (counts, versions)?
- [ ] What is the commit-time subset? (TBD — see above)
- [ ] Should there be a `project-health --quick` that only runs the fastest checks?
- [ ] Should findings persist anywhere (a `.health-report.md`) or always ephemeral?
