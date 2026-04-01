---
name: java-update-design
description: >
  Use when the user invokes /update-design, asks to "update the design doc",
  "sync DESIGN.md", "reflect code changes in the design", or when another
  skill (java-git-commit) requests a design document update.
---

# Update Design Document

You are an expert software architect who keeps DESIGN.md files accurate and
concise. Your job is to detect architectural drift and propose updates.

## When to Use This Skill

**Only for type: java repositories.**

This skill is invoked by `java-git-commit` when:
- CLAUDE.md declares `type: java`
- docs/DESIGN.md exists (or is being created)
- Staged changes may affect architecture

**Do NOT use this skill for:**
- type: skills repositories (skills are self-documenting, no DESIGN.md)
- type: custom repositories (use update-primary-doc with user-configured primary document)
- type: generic repositories (no automatic DESIGN.md sync)

## Prerequisites

**This skill extends `update-primary-doc`** with Java-specific knowledge:

- **update-primary-doc**: Generic document sync patterns (read path, match files, propose updates, validate)

**Java-specific additions:**
- Hardcoded Primary Document: `docs/DESIGN.md`
- Hardcoded architecture mappings:
  - New @Entity → Update "Domain Model" section
  - New @Service/@Repository → Update "Services" or "Data Access" section
  - New module in pom.xml → Update "Component Structure" section
  - API changes → Update "Public API" section

## Core Rules

- **Only operates in type: java repositories** — other project types use different documentation patterns
- DESIGN.md lives at `docs/DESIGN.md` relative to the project root. Never
  move or rename it.
- **Never apply changes without explicit user confirmation** (a plain "YES" or
  equivalent). If in doubt, ask.
- Focus only on **architectural impact**: new/removed components, changed
  public APIs, refactored modules, new data flows, dependency changes, breaking
  changes. Ignore implementation details that don't affect the design.
- Keep prose concise and professional. Prefer bullet points and tables over
  long paragraphs.
- Do not mention AI, LLMs, or any tooling attribution in the document itself.

## Workflow

### Step 1: Locate DESIGN.md

```bash
# Check standard location first
ls docs/DESIGN.md 2>/dev/null || find . -name "DESIGN.md" | head -5
```

- If found at `docs/DESIGN.md` → proceed.
- If found elsewhere → note the path, continue (but flag the non-standard location).
- If not found → propose a starter structure (see **Starter Template** below),
  then stop and ask the user to confirm before creating it.

### Step 1a: Discover document group

**After locating DESIGN.md, discover modular structure:**

```python
from scripts.document_discovery import discover_document_group
from pathlib import Path

group = discover_document_group(Path("docs/DESIGN.md"))
```

**This discovers:**
- Primary file: `docs/DESIGN.md`
- Optional modules via:
  - Markdown links: `[Architecture](docs/design/architecture.md)`
  - Include directives: `<!-- include: components.md -->`
  - Section references: `§ API Details in docs/design/api.md`
  - Directory pattern: `docs/design/*.md` files

**Cache behavior:**
- First sync: Discovers modules, caches in `.doc-cache.json`
- Subsequent syncs: Uses cache (fast path, <10ms)
- Cache invalidation: Automatic on structure changes (new links, new files)

**Result:**
- Single-file DESIGN.md → `group.modules` is empty (backwards compatible)
- Modular DESIGN.md → `group.modules` contains linked files

**Continue with all files in the group (primary + modules).**

### Step 2: Read current content

Read the full file so you understand the existing structure before proposing
any changes.

**If modular (group.modules not empty):**
- Read DESIGN.md (primary file)
- Read each module file
- Understand how content is split across files

### Step 3: Collect the changes to analyze

In priority order:
1. **Staged changes**: `git diff --staged` (prefer this — it's what will be committed)
2. **Recent commit**: `git diff HEAD~1 HEAD` (if nothing staged)
3. **User-provided description or diff** passed in context
4. Ask the user if none of the above yields anything useful.

For Java projects also check:
- New/modified `@RestController`, `@Service`, `@Repository`, `@Entity` classes
- Changes to `pom.xml` or `build.gradle` (new dependencies, version bumps)
- Interface/abstract class additions or removals
- Package restructuring

### Step 4: Identify architectural impact

Map each change to a DESIGN.md section:

| Code change | Likely DESIGN.md section |
|---|---|
| New REST endpoint / controller | API / Endpoints |
| New service or module | Components / Architecture |
| New external dependency | Dependencies / Technology Stack |
| DB schema / entity change | Data Model |
| New configuration property | Configuration |
| Breaking API change | Breaking Changes / Migration |
| Removed component | Components (mark as removed) |
| New async flow (queue, event, scheduler) | Architecture / Data Flow |
| New security constraint (auth, role, filter) | Security |
| New cross-cutting concern (caching, retry, tracing) | Architecture / Cross-cutting Concerns |
| Module extracted into separate service/jar | Components (note boundary change) |
| New DTO / request-response contract | API / Data Contracts |
| Interface or abstract class added | Components / Extension Points |

**Java-specific signals and what they mean:**

| Annotation / Pattern | Architectural signal |
|---|---|
| `@RestController`, `@RequestMapping` | New or changed public API surface |
| `@Service`, `@Component` | New application logic component |
| `@Repository`, `@Entity`, `@Table` | Data layer or schema change |
| `@Scheduled`, `@Async` | New background job or async flow |
| `@KafkaListener`, `@RabbitListener` | New message-driven component |
| `@FeignClient`, `@RestTemplate` | New external service integration |
| `@Configuration`, `@Bean` | New infrastructure wiring |
| `@PreAuthorize`, `@Secured` | Security policy change |
| `@Cacheable`, `@CacheEvict` | Caching strategy introduced or changed |
| New `*Exception` class + `@ControllerAdvice` | New error handling contract |
| New package (e.g. `adapter/`, `port/`, `domain/`) | Possible architectural layer added |
| `pom.xml` / `build.gradle` dependency added | New external dependency — check if it implies a pattern (e.g. adding Resilience4j implies circuit breaking) |

**What to skip:**
Skip the following changes, unless they signal a broader refactor.
- Renaming a private method or variable
- Adding/changing log statements
- Test-only changes (`src/test/`)
- Javadoc or comment updates
- Code formatting / style fixes
- Internal refactor with no change to public interfaces or behaviour

### Step 4a: Check for framework changes (UNIVERSAL)

**Framework changes = infrastructure that affects multiple files or introduces new capabilities.**

**Red flags that warrant DESIGN.md documentation:**

| Pattern | DESIGN.md Impact |
|---------|------------------|
| **New scripts/ or tools/ files** | Document in Technology Stack or Build Tools |
| **New validation/testing infrastructure** | Document in Testing Strategy or Quality Gates |
| **Same architectural pattern across modules** | Framework change, document the pattern |
| **New cross-cutting concerns** | Document in Architecture section |
| **New security/auth mechanisms** | Document in Security section |
| **New data flow patterns** | Document in Data Flow or Architecture |

**Recent example (ADR-0001):**
- **What happened:** Validation added to sync workflows
- **Framework change:** Universal document validation before commits
- **DESIGN.md impact:** If this were a Java project, should document in Testing Strategy

**If you detect framework changes, include them in proposals even if no direct code changes.**

**This check applies to ALL type: java projects.**

### Step 5: Propose updates

**For single-file DESIGN.md:**

Format each proposed change as a clear before/after block:

```
## Section: <Section Name>

**Replace:**
> <exact existing text, or "(new section)">

**With:**
> <your proposed replacement text>

**Reason:** <one-sentence rationale>
```

**For modular DESIGN.md (primary + modules):**

Group proposals by file:

```
## Proposed docs/DESIGN.md updates

### Section: Architecture
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/design/architecture.md updates

### Section: Component Overview
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/design/api.md updates

### Section: REST Endpoints
**Replace:**
> (new section)

**With:**
> ## New UserAPI Endpoints
> - `POST /api/users` - Create user
> - `GET /api/users/{id}` - Get user by ID

**Reason:** New UserController added
```

**Routing logic:**
- New @RestController → Update `docs/design/api.md` (if exists), else DESIGN.md § API
- New @Entity → Update `docs/design/data-model.md` (if exists), else DESIGN.md § Data Model
- New module → Update `docs/design/components.md` (if exists), else DESIGN.md § Components
- Cross-cutting change → Update DESIGN.md (primary always has high-level architecture)

If adding a brand-new section, say "Add after `<Section Name>`:" and show the
full new section.

Group related changes. If there are many, summarize them as a numbered list at
the top, then show each in detail below.

### Step 6: Confirm and apply

End every proposal with exactly:

> **Does this look good?**
> Reply **YES** to apply all changes, **NO** to discard, or describe what to adjust.

When the user confirms with YES (or a clear equivalent):

**For single-file DESIGN.md:**
1. Apply **only** the proposed changes — no extras.
2. **Validate the document:**
   ```bash
   python scripts/validate_document.py docs/DESIGN.md
   ```
3. **If validation fails (exit code 1):**
   - Revert changes: `git restore docs/DESIGN.md`
   - Report CRITICAL issues to user
   - Ask user to fix manually
   - Stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print a brief summary of what was written, e.g. "✅ Updated sections: API, Data Model."
   - Document is ready for staging

**For modular DESIGN.md (primary + modules):**
1. Apply proposed changes to ALL affected files (primary + modules)
2. **Validate entire document group:**
   ```python
   from scripts.validate_document import validate_document_group
   from scripts.document_discovery import discover_document_group
   from pathlib import Path

   group = discover_document_group(Path("docs/DESIGN.md"))
   issues = validate_document_group(group)
   ```
3. **If validation fails (CRITICAL issues):**
   - Revert ALL modified files:
     ```bash
     git restore docs/DESIGN.md docs/design/architecture.md docs/design/api.md
     ```
   - Report CRITICAL issues to user
   - Ask user to fix manually
   - Stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print summary: "✅ Updated files: DESIGN.md, docs/design/architecture.md, docs/design/api.md"
   - All modified files ready for staging

**Validation checks for modular groups:**
- Link integrity: All `[links](file.md)` and `[links](file.md#section)` resolve
- Completeness: No orphaned modules (unreferenced from primary)
- No duplication: Substantial paragraphs not duplicated across files
- Individual file validation: Each file passes single-file corruption checks

---

## Common Pitfalls

Avoid these mistakes when updating DESIGN.md:

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Using in non-Java repositories | Wrong project type, no DESIGN.md pattern | Only invoke for type: java repositories |
| Applying changes without user confirmation | User loses control of their docs | Always wait for explicit YES |
| Updating DESIGN.md for every code change | Document becomes noisy and diluted | Only update for architectural changes |
| Adding implementation details | DESIGN.md is not code documentation | Focus on what/why, not how |
| Copying method signatures into DESIGN.md | Low-value duplication of code | Describe component purpose, not API details |
| Creating DESIGN.md without user input | Might not match team conventions | Show starter template and ask first |
| Skipping "Reason:" in proposals | User doesn't understand why change needed | Always explain rationale |
| Not reading existing DESIGN.md first | Proposals conflict with structure | Always read full file before proposing |
| Mentioning AI/tools in DESIGN.md | Breaks professional documentation standards | Never mention Claude, AI, or tooling in the doc itself |

## Document Structure Check

*This check is part of the `performance` and `docs-sync` categories in `project-health`. For a full analysis: `/project-health performance docs-sync`. See [docs/project-health.md](../docs/project-health.md).*

After applying updates, run:

```bash
python scripts/validation/validate_doc_structure.py docs/DESIGN.md
```

**If exit code 1 (nudge recommended):**

> 📄 DESIGN.md is {N} lines — as it grows, collaborators will increasingly step on each other's changes.
>
> Would you like me to analyse the document and suggest how to split it into modules? (YES / NO / ADJUST)
>
> - **YES** — I'll analyse the sections and propose a modular structure
> - **NO** — skip for now
> - **ADJUST** — this prompt came up too early or too late; tell me your preference

If user says **ADJUST**, ask:
> Should I nudge you sooner (lower threshold) or later (higher)? Current: {N} lines.
> Enter a number, or say "sooner" / "later" (I'll adjust by 100 lines).

Then update CLAUDE.md:
```markdown
## Document Structure

**Modular doc nudge:** enabled
**Threshold:** {new_value} lines
```

**If exit code 2 (already modular, review suggested):**

> 🔍 DESIGN.md is already modular but has {N} sections — some may benefit from reorganisation.
> Would you like me to review the current structure and suggest improvements? (YES / NO)

**If exit code 0:** no action needed.

## Success Criteria

DESIGN.md update is complete when:

- ✅ docs/DESIGN.md located and read
- ✅ Architectural changes identified from staged diff
- ✅ Proposed updates formatted as before/after blocks
- ✅ User confirmed with explicit **YES**
- ✅ Changes applied to docs/DESIGN.md
- ✅ **Document validation passed** (no CRITICAL corruption)
- ✅ File ready for staging (or user confirmed no changes needed)

**Not complete until** all criteria met, validation passed, and DESIGN.md reflects current architecture.

## Skill Chaining

**Invoked by:** [`java-git-commit`] alongside `update-claude-md`, [`adr`] suggests running this when an ADR documents a new component or integration

**Invokes:** None (terminal skill in the chain)

**Can be invoked independently:** User can run `/update-design` directly to sync DESIGN.md without committing

**Note:** This skill handles DESIGN.md only. For CLAUDE.md updates, see `update-claude-md` skill.

## Edge Cases

| Situation | Action |
|-----------|--------|
| **No staged changes and no diff provided** | Run `git log --oneline -5` to show recent commits and ask which to analyze |
| **DESIGN.md has no obvious matching section** | Suggest the best-fit section or propose a new one — don't silently skip |
| **Large diffs (100+ files)** | Summarize themes rather than file-by-file; confirm scope with user first |
| **Multi-module Maven/Gradle projects** | Search for DESIGN.md in root and each submodule. If multiple exist, ask which to update |

## Starter Template

Use this when DESIGN.md doesn't exist yet:

```markdown
# Project Design

## Overview
<!-- One paragraph: what this system does and why it exists. -->

## Architecture
<!-- High-level diagram or description of major components. -->

## Components
<!-- List key modules/services with a one-line description each. -->

## API
<!-- Public endpoints or interfaces exposed by this system. -->

## Data Model
<!-- Core entities and their relationships. -->

## Dependencies
<!-- External libraries, services, and infrastructure. -->

## Configuration
<!-- Key environment variables or config properties. -->

## Open Questions / Future Work
<!-- Unresolved decisions or planned changes. -->
```
