#!/usr/bin/env python3
"""
Generate web app data from SKILL.md files.

Reads all SKILL.md Skill Chaining and Prerequisites sections and regenerates:
  1. CHAINING_TRUTH dict in tests/test_mockup_chaining.py
  2. const CHAIN object in docs/index.html
  3. Overview card <div class="overview-meta"> sections in docs/index.html

Run this whenever a skill's chaining relationships change. The validator
(scripts/validation/validate_web_app.py) catches drift if this isn't run.

Usage:
    python3 scripts/generate_web_app_data.py [--dry-run]
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.common import find_all_skill_files, get_skill_name_from_path, find_skills_root
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
    'epic',
}

# Skills that are universal entry points — chains TO them don't require
# bidirectional invoked_by (they're offers/suggestions, not strict invocations).
BIDIRECTIONAL_EXEMPT = {'git-commit'}

# Check categories used inside health skills — not real skill names.
KNOWN_NON_SKILL_TERMS = {
    'docs-sync', 'user-journey', 'primary-doc', 'cross-refs',
    'java-dependencies', 'java-architecture', 'java-code-quality',
    'ts-types', 'ts-async', 'ts-build', 'ts-dependencies', 'ts-testing',
    'python-types', 'python-deps', 'python-quality', 'python-testing', 'python-build',
    'python-observability', 'go-dependency-update', 'go-observability', 'npm-dependency-update',
}


def extract_full_chaining(skill_path: Path) -> dict:
    """Extract complete chaining info from a SKILL.md file."""
    try:
        content = skill_path.read_text(encoding='utf-8')
    except Exception:
        return {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []}

    sections = extract_sections(content)
    base = extract_chaining_info(sections)  # gives chains_to, invoked_by, prerequisites

    # Filter to known skills only
    def filter_skills(names):
        return [n for n in names if n in ALL_SKILLS and n not in KNOWN_NON_SKILL_TERMS]

    chains_to  = filter_skills(base.get('chains_to', []))
    invoked_by = filter_skills(base.get('invoked_by', []))
    builds_on  = filter_skills(base.get('prerequisites', []))

    # Extract "extended_by" from Skill Chaining section
    extended_by = []
    if 'Skill Chaining' in sections:
        for line in sections['Skill Chaining'].split('\n'):
            if 'extended by' in line.lower():
                matches = re.findall(r'`([a-z][a-z0-9-]+)`', line)
                extended_by.extend(m for m in matches if m in ALL_SKILLS)

    # Deduplicate preserving order
    def dedup(lst):
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]

    return {
        'chains_to':  dedup(chains_to),
        'invoked_by': dedup(invoked_by),
        'builds_on':  dedup(builds_on),
        'extended_by': dedup(extended_by),
    }


def extract_trigger(skill_path: Path) -> str:
    """Extract trigger description from SKILL.md Skill Chaining section."""
    try:
        content = skill_path.read_text(encoding='utf-8')
    except Exception:
        return ''

    sections = extract_sections(content)
    if 'Skill Chaining' not in sections:
        return ''

    for line in sections['Skill Chaining'].split('\n'):
        low = line.lower()
        if 'invoked independently' in low or 'can be invoked' in low:
            # Extract the trigger description after the colon
            idx = line.find(':')
            if idx != -1:
                return line[idx+1:].strip()
    return ''


def build_chaining_truth(skill_data: dict) -> dict:
    """
    Build the CHAINING_TRUTH dict with bidirectional inference.

    SKILL.md files don't always document both sides of a relationship.
    This pass infers the other direction so the graph is complete:
    - If B.invoked_by contains A → ensure A.chains_to contains B
    - If A.chains_to contains B  → ensure B.invoked_by contains A
    - If B.builds_on contains A  → ensure A.extended_by contains B
    - If A.extended_by contains B → ensure B.builds_on contains A
    """
    # Start with raw extracted data
    truth = {name: {k: list(v) for k, v in data.items() if k != 'triggers'}
             for name, data in skill_data.items()}

    # Bidirectional inference — run until stable
    changed = True
    while changed:
        changed = False
        for name, data in truth.items():
            # A.chains_to B → B.invoked_by A
            for target in list(data['chains_to']):
                if target in truth and name not in truth[target]['invoked_by']:
                    truth[target]['invoked_by'].append(name)
                    changed = True
            # B.invoked_by A → A.chains_to B
            for source in list(data['invoked_by']):
                if source in truth and name not in truth[source]['chains_to']:
                    truth[source]['chains_to'].append(name)
                    changed = True
            # A.builds_on B → B.extended_by A
            for base in list(data['builds_on']):
                if base in truth and name not in truth[base]['extended_by']:
                    truth[base]['extended_by'].append(name)
                    changed = True
            # A.extended_by B → B.builds_on A
            for ext in list(data['extended_by']):
                if ext in truth and name not in truth[ext]['builds_on']:
                    truth[ext]['builds_on'].append(name)
                    changed = True

    # Sort all lists for deterministic output
    for data in truth.values():
        for key in ('chains_to', 'invoked_by', 'builds_on', 'extended_by'):
            data[key] = sorted(set(data[key]))

    return truth


def build_chain_js(skill_data: dict) -> dict:
    """Build the CHAIN JS object (parents=invoked_by, children=chains_to)."""
    chain = {}
    for name, data in sorted(skill_data.items()):
        chain[name] = {
            'parents':  data['invoked_by'],
            'children': data['chains_to'],
        }
    return chain


def make_tag(skill_name: str) -> str:
    return f'<span class="overview-tag link" onclick="scrollToSkill(\'{skill_name}\')">{skill_name}</span>'


def make_tags(names: list) -> str:
    return ' '.join(make_tag(n) for n in names)


def build_overview_meta(name: str, data: dict, trigger: str) -> str:
    """Build the overview-meta HTML for a skill's overview card."""
    items = []
    is_foundation = bool(data['extended_by'])

    if is_foundation:
        items.append(
            '          <div class="overview-meta-item">'
            '<strong>Not invoked directly</strong>'
            ' \u2014 loaded via Prerequisites by language-specific skills</div>'
        )
    elif trigger:
        items.append(
            f'          <div class="overview-meta-item">'
            f'<strong>Triggers:</strong> {trigger}</div>'
        )

    if data['chains_to']:
        items.append(
            f'          <div class="overview-meta-item">'
            f'<strong>Chains to:</strong> {make_tags(data["chains_to"])}</div>'
        )
    if data['invoked_by']:
        items.append(
            f'          <div class="overview-meta-item">'
            f'<strong>Invoked by:</strong> {make_tags(data["invoked_by"])}</div>'
        )
    if data['builds_on']:
        items.append(
            f'          <div class="overview-meta-item">'
            f'<strong>Builds on:</strong> {make_tags(data["builds_on"])}</div>'
        )
    if data['extended_by']:
        items.append(
            f'          <div class="overview-meta-item">'
            f'<strong>Extended by:</strong> {make_tags(data["extended_by"])}</div>'
        )

    inner = '\n'.join(items)
    return f'        <div class="overview-meta">\n{inner}\n        </div>\n      </div>'


def write_chaining_truth(truth: dict, test_path: Path, dry_run: bool = False) -> bool:
    """Rewrite the CHAINING_TRUTH dict in the test file."""
    content = test_path.read_text(encoding='utf-8')

    lines = ['CHAINING_TRUTH = {\n']
    for name, data in truth.items():
        entry = (
            f"    '{name}': {{"
            f"'chains_to': {data['chains_to']}, "
            f"'invoked_by': {data['invoked_by']}, "
            f"'builds_on': {data['builds_on']}, "
            f"'extended_by': {data['extended_by']}"
            f"}},\n"
        )
        lines.append(entry)
    lines.append('}\n')
    new_truth_block = ''.join(lines)

    new_content = re.sub(
        r'CHAINING_TRUTH = \{.*?\}\n\n',
        new_truth_block + '\n',
        content,
        flags=re.DOTALL
    )
    if new_content == content:
        print("  CHAINING_TRUTH: no changes needed")
        return False

    if not dry_run:
        test_path.write_text(new_content)
    print(f"  CHAINING_TRUTH: {'would update' if dry_run else 'updated'} ({len(truth)} skills)")
    return True


def write_chain_js(chain: dict, html_path: Path, dry_run: bool = False) -> bool:
    """Rewrite const CHAIN in the HTML file."""
    html = html_path.read_text(encoding='utf-8')

    lines = ['  const CHAIN = {\n']
    for name, data in chain.items():
        parents_str  = str(data['parents']).replace('"', "'")
        children_str = str(data['children']).replace('"', "'")
        lines.append(
            f"    '{name}': "
            f"{{parents:{parents_str},children:{children_str}}},\n"
        )
    lines.append('  };\n')
    new_chain = ''.join(lines)

    new_html = re.sub(
        r'  const CHAIN = \{[\s\S]*?\};\n',
        new_chain,
        html
    )
    if new_html == html:
        print("  CHAIN JS: no changes needed")
        return False

    if not dry_run:
        html_path.write_text(new_html)
    print(f"  CHAIN JS: {'would update' if dry_run else 'updated'} ({len(chain)} skills)")
    return True


def write_overview_metas(skill_data: dict, triggers: dict,
                         html_path: Path, dry_run: bool = False) -> int:
    """Rewrite all overview-meta sections in the HTML file."""
    html = html_path.read_text(encoding='utf-8')
    updated = 0

    for name, data in skill_data.items():
        new_meta = build_overview_meta(name, data, triggers.get(name, ''))
        parts = html.split(f'id="ov-{name}"')
        if len(parts) < 2:
            continue  # skill not in HTML yet

        after = parts[1]
        p_end = after.find('</p>')
        if p_end == -1:
            continue

        kept = after[:p_end + 4]
        depth, pos = 0, p_end + 4
        while pos < len(after):
            m = re.search(r'<(/?)div', after[pos:])
            if not m:
                break
            abs_pos = pos + m.start()
            if m.group(1) == '':
                depth += 1
            else:
                if depth == 0:
                    skill_end = abs_pos + len('</div>')
                    tail = after[skill_end:]
                    new_after = kept + '\n' + new_meta + '\n' + tail
                    if new_after != after:
                        html = parts[0] + f'id="ov-{name}"' + new_after
                        updated += 1
                    break
                depth -= 1
            pos = abs_pos + 1

    if updated == 0:
        print("  Overview metas: no changes needed")
    else:
        if not dry_run:
            html_path.write_text(html)
        print(f"  Overview metas: {'would update' if dry_run else 'updated'} ({updated} cards)")

    return updated


def main(dry_run: bool = False) -> None:
    root = find_skills_root()
    test_path = root / 'tests' / 'test_mockup_chaining.py'
    html_path = root / 'docs' / 'index.html'

    if not test_path.exists():
        print(f"ERROR: {test_path} not found")
        sys.exit(1)
    if not html_path.exists():
        print(f"ERROR: {html_path} not found")
        sys.exit(1)

    print("Reading SKILL.md files...")
    skill_files = find_all_skill_files()
    skill_data = {}
    triggers   = {}

    for skill_path in skill_files:
        name = get_skill_name_from_path(skill_path)
        if name not in ALL_SKILLS:
            continue
        skill_data[name] = extract_full_chaining(skill_path)
        triggers[name]   = extract_trigger(skill_path)

    # Ensure all known skills are present (missing ones get empty entries)
    for name in ALL_SKILLS:
        if name not in skill_data:
            skill_data[name] = {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []}
            triggers[name] = ''

    print(f"Processed {len(skill_data)} skills")
    print()

    truth = build_chaining_truth(skill_data)
    # Build CHAIN JS from the inferred truth (not raw data) so they stay in sync
    chain = {name: {'parents': data['invoked_by'], 'children': data['chains_to']}
             for name, data in truth.items()}

    print("Updating CHAINING_TRUTH in test file...")
    write_chaining_truth(truth, test_path, dry_run)

    print("Updating CHAIN JS in index.html...")
    write_chain_js(chain, html_path, dry_run)

    print("Updating overview card meta sections in index.html...")
    write_overview_metas(truth, triggers, html_path, dry_run)

    print()
    print("Done." if not dry_run else "Dry run complete — no files written.")


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    main(dry_run)
