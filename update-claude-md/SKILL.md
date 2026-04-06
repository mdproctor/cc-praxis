---
name: update-claude-md
description: >
  Use when CLAUDE.md needs updating due to workflow or convention changes, or
  when invoked automatically by git-commit/java-git-commit when commits
  affect build commands, testing patterns, naming conventions, or repository
  structure.
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
- **Never modify the Project Type section** — this is user-configured and defines repository behavior (type: skills, type: java, type: blog, type: custom, type: generic)
- Focus on **workflow and convention changes**: new tools, build commands, testing
  patterns, naming conventions, repository structure changes
- Keep prose concise and professional. Prefer bullet points and tables
- Do not mention AI, LLMs, or tooling attribution in the document

## Workflow

### Step 1: Check if CLAUDE.md exists

```bash
ls CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found"
```

- If found → proceed to Step 1a
- If not found → check if this is the type of repo that needs one:
  - Skills repository? (has */SKILL.md files)
  - Complex build setup? (has build.gradle, pom.xml, package.json, etc.)
  - If yes → propose creating starter CLAUDE.md, ask user to confirm
  - If no → skip (repo may not need CLAUDE.md)

### Step 1a: Discover document group

**After locating CLAUDE.md, discover modular structure:**

```python
from scripts.document_discovery import discover_document_group
from pathlib import Path

group = discover_document_group(Path("CLAUDE.md"))
```

**This discovers:**
- Primary file: `CLAUDE.md`
- Optional modules via:
  - Markdown links: `[Workflows](docs/workflows/ci.md)`
  - Include directives: `<!-- include: patterns.md -->`
  - Section references: `§ Testing in docs/workflows/testing.md`
  - Directory pattern: `docs/workflows/*.md` files

**Cache behavior:**
- First sync: Discovers modules, caches in `.doc-cache.json`
- Subsequent syncs: Uses cache (fast path, <10ms)
- Cache invalidation: Automatic on structure changes (new links, new files)

**Result:**
- Single-file CLAUDE.md → `group.modules` is empty (backwards compatible)
- Modular CLAUDE.md → `group.modules` contains linked files

**Continue with all files in the group (primary + modules).**

### Step 2: Read current content

Read the full file so you understand the existing structure before proposing
any changes.

**If modular (group.modules not empty):**
- Read CLAUDE.md (primary file)
- Read each module file
- Understand how content is split across files

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

**Example:**
- **What happened:** A new linter or validator added to the CI pipeline
- **Framework change:** All commits now require passing lint checks before merge
- **CLAUDE.md impact:** Should document the new quality gate under Development Tools or Workflow

**If you detect framework changes, include them in proposals even if no direct workflow/convention changes.**

**This check applies to ALL project types** (skills/java/blog/custom/generic).

### Step 4b: Check for missing Writing Style Guide section

```bash
ls docs/blog/ 2>/dev/null | head -1
```

If `docs/blog/` exists (meaning write-blog has been used in this project), check whether CLAUDE.md already contains the Writing Style Guide requirement:

```bash
grep -l "writing style guide\|blog-technical" CLAUDE.md 2>/dev/null
```

If `docs/blog/` exists **and** the requirement is absent from CLAUDE.md, propose adding:

```markdown
## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.
```

This is a one-time addition per project — once present, this check passes silently.

### Step 5: Propose updates

**For single-file CLAUDE.md:**

Format each proposed change as a clear before/after block:

```
## Section: <Section Name>

**Replace:**
> <exact existing text, or "(new section)">

**With:**
> <your proposed replacement text>

**Reason:** <one-sentence rationale>
```

**For modular CLAUDE.md (primary + modules):**

Group proposals by file:

```
## Proposed CLAUDE.md updates

### Section: Development Tools
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/workflows/ci.md updates

### Section: Build Pipeline
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/workflows/testing.md updates

### Section: Test Commands
**Replace:**
> (new section)

**With:**
> ## New Test Commands
> - `npm test:integration` - Run integration tests
> - `npm test:e2e` - Run end-to-end tests

**Reason:** New testing infrastructure added
```

**Routing logic:**
- New build commands → Update `docs/workflows/build.md` (if exists), else CLAUDE.md § Development Commands
- New test patterns → Update `docs/workflows/testing.md` (if exists), else CLAUDE.md § Testing Patterns
- New tools → Update `docs/workflows/tools.md` (if exists), else CLAUDE.md § Development Tools
- Repository structure → Update CLAUDE.md (primary always has high-level structure)

Group related changes. Show summary at top if many changes.

### Step 6: Confirm and apply

End every proposal with exactly:

> **Does this look good?**
> Reply **YES** to apply all changes, **NO** to discard, or describe what to adjust.

When user confirms YES:

**For single-file CLAUDE.md:**
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

**For modular CLAUDE.md (primary + modules):**
1. Apply proposed changes to ALL affected files (primary + modules)
2. **Validate entire document group:**
   ```python
   from scripts.validate_document import validate_document_group
   from scripts.document_discovery import discover_document_group
   from pathlib import Path

   group = discover_document_group(Path("CLAUDE.md"))
   issues = validate_document_group(group)
   ```
3. **If validation fails (CRITICAL issues):**
   - Revert ALL modified files:
     ```bash
     git restore CLAUDE.md docs/workflows/ci.md docs/workflows/testing.md
     ```
   - Report CRITICAL issues to user
   - Ask user to fix manually
   - Stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print summary: "✅ Updated files: CLAUDE.md, docs/workflows/ci.md, docs/workflows/testing.md"
   - All modified files ready for staging

**Validation checks for modular groups:**
- Link integrity: All `[links](file.md)` and `[links](file.md#section)` resolve
- Completeness: No orphaned modules (unreferenced from primary)
- No duplication: Substantial paragraphs not duplicated across files
- Individual file validation: Each file passes single-file corruption checks

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

## Document Structure Check

*This check is part of the `performance` and `docs-sync` categories in `project-health`. For a full analysis: `/project-health performance docs-sync`. See [docs/project-health.md](../docs/project-health.md).*

After applying updates, run:

```bash
python scripts/validation/validate_doc_structure.py CLAUDE.md
```

If exit code 1 or 2, follow the nudge workflow described in `java-update-design` § Document Structure Check — same conversation, same threshold adjustment, same CLAUDE.md persistence pattern.

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

**Invoked by:** [`git-commit`] when committing in any repository, [`java-git-commit`] alongside update-design, [`blog-git-commit`] when committing blog changes, [`custom-git-commit`] when committing custom project changes

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

**Type:** [skills | java | blog | custom | generic]

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
