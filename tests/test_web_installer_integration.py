#!/usr/bin/env python3
"""
Integration tests for web_installer.py — real file operations, no _run mocking.

These tests:
- Create a temp directory as the skills dir (via CLAUDE_SKILLS_DIR env var)
- Run real sync-local --skills commands via the web installer API
- Verify /api/state reflects actual filesystem state
- Test all state permutations: none / partial / all installed per bundle
- Test install/uninstall transitions and bundle state consistency
- Test dependency handling (parent skill row state updates with child)

CLAUDE_SKILLS_DIR is propagated to the claude-skill subprocess by web_installer,
so actual file copies go to the temp dir, not ~/.claude/skills/.
"""

import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

import web_installer as wi
from web_installer import InstallerHandler, read_installed_state

try:
    import urllib.request as urlrequest
    import urllib.error as urlerror
except ImportError:
    pass


# ── Shared fixtures ───────────────────────────────────────────────────────────

PYTHON_BUNDLE   = ['python-dev', 'python-code-review', 'python-security-audit',
                   'pip-dependency-update', 'python-project-health']
TS_BUNDLE       = ['ts-dev', 'ts-code-review', 'ts-security-audit',
                   'npm-dependency-update', 'ts-project-health']
CORE_BUNDLE     = ['git-commit', 'update-claude-md', 'adr',
                   'project-health', 'project-refine']
PRINCIPLES      = ['code-review-principles', 'security-audit-principles',
                   'dependency-management-principles', 'observability-principles']

# Skills with declared dependencies (child → [parents])
SKILL_DEPS = {
    'python-code-review':    ['code-review-principles'],
    'python-security-audit': ['security-audit-principles'],
    'pip-dependency-update': ['dependency-management-principles'],
    'python-project-health': ['project-health'],
    'ts-code-review':        ['code-review-principles'],
    'ts-security-audit':     ['security-audit-principles'],
    'npm-dependency-update': ['dependency-management-principles'],
    'ts-project-health':     ['project-health'],
}


class IntegrationServer:
    """Start web_installer server with a temp SKILLS_DIR."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.skills_dir = self.tmp / 'skills'
        self.skills_dir.mkdir()
        self._orig_skills_dir = None
        self._server = None
        self._thread = None
        self.port = 0
        self.url = ''

    def start(self):
        self._orig_skills_dir = wi.SKILLS_DIR
        wi.SKILLS_DIR = self.skills_dir
        # Also set env var so subprocess (claude-skill) targets same dir
        os.environ['CLAUDE_SKILLS_DIR'] = str(self.skills_dir)

        self._server = HTTPServer(('127.0.0.1', 0), InstallerHandler)
        self.port = self._server.server_address[1]
        self.url  = f'http://127.0.0.1:{self.port}'
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()
        wi.SKILLS_DIR = self._orig_skills_dir
        os.environ.pop('CLAUDE_SKILLS_DIR', None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def get(self, path):
        req = urlrequest.Request(f'{self.url}{path}')
        try:
            with urlrequest.urlopen(req, timeout=10) as resp:
                body = resp.read()
                if 'application/json' in resp.headers.get('Content-Type', ''):
                    return resp.status, json.loads(body)
                return resp.status, body
        except urlerror.HTTPError as e:
            return e.code, json.loads(e.read())

    def post(self, path, data):
        body = json.dumps(data).encode()
        req = urlrequest.Request(
            f'{self.url}{path}', data=body,
            headers={'Content-Type': 'application/json'}, method='POST',
        )
        try:
            with urlrequest.urlopen(req, timeout=60) as resp:
                return resp.status, json.loads(resp.read())
        except urlerror.HTTPError as e:
            return e.code, json.loads(e.read())

    def state(self):
        """Convenience: GET /api/state and return body."""
        _, body = self.get('/api/state')
        return body


# ── Helper: install skills via API ────────────────────────────────────────────

def install(server, skills):
    status, body = server.post('/api/install', {'skills': skills})
    assert status == 200 and body.get('ok'), \
        f'install {skills} failed: {body}'

def uninstall(server, skills):
    status, body = server.post('/api/uninstall', {'skills': skills})
    assert status == 200 and body.get('ok'), \
        f'uninstall {skills} failed: {body}'


# ── 1. State permutations ─────────────────────────────────────────────────────

class TestStatPermutations(unittest.TestCase):
    """
    /api/state must accurately reflect filesystem state for all
    combinations of installed/uninstalled skills.
    """

    def setUp(self):
        self.srv = IntegrationServer()
        self.srv.start()

    def tearDown(self):
        self.srv.stop()

    def test_none_installed_state_is_empty(self):
        s = self.srv.state()
        self.assertEqual(s['installed'], [])
        self.assertEqual(s['versions'], {})

    def test_install_one_skill_appears_in_state(self):
        install(self.srv, ['python-dev'])
        s = self.srv.state()
        self.assertIn('python-dev', s['installed'])

    def test_install_partial_bundle_shows_partial_state(self):
        install(self.srv, PYTHON_BUNDLE[:2])  # python-dev, python-code-review
        s = self.srv.state()
        self.assertIn('python-dev',        s['installed'])
        self.assertIn('python-code-review', s['installed'])
        self.assertNotIn('python-security-audit', s['installed'])
        bundle = s['bundles'].get('python', {})
        self.assertEqual(bundle['state'], 'partial')
        self.assertEqual(bundle['installed'], 2)
        self.assertEqual(bundle['total'], 5)

    def test_install_full_bundle_shows_full_state(self):
        install(self.srv, PYTHON_BUNDLE)
        s = self.srv.state()
        for skill in PYTHON_BUNDLE:
            self.assertIn(skill, s['installed'])
        bundle = s['bundles'].get('python', {})
        self.assertEqual(bundle['state'], 'full')
        self.assertEqual(bundle['installed'], 5)

    def test_uninstall_one_removes_from_state(self):
        install(self.srv, PYTHON_BUNDLE)
        uninstall(self.srv, ['python-dev'])
        s = self.srv.state()
        self.assertNotIn('python-dev', s['installed'])
        self.assertIn('python-code-review', s['installed'])
        bundle = s['bundles'].get('python', {})
        self.assertEqual(bundle['state'], 'partial')
        self.assertEqual(bundle['installed'], 4)

    def test_uninstall_all_bundle_returns_empty_state(self):
        install(self.srv, PYTHON_BUNDLE)
        uninstall(self.srv, PYTHON_BUNDLE)
        s = self.srv.state()
        for skill in PYTHON_BUNDLE:
            self.assertNotIn(skill, s['installed'])
        bundle = s['bundles'].get('python', {})
        self.assertEqual(bundle['state'], 'empty')
        self.assertEqual(bundle['installed'], 0)

    def test_multiple_bundles_tracked_independently(self):
        install(self.srv, PYTHON_BUNDLE)
        install(self.srv, ['ts-dev'])
        s = self.srv.state()
        self.assertEqual(s['bundles']['python']['state'], 'full')
        self.assertEqual(s['bundles']['typescript']['state'], 'partial')

    def test_install_then_uninstall_then_reinstall(self):
        install(self.srv,   ['python-dev'])
        uninstall(self.srv, ['python-dev'])
        install(self.srv,   ['python-dev'])
        s = self.srv.state()
        self.assertIn('python-dev', s['installed'])

    def test_state_installed_list_is_sorted(self):
        install(self.srv, ['python-dev', 'adr', 'git-commit'])
        s = self.srv.state()
        installed = s['installed']
        self.assertEqual(installed, sorted(installed))

    def test_all_bundles_present_in_bundle_response(self):
        s = self.srv.state()
        for bundle_name in ('core', 'principles', 'java-quarkus', 'typescript', 'python'):
            self.assertIn(bundle_name, s['bundles'],
                          f'Bundle "{bundle_name}" missing from /api/state')

    def test_none_installed_all_bundles_empty(self):
        s = self.srv.state()
        for name, info in s['bundles'].items():
            self.assertEqual(info['state'], 'empty',
                             f'Bundle {name} should be empty, got {info["state"]}')
            self.assertEqual(info['installed'], 0)


# ── 2. Bundle state transitions ───────────────────────────────────────────────

class TestBundleStateTransitions(unittest.TestCase):
    """
    Bundle state transitions: empty → partial → full → partial → empty.
    Each transition must update both individual skills and bundle metadata.
    """

    def setUp(self):
        self.srv = IntegrationServer()
        self.srv.start()

    def tearDown(self):
        self.srv.stop()

    def test_empty_to_partial(self):
        install(self.srv, TS_BUNDLE[:2])
        bundle = self.srv.state()['bundles']['typescript']
        self.assertEqual(bundle['state'], 'partial')

    def test_partial_to_full(self):
        install(self.srv, TS_BUNDLE[:2])
        install(self.srv, TS_BUNDLE[2:])
        bundle = self.srv.state()['bundles']['typescript']
        self.assertEqual(bundle['state'], 'full')
        self.assertEqual(bundle['installed'], 5)

    def test_full_to_partial(self):
        install(self.srv, TS_BUNDLE)
        uninstall(self.srv, [TS_BUNDLE[0]])
        bundle = self.srv.state()['bundles']['typescript']
        self.assertEqual(bundle['state'], 'partial')
        self.assertEqual(bundle['installed'], 4)

    def test_partial_to_empty(self):
        install(self.srv, TS_BUNDLE[:2])
        uninstall(self.srv, TS_BUNDLE[:2])
        bundle = self.srv.state()['bundles']['typescript']
        self.assertEqual(bundle['state'], 'empty')
        self.assertEqual(bundle['installed'], 0)

    def test_core_bundle_partial_install(self):
        install(self.srv, ['git-commit', 'adr'])
        bundle = self.srv.state()['bundles']['core']
        self.assertEqual(bundle['state'], 'partial')
        self.assertEqual(bundle['installed'], 2)
        self.assertEqual(bundle['total'], 5)

    def test_install_one_skill_at_a_time_accumulates_correctly(self):
        for i, skill in enumerate(PYTHON_BUNDLE, 1):
            install(self.srv, [skill])
            bundle = self.srv.state()['bundles']['python']
            self.assertEqual(bundle['installed'], i)
        self.assertEqual(bundle['state'], 'full')

    def test_uninstall_one_skill_at_a_time_decrements_correctly(self):
        install(self.srv, PYTHON_BUNDLE)
        for i, skill in enumerate(reversed(PYTHON_BUNDLE), 1):
            uninstall(self.srv, [skill])
            bundle = self.srv.state()['bundles']['python']
            expected = len(PYTHON_BUNDLE) - i
            self.assertEqual(bundle['installed'], expected)


# ── 3. Individual skill state consistency ─────────────────────────────────────

class TestIndividualSkillState(unittest.TestCase):
    """
    After install/uninstall, the individual skill appears / disappears
    in the installed list, and its bundle count is consistent.
    """

    def setUp(self):
        self.srv = IntegrationServer()
        self.srv.start()

    def tearDown(self):
        self.srv.stop()

    def test_installed_skill_in_installed_list(self):
        install(self.srv, ['python-dev'])
        self.assertIn('python-dev', self.srv.state()['installed'])

    def test_uninstalled_skill_not_in_installed_list(self):
        install(self.srv, ['python-dev'])
        uninstall(self.srv, ['python-dev'])
        self.assertNotIn('python-dev', self.srv.state()['installed'])

    def test_installing_skill_with_dep_not_installed_dep(self):
        # sync-local --skills only installs what you ask for.
        # Dependencies are the user's responsibility (shown in UI modal).
        # This test documents the behavior: dep NOT auto-installed.
        install(self.srv, ['python-code-review'])
        s = self.srv.state()
        self.assertIn('python-code-review', s['installed'])
        # code-review-principles was not explicitly installed
        self.assertNotIn('code-review-principles', s['installed'])

    def test_explicitly_install_skill_and_its_dep(self):
        # When user installs skill + dep together (as UI suggests), both appear.
        install(self.srv, ['python-code-review', 'code-review-principles'])
        s = self.srv.state()
        self.assertIn('python-code-review',   s['installed'])
        self.assertIn('code-review-principles', s['installed'])

    def test_dep_installed_separately_then_skill(self):
        install(self.srv, ['code-review-principles'])
        install(self.srv, ['python-code-review'])
        s = self.srv.state()
        self.assertIn('code-review-principles', s['installed'])
        self.assertIn('python-code-review',     s['installed'])

    def test_uninstall_skill_leaves_dep_intact(self):
        install(self.srv, ['code-review-principles', 'python-code-review'])
        uninstall(self.srv, ['python-code-review'])
        s = self.srv.state()
        self.assertNotIn('python-code-review',    s['installed'])
        self.assertIn('code-review-principles', s['installed'])

    def test_bundle_count_consistent_with_installed_list(self):
        install(self.srv, PYTHON_BUNDLE[:3])
        s = self.srv.state()
        bundle = s['bundles']['python']
        # bundle.installed should equal the count of PYTHON_BUNDLE skills
        # that appear in s['installed']
        actual = sum(1 for sk in PYTHON_BUNDLE if sk in s['installed'])
        self.assertEqual(bundle['installed'], actual)

    def test_all_bundle_skills_listed_in_bundle_skills_field(self):
        s = self.srv.state()
        python_bundle = s['bundles']['python']
        for skill in PYTHON_BUNDLE:
            self.assertIn(skill, python_bundle['skills'])


# ── 4. /api/install and /api/uninstall end-to-end ────────────────────────────

class TestInstallUninstallEndToEnd(unittest.TestCase):
    """
    Real end-to-end: POST /api/install → filesystem → GET /api/state roundtrip.
    """

    def setUp(self):
        self.srv = IntegrationServer()
        self.srv.start()

    def tearDown(self):
        self.srv.stop()

    def test_install_single_skill_creates_skill_dir(self):
        install(self.srv, ['python-dev'])
        self.assertTrue((self.srv.skills_dir / 'python-dev' / 'SKILL.md').exists())

    def test_install_bundle_creates_all_skill_dirs(self):
        install(self.srv, PYTHON_BUNDLE)
        for skill in PYTHON_BUNDLE:
            self.assertTrue(
                (self.srv.skills_dir / skill / 'SKILL.md').exists(),
                f'{skill}/SKILL.md not found after bundle install'
            )

    def test_uninstall_removes_skill_dir(self):
        install(self.srv, ['python-dev'])
        uninstall(self.srv, ['python-dev'])
        self.assertFalse((self.srv.skills_dir / 'python-dev').exists())

    def test_install_response_ok_true(self):
        status, body = self.srv.post('/api/install', {'skills': ['python-dev']})
        self.assertEqual(status, 200)
        self.assertTrue(body['ok'])
        self.assertIn('output', body)

    def test_uninstall_response_ok_true(self):
        install(self.srv, ['python-dev'])
        status, body = self.srv.post('/api/uninstall', {'skills': ['python-dev']})
        self.assertEqual(status, 200)
        self.assertTrue(body['ok'])

    def test_install_multiple_skills_all_appear_in_state(self):
        skills = ['python-dev', 'ts-dev', 'adr']
        install(self.srv, skills)
        s = self.srv.state()
        for skill in skills:
            self.assertIn(skill, s['installed'])

    def test_uninstall_multiple_skills_all_removed_from_state(self):
        install(self.srv,   PYTHON_BUNDLE[:3])
        uninstall(self.srv, PYTHON_BUNDLE[:3])
        s = self.srv.state()
        for skill in PYTHON_BUNDLE[:3]:
            self.assertNotIn(skill, s['installed'])

    def test_state_after_install_matches_filesystem(self):
        install(self.srv, PYTHON_BUNDLE)
        # Count actual dirs with SKILL.md
        actual_dirs = {
            d.name for d in self.srv.skills_dir.iterdir()
            if d.is_dir() and (d / 'SKILL.md').exists()
        }
        s = self.srv.state()
        self.assertEqual(set(s['installed']), actual_dirs)

    def test_reinstall_already_installed_skill_succeeds(self):
        install(self.srv, ['python-dev'])
        # Second install should succeed (sync-local handles it)
        status, body = self.srv.post('/api/install', {'skills': ['python-dev']})
        self.assertEqual(status, 200)
        self.assertTrue(body['ok'])


# ── 5. Bundle state field integrity ──────────────────────────────────────────

class TestBundleStateFieldIntegrity(unittest.TestCase):
    """
    The 'bundles' field in /api/state must always be internally consistent:
    installed <= total, state matches count, skills list is accurate.
    """

    def setUp(self):
        self.srv = IntegrationServer()
        self.srv.start()

    def tearDown(self):
        self.srv.stop()

    def _assert_bundle_consistent(self, bundle_name, info, installed_set):
        count = info['installed']
        total = info['total']
        state = info['state']
        skills = info['skills']

        self.assertLessEqual(count, total,
            f'{bundle_name}: installed ({count}) > total ({total})')
        self.assertGreaterEqual(count, 0,
            f'{bundle_name}: installed ({count}) < 0')

        actual_count = sum(1 for s in skills if s in installed_set)
        self.assertEqual(count, actual_count,
            f'{bundle_name}: bundle says {count} installed but {actual_count} in installed list')

        if count == 0:
            self.assertEqual(state, 'empty', f'{bundle_name}: count=0 but state={state}')
        elif count == total:
            self.assertEqual(state, 'full', f'{bundle_name}: count=total but state={state}')
        else:
            self.assertEqual(state, 'partial', f'{bundle_name}: count={count}/{total} but state={state}')

    def test_bundle_consistency_with_nothing_installed(self):
        s = self.srv.state()
        for name, info in s['bundles'].items():
            self._assert_bundle_consistent(name, info, set(s['installed']))

    def test_bundle_consistency_with_partial_install(self):
        install(self.srv, PYTHON_BUNDLE[:2] + TS_BUNDLE[:3] + ['adr'])
        s = self.srv.state()
        for name, info in s['bundles'].items():
            self._assert_bundle_consistent(name, info, set(s['installed']))

    def test_bundle_consistency_with_full_bundle(self):
        install(self.srv, PYTHON_BUNDLE)
        s = self.srv.state()
        for name, info in s['bundles'].items():
            self._assert_bundle_consistent(name, info, set(s['installed']))

    def test_bundle_consistency_after_uninstall(self):
        install(self.srv, PYTHON_BUNDLE + TS_BUNDLE[:2])
        uninstall(self.srv, PYTHON_BUNDLE[1:3])
        s = self.srv.state()
        for name, info in s['bundles'].items():
            self._assert_bundle_consistent(name, info, set(s['installed']))

    def test_bundle_total_matches_marketplace(self):
        # Sanity check: bundle totals come from marketplace.json, not hardcoded
        s = self.srv.state()
        self.assertEqual(s['bundles']['python']['total'], len(PYTHON_BUNDLE))
        self.assertEqual(s['bundles']['typescript']['total'], len(TS_BUNDLE))
        self.assertEqual(s['bundles']['core']['total'], len(CORE_BUNDLE))
        self.assertEqual(s['bundles']['principles']['total'], len(PRINCIPLES))


if __name__ == '__main__':
    unittest.main()
