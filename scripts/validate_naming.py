#!/usr/bin/env python3
"""
Validates skill naming conventions.

Exit codes:
  0 - All skills follow naming conventions
  1 - Naming violations found
"""

import os
import re
import sys
from pathlib import Path

# Project-type-specific skills must have these prefixes
NAMING_RULES = {
    'java': {
        'prefix': 'java-',
        'indicators': [
            # File references
            'pom.xml', 'build.gradle', 'DESIGN.md', 'docs/DESIGN.md',
            # Annotations
            '@Entity', '@Service', '@Repository', '@RestController', '@Component',
            # Build tools
            'Maven', 'Gradle',
            # Java concepts
            'package structure', 'Java application', 'Spring', 'Quarkus',
            # Explicit declaration
            'type: java', 'Only for type: java',
        ],
    },
    'custom': {
        'prefix': 'custom-',
        'indicators': [
            # File references
            'VISION.md', 'THESIS.md', 'Primary Document',
            # CLAUDE.md structures
            'Sync Rules', 'Sync Strategy', 'bidirectional-consistency',
            # Custom concepts
            'working groups', 'research progress', 'api-spec-sync',
            # Explicit declaration
            'type: custom', 'Only for type: custom',
        ],
    },
    'skills': {
        'prefix': 'skills-',
        'indicators': [
            # File references
            'SKILL.md files', 'README.md', 'skill collection',
            # Skills concepts
            'skill chaining', 'frontmatter', 'CSO',
            'skill naming', 'SKILL.md validation',
            # Explicit declaration
            'type: skills', 'Only for type: skills', 'skills repositories',
        ],
    },
}

# Universal skills that work in ALL project types (should NOT have prefix)
UNIVERSAL_INDICATORS = [
    'all project types',
    'ALL (skills/java/blog/custom/generic)',
    'universal',
    'works in any project',
]

# Skills that should never have prefixes (generic foundations or implicit type)
EXEMPT_PATTERNS = [
    r'.*-principles$',       # code-review-principles, etc.
    r'^adr$',                # Architecture Decision Records
    r'^skill-creator$',      # Meta skill
    r'^skill-review$',       # Meta skill
    r'^maven-.*',            # Maven implies Java
    r'^quarkus-.*',          # Quarkus implies Java
    r'^gradle-.*',           # Gradle implies Java (if we add these)
    r'^spring-.*',           # Spring implies Java (if we add these)
]

# Skills with correct naming that validator might flag (whitelist)
# Format: skill_name: reason
KNOWN_CORRECT = {
    'java-git-commit': 'Router skill - documents other types but is Java-specific',
    'custom-git-commit': 'Router skill - documents other types but is custom-specific',
    'git-commit': 'Generic router - correctly has no prefix',
    'java-update-design': 'Java-specific - correctly prefixed',
    'skills-update-readme': 'Skills-specific - correctly prefixed',
    'update-primary-doc': 'Generic base - correctly has no prefix',
}


def read_skill_content(skill_path):
    """Read SKILL.md content."""
    skill_file = skill_path / 'SKILL.md'
    if not skill_file.exists():
        return None

    try:
        with open(skill_file, encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Warning: Could not read {skill_file}: {e}")
        return None


def extract_frontmatter(content):
    """Extract YAML frontmatter from content."""
    if not content.startswith('---'):
        return {}

    fm_end = content.find('---', 3)
    if fm_end == -1:
        return {}

    frontmatter = content[3:fm_end]

    # Simple YAML parser for our needs
    data = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()

    return data


def is_universal(content):
    """Check if skill explicitly declares itself as universal."""
    for indicator in UNIVERSAL_INDICATORS:
        if indicator.lower() in content.lower():
            return True
    return False


def is_exempt(skill_name):
    """Check if skill is exempt from naming rules."""
    for pattern in EXEMPT_PATTERNS:
        if re.match(pattern, skill_name):
            return True
    return False


def detect_project_type(content):
    """
    Detect which project type(s) this skill targets.

    Returns:
        list of str: Project types detected ('java', 'custom', 'skills')
    """
    detected_types = []

    for type_name, rules in NAMING_RULES.items():
        for indicator in rules['indicators']:
            if indicator in content:
                detected_types.append(type_name)
                break  # One indicator per type is enough

    return detected_types


def validate_skill_naming(skill_path):
    """
    Validate a single skill's naming convention.

    Returns:
        tuple: (is_valid, violations_list)
    """
    skill_name = skill_path.name
    content = read_skill_content(skill_path)

    if content is None:
        return True, []  # Skip non-skill directories

    # Check if known correct (whitelist)
    if skill_name in KNOWN_CORRECT:
        return True, []

    # Check if exempt
    if is_exempt(skill_name):
        return True, []

    violations = []

    # Check if universal
    if is_universal(content):
        # Universal skills should NOT have project-type prefix
        for type_name, rules in NAMING_RULES.items():
            if skill_name.startswith(rules['prefix']):
                violations.append({
                    'skill': skill_name,
                    'issue': f"Universal skill has {type_name} prefix",
                    'suggestion': f"Remove '{rules['prefix']}' prefix (skill works in all project types)",
                })
        return len(violations) == 0, violations

    # Detect project-type specificity
    detected_types = detect_project_type(content)

    if not detected_types:
        # No project-type detected, should be universal or exempt
        return True, []

    if len(detected_types) > 1:
        # Multi-type skill - this is unusual, flag for review
        violations.append({
            'skill': skill_name,
            'issue': f"Detected multiple project types: {', '.join(detected_types)}",
            'suggestion': "Review skill - should it be universal or project-specific?",
        })
        return False, violations

    # Single project type detected
    detected_type = detected_types[0]
    expected_prefix = NAMING_RULES[detected_type]['prefix']

    if not skill_name.startswith(expected_prefix):
        violations.append({
            'skill': skill_name,
            'issue': f"Detected {detected_type}-specific content but missing prefix",
            'suggestion': f"Rename to '{expected_prefix}{skill_name}'",
            'detected_indicators': [
                ind for ind in NAMING_RULES[detected_type]['indicators']
                if ind in content
            ][:3],  # Show first 3 indicators
        })
        return False, violations

    return True, []


def main():
    """Main validation routine."""
    skills_dir = Path(__file__).parent.parent
    all_violations = []
    checked_count = 0

    # Find all skill directories
    for skill_path in sorted(skills_dir.glob('*/')):
        if skill_path.name.startswith('.'):
            continue
        if skill_path.name in ['scripts', 'docs', '__pycache__']:
            continue

        skill_file = skill_path / 'SKILL.md'
        if not skill_file.exists():
            continue

        checked_count += 1
        is_valid, violations = validate_skill_naming(skill_path)

        if not is_valid:
            all_violations.extend(violations)

    # Report results
    if not all_violations:
        print(f"✅ All {checked_count} skills follow naming conventions")
        return 0

    print(f"❌ Found {len(all_violations)} naming violation(s):\n")

    for i, violation in enumerate(all_violations, 1):
        print(f"{i}. Skill: {violation['skill']}")
        print(f"   Issue: {violation['issue']}")
        print(f"   Suggestion: {violation['suggestion']}")

        if 'detected_indicators' in violation:
            print(f"   Detected indicators: {', '.join(violation['detected_indicators'][:3])}")

        print()

    print(f"See ADR-0002 for naming convention details")
    return 1


if __name__ == '__main__':
    sys.exit(main())
