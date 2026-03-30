# Validation and Testing Scripts

This directory contains validation scripts, test runners, and utilities for ensuring skill quality.

## Directory Structure

```
scripts/
├── validation/     # Automated validation scripts
│   ├── validate_frontmatter.py
│   ├── validate_cso.py
│   ├── validate_flowcharts.py
│   ├── validate_references.py
│   ├── validate_naming.py
│   ├── validate_sections.py
│   └── validate_structure.py
├── testing/        # Test execution and reporting
│   ├── run_skill_tests.py
│   ├── run_regression_tests.py
│   └── generate_report.py
├── utils/          # Shared utilities
│   ├── skill_parser.py
│   ├── yaml_utils.py
│   └── common.py
└── validate_all.py # Master orchestrator
```

## Usage

### Run All Validations

```bash
python scripts/validate_all.py
```

### Run Specific Validation

```bash
python scripts/validation/validate_frontmatter.py
python scripts/validation/validate_cso.py
```

### Run with Auto-Fix (where safe)

```bash
python scripts/validate_all.py --fix
```

### Verbose Output

```bash
python scripts/validate_all.py --verbose
```

### JSON Output

```bash
python scripts/validate_all.py --json > validation_report.json
```

## Exit Codes

All scripts follow this convention:

- `0` - All checks passed
- `1` - CRITICAL issues found (must fix before commit)
- `2` - WARNING issues found (should fix before commit)
- `3` - NOTE issues found (improve when possible)
- `4` - Script execution error

## Pre-Commit Integration

The validation scripts are integrated into the pre-commit workflow via `git-commit` skill.

See CLAUDE.md § Quality Assurance Framework for complete documentation.
