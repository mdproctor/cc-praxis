# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a skill collection for Claude Code, providing specialized guidance for Java/Quarkus development workflows. Skills are markdown files with YAML frontmatter that Claude Code loads to execute specific development tasks.

## Project Type

**Type:** skills

## Project Type Awareness

**CRITICAL: Skills must handle different project types with appropriate workflows.**

This repository follows the **type: skills** project model. All repositories using these skills declare their type in CLAUDE.md to enable appropriate commit workflows, documentation sync, and validation.

### The Four Project Types

Claude Code supports 4 project types, each with tailored behaviors:

| Type | Description | Sync Behavior | When to Use |
|------|-------------|---------------|-------------|
| **`skills`** | Skills repository | Built-in (we know how skills work) | This repository |
| **`java`** | Java/Maven/Gradle | Built-in (we know Java architecture patterns) | Java projects |
| **`custom`** | User-configured | User defines sync strategy | Everything else with special needs |
| **`generic`** | No special handling | Basic conventional commits | Simple projects, no sync needed |

**For this repository:**
- Type: **skills**
- Built-in validation: SKILL.md frontmatter, CSO compliance, cross-references
- Built-in sync: README.md (readme-sync.md), CLAUDE.md (update-claude-md)
- Workflow: git-commit → skill-review → readme-sync.md → update-claude-md → commit

### Complete Project Type Reference

**For comprehensive documentation on all project types, including:**
- Why these four types exist (architectural insight)
- Type 1: Skills Repository (Built-in) — this repository's detailed behavior
- Type 2: Java/Maven/Gradle (Built-in) — DESIGN.md sync, BOM patterns
- Type 3: Custom (User-Configured) — working groups, research, docs
- Type 4: Generic (Fallback) — simple projects
- Decision matrix: When to create a new built-in type
- Routing logic and interactive setup
- Adding support for new domains (Python, Go, etc.)

**See:** 📖 **[docs/PROJECT-TYPES.md](docs/PROJECT-TYPES.md)**

The remainder of this document focuses on **type: skills** specific guidance.

## Skill Architecture

### Frontmatter Requirements

Every `SKILL.md` requires YAML frontmatter with exactly two fields:

```yaml
---
name: skill-name-with-hyphens
description: >
  Use when [specific triggering conditions and symptoms]
---
```

**Critical: Claude Search Optimization (CSO)**

The `description` field determines when Claude loads the skill. Follow these rules:

- **Start with "Use when..."** to focus on triggering conditions
- **NEVER summarize the skill's workflow** in the description
- Describe the *problem* or *symptoms*, not the solution
- Keep under 500 characters if possible
- Third person only (no "I" or "you")

**Why this matters:** If the description summarizes the workflow, Claude may follow the description instead of reading the full skill content. Descriptions are for *when to use*, skill body is for *how to use*.

❌ Bad: `description: Use when executing plans - dispatches subagent per task with code review between tasks`

✅ Good: `description: Use when executing implementation plans with independent tasks in the current session`

### Naming Conventions

Skills follow a hierarchical naming pattern:

**Generic principles skills** (suffix: `-principles`):
- `code-review-principles` — language-agnostic review checklist
- `security-audit-principles` — universal OWASP Top 10
- `dependency-management-principles` — universal BOM patterns
- `observability-principles` — universal logging/tracing/metrics

**Language-specific skills** (prefix: language name):
- `java-dev` — Java development
- `java-code-review` — extends `code-review-principles` for Java/Quarkus
- `java-security-audit` — extends `security-audit-principles` for Java/Quarkus
- `java-git-commit` — extends `git-commit` for Java repositories

**Tool-specific skills** (prefix: tool name):
- `maven-dependency-update` — extends `dependency-management-principles` for Maven

**Framework-specific skills** (prefix: framework name):
- `quarkus-flow-dev` — Quarkus + quarkus-flow development
- `quarkus-flow-testing` — Quarkus + quarkus-flow testing
- `quarkus-observability` — extends `observability-principles` for Quarkus

**Why this matters:** The naming pattern makes it clear which skills are generic foundations vs. language/tool-specific implementations. When adding support for new languages, create skills like `go-code-review` (extends `code-review-principles`), `gradle-dependency-update` (extends `dependency-management-principles`), etc.

#### Extending to New Languages: Pattern Examples

**When adding support for new languages/frameworks, follow established patterns to maintain consistency.**

**Python ecosystem:**
- `python-dev` — NOT `python-development` (keep 1-word suffix for consistency with `java-dev`)
- `python-code-review` — extends `code-review-principles` for Python (consistent with `java-code-review`)
- `pytest-runner` — NOT just `pytest` (suffix clarifies it's a test runner skill)
- `pip-dependency-update` — extends `dependency-management-principles` for pip

**Go ecosystem:**
- `go-dev` — NOT `golang-dev` (use language's canonical name)
- `go-code-review` — extends `code-review-principles` for Go
- `go-security-audit` — extends `security-audit-principles` for Go-specific issues
- `gomod-dependency-update` — extends `dependency-management-principles` for go.mod

**Rust ecosystem:**
- `rust-dev` — follows same pattern
- `rust-code-review` — extends `code-review-principles` for Rust
- `cargo-dependency-update` — extends `dependency-management-principles` for Cargo.toml

**JavaScript/TypeScript ecosystem:**
- `ts-dev` — TypeScript development (abbreviated to avoid `typescript-dev` length)
- `ts-code-review` — extends `code-review-principles` for TypeScript
- `npm-dependency-update` — extends `dependency-management-principles` for package.json
- `react-dev` — framework-specific (follows `quarkus-flow-dev` pattern)

**Common naming mistakes to avoid:**

| Mistake | Why Wrong | Correct |
|---------|-----------|---------|
| `python-development` | Inconsistent with `java-dev` | `python-dev` |
| `golang-dev` | "Go" is canonical name | `go-dev` |
| `python-review` | Doesn't match `java-code-review` pattern | `python-code-review` |
| `pytest` | Ambiguous (skill or tool?) | `pytest-runner` or `pytest-dev` |
| `javascript-dev` | Too long, TypeScript more common | `ts-dev` (covers both) |
| `react` | Just framework name | `react-dev` |

**Key principles:**
1. **Consistency over brevity** — match existing patterns even if longer
2. **1-word base** — `*-dev`, `*-code-review`, `*-security-audit` (NOT `*-development`, `*-reviewing`)
3. **Canonical names** — Go not Golang, Python not Py, TypeScript not JavaScript
4. **Tool prefix for tool-specific** — `cargo-*`, `npm-*`, `pip-*`, `gomod-*`
5. **Framework prefix for framework-specific** — `react-*`, `vue-*`, `django-*`

**Testing consistency:**
```bash
# List all language-specific skills
ls -d *-dev *-code-review *-security-audit 2>/dev/null

# Should show consistent patterns:
# java-dev, python-dev, go-dev (NOT python-development, golang-dev)
# java-code-review, python-code-review, go-code-review (NOT python-review)
```

### Skill Chaining

Skills explicitly reference each other to create workflows. The README documents the complete chaining matrix, but when editing skills:

1. **Add cross-references in "Skill Chaining" sections** (capitalized, not "Skill chaining")
2. **Make references bidirectional** when appropriate (e.g., java-security-audit ↔ java-code-review)
3. **Use Prerequisites sections** for layered skills (e.g., quarkus-flow-testing builds on java-dev and quarkus-flow-dev)
4. **Generic principles skills are never invoked directly** — they're referenced via Prerequisites by language/framework-specific skills

Example chaining patterns:
```
# Java repositories with both DESIGN.md and CLAUDE.md:
java-dev → java-code-review → java-git-commit → java-update-design + update-claude-md (automatic)

# Any repository with CLAUDE.md:
git-commit → update-claude-md (automatic)
```

### Supporting Files

When skill content exceeds ~200 words or includes heavy reference material:

- Extract to separate `.md` files (e.g., `funcDSL-reference.md`)
- Reference from main `SKILL.md`
- Keep skill body focused on workflow and principles

Pattern:
```
skill-name/
  SKILL.md              # Main workflow (required)
  reference-name.md     # Heavy API/reference docs
```

### Skills-Repository-Specific Documentation

**This repository has modularized documentation for skills-specific workflows to avoid token waste in other projects.**

Skills-repository-specific logic (SKILL.md validation, README synchronization) is NOT implemented as portable skills. Instead, it lives in standalone documentation files at the repository root:

| File | Purpose | Used By |
|------|---------|---------|
| **skill-validation.md** | SKILL.md validation workflow (frontmatter, CSO, flowcharts, cross-references) | `git-commit` when type: skills AND SKILL.md files staged |
| **readme-sync.md** | README.md synchronization workflow (skill collection changes) | `git-commit` when type: skills AND skill changes detected |

**Why modularized (not skills):**
- These workflows only apply to THIS repository
- Loading them as skills wastes tokens in all other projects (java, custom, generic)
- They contain heavy reference material (checklists, tables, patterns)
- CLAUDE.md loads automatically in every conversation
- git-commit can reference these files when operating in type: skills mode

**When git-commit operates in type: skills mode:**
1. Check for staged SKILL.md files → Follow skill-validation.md workflow
2. Check for skill collection changes → Follow readme-sync.md workflow
3. Both workflows maintain the same confirmation pattern (propose → user YES → apply)

**These files are NOT:**
- Loaded in java/custom/generic projects (zero token cost)
- Duplicated in skills collection (single source of truth)
- Skills themselves (not in skills/ directory, not user-invocable via Skill tool)

### Flowcharts

Skills use Graphviz dot notation for decision flows. Add flowcharts when:

- Decision points are non-obvious
- Process has loops where you might stop too early
- "When to use A vs B" decisions exist

Never use flowcharts for:
- Reference material (use tables)
- Code examples (use markdown blocks)
- Linear instructions (use numbered lists)

Flowcharts must have semantic labels, not generic ones like `step1`, `helper2`.

### Success Criteria

Skills that produce artifacts (commits, ADRs, dependency updates) include explicit "Success Criteria" sections with checkboxes. This prevents premature completion claims.

Example pattern:
```markdown
## Success Criteria

Dependency update is complete when:

- ✅ User has confirmed changes with **YES**
- ✅ BOM alignment verified (no version drift)
- ✅ Compilation succeeds (`mvn compile` passes)
- ✅ pom.xml changes committed

**Not complete until** all criteria met and changes committed.
```

## Modular Documentation

**Full support for modular documentation across all project types.**

Primary documents (DESIGN.md, CLAUDE.md, README.md, VISION.md, THESIS.md, etc.) can be split into multiple linked files. Sync workflows automatically discover modules, update all files together, and validate the entire document group.

### Why Modular Documentation

**Large documents become unmaintainable:**
- Single 2000-line DESIGN.md is hard to navigate
- Different concerns mixed together (architecture + API + data model)
- Merge conflicts when multiple people edit different sections
- Cognitive overload when updating one part

**Modular structure solves this:**
- Split by concern: `DESIGN.md` → `architecture.md` + `api.md` + `data-model.md`
- Each file focused on one topic (easier to understand, edit, review)
- Parallel editing (no merge conflicts)
- Sync workflows keep all files in sync automatically

### How Discovery Works

**Automatic discovery (preferred):**

Sync workflows discover modules via:
1. **Markdown links:** `[Architecture](docs/design/architecture.md)`
2. **Include directives:** `<!-- include: components.md -->`
3. **Section references:** `§ API Details in docs/design/api.md`
4. **Directory pattern:** `docs/design/*.md` files (if primary is `DESIGN.md`)

**Caching:**
- First sync: Discovers modules, caches in `.doc-cache.json` (gitignored)
- Subsequent syncs: Uses cache (fast path, <10ms)
- Cache invalidation: Automatic on structure changes (new links, new files)

**Backwards compatible:**
- Single-file documents work unchanged (empty modules list)
- No migration required (opt-in by adding links)

### When to Use Modular vs Single-File

**Use modular when:**
- Document exceeds ~500 lines
- Multiple distinct topics (architecture, API, data model, deployment)
- Multiple contributors editing different sections
- Frequent updates to specific sections (avoid touching entire file)

**Keep single-file when:**
- Document under ~300 lines
- Single cohesive topic
- Infrequent updates
- Solo maintainer

### How to Modularize a Document

**Example: Split DESIGN.md**

**Before (single file):**
```
docs/DESIGN.md (1500 lines)
  - Overview
  - Architecture
  - Components
  - API Endpoints
  - Data Model
  - Deployment
```

**After (modular):**
```
docs/DESIGN.md (200 lines - overview + links to modules)
docs/design/architecture.md
docs/design/components.md
docs/design/api.md
docs/design/data-model.md
docs/design/deployment.md
```

**Primary file (DESIGN.md) becomes navigation:**
```markdown
# Project Design

## Overview
High-level summary of the project...

## Architecture
See [Architecture](docs/design/architecture.md) for detailed component structure and data flow.

## Components
See [Components](docs/design/components.md) for service descriptions and responsibilities.

## API
See [API Endpoints](docs/design/api.md) for REST endpoint documentation.

## Data Model
See [Data Model](docs/design/data-model.md) for entity relationships and schema.

## Deployment
See [Deployment](docs/design/deployment.md) for infrastructure and configuration.
```

**Module files contain details:**
```markdown
# Architecture

## Component Overview
[Detailed architecture content...]

## Data Flow
[Sequence diagrams, data flow descriptions...]

## Design Decisions
[Rationale for architectural choices...]
```

### Sync Workflow Behavior

**When syncing modular documents:**

1. **Discovery:** Sync workflow discovers all modules from primary file
2. **Analysis:** Maps code changes to sections across all files
3. **Proposals:** Groups updates by file:
   ```
   ## Proposed DESIGN.md updates
   [changes to primary file]

   ## Proposed docs/design/architecture.md updates
   [changes to architecture module]

   ## Proposed docs/design/api.md updates
   [changes to API module]
   ```
4. **User confirmation:** User reviews all proposed changes
5. **Application:** All files updated together (atomic)
6. **Validation:** Entire document group validated (link integrity, completeness, no duplication)
7. **Revert on failure:** If validation fails, ALL files reverted (not just primary)

**Routing logic:**
- Sync workflows propose updates to the most specific module
- Example (Java): New `@RestController` → `docs/design/api.md` (if exists), else `DESIGN.md` § API
- Example (Skills): New skill → `docs/readme/skills.md` (if exists), else `README.md` § Skills

### Explicit Configuration (Optional)

**Automatic discovery works for most cases.** If needed, declare modules explicitly in CLAUDE.md:

```markdown
## Modular Documentation

### DESIGN.md
**Modules:**
- docs/design/architecture.md
- docs/design/components.md
- docs/design/api.md
- docs/design/data-model.md

### CLAUDE.md
**Modules:**
- docs/workflows/ci.md
- docs/workflows/testing.md
```

**When to use explicit config:**
- Automatic discovery is ambiguous (multiple interpretation)
- Want to control exact module list (exclude some auto-detected files)
- Modules are optional and shouldn't always be included

### Validation

**Cross-module validation ensures document group integrity:**

| Check | Severity | What It Catches |
|-------|----------|----------------|
| **Link integrity** | CRITICAL | Broken `[links](file.md)` or `[links](file.md#section)` |
| **Completeness** | WARNING | Orphaned modules (unreferenced from primary) |
| **No duplication** | NOTE | Substantial paragraphs duplicated across files |
| **Individual file** | CRITICAL | Corrupted tables, duplicate headers, orphaned sections |

**Validation runs automatically:**
- After applying sync proposals (before staging)
- CRITICAL issues block commit and trigger automatic revert of ALL files
- WARNING/NOTE issues are reported but don't block

### Universal Application

**Works across all project types:**

| Project Type | Primary Document | Example Modules |
|--------------|------------------|-----------------|
| **type: skills** | README.md, CLAUDE.md | `docs/readme/skills.md`, `docs/workflows/ci.md` |
| **type: java** | DESIGN.md, CLAUDE.md | `docs/design/architecture.md`, `docs/workflows/build.md` |
| **type: custom** | User-configured (VISION.md, THESIS.md, etc.) | User-configured modules |
| **type: generic** | CLAUDE.md | `docs/workflows/*.md` |

**Same discovery, same validation, same sync behavior** — universal rule applied.

### Migration Path

**No migration required.** Modular support is opt-in:

1. **Keep single-file:** Do nothing, documents work as before
2. **Gradual modularization:** Extract one section at a time, add link, sync detects automatically
3. **Full modularization:** Split entire document, sync handles all modules

**Example gradual migration:**
```
Week 1: Extract API section → docs/design/api.md, link from DESIGN.md
Week 2: Extract Data Model → docs/design/data-model.md, link from DESIGN.md
Week 3: Extract Architecture → docs/design/architecture.md, link from DESIGN.md
```

Each step is independently useful. No "all or nothing" migration.

## Consistency Patterns

When editing skills, maintain these conventions:

### Section Naming

- "Skill Chaining" (capitalized C)
- "Prerequisites" (for layered skills)
- "Success Criteria" (for artifact-producing skills)
- "Common Pitfalls" (table format: Mistake | Why It's Wrong | Fix)

### Cross-Reference Format

```markdown
## Prerequisites

**This skill builds on `skill-name`**. Apply all rules from:
- **skill-name**: [specific rules that apply]
```

or

```markdown
## Skill Chaining

**Triggered by skill-name:**
When [condition], it should invoke this skill for [reason].

**Chains to skill-name:**
After [milestone], invoke skill-name for [purpose].
```

### Common Mistakes Tables

All major skills include "Common Pitfalls" tables documenting real mistakes:

```markdown
| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| [Anti-pattern] | [Consequence] | [Correct approach] |
```

### Third-Party Skill Exclusion

**CRITICAL: Only document skills authored by the repository owner.**

**Rules:**
- ✅ **Document only user-authored skills** in README.md and CLAUDE.md
- ❌ **Never document third-party skills** (skills from superpowers:*, external repos, etc.)
- ✅ **Add third-party skills to .gitignore** immediately upon discovery
- ❌ **Never reference third-party skills** in documentation (chaining tables, workflows, repository structure)

**Rationale:**
- Third-party skills are maintained elsewhere and can change without notice
- Documenting them creates maintenance burden and stale references
- Users already see third-party skills in their skill list
- README/CLAUDE.md should reflect only what this repository provides

**Implementation:**
1. Add skill directory to .gitignore with comment: `# Third-party skill from [source]`
2. Remove all references from README.md (Skills section, Chaining table, Repository Structure)
3. Remove all references from CLAUDE.md (Key Skills section)
4. Verify removal with: `grep -r "skill-name" README.md CLAUDE.md`

**Examples of third-party skills to exclude:**
- `superpowers:*` (all superpowers skills)
- `skill-creator` (external skill authoring tool)
- `frontend-design:*` (third-party frontend skills)
- Any skill not in version control for this repository

**Quality check:** During deep analysis, verify no third-party skills are documented anywhere.

## Editing Skills

When modifying existing skills:

1. **Check README first** — the Skill Chaining Reference table shows the complete dependency graph
2. **Update cross-references** — if you add chaining, update both skills (source and target)
3. **Preserve CSO descriptions** — don't add workflow summaries to frontmatter
4. **Test flowcharts** — invalid dot syntax breaks skill loading
5. **Maintain Prerequisites** — layered skills (quarkus-flow-*) must reference their foundations

## Pre-Commit Checklist for Skills

**CRITICAL: All items are MANDATORY by default unless explicitly marked (advisory).**

**This is NOT a judgment call. This is NOT optional. This is a DISCIPLINE.**

Failing to execute these checks before committing is a failure, not a decision. The bigger the change, the more critical the checklist becomes. Infrastructure changes especially require documentation sync.

### Mandatory Checks

Run these checks **before every commit** to this repository:

- [ ] **SKILL.md files modified?** → Follow readme-sync.md workflow (NEVER skip, let it decide if README needs updates)
- [ ] **CLAUDE.md modified?** → Follow relevant update workflow if applicable
- [ ] **New validation/testing added?** → Update README.md § Skill Quality & Validation AND QUALITY.md § Implementation Status
- [ ] **New scripts/ files added?** → Update README.md § Repository Structure
- [ ] **New chaining relationships?** → Update README.md § Skill Chaining Reference
- [ ] **New features added to skills?** → Update README.md § Key Features
- [ ] **Framework changes** (same pattern across multiple skills)? → Document in README.md AND QUALITY.md if validation-related
- [ ] **Infrastructure changes** (validators, test infrastructure, orchestrators)? → Update README.md § Repository Structure, QUALITY.md § Implementation Status, and this file § Validation Script Roadmap

### Anti-Rationalization Rules

**Do NOT rationalize skipping these checks:**
- ❌ "Just internal changes" → Wrong, internal changes can warrant documentation
- ❌ "Not significant enough" → Wrong, let the workflow decide significance
- ❌ "I know what needs updating" → Wrong, you'll miss things (proven multiple times)
- ❌ "The completion doc is sufficient" → Wrong, README/QUALITY.md must stay current
- ❌ "This is meta-work about infrastructure" → Wrong, infrastructure changes need MORE documentation, not less
- ✅ **ALWAYS execute the checklist** — it exists to catch what you miss

### Enforcement Pattern

**Before committing:**
1. Read this checklist top to bottom
2. For each item that applies: Execute it (don't just think about it)
3. If you're unsure if an item applies: Execute it anyway
4. Only after all applicable items executed: Commit

**This is the same discipline as:**
- Running tests before committing code
- Validating syntax before pushing
- Code review before merging

### Known Regressions (Learn From These)

**Regression 1:** Validation framework added to 4 sync workflows but README.md not updated. Root cause: Skipped readme-sync.md workflow, rationalized "just internal changes". Result: Documentation drift. Fix: Never skip workflows when SKILL.md files change.

**Regression 2:** Created 14 validators + test infrastructure (17 new files, ~2,800 LOC), committed completion document, but didn't update README.md § Repository Structure or QUALITY.md § Implementation Status until user asked. Root cause: Tunnel vision on Options A/B/C, didn't check Pre-Commit Checklist, rationalized "completion doc is sufficient". Result: Primary documentation out of date. Fix: Infrastructure changes require MORE documentation sync, not less. Checklist is mandatory, not advisory.

---

## Meta-Rule: Checklists Are Mandatory By Default

**CRITICAL: All checklists in this file and in skills are MANDATORY unless explicitly marked (advisory).**

**This applies to:**
- Pre-Commit Checklists
- Success Criteria sections in skills
- Validation checklists
- Deep Analysis checklists
- Review checklists
- Any numbered or bulleted procedure

**Default assumption: MANDATORY.**

If an item is truly optional or advisory, it will be explicitly marked:
- "(advisory)" suffix
- "Optional:" prefix
- "Consider:" prefix (judgment call)

**If not marked advisory, it's mandatory. Period.**

**Why this matters:**

Treating checklists as advisory leads to:
- Skipped steps
- Incomplete work
- Documentation drift
- Rationalization ("I know better")
- Repeated regressions

Treating checklists as mandatory ensures:
- Consistent execution
- Complete work
- Up-to-date documentation
- Discipline over judgment
- Prevention of known failures

**The test:**
- "Should I do this?" → Wrong question
- "Is this marked (advisory)?" → Right question
  - If no → Do it
  - If yes → Use judgment

**This is fundamental discipline, like:**
- Running tests before committing
- Reading the file before editing it
- Validating syntax before pushing
- Following TDD cycle (red-green-refactor)

**Exception handling:**
If you believe a checklist item doesn't apply to your situation, that's a flag to:
1. Re-read the item carefully
2. Check if you're rationalizing
3. If still uncertain → Execute it anyway (safer to over-apply than skip)
4. If it truly doesn't apply → Document why in commit message

**Never skip checklist items silently.**

---

## Meta-Rule: Consider Universality First

**CRITICAL: Before applying any fix, ask "Should this be universal?"**

**The principle:**
When you identify a problem and prepare a solution, STOP and consider:
1. **Is this problem specific to one context** (skills repo only, Java only, this file only)?
2. **Or is this a universal problem** (could happen in any project type, any AI assistant, any workflow)?

**If uncertain whether to make it universal → ASK THE USER.**

**Examples:**

| Situation | Narrow Fix | Universal Fix | Correct Choice |
|-----------|------------|---------------|----------------|
| README.md sync missing | Add check to readme-sync.md only | Add framework change detection to ALL sync workflows | Universal (ADR-0001) |
| Java-specific BOM issue | Fix in maven-dependency-update | Make dependency management universal | Narrow (Java-specific) |
| Rationalization bypass | Strengthen git-commit Step 2b | Add mandatory checks to all workflows | Universal |
| Quarkus event loop bug | Fix in quarkus-flow-dev | Make concurrency universal | Already universal (code-review-principles) |

**Why this matters:**
- **Prevents repeated regressions** - fix once, applies everywhere
- **Scales to future project types** - type: python, type: rust get the fix automatically
- **Reduces user burden** - don't re-discover same problem per project
- **Forces better design** - universal solutions are often cleaner

**When to stay narrow:**
- Domain-specific knowledge (Java annotations, Quarkus configuration)
- Language syntax (Java vs Python vs Go)
- Tool-specific features (Maven BOM vs npm package.json)
- Framework patterns (Quarkus vs Spring)

**When to go universal:**
- Process failures (rationalization, skipping workflows)
- Quality gates (validation, testing, documentation)
- Human behavior patterns (cognitive biases, shortcuts)
- Infrastructure (scripts, automation, validation)

**The test:** If the problem could plausibly occur in a different project type with different technologies, it's probably universal.

**See:** ADR-0001: Documentation Completeness Must Be Universal, Not Project-Specific

## Key Skills

**Generic foundation skills** (not invoked directly, referenced via Prerequisites):
- `code-review-principles` — universal code review checklist (extended by `java-code-review`)
- `security-audit-principles` — universal OWASP Top 10 (extended by `java-security-audit`)
- `dependency-management-principles` — universal BOM patterns (extended by `maven-dependency-update`)
- `observability-principles` — universal logging/tracing/metrics (extended by `quarkus-observability`)

**Language/framework foundation skills** (others build on these):
- `java-dev` — all Java development extends this
- `git-commit` — generic conventional commits (extended by `java-git-commit`)

**Workflow integrators** (chain multiple skills):
- `git-commit` — automatically invokes `skill-review` (if SKILL.md staged), `update-claude-md` (if CLAUDE.md exists), and `readme-sync.md` (if README.md exists and skill changes). Routes to java-git-commit or custom-git-commit based on project type
- `java-git-commit` — automatically invokes `java-update-design` and `update-claude-md` (if docs exist). For type: java projects only
- `custom-git-commit` — automatically invokes `update-primary-doc` (if Sync Rules configured) and `update-claude-md` (if exists). For type: custom projects (working groups, research, docs)
- `java-code-review` — triggers `java-security-audit` for security-critical code
- `skill-review` — blocks `git-commit` if CRITICAL findings exist

**Specialized skills** (domain-specific):
- `quarkus-flow-dev` — builds on `java-dev`, extended by `quarkus-flow-testing`
- `java-security-audit` — OWASP Top 10 for Java/Quarkus, triggered by `java-code-review`
- `maven-dependency-update` — Maven BOM management, builds on `dependency-management-principles`
- `quarkus-observability` — Quarkus observability config, builds on `observability-principles`
- `skill-review` — SKILL.md validation (frontmatter, CSO, cross-references, flowcharts), invoked by `git-commit`
- `update-primary-doc` — Generic table-driven primary document sync (VISION.md, THESIS.md, etc.), invoked by `custom-git-commit`. Reads Sync Rules from CLAUDE.md
- `java-update-design` — DESIGN.md synchronization (architecture documentation), invoked by `java-git-commit`. For type: java projects only
- `update-claude-md` — CLAUDE.md synchronization (workflow documentation), invoked by `git-commit`, `java-git-commit`, and `custom-git-commit`
- `readme-sync.md` — README.md synchronization (skills repository documentation), invoked by `git-commit`. For type: skills projects only

## README Synchronization

When adding/modifying skills, update README sections:

- **Skills** section: Add/update skill description with trigger conditions
- **How Skills Work Together**: Update chaining workflows if changed
- **Skill Chaining Reference** table: Add new chaining relationships
- **Key Features**: Note new flowcharts, Prerequisites sections, etc.

The README is the single source of truth for the skill collection's architecture.

## Quality Assurance Framework

**CRITICAL: This section prevents regressions by documenting all types of validation that skills must pass.**

Skills are infrastructure code that guides AI behavior across millions of invocations. Quality issues compound exponentially. This framework ensures skills maintain structural integrity, logical soundness, and documentation accuracy over time.

### The Testing Philosophy

**Skills need both automated and manual validation:**

| Validation Type | What It Catches | Tools |
|----------------|-----------------|-------|
| **Automated** | Structural errors, syntax, format violations, broken references | Scripts, linters, parsers |
| **Manual** | Logic errors, unclear writing, missing edge cases, contradictions | Deep analysis reviews |
| **Functional** | Workflow execution, command correctness, actual usability | Test cases with real Claude instances |

**All three are required.** Automated tests catch mechanical errors fast. Manual reviews catch semantic errors. Functional tests catch real-world failures.

---

### Division of Labor: Automated vs AI-Assisted Validation

**CRITICAL: Scripts cannot replace deep thought. This framework combines automated checks (fast, mechanical) with AI-assisted analysis (semantic, strategic).**

**Universal across ALL project types** — this architecture applies whether you're maintaining skills, Java code, research docs, or any other repository.

#### What Scripts CAN Check (Automated)

**Mechanical/Structural validation (no intelligence needed):**

| Check Type | Example | All Project Types |
|------------|---------|-------------------|
| **Syntax errors** | Broken markdown, invalid YAML, malformed tables | ✅ README.md, DESIGN.md, CLAUDE.md, VISION.md, THESIS.md, etc. |
| **Format violations** | Duplicate headers, missing sections, heading hierarchy | ✅ Any .md file in any repository |
| **Broken references** | Links to non-existent files/sections, missing anchors | ✅ Internal links across all documentation |
| **File existence** | "see docs/MISSING.md" when file doesn't exist | ✅ Verify referenced files exist |
| **Pattern matching** | CSO violations (SKILL.md only), code block language tags | ✅ Skills repos get CSO check, all repos get code block check |
| **Simple rules** | Frontmatter schema (SKILL.md), table structure, list formatting | ✅ Type-specific where needed, universal where possible |

**Exit behavior:** Blocks on CRITICAL mechanical errors. Fast (<2s for commit-level checks).

**Type-specific automated checks:**

| Project Type | Additional Automated Checks | Why Type-Specific |
|--------------|----------------------------|-------------------|
| **type: skills** | SKILL.md frontmatter validation, CSO compliance | SKILL.md format is skills-specific |
| **type: java** | Java syntax validation, import organization | Code structure rules |
| **type: custom** | User-defined validation rules (configurable) | User knows their domain rules |
| **type: generic** | None (universal checks only) | Minimal overhead |

**Universal automated checks (ALL project types):**
- Document corruption (duplicate headers, broken tables, orphaned sections)
- Link validation (internal anchors, cross-document links)
- Code block syntax (bash, python, java examples)
- Spelling and basic grammar
- Structural quality (heading hierarchy, list formatting)

#### What Scripts CANNOT Check (Requires AI)

**Semantic/Strategic analysis (requires understanding):**

| Check Type | Why Scripts Fail | Requires Human/AI |
|------------|------------------|-------------------|
| **Semantic contradictions** | "Always use X" in one section, "Never use X" in another → scripts see valid paragraphs, can't detect conflict | ✅ Claude reads both, understands contradiction |
| **Logical flow** | Workflow says "Step 1, Step 2, Step 4" → scripts see numbers, can't detect missing Step 3 | ✅ Claude simulates execution, notices gap |
| **Nonsensical content** | "Use maven-dependency-update when upgrading Java versions" → scripts see valid sentence, can't detect wrong tool for wrong job | ✅ Claude knows semantic meaning, detects error |
| **Strategic completeness** | Workflow missing error handling → scripts can't know what SHOULD be there | ✅ Claude knows best practices, identifies gaps |
| **Cross-document consistency** | CLAUDE.md says "always sync", skill says "optional" → scripts can flag both mention sync, can't determine contradiction | ✅ Claude understands semantics, detects conflict |
| **Quality judgment** | Is this explanation clear? Best way to structure this? → subjective | ✅ Claude applies judgment, suggests improvements |

**Example: Scripts Flag, Claude Judges**

**Scenario: Potential contradiction in git-commit workflow**

```bash
# Scripts run during pre-push
python scripts/validate_consistency.py --level push

⚠️  WARNING: Potential contradiction detected:
   - git-commit/SKILL.md:24: "Never add attribution"
   - CLAUDE.md:156: "All commits include Co-Authored-By"

   These statements may conflict. Run deep analysis? (Y/n)
```

**User invokes Claude for semantic analysis:**

```
User: "Review git-commit skill for contradictions"

Claude:
1. Reads git-commit/SKILL.md full context:
   - Core Rules: "Never add attribution UNLESS user explicitly requests it"

2. Reads CLAUDE.md § Committing changes:
   - "All commits include Co-Authored-By: Claude"

3. Semantic analysis:
   - git-commit changed to "never add attribution" (recent update)
   - CLAUDE.md has stale text from before this change

4. Reports finding:
   ❌ CRITICAL: CLAUDE.md is stale. git-commit now says "never add
   attribution unless requested" but CLAUDE.md still says all commits
   include Co-Authored-By.

   Fix: Update CLAUDE.md line 156 to match git-commit's current behavior.
```

**Result:** Script identified potential issue (string matching), Claude provided semantic understanding and fix.

#### Universal Application Across Project Types

**This division of labor applies to ALL repositories using these skills:**

**Type: skills (this repository):**
- **Scripts validate:** SKILL.md frontmatter, README.md structure, CLAUDE.md syntax
- **Claude validates:** Skill chaining logic, workflow completeness, cross-skill consistency
- **Hybrid:** Scripts flag CSO violations, Claude assesses if description actually summarizes workflow

**Type: java (Java/Maven/Gradle projects):**
- **Scripts validate:** DESIGN.md structure, CLAUDE.md syntax, Java code formatting
- **Claude validates:** DESIGN.md architecture accuracy, code review for logic errors, DESIGN.md vs code consistency
- **Hybrid:** Scripts flag missing DESIGN.md sections, Claude assesses if architecture description matches actual code

**Type: custom (working groups, research, documentation):**
- **Scripts validate:** Primary doc structure (VISION.md, THESIS.md, etc.), CLAUDE.md syntax, Sync Rules table format
- **Claude validates:** Primary doc coherence, research methodology soundness, claim accuracy
- **Hybrid:** Scripts flag broken references, Claude assesses if referenced sections actually support claims

**Type: generic (simple projects):**
- **Scripts validate:** CLAUDE.md syntax (if exists), basic markdown quality
- **Claude validates:** Commit message quality, documentation clarity
- **Hybrid:** Scripts flag spelling errors, Claude judges if corrections change meaning

#### When to Use Automated vs AI-Assisted

**Automated validation (scripts) — ALWAYS RUNNING:**

| Trigger | Level | Time Budget | Purpose |
|---------|-------|-------------|---------|
| **File save** | Quick | <100ms | Instant feedback (editor integration) |
| **Pre-commit** | Commit | <2s | Block corruption before git history |
| **Pre-push** | Push | <30s | Cross-document checks before sharing |
| **CI/CD** | Full | <5min | Comprehensive mechanical validation |

**AI-assisted validation (Claude) — SELECTIVE INVOCATION:**

| Trigger | Scope | Time Budget | Purpose |
|---------|-------|-------------|---------|
| **User requests review** | `/skill-review`, `/java-code-review` | User-driven | On-demand deep analysis |
| **Major changes** | User judgment call | User-driven | Validate significant refactors |
| **Scripts flag WARNING** | Specific issue | Quick check | Semantic confirmation needed |
| **Before releases** | Full repository | Comprehensive | Ensure quality before publishing |
| **Scheduled deep analysis** | Weekly/monthly | Comprehensive | Prevent quality drift |

**Decision matrix:**

```
Issue detected → Is it mechanical/structural?
                 ├─ YES → Script should catch it (add check if missing)
                 └─ NO → Requires semantic analysis
                          ├─ Simple → Script can flag, Claude confirms
                          └─ Complex → Claude deep analysis required
```

#### Concrete Examples by Project Type

**Example 1: Type: skills — SKILL.md validation**

**Scripts check (automated):**
- ✅ Frontmatter has `name` and `description` fields
- ✅ Description doesn't contain "step 1, step 2" (CSO violation pattern)
- ✅ Cross-referenced skills exist (file existence check)
- ✅ Flowchart has valid Graphviz syntax
- ✅ No duplicate section headers

**Claude checks (AI-assisted):**
- ❓ Does description summarize workflow? (semantic CSO violation)
- ❓ Is workflow logically sound? (can it execute as written?)
- ❓ Are cross-references accurate? (does referenced skill actually do what's claimed?)
- ❓ Is flowchart semantically correct? (do decision branches make sense?)
- ❓ Are examples consistent with rules? (do examples illustrate the point?)

**Example 2: Type: java — DESIGN.md sync**

**Scripts check (automated):**
- ✅ DESIGN.md file exists (blocks commit if missing)
- ✅ Required sections present (Architecture, Components, etc.)
- ✅ No duplicate headers
- ✅ Code examples have syntax highlighting tags
- ✅ Internal links resolve

**Claude checks (AI-assisted):**
- ❓ Does architecture description match actual code structure?
- ❓ When @Service added, is it documented in "Business Logic" section?
- ❓ When new module added to pom.xml, is it in "Component Structure"?
- ❓ Are design decisions explained (not just described)?
- ❓ Do sequence diagrams match actual code flow?

**Example 3: Type: custom — Research project (THESIS.md)**

**Scripts check (automated):**
- ✅ THESIS.md structure valid (chapters, sections)
- ✅ Bibliography references exist
- ✅ Figure references point to existing files
- ✅ No duplicate section numbering
- ✅ Citations formatted consistently

**Claude checks (AI-assisted):**
- ❓ Does Methodology section describe experiments in `experiments/`?
- ❓ Do claims in Results match data in tables?
- ❓ Are conclusions supported by presented evidence?
- ❓ Is literature review comprehensive (all cited works discussed)?
- ❓ Does chapter flow logically build argument?

**Example 4: Type: generic — Simple project (CLAUDE.md only)**

**Scripts check (automated):**
- ✅ CLAUDE.md syntax valid
- ✅ Code examples are valid bash/commands
- ✅ Project Type declared
- ✅ No broken internal links

**Claude checks (AI-assisted):**
- ❓ Do build commands actually work?
- ❓ Is testing guidance accurate?
- ❓ Are conventions clearly explained?
- ❓ Is repository structure description current?

#### Integration: Scripts + Claude Working Together

**Tiered validation with hybrid approach:**

```
Level 1: Quick (on save)
  → Scripts only: Syntax, heading hierarchy
  → 100ms, never blocks

Level 2: Commit (pre-commit hook)
  → Scripts: Structure, format, broken links
  → Blocks on CRITICAL mechanical errors
  → 2s budget

Level 3: Review (user-invoked)
  → Scripts run all checks first
  → Claude performs deep semantic analysis
  → Reports findings with CRITICAL/WARNING/NOTE
  → User-driven timing

Level 4: Push (pre-push hook)
  → Scripts: Cross-document checks, terminology consistency
  → If scripts flag WARNING → optionally invoke Claude
  → 30s budget

Level 5: Full (CI, scheduled)
  → Scripts: Everything automated
  → Claude: Comprehensive deep analysis
  → Generate combined report
  → 5min budget
```

**Workflow example:**

```bash
# 1. Developer edits DESIGN.md
vim docs/DESIGN.md

# 2. On save → scripts validate (quick level)
✅ No syntax errors (100ms)

# 3. Git commit
git add docs/DESIGN.md
git commit -m "docs(design): update architecture"

# → Pre-commit hook runs scripts (commit level)
🔍 Running commit-level validation...
✅ No duplicate headers
✅ No corrupted tables
✅ All links valid
✅ Validation passed

# 4. Developer requests review before push
/java-code-review

# → Claude performs deep analysis
Reading docs/DESIGN.md...
Comparing with actual code structure...

❌ CRITICAL: DESIGN.md says "3-tier architecture" but code has 4 layers
   - Missing documentation for new "gateway" layer added in src/gateway/

⚠️  WARNING: Sequence diagram shows sync call but code uses async
   - Lines 45-67 in DESIGN.md need update

ℹ️  NOTE: Could add example for new gateway pattern

# 5. Developer fixes issues, commits again
git add docs/DESIGN.md
git commit -m "docs(design): add gateway layer, fix sequence diagram"

# 6. Push
git push origin main

# → Pre-push hook runs scripts (push level)
🔍 Running push-level validation...
✅ Cross-document consistency checked
✅ Terminology consistent
✅ No duplication detected
✅ Push validation passed

# 7. CI runs full validation
# → Scripts run all automated checks
# → Claude runs comprehensive deep analysis (if configured)
# → Results posted as PR comment or artifact
```

#### Key Principles for Universal Quality

**1. Scripts are gatekeepers (universal):**
- Fast, mechanical checks on ALL .md files
- Block CRITICAL corruption before git history
- Run automatically (pre-commit, pre-push, CI)
- Type-specific where needed (SKILL.md frontmatter), universal where possible (duplicate headers)

**2. Claude is architect (universal):**
- Semantic analysis on ANY documentation
- Strategic completeness assessment
- Quality judgment and improvement suggestions
- Invoked selectively (user requests, major changes, releases)

**3. Hybrid approach (universal):**
- Scripts identify potential issues quickly
- Claude provides semantic understanding and fixes
- User controls when deep analysis runs
- Both work together for comprehensive quality

**4. Proportional cost (universal):**
- Light checks for small changes (quick)
- Heavy checks for big changes (commit/push)
- Heaviest checks for sharing (CI/release)
- Users can bypass for emergencies (`--no-verify`)

**5. Type-specific where needed, universal where possible:**
- SKILL.md frontmatter → skills only
- DESIGN.md sync → java only
- Primary doc sync → custom only
- Document corruption detection → ALL project types
- Semantic coherence analysis → ALL project types
- Cross-document consistency → ALL project types

**This ensures every project type gets appropriate validation without unnecessary overhead.**

---

### Automated Validation (Level 1)

**These checks can and should be scripted.**

#### 1.1 Frontmatter Validation

**Script location:** `scripts/validate_frontmatter.py` (to be created)

**Checks:**
- ✅ YAML frontmatter exists and is valid YAML
- ✅ Required fields present: `name`, `description`
- ✅ `name` matches directory name (skill-name/SKILL.md → name: skill-name)
- ✅ `name` uses hyphens, not underscores or spaces
- ✅ `description` starts with "Use when"
- ✅ `description` is under 500 characters
- ✅ `description` contains no first/second person ("I", "you")
- ✅ No extra fields (only `name`, `description`, optional `compatibility`)

**Exit code:** Non-zero if any check fails

**Example validation:**
```python
def validate_frontmatter(skill_path):
    # Read SKILL.md
    # Parse YAML frontmatter
    # Check all rules above
    # Return violations list
```

#### 1.2 CSO (Claude Search Optimization) Compliance

**Script location:** `scripts/validate_cso.py` (to be created)

**Checks:**
- ✅ Description does NOT contain workflow keywords: "step", "then", "invoke", "run", "execute", "dispatch"
- ✅ Description focuses on WHEN (symptoms, triggers, conditions)
- ✅ Description does NOT describe HOW (workflow, process, steps)
- ✅ Description does NOT list tool names (Bash, Read, Edit, Agent)
- ✅ Description length appropriate (100-500 chars preferred)

**Why this matters:** Workflow summaries in descriptions cause "expensive wallpaper" - Claude follows the summary instead of reading the skill body, making the skill useless.

**Red flags:**
- "dispatches subagent per task"
- "runs tests then commits"
- "step 1... step 2..."
- "uses Read tool to..."

#### 1.3 Graphviz Flowchart Validation

**Script location:** `scripts/validate_flowcharts.py` (to be created)

**Checks:**
- ✅ All flowcharts use valid Graphviz dot syntax
- ✅ No generic labels (step1, step2, helper1, pattern2)
- ✅ All node labels are semantic and descriptive
- ✅ Flowcharts appear only for decisions/loops (not for reference material)

**Implementation:**
```bash
# Extract flowcharts from SKILL.md
sed -n '/```dot/,/```/p' SKILL.md | sed '1d;$d' > /tmp/flowchart.dot

# Validate with graphviz
dot -Tsvg /tmp/flowchart.dot > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "CRITICAL: Invalid flowchart syntax"
  exit 1
fi

# Check for generic labels
if grep -E '"(step|helper|pattern|node)[0-9]+"' /tmp/flowchart.dot; then
  echo "WARNING: Generic flowchart labels detected"
  exit 1
fi
```

#### 1.4 Cross-Reference Integrity

**Script location:** `scripts/validate_references.py` (to be created)

**Checks:**
- ✅ All skill names referenced in backticks exist as directories
- ✅ All `Chains to X` references have corresponding SKILL.md files
- ✅ All `Prerequisites` references exist
- ✅ All `Invoked by` references exist
- ✅ No references to deleted/renamed skills

**Data structure:**
```python
# Build reference graph
skill_references = {
    'java-git-commit': {
        'chains_to': ['java-update-design', 'update-claude-md'],
        'invoked_by': ['git-commit'],
        'prerequisites': ['git-commit'],
        'mentioned_in': ['java-update-design', 'README.md']
    }
}

# Validate all references resolve
for skill, refs in skill_references.items():
    for ref in refs['chains_to']:
        assert skill_exists(ref), f"{skill} references non-existent {ref}"
```

#### 1.5 Naming Convention Compliance

**Script location:** `scripts/validate_naming.py` (to be created)

**Checks:**
- ✅ Generic principles: `*-principles` suffix
- ✅ Language-specific: language prefix (`java-*`, `python-*`)
- ✅ Tool-specific: tool prefix (`maven-*`, `gradle-*`)
- ✅ Framework-specific: framework prefix (`quarkus-*`, `spring-*`)
- ✅ No mixed patterns (e.g., `java-maven-principles` is ambiguous)

**Pattern matching:**
```python
PATTERNS = {
    'principles': r'^[a-z]+-principles$',
    'language': r'^(java|python|go|rust)-[a-z-]+$',
    'tool': r'^(maven|gradle|npm|pip)-[a-z-]+$',
    'framework': r'^(quarkus|spring|react|vue)-[a-z-]+$',
}

def categorize_skill(name):
    for category, pattern in PATTERNS.items():
        if re.match(pattern, name):
            return category
    return 'uncategorized'
```

#### 1.6 File Organization Validation

**Script location:** `scripts/validate_structure.py` (to be created)

**Checks:**
- ✅ Every skill directory has SKILL.md
- ✅ Supporting files in expected locations (scripts/, references/, assets/)
- ✅ No orphaned files (files not referenced in SKILL.md)
- ✅ Referenced files exist (skill mentions `references/api.md` → file exists)
- ✅ No duplicate content (same reference file in multiple skills)

#### 1.7 Required Sections

**Script location:** `scripts/validate_sections.py` (to be created)

**Checks based on skill type:**

| Skill Type | Required Sections |
|------------|------------------|
| **All skills** | "Skill Chaining" OR "Prerequisites" |
| **Artifact-producing** | "Success Criteria" with checkboxes |
| **Major skills** | "Common Pitfalls" table (3 columns) |
| **Layered skills** | "Prerequisites" referencing foundation |
| **Complex workflows** | Decision flowchart OR clear numbered steps |

**Detection logic:**
```python
def is_artifact_producing(skill_name):
    """Skills that create commits, files, ADRs, updates."""
    return any(keyword in skill_name for keyword in
               ['commit', 'update', 'create', 'sync'])

def requires_success_criteria(skill_path):
    skill_name = os.path.basename(skill_path)
    content = read_skill(skill_path)
    return is_artifact_producing(skill_name) and \
           '## Success Criteria' not in content
```

---

### Deep Analysis Validation (Level 2)

**These checks require human judgment but follow systematic procedures.**

When the user requests "deep analysis" or before major releases, perform ALL of these checks:

#### 2.1 Reference Accuracy

**Manual procedure:**

1. **Read every skill mentioned in cross-references**
2. **Verify bidirectional links:**
   - If A says "chains to B" → check B says "invoked by A"
   - If A says "builds on B" → check B mentions A in "Used by" or "Extended by"
3. **Check reference timestamps:**
   - Skills reference current tool names (not deprecated tools)
   - Examples use current syntax (not outdated API)
   - Links point to current locations (not moved/deleted files)
4. **Verify claim accuracy:**
   - If skill says "automatically invoked by X" → read X and confirm
   - If skill says "only for type: java" → check no other types use it
   - If skill says "blocks commit on CRITICAL" → verify this behavior exists

**Common stale references found:**
- ❌ "invoked by old-skill-name" (skill was renamed)
- ❌ "uses TodoWrite tool" (deprecated tool name)
- ❌ "see docs/ARCHITECTURE.md" (file moved to DESIGN.md)
- ❌ "runs with --flag" (flag removed in newer version)

#### 2.2 Logical Soundness

**Manual procedure:**

1. **Walk through the workflow as if executing it:**
   - Can each step actually be performed?
   - Do commands have correct syntax?
   - Are file paths correct?
   - Do variables exist when referenced?

2. **Check decision logic:**
   - If-then branches cover all cases?
   - No contradictory conditions?
   - Loops have clear exit conditions?
   - Edge cases handled?

3. **Verify prerequisites:**
   - If skill requires X to exist, does it check for X?
   - If skill assumes Y is true, does it validate Y?
   - Dependencies in correct order?

**Example logical errors found:**
- ❌ "Read DESIGN.md" but never checked it exists → fails on first use
- ❌ "If Java project... else if Skills project" → missing else for other types
- ❌ "grep for X, then read $MATCH" → $MATCH variable never set
- ❌ "Run tests, then commit" → no handling for test failures

#### 2.3 Contradiction Detection

**Manual procedure:**

1. **Within-skill contradictions:**
   - Section A says "always do X"
   - Section B says "never do X"
   - Root cause: copy-paste or incremental edits

2. **Cross-skill contradictions:**
   - Skill A: "java-git-commit always syncs DESIGN.md"
   - Skill B: "DESIGN.md sync is optional"
   - Resolution: Determine which is authoritative

3. **Documentation vs. behavior contradictions:**
   - CLAUDE.md: "skill-review blocks on CRITICAL"
   - skill-review: "WARNING level blocks commits"
   - Fix: Make behavior match documentation (or update docs)

**Systematic check:**
- List all imperative statements (MUST, ALWAYS, NEVER)
- Search for opposing statements about same topic
- Resolve by determining correct behavior
- Update all references to be consistent

#### 2.4 Completeness Analysis

**Manual procedure:**

1. **Edge case coverage:**
   - What if file doesn't exist?
   - What if command fails?
   - What if user says "no"?
   - What if input is empty/malformed?

2. **Error handling:**
   - Every command that can fail has failure handling?
   - User is informed of problems with actionable advice?
   - Graceful degradation where possible?

3. **Documentation gaps:**
   - Every mentioned concept is defined?
   - Acronyms spelled out on first use?
   - Examples provided for complex instructions?
   - "Why" explained, not just "what"?

**Gap detection pattern:**
```
Read skill start to finish.
For each instruction:
  - Could a new Claude follow this without prior context?
  - Are there assumptions not stated?
  - Are there terms not defined?
  - Are there examples missing?
```

#### 2.5 Readability & Clarity

**Manual procedure:**

1. **Language clarity:**
   - No ambiguous pronouns (it, this, that without clear antecedent)
   - No double negatives
   - Active voice preferred over passive
   - Consistent terminology (not "sync" in one place, "update" in another)

2. **Structure coherence:**
   - Sections in logical order
   - Related content grouped together
   - Clear transitions between sections
   - Headings accurately describe content

3. **Cognitive load:**
   - Not too many concepts introduced at once
   - Complex ideas broken into steps
   - Tables used for dense reference material
   - Flowcharts for complex decisions

**Red flags:**
- Sentences over 40 words (usually can be split)
- Paragraphs over 8 lines (usually can be broken up)
- More than 3 levels of nesting (restructure)
- Jargon without definition (explain or link)

#### 2.6 Duplication & Overlap

**Manual procedure:**

1. **Unnecessary duplication:**
   - Same instructions in multiple skills → extract to shared foundation
   - Same example repeated → reference once, link from others
   - Same validation logic → create common validation skill

2. **Troublesome overlap:**
   - Two skills that trigger on similar conditions → clarify boundaries
   - Two skills that do similar things → merge or differentiate
   - Two sources of truth for same information → choose canonical location

3. **Gaps between skills:**
   - Workflow ends at skill A, should start at skill B, but no chaining
   - Concept mentioned in skill A, detailed in skill B, but no reference
   - Related skills don't mention each other

**Resolution pattern:**
- Duplication → DRY (extract common, reference from specific)
- Overlap → Differentiate (clear triggering conditions, different purposes)
- Gaps → Connect (add cross-references, chaining)

#### 2.7 Skill Chaining Correctness

**Manual procedure:**

1. **Build the complete chain graph:**
   ```
   git-commit (skills mode)
     ├─ skill-review (if SKILL.md staged)
     ├─ readme-sync.md (if skill changes)
     └─ update-claude-md (if CLAUDE.md exists)

   git-commit (java mode)
     └─ "Use java-git-commit instead"

   java-git-commit
     ├─ java-code-review (if not done)
     │   └─ java-security-audit (if security-critical)
     ├─ java-update-design (if DESIGN.md exists)
     └─ update-claude-md (if CLAUDE.md exists)
   ```

2. **Verify each link:**
   - Parent skill actually invokes child
   - Child skill acknowledges parent
   - Conditions for invocation are clear
   - No circular dependencies

3. **Check chain completeness:**
   - User request → terminal skill (produces artifact)
   - No dead-end skills (invoked but invoke nothing)
   - No orphan skills (never invoked, not user-invocable)

#### 2.8 Third-Party Skill Documentation

**Manual procedure:**

**CRITICAL: Verify no third-party skills are documented in README.md or CLAUDE.md.**

1. **Identify third-party skills:**
   ```bash
   # Check .gitignore for excluded skill directories
   grep '/$' .gitignore | grep -v '^#' | grep -v '^\.'

   # Check for superpowers:* references
   grep -E 'superpowers:|skill-creator|frontend-design:' README.md CLAUDE.md
   ```

2. **Verify exclusions:**
   - ✅ All third-party skill directories in .gitignore
   - ✅ No third-party skills in README.md "Skills" section
   - ✅ No third-party skills in README.md "Skill Chaining Reference" table
   - ✅ No third-party skills in README.md "Repository Structure" section
   - ✅ No third-party skills in CLAUDE.md "Key Skills" section
   - ✅ No third-party skills in workflow diagrams

3. **Check for stale references:**
   - Search for skill names that appear in .gitignore
   - Verify removal from all documentation
   - Check for indirect references (e.g., "use skill-creator to...")

**Common violations found:**
- ❌ skill-creator documented in Development Tools section
- ❌ superpowers:* skills listed in chaining table
- ❌ Third-party skills in repository structure diagram
- ❌ Workflow examples showing third-party skill invocation

**Fix procedure:**
1. Remove all documentation references
2. Verify .gitignore entry exists
3. Run consistency check: `grep -r "<skill-name>" README.md CLAUDE.md` should return no results

---

### Functional Testing (Level 3)

**These checks execute skills against real scenarios.**

#### 3.1 Test Case Structure

**Location:** Each skill directory can have `tests/` subdirectory

**Structure:**
```
skill-name/
  SKILL.md
  tests/
    test_cases.json       # Test definitions
    fixtures/             # Input files for tests
    expected/             # Expected outputs
    results/              # Actual outputs (gitignored)
```

**Test case format:**
```json
{
  "skill_name": "java-git-commit",
  "tests": [
    {
      "id": "basic-commit",
      "description": "Commit single Java file change",
      "setup": "scripts/setup_basic_commit.sh",
      "prompt": "commit these changes",
      "expected_behavior": {
        "invokes_skills": ["java-update-design", "update-claude-md"],
        "creates_commit": true,
        "commit_message_matches": "^(feat|fix|refactor)\\(.*\\):.*",
        "files_modified": ["docs/DESIGN.md", "CLAUDE.md"]
      },
      "assertions": [
        {"type": "file_exists", "path": "docs/DESIGN.md"},
        {"type": "git_commit_exists", "message_contains": "Co-Authored-By: Claude"},
        {"type": "skill_invoked", "skill": "java-update-design"}
      ]
    }
  ]
}
```

#### 3.2 Test Execution Framework

**Script location:** `scripts/testing/run_skill_tests.py`

**Process:**
1. Create isolated git worktree for each test
2. Run setup script to prepare state
3. Invoke Claude with skill loaded and test prompt
4. Capture outputs (files created, commits made, skills invoked)
5. Compare against expected behavior
6. Report pass/fail with details

**Execution:**
```bash
# Run all tests for a skill
python scripts/testing/run_skill_tests.py java-git-commit

# Run specific test
python scripts/testing/run_skill_tests.py java-git-commit --test basic-commit

# Run all skill tests in repository
python scripts/testing/run_skill_tests.py --all
```

#### 3.3 Regression Test Suite

**Location:** `tests/regression/`

**Purpose:** Prevent known issues from reoccurring

**Structure:**
```
tests/regression/
  issue-001-cso-violation.json          # CSO description had workflow
  issue-002-circular-dependency.json    # Skill A → B → A loop
  issue-003-missing-bidirectional.json  # A references B, B doesn't reference A
  issue-004-stale-tool-name.json        # Referenced deprecated TodoWrite
```

**Each regression test:**
- Documents the original issue
- Provides failing example
- Validates the fix
- Runs on every commit

**Example regression test:**
```json
{
  "issue_id": "001",
  "title": "CSO Violation - Workflow in Description",
  "description": "Skill had workflow summary in description, causing expensive wallpaper",
  "original_violation": {
    "skill": "superpowers:execute-plan",
    "description": "Use when executing plans - dispatches subagent per task with code review between tasks"
  },
  "why_it_failed": "Claude followed description instead of reading full skill",
  "fix_applied": "Removed workflow details from description",
  "validation": {
    "type": "cso_check",
    "description_must_not_contain": ["dispatches", "per task", "code review"]
  }
}
```

**Regression test execution:**
```bash
# Run all regression tests
python scripts/testing/run_regression_tests.py

# Verify specific issue is fixed
python scripts/testing/run_regression_tests.py --issue 001
```

---

### Standards & Best Practices

**Follow these established standards for skill validation:**

#### Documentation Standards

| Standard | Reference | Application |
|----------|-----------|-------------|
| **Markdown CommonMark** | https://commonmark.org/ | All SKILL.md files |
| **YAML 1.2** | https://yaml.org/spec/1.2/ | Frontmatter only |
| **Graphviz DOT** | https://graphviz.org/doc/info/lang.html | Flowcharts |
| **Conventional Commits** | https://www.conventionalcommits.org/ | Commit message format (not skill content) |

#### Code Quality Standards (for scripts/)

| Standard | Tool | Application |
|----------|------|-------------|
| **Python PEP 8** | `flake8`, `black` | All .py scripts |
| **Shell POSIX** | `shellcheck` | All .sh scripts |
| **Type hints** | `mypy` | Python validation scripts |

#### Test Coverage Standards

**Minimum test coverage for production skills:**
- ✅ 100% of user-invocable skills have at least 1 functional test
- ✅ 100% of auto-invoked skills have regression tests
- ✅ All flowchart decision branches covered by tests
- ✅ All error conditions have failure tests

**Coverage tracking:**
```bash
# Generate coverage report
python scripts/testing/test_coverage.py --report

# Output:
# java-git-commit: 5/5 branches tested (100%)
# git-commit: 3/4 branches tested (75%) - missing: type: custom test
# skill-review: 8/8 validations tested (100%)
```

---

### Integration with Skill Workflows

**How validation integrates into development workflows:**

#### Pre-Commit Validation (Tier: COMMIT, <2s budget)

**Triggered by:** `git-commit` when SKILL.md files are staged

**Workflow:**
```
git-commit (for type: skills)
  ├─ Run COMMIT tier validation (<2s budget)
  │   ├─ validate_frontmatter.py
  │   ├─ validate_cso.py
  │   ├─ validate_flowcharts.py
  │   ├─ validate_references.py
  │   ├─ validate_naming.py
  │   ├─ validate_sections.py
  │   └─ validate_structure.py
  │
  ├─ skill-review (manual deep checks, optional)
  │   ├─ Reference accuracy
  │   ├─ Logical soundness
  │   ├─ Completeness
  │   └─ Block on CRITICAL findings
  │
  ├─ readme-sync.md (if skills changed)
  └─ update-claude-md (if exists)
```

**Command executed:**
```bash
python3 scripts/validate_all.py --tier commit
```

**Exit behavior:**
- ❌ **CRITICAL findings → Block commit** (frontmatter invalid, flowchart broken, references missing)
- ⚠️ **WARNING findings → Show but allow** (naming convention violation, missing Common Pitfalls)
- ℹ️ **NOTE findings → Log only** (could add examples, could improve clarity)

#### Pre-Push Validation (Tier: PUSH, <30s budget)

**Triggered by:** `git push` hook (to be configured)

**Workflow:**
```
git push
  ├─ Run PUSH tier validation (<30s budget)
  │   ├─ All COMMIT tier validators (from above)
  │   ├─ validate_cross_document.py
  │   ├─ validate_temporal.py
  │   ├─ validate_usability.py
  │   ├─ validate_edge_cases.py
  │   ├─ validate_behavior.py
  │   └─ validate_readme_sync.py
  │
  ├─ Run regression tests
  │   └─ run_regression_tests.py
  │
  └─ Run test coverage
      └─ test_coverage.py
```

**Command executed:**
```bash
python3 scripts/validate_all.py --tier push
```

**Why pre-push:** Cross-document consistency checks, prevents stale state reaching remote, moderate cost (<30s).

#### CI Validation (Tier: CI, <5min budget)

**Triggered by:** GitHub Actions on push to main or PR

**Workflow:**
```
CI Pipeline
  ├─ Run CI tier validation (<5min budget)
  │   ├─ All COMMIT tier validators
  │   ├─ All PUSH tier validators
  │   ├─ validate_python_quality.py (mypy, flake8, bandit)
  │   └─ run_skill_tests.py (functional tests with worktrees)
  │
  └─ Generate comprehensive report
      └─ generate_report.py
```

**Command executed:**
```bash
python3 scripts/validate_all.py --tier ci --json
```

**Why CI:** Expensive operations (git worktrees, static analysis), comprehensive validation before merging.

#### Deep Analysis Review

**Triggered by:** User request ("do a deep analysis") or before release

**Workflow:**
```
deep-analysis
  ├─ Run ALL Level 1 automated checks
  ├─ Run ALL Level 2 manual procedures
  ├─ Run Level 3 functional tests
  ├─ Generate comprehensive report
  └─ Create action items for findings
```

**Report format:**
```markdown
# Deep Analysis Report - 2026-03-30

## Summary
- Skills analyzed: 45
- Automated checks: 312 passed, 3 failed
- Manual reviews: 45 completed
- Functional tests: 89 passed, 2 failed
- Total issues: 14 (4 critical, 6 warning, 4 note)

## Critical Issues (Must Fix)
1. java-security-audit: Flowchart has invalid dot syntax
2. quarkus-flow-dev: References non-existent `quarkus-reactive-dev`
3. maven-dependency-update: CSO violation in description
4. java-update-design: Missing Success Criteria section

## Warning Issues (Should Fix)
...

## Functional Test Failures
1. java-git-commit/basic-commit: DESIGN.md not updated
2. skill-review/cso-check: False negative on workflow keywords

## Recommendations
...
```

#### Continuous Integration

**Triggered by:** Push to repository, Pull Request

**GitHub Actions workflow:**
```yaml
name: Skill Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Automated Validation
        run: |
          python scripts/validate_all.py --strict

      - name: Run Regression Tests
        run: |
          python scripts/testing/run_regression_tests.py

      - name: Check Documentation Sync
        run: |
          python scripts/check_readme_sync.py
          python scripts/check_claude_md_sync.py

      - name: Report Results
        run: |
          python scripts/generate_report.py --output report.md
          cat report.md >> $GITHUB_STEP_SUMMARY
```

---

### Validation Script Roadmap

**Scripts organized by validation tier for optimal performance:**

#### COMMIT tier (<2s budget)

**Existing validators (mechanical/structural checks):**
1. ✅ **`validate_frontmatter.py`** - YAML structure, required fields [COMMIT]
2. ✅ **`validate_cso.py`** - Description compliance [COMMIT]
3. ✅ **`validate_flowcharts.py`** - Graphviz syntax, semantic labels [COMMIT]
4. ✅ **`validate_references.py`** - Cross-reference integrity [COMMIT]
5. ✅ **`validate_naming.py`** - Naming conventions [COMMIT]
6. ✅ **`validate_sections.py`** - Required sections [COMMIT]
7. ✅ **`validate_structure.py`** - File organization [COMMIT]

**Why pre-commit:** Fast (<2s total), block corruption before git history.

#### PUSH tier (<30s budget)

**Semantic validators (cross-document/consistency checks):**
8. ✅ **`validate_cross_document.py`** - Cross-document consistency [PUSH]
9. ✅ **`validate_temporal.py`** - Temporal consistency (stale references) [PUSH]
10. ✅ **`validate_usability.py`** - Usability/UX validator [PUSH]
11. ✅ **`validate_edge_cases.py`** - Edge case coverage validator [PUSH]
12. ✅ **`validate_behavior.py`** - Behavioral consistency validator [PUSH]

**Test infrastructure:**
13. ✅ **`validate_readme_sync.py`** - README/CLAUDE sync validator [PUSH]
14. ✅ **`run_regression_tests.py`** - Regression test runner [PUSH]
15. ✅ **`test_coverage.py`** - Coverage reporting [PUSH]
16. ✅ **`run_skill_tests.py`** - Functional test runner (git worktrees) [CI]

**Why pre-push:** Moderate cost (<30s), cross-file checks, prevents bad state reaching remote.

#### CI/Scheduled Tier (<5min budget)

**Expensive tests:**
17. ✅ **`validate_python_quality.py`** - mypy, flake8, bandit [CI]

**Orchestration & Reporting:**
18. ✅ **`validate_all.py`** - Master orchestrator with `--tier` support [UNIVERSAL]
19. **`generate_report.py`** - Comprehensive reporting [CI] (TO BE CREATED)

**Why CI:** Expensive operations (worktrees, static analysis), comprehensive validation before merging.

#### Validation Tiering Strategy

**validate_all.py usage:**
```bash
# Pre-commit: fast mechanical checks only
python3 scripts/validate_all.py --tier commit

# Pre-push: commit validators + cross-document + tests
python3 scripts/validate_all.py --tier push

# CI: all validators + functional tests + python quality
python3 scripts/validate_all.py --tier ci
```

**Tiers are accumulative:**
- `push` includes `commit` validators
- `ci` includes `commit` + `push` validators

**Performance budgets enforced:**
- Commit: <2s (immediate feedback)
- Push: <30s (before sharing)
- CI: <5min (comprehensive)

**Each script should:**
- Exit with code 0 (pass) or non-zero (fail)
- Output JSON results for parsing
- Support `--verbose` flag for detailed output
- Support `--fix` flag for auto-fixable issues (where safe)
- Include TIER annotation in docstring
- Include unit tests for the validator itself

---

### Deep Analysis Checklist

**When user requests deep analysis, systematically perform ALL checks:**

#### Automated Checks (Run Scripts)
- [ ] Frontmatter validation (all skills)
- [ ] CSO compliance (all skills)
- [ ] Flowchart validation (skills with flowcharts)
- [ ] Cross-reference integrity (all references)
- [ ] Naming convention compliance (all skills)
- [ ] Required sections (by skill type)
- [ ] File organization (all skills)

#### Manual Analysis (Systematic Review)
- [ ] Reference accuracy (bidirectional verification)
- [ ] Logical soundness (workflow walkthrough)
- [ ] Contradiction detection (within & across skills)
- [ ] Completeness analysis (edge cases, error handling)
- [ ] Readability & clarity (language, structure)
- [ ] Duplication & overlap (DRY, differentiation)
- [ ] Skill chaining correctness (graph validation)

#### Functional Testing
- [ ] Run all skill functional tests
- [ ] Run all regression tests
- [ ] Test coverage report
- [ ] New test case identification

#### Documentation Sync
- [ ] README.md accuracy (chaining table, skill list)
- [ ] CLAUDE.md accuracy (architecture, conventions)
- [ ] Cross-references up to date
- [ ] Examples still valid

#### Report Generation
- [ ] Findings categorized (CRITICAL/WARNING/NOTE)
- [ ] Action items prioritized
- [ ] Regression test coverage verified
- [ ] Recommendations documented

**Time estimate:** 2-4 hours for full deep analysis of 40+ skills

---

### Preventing Regressions

**Known issues that MUST NOT recur:**

#### Issue Registry

**Location:** `docs/known-issues.md`

**Format:**
```markdown
## Issue #001: CSO Violation - Workflow in Description

**Symptom:** Skill has workflow summary in description field

**Impact:** Claude follows description instead of reading skill body (expensive wallpaper)

**Root Cause:** Description field is visible in skill list, tempting to summarize workflow

**Detection:** Automated - `validate_cso.py` checks for workflow keywords

**Prevention:**
- CSO validation in pre-commit hook
- Regression test issue-001-cso-violation.json
- Documentation in CLAUDE.md "Frontmatter Requirements"

**Last Occurrence:** 2026-01-15 (fixed in commit abc123)

**Test Coverage:** ✅ Automated + Regression test
```

#### Common Regression Patterns

| Pattern | How It Happens | Prevention |
|---------|----------------|------------|
| **CSO violations** | New skill copies old bad description | Pre-commit CSO validation |
| **Broken references** | Skill renamed, references not updated | Automated reference integrity check |
| **Missing bidirectional links** | Skill A added, forgot to update Skill B | Manual checklist + reference validation |
| **Stale tool names** | Tool renamed, old examples not updated | Grep for deprecated names in validation |
| **Flowchart syntax errors** | Copy-paste from different syntax variant | Graphviz validation pre-commit |
| **Contradictory statements** | Incremental edits without full context | Deep analysis before releases |
| **Missing Success Criteria** | New artifact-producing skill added | Section validation script |

#### Regression Prevention Workflow

**For every bug fix:**

1. **Document the issue** in `docs/known-issues.md`
2. **Create regression test** in `tests/regression/issue-XXX.json`
3. **Add validation** (automated if possible)
4. **Update checklists** (if new category of issue)
5. **Run full test suite** to verify fix doesn't break other things

**For every new skill:**

1. **Run all automated checks** before first commit
2. **Create functional tests** (at least 1 happy path)
3. **Verify in skill-review** checklist
4. **Update README.md** and potentially CLAUDE.md
5. **Deep analysis review** before marking complete

---

### Success Criteria for QA Framework

**The QA framework is working when:**

- ✅ Zero CRITICAL findings pass pre-commit validation
- ✅ All skills have at least 1 functional test
- ✅ All known issues have regression tests
- ✅ Deep analysis finds ≤5 WARNING issues per 40 skills
- ✅ No duplicate issues across releases (regressions blocked)
- ✅ New contributors can run validation locally
- ✅ CI blocks PRs with validation failures

**Not complete until:**
- Validation scripts created (Phase 1-3 minimum)
- Regression test suite established
- CI integration configured
- Documentation reviewed and approved

---

## Document Sync Quality Assurance

**CRITICAL: Universal validation for all .md files being synced across all project types.**

Document corruption can occur during any sync operation (README.md, CLAUDE.md, DESIGN.md, custom primary docs). This framework prevents corruption before it reaches git commits.

### When This Applies

**All project types:**
- **type: skills** → README.md, CLAUDE.md (via readme-sync.md, update-claude-md)
- **type: java** → DESIGN.md, CLAUDE.md (via java-update-design, update-claude-md)
- **type: custom** → Primary doc (VISION.md, THESIS.md, API.md, etc.), CLAUDE.md (via update-primary-doc, update-claude-md)
- **type: generic** → CLAUDE.md (via update-claude-md)

**Any document being automatically synchronized is at risk.**

### Validation Script

**Location:** `scripts/validate_document.py`

**Universal validation that works on any .md file:**

```bash
python scripts/validate_document.py <filepath>
```

**Exit codes:**
- `0` - No issues (clean document)
- `1` - CRITICAL issues (blocks commit)
- `2` - WARNING issues (should review)

**What it detects:**

1. **Duplicate section headers** (CRITICAL)
   - Same `## Header` appears multiple times
   - Usually caused by copy-paste errors during sync

2. **Corrupted table structures** (CRITICAL)
   - Table header followed by prose instead of separator/data rows
   - Example: `| Col1 | Col2 |` followed by "This is a description" instead of `|---|---|`

3. **Orphaned sections** (WARNING)
   - Section header with no content before next header
   - May indicate incomplete sync or missing content

4. **Large structural changes** (WARNING)
   - More than 100 lines modified
   - Requires manual structural review

### Running Validators Locally

**Before committing changes, test them locally to catch issues early:**

#### Validating a Single Document

```bash
# Validate README.md before staging
python scripts/validate_document.py README.md

# Validate DESIGN.md after editing
python scripts/validate_document.py docs/DESIGN.md

# Validate custom primary doc
python scripts/validate_document.py docs/vision.md
```

**Output examples:**

**Clean document (exit code 0):**
```
✅ No issues found in README.md
```

**Critical issues (exit code 1):**
```
❌ CRITICAL issues found in DESIGN.md:
  - Line 45: Duplicate header "## Architecture Overview"
  - Line 127: Corrupted table (header followed by prose)

Fix these issues before committing.
```

**Warnings (exit code 2):**
```
⚠️  WARNING issues found in CLAUDE.md:
  - Line 234: Orphaned section header (no content before next section)
  - Large structural change: 156 lines modified

Review recommended but not blocking.
```

#### Validating All Staged Files

```bash
# Validate all .md files about to be committed
git diff --staged --name-only | grep '\.md$' | while read file; do
  python scripts/validate_document.py "$file"
done
```

#### Validating Specific Project Type Docs

**For type: skills repositories:**
```bash
# Validate README.md and CLAUDE.md
python scripts/validate_document.py README.md
python scripts/validate_document.py CLAUDE.md
```

**For type: java repositories:**
```bash
# Validate DESIGN.md and CLAUDE.md
python scripts/validate_document.py docs/DESIGN.md
python scripts/validate_document.py CLAUDE.md
```

**For type: custom repositories:**
```bash
# Validate your primary doc (example: vision.md)
python scripts/validate_document.py docs/vision.md
python scripts/validate_document.py CLAUDE.md
```

#### Common Workflow: Edit → Validate → Stage → Commit

```bash
# 1. Edit document
vim README.md

# 2. Validate locally
python scripts/validate_document.py README.md

# 3. If clean, stage
git add README.md

# 4. Commit (validation runs again automatically)
# git-commit invokes validation as pre-commit gate
```

**Why validate locally:**
- Catch corruption before staging
- Faster feedback loop (no need to attempt commit)
- Understand issues in context (see the file while fixing)
- Learn document quality patterns over time

**Integration with workflows:**
- Local validation is **optional** (but recommended)
- Pre-commit validation is **mandatory** (runs automatically)
- Both use the same `validate_document.py` script (consistent rules)

### Integration Points

**All sync workflows MUST validate after applying changes:**

#### update-claude-md Step 6 (after user confirms YES)

```bash
# Apply proposed changes
# Then validate:
python scripts/validate_document.py CLAUDE.md
if [ $? -eq 1 ]; then
  echo "❌ CRITICAL: Validation failed, reverting changes"
  git restore CLAUDE.md
  exit 1
fi
```

#### java-update-design Step 6 (after user confirms YES)

```bash
# Apply proposed changes
# Then validate:
python scripts/validate_document.py docs/DESIGN.md
if [ $? -eq 1 ]; then
  echo "❌ CRITICAL: Validation failed, reverting changes"
  git restore docs/DESIGN.md
  exit 1
fi
```

#### update-primary-doc Step 6 (after user confirms YES)

```bash
# Apply proposed changes to primary doc
# Then validate:
python scripts/validate_document.py <primary-doc-path>
if [ $? -eq 1 ]; then
  echo "❌ CRITICAL: Validation failed, reverting changes"
  git restore <primary-doc-path>
  exit 1
fi
```

#### readme-sync.md Step 6 (after user confirms YES)

```bash
# Apply proposed changes
# Then validate:
python scripts/validate_document.py README.md
if [ $? -eq 1 ]; then
  echo "❌ CRITICAL: Validation failed, reverting changes"
  git restore README.md
  exit 1
fi
```

### Pre-Commit Gate (git-commit)

**Before committing, validate ALL staged .md files:**

```markdown
### Step 1c — Validate documentation files

Check for staged .md files (excluding SKILL.md):
```bash
git diff --staged --name-only | grep '\.md$' | grep -v 'SKILL\.md$'
```

**For each .md file found:**
```bash
python scripts/validate_document.py <file>
```

**If validation fails:**
- **CRITICAL (exit code 1):** BLOCK commit, show issues, ask user to fix
- **WARNING (exit code 2):** Show warnings, ask user to confirm before proceeding
```

**This runs in ALL project types** (skills, java, custom, generic).

### Portable Implementation

**The validation script is portable:**

1. **Copy to any project using these skills:**
   ```bash
   cp scripts/validate_document.py <target-project>/scripts/
   ```

2. **Works standalone (no dependencies):**
   - Pure Python 3
   - No external libraries required
   - Uses only stdlib (sys, re, pathlib, collections, subprocess)

3. **Integrates with any sync workflow:**
   - Language-agnostic (checks .md syntax, not content semantics)
   - Works on any document type (README, DESIGN, VISION, THESIS, etc.)
   - Project-type independent

### Common Document Corruption Patterns

**These patterns are detected automatically:**

| Pattern | Example | Detection | Prevention |
|---------|---------|-----------|------------|
| **Duplicate headers during restructure** | Two "## Skills" sections | Duplicate header check | Validate before commit |
| **Table header + prose** | `\| Col1 \| Col2 \|` followed by description text | Corrupted table check | Validate table format |
| **Copy-paste from wrong section** | Section content pasted under wrong header | Orphaned section check | Review large diffs |
| **Incomplete sync** | Section header added but content not synced | Orphaned section check | Validate completeness |
| **Merge conflict corruption** | `<<<<<<< HEAD` markers in document | Git diff check | Pre-commit validation |

### Regression Prevention

**Add to Issue Registry:**

```markdown
## Issue #002: Document Corruption During Sync

**Symptom:** Duplicate sections, corrupted tables, orphaned headers

**Impact:** Unreadable documentation, broken links, user confusion

**Root Cause:** Sync operations (update-claude-md, java-update-design, etc.) can introduce corruption when proposing large changes

**Detection:** Automated - `validate_document.py` checks all .md files

**Prevention:**
- Universal validation in all sync workflows
- Pre-commit gate in git-commit for all project types
- Automated revert if validation fails
- Documentation in CLAUDE.md "Document Sync Quality Assurance"

**Test Coverage:** ✅ Automated validation on all sync operations
```

### Success Criteria

Document sync quality assurance is working when:

- ✅ All sync workflows validate before staging
- ✅ git-commit validates all staged .md files (all project types)
- ✅ CRITICAL corruption is automatically caught and reverted
- ✅ Zero document corruption reaches commits
- ✅ Validation script is portable to all projects using these skills
- ✅ Users never need to manually check for corruption

**Not complete until:**
- validate_document.py created and tested
- All 4 sync workflows updated (update-claude-md, java-update-design, update-primary-doc, readme-sync.md)
- git-commit updated to validate all .md files
- CLAUDE.md documentation complete
