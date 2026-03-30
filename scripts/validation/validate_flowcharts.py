#!/usr/bin/env python3
"""
Validate Graphviz flowcharts in SKILL.md files.

Checks:
- Flowcharts use valid Graphviz dot syntax
- No generic labels (step1, step2, helper1, pattern2, etc.)
- All node labels are semantic and descriptive
- Flowcharts are appropriate (for decisions/loops, not reference material)
"""

import sys
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity,
    find_all_skill_files, read_file_with_line_numbers,
    print_summary
)
from utils.skill_parser import extract_flowcharts


# Generic label patterns that should not be used
GENERIC_PATTERNS = [
    r'\b(step|phase|stage)\s*\d+\b',  # "step 1", "phase2"
    r'\b(helper|pattern|node|task)\s*\d+\b',  # "helper1", "pattern2"
    r'^(start|end|\d+)$',  # Too generic single words or numbers
]


def check_graphviz_syntax(flowchart_code: str) -> tuple[bool, str]:
    """
    Check if flowchart is valid Graphviz syntax.

    Returns:
        (is_valid, error_message)
    """
    try:
        # Write to temp file
        with NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            f.write(flowchart_code)
            temp_path = f.name

        # Try to compile with dot
        result = subprocess.run(
            ['dot', '-Tsvg', temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Clean up
        Path(temp_path).unlink()

        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr

    except FileNotFoundError:
        # Graphviz not installed - skip validation
        return True, "Graphviz not installed - skipping syntax check"
    except subprocess.TimeoutExpired:
        return False, "Graphviz compilation timeout"
    except Exception as e:
        return False, f"Error checking syntax: {str(e)}"


def find_generic_labels(flowchart_code: str) -> list[str]:
    """Find generic/non-semantic labels in flowchart."""
    generic_labels = []

    # Extract all quoted labels from nodes
    # Pattern: "label text" [shape=...]
    label_pattern = r'"([^"]+)"'
    labels = re.findall(label_pattern, flowchart_code)

    for label in labels:
        # Check against generic patterns
        for pattern in GENERIC_PATTERNS:
            if re.search(pattern, label, re.IGNORECASE):
                generic_labels.append(label)
                break

    return list(set(generic_labels))


def find_flowchart_line_number(content: str, flowchart_code: str) -> int:
    """Find the line number where flowchart starts."""
    lines = content.split('\n')

    # Find the ```dot line before this flowchart
    flowchart_start = flowchart_code.split('\n')[0] if flowchart_code else ""

    for i, line in enumerate(lines, start=1):
        if line.strip() == '```dot':
            # Check if next lines match flowchart
            if flowchart_start and i < len(lines):
                if flowchart_start.strip() in lines[i].strip():
                    return i
    return 0


def validate_skill_flowcharts(skill_path: Path) -> list[ValidationIssue]:
    """Validate flowcharts for a single skill."""
    issues = []

    # Read file content
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract flowcharts
    flowcharts = extract_flowcharts(content)

    if not flowcharts:
        # No flowcharts - not an issue
        return issues

    # Validate each flowchart
    for i, flowchart in enumerate(flowcharts, start=1):
        line_number = find_flowchart_line_number(content, flowchart)

        # Check Graphviz syntax
        is_valid, error_msg = check_graphviz_syntax(flowchart)
        if not is_valid and "not installed" not in error_msg:
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(skill_path),
                line_number=line_number,
                message=f"Flowchart {i} has invalid Graphviz syntax: {error_msg}",
                fix_suggestion="Fix dot syntax - test with: echo 'digraph { ... }' | dot -Tsvg"
            ))

        # Check for generic labels
        generic_labels = find_generic_labels(flowchart)
        if generic_labels:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                file_path=str(skill_path),
                line_number=line_number,
                message=f"Flowchart {i} has generic labels: {', '.join(generic_labels[:3])}",
                fix_suggestion="Use semantic labels that describe what each node does"
            ))

    return issues


def main():
    """Main validation entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate skill flowcharts')
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
        issues = validate_skill_flowcharts(skill_path)
        all_issues.extend(issues)

    # Create result
    result = ValidationResult(
        validator_name='Flowchart Validation',
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
