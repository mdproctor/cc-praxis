#!/usr/bin/env python3
"""
Test that the web installer mockup HTML correctly reflects the bidirectional
chaining relationships defined in each skill's SKILL.md file.

This prevents bit rot: when a skill's chaining is updated, this test fails
until the mockup overview cards are updated to match.

Run with: python3 -m pytest tests/test_mockup_chaining.py -v
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

SKILLS_ROOT = Path(__file__).parent.parent
MOCKUP_PATH = SKILLS_ROOT / 'docs' / 'index.html'  # canonical file (was web-installer-mockup.html)

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
    'idea-log', 'project-blog', 'cc-praxis-ui', 'garden', 'session-handoff',
}

# Ground truth extracted from all SKILL.md files.
# Update this when a skill's chaining is intentionally changed.
CHAINING_TRUTH = {
    'adr': {'chains_to': ['custom-git-commit', 'git-commit', 'java-git-commit', 'java-update-design', 'project-blog'], 'invoked_by': ['design-snapshot', 'idea-log', 'java-update-design', 'maven-dependency-update', 'project-blog'], 'builds_on': [], 'extended_by': []},
    'blog-git-commit': {'chains_to': ['update-claude-md'], 'invoked_by': ['git-commit'], 'builds_on': [], 'extended_by': []},
    'blog-project-health': {'chains_to': [], 'invoked_by': ['project-health'], 'builds_on': ['project-health'], 'extended_by': []},
    'cc-praxis-ui': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []},
    'code-review-principles': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': ['java-code-review', 'python-code-review', 'ts-code-review']},
    'custom-git-commit': {'chains_to': ['update-claude-md', 'update-primary-doc'], 'invoked_by': ['adr', 'design-snapshot', 'idea-log', 'project-blog'], 'builds_on': ['git-commit'], 'extended_by': []},
    'custom-project-health': {'chains_to': [], 'invoked_by': ['project-health'], 'builds_on': ['project-health'], 'extended_by': []},
    'dependency-management-principles': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': ['maven-dependency-update', 'npm-dependency-update', 'pip-dependency-update']},
    'design-snapshot': {'chains_to': ['adr', 'custom-git-commit', 'git-commit', 'idea-log', 'java-git-commit', 'project-blog'], 'invoked_by': ['project-blog'], 'builds_on': [], 'extended_by': []},
    'garden': {'chains_to': ['git-commit'], 'invoked_by': [], 'builds_on': [], 'extended_by': []},
    'git-commit': {'chains_to': ['blog-git-commit', 'issue-workflow', 'python-code-review', 'ts-code-review', 'update-claude-md'], 'invoked_by': ['adr', 'design-snapshot', 'garden', 'idea-log', 'project-blog', 'python-code-review', 'ts-code-review'], 'builds_on': [], 'extended_by': ['custom-git-commit', 'java-git-commit']},
    'idea-log': {'chains_to': ['adr', 'custom-git-commit', 'git-commit', 'issue-workflow', 'java-git-commit'], 'invoked_by': ['design-snapshot', 'java-code-review', 'python-code-review', 'ts-code-review'], 'builds_on': [], 'extended_by': []},
    'install-skills': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []},
    'issue-workflow': {'chains_to': [], 'invoked_by': ['git-commit', 'idea-log'], 'builds_on': [], 'extended_by': []},
    'java-code-review': {'chains_to': ['idea-log', 'java-git-commit', 'java-security-audit'], 'invoked_by': ['java-dev', 'java-git-commit', 'quarkus-flow-dev', 'quarkus-flow-testing'], 'builds_on': ['code-review-principles', 'java-dev'], 'extended_by': []},
    'java-dev': {'chains_to': ['java-code-review', 'quarkus-observability'], 'invoked_by': [], 'builds_on': [], 'extended_by': ['java-code-review', 'java-security-audit', 'quarkus-flow-dev', 'quarkus-flow-testing']},
    'java-git-commit': {'chains_to': ['java-code-review', 'java-update-design', 'update-claude-md'], 'invoked_by': ['adr', 'design-snapshot', 'idea-log', 'java-code-review', 'maven-dependency-update', 'project-blog', 'quarkus-flow-dev', 'quarkus-flow-testing', 'quarkus-observability'], 'builds_on': ['git-commit'], 'extended_by': []},
    'java-project-health': {'chains_to': [], 'invoked_by': ['project-health'], 'builds_on': ['project-health'], 'extended_by': []},
    'java-security-audit': {'chains_to': [], 'invoked_by': ['java-code-review'], 'builds_on': ['java-dev', 'security-audit-principles'], 'extended_by': []},
    'java-update-design': {'chains_to': ['adr'], 'invoked_by': ['adr', 'java-git-commit', 'update-claude-md'], 'builds_on': ['update-primary-doc'], 'extended_by': []},
    'maven-dependency-update': {'chains_to': ['adr', 'java-git-commit'], 'invoked_by': ['quarkus-observability'], 'builds_on': ['dependency-management-principles'], 'extended_by': []},
    'npm-dependency-update': {'chains_to': [], 'invoked_by': [], 'builds_on': ['dependency-management-principles'], 'extended_by': []},
    'observability-principles': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': ['quarkus-observability']},
    'pip-dependency-update': {'chains_to': [], 'invoked_by': [], 'builds_on': ['dependency-management-principles'], 'extended_by': []},
    'project-blog': {'chains_to': ['adr', 'custom-git-commit', 'design-snapshot', 'git-commit', 'java-git-commit'], 'invoked_by': ['adr', 'design-snapshot'], 'builds_on': [], 'extended_by': []},
    'project-health': {'chains_to': ['blog-project-health', 'custom-project-health', 'java-project-health', 'python-project-health', 'skills-project-health', 'ts-project-health'], 'invoked_by': [], 'builds_on': [], 'extended_by': ['blog-project-health', 'custom-project-health', 'java-project-health', 'python-project-health', 'skills-project-health', 'ts-project-health']},
    'project-refine': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []},
    'python-code-review': {'chains_to': ['git-commit', 'idea-log', 'python-security-audit'], 'invoked_by': ['git-commit', 'python-dev'], 'builds_on': ['code-review-principles', 'python-dev'], 'extended_by': []},
    'python-dev': {'chains_to': ['python-code-review'], 'invoked_by': [], 'builds_on': [], 'extended_by': ['python-code-review', 'python-security-audit']},
    'python-project-health': {'chains_to': [], 'invoked_by': ['project-health'], 'builds_on': ['project-health'], 'extended_by': []},
    'python-security-audit': {'chains_to': [], 'invoked_by': ['python-code-review'], 'builds_on': ['python-dev', 'security-audit-principles'], 'extended_by': []},
    'quarkus-flow-dev': {'chains_to': ['java-code-review', 'java-git-commit', 'quarkus-flow-testing', 'quarkus-observability'], 'invoked_by': [], 'builds_on': ['java-dev'], 'extended_by': ['quarkus-flow-testing']},
    'quarkus-flow-testing': {'chains_to': ['java-code-review', 'java-git-commit'], 'invoked_by': ['quarkus-flow-dev'], 'builds_on': ['java-dev', 'quarkus-flow-dev'], 'extended_by': []},
    'quarkus-observability': {'chains_to': ['java-git-commit', 'maven-dependency-update'], 'invoked_by': ['java-dev', 'quarkus-flow-dev'], 'builds_on': ['observability-principles'], 'extended_by': []},
    'security-audit-principles': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': ['java-security-audit', 'python-security-audit', 'ts-security-audit']},
    'session-handoff': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []},
    'skills-project-health': {'chains_to': [], 'invoked_by': ['project-health'], 'builds_on': ['project-health'], 'extended_by': []},
    'ts-code-review': {'chains_to': ['git-commit', 'idea-log', 'ts-security-audit'], 'invoked_by': ['git-commit', 'ts-dev'], 'builds_on': ['code-review-principles', 'ts-dev'], 'extended_by': []},
    'ts-dev': {'chains_to': ['ts-code-review'], 'invoked_by': [], 'builds_on': [], 'extended_by': ['ts-code-review', 'ts-security-audit']},
    'ts-project-health': {'chains_to': [], 'invoked_by': ['project-health'], 'builds_on': ['project-health'], 'extended_by': []},
    'ts-security-audit': {'chains_to': [], 'invoked_by': ['ts-code-review'], 'builds_on': ['security-audit-principles', 'ts-dev'], 'extended_by': []},
    'uninstall-skills': {'chains_to': [], 'invoked_by': [], 'builds_on': [], 'extended_by': []},
    'update-claude-md': {'chains_to': ['java-update-design'], 'invoked_by': ['blog-git-commit', 'custom-git-commit', 'git-commit', 'java-git-commit'], 'builds_on': [], 'extended_by': []},
    'update-primary-doc': {'chains_to': [], 'invoked_by': ['custom-git-commit'], 'builds_on': [], 'extended_by': ['java-update-design']},
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_mockup_chains():
    """Extract chaining relationships from each overview-skill card in the mockup."""
    if not MOCKUP_PATH.exists():
        raise FileNotFoundError(f"Mockup not found: {MOCKUP_PATH}")

    html = MOCKUP_PATH.read_text(encoding='utf-8')
    skill_blocks = {}
    parts = re.split(r'<div class="overview-skill" id="ov-([^"]+)">', html)
    for i in range(1, len(parts), 2):
        skill_name = parts[i]
        # Take content up to the next skill card or end of overview-skills-list
        block = parts[i + 1].split('<div class="overview-skill"')[0].split('id="ov-')[0]
        skill_blocks[skill_name] = block
    return skill_blocks


def extract_rel(block, label):
    """Extract scrollToSkill targets from a meta-item with the given label."""
    pattern = rf'<strong>{re.escape(label)}[:\s]*</strong>(.*?)(?=<div class="overview-meta-item"|</div>\s*</div>)'
    m = re.search(pattern, block, re.DOTALL)
    if not m:
        return set()
    return set(re.findall(r"scrollToSkill\('([^']+)'\)", m.group(1)))


def extract_skillmd_chains(skill_name):
    """Extract chaining from a SKILL.md file's ## Skill Chaining section."""
    skill_path = SKILLS_ROOT / skill_name / 'SKILL.md'
    if not skill_path.exists():
        return None

    content = skill_path.read_text(encoding='utf-8')
    section_m = re.search(r'## Skill Chaining(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if not section_m:
        return {'chains_to': set(), 'invoked_by': set(), 'builds_on': set(), 'extended_by': set()}

    section = section_m.group(1)

    def extract_skill_names(text):
        """Extract skill names in backticks from text."""
        names = set(re.findall(r'`([a-z][a-z0-9-]+)`', text))
        return names & ALL_SKILLS

    chains_to = set()
    invoked_by = set()
    builds_on = set()

    for line in section.split('\n'):
        low = line.lower()
        if any(k in low for k in ['chains to', 'invokes:', '**invokes**']):
            chains_to |= extract_skill_names(line)
        if any(k in low for k in ['invoked by', '**invoked by**']):
            invoked_by |= extract_skill_names(line)
        if any(k in low for k in ['builds on', 'prerequisites', 'extends', 'extended by']):
            builds_on |= extract_skill_names(line)

    # Also check Prerequisites section
    prereq_m = re.search(r'## Prerequisites(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if prereq_m:
        for line in prereq_m.group(1).split('\n'):
            low = line.lower()
            if any(k in low for k in ['build', 'extends', 'based on', 'applies all']):
                builds_on |= extract_skill_names(line)

    return {'chains_to': chains_to, 'invoked_by': invoked_by, 'builds_on': builds_on, 'extended_by': set()}


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_mockup_has_overview_card_for_every_skill():
    """Every known skill must have an overview card in the mockup."""
    skill_blocks = parse_mockup_chains()
    missing = ALL_SKILLS - set(skill_blocks.keys())
    assert not missing, f"Missing overview cards for: {sorted(missing)}"


def test_mockup_chains_match_ground_truth():
    """Overview card relationship tags must match the CHAINING_TRUTH table."""
    skill_blocks = parse_mockup_chains()
    errors = []

    for skill, truth in CHAINING_TRUTH.items():
        block = skill_blocks.get(skill, '')
        mockup = {
            'chains_to':  extract_rel(block, 'Chains to'),
            'invoked_by': extract_rel(block, 'Invoked by'),
            'builds_on':  extract_rel(block, 'Builds on'),
            'extended_by':extract_rel(block, 'Extended by'),
        }
        for rel in ('chains_to', 'invoked_by', 'builds_on', 'extended_by'):
            truth_set = set(truth[rel])
            mock_set  = mockup[rel]
            missing = truth_set - mock_set
            extra   = mock_set - truth_set
            if missing:
                errors.append(f"[{skill}] {rel} MISSING in mockup: {sorted(missing)}")
            if extra:
                errors.append(f"[{skill}] {rel} EXTRA in mockup (not in truth): {sorted(extra)}")

    assert not errors, "Mockup overview cards don't match ground truth:\n" + '\n'.join(errors)


def test_ground_truth_is_bidirectional():
    """
    If A.chains_to contains B, then B.invoked_by should contain A.
    If A.builds_on contains B, then B.extended_by should contain A (for principles)
    or B is a valid build target.
    This catches inconsistencies in the CHAINING_TRUTH table itself.

    KNOWN ASYMMETRY: git-commit is a universal user-triggered entry point.
    Many skills (ts-code-review, java-code-review) chain TO git-commit as a
    suggestion after completing their workflow, but git-commit's own SKILL.md
    documents it as user-triggered only — it does not list those skills as
    invokers. This is intentional: the chain is an offer, not a strict
    invocation relationship. git-commit is therefore exempt from the
    bidirectionality check for its invoked_by direction.
    """
    BIDIRECTIONAL_EXEMPT_TARGETS = {'git-commit'}  # universal entry points

    errors = []
    for skill, data in CHAINING_TRUTH.items():
        for target in data['chains_to']:
            if target not in CHAINING_TRUTH:
                continue
            if target in BIDIRECTIONAL_EXEMPT_TARGETS:
                continue  # these skills are offers/suggestions, not strict invocations
            if skill not in CHAINING_TRUTH[target]['invoked_by']:
                errors.append(
                    f"{skill} chains_to {target}, but {target}.invoked_by doesn't include {skill}"
                )
        for target in data['invoked_by']:
            if target not in CHAINING_TRUTH:
                continue
            if skill not in CHAINING_TRUTH[target]['chains_to']:
                errors.append(
                    f"{skill} invoked_by {target}, but {target}.chains_to doesn't include {skill}"
                )

    assert not errors, "CHAINING_TRUTH is not bidirectionally consistent:\n" + '\n'.join(errors)


def test_ground_truth_references_known_skills_only():
    """All skill names in CHAINING_TRUTH must be in ALL_SKILLS."""
    errors = []
    for skill, data in CHAINING_TRUTH.items():
        for rel, targets in data.items():
            for t in targets:
                if t not in ALL_SKILLS:
                    errors.append(f"[{skill}] {rel} references unknown skill: {t}")
    assert not errors, '\n'.join(errors)


def test_skillmd_chains_roughly_match_truth():
    """
    Sanity check: chains_to and builds_on in SKILL.md files should broadly
    align with CHAINING_TRUTH. Fails loudly if a SKILL.md is updated but
    CHAINING_TRUTH is not, prompting a human to review and update the truth table.
    """
    errors = []
    for skill in ALL_SKILLS:
        md_chains = extract_skillmd_chains(skill)
        if md_chains is None:
            continue  # skill dir doesn't exist yet
        truth = CHAINING_TRUTH.get(skill, {})

        # Check chains_to: anything in SKILL.md chains_to should be in truth
        truth_ct = set(truth.get('chains_to', []))
        md_ct    = md_chains['chains_to']
        extra_in_md = md_ct - truth_ct - {'user'}
        if extra_in_md:
            errors.append(
                f"[{skill}] SKILL.md chains_to has {extra_in_md} not in CHAINING_TRUTH — "
                f"update CHAINING_TRUTH and the mockup"
            )

        # Check builds_on
        truth_bo = set(truth.get('builds_on', [])) | set(truth.get('extended_by', []))
        md_bo    = md_chains['builds_on']
        extra_in_md = md_bo - truth_bo - {'user'}
        if extra_in_md:
            errors.append(
                f"[{skill}] SKILL.md builds_on has {extra_in_md} not in CHAINING_TRUTH — "
                f"update CHAINING_TRUTH and the mockup"
            )

    assert not errors, (
        "SKILL.md chaining has drifted from CHAINING_TRUTH:\n" + '\n'.join(errors) +
        "\n\nTo fix: update CHAINING_TRUTH in this file and regenerate the mockup meta sections."
    )


def test_chain_js_matches_chaining_truth():
    """
    The const CHAIN object in index.html must match CHAINING_TRUTH.

    This catches drift between the generator output (CHAINING_TRUTH) and the
    CHAIN JS in the web app. If this fails, run:
        python3 scripts/generate_web_app_data.py
    """
    import re

    html = MOCKUP_PATH.read_text(encoding='utf-8')

    # Parse const CHAIN from the HTML
    m = re.search(r'const CHAIN = \{([\s\S]*?)\};', html)
    assert m, "const CHAIN not found in index.html"

    chain_js = {}
    for entry in re.finditer(
        r"'([^']+)':\s*\{parents:\[([^\]]*)\],children:\[([^\]]*)\]\}",
        m.group(1)
    ):
        name     = entry.group(1)
        parents  = sorted(s.strip("' ") for s in entry.group(2).split(',') if s.strip("' "))
        children = sorted(s.strip("' ") for s in entry.group(3).split(',') if s.strip("' "))
        chain_js[name] = {'parents': parents, 'children': children}

    errors = []
    for skill, truth in CHAINING_TRUTH.items():
        if skill not in chain_js:
            errors.append(f"'{skill}' missing from const CHAIN in index.html")
            continue
        js = chain_js[skill]

        # children should match chains_to
        truth_children = sorted(truth['chains_to'])
        if js['children'] != truth_children:
            errors.append(
                f"'{skill}' CHAIN.children {js['children']} != "
                f"CHAINING_TRUTH.chains_to {truth_children}"
            )

        # parents should match invoked_by
        truth_parents = sorted(truth['invoked_by'])
        if js['parents'] != truth_parents:
            errors.append(
                f"'{skill}' CHAIN.parents {js['parents']} != "
                f"CHAINING_TRUTH.invoked_by {truth_parents}"
            )

    assert not errors, (
        "const CHAIN in index.html doesn't match CHAINING_TRUTH.\n"
        "Run: python3 scripts/generate_web_app_data.py\n\n"
        + '\n'.join(errors)
    )


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
