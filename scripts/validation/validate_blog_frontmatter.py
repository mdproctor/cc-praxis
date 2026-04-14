#!/usr/bin/env python3
"""
Validate frontmatter in blog entry files (docs/_posts/).

Checks:
- entry_type present and valid (article | note)
- subtype present for notes (e.g. diary)
- projects present and non-empty list
- tags, if present, is a list
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity, print_summary
)
from utils.yaml_utils import extract_frontmatter

VALID_ENTRY_TYPES = {'article', 'note'}
BLOG_DIR = Path('docs/_posts')


def validate_blog_entry_frontmatter(frontmatter: dict) -> list[str]:
    """
    Validate blog entry frontmatter fields.
    Returns list of error message strings — empty list means valid.
    """
    errors = []

    # entry_type required and valid
    entry_type = frontmatter.get('entry_type')
    if not entry_type:
        errors.append("Missing required field: entry_type (article | note)")
    elif entry_type not in VALID_ENTRY_TYPES:
        errors.append(
            f"Invalid entry_type '{entry_type}': must be one of "
            f"{sorted(VALID_ENTRY_TYPES)}"
        )

    # projects required and non-empty list
    projects = frontmatter.get('projects')
    if projects is None:
        errors.append("Missing required field: projects (non-empty list of project identifiers)")
    elif not isinstance(projects, list):
        errors.append(f"projects must be a list, got {type(projects).__name__}")
    elif len(projects) == 0:
        errors.append("projects must be non-empty")

    # subtype required for notes
    if entry_type == 'note':
        subtype = frontmatter.get('subtype')
        if not subtype:
            errors.append(
                "Missing required field: subtype for entry_type 'note' "
                "(e.g. 'diary')"
            )

    # tags must be a list if present
    tags = frontmatter.get('tags')
    if tags is not None and not isinstance(tags, list):
        errors.append(f"tags must be a list, got {type(tags).__name__}")

    return errors


def validate_blog_file(path: Path) -> list[ValidationIssue]:
    """Validate a single blog entry file."""
    issues = []

    frontmatter, error, _ = extract_frontmatter(path)

    if error:
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(path),
            line_number=1,
            message=error,
            fix_suggestion="Add valid YAML frontmatter"
        ))
        return issues

    for msg in validate_blog_entry_frontmatter(frontmatter):
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(path),
            line_number=1,
            message=msg,
            fix_suggestion="Add or correct the field in frontmatter"
        ))

    return issues


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Validate blog entry frontmatter')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('files', nargs='*', help='Specific files to check')
    args = parser.parse_args()

    if args.files:
        blog_files = [Path(f) for f in args.files]
    else:
        blog_files = sorted(BLOG_DIR.glob('*.md')) if BLOG_DIR.exists() else []
        blog_files = [f for f in blog_files if f.name != 'INDEX.md']

    all_issues = []
    for path in blog_files:
        all_issues.extend(validate_blog_file(path))

    result = ValidationResult(
        validator_name='Blog Entry Frontmatter',
        issues=all_issues,
        files_checked=len(blog_files)
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_summary(result, verbose=args.verbose)

    sys.exit(result.exit_code)


if __name__ == '__main__':
    main()
