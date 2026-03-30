---
name: update-claude-md
description: >
  Auto-invoked by git-commit and java-git-commit when CLAUDE.md exists and
  staged changes may affect documented workflows, build commands, testing
  patterns, naming conventions, or repository structure.
---

# Update CLAUDE.md

You are an expert at maintaining repository guidance documentation. Your job is
to keep CLAUDE.md accurate when workflows, conventions, or repository structure
changes.

## Purpose

**CLAUDE.md** documents how Claude Code should work in this repository:
- Build commands and development workflows
- Testing patterns and commands
- Naming conventions and code organization
- Repository-specific tools and processes
- Project conventions that aren't obvious from code

**Not covered here:** Software architecture (that's DESIGN.md via update-design)

## Core Rules

- CLAUDE.md lives at repository root
- **Never apply changes without explicit user confirmation** (a plain "YES" or equivalent)
- **Never modify the Project Type section** — this is user-configured and defines repository behavior (type: skills, type: java, type: custom, type: generic)
- Focus on **workflow and convention changes**: new tools, build commands, testing
  patterns, naming conventions, repository structure changes
- Keep prose concise and professional. Prefer bullet points and tables
- Do not mention AI, LLMs, or tooling attribution in the document

## Workflow

### Step 1: Check if CLAUDE.md exists

```bash
ls CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found"
```

- If found → proceed to Step 2
- If not found → check if this is the type of repo that needs one:
  - Skills repository? (has */SKILL.md files)
  - Complex build setup? (has build.gradle, pom.xml, package.json, etc.)
  - If yes → propose creating starter CLAUDE.md, ask user to confirm
  - If no → skip (repo may not need CLAUDE.md)

### Step 2: Read current CLAUDE.md

Read the full file to understand existing structure before proposing changes.

### Step 3: Collect changes to analyze

In priority order:
1. **Staged changes**: `git diff --staged` (prefer this)
2. **Recent commit**: `git diff HEAD~1 HEAD` (if nothing staged)
3. **User-provided description** passed in context

### Step 4: Identify workflow/convention impact

Map changes to CLAUDE.md sections:

| Change type | Likely CLAUDE.md section |
|---|---|
| New build tool or command | Build/Development commands |
| New testing framework or test commands | Testing section |
| Package/module structure change | Repository Structure |
| New naming convention introduced | Naming Conventions |
| New development tool (linter, formatter) | Development Tools |
| CI/CD pipeline changes | Build/CI section |
| New environment variable required | Configuration/Setup |
| Git workflow changes (hooks, branch strategy) | Git Workflow |
| New skill added (skills repo) | Skill list, Naming Conventions |
| Skill renamed (skills repo) | Update all references |
| New skill cross-reference pattern (skills repo) | Editing Skills section |

**What to skip:**
- **Project Type section** — never modify this user-configured section
- Code implementation details (that's for DESIGN.md)
- Architecture changes (that's for DESIGN.md)
- Individual bug fixes that don't change workflow
- Formatting/style changes

### Step 4a: Check for framework changes (UNIVERSAL)

**Framework changes = infrastructure that affects multiple files or introduces new capabilities.**

**Red flags that warrant CLAUDE.md documentation:**

| Pattern | CLAUDE.md Impact |
|---------|------------------|
| **New scripts/ or tools/ files** | Document in Development Tools or Repository Structure |
| **New validation/testing infrastructure** | Document in Testing section or Quality Assurance |
| **Same pattern applied across multiple files** | Framework change, document the pattern |
| **New automation or sync capabilities** | Document in workflow sections |
| **New quality gates or pre-commit hooks** | Document in Git Workflow or Development Tools |
| **New dependency management patterns** | Document in Dependencies section |

**Recent example (ADR-0001):**
- **What happened:** Validation added to 4 sync workflows (update-claude-md, update-design, sync-primary-doc, readme-sync.md)
- **Framework change:** All sync workflows now validate documents before staging
- **CLAUDE.md impact:** Should have updated Development Tools or Quality Assurance section

**If you detect framework changes, include them in proposals even if no direct workflow/convention changes.**

**This check applies to ALL project types** (skills/java/custom/generic).

### Step 5: Propose updates

Format each proposed change as clear before/after:

```
## Section: <Section Name>

**Replace:**
> <exact existing text, or "(new section)">

**With:**
> <your proposed replacement text>

**Reason:** <one-sentence rationale>
```

Group related changes. Show summary at top if many changes.

### Step 6: Confirm and apply

End every proposal with exactly:

> **Does this look good?**
> Reply **YES** to apply all changes, **NO** to discard, or describe what to adjust.

When user confirms YES:
1. Apply **only** the proposed changes
2. **Validate the document:**
   ```bash
   python scripts/validate_document.py CLAUDE.md
   ```
3. **If validation fails (exit code 1):**
   - Revert changes: `git restore CLAUDE.md`
   - Report CRITICAL issues to user
   - Ask user to fix manually
   - Stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print brief summary: "✅ Updated sections: Build Commands, Testing"
   - Document is ready for staging

---

## Common Pitfalls

Avoid these mistakes when updating CLAUDE.md:

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Modifying Project Type section | Breaks repository behavior, user-configured | Never touch this section, skip it entirely |
| Applying changes without confirmation | User loses control | Always wait for explicit YES |
| Documenting architecture in CLAUDE.md | Wrong file - DESIGN.md is for architecture | Focus on workflow/conventions only |
| Over-documenting obvious things | Clutter, maintenance burden | Only document non-obvious workflows |
| Not updating CLAUDE.md when adding tools | Claude doesn't know about new tools | Update when workflow changes |
| Copying command help text verbatim | Duplicate of `--help` output | Summarize common use cases |

## Success Criteria

CLAUDE.md update is complete when:

- ✅ CLAUDE.md located and read
- ✅ Workflow/convention changes identified from staged diff
- ✅ Proposed updates formatted as before/after blocks
- ✅ User confirmed with explicit **YES**
- ✅ Changes applied to CLAUDE.md
- ✅ **Document validation passed** (no CRITICAL corruption)
- ✅ File ready for staging (or user confirmed no changes needed)

**Not complete until** all criteria met, validation passed, and CLAUDE.md reflects current workflows.

## Skill Chaining

**Invoked by:** [`git-commit`] when committing in any repository, [`java-git-commit`] alongside update-design

**Invokes:** None (terminal skill in the chain)

**Can be invoked independently:** User can run `/update-claude-md` directly to sync CLAUDE.md without committing

## Starter Template (Skills Repository)

Use this when creating CLAUDE.md for a skills repository:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Type

**Type:** skills

## Repository Purpose

[Brief description of what this skills collection provides]

## Skill Architecture

### Frontmatter Requirements

[YAML frontmatter structure and CSO rules]

### Naming Conventions

[Skill naming patterns - generic vs specific]

### Skill Chaining

[How skills reference each other]

## Editing Skills

[Guidelines for modifying skills]

## Key Skills

[List of important skills and their purposes]
```

## Starter Template (Code Repository)

Use this when creating CLAUDE.md for a code repository:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Type

**Type:** [java | custom | generic]

## Repository Purpose

[What this project does]

## Development Commands

**Build:**
```bash
[build command]
```

**Test:**
```bash
[test command]
```

**Run:**
```bash
[run command]
```

## Testing Patterns

[Testing framework, conventions, key patterns]

## Code Organization

[Package structure, module organization, naming conventions]

## Configuration

[Environment variables, config files, setup requirements]
```
