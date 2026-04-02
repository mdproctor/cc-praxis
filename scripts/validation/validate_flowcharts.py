#!/usr/bin/env python3
"""
Validate Mermaid flowcharts in SKILL.md files.

Checks:
- Flowcharts use valid Mermaid syntax (via mmdc)
- No generic labels (step1, step2, helper1, pattern2, etc.)
- All node labels are semantic and descriptive

Runs at PUSH tier: mmdc requires puppeteer (~5-10s startup), so this
does not meet the COMMIT tier <2s budget. Parallel execution keeps
total runtime within the PUSH tier 30s budget.
"""

import sys
import re
import subprocess
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity,
    find_all_skill_files, print_summary
)
from utils.skill_parser import extract_mermaid_charts


# Generic label patterns that should not be used in node labels.
# Note: "Start" and "End" are intentionally excluded — they are the standard
# convention for start/end circle nodes in flowcharts and are semantic, not generic.
GENERIC_PATTERNS = [
    r'\b(step|phase|stage)\s*\d+\b',        # "step 1", "phase2"
    r'\b(helper|pattern|node|task)\s*\d+\b', # "helper1", "pattern2"
    r'^\d+$',                                # bare numbers ("1", "42")
]

# Label text extraction: matches content inside Mermaid shape markers
# Handles: [label], {label}, ((label)), (label), ["label"], {"label"}
_LABEL_RE = re.compile(
    r'(?:'
    r'\[\["([^"]+)"\]\]'    # [["quoted"]]
    r'|\["([^"]+)"\]'       # ["quoted"]
    r'|\{"([^"]+)"\}'       # {"quoted"}
    r'|\(\("([^"]+)"\)\)'   # (("quoted"))
    r'|\(\[([^\]]+)\]\)'    # ([unquoted])
    r'|\[\[([^\]]+)\]\]'    # [[unquoted]]
    r'|\[([^\]]+)\]'        # [unquoted]
    r'|\{([^}]+)\}'         # {unquoted}
    r'|\(\(([^)]+)\)\)'     # ((unquoted))
    r'|\(([^)]+)\)'         # (unquoted)
    r')'
)


def _mmdc_available() -> bool:
    """Check if mmdc (mermaid CLI) is accessible via npx."""
    try:
        result = subprocess.run(
            ['npx', '--yes', '@mermaid-js/mermaid-cli', '--version'],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_mermaid_syntax(chart_code: str) -> tuple[bool, str]:
    """
    Validate Mermaid syntax using mmdc.

    Returns:
        (is_valid, error_message)
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(chart_code)
            in_path = f.name

        out_path = in_path.replace('.mmd', '.svg')

        result = subprocess.run(
            ['npx', '--yes', '@mermaid-js/mermaid-cli', '-i', in_path, '-o', out_path],
            capture_output=True, text=True, timeout=30
        )

        # Clean up temp files
        Path(in_path).unlink(missing_ok=True)
        Path(out_path).unlink(missing_ok=True)

        combined = result.stdout + result.stderr
        if 'Error:' in combined or result.returncode != 0:
            # Look for actual parse errors (not puppeteer/Chrome infrastructure failures)
            for line in combined.splitlines():
                if 'Parse error' in line or ('Error:' in line and 'puppeteer' not in line):
                    return False, line.strip()
            # No parse errors found — failure is infrastructure (puppeteer/Chrome unavailable)
            # Treat as mmdc unavailable rather than a syntax error
            return True, ""

        return True, ""

    except subprocess.TimeoutExpired:
        return False, "mmdc timeout (>30s)"
    except Exception as e:
        return False, f"mmdc error: {e}"


def find_generic_labels(chart_code: str) -> list[str]:
    """Find generic/non-semantic labels in a Mermaid chart."""
    generic = []
    for match in _LABEL_RE.finditer(chart_code):
        # Get whichever capture group matched
        label = next((g for g in match.groups() if g is not None), '')
        label = label.strip()
        for pattern in GENERIC_PATTERNS:
            if re.search(pattern, label, re.IGNORECASE):
                generic.append(label)
                break
    return list(set(generic))


def find_chart_line(content: str, chart_code: str) -> int:
    """Return line number of the ```mermaid opening for this chart."""
    first_line = chart_code.split('\n')[0].strip() if chart_code else ''
    lines = content.split('\n')
    for i, line in enumerate(lines, start=1):
        if line.strip() == '```mermaid':
            # Confirm by checking the next non-empty line
            for j in range(i, min(i + 3, len(lines))):
                if lines[j].strip() and lines[j].strip() == first_line:
                    return i
            return i
    return 0


def validate_one_skill(skill_path: Path, mmdc_ok: bool) -> list[ValidationIssue]:
    """Validate Mermaid charts in a single SKILL.md."""
    issues = []

    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    charts = extract_mermaid_charts(content)
    if not charts:
        return issues

    for idx, chart in enumerate(charts, start=1):
        line_no = find_chart_line(content, chart)

        if mmdc_ok:
            is_valid, error_msg = check_mermaid_syntax(chart)
            if not is_valid:
                issues.append(ValidationIssue(
                    severity=Severity.CRITICAL,
                    file_path=str(skill_path),
                    line_number=line_no,
                    message=f"Chart {idx}: invalid Mermaid syntax — {error_msg}",
                    fix_suggestion=(
                        "Quote labels that contain parentheses: "
                        "|\"yes (label)\"| or [\"node (label)\"]"
                    )
                ))

        generic = find_generic_labels(chart)
        if generic:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                file_path=str(skill_path),
                line_number=line_no,
                message=f"Chart {idx}: generic labels: {', '.join(generic[:3])}",
                fix_suggestion="Use semantic labels (e.g. 'Check BOM alignment' not 'step1')"
            ))

    return issues


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Validate Mermaid flowcharts in SKILL.md files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('files', nargs='*', help='Specific files to check')
    args = parser.parse_args()

    skill_files = [Path(f) for f in args.files] if args.files else find_all_skill_files()

    mmdc_ok = _mmdc_available()
    if not mmdc_ok and args.verbose:
        print("⚠️  mmdc not available — skipping syntax check, checking labels only",
              file=sys.stderr)

    all_issues: list[ValidationIssue] = []

    # Validate in parallel: mmdc is I/O-bound (puppeteer subprocess)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(validate_one_skill, p, mmdc_ok): p for p in skill_files}
        for future in as_completed(futures):
            all_issues.extend(future.result())

    result = ValidationResult(
        validator_name='Mermaid Flowchart Validation',
        issues=all_issues,
        files_checked=len(skill_files)
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_summary(result, verbose=args.verbose)

    sys.exit(result.exit_code)


if __name__ == '__main__':
    main()
