#!/usr/bin/env python3
"""
README/CLAUDE.md sync validator.
Checks documentation is in sync with actual repository state.

TIER: PRE-PUSH (documentation sync validation, <30s budget)
"""

import re
import sys
from pathlib import Path
from typing import List, Set, Dict

def get_skills_from_filesystem() -> Set[str]:
    """Get actual skills from filesystem."""
    skills = set()
    for skill_dir in Path('.').glob('*/SKILL.md'):
        skills.add(skill_dir.parent.name)
    return skills

def get_skills_from_readme() -> Set[str]:
    """Parse skills from README.md and docs/skills-catalog.md.

    After the README extraction, skill descriptions live in docs/skills-catalog.md.
    Check both files so validation works whether skills are in README or the catalog.
    Pattern: #### **skill-name**
    """
    skills = set()
    pattern = re.compile(r'####\s+\*\*([a-z][a-z0-9-]+)\*\*')

    for path in [Path('README.md'), Path('docs/skills-catalog.md')]:
        if not path.exists():
            continue
        for match in pattern.finditer(path.read_text()):
            skills.add(match.group(1))

    return skills

def get_chaining_from_readme() -> Dict[str, List[str]]:
    """Parse chaining relationships from README table."""
    readme = Path('README.md')
    if not readme.exists():
        return {}

    content = readme.read_text()
    chaining = {}

    # Find Skill Chaining Reference table
    # Pattern: | `skill-a` | `skill-b` | When |
    for match in re.finditer(r'\|\s*`([a-z][a-z0-9-]+)`\s*\|\s*`([a-z][a-z0-9-]+)`\s*\|', content):
        from_skill = match.group(1)
        to_skill = match.group(2)

        if from_skill not in chaining:
            chaining[from_skill] = []
        chaining[from_skill].append(to_skill)

    return chaining

def get_adrs_from_filesystem() -> Set[str]:
    """Get ADR files from filesystem."""
    adr_dir = Path('docs/adr')
    if not adr_dir.exists():
        return set()

    adrs = set()
    for adr_file in adr_dir.glob('*.md'):
        adrs.add(adr_file.name)
    return adrs

def get_adr_references_from_claude() -> Set[str]:
    """Parse ADR references from CLAUDE.md."""
    claude_md = Path('CLAUDE.md')
    if not claude_md.exists():
        return set()

    content = claude_md.read_text()
    adrs = set()

    # Pattern: ADR-XXXX or 0001-some-name.md
    for match in re.finditer(r'(ADR-\d{4}|\d{4}-[a-z-]+\.md)', content):
        ref = match.group(1)
        # Normalize to filename format
        if ref.startswith('ADR-'):
            # This is old format, skip for now
            continue
        adrs.add(ref)

    return adrs

def validate_readme_skills():
    """Validate skills in README match filesystem."""
    actual_skills = get_skills_from_filesystem()
    readme_skills = get_skills_from_readme()

    issues = []

    # Check for missing skills in README
    missing_from_readme = actual_skills - readme_skills
    if missing_from_readme:
        issues.append({
            'severity': 'WARNING',
            'type': 'missing_in_readme',
            'skills': sorted(missing_from_readme),
            'message': f"Skills exist but not documented in README: {', '.join(sorted(missing_from_readme))}"
        })

    # Check for skills in README that don't exist
    extra_in_readme = readme_skills - actual_skills
    if extra_in_readme:
        issues.append({
            'severity': 'CRITICAL',
            'type': 'nonexistent_in_readme',
            'skills': sorted(extra_in_readme),
            'message': f"Skills documented but don't exist: {', '.join(sorted(extra_in_readme))}"
        })

    return issues

def validate_chaining():
    """Validate chaining table references actual skills."""
    actual_skills = get_skills_from_filesystem()
    chaining = get_chaining_from_readme()

    issues = []

    for from_skill, to_skills in chaining.items():
        # Check from_skill exists
        if from_skill not in actual_skills:
            issues.append({
                'severity': 'WARNING',
                'type': 'invalid_chaining_source',
                'message': f"Chaining source '{from_skill}' doesn't exist"
            })

        # Check to_skills exist
        for to_skill in to_skills:
            if to_skill not in actual_skills:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'invalid_chaining_target',
                    'message': f"Chaining target '{to_skill}' doesn't exist (referenced by {from_skill})"
                })

    return issues

def validate_adrs():
    """Validate ADR references in CLAUDE.md."""
    actual_adrs = get_adrs_from_filesystem()
    referenced_adrs = get_adr_references_from_claude()

    issues = []

    # Check for referenced ADRs that don't exist
    missing_adrs = referenced_adrs - actual_adrs
    if missing_adrs:
        issues.append({
            'severity': 'WARNING',
            'type': 'missing_adrs',
            'message': f"ADRs referenced but don't exist: {', '.join(sorted(missing_adrs))}"
        })

    return issues

def print_results(all_issues: List[Dict]):
    """Print validation results."""
    critical = [i for i in all_issues if i['severity'] == 'CRITICAL']
    warnings = [i for i in all_issues if i['severity'] == 'WARNING']

    print("README/CLAUDE.md Sync Check")
    print("=" * 60)

    if not all_issues:
        print("✅ All documentation in sync")
        return 0

    if critical:
        print(f"\n❌ CRITICAL Issues: {len(critical)}")
        for issue in critical:
            print(f"  - {issue['message']}")

    if warnings:
        print(f"\n⚠️  WARNING Issues: {len(warnings)}")
        for issue in warnings:
            print(f"  - {issue['message']}")

    print(f"\nTotal issues: {len(all_issues)}")

    # Return exit code: 1 for CRITICAL, 2 for WARNING only, 0 for clean
    if critical:
        return 1
    elif warnings:
        return 2
    return 0

def main():
    """Main entry point."""
    all_issues = []

    # Run all validations
    all_issues.extend(validate_readme_skills())
    all_issues.extend(validate_chaining())
    all_issues.extend(validate_adrs())

    # Print and exit
    exit_code = print_results(all_issues)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
