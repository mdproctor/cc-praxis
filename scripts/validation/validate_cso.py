#!/usr/bin/env python3
"""
Validate CSO (Claude Search Optimization) compliance.

Checks that skill descriptions focus on WHEN to use (triggering conditions)
rather than HOW it works (workflow summary).

CSO Violations (Expensive Wallpaper):
- Description contains workflow keywords
- Description describes process/steps
- Description lists tools used
- Description summarizes what the skill does instead of when to use it

This causes Claude to follow the description instead of reading the skill body,
making the skill useless.
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity,
    find_all_skill_files,
    print_summary
)
from utils.yaml_utils import extract_frontmatter


# Workflow keywords that indicate "how" instead of "when"
WORKFLOW_KEYWORDS = [
    'step', 'then', 'invoke', 'run', 'execute', 'dispatch',
    'call', 'trigger', 'spawn', 'launch', 'start',
    'first', 'second', 'third', 'next', 'after', 'before',
    'reads', 'writes', 'creates', 'updates', 'deletes',
    'analyzes', 'validates', 'checks', 'verifies'
]

# Tool names that shouldn't be in descriptions
TOOL_NAMES = [
    'Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob',
    'Agent', 'Skill', 'TodoWrite', 'TaskCreate'
]

# Process/workflow indicators
PROCESS_PATTERNS = [
    r'\b(step \d+|phase \d+)\b',  # "step 1", "phase 2"
    r'\bthen\s+\w+',  # "then invoke", "then run"
    r'\bafter\s+\w+ing\b',  # "after reading"
    r'\b(per|for each)\s+\w+',  # "per task", "for each file"
]


def check_workflow_keywords(description: str) -> list[str]:
    """Find workflow keywords in description."""
    found = []
    desc_lower = description.lower()

    for keyword in WORKFLOW_KEYWORDS:
        if re.search(rf'\b{keyword}\b', desc_lower):
            found.append(keyword)

    return found


def check_tool_names(description: str) -> list[str]:
    """Find tool names in description."""
    found = []

    for tool in TOOL_NAMES:
        if re.search(rf'\b{tool}\b', description):
            found.append(tool)

    return found


def check_process_patterns(description: str) -> list[str]:
    """Find process/workflow patterns in description."""
    found = []

    for pattern in PROCESS_PATTERNS:
        matches = re.findall(pattern, description, re.IGNORECASE)
        found.extend(matches)

    return found


def validate_skill_cso(skill_path: Path) -> list[ValidationIssue]:
    """Validate CSO compliance for a single skill."""
    issues = []

    # Extract frontmatter
    frontmatter, error, _ = extract_frontmatter(skill_path)

    if error or 'description' not in frontmatter:
        # Frontmatter validation will catch this
        return issues

    description = frontmatter['description']

    # Check for workflow keywords
    workflow_keywords = check_workflow_keywords(description)
    if workflow_keywords:
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(skill_path),
            line_number=3,
            message=f"CSO violation: Description contains workflow keywords: {', '.join(workflow_keywords[:5])}",
            fix_suggestion="Describe WHEN to use (symptoms, triggers), not HOW it works (workflow steps)"
        ))

    # Check for tool names
    tool_names = check_tool_names(description)
    if tool_names:
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(skill_path),
            line_number=3,
            message=f"CSO violation: Description mentions tools: {', '.join(tool_names)}",
            fix_suggestion="Remove tool names - description should focus on when/why, not implementation details"
        ))

    # Check for process patterns
    process_patterns = check_process_patterns(description)
    if process_patterns:
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(skill_path),
            line_number=3,
            message=f"CSO violation: Description describes process: {', '.join(process_patterns[:3])}",
            fix_suggestion="Remove process description - focus on triggering conditions"
        ))

    # Check description length (already in frontmatter validator, but critical for CSO)
    if len(description) > 500:
        issues.append(ValidationIssue(
            severity=Severity.WARNING,
            file_path=str(skill_path),
            line_number=3,
            message=f"Description too detailed: {len(description)} chars (prefer 100-500)",
            fix_suggestion="Shorter descriptions trigger more reliably - focus on key conditions"
        ))

    return issues


def main():
    """Main validation entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate CSO compliance')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('files', nargs='*', help='Specific files to check')
    args = parser.parse_args()

    # Find skills to validate
    if args.files:
        skill_files = [Path(f) for f in args.files]
    else:
        skill_files = find_all_skill_files()

    # Validate each skill
    all_issues = []
    for skill_path in skill_files:
        issues = validate_skill_cso(skill_path)
        all_issues.extend(issues)

    # Create result
    result = ValidationResult(
        validator_name='CSO Compliance Validation',
        issues=all_issues,
        files_checked=len(skill_files)
    )

    # Output results
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_summary(result, verbose=args.verbose)

    sys.exit(result.exit_code)


if __name__ == '__main__':
    main()
