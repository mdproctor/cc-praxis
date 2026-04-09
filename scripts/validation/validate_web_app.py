#!/usr/bin/env python3
"""
TIER: PUSH (<30s budget)

Validate that docs/index.html is in sync with SKILL.md files.

Checks:
1. Every known skill has an overview card (id="ov-{name}") in index.html
2. The CHAIN JS object matches the chaining extracted from SKILL.md
3. Overview card meta sections match SKILL.md chaining

Run the generator to fix drift:
    python3 scripts/generate_web_app_data.py

Exit codes:
    0 — all in sync
    1 — CRITICAL drift detected (blocks push)
    2 — WARNING (minor inconsistencies)
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.common import (
    ValidationIssue, ValidationResult, Severity,
    find_all_skill_files, get_skill_name_from_path,
    find_skills_root, print_summary
)
from utils.skill_parser import extract_sections, extract_chaining_info

ALL_SKILLS = {
    'git-commit', 'update-claude-md', 'adr', 'project-health', 'project-refine',
    'code-review-principles', 'security-audit-principles',
    'dependency-management-principles', 'observability-principles',
    'ts-dev', 'ts-code-review', 'ts-security-audit', 'npm-dependency-update',
    'ts-project-health', 'java-dev', 'java-code-review', 'java-security-audit',
    'java-git-commit', 'java-update-design', 'maven-dependency-update',
    'quarkus-flow-dev', 'quarkus-flow-testing', 'quarkus-observability',
    'java-project-health', 'issue-workflow', 'blog-git-commit', 'custom-git-commit',
    'update-primary-doc', 'skills-project-health', 'blog-project-health',
    'custom-project-health', 'install-skills', 'uninstall-skills',
    'python-dev', 'python-code-review', 'python-security-audit',
    'pip-dependency-update', 'python-project-health', 'design-snapshot',
    'idea-log', 'write-blog', 'cc-praxis-ui', 'garden', 'handover',
    'workspace-init', 'retro-issues',
}

KNOWN_NON_SKILL_TERMS = {
    'docs-sync', 'user-journey', 'primary-doc', 'cross-refs',
    'java-dependencies', 'java-architecture', 'java-code-quality',
    'ts-types', 'ts-async', 'ts-build', 'ts-dependencies', 'ts-testing',
    'python-types', 'python-deps', 'python-quality', 'python-testing', 'python-build',
    'python-observability', 'go-dependency-update', 'go-observability', 'npm-dependency-update',
}


def extract_skillmd_chains(skill_path: Path) -> dict:
    """Extract chaining from SKILL.md (chains_to and invoked_by only)."""
    try:
        content = skill_path.read_text(encoding='utf-8')
    except Exception:
        return {'chains_to': [], 'invoked_by': []}

    sections = extract_sections(content)
    base = extract_chaining_info(sections)

    def filter_skills(names):
        return sorted(set(
            n for n in names
            if n in ALL_SKILLS and n not in KNOWN_NON_SKILL_TERMS
        ))

    return {
        'chains_to':  filter_skills(base.get('chains_to', [])),
        'invoked_by': filter_skills(base.get('invoked_by', [])),
    }


def extract_chain_js(html: str) -> dict:
    """Parse the const CHAIN object from index.html."""
    m = re.search(r'const CHAIN = \{([\s\S]*?)\};', html)
    if not m:
        return {}

    chain = {}
    block = m.group(1)
    for entry in re.finditer(
        r"'([^']+)':\s*\{parents:\[([^\]]*)\],children:\[([^\]]*)\]\}",
        block
    ):
        name     = entry.group(1)
        parents  = [s.strip("' ") for s in entry.group(2).split(',') if s.strip("' ")]
        children = [s.strip("' ") for s in entry.group(3).split(',') if s.strip("' ")]
        chain[name] = {'parents': parents, 'children': children}

    return chain


def main() -> None:
    import argparse, json

    parser = argparse.ArgumentParser(description='Validate web app is in sync with SKILL.md')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    root     = find_skills_root()
    html_path = root / 'docs' / 'index.html'

    issues = []

    if not html_path.exists():
        issues.append(ValidationIssue(
            severity=Severity.CRITICAL,
            file_path=str(html_path),
            line_number=None,
            message='docs/index.html not found',
            fix_suggestion='Run scripts/generate_web_app_data.py'
        ))
        result = ValidationResult('Web App Sync', issues, 0)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print_summary(result, verbose=args.verbose)
        sys.exit(result.exit_code)

    html = html_path.read_text(encoding='utf-8')
    chain_js = extract_chain_js(html)

    skill_files = find_all_skill_files()
    files_checked = 0

    for skill_path in skill_files:
        name = get_skill_name_from_path(skill_path)
        if name not in ALL_SKILLS:
            continue
        files_checked += 1

        # 1. Check overview card exists
        if f'id="ov-{name}"' not in html:
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(html_path),
                line_number=None,
                message=f"Missing overview card for '{name}' (id=\"ov-{name}\" not found)",
                fix_suggestion='Run: python3 scripts/generate_web_app_data.py'
            ))
            continue

        # 2. Check CHAIN JS entry exists
        if name not in chain_js:
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(html_path),
                line_number=None,
                message=f"'{name}' missing from const CHAIN in index.html",
                fix_suggestion='Run: python3 scripts/generate_web_app_data.py'
            ))
            continue

        # 3. Check chains_to / children match
        md = extract_skillmd_chains(skill_path)
        js = chain_js[name]

        md_children = set(md['chains_to'])
        js_children = set(js['children'])

        missing = md_children - js_children
        extra   = js_children - md_children - KNOWN_NON_SKILL_TERMS

        if missing:
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(html_path),
                line_number=None,
                message=f"'{name}' CHAIN.children missing {sorted(missing)} (SKILL.md has these in chains_to)",
                fix_suggestion='Run: python3 scripts/generate_web_app_data.py'
            ))
        if extra:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                file_path=str(html_path),
                line_number=None,
                message=f"'{name}' CHAIN.children has extra {sorted(extra)} not in SKILL.md chains_to",
                fix_suggestion='Run: python3 scripts/generate_web_app_data.py'
            ))

        # 4. Check invoked_by / parents match
        md_parents = set(md['invoked_by'])
        js_parents = set(js['parents'])

        missing_p = md_parents - js_parents
        extra_p   = js_parents - md_parents - KNOWN_NON_SKILL_TERMS

        if missing_p:
            issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                file_path=str(html_path),
                line_number=None,
                message=f"'{name}' CHAIN.parents missing {sorted(missing_p)} (SKILL.md has these in invoked_by)",
                fix_suggestion='Run: python3 scripts/generate_web_app_data.py'
            ))
        if extra_p:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                file_path=str(html_path),
                line_number=None,
                message=f"'{name}' CHAIN.parents has extra {sorted(extra_p)} not in SKILL.md invoked_by",
                fix_suggestion='Run: python3 scripts/generate_web_app_data.py'
            ))

    result = ValidationResult('Web App Sync', issues, files_checked)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_summary(result, verbose=args.verbose)

    sys.exit(result.exit_code)


if __name__ == '__main__':
    main()
