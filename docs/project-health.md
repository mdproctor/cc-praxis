# project-health — Design Document

**Status:** Design phase — not yet implemented as a skill
**Skill name (planned):** `project-health`
**Slash command (planned):** `/project-health`
**Companion skill:** [`project-refine`](project-refine.md) — dedicated improvement and bloat reduction
**Type-specific skills:** [`java-project-health`](java-project-health.md) · [`blog-project-health`](blog-project-health.md) · [`custom-project-health`](custom-project-health.md) · [`skills-project-health`](skills-project-health.md)

This document tracks the design and scope of the `project-health` skill. It is a working document — update it as the skill evolves.

---

## Purpose

Answers the question: **is the project correct, complete, and consistent?**

`project-health` covers the **universal checks** that apply to every project type. It is **bidirectionally chained** with type-specific health skills — it routes *to* them for additional checks, and they invoke it as their prerequisite foundation. This is the same pattern as `git-commit` ↔ `java-git-commit`, `blog-git-commit`, and `custom-git-commit`.

This bidirectional design keeps each skill focused and composable: `project-health` is truly universal, type-specific skills contain only what is specific to their type, and you can invoke either end of the chain — `/project-health` runs everything for your project type, or `/java-project-health` can be invoked directly and will include the universal checks automatically.

It replaces:
- "make sure docs and code are in sync"
- "check for duplications, conflicts, gaps"
- "look for potential bugs or poor UX"
- pre-release system reviews

Other skills can reference specific check categories when they need things verified.

---

## Routing

After running universal checks, `project-health` **automatically chains to** the type-specific skill based on `## Project Type` in CLAUDE.md — in the same session, with output combined:

| Project type | Auto-chains to |
|---|---|
| `java` | [`java-project-health`](java-project-health.md) |
| `blog` | [`blog-project-health`](blog-project-health.md) |
| `custom` | [`custom-project-health`](custom-project-health.md) |
| `skills` | [`skills-project-health`](skills-project-health.md) |
| `generic` | No chaining — universal checks only |

**How it works:**
1. `project-health` reads `## Project Type` from CLAUDE.md — **this happens first, before any checks run**
2. Runs all universal check categories — type context is now available, so type-sensitive checks (`primary-doc`, `artifacts`, `conventions`, `framework`) know what to look for for this project type
3. Automatically invokes the type-specific skill in the same session
4. Output is combined into one unified report

**Why type-sensitive universal checks work:** `primary-doc`, `artifacts`, `conventions`, and `framework` are universal in *structure* but type-aware in *content* — they ask the same questions for every project but apply them to the correct artifacts for the detected type. Because type detection is always step 1, these checks always have the context they need.

**Two valid entry points, same result:**
- `/project-health` — universal entry point, auto-chains to type-specific. Use this when you don't know or don't care which type-specific skill applies.
- `/java-project-health` — type-specific entry point, runs universal checks as its prerequisite first, then its own. Use this when you know you're working on a Java project.

Both produce identical output. Neither redirects the user to run a second command.

---

## Relationship with project-refine

`project-health` and [`project-refine`](project-refine.md) are companion skills designed to work together:

| | `project-health` | `project-refine` |
|--|-----------------|-----------------|
| **Question** | Is it correct? | Could it be better? |
| **Output** | CRITICAL / HIGH / MEDIUM / LOW findings | 🔴🟡🟢 bloat score opportunities |
| **Mindset** | Pass / fail | Improvement suggestions |
| **Runs at** | Every commit (subset), pre-release, on demand | Periodic sessions, on demand |
| **Blocks work?** | CRITICAL findings should block release | Never blocks — always advisory |
| **Refinement notes** | ✅ Within each category (domain-specific) | ✅ Across docs, code, and tests |

**Using them together:**

```bash
# 1. Verify correctness first
/project-health --prerelease

# 2. Once health is green, look for improvement opportunities
/project-refine

# Or run both in sequence for a full review
/project-health --all
/project-refine
```

The refinement questions within each `project-health` category (e.g. "could `docs-sync` be improved?") are domain-specific — they belong in `project-health` because they're refinement considerations *about a specific correctness domain*. General improvement work (docs restructuring, code and test deduplication, bloat reduction) belongs in `project-refine` because it cuts across domains and requires a different mindset.

**Shared infrastructure:** both skills use the same document scanning scope, CLAUDE.md configuration section, and project type awareness. Running one does not duplicate work done by the other.

---

## Invocation

```bash
# Interactive — presents menu of categories to select
/project-health

# Run specific categories
/project-health docs-sync consistency

# Run all categories for this project type
/project-health --all

# Run categories configured as default in CLAUDE.md
/project-health --defaults

# Predefined groups (see Suggested Invocation Groups)
/project-health --commit
/project-health --prerelease
/project-health --setup

# For improvement and bloat reduction, use the companion skill
/project-refine
```

---

## CLAUDE.md Configuration

Stored in `## Health Check Configuration`:

```markdown
## Health Check Configuration

**Default checks:** docs-sync, consistency, logic, config, primary-doc
**Skip:** git, user-journey
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

### 3. Type-specific scan targets

Each type-specific health skill defines its own additional scan targets — source files, config files, and project-specific directories relevant to that type. See each skill's document for details:
- [`java-project-health`](java-project-health.md) — `pom.xml`, `build.gradle`, Javadoc in `src/`
- [`blog-project-health`](blog-project-health.md) — `_config.yml`, `_posts/`, `_layouts/`, `_includes/`
- [`skills-project-health`](skills-project-health.md) — all `SKILL.md` files in repo root subdirectories
- [`custom-project-health`](custom-project-health.md) — the Primary Document path declared in CLAUDE.md

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

*Apply to every project type. Type-specific augmentations are handled by the routed type-specific skill.*

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
| `primary-doc` | Project's designated primary document is accurate and current | Could it be better structured or modularised? | Mixed | Pre-release, deep review |
| `artifacts` | All required primary artifacts for this project type exist | Are any required artifacts over-complicated? | Mechanical | On setup, pre-release |
| `conventions` | Project conventions are documented in CLAUDE.md and followed | Could conventions be expressed more concisely? | Mixed | Pre-release |
| `framework` | Documented patterns and examples are correct for the project's framework | Could framework guidance be simplified? | Judgment | Pre-release, deep review |
| *(see project-refine)* | — | Docs structure, code deduplication (including tests), universal bloat — handled by [`project-refine`](project-refine.md) | Judgment | On demand, periodic |

---

*Type-specific checks (java, blog, custom, skills) are documented in their respective skills — see [Routing](#routing) above.*

### Suggested Invocation Groups

| Group | Categories | Use when |
|-------|-----------|----------|
| `--commit` | `docs-sync`, `cross-refs`*, `coverage`*, `naming`* | Fast checks after every significant change |
| `--prerelease` | All mechanical + mixed categories for the project type | Before tagging a release |
| `--deep` | All categories for the project type | Periodic deep review, after major refactors |
| `--setup` | `config`, `artifacts`, `infrastructure`*, `coverage`* | After initial project setup |

*\* type: skills only — skipped automatically for other project types*

For dedicated improvement sessions, use [`/project-refine`](project-refine.md).

---

## Check Categories

Each category below covers both **Quality** (is it correct?) and **Refinement** (could it be better?). Quality items are declarative pass/fail checks. Refinement items are judgment questions — there is no single right answer.

---

### `docs-sync` — Documentation Accuracy

**Quality** — Does documentation accurately reflect the current state of the code?
- [ ] Code behaviour matches what docs describe
- [ ] No "planned" / "not yet implemented" language for things that exist
- [ ] Component and artifact counts are correct everywhere they are stated
- [ ] Version numbers consistent across all places they appear
- [ ] URLs and external references are correct and reachable
- [ ] No stale "TODO" or "coming soon" references
- [ ] Release status language matches actual state
- [ ] Temporal claims are still accurate ("as of Q1 2026", "in the last 6 months")
- [ ] Code examples and output samples match what the code actually produces
- [ ] Environment variable names, config keys, and file paths match the actual source exactly

**Refinement** — Could the documentation communicate the same information more effectively?
- [ ] Are there over-explained sections where the code is self-evident?
- [ ] Is the detail level appropriate for the intended audience?
- [ ] Could any prose be replaced with a table or example that's easier to scan?
- [ ] Are there sections whose purpose overlaps enough to merge?

---

### `consistency` — Internal Consistency

**Quality** — Does everything agree with itself?
- [ ] No contradictions between any two documents on the same topic
- [ ] No duplicate information that could drift (same content in 2+ places)
- [ ] Section naming conventions are followed consistently throughout
- [ ] Recurring structural elements (tables, lists, headings) use consistent formatting
- [ ] Severity levels (CRITICAL/WARNING/NOTE) used consistently
- [ ] Terminology is consistent (e.g. "invoke" not mixed with "call" or "use")
- [ ] The same concept is named the same way across all audience levels (novice and architecture docs agree on terms)

**Refinement** — Could duplicated or scattered information be consolidated?
- [ ] Could scattered terminology be unified in a glossary or shared reference?
- [ ] Are there sections that say the same thing in different words that should be merged?
- [ ] Could inconsistent formatting be standardised to reduce cognitive load?

---

### `logic` — Workflow Logic & UX

**Quality** — Do the described workflows actually work?
- [ ] No workflow step references a script or file that doesn't exist
- [ ] No workflow step requires an external tool (`gh`, `mvn`, etc.) without verifying it's installed
- [ ] Hook outputs are directive (ACTION REQUIRED) not just informational
- [ ] Hook doesn't fire on non-git directories
- [ ] No workflow blocks progress without giving the user a way forward
- [ ] Error messages include recovery steps
- [ ] No redundant checks (same thing checked twice in the same flow)
- [ ] Chained workflows don't create infinite loops
- [ ] Exit codes are consistent and documented
- [ ] Workflow steps that require user judgment specify clear decision criteria (not "do what makes sense")
- [ ] Ordered workflows document what happens if steps are skipped or reordered

**Refinement** — Could workflows be simpler or more intuitive?
- [ ] Are there steps that could be combined without losing clarity?
- [ ] Are any prompts or confirmations asked more times than necessary?
- [ ] Could any multi-step flow be reduced by inferring the answer from context?
- [ ] Are any error messages technical where plain language would serve the user better?

---

### `config` — Project Configuration Health

**Quality** — Is the project properly configured for its type?
- [ ] CLAUDE.md exists and has `## Project Type`
- [ ] Project type is one of: skills, java, blog, custom, generic
- [ ] Required primary artifacts for the project type exist (see type-specific skills for details)
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
- [ ] All executable scripts have correct permissions (executable for owner, not world-writable) — not just hooks
- [ ] No secrets in git history (check recent commits)
- [ ] Scripts validate inputs before acting on them
- [ ] External tool dependencies are documented or checked before use (PATH assumptions are explicit)
- [ ] Scripts that write files check the target directory exists before writing
- [ ] Relative paths in scripts work correctly regardless of the working directory the script is called from

**Refinement** — Could scripts be made safer by being simpler?
- [ ] Are any scripts doing more than they need to (smaller attack surface = less code)?
- [ ] Could complex shell logic be replaced with Python that's easier to audit?
- [ ] Are permission checks and input validation in the most readable location?

---

### `release` — Release Readiness

**Quality** — Is the project ready for a versioned release?
- [ ] No version markers indicating work-in-progress (SNAPSHOT, dev, alpha) in release artifacts
- [ ] All component versions consistent and intentional
- [ ] GitHub labels set up for release note generation
- [ ] `gh release create --generate-notes` would produce meaningful output
- [ ] Release strategy documentation reflects current approach
- [ ] No obviously incomplete components (stubs, empty sections, placeholder content)
- [ ] All tests passing
- [ ] Release notes actually reference the issues or PRs being released (not just a version number bump)
- [ ] Release notes don't claim fixes or features that aren't in this release

**Refinement** — Would the release be meaningful and well-presented?
- [ ] Would the generated release notes tell a coherent story?
- [ ] Are the GitHub issue titles good enough to serve as changelog entries?
- [ ] Could the versioning strategy be simplified (e.g. fewer SNAPSHOT states)?

---

### `user-journey` — End User Experience

**Quality** — Would a first-time user have a coherent experience?
- [ ] Getting started path is documented and works end-to-end
- [ ] First meaningful action (first commit, first build, etc.) is guided
- [ ] Setup prompts are clear and skippable where optional
- [ ] Error messages explain what went wrong and how to recover
- [ ] No dead ends (every failure state has a next step)
- [ ] Entry points (commands, slash commands, scripts) work as documented
- [ ] Getting started has been validated from a fresh environment, not just the developer's pre-configured machine
- [ ] Documented error recovery steps actually resolve the stated error (not generic troubleshooting)

**Refinement** — Could the experience be faster or less friction-heavy?
- [ ] Could any required setup step be inferred or automated rather than prompted?
- [ ] Is the onboarding sequence longer than it needs to be?
- [ ] Are any optional prompts surfaced too early in the flow?

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

### `primary-doc` — Primary Document Accuracy

Every project type has a designated primary document. This check verifies it is accurate and current regardless of what that document is.

**Quality** — Does the primary document accurately reflect the current state of the project?
- [ ] The primary document exists (type-specific — see augmentation table)
- [ ] Content accurately describes what the project currently does, not what was planned
- [ ] No sections describe features, architecture, or workflows that no longer exist
- [ ] Referenced files, paths, and modules within the document still exist
- [ ] Terminology matches what is actually used in the codebase

**Refinement** — Could the primary document be better structured or more useful?
- [ ] Is the document an appropriate size, or should it be split into focused modules?
- [ ] Are there sections so rarely updated they've become stale noise?
- [ ] Could the structure be reorganised to match how readers actually navigate it?
- [ ] Are there sections that duplicate information found in other documents?

\*Type-specific augmentations: handled by the routed type-specific skill.\*

---

### `artifacts` — Required Artifacts Exist

Every project type has required primary artifacts. This check verifies they are all present without knowing in advance what they are — the project type determines the list.

**Quality** — Do all required primary artifacts for this project type exist?
- [ ] All required files and directories exist (type-specific — see augmentation table)
- [ ] Required configuration files are present and parseable
- [ ] Any artifact referenced in CLAUDE.md actually exists at the declared path
- [ ] No required artifact is empty, stubbed, or contains only placeholder content
- [ ] No required artifact appears abandoned (no updates for unexpectedly long period given project activity)

**Refinement** — Are the required artifacts appropriate in scope?
- [ ] Is any required artifact significantly larger than it needs to be?
- [ ] Are there required artifacts that have become redundant and could be retired?
- [ ] Could any required artifacts be combined without losing their purpose?

\*Type-specific augmentations: handled by the routed type-specific skill.\*

---

### `conventions` — Conventions Declared and Followed

Every project type has conventions — commit formats, file naming rules, coding standards. This check verifies they are documented and the project adheres to them.

**Quality** — Are project conventions documented and followed?
- [ ] Project-specific conventions are documented in CLAUDE.md (or a referenced doc)
- [ ] Commit messages follow the declared conventions for this project type
- [ ] File naming follows the declared conventions (type-specific — see augmentation table)
- [ ] No convention is documented but never followed, or followed but never documented
- [ ] Conventions referenced in skill/workflow documentation match what's actually enforced
- [ ] Declared conventions that can be enforced automatically are enforced by tooling or validators (not just documented hope)

**Refinement** — Could conventions be expressed more clearly or concisely?
- [ ] Are any conventions so obvious they don't need documentation?
- [ ] Are any conventions so complex they suggest the underlying approach should simplify?
- [ ] Could related conventions be grouped for easier reference?
- [ ] Are there conventions that conflict with each other subtly?

\*Type-specific augmentations: handled by the routed type-specific skill.\*

---

### `framework` — Framework-Specific Pattern Correctness

Every project uses a framework with specific patterns. This check verifies that documented examples, code patterns, and workflow guidance are correct for the declared framework — not just generically correct.

**Quality** — Are documented patterns correct for this project's framework?
- [ ] Code examples in docs use patterns that are correct for the declared framework
- [ ] Documented workflows account for framework-specific constraints
- [ ] No guidance recommends an approach the framework explicitly discourages
- [ ] Framework-specific annotations, decorators, or conventions are used correctly in examples
- [ ] Patterns are current for the version of the framework in use

**Refinement** — Could framework guidance be more focused or easier to apply?
- [ ] Is framework-specific guidance scattered or consolidated where it's easy to find?
- [ ] Are there framework patterns documented that are never actually used in the project?
- [ ] Could framework guidance link to authoritative external docs rather than re-explaining concepts?

\*Type-specific augmentations: handled by the routed type-specific skill.\*

---

## Output Format

Findings grouped by severity:

```
## project-health report — [categories run]

### CRITICAL (must fix)
- [docs-sync] docs/architecture.md describes a caching layer that was removed 6 months ago
- [artifacts] Primary Document path declared in CLAUDE.md does not exist

### HIGH (should fix)
- [conventions] Commit messages use 'feat:' but project declared 'post:' as the convention

### MEDIUM (worth fixing)
- [config] CLAUDE.md missing ## Commit Messages section (no-AI-attribution rule)

### LOW (nice to fix)
- [docs-sync] README version number (v1.2) doesn't match RELEASE.md (v1.3)

### PASS
✅ consistency, security, git, user-journey, release
```

For improvement opportunities and bloat scoring, see [`project-refine`](project-refine.md) — its output format uses 🔴🟡🟢 bloat scores rather than severity ratings.

---

## Commit-time Subset

Some checks are fast and important enough to run after every significant commit. The full set is TBD — marked here as a placeholder.

**Candidates for universal commit subset:**
- `docs-sync` — "planned" language, wrong counts, stale references
- `config` — CLAUDE.md missing required sections
- `artifacts` — required artifact deleted or moved
- `conventions` — undocumented convention in use

**Candidates for type-specific commit subset:**
- Defined by each type-specific skill (e.g. `cross-refs`, `coverage`, `naming` in `skills-project-health`)

**Not suitable for every commit:**
- `user-journey` — expensive, judgment-heavy
- `framework` — expensive, requires code analysis
- `git` — stateful
- `release` — milestone only

---

## Calling from Other Skills

When a skill needs a specific check, it references this skill rather than duplicating the check list:

```
# After significant changes, run a full pre-release check
/project-health --prerelease

# Or target specific categories
/project-health docs-sync conventions
```

Skills and workflows that should reference project-health:
- Any commit skill (`git-commit`, `java-git-commit`, etc.) — can suggest `/project-health --commit` subset after commits that affect documentation
- Pre-commit checklist in CLAUDE.md — reference `project-health --prerelease` before releases
- Type-specific health skills — invoke `project-health` as their prerequisite

---

## Implementation Decisions

**Q1 — Claude-driven or Python validators?**
Both, in sequence. First run `python scripts/validate_all.py --tier commit` to catch everything scriptable mechanically. Then Claude handles judgment checks the scripts can't do (logic, user-journey, conventions, framework, etc.). This reuses existing infrastructure and keeps fast checks fast.

**Q2 — Auto-fix mechanical issues?**
Yes, with confirmation — same pattern as git-commit (propose → user YES → apply). Mechanical fixes (wrong count in README, missing `commands/<name>.md`, stale version number) are offered automatically. Judgment calls are never auto-fixed. Opt-in per run, not the default.

**Q3 — Commit-time subset**
The `--commit` group runs `validate_all.py --tier commit` followed by quick universal checks (docs-sync, config, artifacts) that aren't already covered by the validators. No finer breakdown needed.

**Q4 — `--quick` flag**
Not needed — `--commit` already serves this purpose. Dropped.

**Q5 — Findings persistence**
Default: ephemeral. Optional: pass `--save` to write a date-prefixed report file (`YYYY-MM-DD-health-report.md`) so multiple runs don't overwrite each other. The file is gitignored by default. Useful for sharing findings in a PR or discussing with the team.

```bash
# Save report with date prefix (e.g. 2026-04-02-health-report.md)
/project-health --prerelease --save
```
