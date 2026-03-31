#!/usr/bin/env python3
"""
Universal Markdown Document Validation

Detects corruption in .md files across all project types (skills, java, blog, custom, generic).
Used by sync workflows to prevent document corruption before committing.

Usage:
    python validate_document.py <filepath>

Exit codes:
    0 - No issues
    1 - CRITICAL issues found (blocks commit)
    2 - WARNING issues found (should review)
"""

import sys
import re
from pathlib import Path
from collections import Counter


def find_duplicate_headers(filepath):
    """Find duplicate ## section headers (excluding code blocks)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    headers = []
    in_code_block = False

    for i, line in enumerate(lines, 1):
        # Track code block boundaries
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue

        # Only check headers outside code blocks
        if not in_code_block and line.startswith('## '):
            header = line.strip()
            headers.append((header, i))

    # Find duplicates
    header_texts = [h[0] for h in headers]
    counts = Counter(header_texts)
    duplicates = [(h, [line for hdr, line in headers if hdr == h])
                  for h, count in counts.items() if count > 1]

    return duplicates


def find_corrupted_tables(filepath):
    """Find table headers followed by prose instead of separator/data rows (excluding code blocks)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    corrupted = []
    in_code_block = False
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Track code block boundaries
        if line.startswith('```'):
            in_code_block = not in_code_block
            i += 1
            continue

        # Only check tables outside code blocks
        if not in_code_block:
            # Check if this is a table header (has | ... | ... |)
            if re.match(r'^\|.*\|.*\|$', line) and '---' not in line:
                # Next line should be separator (|---|---|) or data row (| ... | ... |)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()

                    # Check if next line is separator, table row, or blank (table end)
                    is_separator = re.match(r'^\|[-:\s]+\|[-:\s]+\|', next_line)
                    is_table_row = re.match(r'^\|.*\|.*\|$', next_line)
                    is_blank = not next_line  # Blank line = table ended normally

                    if not is_separator and not is_table_row and not is_blank:
                        # Next line is prose, not table content or table end
                        corrupted.append({
                            'line': i + 1,
                            'header': line,
                            'invalid_next': next_line
                        })
        i += 1

    return corrupted


def find_orphaned_sections(filepath):
    """Find section headers with no content before next header"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    orphaned = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check if this is a section header
        if line.startswith('## '):
            # Look ahead for content before next header
            has_content = False
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()

                # Hit another header without finding content
                if next_line.startswith('## '):
                    break

                # Found non-empty, non-header content
                if next_line and not next_line.startswith('#'):
                    has_content = True
                    break

                j += 1

            if not has_content and j < len(lines):
                # Orphaned section (header immediately followed by another header)
                orphaned.append({
                    'line': i + 1,
                    'header': line,
                    'next_header': lines[j].strip() if j < len(lines) else 'EOF'
                })
        i += 1

    return orphaned


def check_line_diff(filepath):
    """Check for large structural changes (requires git)"""
    try:
        import subprocess

        # Check if file is staged
        result = subprocess.run(
            ['git', 'diff', '--staged', '--numstat', filepath],
            capture_output=True,
            text=True,
            cwd=Path(filepath).parent
        )

        if result.returncode == 0 and result.stdout.strip():
            # Parse numstat output: additions deletions filename
            parts = result.stdout.strip().split('\t')
            if len(parts) >= 2:
                additions = int(parts[0]) if parts[0] != '-' else 0
                deletions = int(parts[1]) if parts[1] != '-' else 0
                net_change = additions + deletions
                return net_change

        return 0
    except Exception:
        return 0


def validate_document(filepath):
    """Run all validation checks on a document"""
    filepath = Path(filepath)

    if not filepath.exists():
        return {
            'critical': [f"File not found: {filepath}"],
            'warnings': []
        }

    issues = {
        'critical': [],
        'warnings': []
    }

    # Check 1: Duplicate headers
    duplicates = find_duplicate_headers(filepath)
    if duplicates:
        for header, lines in duplicates:
            issues['critical'].append(
                f"Duplicate header '{header}' at lines: {', '.join(map(str, lines))}"
            )

    # Check 2: Corrupted tables
    corrupted_tables = find_corrupted_tables(filepath)
    if corrupted_tables:
        for table in corrupted_tables:
            issues['critical'].append(
                f"Corrupted table at line {table['line']}: "
                f"Table header followed by prose instead of data row"
            )

    # Check 3: Orphaned sections
    orphaned = find_orphaned_sections(filepath)
    if orphaned:
        for section in orphaned:
            issues['warnings'].append(
                f"Orphaned section at line {section['line']}: "
                f"'{section['header']}' has no content before next section"
            )

    # Check 4: Large structural changes
    line_diff = check_line_diff(filepath)
    if line_diff > 100:
        issues['warnings'].append(
            f"Large structural change: {line_diff} lines modified - review recommended"
        )

    return issues


def validate_document_group(group):
    """
    Validate entire DocumentGroup (primary + modules).

    Entry point for modular documentation validation. Delegates to
    modular_validator.py for cross-module checks.

    Args:
        group: DocumentGroup (from document_discovery.py)

    Returns:
        dict with 'critical' and 'warnings' lists (aggregated from all checks)
    """
    try:
        from modular_validator import validate_document_group as validate_group
    except ImportError:
        # Fallback if modular_validator not available
        try:
            # Try absolute import
            import sys
            from pathlib import Path
            script_dir = Path(__file__).parent
            sys.path.insert(0, str(script_dir))
            from modular_validator import validate_document_group as validate_group
        except ImportError:
            # No modular validation available, fall back to single-file validation
            return validate_document(group.primary_file)

    # Run modular validation (returns list of ValidationResult objects)
    results = validate_group(group)

    # Aggregate into legacy format for backwards compatibility
    aggregated = {
        'critical': [],
        'warnings': []
    }

    for result in results:
        aggregated['critical'].extend(result.critical)
        aggregated['warnings'].extend(result.warnings)

    return aggregated


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_document.py <filepath>", file=sys.stderr)
        sys.exit(3)

    filepath = sys.argv[1]
    issues = validate_document(filepath)

    has_critical = len(issues['critical']) > 0
    has_warnings = len(issues['warnings']) > 0

    if has_critical:
        print(f"❌ CRITICAL issues found in {filepath}:")
        for issue in issues['critical']:
            print(f"  - {issue}")

    if has_warnings:
        print(f"⚠️  WARNING issues found in {filepath}:")
        for issue in issues['warnings']:
            print(f"  - {issue}")

    if not has_critical and not has_warnings:
        print(f"✅ {filepath} - No issues found")
        sys.exit(0)
    elif has_critical:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
