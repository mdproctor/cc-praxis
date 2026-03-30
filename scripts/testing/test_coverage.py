#!/usr/bin/env python3
"""
Test coverage reporter.
Calculates and reports test coverage metrics.

TIER: PRE-PUSH (coverage tracking, <30s budget)
"""

import json
from pathlib import Path
from typing import Dict, List, Set
import sys

def get_all_skills() -> List[str]:
    """Get list of all skills (directories with SKILL.md)."""
    skills = []
    for skill_dir in Path('.').glob('*/SKILL.md'):
        skills.append(skill_dir.parent.name)
    return sorted(skills)

def get_tested_skills() -> Set[str]:
    """Get set of skills with test cases."""
    tested = set()
    # Check for test cases in <skill>/tests/test_cases.json
    for skill_dir in Path('.').glob('*/SKILL.md'):
        skill_name = skill_dir.parent.name
        test_file = skill_dir.parent / 'tests' / 'test_cases.json'
        if test_file.exists():
            tested.add(skill_name)
    return tested

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize skills by type."""
    categories = {
        'user-invocable': [],
        'foundation': [],
        'update': [],
        'review': [],
        'other': []
    }

    for skill in skills:
        if 'commit' in skill or skill in ['skill-review', 'java-code-review']:
            categories['user-invocable'].append(skill)
        elif '-principles' in skill:
            categories['foundation'].append(skill)
        elif 'update' in skill or 'sync' in skill:
            categories['update'].append(skill)
        elif 'review' in skill:
            categories['review'].append(skill)
        else:
            categories['other'].append(skill)

    return categories

def count_test_scenarios(skill: str) -> int:
    """Count test scenarios for a skill."""
    test_file = Path(skill) / 'tests' / 'test_cases.json'
    if not test_file.exists():
        return 0

    with open(test_file, 'r') as f:
        data = json.load(f)
        return len(data.get('tests', []))

def generate_coverage_report():
    """Generate coverage report."""
    all_skills = get_all_skills()
    tested_skills = get_tested_skills()
    categories = categorize_skills(all_skills)

    total_skills = len(all_skills)
    total_tested = len(tested_skills)
    overall_pct = (total_tested / total_skills * 100) if total_skills > 0 else 0

    print("Test Coverage Report")
    print("=" * 60)
    print(f"Overall: {overall_pct:.0f}% ({total_tested}/{total_skills} skills)\n")

    print("By Category:")
    for category, skills in categories.items():
        if not skills:
            continue
        tested_in_category = len([s for s in skills if s in tested_skills])
        total_in_category = len(skills)
        pct = (tested_in_category / total_in_category * 100) if total_in_category > 0 else 0
        print(f"  {category.replace('-', ' ').title()}: {pct:.0f}% ({tested_in_category}/{total_in_category})")

    # Show gaps
    untested = sorted(set(all_skills) - tested_skills)
    if untested:
        print("\nGaps (no tests):")
        for skill in untested:
            print(f"  - {skill}")

    # Show test scenario counts
    print("\nTest Scenarios:")
    for skill in sorted(tested_skills):
        count = count_test_scenarios(skill)
        print(f"  {skill}: {count} scenarios")

    # Recommendations
    print("\nRecommendations:")
    if categories['user-invocable']:
        untested_ui = [s for s in categories['user-invocable'] if s not in tested_skills]
        if untested_ui:
            print(f"  - Add tests for user-invocable skills: {', '.join(untested_ui)}")

    if categories['foundation']:
        untested_foundation = [s for s in categories['foundation'] if s not in tested_skills]
        if untested_foundation:
            print(f"  - Add tests for foundation skills: {', '.join(untested_foundation)}")

def generate_json_report():
    """Generate JSON coverage report."""
    all_skills = get_all_skills()
    tested_skills = get_tested_skills()

    report = {
        'overall': {
            'total': len(all_skills),
            'tested': len(tested_skills),
            'percentage': (len(tested_skills) / len(all_skills) * 100) if all_skills else 0
        },
        'skills': {}
    }

    for skill in all_skills:
        report['skills'][skill] = {
            'tested': skill in tested_skills,
            'scenarios': count_test_scenarios(skill) if skill in tested_skills else 0
        }

    print(json.dumps(report, indent=2))

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate test coverage report')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()

    if args.json:
        generate_json_report()
    else:
        generate_coverage_report()

if __name__ == "__main__":
    main()
