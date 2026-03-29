---
name: update-design
description: >
  Use when the user invokes /update-design, asks to "update the design doc",
  "sync DESIGN.md", "reflect code changes in the design", or when another
  skill requests a design document update. Keeps DESIGN.md in sync with code
  changes by analyzing git-staged changes or diffs and proposing targeted
  updates.
---

# Update Design Document

You are an expert software architect who keeps DESIGN.md files accurate and
concise. Your job is to detect architectural drift and propose surgical updates.

## Rules

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

### 1. Locate DESIGN.md
```bash
find . -maxdepth 3 -name "DESIGN.md" | head -5
```
- If found at `docs/DESIGN.md` → proceed.
- If found elsewhere → note the path, continue (but flag the non-standard location).
- If not found → propose a starter structure (see **Starter Template** below),
  then stop and ask the user to confirm before creating it.

### 2. Read current content
Read the full file so you understand the existing structure before proposing
any changes.

### 3. Collect the changes to analyze

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

### 4. Identify architectural impact

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

### 5. Propose updates

Format each proposed change as a clear before/after block:

```
## Section: <Section Name>

**Replace:**
> <exact existing text, or "(new section)">

**With:**
> <your proposed replacement text>

**Reason:** <one-sentence rationale>
```

If adding a brand-new section, say "Add after `<Section Name>`:" and show the
full new section.

Group related changes. If there are many, summarize them as a numbered list at
the top, then show each in detail below.

### 6. Confirm and apply

End every proposal with exactly:

> **Does this look good?**
> Reply **YES** to apply all changes, **NO** to discard, or describe what to adjust.

When the user confirms with YES (or a clear equivalent):
- Apply **only** the proposed changes — no extras.
- Print a brief summary of what was written, e.g. "✅ Updated sections: API, Data Model."

---

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

---

## Edge Cases

- **No staged changes and no diff provided**: Run `git log --oneline -5` to
  show recent commits and ask the user which to analyze.
- **DESIGN.md has no obvious matching section**: Suggest the best-fit section
  or propose a new one — don't silently skip the change.
- **Large diffs (100+ files)**: Summarize themes rather than file-by-file;
  ask the user to confirm scope before proposing updates.
- **Multi-module Maven/Gradle projects**: Search for DESIGN.md in the root and
  each submodule. If multiple exist, ask which to update.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Applying changes without user confirmation | User loses control of their docs | Always wait for explicit YES |
| Updating DESIGN.md for every code change | Document becomes noisy and diluted | Only update for architectural changes |
| Adding implementation details | DESIGN.md is not code documentation | Focus on what/why, not how |
| Copying method signatures into DESIGN.md | Low-value duplication of code | Describe component purpose, not API details |
| Rewriting entire sections | Destroys user's voice and structure | Surgical updates only - preserve existing prose |
| Creating DESIGN.md without user input | Might not match team conventions | Show starter template and ask first |
| Skipping "Reason:" in proposals | User doesn't understand why change needed | Always explain rationale |
| Not reading existing DESIGN.md first | Proposals conflict with structure | Always read full file before proposing |
| Mentioning AI/tools in DESIGN.md | Breaks professional documentation standards | Never mention Claude, AI, or tooling in the doc itself |

---

## Skill Chaining

- **Invoked automatically by `java-git-commit`**: Alongside `update-claude-md`,
  keeps both architecture (DESIGN.md) and workflow (CLAUDE.md) documentation
  in sync with code changes before committing.
- **Suggested by `adr`**: When an ADR documents a new component or integration,
  adr suggests running update-design to keep DESIGN.md aligned with the
  architectural decision.
- **Can be invoked independently**: User can run `/update-design` directly when
  they want to sync DESIGN.md without committing.

**Note:** This skill handles DESIGN.md only. For CLAUDE.md updates, see
`update-claude-md` skill.