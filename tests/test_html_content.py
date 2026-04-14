#!/usr/bin/env python3
"""
Fast static tests for docs/index.html content correctness.

These tests parse the HTML without a browser or server — they catch
regressions in hardcoded text, stats, and structural content that
don't require JS execution.

Tests cover the UX/design review fixes:
- Hero stats accuracy (skills, languages, tests)
- Python stack card shows FULL SUITE, not COMING SOON
- No misleading 'Auto-refreshing' label
- Sync bar initial state shows 'Checking...' not stale numbers
- 'Extras' bundle not 'Individual Skills'
- Chain button markup includes 'Chain' text label
- CTA secondary button exists with correct default text
"""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
HTML_PATH = REPO_ROOT / 'docs' / 'index.html'


def load_html() -> str:
    return HTML_PATH.read_text(encoding='utf-8')


class TestHeroStats(unittest.TestCase):
    """Hero stats must reflect the actual collection size."""

    def setUp(self):
        self.html = load_html()

    def test_skills_count_is_current(self):
        m = re.search(r'hero-stat-num[^>]*>(\d+)</div><div class="hero-stat-label">Skills', self.html)
        self.assertIsNotNone(m, 'Could not find Skills stat')
        actual = int(m.group(1))
        self.assertGreaterEqual(actual, 48, f'Skills count in web app ({actual}) is below expected minimum of 48')
        self.assertLess(actual, 200, f'Skills count ({actual}) is suspiciously high')

    def test_languages_count_is_current(self):
        # Should show 3 (Java, TypeScript, Python), not 2
        m = re.search(r'hero-stat-num[^>]*>(\d+)</div><div class="hero-stat-label">Languages', self.html)
        self.assertIsNotNone(m, 'Could not find Languages stat')
        self.assertEqual(m.group(1), '3', f'Languages stat shows {m.group(1)}, expected 3')

    def test_tests_count_is_current(self):
        # Should show 295, not the old 163
        m = re.search(r'hero-stat-num[^>]*>(\d+)</div><div class="hero-stat-label">Tests', self.html)
        self.assertIsNotNone(m, 'Could not find Tests stat')
        count = int(m.group(1))
        self.assertGreaterEqual(count, 295, f'Tests stat shows {count}, expected ≥295')

    def test_token_efficiency_references_current_skill_count(self):
        # The "42 skills cost less than one prompt" section
        self.assertIn('42 skills cost less than one prompt', self.html)
        self.assertNotIn('33 skills cost less than one prompt', self.html)

    def test_token_word_count_matches_skills(self):
        # 41 skills × ~30 words = ~1,200 words
        self.assertIn('42 skills', self.html)
        self.assertIn('1,200 words', self.html)
        self.assertNotIn('1,000 words', self.html)


class TestPythonStackCard(unittest.TestCase):
    """Python must be shown as a full suite, not coming soon."""

    def setUp(self):
        self.html = load_html()

    def test_python_not_coming_soon(self):
        self.assertNotIn('COMING SOON', self.html,
                         'Python stack still shows COMING SOON — must be updated to FULL SUITE')

    def test_python_shows_full_suite(self):
        # The Python card should have "FULL SUITE" and green styling
        self.assertIn('FULL SUITE', self.html)

    def test_python_has_real_features(self):
        # Should list actual Python features, not placeholder bullets
        self.assertIn('pip/poetry/pipenv', self.html)
        self.assertNotIn('◦ Development skill', self.html)

    def test_python_card_not_greyed_out(self):
        # Old grey styling: color:#6b7280 on Python heading
        # New: no grey override on Python heading
        # Check that the COMING SOON grey color block is gone
        self.assertNotIn('color:#9ca3af;">COMING SOON', self.html)
        self.assertNotIn('color:#9ca3af;">◦', self.html)


class TestMisleadingLabelsRemoved(unittest.TestCase):
    """Removed UI elements must stay removed."""

    def setUp(self):
        self.html = load_html()

    def test_auto_refreshing_label_removed(self):
        self.assertNotIn('Auto-refreshing', self.html,
                         '"Auto-refreshing" label is back — must be removed (page does not auto-refresh)')

    def test_refresh_dot_css_removed(self):
        self.assertNotIn('refresh-dot', self.html,
                         'refresh-dot CSS/element is back — must be removed with Auto-refreshing label')


class TestSyncBarInitialState(unittest.TestCase):
    """Sync bar must show a loading state, not stale hardcoded numbers."""

    def setUp(self):
        self.html = load_html()

    def test_sync_bar_does_not_show_stale_count(self):
        # Old hardcoded "15 of 33 installed" must be gone
        self.assertNotIn('15 of 33 installed', self.html)
        self.assertNotIn('15 of 40 installed', self.html)

    def test_sync_bar_shows_loading_placeholder(self):
        # Should start with a neutral loading state
        self.assertIn('Checking', self.html,
                      'Sync bar should show "Checking…" as initial state')

    def test_outdated_label_not_hardcoded(self):
        # Must not have a hardcoded number — JS populates this dynamically
        self.assertNotIn('2 outdated', self.html,
                         'Hardcoded "2 outdated" found — outdated-label must start empty')


class TestBundleNaming(unittest.TestCase):
    """The catch-all bundle must be named 'Extras', not 'Individual Skills'."""

    def setUp(self):
        self.html = load_html()

    def test_individual_skills_label_removed(self):
        # The section-label and bundle-name should say Extras, not Individual Skills
        self.assertNotIn('>Individual Skills<', self.html)

    def test_extras_bundle_name_present(self):
        self.assertIn('>Extras<', self.html)

    def test_extras_nav_pill(self):
        # Nav pill should contain Extras (whitespace may vary)
        self.assertRegex(self.html, r'nav-pill[^>]*href="#b-individual"[^>]*>[\s\S]*?Extras')

    def test_extras_has_descriptive_subtitle(self):
        self.assertIn('Workflow tools, documentation aids', self.html)


class TestChainButtonLabel(unittest.TestCase):
    """Chain button must include 'Chain' text, not just the icon."""

    def setUp(self):
        self.html = load_html()

    def test_chain_button_includes_text_label(self):
        # wireChainHovers injects a 'Chain' text span into every chain button.
        # The label is in the JS source (injected at runtime), not static HTML.
        self.assertIn('>Chain</span>', self.html,
                      "Chain button JS injection must include 'Chain' text label")

    def test_chain_button_has_flex_layout(self):
        # Button must have inline-flex to lay out icon + text
        self.assertIn('inline-flex', self.html)


class TestCTAButtons(unittest.TestCase):
    """CTA secondary button must be context-aware."""

    def setUp(self):
        self.html = load_html()

    def test_cta_secondary_button_exists(self):
        self.assertIn('id="cta-secondary"', self.html)

    def test_cta_secondary_handles_web_context(self):
        # Must include logic to show 'View on GitHub' on web
        self.assertIn('View on GitHub', self.html)

    def test_cta_secondary_local_action(self):
        # Must call setView('install') when local
        self.assertIn("setView('install')", self.html)

    def test_install_now_default_text(self):
        # Default text (before JS runs) should be Install Now
        self.assertIn('Install Now', self.html)


class TestRefreshButton(unittest.TestCase):
    """Refresh button must be wired to loadState()."""

    def setUp(self):
        self.html = load_html()

    def test_refresh_button_calls_load_state(self):
        # btn-refresh must have onclick calling loadState
        self.assertIn('btn-refresh', self.html)
        # Check the button has an onclick that calls loadState
        m = re.search(r'btn-refresh[^>]*onclick="([^"]*)"', self.html)
        self.assertIsNotNone(m, 'btn-refresh has no onclick handler')
        self.assertIn('loadState', m.group(1),
                      f'Refresh button onclick does not call loadState: {m.group(1)!r}')


class TestManualModeText(unittest.TestCase):
    """Manual mode confirm button and note text must guide the user correctly."""

    def setUp(self):
        self.html = load_html()

    def test_manual_mode_confirm_button_says_done_refresh(self):
        # The JS sets btn.textContent to 'Done — Refresh' in manual mode
        self.assertIn('Done — Refresh', self.html)

    def test_manual_mode_note_guides_copy_paste_workflow(self):
        # Note should tell user to click Done after running the command
        self.assertIn('click Done', self.html)
        # Old misleading text must be gone from BOTH modal note locations
        self.assertNotIn('auto-refresh once complete', self.html,
                         'Old "auto-refresh once complete" text still present in a modal note')


if __name__ == '__main__':
    unittest.main()
