#!/usr/bin/env python3
"""
Tests for cc-praxis-check skill.

Unit: SKILL.md structure and CSO compliance.
Integration: All four diagnostic checks are documented, recovery steps present,
  marketplace and commands are wired up.
"""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILL_PATH = REPO_ROOT / 'cc-praxis-check' / 'SKILL.md'
COMMAND_PATH = REPO_ROOT / 'cc-praxis-check' / 'commands' / 'cc-praxis-check.md'
MARKETPLACE_PATH = REPO_ROOT / '.claude-plugin' / 'marketplace.json'


def load_skill() -> str:
    return SKILL_PATH.read_text(encoding='utf-8')


class TestSkillExists(unittest.TestCase):
    """Unit: skill files exist with correct structure."""

    def test_skill_md_exists(self):
        self.assertTrue(SKILL_PATH.exists(), 'cc-praxis-check/SKILL.md must exist')

    def test_command_file_exists(self):
        self.assertTrue(COMMAND_PATH.exists(),
                        'cc-praxis-check/commands/cc-praxis-check.md must exist')

    def test_skill_has_frontmatter(self):
        content = load_skill()
        self.assertTrue(content.startswith('---'), 'SKILL.md must have YAML frontmatter')

    def test_skill_name_matches_directory(self):
        content = load_skill()
        self.assertIn('name: cc-praxis-check', content)

    def test_description_starts_with_use_when(self):
        content = load_skill()
        self.assertIn('Use when', content)

    def test_description_is_not_workflow_summary(self):
        """CSO: description must not say HOW the skill works."""
        content = load_skill()
        # Extract description block
        fm_end = content.index('---', 3)
        frontmatter = content[:fm_end]
        for banned in ('runs', 'checks', 'diagnoses', 'reports', 'lists'):
            # These workflow words should be in the body, not in the description
            desc_start = frontmatter.find('description:')
            if desc_start == -1:
                continue
            desc_text = frontmatter[desc_start:]
            # Allow them after the first line (the "Use when" line)
            first_line = desc_text.split('\n')[1] if '\n' in desc_text else ''
            self.assertNotIn(f' {banned} ', first_line.lower(),
                             f'Description first line must not contain workflow word "{banned}"')


class TestSkillInMarketplace(unittest.TestCase):
    """Integration: skill is registered in marketplace.json."""

    def setUp(self):
        import json
        with open(MARKETPLACE_PATH) as f:
            self.data = json.load(f)
        self.plugins = {p['name']: p for p in self.data['plugins']}

    def test_skill_in_marketplace(self):
        self.assertIn('cc-praxis-check', self.plugins,
                      'cc-praxis-check must be in marketplace.json plugins')

    def test_marketplace_description_not_empty(self):
        desc = self.plugins.get('cc-praxis-check', {}).get('description', '')
        self.assertGreater(len(desc), 20, 'Marketplace description must be meaningful')

    def test_marketplace_source_correct(self):
        source = self.plugins.get('cc-praxis-check', {}).get('source', '')
        self.assertEqual(source, './cc-praxis-check')


class TestDiagnosticCoverage(unittest.TestCase):
    """Integration: all four diagnostic checks are documented in the skill."""

    def setUp(self):
        self.content = load_skill()

    def test_check1_claude_md(self):
        self.assertIn('CLAUDE.md', self.content)
        self.assertIn('project type', self.content.lower())

    def test_check2_installed_skills(self):
        self.assertIn('~/.claude/skills/', self.content)
        self.assertIn('Installed skills', self.content)

    def test_check3_session_hook(self):
        self.assertIn('check_project_setup', self.content)
        self.assertIn('settings.json', self.content)

    def test_check4_design_md(self):
        self.assertIn('DESIGN.md', self.content)

    def test_all_four_checks_present(self):
        """Each check must be marked as a distinct numbered check."""
        for n in ('1', '2', '3', '4'):
            self.assertIn(f'Check {n}', self.content,
                          f'Check {n} must be present in the skill')


class TestRecoverySteps(unittest.TestCase):
    """Integration: recovery steps are specific, not vague."""

    def setUp(self):
        self.content = load_skill()

    def test_claude_md_recovery_is_a_prompt(self):
        """Recovery for missing CLAUDE.md is a Claude prompt, not a generic instruction."""
        self.assertIn('Set up a CLAUDE.md', self.content)

    def test_skill_install_recovery_uses_exact_command(self):
        """Recovery for missing skill shows the install command."""
        self.assertIn('scripts/claude-skill install', self.content)

    def test_hook_recovery_mentions_install_skills(self):
        self.assertIn('/install-skills', self.content)

    def test_design_md_recovery_present(self):
        self.assertIn('Create a DESIGN.md', self.content)

    def test_report_uses_status_symbols(self):
        """Report must use ✅ / ❌ / ⚠️ symbols."""
        self.assertIn('✅', self.content)
        self.assertIn('❌', self.content)
        self.assertIn('⚠️', self.content)


class TestSkillQuality(unittest.TestCase):
    """Integration: skill has required quality sections."""

    def setUp(self):
        self.content = load_skill()

    def test_has_success_criteria(self):
        self.assertIn('Success Criteria', self.content)

    def test_has_common_pitfalls(self):
        self.assertIn('Common Pitfalls', self.content)

    def test_has_skill_chaining(self):
        self.assertIn('Skill Chaining', self.content)

    def test_skill_body_under_400_lines(self):
        lines = self.content.splitlines()
        self.assertLess(len(lines), 400,
                        f'SKILL.md is {len(lines)} lines — keep under 400')

    def test_java_specific_check_scoped_correctly(self):
        """DESIGN.md check must be explicitly scoped to Java only."""
        self.assertIn('Java only', self.content)
