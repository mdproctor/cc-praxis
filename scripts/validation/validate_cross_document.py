#!/usr/bin/env python3
"""
Cross-document consistency validator.
Checks consistency across README, CLAUDE, skills, ADRs.

TIER: PRE-PUSH (30s budget)
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Set
import json

def get_skill_names_from_filesystem() -> Set[str]:
    """Get all skill names from */SKILL.md files."""
    skills = set()
    for skill_path in Path('.').glob('*/SKILL.md'):
        skills.add(skill_path.parent.name)
    return skills

def get_skill_names_from_readme() -> Set[str]:
    """Parse skill names from README § Skills section."""
    readme = Path('README.md')
    if not readme.exists():
        return set()

    content = readme.read_text()
    skills = set()

    # Pattern: #### **skill-name**
    for match in re.finditer(r'####\s+\*\*([a-z][a-z0-9-]+)\*\*', content):
        skills.add(match.group(1))

    return skills

def get_chaining_claims_from_skills() -> Dict[str, List[str]]:
    """Parse chaining claims from all SKILL.md files."""
    chaining = {}

    for skill_path in Path('.').glob('*/SKILL.md'):
        skill_name = skill_path.parent.name
        content = skill_path.read_text()

        # Find "Chains to X" or "Invokes X" patterns
        chains_to = []

        # Pattern: `skill-name` in backticks
        for match in re.finditer(r'`([a-z][a-z0-9-]+)`', content):
            referenced_skill = match.group(1)
            if referenced_skill != skill_name:  # Not self-reference
                chains_to.append(referenced_skill)

        if chains_to:
            chaining[skill_name] = list(set(chains_to))  # Remove duplicates

    return chaining

def validate_skill_existence() -> List[Dict]:
    """Validate skills referenced exist."""
    issues = []

    actual_skills = get_skill_names_from_filesystem()
    chaining = get_chaining_claims_from_skills()

    for skill, referenced in chaining.items():
        for ref in referenced:
            if ref not in actual_skills:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'nonexistent_skill_reference',
                    'skill': skill,
                    'reference': ref,
                    'message': f"{skill} references non-existent skill: {ref}"
                })

    return issues

def validate_readme_consistency() -> List[Dict]:
    """Validate README lists all skills."""
    issues = []

    actual_skills = get_skill_names_from_filesystem()
    readme_skills = get_skill_names_from_readme()

    # Missing from README
    missing = actual_skills - readme_skills
    if missing:
        issues.append({
            'severity': 'WARNING',
            'type': 'missing_from_readme',
            'skills': sorted(missing),
            'message': f"Skills exist but not in README: {', '.join(sorted(missing))}"
        })

    # Extra in README (deleted skills)
    extra = readme_skills - actual_skills
    if extra:
        issues.append({
            'severity': 'CRITICAL',
            'type': 'stale_in_readme',
            'skills': sorted(extra),
            'message': f"README documents non-existent skills: {', '.join(sorted(extra))}"
        })

    return issues

def main():
    """Main entry point."""
    all_issues = []

    print("Cross-Document Consistency Check", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Run validations
    all_issues.extend(validate_skill_existence())
    all_issues.extend(validate_readme_consistency())

    # Print results
    critical = [i for i in all_issues if i['severity'] == 'CRITICAL']
    warnings = [i for i in all_issues if i['severity'] == 'WARNING']

    if not all_issues:
        print("✅ No cross-document consistency issues", file=sys.stderr)
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
