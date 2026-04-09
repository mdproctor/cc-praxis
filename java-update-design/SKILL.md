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
- design/DESIGN.md exists (or is being created)
- Staged changes may affect architecture

**Do NOT use this skill for:**
- type: skills repositories (skills are self-documenting, no DESIGN.md)
- type: custom repositories (use update-primary-doc with user-configured primary document)
- type: generic repositories (no automatic DESIGN.md sync)

## Prerequisites

**This skill extends `update-primary-doc`** with Java-specific knowledge:

- **update-primary-doc**: Generic document sync patterns (read path, match files, propose updates, validate)

**Java-specific additions:**
- Hardcoded Primary Document: `design/DESIGN.md`
- Hardcoded architecture mappings:
  - New @Entity → Update "Domain Model" section
  - New @Service/@Repository → Update "Services" or "Data Access" section
  - New module in pom.xml → Update "Component Structure" section
  - API changes → Update "Public API" section

## Core Rules

- **Only operates in type: java repositories** — other project types use different documentation patterns
- DESIGN.md lives at `design/DESIGN.md` in the workspace (CWD). In the workspace
  model, the project is accessed via `add-dir`.
- **Epic close:** When the epic completes, merge workspace `design/DESIGN.md`
  back into the project's `DESIGN.md` (user-confirmed, one manual merge step).
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
ls design/DESIGN.md 2>/dev/null || find . -name "DESIGN.md" | head -5
```

- If found at `design/DESIGN.md` → proceed.
- If found elsewhere → note the path, continue (but flag the non-standard location).
- If not found → propose a starter structure (see **Starter Template** below),
  then stop and ask the user to confirm before creating it.

### Step 1a: Check for modular structure

Run `python scripts/document_discovery.py design/DESIGN.md` (or use the API) to detect linked module files. **If modules exist**, switch to the [modular-handling.md](modular-handling.md) workflow for Steps 2, 5, and 6.

### Step 2: Read current content

Read the full DESIGN.md so you understand the existing structure before proposing changes.

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

Map each change to a DESIGN.md section using **[mapping-reference.md](mapping-reference.md)**
(code change → section table, and Java annotation → architectural signal table).

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

**For modular DESIGN.md:** see [modular-handling.md](modular-handling.md) § Step 5.

If adding a brand-new section, say "Add after `<Section Name>`:" and show the
full new section. Group related changes; summarize at top if many.

### Step 6: Confirm and apply

End every proposal with exactly:

> **Does this look good?**
> Reply **YES** to apply all changes, **NO** to discard, or describe what to adjust.

When the user confirms with YES (or a clear equivalent):

**For single-file DESIGN.md:**
1. Apply **only** the proposed changes — no extras.
2. **Validate the document:**
   ```bash
   python scripts/validate_document.py design/DESIGN.md
   ```
3. **If validation fails (exit code 1):**
   - Revert changes: `git restore design/DESIGN.md`
   - Report CRITICAL issues to user
   - Ask user to fix manually
   - Stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print a brief summary of what was written, e.g. "✅ Updated sections: API, Data Model."
   - Document is ready for staging

**For modular DESIGN.md:** see [modular-handling.md](modular-handling.md) § Step 6.

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
python scripts/validation/validate_doc_structure.py design/DESIGN.md
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

- ✅ design/DESIGN.md located and read
- ✅ Architectural changes identified from staged diff
- ✅ Proposed updates formatted as before/after blocks
- ✅ User confirmed with explicit **YES**
- ✅ Changes applied to design/DESIGN.md
- ✅ **Document validation passed** (no CRITICAL corruption)
- ✅ File ready for staging (or user confirmed no changes needed)

**Not complete until** all criteria met, validation passed, and DESIGN.md reflects current architecture.

## Skill Chaining

**Invoked by:** [`java-git-commit`] alongside `update-claude-md`, [`adr`] suggests running this when an ADR documents a new component or integration

**Invokes:** None (terminal skill in the chain)

**Complements:** `design-snapshot` — this skill keeps DESIGN.md *current* (mutable, always up to date); `design-snapshot` *freezes* a moment in time (immutable). After a significant architectural update, consider offering a snapshot to record where the design stands.

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

Use this when DESIGN.md doesn't exist yet. Full template in **[starter-template.md](starter-template.md)**.
