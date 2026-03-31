#!/usr/bin/env python3
"""
Master validation orchestrator with tier support.
Runs appropriate validators based on tier (commit, push, ci).
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json

# Validator tier assignments
VALIDATORS = {
    'commit': [
        # Pre-commit tier: <2s budget, fast mechanical checks
        {'script': 'validate_frontmatter.py', 'name': 'Frontmatter', 'target': None},
        {'script': 'validate_cso.py', 'name': 'CSO Compliance', 'target': None},
        {'script': 'validate_references.py', 'name': 'References', 'target': None},
        {'script': 'validate_naming.py', 'name': 'Naming', 'target': None},
        {'script': 'validate_sections.py', 'name': 'Sections', 'target': None},
        {'script': 'validate_structure.py', 'name': 'Structure', 'target': None},
        {'script': 'validate_project_types.py', 'name': 'Project Type Lists', 'target': None},
    ],
    'push': [
        # Pre-push tier: <30s budget, moderate validators + regression
        # Flowcharts: mmdc requires puppeteer (~5-10s/chart), too slow for commit tier
        {'script': 'validate_flowcharts.py', 'name': 'Mermaid Flowcharts', 'target': None},
        {'script': 'validate_cross_document.py', 'name': 'Cross-Document', 'target': None},
        {'script': 'validate_temporal.py', 'name': 'Temporal', 'target': None},
        {'script': 'validate_usability.py', 'name': 'Usability', 'target': None},
        {'script': 'validate_edge_cases.py', 'name': 'Edge Cases', 'target': None},
        {'script': 'validate_behavior.py', 'name': 'Behavior', 'target': None},
        {'script': 'validate_readme_sync.py', 'name': 'README Sync', 'target': None},
    ],
    'ci': [
        # CI tier: <5min budget, expensive tests
        {'script': 'validate_python_quality.py', 'name': 'Python Quality', 'target': 'scripts/'},
    ]
}

def run_validator(validator: Dict[str, str]) -> Dict[str, Any]:
    """Run a single validator and return results."""
    script_path = Path('scripts/validation') / validator['script']

    try:
        # Build command - only add target if not None
        cmd = ['python3', str(script_path)]
        if validator['target'] is not None:
            cmd.append(validator['target'])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            'name': validator['name'],
            'passed': result.returncode == 0,
            'exit_code': result.returncode,
            'output': result.stdout + result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'name': validator['name'],
            'passed': False,
            'exit_code': -1,
            'output': 'Timeout exceeded'
        }
    except Exception as e:
        return {
            'name': validator['name'],
            'passed': False,
            'exit_code': -1,
            'output': str(e)
        }

def run_tier(tier: str, verbose: bool = False) -> List[Dict[str, Any]]:
    """Run all validators for a given tier."""
    validators = []

    # Accumulate validators up to and including this tier
    if tier in ['push', 'ci']:
        validators.extend(VALIDATORS['commit'])
    if tier in ['ci']:
        validators.extend(VALIDATORS['push'])
    validators.extend(VALIDATORS.get(tier, []))

    results = []
    for validator in validators:
        if verbose:
            print(f"Running {validator['name']}...", file=sys.stderr)
        result = run_validator(validator)
        results.append(result)

        if not result['passed'] and verbose:
            print(f"  ❌ FAILED", file=sys.stderr)

    return results

def run_tests(tier: str, verbose: bool = False) -> Dict[str, Any]:
    """Run test execution for a given tier."""
    results = {
        'regression': None,
        'coverage': None,
        'functional': None
    }

    if tier in ['push', 'ci']:
        # Run regression tests (pre-push)
        if verbose:
            print("Running regression tests...", file=sys.stderr)
        try:
            result = subprocess.run(
                ['python3', 'scripts/testing/run_regression_tests.py', '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            results['regression'] = {
                'passed': result.returncode == 0,
                'output': json.loads(result.stdout) if result.stdout else {}
            }
        except Exception as e:
            results['regression'] = {'passed': False, 'error': str(e)}

        # Run test coverage (pre-push)
        if verbose:
            print("Running test coverage...", file=sys.stderr)
        try:
            result = subprocess.run(
                ['python3', 'scripts/testing/test_coverage.py', '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            results['coverage'] = {
                'passed': result.returncode == 0,
                'output': json.loads(result.stdout) if result.stdout else {}
            }
        except Exception as e:
            results['coverage'] = {'passed': False, 'error': str(e)}

    if tier == 'ci':
        # Run functional tests (CI only, expensive)
        if verbose:
            print("Running functional tests...", file=sys.stderr)
        # Will be implemented when functional tests are ready
        results['functional'] = {'passed': True, 'skipped': 'Not yet implemented'}

    return results

def print_results(validation_results: List[Dict[str, Any]], test_results: Dict[str, Any], tier: str):
    """Print validation results."""
    print(f"\n{'='*60}")
    print(f"Validation Results - Tier: {tier.upper()}")
    print(f"{'='*60}\n")

    # Validation results
    passed = sum(1 for r in validation_results if r['passed'])
    total = len(validation_results)
    print(f"Validators: {passed}/{total} passed\n")

    for result in validation_results:
        status = "✅" if result['passed'] else "❌"
        print(f"{status} {result['name']}")
        if not result['passed'] and result['exit_code'] != 0:
            # Show first 3 lines of output
            lines = result['output'].split('\n')[:3]
            for line in lines:
                if line.strip():
                    print(f"    {line}")

    # Test results
    print(f"\nTests:")
    if test_results['regression']:
        status = "✅" if test_results['regression']['passed'] else "❌"
        print(f"{status} Regression Tests")
    if test_results['coverage']:
        status = "✅" if test_results['coverage']['passed'] else "❌"
        print(f"{status} Test Coverage")
    if test_results['functional'] and not test_results['functional'].get('skipped'):
        status = "✅" if test_results['functional']['passed'] else "❌"
        print(f"{status} Functional Tests")

    print()

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Run validation checks with tier support')
    parser.add_argument('--tier', choices=['commit', 'push', 'ci'], default='commit',
                        help='Validation tier (commit: <2s, push: <30s, ci: <5min)')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    # Run validations
    validation_results = run_tier(args.tier, args.verbose)

    # Run tests
    test_results = run_tests(args.tier, args.verbose)

    # Output results
    if args.json:
        output = {
            'tier': args.tier,
            'validation': {
                'total': len(validation_results),
                'passed': sum(1 for r in validation_results if r['passed']),
                'results': validation_results
            },
            'tests': test_results
        }
        print(json.dumps(output, indent=2))
    else:
        print_results(validation_results, test_results, args.tier)

    # Exit with error if anything failed
    all_passed = all(r['passed'] for r in validation_results)
    if test_results['regression']:
        all_passed = all_passed and test_results['regression']['passed']
    if test_results['coverage']:
        all_passed = all_passed and test_results['coverage']['passed']
    if test_results['functional'] and not test_results['functional'].get('skipped'):
        all_passed = all_passed and test_results['functional']['passed']

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
