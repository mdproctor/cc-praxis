#!/usr/bin/env python3
"""
UI integration tests for the cc-praxis web installer using Playwright.

These tests run a real web installer server with a temp SKILLS_DIR,
open a browser, and assert on the actual rendered HTML — not just the API.

Tests verify for every bundle:
- bundle-count text matches installed/total
- state class (state-empty / state-partial / state-full) is correct
- Install button visible when not all skills installed
- Uninstall button visible when any skills installed
- Both buttons visible when partial
- Individual skill rows show correct Install/Uninstall button

Run:
    python3 -m pytest tests/test_web_installer_ui.py -v
"""

import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from http.server import HTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

import web_installer as wi
from web_installer import InstallerHandler

try:
    from playwright.sync_api import sync_playwright, Page, expect
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# ── Bundle definitions (must match marketplace.json) ─────────────────────────

BUNDLES = {
    'core':       {'el': 'b-core',       'install_modal': 'install-core',       'uninstall_modal': 'uninstall-core',
                   'skills': ['git-commit','update-claude-md','adr','project-health','project-refine']},
    'principles': {'el': 'b-principles', 'install_modal': 'install-principles', 'uninstall_modal': 'uninstall-principles',
                   'skills': ['code-review-principles','security-audit-principles','dependency-management-principles','observability-principles']},
    'java':       {'el': 'b-java',       'install_modal': 'install-java',        'uninstall_modal': 'uninstall-java',
                   'skills': ['java-dev','java-code-review','java-security-audit','java-git-commit','java-update-design',
                              'maven-dependency-update','quarkus-flow-dev','quarkus-flow-testing','quarkus-observability','java-project-health']},
    'typescript': {'el': 'b-ts',         'install_modal': 'install-ts',          'uninstall_modal': 'uninstall-ts',
                   'skills': ['ts-dev','ts-code-review','ts-security-audit','npm-dependency-update','ts-project-health']},
    'python':     {'el': 'b-python',     'install_modal': 'install-python',      'uninstall_modal': 'uninstall-python',
                   'skills': ['python-dev','python-code-review','python-security-audit','pip-dependency-update','python-project-health']},
}

PYTHON_BUNDLE = BUNDLES['python']['skills']
TS_BUNDLE     = BUNDLES['typescript']['skills']
CORE_BUNDLE   = BUNDLES['core']['skills']
PRINCIPLES    = BUNDLES['principles']['skills']


# ── Server + browser fixture ──────────────────────────────────────────────────

class UITestBase(unittest.TestCase):
    """Base class: starts server + Playwright browser, provides helpers."""

    @classmethod
    def setUpClass(cls):
        if not PLAYWRIGHT_AVAILABLE:
            raise unittest.SkipTest('playwright not installed')

        cls.tmp = Path(tempfile.mkdtemp())
        cls.skills_dir = cls.tmp / 'skills'
        cls.skills_dir.mkdir()

        # Patch web_installer module
        cls._orig_skills_dir = wi.SKILLS_DIR
        wi.SKILLS_DIR = cls.skills_dir
        os.environ['CLAUDE_SKILLS_DIR'] = str(cls.skills_dir)

        cls._server = HTTPServer(('127.0.0.1', 0), InstallerHandler)
        cls.port = cls._server.server_address[1]
        cls.base_url = f'http://127.0.0.1:{cls.port}'
        cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
        cls._thread.start()

        cls._pw = sync_playwright().start()
        cls._browser = cls._pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls._browser.close()
        cls._pw.stop()
        cls._server.shutdown()
        wi.SKILLS_DIR = cls._orig_skills_dir
        os.environ.pop('CLAUDE_SKILLS_DIR', None)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        # Clean skills dir between tests
        shutil.rmtree(self.skills_dir, ignore_errors=True)
        self.skills_dir.mkdir()
        self.page = self._browser.new_page()
        self._open_install_tab()

    def tearDown(self):
        self.page.close()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _open_install_tab(self):
        self.page.goto(self.base_url)
        self.page.wait_for_load_state('networkidle')
        self.page.click('#tab-install')
        # Expand all bundles so skill rows are visible (collapsed by default)
        self.page.evaluate(
            "BUNDLE_IDS.forEach(id => document.getElementById(id).classList.add('open'))"
        )
        self.page.wait_for_timeout(200)

    def _install(self, skills: list[str]):
        """Install skills via API and refresh page state."""
        import urllib.request, json as _json
        body = _json.dumps({'skills': skills}).encode()
        req = urllib.request.Request(
            f'{self.base_url}/api/install', data=body,
            headers={'Content-Type': 'application/json'}, method='POST',
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            result = _json.loads(r.read())
        assert result.get('ok'), f'install failed: {result}'
        # Await the async loadState() call and wait for DOM to settle
        self.page.evaluate('async () => { await loadState(); }')
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(200)

    def _uninstall(self, skills: list[str]):
        """Uninstall skills via API and refresh page state."""
        import urllib.request, json as _json
        body = _json.dumps({'skills': skills}).encode()
        req = urllib.request.Request(
            f'{self.base_url}/api/uninstall', data=body,
            headers={'Content-Type': 'application/json'}, method='POST',
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            result = _json.loads(r.read())
        assert result.get('ok'), f'uninstall failed: {result}'
        self.page.evaluate('async () => { await loadState(); }')
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(200)

    def _bundle(self, bundle_name: str) -> dict:
        """Return Playwright locators for a bundle by name."""
        info = BUNDLES[bundle_name]
        el_id = info['el']
        el = self.page.locator(f'#{el_id}')
        return {
            'el':         el,
            'count':      el.locator('.bundle-count'),
            'state_class': lambda: self.page.evaluate(
                f'document.getElementById("{el_id}").className'
            ),
            'install_btn':   el.locator('.bundle-actions .btn-install'),
            'uninstall_btn': el.locator('.bundle-actions .btn-uninstall'),
            'skills':        info['skills'],
            'total':         len(info['skills']),
        }

    def _skill_row(self, skill_name: str):
        """Locator for a skill row in the Install tab."""
        return self.page.locator(f'.skill-row').filter(
            has=self.page.locator(f'.skill-name:text-is("{skill_name}")')
        )

    def _assert_bundle_state(self, bundle_name, expected_count, expected_total, expected_state):
        b = self._bundle(bundle_name)
        self.assertEqual(
            b['count'].inner_text(),
            f'{expected_count} of {expected_total}',
            f'{bundle_name}: wrong count text'
        )
        classes = b['state_class']()
        self.assertIn(f'state-{expected_state}', classes,
                      f'{bundle_name}: expected state-{expected_state} in "{classes}"')

        if expected_state == 'empty':
            expect(b['install_btn']).to_be_visible()
            expect(b['uninstall_btn']).not_to_be_visible()
        elif expected_state == 'full':
            expect(b['install_btn']).not_to_be_visible()
            expect(b['uninstall_btn']).to_be_visible()
        else:  # partial
            expect(b['install_btn']).to_be_visible()
            expect(b['uninstall_btn']).to_be_visible()


# ── 1. Initial state — nothing installed ─────────────────────────────────────

class TestInitialState(UITestBase):
    """All bundles start empty — install button visible, uninstall hidden."""

    def test_all_bundles_show_zero_installed(self):
        for name, info in BUNDLES.items():
            self._assert_bundle_state(name, 0, len(info['skills']), 'empty')

    def test_all_skill_rows_show_install_button(self):
        for skill in PYTHON_BUNDLE:
            row = self._skill_row(skill)
            expect(row.locator('.btn-install')).to_be_visible()
            expect(row.locator('.btn-uninstall')).not_to_be_visible()


# ── 2. Partial install state ──────────────────────────────────────────────────

class TestPartialInstallState(UITestBase):
    """After installing some skills, bundle shows partial state."""

    def test_partial_python_shows_partial_state(self):
        self._install(PYTHON_BUNDLE[:2])
        self._assert_bundle_state('python', 2, 5, 'partial')

    def test_partial_shows_both_buttons(self):
        self._install(PYTHON_BUNDLE[:3])
        b = self._bundle('python')
        expect(b['install_btn']).to_be_visible()
        expect(b['uninstall_btn']).to_be_visible()

    def test_installed_skill_rows_show_uninstall(self):
        self._install(PYTHON_BUNDLE[:2])
        for skill in PYTHON_BUNDLE[:2]:
            row = self._skill_row(skill)
            expect(row.locator('.btn-uninstall')).to_be_visible()

    def test_uninstalled_skill_rows_show_install(self):
        self._install(PYTHON_BUNDLE[:2])
        for skill in PYTHON_BUNDLE[2:]:
            row = self._skill_row(skill)
            expect(row.locator('.btn-install')).to_be_visible()

    def test_count_text_updates_correctly(self):
        self._install(PYTHON_BUNDLE[:3])
        b = self._bundle('python')
        self.assertEqual(b['count'].inner_text(), '3 of 5')

    def test_partial_typescript(self):
        self._install(TS_BUNDLE[:2])
        self._assert_bundle_state('typescript', 2, 5, 'partial')

    def test_partial_core(self):
        self._install(CORE_BUNDLE[:2])
        self._assert_bundle_state('core', 2, 5, 'partial')

    def test_partial_principles(self):
        self._install(PRINCIPLES[:2])
        self._assert_bundle_state('principles', 2, 4, 'partial')

    def test_multiple_bundles_independent(self):
        self._install(PYTHON_BUNDLE[:2])
        self._install(TS_BUNDLE)
        self._assert_bundle_state('python',     2, 5, 'partial')
        self._assert_bundle_state('typescript', 5, 5, 'full')


# ── 3. Full install state ─────────────────────────────────────────────────────

class TestFullInstallState(UITestBase):
    """After installing all skills in a bundle, only Uninstall shown."""

    def test_full_python_shows_full_state(self):
        self._install(PYTHON_BUNDLE)
        self._assert_bundle_state('python', 5, 5, 'full')

    def test_full_typescript_shows_full_state(self):
        self._install(TS_BUNDLE)
        self._assert_bundle_state('typescript', 5, 5, 'full')

    def test_full_core_shows_full_state(self):
        self._install(CORE_BUNDLE)
        self._assert_bundle_state('core', 5, 5, 'full')

    def test_full_principles_shows_full_state(self):
        self._install(PRINCIPLES)
        self._assert_bundle_state('principles', 4, 4, 'full')

    def test_full_install_hides_install_button(self):
        self._install(PYTHON_BUNDLE)
        b = self._bundle('python')
        expect(b['install_btn']).not_to_be_visible()
        expect(b['uninstall_btn']).to_be_visible()

    def test_all_skill_rows_show_uninstall_when_full(self):
        self._install(PYTHON_BUNDLE)
        for skill in PYTHON_BUNDLE:
            row = self._skill_row(skill)
            expect(row.locator('.btn-uninstall')).to_be_visible()


# ── 4. Uninstall transitions ──────────────────────────────────────────────────

class TestUninstallTransitions(UITestBase):
    """Uninstalling skills must update bundle state correctly."""

    def test_full_to_partial_on_one_uninstall(self):
        self._install(PYTHON_BUNDLE)
        self._uninstall([PYTHON_BUNDLE[0]])
        self._assert_bundle_state('python', 4, 5, 'partial')

    def test_partial_to_empty_on_remaining_uninstall(self):
        self._install(PYTHON_BUNDLE[:2])
        self._uninstall(PYTHON_BUNDLE[:2])
        self._assert_bundle_state('python', 0, 5, 'empty')

    def test_full_to_empty_uninstalls_all(self):
        self._install(PYTHON_BUNDLE)
        self._uninstall(PYTHON_BUNDLE)
        self._assert_bundle_state('python', 0, 5, 'empty')

    def test_uninstalled_row_shows_install_button(self):
        self._install(PYTHON_BUNDLE)
        self._uninstall([PYTHON_BUNDLE[0]])
        row = self._skill_row(PYTHON_BUNDLE[0])
        expect(row.locator('.btn-install')).to_be_visible()

    def test_remaining_rows_still_show_uninstall(self):
        self._install(PYTHON_BUNDLE)
        self._uninstall([PYTHON_BUNDLE[0]])
        for skill in PYTHON_BUNDLE[1:]:
            row = self._skill_row(skill)
            expect(row.locator('.btn-uninstall')).to_be_visible()

    def test_count_decrements_on_uninstall(self):
        self._install(PYTHON_BUNDLE)
        for expected in range(4, -1, -1):
            if expected < 5:
                self._uninstall([PYTHON_BUNDLE[4 - expected]])
            b = self._bundle('python')
            self.assertEqual(b['count'].inner_text(), f'{expected} of 5')


# ── 5. Bundle modal reflects actual installed count, not hardcoded total ───────

class TestBundleModalAccuracy(UITestBase):
    """
    Bundle-level Install/Uninstall modals must reflect only the skills
    that are actually relevant — not the full hardcoded list.

    Bug: with 2 of 5 Python skills installed, clicking the bundle Uninstall
    button showed "Uninstall 5 skills" and would attempt to uninstall all 5,
    even though only 2 are present.

    Desired behaviour:
    - Bundle Uninstall modal: label and sub-text show only the installed count
    - Bundle Install modal: label and sub-text show only the NOT-yet-installed count
    """

    def _open_bundle_modal(self, bundle_name, action):
        """Click Install or Uninstall on a bundle and wait for modal to open."""
        b = self._bundle(bundle_name)
        btn = b['install_btn'] if action == 'install' else b['uninstall_btn']
        btn.click()
        self.page.wait_for_selector('#overlay.open', timeout=5000)

    def _close_modal(self):
        # Cancel button uses class .btn-cancel (no id), inside #overlay
        self.page.locator('#overlay .btn-cancel').click()
        # Overlay closes by removing .open class, making it display:none → wait for hidden
        self.page.locator('#overlay').wait_for(state='hidden', timeout=3000)

    # ── Uninstall modal ───────────────────────────────────────────────────────

    def test_uninstall_modal_shows_installed_count_not_total(self):
        """With 2 of 5 installed, Uninstall modal must say 2, not 5."""
        self._install(PYTHON_BUNDLE[:2])
        self._open_bundle_modal('python', 'uninstall')
        sub = self.page.locator('#m-sub').inner_text()
        label = self.page.locator('#m-confirm').inner_text()
        self._close_modal()
        self.assertIn('2', label, f'Label should say 2 skills, got: {label!r}')
        self.assertNotIn('5', label, f'Label must not say 5 skills, got: {label!r}')
        # Sub-text should also reflect the actual count
        self.assertNotIn('5 Python', sub)

    def test_uninstall_modal_cmd_shows_only_installed_skills(self):
        """The displayed command must list only installed skills."""
        installed = PYTHON_BUNDLE[:2]
        not_installed = PYTHON_BUNDLE[2:]
        self._install(installed)
        self._open_bundle_modal('python', 'uninstall')
        cmd = self.page.locator('#m-cmd').inner_text()
        self._close_modal()
        for skill in installed:
            self.assertIn(skill, cmd, f'Installed skill {skill} missing from cmd')
        for skill in not_installed:
            self.assertNotIn(skill, cmd, f'Uninstalled skill {skill} should not be in cmd')

    def test_uninstall_modal_single_remaining_skill(self):
        """With 1 of 5 installed, label says 'Uninstall 1 skill'."""
        self._install([PYTHON_BUNDLE[0]])
        self._open_bundle_modal('python', 'uninstall')
        label = self.page.locator('#m-confirm').inner_text()
        self._close_modal()
        self.assertIn('1', label)
        self.assertNotIn('5', label)

    def test_uninstall_all_installed_shows_full_count(self):
        """With all 5 installed, Uninstall modal correctly says 5."""
        self._install(PYTHON_BUNDLE)
        self._open_bundle_modal('python', 'uninstall')
        label = self.page.locator('#m-confirm').inner_text()
        self._close_modal()
        self.assertIn('5', label)

    # ── Install modal ─────────────────────────────────────────────────────────

    def test_install_modal_shows_missing_count_not_total(self):
        """With 3 of 5 already installed, Install modal must say 2, not 5."""
        self._install(PYTHON_BUNDLE[:3])
        self._open_bundle_modal('python', 'install')
        label = self.page.locator('#m-confirm').inner_text()
        self._close_modal()
        self.assertIn('2', label, f'Should say 2 remaining, got: {label!r}')
        self.assertNotIn('5', label)

    def test_install_modal_cmd_excludes_already_installed(self):
        """The displayed install command must not include already-installed skills."""
        already = PYTHON_BUNDLE[:3]
        remaining = PYTHON_BUNDLE[3:]
        self._install(already)
        self._open_bundle_modal('python', 'install')
        cmd = self.page.locator('#m-cmd').inner_text()
        self._close_modal()
        for skill in remaining:
            self.assertIn(skill, cmd, f'Missing skill {skill} should be in cmd')
        for skill in already:
            self.assertNotIn(skill, cmd, f'Already-installed {skill} should not be in cmd')

    def test_install_modal_single_remaining_skill(self):
        """With 4 of 5 installed, Install modal says 'Install 1 skill'."""
        self._install(PYTHON_BUNDLE[:4])
        self._open_bundle_modal('python', 'install')
        label = self.page.locator('#m-confirm').inner_text()
        self._close_modal()
        self.assertIn('1', label)
        self.assertNotIn('5', label)

    def test_principles_uninstall_modal_accuracy(self):
        """Same bug applies to Principles bundle — verify fix is universal."""
        self._install(PRINCIPLES[:2])
        self._open_bundle_modal('principles', 'uninstall')
        label = self.page.locator('#m-confirm').inner_text()
        self._close_modal()
        self.assertIn('2', label)
        self.assertNotIn('4', label)


# ── 6. State transition cycle ─────────────────────────────────────────────────

class TestStateTransitionCycle(UITestBase):
    """Full cycle: empty → partial → full → partial → empty for all bundles."""

    def _cycle(self, bundle_name):
        info = BUNDLES[bundle_name]
        skills = info['skills']
        total  = len(skills)
        half   = total // 2

        # empty
        self._assert_bundle_state(bundle_name, 0, total, 'empty')

        # partial
        self._install(skills[:half])
        self._assert_bundle_state(bundle_name, half, total, 'partial')

        # full
        self._install(skills[half:])
        self._assert_bundle_state(bundle_name, total, total, 'full')

        # back to partial
        self._uninstall([skills[0]])
        self._assert_bundle_state(bundle_name, total - 1, total, 'partial')

        # back to empty
        self._uninstall(skills[1:])
        self._assert_bundle_state(bundle_name, 0, total, 'empty')

    def test_cycle_python(self):
        self._cycle('python')

    def test_cycle_typescript(self):
        self._cycle('typescript')

    def test_cycle_core(self):
        self._cycle('core')

    def test_cycle_principles(self):
        self._cycle('principles')


# ── 6. Dependency display ─────────────────────────────────────────────────────

class TestDependencyDisplay(UITestBase):
    """
    When installing a skill with an uninstalled dependency, the dep's
    skill row must also update after install (user installs both together).
    """

    def test_installing_skill_and_dep_both_rows_update(self):
        self._install(['python-code-review', 'code-review-principles'])
        # Both rows should show Uninstall
        row_skill = self._skill_row('python-code-review')
        expect(row_skill.locator('.btn-uninstall')).to_be_visible()

        # code-review-principles is in the principles bundle
        row_dep = self._skill_row('code-review-principles')
        expect(row_dep.locator('.btn-uninstall')).to_be_visible()

    def test_installing_dep_updates_its_bundle_count(self):
        self._install(['code-review-principles'])
        self._assert_bundle_state('principles', 1, 4, 'partial')

    def test_skill_row_without_dep_installed_shows_install(self):
        # dep not installed: skill row still shows install (no auto-install)
        self._install(['python-code-review'])
        row_dep = self._skill_row('code-review-principles')
        expect(row_dep.locator('.btn-install')).to_be_visible()


if __name__ == '__main__':
    unittest.main()
