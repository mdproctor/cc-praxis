# custom-project-health — Design Document

**Status:** Design phase — not yet implemented as a skill
**Skill name (planned):** `custom-project-health`
**Slash command (planned):** `/custom-project-health`
**Invoked by:** [`project-health`](project-health.md) when `type: custom` declared in CLAUDE.md

This document tracks the custom-project-specific health checks that augment the universal checks in `project-health`.

---

## Purpose

Runs after `project-health` completes its universal checks. Adds checks specific to custom projects — working groups, research projects, advocacy, documentation sites — where the user defines their own sync strategy and primary document.

Follows the same pattern as `custom-git-commit` extending `git-commit`.

---

## Prerequisite

**This skill builds on [`project-health`](project-health.md).** When invoked directly (e.g. `/custom-project-health`), it runs all universal checks first then its own additions — identical output to `project-health` auto-chaining to this skill. Either entry point produces the same result.

---

## Augmentations to Universal Checks

These extend the universal categories with custom-project-specific items:

| Universal check | Quality additions | Refinement additions |
|----------------|------------------|---------------------|
| `primary-doc` | Primary document (path from CLAUDE.md) reflects current project state; sync rules still match actual file structure | Is the primary document the right size, or should it be modularised? |
| `artifacts` | Primary Document path declared in CLAUDE.md exists; milestone is current; any secondary docs referenced in Sync Rules exist | Could milestone tracking be simpler? |
| `conventions` | Sync Rules configured in CLAUDE.md; rules match actual workflow and file patterns | Could Sync Rules be expressed more concisely without losing fidelity? Are any rules never triggered? |
| `framework` | Sync patterns match the declared sync strategy; no Sync Rules reference non-existent file patterns | Could any Sync Rules be merged or simplified? |

---

## Custom-Project-Specific Categories

These categories only exist for custom projects and are not present in `project-health`:

### `sync-rules` — Sync Rule Health

**Quality** — Are the Sync Rules in CLAUDE.md correct and complete?
- [ ] Every file pattern in Sync Rules matches at least one actual file
- [ ] Every document section referenced in Sync Rules exists in the primary document
- [ ] No Sync Rules reference files that have been renamed or removed
- [ ] The sync strategy (bidirectional-consistency, research-progress, etc.) matches actual usage
- [ ] Current Milestone reflects the actual phase of the project
- [ ] No two Sync Rules match overlapping file patterns without clear precedence

**Refinement** — Could Sync Rules be cleaner or more maintainable?
- [ ] Are there rules that overlap or could be merged?
- [ ] Are any rules so broad they match files they shouldn't?
- [ ] Could the primary document be restructured to make Sync Rules simpler?
- [ ] Are there common changes that aren't captured by any rule?

### `project-currency` — Is the Project Current?

**Quality** — Does the project reflect its current reality?
- [ ] Primary document milestone matches the actual current phase
- [ ] No sections describe work that has been completed but still marked as planned
- [ ] No participants listed who are no longer active
- [ ] Referenced external documents, tools, or systems still exist
- [ ] No completed work items remain marked as "planned" or "in progress"
- [ ] External tool links (Notion, Figma, Jira, etc.) are all still reachable and point to current content

**Refinement** — Could the project's current state be expressed more clearly?
- [ ] Could the primary document be reorganised to surface current work more prominently?
- [ ] Are historical phases cluttering the document and making it harder to navigate?

---

## Output Format

Same severity rating as `project-health`, prefixed with `[custom]`:

```
### HIGH (should fix)
- [custom][sync-rules] Sync Rule pattern 'catalog/*.md' matches no files — directory may have been renamed
- [custom][project-currency] Milestone says "Phase 1 - Discovery" but Phase 2 work is underway

### MEDIUM (worth fixing)
- [custom][sync-rules] Two rules both match 'docs/meetings/' — consolidate to one rule
```
