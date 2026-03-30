#!/usr/bin/env python3
"""
Regression test runner.
Verifies known issues don't recur by running regression tests.

TIER: PRE-PUSH (regression prevention, <30s budget)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

def load_regression_test(test_file: Path) -> Dict[str, Any]:
    """Load regression test from JSON."""
    try:
        with open(test_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {test_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading {test_file}: {e}")
        sys.exit(1)

def run_validator(validator: str, target: str) -> tuple[int, str]:
    """Run a validator and return exit code and output."""
    validator_path = Path(f"scripts/validation/{validator}")
    if not validator_path.exists():
        return -1, f"Validator not found: {validator_path}"

    try:
        result = subprocess.run(
            ["python3", str(validator_path), target],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return -1, "Timeout exceeded"
    except Exception as e:
        return -1, str(e)

def execute_regression_test(test: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single regression test."""
    issue_id = test['issue_id']
    title = test['title']
    validation = test.get('validation', {})

    result = {
        'issue_id': issue_id,
        'title': title,
        'passed': False,
        'details': ''
    }

    val_type = validation.get('type')

    if val_type == 'cso_check':
        # Run CSO validator
        exit_code, output = run_validator('validate_cso.py', '.')

        # Check for forbidden patterns
        forbidden = validation.get('description_must_not_contain', [])
        found_violations = []

        for pattern in forbidden:
            if pattern.lower() in output.lower():
                found_violations.append(pattern)

        if found_violations:
            result['passed'] = False
            result['details'] = f"Found forbidden patterns: {', '.join(found_violations)}"
        else:
            result['passed'] = True
            result['details'] = "No CSO violations found"
    elif val_type is None:
        result['passed'] = False
        result['details'] = "No validation type specified in test"
    else:
        result['passed'] = False
        result['details'] = f"Unknown validation type: {val_type}"

    return result

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Run regression tests')
    parser.add_argument('--issue', help='Specific issue to test (e.g., 001)')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()

    # Find regression tests
    regression_dir = Path('tests/regression')
    if not regression_dir.exists():
        if args.json:
            print(json.dumps({'error': 'Regression test directory not found'}))
        else:
            print("❌ Regression test directory not found: tests/regression")
        sys.exit(1)

    if args.issue:
        test_files = list(regression_dir.glob(f'issue-{args.issue}-*.json'))
    else:
        test_files = list(regression_dir.glob('issue-*.json'))

    if not test_files:
        print("No regression tests found")
        sys.exit(1)

    results = []
    for test_file in sorted(test_files):
        test = load_regression_test(test_file)
        result = execute_regression_test(test)
        results.append(result)

    # Output results
    if args.json:
        output = {
            'total': len(results),
            'passed': sum(1 for r in results if r['passed']),
            'results': results
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Regression Tests: {sum(1 for r in results if r['passed'])}/{len(results)} passed")
        print(f"{'='*60}\n")

        for result in results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"{status} - Issue #{result['issue_id']}: {result['title']}")
            print(f"  {result['details']}")

    # Exit with error if any failed
    if not all(r['passed'] for r in results):
        sys.exit(1)

if __name__ == "__main__":
    main()
