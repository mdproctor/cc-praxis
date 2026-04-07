---
name: skills-project-health
description: >
  Use when health-checking a type: skills (Claude Code skill collection)
  repository, or when invoked automatically by project-health on skills project
  type detection.
---

# skills-project-health

Health checks for Claude Code skill collection repositories. Runs all universal
checks from `project-health` first, then adds skills-specific checks for skill
craft, cross-references, marketplace integration, and validator infrastructure.

## Prerequisites

**This skill builds on `project-health`.** Apply all universal checks first:

- All universal categories: `docs-sync`, `consistency`, `logic`, `config`,
  `security`, `release`, `user-journey`, `git`, `primary-doc`, `artifacts`,
  `conventions`, `framework`
- Same tier system (1–4) and named aliases (`--commit`, `--standard`,
  `--prerelease`, `--deep`)
- Same output format — skills-specific findings are prefixed with `[skills]`

When invoked directly (`/skills-project-health`), run universal checks first,
then skills-specific checks. Output is combined — identical to `project-health`
auto-chaining here.

---

## Tier System

Inherited from `project-health` — see [check-categories.md](../project-health/check-categories.md#tier-system).
Skills-specific categories (`cross-refs`, `coverage`, `quality`, `naming`, `infrastructure`, `dependencies`, `performance`, `effectiveness`) run at tier 3+.

---

## Type-Specific Scan Targets

In addition to the universal document scan, include:

- All `SKILL.md` files in direct subdirectories of the repo root
- All `commands/<skill-name>.md` files
- All `.claude-plugin/plugin.json` files
- `.claude-plugin/marketplace.json` — skill registry and bundle definitions
- `scripts/validate_all.py` and all files under `scripts/validation/`
- `hooks/check_project_setup.sh`
- `~/.claude/settings.json` — session-start hook registration

---

## Augmentations to Universal Checks

These extend universal categories with skills-repository-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] README.md reflects the current skill collection (skill counts match actual skills)
- [ ] README.md § Skill Chaining Reference table includes all skills
- [ ] README.md skill descriptions don't contradict the "Use when..." trigger conditions in each SKILL.md

**Refinement (tier 4):**
- [ ] Could README sections be reorganised for better discoverability?

### `artifacts` augmentations

**Quality:**
- [ ] Every skill directory has a `SKILL.md`
- [ ] Every skill directory has a `commands/<skill-name>.md`
- [ ] Every skill directory has a `.claude-plugin/plugin.json`
- [ ] No phantom skills in `marketplace.json` without a corresponding directory and SKILL.md

**Refinement (tier 4):**
- [ ] Are any `plugin.json` files more complex than they need to be?

### `conventions` augmentations

**Quality:**
- [ ] CSO rules documented in CLAUDE.md (`description` starts with "Use when...", no workflow summaries)
- [ ] Skill naming patterns documented and followed
- [ ] Chaining conventions documented

**Refinement (tier 4):**
- [ ] Could naming convention documentation be more concise?

### `framework` augmentations

**Quality:**
- [ ] CSO description examples in CLAUDE.md are correct (good vs. bad examples valid)
- [ ] Skill chaining examples in CLAUDE.md match actual invocation behaviour

**Refinement (tier 4):**
- [ ] Could chaining documentation be better structured?

---

## Skills-Specific Categories

These categories are only checked for type: skills projects (tier 3+).

### `cross-refs` — Cross-Reference Integrity

**Quality** — Are all skill cross-references complete and bidirectional?
- [ ] Every skill mentioned in the README Skill Chaining Reference table exists on disk
- [ ] Chaining is bidirectional where required (if A chains to B, B mentions being invoked by A)
- [ ] Prerequisites sections reference skills that exist
- [ ] All markdown links to other `.md` files resolve (no 404 within repo)
- [ ] Documented chaining reflects actual invocation — if A says it chains to B, the workflow actually does so
- [ ] No Prerequisites section references a skill with a different purpose than implied

**Refinement (tier 4):**
- [ ] Are any chains unnecessarily long?
- [ ] Could the chaining table be reorganised to group related skills more intuitively?
- [ ] Do the number of cross-references between two skills suggest they should merge?

---

### `coverage` — Integration Coverage

**Quality** — Are new skills and features fully wired into the broader system?
- [ ] Every skill has a `commands/<skill-name>.md` slash command file
- [ ] Every skill is listed in `.claude-plugin/marketplace.json` plugins list
- [ ] Every skill appears in README.md § Skills section
- [ ] New skills appear in README.md § Skill Chaining Reference table
- [ ] New skills appear in CLAUDE.md § Key Skills
- [ ] Every validator in `scripts/validation/` is wired into `scripts/validate_all.py` at the correct tier
- [ ] Every skill in `marketplace.json` has a corresponding directory and SKILL.md (no phantom skills)
- [ ] README skill descriptions match the "Use when..." trigger conditions in each SKILL.md

**Refinement (tier 4):**
- [ ] Are any manual integration steps candidates for automation?
- [ ] Are there steps consistently forgotten, suggesting a better workflow?

---

### `quality` — Skill Craft Quality

**Quality** — Are skills well-written and will they trigger correctly?
- [ ] All `description` fields start with "Use when..." (CSO compliance)
- [ ] No description summarises the workflow (only trigger conditions and symptoms)
- [ ] No first/second person in descriptions ("I", "you")
- [ ] All major skills have: Prerequisites (if layered), Common Pitfalls, Success Criteria sections
- [ ] Flowcharts use `flowchart TD` notation with semantic labels
- [ ] Flowcharts only used where decision points are non-obvious
- [ ] No SKILL.md exceeds ~400 lines

**Refinement (tier 4):**
- [ ] Are there skills where the workflow could be expressed in fewer steps?
- [ ] Are any flowcharts earning their complexity, or would a numbered list be clearer?
- [ ] Could any Common Pitfalls rows be removed because they're obvious or never occur?

---

### `naming` — Naming Consistency

**Quality** — Are skill names consistent across all the places they appear?
- [ ] Skill `name` in frontmatter matches the directory name exactly
- [ ] Skill name in `marketplace.json` matches directory name
- [ ] Command file is named `commands/<skill-name>.md`
- [ ] Skill name in `plugin.json` matches directory name
- [ ] Skill name in README matches actual directory name (no typos or variants)
- [ ] All references to a skill use identical spelling across chaining tables, README, CLAUDE.md

**Refinement (tier 4):**
- [ ] Would a new user guess the right skill name without reading the docs?
- [ ] Are any names technically accurate but unintuitive?

---

### `infrastructure` — Tooling Infrastructure

**Quality** — Is the supporting infrastructure correct?
- [ ] All validators in `scripts/validation/` are wired into `scripts/validate_all.py`
- [ ] Each validator is assigned to the correct tier (COMMIT: <2s, PUSH: <30s, CI: <5min)
- [ ] Session-start hook is registered in `~/.claude/settings.json`
- [ ] Hook script at `hooks/check_project_setup.sh` matches the expected template
- [ ] Generated files (reports, caches) are in `.gitignore`
- [ ] `.gitignore` entries match the files that validators or scripts actually generate

**Refinement (tier 4):**
- [ ] Are any two validators doing overlapping checks that could be merged?
- [ ] Are any validators in a higher tier than their actual speed justifies?
- [ ] Could any scripts be removed because the problem they solve no longer exists?

---

### `dependencies` — Skill Dependencies

**Quality** — Do skill dependency chains actually work?
- [ ] All skills listed as Prerequisites exist on disk
- [ ] No circular dependency chains exist
- [ ] `plugin.json` dependency names match actual skill directory names
- [ ] Marketplace dependency resolution would succeed for all skills
- [ ] Optional dependencies are genuinely optional — the skill functions without them

**Refinement (tier 4):**
- [ ] Are any chains deeper than necessary?
- [ ] Could any skill with only one dependent be absorbed into that dependent?

---

### `performance` — Token Budget

**Quality** — Are skills within their token budget?
- [ ] No SKILL.md exceeds ~400 lines
- [ ] Heavy reference material extracted to separate `.md` files
- [ ] No duplicate content across skills inflating token cost
- [ ] No skill substantially duplicates passages from its dependency skills (each owns its scope)
- [ ] SKILL.md content is about how to use the skill, not background theory

**Refinement (tier 4):**
- [ ] Are there skill sections that add length without adding guidance?
- [ ] Are there validators whose findings could fold into an existing validator?

---

### `effectiveness` — Skill Effectiveness

**Quality** — Are skills correctly scoped and triggered?
- [ ] No two skills overlap significantly in purpose
- [ ] No description is so generic it would trigger on everything
- [ ] No description is so specific it would never trigger
- [ ] Obvious use cases for a skill collection repository are covered
- [ ] Skill workflow outputs match the declared use case (a "validate" skill produces pass/fail, not open-ended commentary)
- [ ] No skill description references other skills by file path rather than human-readable name

**Refinement (tier 4):**
- [ ] Are any skills doing so little they'd be better absorbed into their caller?
- [ ] Are there common workflows requiring 3+ skills that could be wrapped into one?

---

## Output Format

Universal findings appear without a prefix. Skills-specific findings use `[skills]`:

```
## project-health report — cross-refs, coverage, quality [skills]

### CRITICAL (must fix)
- [skills][coverage] issue-workflow missing from README § Skill Chaining Reference

### HIGH (should fix)
- [skills][cross-refs] git-commit says it routes to blog-git-commit but blog-git-commit doesn't mention being invoked by git-commit

### MEDIUM (worth fixing)
- [skills][quality] quarkus-flow-dev/SKILL.md description summarises the workflow instead of trigger conditions

### LOW (nice to fix)
- [skills][performance] update-primary-doc/SKILL.md is 312 lines — approaching budget

### PASS
✅ docs-sync, consistency, security, naming, dependencies
```

Severity scale: see [check-categories.md](../project-health/check-categories.md#severity-scale).

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Skills-specific checks don't replace universal ones | Always run universal checks first (prerequisite) |
| Checking only the README for cross-refs | CLAUDE.md § Key Skills and chaining tables are separate | Check README, CLAUDE.md, and each SKILL.md's chaining section |
| Treating long skills as automatically bad | A 380-line skill covering a complex domain may be fine | Flag only if length is from padding, not substance |
| Marking a skill "not covered" in README when it's principles-only | Principles skills are never invoked directly | Principles skills should be listed as foundations, not as primary entries |
| Flagging missing slash command for principles skills | Principles skills are Prerequisites, not direct invocations | Only flag missing `commands/<name>.md` for user-invocable skills |
| Calling a dependency circular after one hop | Circular means A→B→A, not A→B and B→A in different contexts | Trace the actual invocation chain before flagging |

---

## Skill Chaining

**Invoked by:** `project-health` automatically when `type: skills` detected in CLAUDE.md

**Can be invoked directly:** Yes — `/skills-project-health` runs universal checks first,
then skills-specific checks, producing identical output to the auto-chained flow

**Prerequisite for:** Nothing currently chains from this skill

**Related skills:**
- `project-health` — universal prerequisite foundation
- `project-refine` — companion for improvement opportunities after health is green
- `git-commit` — commit skill for this repository type; references `skill-validation.md` and `readme-sync.md`
