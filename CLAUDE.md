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

**Note:** This repository does not use modular documentation. Skills use single `SKILL.md` files.

For projects that split large documents into linked modules (e.g., `DESIGN.md` → `docs/design/architecture.md` + `api.md` + `data-model.md`), with automatic discovery, validation, and sync across all modules:

**See:** 📖 **[QUALITY.md § Modular Documentation Quality Assurance](QUALITY.md#modular-documentation-quality-assurance)** and **[README.md § Modular Documentation](README.md#modular-documentation)**

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

**Comprehensive validation ensures skills maintain structural integrity, logical soundness, and documentation accuracy.**

Skills are infrastructure code guiding AI behavior across millions of invocations. Quality issues compound exponentially. This framework provides automated checks (scripts), semantic analysis (Claude), and functional testing.

### Quality Assurance Philosophy

**Scripts handle mechanical checks (syntax, structure, format).**
**Claude handles semantic analysis (logic, contradictions, completeness).**

For complete details on the division of labor, validation tiers, what gets checked, and integration patterns:
📖 **[QUALITY.md § The Architecture: Scripts + Claude](QUALITY.md#the-architecture-scripts--claude)**

### Automated Validation

**14 validators across 3 tiers (COMMIT/PUSH/CI):**

For complete validator specifications, tier assignments, and implementation details:
📖 **[QUALITY.md § Implementation Status](QUALITY.md#implementation-status)**

**Pre-Commit Checklist integration:** See § Pre-Commit Checklist for Skills below for mandatory validation hooks.

### Deep Analysis Procedures

When user requests deep analysis of skills ("/skill-review", "do a deep analysis", "comprehensive review"):

📖 **[QUALITY.md § Deep Analysis Validation](QUALITY.md#deep-analysis-validation-level-2)**

**Mandatory checklist:**
- [ ] Run all automated checks (`python scripts/validate_all.py --tier commit`)
- [ ] Perform all manual analysis procedures (reference accuracy, logical soundness, completeness, etc.)
- [ ] Document findings by severity (CRITICAL/WARNING/NOTE)
- [ ] Create action items for CRITICAL/WARNING findings

### Validation Infrastructure

For complete inventory of validation scripts by tier:
📖 **[QUALITY.md § Validation Script Roadmap](QUALITY.md#validation-script-roadmap)**

**Quick reference:**
- **COMMIT tier (<2s)**: 7 validators (frontmatter, CSO, flowcharts, references, naming, sections, structure)
- **PUSH tier (<30s)**: 5 validators + 3 test tools (cross-document, temporal, usability, edge cases, behavior, readme sync, regression tests, coverage)
- **CI tier (<5min)**: Python quality (mypy, flake8, bandit) + functional tests

### Success Criteria

Validation framework is working when:
- ✅ Zero CRITICAL findings pass pre-commit
- ✅ All skills have functional tests
- ✅ All known issues have regression tests
- ✅ Deep analysis finds ≤5 WARNING issues per 40 skills
- ✅ No duplicate issues across releases
- ✅ CI blocks PRs with validation failures

For complete success criteria and implementation status:
📖 **[QUALITY.md § Success Criteria for QA Framework](QUALITY.md#success-criteria-for-qa-framework)**

---

## Document Sync Quality Assurance

**Universal validation prevents document corruption during sync operations across all project types.**

For complete details on validation rules, integration points, corruption patterns, and regression prevention:
📖 **[QUALITY.md § Document Sync Quality Assurance](QUALITY.md#document-sync-quality-assurance)**

### Running Validators Locally

**Before committing changes, test locally to catch issues early:**

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

---

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
