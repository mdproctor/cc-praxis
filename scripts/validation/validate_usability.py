#!/usr/bin/env python3
"""
TIER: PRE-PUSH (30s budget)

Usability/UX validator - checks readability and clarity.
"""
import sys
from pathlib import Path
from typing import List, Dict
import re

def check_long_sentences(content: str, file_path: Path) -> List[Dict]:
    """Find overly long sentences (>40 words)."""
    issues = []

    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Skip code blocks, headers, lists
        if line.strip().startswith(('```', '#', '-', '*', '|')):
            continue

        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+\s+', line)
        for sentence in sentences:
            word_count = len(sentence.split())
            if word_count > 40:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'long_sentence',
                    'file': str(file_path),
                    'line': line_num,
                    'word_count': word_count,
                    'message': f"{file_path}:{line_num}: Long sentence ({word_count} words, recommend <40)"
                })

    return issues

def check_dense_paragraphs(content: str, file_path: Path) -> List[Dict]:
    """Find dense paragraphs (>8 consecutive non-empty lines)."""
    issues = []

    lines = content.split('\n')
    para_start = None
    para_length = 0

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip code blocks, headers, lists, tables
        if stripped.startswith(('```', '#', '-', '*', '|')) or not stripped:
            if para_length > 8 and para_start:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'dense_paragraph',
                    'file': str(file_path),
                    'line': para_start,
                    'length': para_length,
                    'message': f"{file_path}:{para_start}: Dense paragraph ({para_length} lines, recommend <8)"
                })
            para_start = None
            para_length = 0
        else:
            if para_start is None:
                para_start = line_num
            para_length += 1

    return issues

def check_ambiguous_pronouns(content: str, file_path: Path) -> List[Dict]:
    """Find potentially ambiguous pronoun usage."""
    issues = []

    # Patterns that often indicate ambiguous pronouns
    ambiguous_patterns = [
        r'\bIt\s+(?:will|should|must|can|does|is|has)',
        r'\bThis\s+(?:will|should|must|can|does|is|has)',
        r'\bThat\s+(?:will|should|must|can|does|is|has)',
    ]

    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Skip code blocks, headers, code examples
        if line.strip().startswith(('```', '#', '`')):
            continue

        for pattern in ambiguous_patterns:
            if re.search(pattern, line):
                # Only flag if line is short and pronoun is at start (more likely to be ambiguous)
                if len(line.split()) < 15 and line.strip().startswith(('It ', 'This ', 'That ')):
                    issues.append({
                        'severity': 'NOTE',
                        'type': 'ambiguous_pronoun',
                        'file': str(file_path),
                        'line': line_num,
                        'message': f"{file_path}:{line_num}: Potentially ambiguous pronoun - ensure clear antecedent"
                    })

    return issues

def check_double_negatives(content: str, file_path: Path) -> List[Dict]:
    """Find double negatives."""
    issues = []

    # Common double negative patterns
    patterns = [
        r"not\s+un\w+",
        r"never\s+not",
        r"cannot\s+not",
        r"don't\s+not",
    ]

    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({
                    'severity': 'WARNING',
                    'type': 'double_negative',
                    'file': str(file_path),
                    'line': line_num,
                    'message': f"{file_path}:{line_num}: Double negative found - consider positive phrasing"
                })

    return issues

def check_excessive_nesting(content: str, file_path: Path) -> List[Dict]:
    """Find excessive markdown list nesting (>3 levels)."""
    issues = []

    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Count indentation level for list items
        if re.match(r'^(\s*)([-*]|\d+\.)\s', line):
            indent = len(re.match(r'^(\s*)', line).group(1))
            # Assume 2 spaces per level
            level = indent // 2

            if level > 3:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'excessive_nesting',
                    'file': str(file_path),
                    'line': line_num,
                    'level': level,
                    'message': f"{file_path}:{line_num}: Excessive nesting (level {level}, recommend ≤3)"
                })

    return issues

def check_heading_hierarchy(content: str, file_path: Path) -> List[Dict]:
    """Check for broken heading hierarchy (e.g., # followed by ###)."""
    issues = []

    lines = content.split('\n')
    prev_level = 0

    for line_num, line in enumerate(lines, 1):
        match = re.match(r'^(#{1,6})\s+', line)
        if match:
            level = len(match.group(1))

            # Heading should not skip levels (e.g., ## to ####)
            if prev_level > 0 and level > prev_level + 1:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'broken_hierarchy',
                    'file': str(file_path),
                    'line': line_num,
                    'skipped': level - prev_level - 1,
                    'message': f"{file_path}:{line_num}: Broken heading hierarchy (skipped from level {prev_level} to {level})"
                })

            prev_level = level

    return issues

def validate_file(file_path: Path) -> List[Dict]:
    """Validate a single file for usability issues."""
    try:
        content = file_path.read_text()
    except Exception as e:
        return [{
            'severity': 'WARNING',
            'type': 'read_error',
            'file': str(file_path),
            'message': f"Could not read {file_path}: {e}"
        }]

    issues = []
    issues.extend(check_long_sentences(content, file_path))
    issues.extend(check_dense_paragraphs(content, file_path))
    issues.extend(check_ambiguous_pronouns(content, file_path))
    issues.extend(check_double_negatives(content, file_path))
    issues.extend(check_excessive_nesting(content, file_path))
    issues.extend(check_heading_hierarchy(content, file_path))

    return issues

def main():
    """Main entry point."""
    base_dir = Path('.')

    # Find all SKILL.md files
    skill_files = list(base_dir.glob('*/SKILL.md'))

    # Also check README.md and CLAUDE.md
    doc_files = [
        f for f in [base_dir / 'README.md', base_dir / 'CLAUDE.md']
        if f.exists()
    ]

    all_files = skill_files + doc_files
    all_issues = []

    print("Usability/UX Check", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Checking {len(all_files)} files for usability issues...", file=sys.stderr)

    for file_path in all_files:
        all_issues.extend(validate_file(file_path))

    # Categorize issues
    critical = [i for i in all_issues if i['severity'] == 'CRITICAL']
    warnings = [i for i in all_issues if i['severity'] == 'WARNING']
    notes = [i for i in all_issues if i['severity'] == 'NOTE']

    if not all_issues:
        print("✅ No usability issues found", file=sys.stderr)
        sys.exit(0)

    if critical:
        print(f"\n❌ CRITICAL: {len(critical)}", file=sys.stderr)
        for issue in critical:
            print(f"  - {issue['message']}", file=sys.stderr)

    if warnings:
        print(f"\n⚠️  WARNING: {len(warnings)}", file=sys.stderr)
        # Show first 10 warnings to avoid spam
        for issue in warnings[:10]:
            print(f"  - {issue['message']}", file=sys.stderr)
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings", file=sys.stderr)

    if notes:
        print(f"\nℹ️  NOTE: {len(notes)}", file=sys.stderr)
        # Show first 5 notes
        for issue in notes[:5]:
            print(f"  - {issue['message']}", file=sys.stderr)
        if len(notes) > 5:
            print(f"  ... and {len(notes) - 5} more notes", file=sys.stderr)

    # Exit code: 1 for CRITICAL, 2 for WARNING only, 0 for NOTE only
    if critical:
        sys.exit(1)
    elif warnings:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
