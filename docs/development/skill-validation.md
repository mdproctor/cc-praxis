# SKILL.md Validation

Pre-commit review for Claude Code skills to ensure structural integrity, CSO compliance,
and documentation completeness before committing to the repository.

**Only for type: skills repositories.** Invoked when SKILL.md files are staged.

## Core Rules

- **Block commits on CRITICAL findings** — structural violations must be fixed first
- Focus on **format compliance and conventions**, not subjective quality
- Check **cross-references bidirectionally** — if A references B, verify B references A
- Validate **Mermaid syntax** — invalid flowcharts break skill loading
- Ensure **CSO description compliance** — no workflow summaries in frontmatter

## Workflow

### Step 1 — Identify skills to review

**If specific skill provided:**
```bash
ls <skill-path>/SKILL.md
```

**If reviewing staged changes:**
```bash
git diff --staged --name-only | grep 'SKILL.md$'
```

**If no context:**
Ask user which skill(s) to review.

### Step 2 — Review each skill

For each SKILL.md, run all checks systematically:

1. **Read the full file** (always read, never assume)
2. **Check frontmatter** (CRITICAL: name, description, CSO compliance)
3. **Validate flowcharts** (if present, test with `dot`)
4. **Check naming conventions** (match against patterns)
5. **Verify cross-references** (read referenced skills to confirm bidirectional)
6. **Check documentation completeness** (Success Criteria, Common Pitfalls, Prerequisites)

### Step 3 — Present findings

Group findings by severity:

```markdown
## Skill: skill-name

### CRITICAL Issues (must fix before commit)
- [Issue description with line reference]

### WARNING Issues (fix before commit)
- [Issue description with line reference]

### NOTE Issues (improve when possible)
- [Issue description with line reference]
```

**If CRITICAL findings exist:**
> "❌ **Cannot commit.** Fix CRITICAL issues first, then re-review."

**If only WARNING/NOTE findings:**
> "⚠️ **Fix warnings before commit.** Notes can be addressed later."

**If no findings:**
> "✅ **Approved.** Skill meets all structural requirements."

### Step 4 — Verify cross-references

When skill references another skill, read that skill to verify:

**Prerequisites pattern:**
```markdown
## Prerequisites

**This skill builds on `other-skill`**. Apply all rules from:
- **other-skill**: [specific rules]
```

Check: Does `other-skill/SKILL.md` exist? Does it make sense as a foundation?

**Skill Chaining pattern:**
```markdown
## Skill Chaining

**Chains to other-skill:**
After [milestone], invoke other-skill for [purpose].
```

Check: Does `other-skill/SKILL.md` mention being invoked by this skill?

### Step 5 — Test flowcharts (if present)

Extract Mermaid blocks and validate with the automated validator:

```bash
# Run automated Mermaid validation (PUSH tier)
python3 scripts/validation/validate_flowcharts.py <skill-path>/SKILL.md

# Or validate all skills at once
python3 scripts/validate_all.py --tier push
```

**Common Mermaid syntax errors to watch for:**
- Parentheses inside edge labels: `-->|yes (label)|` → fix: `-->|"yes (label)"|`
- Parentheses inside node labels: `[Node (detail)]` → fix: `["Node (detail)"]`

## Review Severity Decision Flow

```mermaid
flowchart TD
    Start_review((Start review))
    Frontmatter_missing_invalid_{Frontmatter missing/invalid?}
    Flowchart_syntax_invalid_{Flowchart syntax invalid?}
    CSO_description_violation_{CSO description violation?}
    Naming_convention_violated_{Naming convention violated?}
    Cross_references_broken_{Cross-references broken?}
    Documentation_incomplete_{Documentation incomplete?}
    CRITICAL__Block_commit[CRITICAL: Block commit]
    WARNING__Fix_before_commit[WARNING: Fix before commit]
    NOTE__Improve_when_possible[NOTE: Improve when possible]
    Report_findings[Report findings]
    Approved((Approved))
    Start_review --> Frontmatter_missing_invalid_
    Frontmatter_missing_invalid_ -->|yes| CRITICAL__Block_commit
    Frontmatter_missing_invalid_ -->|no| Flowchart_syntax_invalid_
    Flowchart_syntax_invalid_ -->|yes| CRITICAL__Block_commit
    Flowchart_syntax_invalid_ -->|no| CSO_description_violation_
    CSO_description_violation_ -->|yes| CRITICAL__Block_commit
    CSO_description_violation_ -->|no| Naming_convention_violated_
    Naming_convention_violated_ -->|yes| WARNING__Fix_before_commit
    Naming_convention_violated_ -->|no| Cross_references_broken_
    Cross_references_broken_ -->|yes| WARNING__Fix_before_commit
    Cross_references_broken_ -->|no| Documentation_incomplete_
    Documentation_incomplete_ -->|yes| NOTE__Improve_when_possible
    Documentation_incomplete_ -->|no| Report_findings
    CRITICAL__Block_commit --> Report_findings
    WARNING__Fix_before_commit --> Report_findings
    NOTE__Improve_when_possible --> Report_findings
    Report_findings --> Approved
```

## Review Checklist

### Frontmatter Structure (CRITICAL)

| Check | What to verify |
|-------|---------------|
| **name field** | Present, matches directory name, uses hyphens (not underscores/spaces) |
| **description field** | Present, starts with "Use when...", under 500 chars |
| **No workflow summary** | Description describes *when to use*, not *how it works* |
| **Third person** | No "I" or "you" in description |
| **YAML syntax** | Valid YAML, `>` for multi-line descriptions |

**CSO violations are CRITICAL** — descriptions that summarize workflow cause Claude to
skip reading the skill body.

❌ Bad: `description: Use when executing plans - dispatches subagent per task with code review between tasks`

✅ Good: `description: Use when executing implementation plans with independent tasks in the current session`

### Naming Conventions (WARNING)

| Pattern | Examples |
|---------|----------|
| Generic principles | `*-principles` suffix: `code-review-principles`, `security-audit-principles` |
| Language-specific | Language prefix: `java-dev`, `java-code-review`, `python-dev` |
| Tool-specific | Tool prefix: `maven-dependency-update`, `gradle-dependency-update` |
| Framework-specific | Framework prefix: `quarkus-flow-dev`, `spring-security-audit` |

**Check:**
- ✅ Name follows hierarchical pattern (generic vs specific)
- ✅ Prefix/suffix matches skill's scope
- ✅ Hyphen-separated (not underscore or camelCase)

### Cross-References (WARNING)

| Section | What to verify |
|---------|---------------|
| **Prerequisites** | Layered skills reference their foundations |
| **Skill Chaining** | Bidirectional references (if A → B, then B mentions A) |
| **Invocation claims** | If skill says "invoked by X", verify X actually invokes it |

**Check:**
- ✅ All referenced skills exist
- ✅ Cross-references are bidirectional where appropriate
- ✅ No dangling references (skill doesn't exist)

### Flowcharts (CRITICAL if present)

| Check | What to verify |
|-------|---------------|
| **Valid Mermaid** | Syntax is valid `flowchart TD` with proper node/edge format |
| **Semantic labels** | No generic labels like `step1`, `helper2`, `pattern3` |
| **Appropriate use** | Used for decisions, not for reference material or linear steps |

**Invalid flowcharts break skill loading** — this is CRITICAL.

Test validity:
```bash
python3 scripts/validation/validate_flowcharts.py <skill-path>/SKILL.md
```

### Documentation Completeness (NOTE)

| Skill Type | Required Sections |
|------------|------------------|
| **All skills** | Skill Chaining or Prerequisites section |
| **Artifact-producing** | Success Criteria section with checkboxes |
| **Major skills** | Common Pitfalls table (Mistake \| Why It's Wrong \| Fix) |
| **Layered skills** | Prerequisites section referencing foundations |

**Check:**
- ✅ Success Criteria present for skills that produce artifacts (commits, ADRs, updates)
- ✅ Common Pitfalls table for major skills
- ✅ Prerequisites for skills that build on others

### File Organization (NOTE)

| Check | What to verify |
|-------|---------------|
| **Heavy reference** | >300 line reference material extracted to separate `.md` files |
| **Skill body focus** | SKILL.md focuses on workflow/principles, not exhaustive API docs |
| **Clear references** | External files referenced clearly from SKILL.md |

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Workflow summary in description | Claude follows description instead of reading skill body (skill becomes expensive wallpaper) | Remove workflow details, describe *when to use* only |
| Missing name or description field | Skill won't load | Add required frontmatter fields |
| Generic flowchart labels | Unreadable, unclear intent | Use semantic labels (e.g., "Check BOM alignment" not "step1") |
| Dangling cross-references | Skill references non-existent skill | Verify all referenced skills exist |
| Missing Success Criteria | Premature completion claims | Add checklist for artifact-producing skills |
| Invalid Mermaid syntax | Skill loading fails | Run `validate_flowcharts.py` before committing |
| Unidirectional chaining | Incomplete documentation graph | Make cross-references bidirectional |
| First-person in description | Injected into system prompt | Use third person ("Use when..." not "I help you...") |
| No Common Pitfalls table | Users repeat known mistakes | Document mistakes with fixes |

## Edge Cases

| Situation | Action |
|-----------|--------|
| Skill has no flowcharts | Skip flowchart validation |
| Generic `-principles` skill | Verify it's NOT invoked directly, only referenced via Prerequisites |
| Skill references external file | Verify file exists in skill directory |
| Multiple SKILL.md files staged | Review all, report findings together |
| Skill naming doesn't match pattern | WARNING if functional, NOTE if just style |

## Deep Analysis Mode

For extended skill analysis, see **CLAUDE.md § Quality Assurance Framework § Deep Analysis Procedures**.

## Success Criteria

Skill review is complete when:

- ✅ All SKILL.md files read
- ✅ Frontmatter validated (name, description, CSO compliance)
- ✅ Flowcharts tested (if present)
- ✅ Naming conventions checked
- ✅ Cross-references verified bidirectionally
- ✅ Documentation completeness assessed
- ✅ Findings presented grouped by severity

**Not complete until** all checks performed and user informed of results.
