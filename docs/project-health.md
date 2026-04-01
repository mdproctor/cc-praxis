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

# Run all categories
/project-health --all

# Run categories configured as default in CLAUDE.md
/project-health --defaults
```

---

## CLAUDE.md Configuration

Stored in `## Health Check Configuration` section:

```markdown
## Health Check Configuration

**Default checks:** docs-sync, cross-refs, consistency, coverage, quality
**Skip:** git, effectiveness
**Performance budget:** 400 lines max per SKILL.md
```

If no section is present, a built-in default set is used.

---

## Document Scanning Scope

When running any check that involves reading documentation, build the scan list in this order:

### 1. Universal baseline (always included)
- All `.md` files in the **project root**
- All `.md` files (recursive) in any folder named **`doc/`, `docs/`, or `documentation/`**

### 2. Inline documentation (always included)
Some projects keep docs alongside their code rather than in a central folder. Always scan:
- Any **`README.md`** anywhere in the directory tree (per-module, per-package docs)
- For Java: **`package-info.java`** and Javadoc comments in source files (for logic and docs-sync checks)
- Any **`CHANGELOG.md`**, `CONTRIBUTING.md`, `ARCHITECTURE.md`** found anywhere in the tree

### 3. Per project type (included automatically)

| Type | Additional scan targets |
|------|------------------------|
| `skills` | All `SKILL.md` files in repo root subdirectories |
| `java` | `pom.xml` / `build.gradle` (dependency and version checks); Javadoc in `src/` |
| `blog` | `_config.yml`, `_posts/`, `_layouts/`, `_includes/` |
| `custom` | The Primary Document path declared in CLAUDE.md |

### 4. User-configured locations (from CLAUDE.md)
Projects can declare additional documentation locations in `## Health Check Configuration`:

```markdown
## Health Check Configuration

**Additional doc paths:** src/main/resources/META-INF/, wiki/, design/
```

These are scanned in addition to the baseline — useful for projects where docs live in non-standard locations (generated resource files, wiki directories, architecture folders, etc.).

### 5. Non-markdown files (scanned where relevant)
- `.claude-plugin/marketplace.json` — skill registry and versions
- `hooks/` — hook scripts
- `scripts/` — what scripts actually do (for logic and docs-sync checks)
- `tests/` — what is tested (for coverage and code checks)

**Principle:** scan broadly rather than miss a stale reference. If a file is irrelevant, the check simply finds nothing of interest there.

---

## Category Overview

**Type key:** Mechanical — scriptable, low ambiguity · Judgment — Claude must reason about intent or UX · Mixed — some of each

---

### Universal Checks
*Apply to every project type. The specific items within a category may vary by type — see per-type notes below.*

| Category | What it covers | Checks | Type | When to run |
|----------|---------------|--------|------|-------------|
| `docs-sync` | Code matches docs, no stale/planned language, correct counts, correct URLs | 7 | Mechanical | Every commit, pre-release |
| `consistency` | Contradictions between docs, duplicated information, terminology drift | 6 | Judgment | Pre-release, deep review |
| `logic` | Workflows executable, UX friction, redundant checks, error messages have recovery steps | 8 | Judgment | Pre-release, deep review |
| `config` | CLAUDE.md exists, project type declared, required sections present for that type | 8 | Mechanical | On setup, pre-release |
| `security` | No hardcoded secrets, safe shell patterns, correct permissions on scripts | 6 | Mechanical | Pre-release |
| `release` | Versions consistent, release notes will be meaningful, RELEASE.md current | 7 | Mixed | Release only |
| `user-journey` | Onboarding coherent, errors have recovery steps, no dead ends | 6 | Judgment | Pre-release, major changes |
| `git` | Clean working tree, no stale worktrees, tags match versions | 5 | Mechanical | On demand |

---

### type: skills
*Additional checks that only apply to skill collection repositories.*

| Category | What it covers | Checks | Type | When to run |
|----------|---------------|--------|------|-------------|
| `cross-refs` | Bidirectional skill chaining, chaining table complete, all references resolve | 6 | Mechanical | Every commit |
| `coverage` | New skills in marketplace + README + commands/ + chaining table | 6 | Mechanical | Every commit |
| `quality` | CSO compliance, required skill sections, flowchart syntax, token budget | 8 | Mixed | Pre-release |
| `naming` | Skill name consistent across directory, frontmatter, marketplace, README, commands/ | 5 | Mechanical | Every commit |
| `infrastructure` | All validators wired into validate_all.py at correct tier, hook registered, gitignore | 6 | Mechanical | Pre-release |
| `dependencies` | Skill prerequisites exist, no circular chains, plugin.json versions consistent | 5 | Mechanical | Pre-release |
| `performance` | SKILL.md within token budget (~400 lines), heavy content extracted to reference files | 5 | Mixed | Pre-release |
| `effectiveness` | No redundant skills, descriptions specific enough to trigger correctly | 5 | Judgment | Deep review only |

---

### type: java
*Additional items within universal categories that apply to Java/Maven/Gradle projects.*

| Category | Extra items |
|----------|------------|
| `docs-sync` | DESIGN.md exists and reflects current architecture; no stale entity/service references |
| `config` | `docs/DESIGN.md` present (java-git-commit blocks without it); BOM strategy documented |
| `logic` | No blocking JDBC on Vert.x event loop in code examples; @Blocking annotations correct |

---

### type: blog
*Additional items within universal categories that apply to GitHub Pages / Jekyll blogs.*

| Category | Extra items |
|----------|------------|
| `docs-sync` | Post filenames follow `YYYY-MM-DD-title.md` convention; no broken Jekyll front matter |
| `config` | `_posts/` directory exists; `_config.yml` present; Jekyll conventions documented in CLAUDE.md |
| `quality` | Blog commit messages use valid types (post/edit/draft/asset/config); 72-char subject limit |

---

### type: custom
*Additional items within universal categories that apply to custom projects.*

| Category | Extra items |
|----------|------------|
| `config` | Sync Rules table configured in CLAUDE.md; Primary Document path exists; milestone current |
| `docs-sync` | Primary document reflects current project state; sync rules still match actual file structure |

---

### Suggested Invocation Groups

| Group | Categories | Use when |
|-------|-----------|----------|
| `--commit` | `docs-sync`, `cross-refs`*, `coverage`*, `naming`* | Fast checks after every significant change |
| `--prerelease` | All mechanical + mixed categories for the project type | Before tagging a release |
| `--deep` | All categories for the project type | Periodic deep review, after major refactors |
| `--setup` | `config`, `infrastructure`*, `coverage`* | After initial project setup |

*\* type: skills only — skipped automatically for other project types*

---

## Check Categories

### `docs-sync` — Documentation Accuracy
> Does documentation accurately reflect the current state of the code?

- [ ] Code behaviour matches what docs describe
- [ ] No "planned" / "not yet implemented" language for things that exist
- [ ] Skill counts and validator counts are correct everywhere
- [ ] Version numbers consistent (marketplace.json, plugin.json, docs)
- [ ] URLs and GitHub repo references are correct
- [ ] No stale "TODO" or "coming soon" references
- [ ] Release status language matches actual state

---

### `cross-refs` — Cross-Reference Integrity
> Are all the links between skills and documents complete and bidirectional?

- [ ] Every skill mentioned in the chaining table exists
- [ ] Chaining is bidirectional where required (A→B means B mentions A)
- [ ] Skill Chaining Reference table covers all skills including new additions
- [ ] Skill A says it chains to B, and B says it is invoked by A
- [ ] Prerequisites sections reference skills that exist
- [ ] All markdown links to other `.md` files resolve

---

### `consistency` — Internal Consistency
> Does everything agree with itself?

- [ ] No contradictions between any two documents on the same topic
- [ ] No duplicate information that could drift (same content in 2+ places)
- [ ] Section naming conventions followed (Skill Chaining, not Skill chaining)
- [ ] Common Pitfalls tables use consistent column format
- [ ] Severity levels (CRITICAL/WARNING/NOTE) used consistently
- [ ] Terminology is consistent (e.g. "invoke" not mixed with "call" or "use")

---

### `coverage` — Integration Coverage
> Are new skills and features fully wired into the broader system?

- [ ] Every skill has a `commands/<skill-name>.md` slash command file
- [ ] Every skill is in `.claude-plugin/marketplace.json` plugins list
- [ ] Every skill appears in README.md § Skills section
- [ ] New skills appear in README.md § Skill Chaining Reference table
- [ ] New skills appear in CLAUDE.md § Key Skills
- [ ] Every validator is wired into `scripts/validate_all.py` at the correct tier
- [ ] New project types added to all required locations (validate_project_types catches this)

---

### `logic` — Workflow Logic & UX
> Do the described workflows actually work? Is the UX reasonable?

- [ ] No skill step references a script that doesn't exist
- [ ] No skill step requires a tool (`gh`, `mvn`, etc.) without checking it's available
- [ ] Hook outputs are directive (ACTION REQUIRED) not just informational
- [ ] Hook doesn't fire on non-git directories
- [ ] No skill blocks progress without giving the user a way forward
- [ ] Error messages include recovery steps
- [ ] No redundant checks (same thing checked twice in the same flow)
- [ ] Skill chaining doesn't create infinite loops
- [ ] Exit codes in validators match what calling skills expect

---

### `quality` — Skill Craft Quality
> Are skills well-written and will they trigger and execute correctly?

- [ ] All descriptions start with "Use when..." (CSO compliance)
- [ ] No descriptions summarise the workflow (only trigger conditions)
- [ ] No first/second person in descriptions ("I", "you")
- [ ] All major skills have: Prerequisites (if layered), Common Pitfalls, Success Criteria
- [ ] Flowcharts use `flowchart TD` with semantic labels (not step1, step2)
- [ ] Flowcharts only used where decision points are non-obvious
- [ ] No skill is excessively long (rough budget: ~400 lines)
- [ ] Token-heavy content extracted to reference files where appropriate

---

### `naming` — Naming Consistency
> Are names consistent across all the places they appear?

- [ ] Skill name in frontmatter matches directory name
- [ ] Skill name in marketplace.json matches directory name
- [ ] Command file named `commands/<skill-name>.md` (matches skill name)
- [ ] Skill name in README matches actual name
- [ ] No drift between any of the above
- [ ] New language skills follow established naming patterns (`lang-dev`, `lang-code-review`)

---

### `dependencies` — Skill Dependencies
> Do skill dependency chains actually work?

- [ ] All skills listed as Prerequisites exist
- [ ] No circular dependency chains (A depends on B depends on A)
- [ ] plugin.json dependency names match actual skill names
- [ ] Skills that build on others explicitly reference them in Prerequisites section
- [ ] Marketplace dependency resolution would succeed for all skills

---

### `config` — Project Configuration Health
> Is the project properly configured for its type?

- [ ] CLAUDE.md exists and has `## Project Type`
- [ ] Project type is one of: skills, java, blog, custom, generic
- [ ] For type: java — `docs/DESIGN.md` exists
- [ ] For type: custom — Sync Rules configured
- [ ] For type: blog — `_posts/` directory exists or is planned
- [ ] `## Commit Messages` section present (no-AI-attribution rule)
- [ ] `## Work Tracking` present if team collaboration is needed (advisory)
- [ ] `## Document Structure` threshold configured if doc nudge is desired

---

### `security` — Security & Safety
> Are there security or safety issues in scripts and hooks?

- [ ] No hardcoded tokens, passwords, or API keys in any file
- [ ] Shell scripts quote variables to prevent word splitting
- [ ] No `rm -rf` without explicit path validation
- [ ] No `eval` of untrusted input
- [ ] Hook scripts have correct permissions (executable, not world-writable)
- [ ] No secrets in git history (check recent commits)
- [ ] Scripts validate inputs before acting on them

---

### `infrastructure` — Tooling Infrastructure
> Is the supporting infrastructure correct?

- [ ] All validators in `scripts/validation/` are wired into `validate_all.py`
- [ ] Each validator is in the correct tier (COMMIT: <2s, PUSH: <30s, CI: <5min)
- [ ] Session-start hook is registered in `~/.claude/settings.json`
- [ ] Hook script matches the template in `hooks/check_project_setup.sh`
- [ ] Generated files are in `.gitignore` (`*.pyc`, `skill.json`, `.doc-cache.json`)
- [ ] `scripts/claude-skill` installer correctly targets `~/.claude/skills/`

---

### `release` — Release Readiness
> Is the project ready for a versioned release?

- [ ] No `SNAPSHOT` version suffixes in marketplace.json for release
- [ ] All skill versions consistent and intentional
- [ ] GitHub labels set up for release note generation
- [ ] `gh release create --generate-notes` would produce meaningful output
- [ ] RELEASE.md reflects current versioning strategy
- [ ] No obviously incomplete skills (stubs, empty sections)
- [ ] All tests passing

---

### `user-journey` — End User Experience
> Would a first-time user have a coherent experience?

- [ ] Installation path is documented and works (`/plugin marketplace add` → `/install-skills`)
- [ ] First commit flow is guided (CLAUDE.md created, project type set)
- [ ] Session-start hook provides helpful prompt on first open
- [ ] `/issue-workflow` offer is clear and skippable
- [ ] Error messages explain what went wrong and how to recover
- [ ] No dead ends (every failure state has a next step)
- [ ] Slash commands autocomplete correctly (`/java-git-commit`, etc.)

---

### `effectiveness` — Skill Effectiveness
> Are skills actually useful and correctly scoped?

- [ ] No two skills overlap significantly in purpose
- [ ] No skills with descriptions so generic they'll trigger on everything
- [ ] No skills with descriptions so specific they'll never trigger
- [ ] Obvious use cases for the project type are covered
- [ ] Skills that are never invoked (would need telemetry — advisory check only)

---

### `git` — Repository State
> Is the git repository in a healthy state?

- [ ] No uncommitted changes that should be committed
- [ ] No stale git worktrees
- [ ] Tags consistent with marketplace versions (for release)
- [ ] No merge conflict markers in tracked files
- [ ] Branch is up to date with remote

---

### `performance` — Token & Runtime Performance
> Are skills and validators appropriately sized?

- [ ] No SKILL.md over ~400 lines (token budget)
- [ ] Heavy reference material extracted to separate files
- [ ] No duplicate content that inflates token cost
- [ ] Validators in COMMIT tier run in <2s
- [ ] Validators in PUSH tier run in <30s
- [ ] No validator doing the same check as another (redundancy)

---

## Output Format

Findings grouped by severity, then by category:

```
## project-health report

### CRITICAL (must fix)
- [docs-sync] docs/PROJECT-TYPES.md says blog-git-commit is "not yet implemented" — it is
- [coverage] issue-workflow missing from README § Skill Chaining Reference

### HIGH (should fix)
- [cross-refs] git-commit description omits blog-git-commit routing

### MEDIUM (worth fixing)
- [naming] issue-workflow not in Workflow integrators section of CLAUDE.md

### LOW (nice to fix)
- [quality] issue-workflow SKILL.md is 287 lines — within budget but growing

### PASS (no issues)
✅ frontmatter, consistency, security, infrastructure, release
```

---

## Commit-time Subset (to define later)

Some checks are fast enough and important enough to run on every commit. This subset is TBD — marked here as a placeholder.

**Candidates for commit-time subset:**
- `coverage` — new skill added but not integrated
- `cross-refs` — new chaining without bidirectional update
- `naming` — skill name drift
- `docs-sync` — "planned" language, wrong counts

**Not suitable for every commit:**
- `user-journey` — expensive, judgment-heavy
- `effectiveness` — subjective
- `git` — stateful
- `release` — only relevant at milestone time

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
- [ ] Should findings persist anywhere (a `.health-report.md` file) or always ephemeral?
