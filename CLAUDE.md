# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a skill collection for Claude Code, providing specialized guidance for Java/Quarkus development workflows. Skills are markdown files with YAML frontmatter that Claude Code loads to execute specific development tasks.

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

### Skill Chaining

Skills explicitly reference each other to create workflows. The README documents the complete chaining matrix, but when editing skills:

1. **Add cross-references in "Skill Chaining" sections** (capitalized, not "Skill chaining")
2. **Make references bidirectional** when appropriate (e.g., java-security-audit ↔ java-code-review)
3. **Use Prerequisites sections** for layered skills (e.g., quarkus-flow-testing builds on java-dev and quarkus-flow-dev)
4. **Generic principles skills are never invoked directly** — they're referenced via Prerequisites by language/framework-specific skills

Example chaining patterns:
```
# Java repositories with both DESIGN.md and CLAUDE.md:
java-dev → java-code-review → java-git-commit → update-design + update-claude-md (automatic)

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

## Editing Skills

When modifying existing skills:

1. **Check README first** — the Skill Chaining Reference table shows the complete dependency graph
2. **Update cross-references** — if you add chaining, update both skills (source and target)
3. **Preserve CSO descriptions** — don't add workflow summaries to frontmatter
4. **Test flowcharts** — invalid dot syntax breaks skill loading
5. **Maintain Prerequisites** — layered skills (quarkus-flow-*) must reference their foundations

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
- `git-commit` — automatically invokes `update-claude-md` (if CLAUDE.md exists)
- `java-git-commit` — automatically invokes `update-design` and `update-claude-md` (if docs exist)
- `java-code-review` — triggers `java-security-audit` for security-critical code

**Specialized skills** (domain-specific):
- `quarkus-flow-dev` — builds on `java-dev`, extended by `quarkus-flow-testing`
- `java-security-audit` — OWASP Top 10 for Java/Quarkus, triggered by `java-code-review`
- `maven-dependency-update` — Maven BOM management, builds on `dependency-management-principles`
- `quarkus-observability` — Quarkus observability config, builds on `observability-principles`
- `update-design` — DESIGN.md synchronization (architecture documentation), invoked by `java-git-commit`
- `update-claude-md` — CLAUDE.md synchronization (workflow documentation), invoked by `git-commit` and `java-git-commit`

## README Synchronization

When adding/modifying skills, update README sections:

- **Skills** section: Add/update skill description with trigger conditions
- **How Skills Work Together**: Update chaining workflows if changed
- **Skill Chaining Reference** table: Add new chaining relationships
- **Key Features**: Note new flowcharts, Prerequisites sections, etc.

The README is the single source of truth for the skill collection's architecture.
