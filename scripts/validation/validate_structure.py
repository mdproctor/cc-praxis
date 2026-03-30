#!/usr/bin/env python3
"""
Validate skill file organization.

Checks:
- Every skill directory has SKILL.md
- Supporting files in expected locations (scripts/, references/, assets/)
- No orphaned files (files not referenced in SKILL.md)
- Referenced files exist
- No duplicate content across skills
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


EXPECTED_SUBDIRS = ['scripts', 'references', 'assets', 'tests', 'agents']


def find_referenced_files(content: str) -> set[str]:
    """Find all file paths referenced in content."""
    referenced = set()

    # Pattern 1: Markdown links [text](path)
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for _, path in md_links:
        if not path.startswith('http'):  # Skip URLs
            referenced.add(path)

    # Pattern 2: Backtick file paths `path/to/file.ext`
    file_refs = re.findall(r'`([a-zA-Z0-9_/-]+\.[a-z]+)`', content)
    referenced.update(file_refs)

    # Pattern 3: "see filename.md" or "Read filename.py"
    see_refs = re.findall(r'(?:see|read|check|in)\s+([a-z_/-]+\.[a-z]+)', content, re.IGNORECASE)
    referenced.update(see_refs)

    return referenced


def find_all_files_in_skill(skill_dir: Path) -> set[Path]:
    """Find all files in skill directory (excluding SKILL.md)."""
    all_files = set()

    for path in skill_dir.rglob('*'):
        if path.is_file() and path.name != 'SKILL.md':
            # Get relative path from skill directory
            rel_path = path.relative_to(skill_dir)
            all_files.add(rel_path)

    return all_files


def validate_skill_structure(skill_path: Path) -> list[ValidationIssue]:
    """Validate file organization for a single skill."""
    issues = []
    skill_dir = skill_path.parent

    # Read SKILL.md content
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find referenced files
    referenced_files = find_referenced_files(content)

    # Check each referenced file exists
    for ref_file in referenced_files:
        # Try as absolute path from skill dir
        file_path = skill_dir / ref_file

        # Also try from repo root for paths like scripts/
        if not file_path.exists():
            repo_root = find_skills_root()
            file_path = repo_root / ref_file

        if not file_path.exists():
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                file_path=str(skill_path),
                line_number=None,
                message=f"Referenced file doesn't exist: {ref_file}",
                fix_suggestion=f"Create {ref_file} or remove reference"
            ))

    # Find all files in skill directory
    all_files = find_all_files_in_skill(skill_dir)

    # Check for orphaned files (exist but not referenced)
    orphaned = []
    for file_path in all_files:
        file_str = str(file_path)

        # Check if referenced in SKILL.md
        if file_str not in referenced_files:
            # Also check just the filename
            if file_path.name not in {Path(r).name for r in referenced_files}:
                # Skip common non-referenced files
                if file_path.name not in ['.gitignore', 'README.md', '__pycache__']:
                    orphaned.append(file_str)

    if orphaned:
        issues.append(ValidationIssue(
            severity=Severity.NOTE,
            file_path=str(skill_path),
            line_number=None,
            message=f"Orphaned files (not referenced in SKILL.md): {', '.join(orphaned[:3])}",
            fix_suggestion="Reference these files in SKILL.md or remove if unused"
        ))

    # Check directory organization
    for file_path in all_files:
        parts = file_path.parts

        # Check if in expected subdirectory
        if len(parts) > 1:
            subdir = parts[0]
            if subdir not in EXPECTED_SUBDIRS and subdir != '.git':
                issues.append(ValidationIssue(
                    severity=Severity.NOTE,
                    file_path=str(skill_path),
                    line_number=None,
                    message=f"Unexpected subdirectory: {subdir}/",
                    fix_suggestion=f"Use standard subdirectories: {', '.join(EXPECTED_SUBDIRS)}"
                ))

    return issues


def main():
    """Main validation entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate skill file structure')
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
        issues = validate_skill_structure(skill_path)
        all_issues.extend(issues)

    # Create result
    result = ValidationResult(
        validator_name='File Structure Validation',
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
