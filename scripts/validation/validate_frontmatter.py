#!/usr/bin/env python3
"""
Validate YAML frontmatter in SKILL.md files.

Checks:
- YAML frontmatter exists and is valid
- Required fields present: name, description
- name matches directory name
- name uses hyphens (not underscores/spaces)
- description starts with "Use when"
- description is under 500 characters
- description contains no first/second person
- No extra fields beyond name, description, compatibility
"""

import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity,
    find_all_skill_files, get_skill_name_from_path,
    print_summary
)
from utils.yaml_utils import extract_frontmatter, validate_yaml_structure


def validate_frontmatter_content(
    skill_path: Path,
    frontmatter: dict
) -> list[ValidationIssue]:
    """Validate frontmatter field content."""
    issues = []
    skill_name = get_skill_name_from_path(skill_path)

    # Check name field
    if 'name' in frontmatter:
        name = frontmatter['name']

        # Name should match directory name
        if name != skill_name:
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(skill_path),
                line_number=2,  # Typically line 2
                message=f"Name mismatch: frontmatter has '{name}' but directory is '{skill_name}'",
                fix_suggestion=f"Change name to: {skill_name}"
            ))

        # Name should use hyphens
        if '_' in name or ' ' in name:
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(skill_path),
                line_number=2,
                message=f"Name uses underscores or spaces: '{name}'",
                fix_suggestion=f"Use hyphens: {name.replace('_', '-').replace(' ', '-')}"
            ))

    # Check description field
    if 'description' in frontmatter:
        description = frontmatter['description']

        # Should start with "Use when"
        if not description.startswith('Use when'):
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(skill_path),
                line_number=3,  # Typically line 3
                message="Description doesn't start with 'Use when'",
                fix_suggestion="Start description with: Use when..."
            ))

        # Should be under 500 characters
        if len(description) > 500:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                file_path=str(skill_path),
                line_number=3,
                message=f"Description too long: {len(description)} chars (max 500)",
                fix_suggestion="Shorten description to focus on triggering conditions"
            ))

        # Should not contain first/second person
        personal_pronouns = re.findall(r'\b(I|me|my|you|your)\b', description, re.IGNORECASE)
        if personal_pronouns:
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(skill_path),
                line_number=3,
                message=f"Description contains personal pronouns: {', '.join(set(personal_pronouns))}",
                fix_suggestion="Use third person only (e.g., 'Use when the user...')"
            ))

    return issues


def validate_skill_frontmatter(skill_path: Path) -> list[ValidationIssue]:
    """Validate frontmatter for a single skill."""
    issues = []

    # Extract frontmatter
    frontmatter, error, end_line = extract_frontmatter(skill_path)

    if error:
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(skill_path),
            line_number=1,
            message=error,
            fix_suggestion="Add valid YAML frontmatter at the top of the file"
        ))
        return issues

    # Validate YAML structure
    is_valid, error_msg = validate_yaml_structure(frontmatter)
    if not is_valid:
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(skill_path),
            line_number=1,
            message=error_msg,
            fix_suggestion="Fix YAML structure"
        ))
        return issues

    # Validate field content
    issues.extend(validate_frontmatter_content(skill_path, frontmatter))

    return issues


def main():
    """Main validation entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate skill frontmatter')
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
        issues = validate_skill_frontmatter(skill_path)
        all_issues.extend(issues)

    # Create result
    result = ValidationResult(
        validator_name='Frontmatter Validation',
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
