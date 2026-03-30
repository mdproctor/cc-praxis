#!/usr/bin/env python3
"""
Master validation orchestrator - runs all validation scripts.

Usage:
    python scripts/validate_all.py                  # Run all validations
    python scripts/validate_all.py --verbose        # Detailed output
    python scripts/validate_all.py --json           # JSON output
    python scripts/validate_all.py --fix            # Auto-fix where possible
    python scripts/validate_all.py skill-name/      # Validate specific skill
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict

# Add to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.common import (
    ValidationResult, Severity,
    find_all_skill_files, print_summary
)


# Validation scripts in order of execution
VALIDATORS = [
    {
        'name': 'Frontmatter',
        'script': 'validation/validate_frontmatter.py',
        'critical': True,
        'description': 'YAML structure, required fields, CSO compliance'
    },
    {
        'name': 'CSO Compliance',
        'script': 'validation/validate_cso.py',
        'critical': True,
        'description': 'Description focuses on WHEN not HOW'
    },
    {
        'name': 'Flowcharts',
        'script': 'validation/validate_flowcharts.py',
        'critical': True,
        'description': 'Graphviz syntax, semantic labels'
    },
    {
        'name': 'Cross-References',
        'script': 'validation/validate_references.py',
        'critical': True,
        'description': 'All references resolve, bidirectional links'
    },
    {
        'name': 'Naming Conventions',
        'script': 'validation/validate_naming.py',
        'critical': False,
        'description': 'Skill name patterns'
    },
    {
        'name': 'Required Sections',
        'script': 'validation/validate_sections.py',
        'critical': False,
        'description': 'Skill Chaining, Success Criteria, Common Pitfalls'
    },
    {
        'name': 'File Structure',
        'script': 'validation/validate_structure.py',
        'critical': False,
        'description': 'Referenced files exist, no orphans'
    }
]


def run_validator(validator: Dict, files: List[str], verbose: bool = False) -> Dict:
    """
    Run a single validator script.

    Returns:
        Result dictionary with exit_code, output, issues
    """
    script_path = Path(__file__).parent / validator['script']

    cmd = [sys.executable, str(script_path), '--json']
    if files:
        cmd.extend(files)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Parse JSON output
        if result.stdout:
            output = json.loads(result.stdout)
        else:
            output = {
                'validator_name': validator['name'],
                'files_checked': 0,
                'critical_count': 0,
                'warning_count': 0,
                'note_count': 0,
                'passed': False,
                'issues': []
            }

        return {
            'exit_code': result.returncode,
            'output': output,
            'stderr': result.stderr
        }

    except subprocess.TimeoutExpired:
        return {
            'exit_code': 4,
            'output': None,
            'stderr': f"{validator['name']} timed out"
        }
    except Exception as e:
        return {
            'exit_code': 4,
            'output': None,
            'stderr': f"Error running {validator['name']}: {str(e)}"
        }


def aggregate_results(results: List[Dict]) -> Dict:
    """Aggregate results from all validators."""
    total_files = 0
    total_critical = 0
    total_warning = 0
    total_note = 0
    all_issues = []
    failed_validators = []

    for result in results:
        if result['output']:
            output = result['output']
            total_files = max(total_files, output.get('files_checked', 0))
            total_critical += output.get('critical_count', 0)
            total_warning += output.get('warning_count', 0)
            total_note += output.get('note_count', 0)
            all_issues.extend(output.get('issues', []))

            if not output.get('passed', True):
                failed_validators.append(output.get('validator_name', 'Unknown'))

    return {
        'files_checked': total_files,
        'total_critical': total_critical,
        'total_warning': total_warning,
        'total_note': total_note,
        'passed': total_critical == 0,
        'failed_validators': failed_validators,
        'all_issues': all_issues
    }


def print_report(results: List[Dict], aggregate: Dict, verbose: bool = False):
    """Print validation report."""
    print("\n" + "=" * 70)
    print("SKILL VALIDATION REPORT")
    print("=" * 70)

    print(f"\nFiles checked: {aggregate['files_checked']}")
    print(f"Total issues: {aggregate['total_critical'] + aggregate['total_warning'] + aggregate['total_note']}")
    print(f"  Critical: {aggregate['total_critical']}")
    print(f"  Warning:  {aggregate['total_warning']}")
    print(f"  Note:     {aggregate['total_note']}")

    # Print validator results
    print("\n" + "-" * 70)
    print("VALIDATOR RESULTS")
    print("-" * 70)

    for i, (validator, result) in enumerate(zip(VALIDATORS, results), 1):
        output = result.get('output')
        if output:
            status = "✅ PASS" if output.get('passed') else "❌ FAIL"
            critical = output.get('critical_count', 0)
            warning = output.get('warning_count', 0)
            note = output.get('note_count', 0)

            print(f"\n{i}. {validator['name']}: {status}")
            print(f"   {validator['description']}")
            if critical > 0 or warning > 0 or note > 0:
                print(f"   Issues: {critical} critical, {warning} warning, {note} note")
        else:
            print(f"\n{i}. {validator['name']}: ⚠️  ERROR")
            if result.get('stderr'):
                print(f"   {result['stderr']}")

    # Overall result
    print("\n" + "=" * 70)
    if aggregate['passed']:
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 70)
        return 0
    else:
        print("❌ VALIDATION FAILED")
        print(f"Failed validators: {', '.join(aggregate['failed_validators'])}")
        print("=" * 70)
        return 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Run all skill validations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_all.py                    # Validate all skills
  python scripts/validate_all.py --verbose          # Detailed output
  python scripts/validate_all.py --json             # JSON output
  python scripts/validate_all.py java-dev/          # Validate specific skill
        """
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output only')
    parser.add_argument('--fix', action='store_true', help='Auto-fix where possible (not implemented yet)')
    parser.add_argument('--strict', action='store_true', help='Fail on warnings, not just critical')
    parser.add_argument('files', nargs='*', help='Specific files or directories to validate')
    args = parser.parse_args()

    # Resolve file arguments
    file_args = []
    if args.files:
        for file_arg in args.files:
            path = Path(file_arg)
            if path.is_dir():
                # If directory, find SKILL.md in it
                skill_md = path / 'SKILL.md'
                if skill_md.exists():
                    file_args.append(str(skill_md))
            elif path.exists():
                file_args.append(str(path))

    # Run all validators
    results = []
    for validator in VALIDATORS:
        if not args.json and args.verbose:
            print(f"\nRunning {validator['name']}...")

        result = run_validator(validator, file_args, args.verbose)
        results.append(result)

    # Aggregate results
    aggregate = aggregate_results(results)

    # Output
    if args.json:
        output = {
            'summary': aggregate,
            'validators': [
                {
                    'name': v['name'],
                    'critical': v['critical'],
                    'result': r['output']
                }
                for v, r in zip(VALIDATORS, results)
            ]
        }
        print(json.dumps(output, indent=2))
        sys.exit(0 if aggregate['passed'] else 1)
    else:
        exit_code = print_report(results, aggregate, args.verbose)

        # In strict mode, fail on warnings too
        if args.strict and aggregate['total_warning'] > 0:
            exit_code = 2

        sys.exit(exit_code)


if __name__ == '__main__':
    main()
