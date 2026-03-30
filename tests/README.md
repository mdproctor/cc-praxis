# Skill Testing Framework

This directory contains the test framework for validating skills through functional tests and regression tests.

## Directory Structure

```
tests/
├── regression/         # Regression tests for known issues
│   ├── issue-001-cso-violation.json
│   ├── issue-002-circular-dependency.json
│   └── ...
├── fixtures/           # Test input files
│   ├── sample_java_project/
│   ├── sample_skill.md
│   └── ...
├── templates/          # Test case templates
│   ├── test_case_template.json
│   └── regression_test_template.json
└── README.md           # This file
```

## Test Types

### 1. Functional Tests

Functional tests execute skills against real scenarios to verify they work as expected.

**Location:** Each skill directory can have a `tests/` subdirectory with `test_cases.json`

**Example:**
```
java-git-commit/
  SKILL.md
  tests/
    test_cases.json         # Test definitions
    fixtures/               # Input files
    expected/               # Expected outputs
```

**Test Case Format:**
```json
{
  "skill_name": "java-git-commit",
  "tests": [
    {
      "id": "basic-commit",
      "description": "Commit single Java file change",
      "setup": "scripts/setup_basic_commit.sh",
      "prompt": "commit these changes",
      "expected_behavior": {
        "invokes_skills": ["update-design", "update-claude-md"],
        "creates_commit": true,
        "commit_message_matches": "^(feat|fix|refactor)\\(.*\\):.*",
        "files_modified": ["docs/DESIGN.md", "CLAUDE.md"]
      },
      "assertions": [
        {"type": "file_exists", "path": "docs/DESIGN.md"},
        {"type": "git_commit_exists", "message_contains": "Co-Authored-By: Claude"},
        {"type": "skill_invoked", "skill": "update-design"}
      ]
    }
  ]
}
```

### 2. Regression Tests

Regression tests prevent known issues from recurring.

**Location:** `tests/regression/issue-XXX-description.json`

**Regression Test Format:**
```json
{
  "issue_id": "001",
  "title": "CSO Violation - Workflow in Description",
  "description": "Skill had workflow summary in description field",
  "severity": "critical",
  "date_discovered": "2026-01-15",
  "date_fixed": "2026-01-15",

  "original_violation": {
    "skill": "superpowers:execute-plan",
    "description": "Use when executing plans - dispatches subagent per task with code review between tasks"
  },

  "why_it_failed": "Claude followed description instead of reading full skill (expensive wallpaper)",

  "fix_applied": "Removed workflow details from description",

  "correct_example": {
    "description": "Use when executing implementation plans with independent tasks in the current session"
  },

  "validation": {
    "type": "cso_check",
    "validator": "validate_cso.py",
    "description_must_not_contain": ["dispatches", "per task", "code review", "then"]
  },

  "test_cases": [
    {
      "test_name": "Check no CSO violations in all skills",
      "command": "python scripts/validation/validate_cso.py",
      "expected_exit_code": 0
    }
  ]
}
```

## Running Tests

### Run All Functional Tests

```bash
# Not yet implemented
python scripts/testing/run_skill_tests.py --all
```

### Run Specific Skill Tests

```bash
# Not yet implemented
python scripts/testing/run_skill_tests.py java-git-commit
```

### Run All Regression Tests

```bash
# Not yet implemented
python scripts/testing/run_regression_tests.py
```

### Run Specific Regression Test

```bash
# Not yet implemented
python scripts/testing/run_regression_tests.py --issue 001
```

## Creating New Tests

### Creating a Functional Test

1. Create `tests/` directory in skill folder
2. Copy template: `cp tests/templates/test_case_template.json skill-name/tests/test_cases.json`
3. Edit test cases
4. Create setup scripts if needed
5. Run tests: `python scripts/testing/run_skill_tests.py skill-name`

### Creating a Regression Test

1. Document the issue in `docs/known-issues.md`
2. Copy template: `cp tests/templates/regression_test_template.json tests/regression/issue-XXX-description.json`
3. Fill in issue details
4. Define validation checks
5. Run: `python scripts/testing/run_regression_tests.py --issue XXX`

## Test Coverage

View test coverage report:

```bash
# Not yet implemented
python scripts/testing/test_coverage.py --report
```

Expected output:
```
Skill Test Coverage Report
===========================

User-Invocable Skills:
  java-git-commit:     5/5 branches tested (100%) ✅
  git-commit:          3/4 branches tested (75%)  ⚠️
  skill-review:        8/8 validations tested (100%) ✅

Auto-Invoked Skills:
  update-design:       2/2 scenarios tested (100%) ✅
  update-readme:       1/1 scenario tested (100%) ✅

Regression Coverage:
  Known issues:        12
  With regression tests: 12 (100%) ✅

Overall Coverage: 92% (23/25 test scenarios)
```

## Test Writing Guidelines

### Good Tests

- ✅ **Realistic prompts** - what users actually say
- ✅ **Observable outputs** - file changes, commits, artifacts
- ✅ **Clear assertions** - specific, verifiable conditions
- ✅ **Independent** - can run in isolation
- ✅ **Repeatable** - same input → same output

### Bad Tests

- ❌ **Vague prompts** - "do the thing"
- ❌ **Subjective outputs** - "code looks good"
- ❌ **Weak assertions** - "some file changed"
- ❌ **Coupled** - depends on other tests running first
- ❌ **Flaky** - passes sometimes, fails sometimes

## Assertion Types

### File Assertions
- `file_exists`: Path exists
- `file_contains`: File contains text
- `file_matches_regex`: File matches pattern
- `file_equals`: File equals expected content

### Git Assertions
- `git_commit_exists`: Commit was created
- `commit_message_matches`: Message matches pattern
- `files_in_commit`: Specific files committed
- `branch_exists`: Branch created

### Skill Assertions
- `skill_invoked`: Skill was called
- `skill_chain_followed`: Expected chain executed
- `no_critical_issues`: Validation passed

### Output Assertions
- `output_contains`: Claude's response contains text
- `no_errors`: No error messages
- `warning_shown`: Expected warning appeared

## Integration with CI

Tests run automatically on:
- Every commit (quick tests only)
- Pull requests (full test suite)
- Scheduled (nightly full validation)

See `.github/workflows/skill-validation.yml` for CI configuration.
