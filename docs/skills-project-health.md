# skills-project-health — Design Document

**Status:** Design phase — not yet implemented as a skill
**Skill name (planned):** `skills-project-health`
**Slash command (planned):** `/skills-project-health`
**Invoked by:** [`project-health`](project-health.md) when `type: skills` declared in CLAUDE.md

This document tracks the skills-repository-specific health checks that augment the universal checks in `project-health`.

---

## Purpose

Runs after `project-health` completes its universal checks. Adds checks specific to Claude Code skill collection repositories — the most extensive type-specific skill, covering skill structure, chaining, marketplace integration, and validator infrastructure.

---

## Prerequisite

**This skill builds on [`project-health`](project-health.md).** All universal checks run first. This skill adds skills-repository-specific checks on top.

---

## Augmentations to Universal Checks

These extend the universal categories with skills-repository-specific items:

| Universal check | Quality additions | Refinement additions |
|----------------|------------------|---------------------|
| `primary-doc` | README.md reflects current skill collection (counts, descriptions, chaining table) | Could README sections be better organised for discoverability? |
| `artifacts` | All skills have `SKILL.md`, `commands/<name>.md`, `.claude-plugin/plugin.json` | Are any plugin.json files more complex than they need to be? |
| `conventions` | CSO rules documented; skill naming patterns documented; chaining conventions documented | Could naming convention documentation be more concise? |
| `framework` | CSO description examples are correct; skill chaining examples match actual behaviour | Could chaining documentation be better structured? |

---

## Skills-Specific Categories

These categories only exist for skills repositories and are not present in `project-health`:

### `cross-refs` — Cross-Reference Integrity

**Quality** — Are all skill cross-references complete and bidirectional?
- [ ] Every skill mentioned in the chaining table exists
- [ ] Chaining is bidirectional where required (A→B means B mentions A)
- [ ] Skill Chaining Reference table covers all skills including new additions
- [ ] Prerequisites sections reference skills that exist
- [ ] All markdown links to other `.md` files resolve

**Refinement** — Could the reference structure be simpler or more navigable?
- [ ] Are any chains unnecessarily long?
- [ ] Could the chaining table be reorganised to group related skills more intuitively?
- [ ] Do the number of cross-references between two skills suggest they should merge?

### `coverage` — Integration Coverage

**Quality** — Are new skills and features fully wired into the broader system?
- [ ] Every skill has a `commands/<skill-name>.md` slash command file
- [ ] Every skill is in `.claude-plugin/marketplace.json` plugins list
- [ ] Every skill appears in README.md § Skills section
- [ ] New skills appear in README.md § Skill Chaining Reference table
- [ ] New skills appear in CLAUDE.md § Key Skills
- [ ] Every validator is wired into `scripts/validate_all.py` at the correct tier

**Refinement** — Are there integration points that could be automated or simplified?
- [ ] Are any manual integration steps candidates for automation?
- [ ] Are there steps consistently forgotten, suggesting a better workflow?

### `quality` — Skill Craft Quality

**Quality** — Are skills well-written and will they trigger correctly?
- [ ] All descriptions start with "Use when..." (CSO compliance)
- [ ] No descriptions summarise the workflow (only trigger conditions)
- [ ] No first/second person in descriptions ("I", "you")
- [ ] All major skills have: Prerequisites (if layered), Common Pitfalls, Success Criteria
- [ ] Flowcharts use `flowchart TD` with semantic labels
- [ ] Flowcharts only used where decision points are non-obvious
- [ ] No skill is excessively long (rough budget: ~400 lines)

**Refinement** — Could skills be more concise or easier to follow?
- [ ] Are there skills where the workflow could be expressed in fewer steps?
- [ ] Are any flowcharts earning their complexity, or would a numbered list be clearer?
- [ ] Could any Common Pitfalls rows be removed because they're obvious or never occur?

### `naming` — Naming Consistency

**Quality** — Are skill names consistent across all the places they appear?
- [ ] Skill name in frontmatter matches directory name
- [ ] Skill name in marketplace.json matches directory name
- [ ] Command file named `commands/<skill-name>.md`
- [ ] Skill name in README matches actual name
- [ ] New language skills follow established naming patterns (`lang-dev`, `lang-code-review`)

**Refinement** — Are names clear and discoverable, not just consistent?
- [ ] Would a new user guess the right skill name without reading the docs?
- [ ] Are any names technically accurate but unintuitive?

### `infrastructure` — Tooling Infrastructure

**Quality** — Is the supporting infrastructure correct?
- [ ] All validators in `scripts/validation/` are wired into `validate_all.py`
- [ ] Each validator is in the correct tier (COMMIT: <2s, PUSH: <30s, CI: <5min)
- [ ] Session-start hook is registered in `~/.claude/settings.json`
- [ ] Hook script matches the template in `hooks/check_project_setup.sh`
- [ ] Generated files are in `.gitignore`

**Refinement** — Could the infrastructure be leaner?
- [ ] Are any two validators doing overlapping checks that could be merged?
- [ ] Are any validators in a higher tier than their speed justifies?
- [ ] Could any scripts be removed because the problem they solve no longer exists?

### `dependencies` — Skill Dependencies

**Quality** — Do skill dependency chains actually work?
- [ ] All skills listed as Prerequisites exist
- [ ] No circular dependency chains
- [ ] plugin.json dependency names match actual skill names
- [ ] Marketplace dependency resolution would succeed for all skills

**Refinement** — Could dependency chains be simplified?
- [ ] Are any chains deeper than necessary?
- [ ] Could any skill with only one dependent be absorbed into that dependent?

### `performance` — Token Budget

**Quality** — Are skills within their token budget?
- [ ] No SKILL.md over ~400 lines
- [ ] Heavy reference material extracted to separate files
- [ ] No duplicate content across skills inflating token cost

**Refinement** — Could skills be leaner without losing value?
- [ ] Are there skill sections that add length without adding guidance?
- [ ] Are there validators whose findings could fold into an existing validator?

### `effectiveness` — Skill Effectiveness

**Quality** — Are skills correctly scoped and triggered?
- [ ] No two skills overlap significantly in purpose
- [ ] No descriptions so generic they trigger on everything
- [ ] No descriptions so specific they never trigger
- [ ] Obvious use cases for the project type are covered

**Refinement** — Are skills as useful as they could be?
- [ ] Are any skills doing so little they'd be better absorbed into their caller?
- [ ] Are there common workflows requiring 3+ skills that could be wrapped in one?

---

## Output Format

Same severity rating as `project-health`, prefixed with `[skills]`:

```
### CRITICAL (must fix)
- [skills][coverage] issue-workflow missing from README § Skill Chaining Reference

### HIGH (should fix)
- [skills][cross-refs] git-commit says it routes to blog-git-commit but blog-git-commit doesn't mention being invoked by git-commit

### LOW (nice to fix)
- [skills][performance] update-primary-doc/SKILL.md is 312 lines — approaching budget
```
