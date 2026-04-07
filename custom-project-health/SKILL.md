---
name: custom-project-health
description: >
  Use when health-checking a type: custom project (working groups, research,
  advocacy, documentation sites), or when invoked automatically by project-health
  on custom project type detection.
---

# custom-project-health

Health checks for type: custom projects — working groups, research projects,
advocacy, documentation sites. These projects define their own sync strategy
and primary document in CLAUDE.md. This skill runs all universal checks from
`project-health` first, then adds checks specific to Sync Rules correctness,
primary document currency, and project state consistency.

## Prerequisites

**This skill builds on `project-health`.** Apply all universal checks first:

- All universal categories: `docs-sync`, `consistency`, `logic`, `config`,
  `security`, `release`, `user-journey`, `git`, `primary-doc`, `artifacts`,
  `conventions`, `framework`
- Same tier system (1-4) and named aliases (`--commit`, `--standard`,
  `--prerelease`, `--deep`)
- Same output format — custom-specific findings are prefixed with `[custom]`

When invoked directly (`/custom-project-health`), run universal checks first,
then custom-specific checks. Output is combined — identical to `project-health`
auto-chaining here.

---

## Tier System

Inherited from `project-health` — see [check-categories.md](../project-health/check-categories.md#tier-system).
Custom-specific categories (`sync-rules`, `project-currency`) run at tier 3+.

---

## Type-Specific Scan Targets

In addition to the universal document scan, include:

- The **Primary Document** path declared in `CLAUDE.md` (under `## Project Type`)
- All files matching patterns in the **Sync Rules** table in `CLAUDE.md`
- Any secondary documents referenced in the Sync Rules

Read `## Project Type` from CLAUDE.md first to discover these paths before
running any checks — they vary per project.

---

## Augmentations to Universal Checks

These extend universal categories with custom-project-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] Primary document (path from CLAUDE.md) reflects the current project state
- [ ] Sync Rules in CLAUDE.md still match the actual file structure

**Refinement (tier 4):**
- [ ] Is the primary document an appropriate size, or should it be modularised?

### `artifacts` augmentations

**Quality:**
- [ ] Primary Document path declared in CLAUDE.md exists on disk
- [ ] Current Milestone section is present and up to date
- [ ] Any secondary documents referenced in Sync Rules exist at their declared paths

**Refinement (tier 4):**
- [ ] Could milestone tracking be simpler or expressed more compactly?

### `conventions` augmentations

**Quality:**
- [ ] Sync Rules are configured in CLAUDE.md (`## Project Type` → Sync Rules table)
- [ ] Sync Rules match actual workflow and file patterns in the repository

**Refinement (tier 4):**
- [ ] Could Sync Rules be expressed more concisely without losing fidelity?
- [ ] Are any Sync Rules never triggered in practice?

### `framework` augmentations

**Quality:**
- [ ] Sync patterns in rules match the declared sync strategy (e.g. `bidirectional-consistency`, `research-progress`)
- [ ] No Sync Rule references a file pattern that matches zero files

**Refinement (tier 4):**
- [ ] Could any Sync Rules be merged or simplified?

---

## Custom-Specific Categories

These categories are only checked for type: custom projects (tier 3+).

### `sync-rules` — Sync Rule Health

**Quality** — Are the Sync Rules in CLAUDE.md correct and complete?
- [ ] Every file pattern in Sync Rules matches at least one actual file
- [ ] Every document section referenced in Sync Rules exists in the primary document
- [ ] No Sync Rules reference files that have been renamed or removed
- [ ] The sync strategy matches actual usage (declared strategy vs observed commit patterns)
- [ ] Current Milestone reflects the actual phase of the project
- [ ] No two Sync Rules match overlapping file patterns without clear precedence

**Refinement (tier 4):**
- [ ] Are there rules that overlap or could be merged into one?
- [ ] Are any rules so broad they match files they shouldn't?
- [ ] Could the primary document be restructured to make Sync Rules simpler?
- [ ] Are there common types of changes not captured by any rule?

### `project-currency` — Is the Project Current?

**Quality** — Does the project reflect its actual current state?
- [ ] Primary document milestone matches the actual current phase
- [ ] No sections describe work that has been completed but is still marked as planned
- [ ] No participants listed who are no longer active (if participant lists exist)
- [ ] Referenced external documents, tools, or systems still exist and are accessible
- [ ] No completed work items remain marked as "planned" or "in progress"
- [ ] External tool links (Notion, Figma, Jira, etc.) are reachable and point to current content

**Refinement (tier 4):**
- [ ] Could the primary document be reorganised to surface current work more prominently?
- [ ] Are historical phases cluttering the document and making it harder to navigate?

---

## Output Format

Universal findings appear without a prefix. Custom-specific findings use `[custom]`:

```
## project-health report — sync-rules, project-currency, primary-doc [augmented]

### CRITICAL (must fix)
- [custom][artifacts] Primary Document path 'docs/vision.md' declared in CLAUDE.md does not exist

### HIGH (should fix)
- [custom][sync-rules] Sync Rule pattern 'catalog/*.md' matches no files — directory may have been renamed
- [custom][project-currency] Milestone says "Phase 1 - Discovery" but Phase 2 work is underway

### MEDIUM (worth fixing)
- [custom][sync-rules] Two rules both match 'docs/meetings/' — consolidate to one rule

### LOW (nice to fix)
- [custom][project-currency] External Figma link in primary doc returns 404

### PASS
✅ docs-sync, consistency, security, git, conventions
```

Severity scale: see [check-categories.md](../project-health/check-categories.md#severity-scale).

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Custom-specific checks don't replace universal ones | Always run universal checks first (prerequisite) |
| Reporting stale Sync Rules without checking | Rules may be intentionally broad or future-dated | Check if the pattern ever matched before flagging as stale |
| Flagging milestone mismatch without context | Project may be mid-transition between phases | Note the discrepancy, ask user if flag is appropriate |
| Checking only CLAUDE.md, not the primary doc | Primary doc may have drifted even if CLAUDE.md is current | Always read both and compare |
| Treating absent external links as CRITICAL | External tools go offline temporarily | Flag as MEDIUM unless the linked content is referenced by active workflows |

---

## Skill Chaining

**Invoked by:** `project-health` automatically when `type: custom` detected in CLAUDE.md

**Can be invoked directly:** Yes — `/custom-project-health` runs universal checks first, then custom-specific checks, producing identical output to the auto-chained flow

**Prerequisite for:** Nothing currently chains from this skill

**Related skills:**
- `custom-git-commit` — sync strategy and Sync Rules this skill validates
- `update-primary-doc` — applies the sync rules this skill checks for correctness
- `project-health` — universal prerequisite foundation
