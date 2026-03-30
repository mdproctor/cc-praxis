#!/usr/bin/env python3
"""
Validate cross-references between skills.

Checks:
- All skill names referenced in backticks exist as directories
- All "Chains to X" references have corresponding SKILL.md files
- All "Prerequisites" references exist
- All "Invoked by" references exist
- Bidirectional references (if A chains to B, B should mention A)
- No references to deleted/renamed skills
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity,
    find_all_skill_files, get_skill_name_from_path,
    find_skills_root, print_summary
)
from utils.skill_parser import extract_skill_references, extract_sections, extract_chaining_info


def build_skill_index() -> dict[str, Path]:
    """Build index of skill_name -> skill_path."""
    skill_index = {}

    for skill_path in find_all_skill_files():
        skill_name = get_skill_name_from_path(skill_path)
        skill_index[skill_name] = skill_path

    return skill_index


def extract_all_references(content: str) -> set[str]:
    """Extract all potential skill references from content."""
    # Find all backtick-quoted identifiers
    pattern = r'`([a-z][a-z0-9-]+)`'
    all_matches = set(re.findall(pattern, content))

    # Filter to likely skill names (2-4 hyphenated parts)
    skill_refs = set()
    for match in all_matches:
        parts = match.split('-')
        if 2 <= len(parts) <= 4:
            # Exclude obvious non-skills
            if not any(ext in parts for ext in ['md', 'json', 'yml', 'yaml', 'sh', 'py', 'js']):
                skill_refs.add(match)

    return skill_refs


def validate_skill_references(skill_path: Path, skill_index: dict[str, Path]) -> list[ValidationIssue]:
    """Validate references for a single skill."""
    issues = []

    # Read content
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    skill_name = get_skill_name_from_path(skill_path)

    # Extract all skill references
    references = extract_all_references(content)

    # Check each reference exists
    for ref in references:
        if ref not in skill_index:
            # Check if it might be a file/path instead of skill
            if '/' in ref or '.' in ref:
                continue

            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(skill_path),
                line_number=None,
                message=f"References non-existent skill: `{ref}`",
                fix_suggestion=f"Remove reference or create {ref}/SKILL.md"
            ))

    # Check bidirectional chaining
    sections = extract_sections(content)
    chaining = extract_chaining_info(sections)

    # For each skill we chain to, check if they mention us back
    for target_skill in chaining['chains_to']:
        if target_skill in skill_index:
            target_path = skill_index[target_skill]
            with open(target_path, 'r', encoding='utf-8') as f:
                target_content = f.read()

            # Check if target mentions this skill
            if f'`{skill_name}`' not in target_content:
                issues.append(ValidationIssue(
                    severity=Severity.WARNING,
                    file_path=str(skill_path),
                    line_number=None,
                    message=f"Chains to `{target_skill}` but it doesn't mention `{skill_name}` back",
                    fix_suggestion=f"Add bidirectional reference in {target_skill}/SKILL.md"
                ))

    # For each skill that invokes us, verify they actually reference us
    for invoking_skill in chaining['invoked_by']:
        if invoking_skill in skill_index:
            invoking_path = skill_index[invoking_skill]
            with open(invoking_path, 'r', encoding='utf-8') as f:
                invoking_content = f.read()

            # Check if invoker actually mentions this skill
            if f'`{skill_name}`' not in invoking_content:
                issues.append(ValidationIssue(
                    severity=Severity.WARNING,
                    file_path=str(skill_path),
                    line_number=None,
                    message=f"Claims invoked by `{invoking_skill}` but it doesn't reference us",
                    fix_suggestion=f"Verify {invoking_skill} actually invokes {skill_name}, or remove claim"
                ))

    return issues


def main():
    """Main validation entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate skill cross-references')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('files', nargs='*', help='Specific files to check')
    args = parser.parse_args()

    # Build skill index
    skill_index = build_skill_index()

    # Find skills to validate
    if args.files:
        skill_files = [Path(f) for f in args.files]
    else:
        skill_files = find_all_skill_files()

    # Validate each skill
    all_issues = []
    for skill_path in skill_files:
        issues = validate_skill_references(skill_path, skill_index)
        all_issues.extend(issues)

    # Create result
    result = ValidationResult(
        validator_name='Cross-Reference Validation',
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
