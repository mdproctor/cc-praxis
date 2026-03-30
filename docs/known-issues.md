# Known Issues Registry

This document tracks all known skill quality issues that have been discovered and fixed. Each issue has a corresponding regression test in `tests/regression/`.

**Purpose:** Prevent issues from recurring by documenting root causes, fixes, and validation procedures.

---

## Issue #001: CSO Violation - Workflow in Description

**Status:** ✅ Fixed
**Severity:** CRITICAL
**Date Discovered:** 2026-01-15
**Date Fixed:** 2026-03-30

### Symptom
Skill has workflow summary in description field instead of triggering conditions.

### Impact
**Expensive Wallpaper** - Claude reads the description, thinks it understands the workflow, and never loads the full skill body. The skill becomes useless because Claude follows the incomplete description instead of the detailed instructions in SKILL.md.

### Root Cause
The description field is visible in Claude's `available_skills` list. It's tempting to summarize what the skill does in this field. However, descriptions should focus on **WHEN** to use (symptoms, triggers, conditions), not **HOW** it works (workflow, process, steps).

### Example Violation
```yaml
description: Use when executing plans - dispatches subagent per task with code review between tasks
```

Problems:
- "dispatches" - workflow keyword
- "per task" - process description
- "code review between tasks" - sequential workflow description

### Correct Example
```yaml
description: Use when executing implementation plans with independent tasks in the current session
```

Focuses on:
- WHEN: "executing implementation plans"
- Context: "with independent tasks"
- Scope: "in the current session"

### Detection
**Automated:** `scripts/validation/validate_cso.py`

Checks for:
- Workflow keywords: step, then, invoke, run, execute, dispatch
- Tool names: Read, Write, Edit, Bash, Agent
- Process patterns: "step 1", "then run", "after reading"

### Prevention
- ✅ Pre-commit validation via `skill-review` skill
- ✅ Regression test: `tests/regression/issue-001-cso-violation.json`
- ✅ Documentation: CLAUDE.md § Frontmatter Requirements
- ✅ Deep analysis checklist includes CSO compliance

### Last Occurrence
2026-01-15 (fixed in commit abc123)

### Test Coverage
✅ Automated validation (`validate_cso.py`)
✅ Regression test exists
✅ Runs in CI pipeline

---

## Issue Template

```markdown
## Issue #XXX: Title

**Status:** 🔴 Active | ✅ Fixed | ⚠️ Partial
**Severity:** CRITICAL | WARNING | NOTE
**Date Discovered:** YYYY-MM-DD
**Date Fixed:** YYYY-MM-DD

### Symptom
What did we observe?

### Impact
What was the consequence?

### Root Cause
Why did it happen?

### Example Violation
Code/text that demonstrates the problem.

### Correct Example
Code/text showing the fix.

### Detection
How do we catch this?

### Prevention
What stops it from happening again?

### Last Occurrence
When did this last appear?

### Test Coverage
What tests cover this?
```

---

## Adding a New Issue

When you discover and fix an issue:

1. **Assign next issue number** (increment from last)
2. **Document in this file** using template above
3. **Create regression test** in `tests/regression/issue-XXX-description.json`
4. **Add validation** (automated if possible)
5. **Update checklists** if new category of issue
6. **Run full test suite** to verify fix doesn't break anything

## Issue Categories

| Category | Count | Examples |
|----------|-------|----------|
| CSO Violations | 1 | #001 |
| Broken References | 0 | - |
| Missing Sections | 0 | - |
| Flowchart Errors | 0 | - |
| Logical Contradictions | 0 | - |

**Total Issues:** 1
**Active Issues:** 0
**Fixed Issues:** 1
