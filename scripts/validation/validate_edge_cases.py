#!/usr/bin/env python3
"""
TIER: PRE-PUSH (30s budget)

Edge case coverage validator - checks error handling completeness.
"""
import sys
from pathlib import Path
from typing import List, Dict
import re

def check_file_existence_before_read(content: str, file_path: Path) -> List[Dict]:
    """Check if file operations verify existence first."""
    issues = []

    # Patterns that read files
    read_patterns = [
        r'cat\s+[\w/.-]+',
        r'Read\s+tool.*file',
        r'read_text\(\)',
        r'open\([\'"].*[\'"]',
    ]

    lines = content.split('\n')
    in_code_block = False

    for line_num, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue

        # Only check within code blocks and instructions
        if not in_code_block and not line.strip().startswith(('-', '*', '1.', '2.', '3.')):
            continue

        for pattern in read_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Look back a few lines for existence check
                check_found = False
                for lookback in range(max(0, line_num - 5), line_num):
                    if lookback < len(lines):
                        prev_line = lines[lookback]
                        # Check for file existence patterns
                        if re.search(r'(ls|test -[ef]|exists\(\)|\.exists\(\)|if.*file)', prev_line, re.IGNORECASE):
                            check_found = True
                            break

                if not check_found:
                    issues.append({
                        'severity': 'WARNING',
                        'type': 'missing_file_check',
                        'file': str(file_path),
                        'line': line_num,
                        'message': f"{file_path}:{line_num}: File operation without existence check"
                    })

    return issues

def check_command_error_handling(content: str, file_path: Path) -> List[Dict]:
    """Check if bash commands have error handling."""
    issues = []

    # Patterns indicating command execution
    command_patterns = [
        r'```bash\s*\n',
        r'subprocess\.',
        r'\$\(',
    ]

    lines = content.split('\n')
    in_bash_block = False
    bash_block_start = 0

    for line_num, line in enumerate(lines, 1):
        # Track bash code blocks
        if re.match(r'```bash', line):
            in_bash_block = True
            bash_block_start = line_num
        elif line.strip() == '```' and in_bash_block:
            # End of bash block - check if any error handling present
            block_content = '\n'.join(lines[bash_block_start:line_num])

            # Look for error handling patterns
            has_error_handling = any([
                'if [ $? -' in block_content,
                '|| echo' in block_content,
                '2>/dev/null' in block_content,
                'set -e' in block_content,
                'trap' in block_content,
            ])

            # Check if block has risky commands (grep, find, git, etc.)
            has_risky_commands = any([
                re.search(r'\b(grep|find|git|curl|wget|rm|mv)\b', block_content),
            ])

            if has_risky_commands and not has_error_handling:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'missing_error_handling',
                    'file': str(file_path),
                    'line': bash_block_start,
                    'message': f"{file_path}:{bash_block_start}: Bash block with risky commands lacks error handling"
                })

            in_bash_block = False

    return issues

def check_empty_input_handling(content: str, file_path: Path) -> List[Dict]:
    """Check for empty/null input validation."""
    issues = []

    # Patterns indicating variable usage without validation
    usage_patterns = [
        r'if\s+\$\w+\s+==',  # Bash variable comparison without quotes
        r'for\s+\w+\s+in\s+\$',  # Iteration over unquoted variable
    ]

    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern in usage_patterns:
            if re.search(pattern, line):
                issues.append({
                    'severity': 'NOTE',
                    'type': 'potential_empty_input',
                    'file': str(file_path),
                    'line': line_num,
                    'message': f"{file_path}:{line_num}: Variable usage may fail on empty input"
                })

    return issues

def check_conditional_completeness(content: str, file_path: Path) -> List[Dict]:
    """Check if if-elif chains have else clauses."""
    issues = []

    lines = content.split('\n')
    in_conditional = False
    conditional_start = 0
    has_elif = False
    has_else = False

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Start of conditional
        if stripped.startswith(('If ', '**If ', '- If ', '* If ')):
            in_conditional = True
            conditional_start = line_num
            has_elif = False
            has_else = False

        # Track elif/else
        elif in_conditional:
            if stripped.startswith(('Else if ', '**Else if ', 'elif ', 'Otherwise if ')):
                has_elif = True
            elif stripped.startswith(('Else ', '**Else ', 'else:', 'Otherwise ')):
                has_else = True
                in_conditional = False
            elif not stripped or stripped.startswith(('#', '---', '##')):
                # End of conditional block
                if in_conditional and has_elif and not has_else:
                    issues.append({
                        'severity': 'WARNING',
                        'type': 'incomplete_conditional',
                        'file': str(file_path),
                        'line': conditional_start,
                        'message': f"{file_path}:{conditional_start}: If-elif chain without else clause (unhandled cases)"
                    })
                in_conditional = False

    return issues

def check_success_without_verification(content: str, file_path: Path) -> List[Dict]:
    """Check for success claims without verification commands."""
    issues = []

    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()

        # Look for success/completion claims
        if any(word in line_lower for word in ['success', 'complete', 'done', 'finished']):
            # Check if followed by verification within next 3 lines
            has_verification = False
            for lookahead in range(line_num, min(line_num + 3, len(lines))):
                if lookahead < len(lines):
                    next_line = lines[lookahead]
                    # Check for verification patterns
                    if re.search(r'(git log|git status|test|verify|check|confirm)', next_line, re.IGNORECASE):
                        has_verification = True
                        break

            # Only flag in Success Criteria or workflow sections
            if not has_verification and ('success' in line_lower or 'criteria' in line_lower):
                issues.append({
                    'severity': 'NOTE',
                    'type': 'unverified_success',
                    'file': str(file_path),
                    'line': line_num,
                    'message': f"{file_path}:{line_num}: Success claim without verification command"
                })

    return issues

def validate_file(file_path: Path) -> List[Dict]:
    """Validate a single file for edge case handling."""
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
    issues.extend(check_file_existence_before_read(content, file_path))
    issues.extend(check_command_error_handling(content, file_path))
    issues.extend(check_empty_input_handling(content, file_path))
    issues.extend(check_conditional_completeness(content, file_path))
    issues.extend(check_success_without_verification(content, file_path))

    return issues

def main():
    """Main entry point."""
    base_dir = Path('.')

    # Find all SKILL.md files
    skill_files = list(base_dir.glob('*/SKILL.md'))

    all_issues = []

    print("Edge Case Coverage Check", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Checking {len(skill_files)} skills for edge case handling...", file=sys.stderr)

    for file_path in skill_files:
        all_issues.extend(validate_file(file_path))

    # Categorize issues
    critical = [i for i in all_issues if i['severity'] == 'CRITICAL']
    warnings = [i for i in all_issues if i['severity'] == 'WARNING']
    notes = [i for i in all_issues if i['severity'] == 'NOTE']

    if not all_issues:
        print("✅ Good edge case coverage", file=sys.stderr)
        sys.exit(0)

    if critical:
        print(f"\n❌ CRITICAL: {len(critical)}", file=sys.stderr)
        for issue in critical:
            print(f"  - {issue['message']}", file=sys.stderr)

    if warnings:
        print(f"\n⚠️  WARNING: {len(warnings)}", file=sys.stderr)
        # Show first 10 warnings
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
