#!/usr/bin/env python3
"""
TIER: CI (5min budget)

Python quality validator - runs mypy, flake8, bandit on scripts.
"""
import sys
import subprocess
from pathlib import Path
from typing import List, Dict
import shutil

def check_tool_available(tool: str) -> bool:
    """Check if a tool is installed."""
    return shutil.which(tool) is not None

def run_mypy(target_dir: Path) -> Dict:
    """Run mypy type checker."""
    if not check_tool_available('mypy'):
        return {
            'tool': 'mypy',
            'skipped': True,
            'reason': 'mypy not installed'
        }

    try:
        result = subprocess.run(
            ['mypy', '--strict', '--ignore-missing-imports', str(target_dir)],
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            'tool': 'mypy',
            'exit_code': result.returncode,
            'output': result.stdout + result.stderr,
            'passed': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'tool': 'mypy',
            'exit_code': -1,
            'output': 'Timeout exceeded',
            'passed': False
        }
    except Exception as e:
        return {
            'tool': 'mypy',
            'exit_code': -1,
            'output': str(e),
            'passed': False
        }

def run_flake8(target_dir: Path) -> Dict:
    """Run flake8 style checker."""
    if not check_tool_available('flake8'):
        return {
            'tool': 'flake8',
            'skipped': True,
            'reason': 'flake8 not installed'
        }

    try:
        result = subprocess.run(
            [
                'flake8',
                str(target_dir),
                '--max-line-length=120',
                '--ignore=E501,W503',  # Ignore line length, line break before binary operator
                '--exclude=__pycache__,.git,.venv,venv'
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            'tool': 'flake8',
            'exit_code': result.returncode,
            'output': result.stdout + result.stderr,
            'passed': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'tool': 'flake8',
            'exit_code': -1,
            'output': 'Timeout exceeded',
            'passed': False
        }
    except Exception as e:
        return {
            'tool': 'flake8',
            'exit_code': -1,
            'output': str(e),
            'passed': False
        }

def run_bandit(target_dir: Path) -> Dict:
    """Run bandit security scanner."""
    if not check_tool_available('bandit'):
        return {
            'tool': 'bandit',
            'skipped': True,
            'reason': 'bandit not installed'
        }

    try:
        result = subprocess.run(
            [
                'bandit',
                '-r', str(target_dir),
                '-ll',  # Only report medium and high severity
                '--exclude', '__pycache__,.git,.venv,venv'
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Bandit exit codes: 0 = no issues, 1 = issues found
        return {
            'tool': 'bandit',
            'exit_code': result.returncode,
            'output': result.stdout + result.stderr,
            'passed': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'tool': 'bandit',
            'exit_code': -1,
            'output': 'Timeout exceeded',
            'passed': False
        }
    except Exception as e:
        return {
            'tool': 'bandit',
            'exit_code': -1,
            'output': str(e),
            'passed': False
        }

def categorize_severity(results: List[Dict]) -> str:
    """Determine overall severity from tool results."""
    # Security issues (bandit failures) are CRITICAL
    for result in results:
        if result['tool'] == 'bandit' and not result.get('skipped') and not result.get('passed'):
            return 'CRITICAL'

    # Other tool failures are WARNING
    for result in results:
        if not result.get('skipped') and not result.get('passed'):
            return 'WARNING'

    return 'CLEAN'

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Python quality validation')
    parser.add_argument('target', nargs='?', default='scripts/',
                        help='Target directory to validate (default: scripts/)')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    args = parser.parse_args()

    target_dir = Path(args.target)

    if not target_dir.exists():
        print(f"❌ Target directory does not exist: {target_dir}", file=sys.stderr)
        sys.exit(1)

    print("Python Quality Check", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Target: {target_dir}", file=sys.stderr)
    print(file=sys.stderr)

    # Run all tools
    results = []

    print("Running mypy...", file=sys.stderr)
    results.append(run_mypy(target_dir))

    print("Running flake8...", file=sys.stderr)
    results.append(run_flake8(target_dir))

    print("Running bandit...", file=sys.stderr)
    results.append(run_bandit(target_dir))

    # Output results
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("Results:", file=sys.stderr)
        print(file=sys.stderr)

        for result in results:
            tool = result['tool']

            if result.get('skipped'):
                print(f"⏭️  {tool}: SKIPPED ({result['reason']})", file=sys.stderr)
            elif result.get('passed'):
                print(f"✅ {tool}: PASSED", file=sys.stderr)
            else:
                print(f"❌ {tool}: FAILED", file=sys.stderr)

                # Show output (first 10 lines)
                output_lines = result.get('output', '').strip().split('\n')
                if output_lines and output_lines[0]:
                    print(file=sys.stderr)
                    for line in output_lines[:10]:
                        print(f"  {line}", file=sys.stderr)
                    if len(output_lines) > 10:
                        print(f"  ... and {len(output_lines) - 10} more lines", file=sys.stderr)
                print(file=sys.stderr)

    # Determine exit code
    severity = categorize_severity(results)

    if severity == 'CRITICAL':
        print("❌ CRITICAL: Security issues found", file=sys.stderr)
        sys.exit(1)
    elif severity == 'WARNING':
        print("⚠️  WARNING: Code quality issues found", file=sys.stderr)
        sys.exit(2)
    else:
        print("✅ All quality checks passed", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
