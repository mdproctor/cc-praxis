#!/usr/bin/env python3
"""
Validate that hardcoded project type lists stay in sync with the canonical
list defined in CLAUDE.md's "The Four Project Types" table.

Canonical source of truth: CLAUDE.md § The Four Project Types table.

A "hardcoded list" is a line where 3+ canonical type names appear
consecutively, separated only by delimiters (|  /  ,  or  and) with
no significant prose between them. This distinguishes actual lists like:

  Choices: skills | java | custom | generic  # nocheck:project-types
  (skills/java/custom/generic)  # nocheck:project-types

...from prose sentences that happen to mention several types:

  "routes to java-git-commit for type: java, custom-git-commit for type: custom"

Checks:
- Canonical list can be extracted from CLAUDE.md
- All hardcoded lists contain every canonical type
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity,
    find_skills_root, read_file_with_line_numbers, print_summary
)

VALIDATOR_NAME = "Project Type List Consistency"

SCAN_EXTENSIONS = {'.md', '.sh', '.py'}
CANONICAL_FILE = 'CLAUDE.md'

# Inline suppression marker — append to a line to mark a partial list as intentional.
# Markdown:  <!-- nocheck:project-types -->
# Python/sh: # nocheck:project-types
SUPPRESS_MARKER = 'nocheck:project-types'

# Regex to extract type names from the canonical CLAUDE.md table row, e.g.:
#   | **`skills`** | Skills repository | ...
CANONICAL_ROW_RE = re.compile(r'^\|\s*\*{0,2}`([a-z][a-z0-9-]*)`\*{0,2}\s*\|')

# Separator pattern: only | / , whitespace, or the words 'or'/'and'
# This deliberately excludes prose words so we match lists, not sentences.
_SEP = r'[\s]*[|/,][\s]*(?:or\s+|and\s+)?'


def _build_list_pattern(canonical_types: list[str]) -> re.Pattern:
    """
    Build a regex matching 3+ canonical type names in a consecutive delimited
    list (separated only by |, /, or ,).  Matches the entire run so we can
    extract which types were present.
    """
    t = '|'.join(re.escape(t) for t in canonical_types)
    one = f'(?:{t})'
    return re.compile(
        rf'\b{one}(?:{_SEP}{one}){{2,}}\b',
        re.IGNORECASE
    )


def extract_canonical_types(root: Path) -> tuple[list[str], str]:
    """
    Extract the canonical project type list from CLAUDE.md.
    Returns (types, error_message). error_message is empty on success.
    """
    claude_md = root / CANONICAL_FILE
    if not claude_md.exists():
        return [], f"{CANONICAL_FILE} not found at {root}"

    lines = read_file_with_line_numbers(claude_md)
    in_table = False
    types = []

    for _lineno, line in lines:
        if 'Project Types' in line or '## Project Type Awareness' in line:
            in_table = True
            continue
        if in_table:
            if line.startswith('## ') and 'Project Type' not in line:
                break
            match = CANONICAL_ROW_RE.match(line)
            if match:
                types.append(match.group(1))

    if not types:
        return [], (
            f"Could not extract project types from {CANONICAL_FILE}. "
            "Expected a table under '## Project Type Awareness' / 'The Four Project Types' "
            "with rows like | **`typename`** | ..."
        )

    return types, ""


def find_hardcoded_lists(
    file_path: Path,
    canonical_types: list[str],
    list_pattern: re.Pattern,
) -> list[ValidationIssue]:
    """
    Scan a file for delimited project type lists and check they are complete.
    """
    issues = []
    lines = read_file_with_line_numbers(file_path)

    for lineno, line in lines:
        if SUPPRESS_MARKER in line:
            continue
        for match in list_pattern.finditer(line):
            matched_text = match.group(0)
            found = [t for t in canonical_types
                     if re.search(rf'\b{re.escape(t)}\b', matched_text, re.IGNORECASE)]
            missing = [t for t in canonical_types if t not in found]

            if missing:
                issues.append(ValidationIssue(
                    severity=Severity.CRITICAL,
                    file_path=str(file_path),
                    line_number=lineno,
                    message=(
                        f"Hardcoded project type list is missing: {', '.join(missing)}. "
                        f"List found: '{matched_text}'"
                    ),
                    fix_suggestion=(
                        f"Add {', '.join(missing)} to this list, or update {CANONICAL_FILE} "
                        "if the type was intentionally removed."
                    )
                ))

    return issues


def files_to_scan(root: Path) -> list[Path]:
    """Collect all scannable files, excluding the canonical source itself."""
    canonical = (root / CANONICAL_FILE).resolve()
    files = []

    for ext in SCAN_EXTENSIONS:
        for f in root.rglob(f'*{ext}'):
            if any(part.startswith('.') for part in f.parts):
                continue
            if any(skip in f.parts for skip in ('venv', 'node_modules', '__pycache__')):
                continue
            if f.resolve() == canonical:
                continue
            files.append(f)

    return sorted(files)


def validate() -> ValidationResult:
    root = find_skills_root()
    issues = []
    files_checked = 0

    canonical_types, error = extract_canonical_types(root)
    if error:
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=CANONICAL_FILE,
            line_number=None,
            message=f"Cannot determine canonical project types: {error}",
            fix_suggestion=(
                f"Ensure {CANONICAL_FILE} has a 'Project Types' table under "
                "'## Project Type Awareness' with rows like | **`typename`** | ..."
            )
        ))
        return ValidationResult(VALIDATOR_NAME, issues, 0)

    list_pattern = _build_list_pattern(canonical_types)

    for file_path in files_to_scan(root):
        files_checked += 1
        issues.extend(find_hardcoded_lists(file_path, canonical_types, list_pattern))

    return ValidationResult(VALIDATOR_NAME, issues, files_checked)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    result = validate()
    print_summary(result, verbose=args.verbose)

    if result.issues:
        for issue in sorted(result.issues, key=lambda x: (x.severity.value, x.file_path)):
            print(f"\n{issue}")

    sys.exit(result.exit_code)


if __name__ == '__main__':
    main()
