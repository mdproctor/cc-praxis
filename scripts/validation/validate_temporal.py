#!/usr/bin/env python3
"""
TIER: PRE-PUSH (30s budget)

Temporal consistency validator - detects stale references.
"""
import sys
from pathlib import Path
from typing import List, Dict
import re

# Known renames and deprecations
DEPRECATED_TOOLS = {
    'TodoWrite': 'Deprecated - use task tracking in conversation',
    'TodoRead': 'Deprecated - use task tracking in conversation',
    'NotebookEdit': 'Deprecated - use Edit tool',
}

RENAMED_SKILLS = {
    # Add any known renames: 'old-name': 'new-name'
}

MOVED_FILES = {
    'docs/ARCHITECTURE.md': 'docs/DESIGN.md',
    'ARCHITECTURE.md': 'DESIGN.md',
}

def find_deprecated_tool_usage(content: str, file_path: Path) -> List[Dict]:
    """Find usage of deprecated tools."""
    issues = []

    for tool, replacement in DEPRECATED_TOOLS.items():
        # Check for tool mentions in backticks or prose
        if tool in content:
            # Find line numbers
            for line_num, line in enumerate(content.split('\n'), 1):
                if tool in line:
                    issues.append({
                        'severity': 'WARNING',
                        'type': 'deprecated_tool',
                        'file': str(file_path),
                        'line': line_num,
                        'tool': tool,
                        'replacement': replacement,
                        'message': f"{file_path}:{line_num}: References deprecated tool '{tool}' - {replacement}"
                    })

    return issues

def find_moved_file_references(content: str, file_path: Path) -> List[Dict]:
    """Find references to moved files."""
    issues = []

    for old_path, new_path in MOVED_FILES.items():
        if old_path in content:
            for line_num, line in enumerate(content.split('\n'), 1):
                if old_path in line:
                    issues.append({
                        'severity': 'WARNING',
                        'type': 'moved_file',
                        'file': str(file_path),
                        'line': line_num,
                        'old_path': old_path,
                        'new_path': new_path,
                        'message': f"{file_path}:{line_num}: References moved file '{old_path}' (now at '{new_path}')"
                    })

    return issues

def find_renamed_skill_references(content: str, file_path: Path) -> List[Dict]:
    """Find references to renamed skills."""
    issues = []

    for old_name, new_name in RENAMED_SKILLS.items():
        # Look for skill name in backticks
        pattern = f'`{re.escape(old_name)}`'
        if re.search(pattern, content):
            for line_num, line in enumerate(content.split('\n'), 1):
                if re.search(pattern, line):
                    issues.append({
                        'severity': 'CRITICAL',
                        'type': 'renamed_skill',
                        'file': str(file_path),
                        'line': line_num,
                        'old_name': old_name,
                        'new_name': new_name,
                        'message': f"{file_path}:{line_num}: References renamed skill '{old_name}' (now '{new_name}')"
                    })

    return issues

def validate_file(file_path: Path) -> List[Dict]:
    """Validate a single file for temporal issues."""
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
    issues.extend(find_deprecated_tool_usage(content, file_path))
    issues.extend(find_moved_file_references(content, file_path))
    issues.extend(find_renamed_skill_references(content, file_path))

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

    print("Temporal Consistency Check", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Checking {len(all_files)} files for stale references...", file=sys.stderr)

    for file_path in all_files:
        all_issues.extend(validate_file(file_path))

    # Categorize issues
    critical = [i for i in all_issues if i['severity'] == 'CRITICAL']
    warnings = [i for i in all_issues if i['severity'] == 'WARNING']

    if not all_issues:
        print("✅ No temporal inconsistencies found", file=sys.stderr)
        sys.exit(0)

    if critical:
        print(f"\n❌ CRITICAL: {len(critical)}", file=sys.stderr)
        for issue in critical:
            print(f"  - {issue['message']}", file=sys.stderr)

    if warnings:
        print(f"\n⚠️  WARNING: {len(warnings)}", file=sys.stderr)
        for issue in warnings:
            print(f"  - {issue['message']}", file=sys.stderr)

    # Exit code: 1 for CRITICAL, 2 for WARNING only
    sys.exit(1 if critical else 2)

if __name__ == "__main__":
    main()
