#!/usr/bin/env python3
"""
Validate skill naming conventions.

Checks:
- Generic principles: *-principles suffix
- Language-specific: language prefix (java-*, python-*)
- Tool-specific: tool prefix (maven-*, gradle-*)
- Framework-specific: framework prefix (quarkus-*, spring-*)
- No mixed patterns
- Consistent hyphenation
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity,
    find_all_skill_files, get_skill_name_from_path,
    print_summary
)


# Naming patterns
NAMING_PATTERNS = {
    'principles': {
        'pattern': r'^[a-z]+-principles$',
        'description': 'Generic principles (e.g., code-review-principles)',
        'examples': ['code-review-principles', 'security-audit-principles']
    },
    'language': {
        'pattern': r'^(java|python|go|rust|javascript|typescript)-[a-z-]+$',
        'description': 'Language-specific (e.g., java-dev, python-test)',
        'examples': ['java-dev', 'python-code-review']
    },
    'tool': {
        'pattern': r'^(maven|gradle|npm|pip|cargo)-[a-z-]+$',
        'description': 'Tool-specific (e.g., maven-dependency-update)',
        'examples': ['maven-dependency-update', 'gradle-build']
    },
    'framework': {
        'pattern': r'^(quarkus|spring|react|vue|django)-[a-z-]+$',
        'description': 'Framework-specific (e.g., quarkus-flow-dev)',
        'examples': ['quarkus-flow-dev', 'spring-security']
    },
    'workflow': {
        'pattern': r'^(git|update|sync|create)-[a-z-]+$',
        'description': 'Workflow skills (e.g., git-commit, update-design)',
        'examples': ['git-commit', 'update-readme']
    },
    'superpowers': {
        'pattern': r'^superpowers:[a-z-]+$',
        'description': 'Superpowers namespace',
        'examples': ['superpowers:brainstorming', 'superpowers:test-driven-development']
    },
    'external': {
        'pattern': r'^[a-z-]+:[a-z-]+$',
        'description': 'External namespace (org:skill-name)',
        'examples': ['frontend-design:frontend-design']
    }
}


def categorize_skill(skill_name: str) -> tuple[str, bool]:
    """
    Categorize skill by naming pattern.

    Returns:
        (category, matches_pattern)
    """
    for category, info in NAMING_PATTERNS.items():
        if re.match(info['pattern'], skill_name):
            return category, True

    return 'uncategorized', False


def validate_skill_naming(skill_path: Path) -> list[ValidationIssue]:
    """Validate naming for a single skill."""
    issues = []
    skill_name = get_skill_name_from_path(skill_path)

    # Check for underscores or spaces
    if '_' in skill_name or ' ' in skill_name:
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(skill_path),
            line_number=None,
            message=f"Skill name uses underscores or spaces: {skill_name}",
            fix_suggestion=f"Use hyphens: {skill_name.replace('_', '-').replace(' ', '-')}"
        ))
        return issues  # Don't check further if basic format is wrong

    # Categorize skill
    category, matches = categorize_skill(skill_name)

    if not matches:
        issues.append(ValidationIssue(
            severity=Severity.NOTE,
            file_path=str(skill_path),
            line_number=None,
            message=f"Skill name doesn't match standard patterns: {skill_name}",
            fix_suggestion="Consider using: <type>-<name> where type is language/tool/framework, or <name>-principles for generic skills"
        ))

    # Check for ambiguous patterns
    # e.g., "java-maven-something" is ambiguous - is it java or maven?
    parts = skill_name.split('-')
    if len(parts) >= 3:
        # Check if multiple prefixes
        language_prefixes = ['java', 'python', 'go', 'rust']
        tool_prefixes = ['maven', 'gradle', 'npm', 'pip']
        framework_prefixes = ['quarkus', 'spring', 'react', 'vue']

        has_language = any(p in parts for p in language_prefixes)
        has_tool = any(p in parts for p in tool_prefixes)
        has_framework = any(p in parts for p in framework_prefixes)

        if sum([has_language, has_tool, has_framework]) > 1:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                file_path=str(skill_path),
                line_number=None,
                message=f"Ambiguous skill name with multiple type indicators: {skill_name}",
                fix_suggestion="Use primary type as prefix (framework > language > tool)"
            ))

    return issues


def main():
    """Main validation entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate skill naming conventions')
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
        issues = validate_skill_naming(skill_path)
        all_issues.extend(issues)

    # Create result
    result = ValidationResult(
        validator_name='Naming Convention Validation',
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
