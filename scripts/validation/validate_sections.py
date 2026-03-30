#!/usr/bin/env python3
"""
Validate required sections in SKILL.md files.

Checks based on skill type:
- All skills: "Skill Chaining" OR "Prerequisites" section
- Artifact-producing skills: "Success Criteria" with checkboxes
- Major skills: "Common Pitfalls" table
- Layered skills: "Prerequisites" referencing foundation
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
from utils.skill_parser import has_section, extract_sections


# Keywords that indicate artifact-producing skills
ARTIFACT_KEYWORDS = [
    'commit', 'update', 'create', 'sync', 'generate',
    'write', 'deploy', 'publish', 'build'
]

# Keywords for major/complex skills that should have Common Pitfalls
MAJOR_SKILL_INDICATORS = [
    'review', 'audit', 'test', 'dev', 'commit'
]


def is_artifact_producing(skill_name: str) -> bool:
    """Check if skill produces artifacts (commits, files, updates)."""
    return any(keyword in skill_name for keyword in ARTIFACT_KEYWORDS)


def is_major_skill(skill_name: str, content: str) -> bool:
    """Check if this is a major/complex skill."""
    # Check skill name
    if any(keyword in skill_name for keyword in MAJOR_SKILL_INDICATORS):
        return True

    # Check word count (major skills are typically longer)
    word_count = len(re.findall(r'\b\w+\b', content))
    return word_count > 500


def is_layered_skill(skill_name: str, sections: dict) -> bool:
    """Check if skill builds on other skills."""
    # Check for Prerequisites section
    if 'Prerequisites' in sections:
        return True

    # Check naming patterns that indicate layering
    # e.g., java-code-review extends code-review-principles
    if '-' in skill_name:
        parts = skill_name.split('-')
        # If starts with language/framework, likely extends something
        if parts[0] in ['java', 'python', 'quarkus', 'spring', 'maven', 'gradle']:
            return True

    return False


def validate_skill_sections(skill_path: Path) -> list[ValidationIssue]:
    """Validate sections for a single skill."""
    issues = []
    skill_name = get_skill_name_from_path(skill_path)

    # Read content
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = extract_sections(content)

    # All skills must have either "Skill Chaining" or "Prerequisites"
    has_chaining = has_section(content, 'Skill Chaining')
    has_prerequisites = has_section(content, 'Prerequisites')

    if not has_chaining and not has_prerequisites:
        issues.append(ValidationIssue(
            severity=Severity.WARNING,
            file_path=str(skill_path),
            line_number=None,
            message="Missing both 'Skill Chaining' and 'Prerequisites' sections",
            fix_suggestion="Add '## Skill Chaining' or '## Prerequisites' section"
        ))

    # Artifact-producing skills need Success Criteria
    if is_artifact_producing(skill_name):
        has_success_criteria = has_section(content, 'Success Criteria')
        if not has_success_criteria:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                file_path=str(skill_path),
                line_number=None,
                message="Artifact-producing skill missing 'Success Criteria' section",
                fix_suggestion="Add '## Success Criteria' with checkboxes for completion conditions"
            ))
        else:
            # Check for checkboxes
            success_section = sections.get('Success Criteria', '')
            if '- ✅' not in success_section and '- [ ]' not in success_section:
                issues.append(ValidationIssue(
                    severity=Severity.NOTE,
                    file_path=str(skill_path),
                    line_number=None,
                    message="Success Criteria section lacks checkboxes",
                    fix_suggestion="Add checkboxes: - ✅ criterion"
                ))

    # Major skills should have Common Pitfalls
    if is_major_skill(skill_name, content):
        has_pitfalls = has_section(content, 'Common Pitfalls')
        if not has_pitfalls:
            issues.append(ValidationIssue(
                severity=Severity.NOTE,
                file_path=str(skill_path),
                line_number=None,
                message="Major skill missing 'Common Pitfalls' section",
                fix_suggestion="Add '## Common Pitfalls' table: Mistake | Why It's Wrong | Fix"
            ))
        else:
            # Check table structure
            pitfalls_section = sections.get('Common Pitfalls', '')
            if '| Mistake |' not in pitfalls_section:
                issues.append(ValidationIssue(
                    severity=Severity.NOTE,
                    file_path=str(skill_path),
                    line_number=None,
                    message="Common Pitfalls should use table format",
                    fix_suggestion="Use table: | Mistake | Why It's Wrong | Fix |"
                ))

    # Layered skills should have Prerequisites
    if is_layered_skill(skill_name, sections) and not has_prerequisites:
        issues.append(ValidationIssue(
            severity=Severity.NOTE,
            file_path=str(skill_path),
            line_number=None,
            message="Layered skill should have 'Prerequisites' section",
            fix_suggestion="Add '## Prerequisites' section referencing foundation skills"
        ))

    return issues


def main():
    """Main validation entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate required sections')
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
        issues = validate_skill_sections(skill_path)
        all_issues.extend(issues)

    # Create result
    result = ValidationResult(
        validator_name='Required Sections Validation',
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
