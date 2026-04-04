#!/usr/bin/env python3
"""
Tests for scripts/web_installer.py — Section 2 of the web installer test spec.

Covers:
  2.1  GET /api/state
  2.2  GET /api/marketplace
  2.3  POST /api/install
  2.4  POST /api/uninstall
  2.5  POST /api/update
  2.6  Version detection / is_outdated()
  2.7  Static file serving (GET /)
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
from unittest.mock import MagicMock, patch

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

from web_installer import (
    InstallerHandler,
    is_outdated,
    read_installed_state,
    validate_skill_names,
    MARKETPLACE_PATH,
    HTML_PATH,
)

try:
    import urllib.request as urlrequest
    import urllib.error as urlerror
except ImportError:
    pass  # should always be available


# ── Test HTTP client helper ───────────────────────────────────────────────────

class ServerFixture:
    """Starts web_installer.py's HTTP server on a random port for testing."""

    def __init__(self, skills_dir: Path, marketplace_path: Path | None = None):
        self.skills_dir = skills_dir
        self.marketplace_path = marketplace_path
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port: int = 0
        self.url: str = ''

    def start(self):
        import web_installer as wi
        # Patch module-level paths to use test fixtures
        self._orig_skills_dir = wi.SKILLS_DIR
        self._orig_mkt_path   = wi.MARKETPLACE_PATH
        wi.SKILLS_DIR       = self.skills_dir
        if self.marketplace_path is not None:
            wi.MARKETPLACE_PATH = self.marketplace_path

        self._server = HTTPServer(('127.0.0.1', 0), InstallerHandler)
        self.port = self._server.server_address[1]
        self.url  = f'http://127.0.0.1:{self.port}'

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        import web_installer as wi
        if self._server:
            self._server.shutdown()
        wi.SKILLS_DIR       = self._orig_skills_dir
        wi.MARKETPLACE_PATH = self._orig_mkt_path

    def get(self, path: str) -> tuple[int, dict | bytes, dict]:
        req = urlrequest.Request(f'{self.url}{path}')
        try:
            with urlrequest.urlopen(req, timeout=5) as resp:
                body = resp.read()
                ct = resp.headers.get('Content-Type', '')
                headers = dict(resp.headers)
                if 'application/json' in ct:
                    return resp.status, json.loads(body), headers
                return resp.status, body, headers
        except urlerror.HTTPError as e:
            body = e.read()
            ct = e.headers.get('Content-Type', '')
            if 'application/json' in ct:
                return e.code, json.loads(body), dict(e.headers)
            return e.code, body, dict(e.headers)

    def post(self, path: str, data: dict) -> tuple[int, dict, dict]:
        body = json.dumps(data).encode()
        req = urlrequest.Request(
            f'{self.url}{path}', data=body,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urlrequest.urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read()), dict(resp.headers)
        except urlerror.HTTPError as e:
            return e.code, json.loads(e.read()), dict(e.headers)


def make_skill(skills_dir: Path, name: str, version: str | None = None) -> Path:
    """Create a minimal installed skill directory."""
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / 'SKILL.md').write_text(f'# {name}\n', encoding='utf-8')
    if version is not None:
        (skill_dir / 'plugin.json').write_text(
            json.dumps({'version': version}), encoding='utf-8'
        )
    return skill_dir


def make_marketplace(path: Path, plugins: list[dict]) -> None:
    """Write a minimal marketplace.json for testing."""
    data = {'name': 'cc-praxis', 'plugins': plugins}
    path.write_text(json.dumps(data), encoding='utf-8')


# ── 2.1 GET /api/state ────────────────────────────────────────────────────────

class TestGetState(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.skills_dir = self.tmp / 'skills'
        self.skills_dir.mkdir()
        self.server = ServerFixture(skills_dir=self.skills_dir)
        self.server.start()

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_2_1_1_empty_dir_returns_empty_installed(self):
        status, body, _ = self.server.get('/api/state')
        self.assertEqual(status, 200)
        self.assertEqual(body['installed'], [])
        self.assertEqual(body['versions'], {})

    def test_2_1_2_missing_dir_returns_empty(self):
        self.skills_dir.rmdir()
        status, body, _ = self.server.get('/api/state')
        self.assertEqual(status, 200)
        self.assertEqual(body['installed'], [])

    def test_2_1_3_one_skill_installed(self):
        make_skill(self.skills_dir, 'git-commit')
        status, body, _ = self.server.get('/api/state')
        self.assertEqual(status, 200)
        self.assertIn('git-commit', body['installed'])

    def test_2_1_4_dir_without_skill_md_not_counted(self):
        (self.skills_dir / 'random-dir').mkdir()  # no SKILL.md
        status, body, _ = self.server.get('/api/state')
        self.assertNotIn('random-dir', body['installed'])

    def test_2_1_5_version_read_from_plugin_json(self):
        make_skill(self.skills_dir, 'git-commit', version='1.0.0')
        status, body, _ = self.server.get('/api/state')
        self.assertEqual(body['versions']['git-commit'], '1.0.0')

    def test_2_1_6_missing_plugin_json_version_absent(self):
        make_skill(self.skills_dir, 'ts-dev')  # no version
        status, body, _ = self.server.get('/api/state')
        self.assertIn('ts-dev', body['installed'])
        self.assertNotIn('ts-dev', body['versions'])

    def test_2_1_7_content_type_is_json(self):
        _, _, headers = self.server.get('/api/state')
        self.assertIn('application/json', headers.get('Content-Type', ''))

    def test_2_1_8_multiple_skills(self):
        names = ['git-commit', 'adr', 'ts-dev', 'java-dev', 'update-claude-md']
        for n in names:
            make_skill(self.skills_dir, n)
        status, body, _ = self.server.get('/api/state')
        for n in names:
            self.assertIn(n, body['installed'])


# ── 2.2 GET /api/marketplace ──────────────────────────────────────────────────

class TestGetMarketplace(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.skills_dir = self.tmp / 'skills'
        self.skills_dir.mkdir()
        self.mkt_path = self.tmp / 'marketplace.json'

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_2_2_1_returns_full_marketplace(self):
        make_marketplace(self.mkt_path, [{'name': 'git-commit', 'version': '1.0.0'}])
        server = ServerFixture(self.skills_dir, self.mkt_path)
        server.start()
        try:
            status, body, _ = server.get('/api/marketplace')
            self.assertEqual(status, 200)
            self.assertEqual(body['name'], 'cc-praxis')
        finally:
            server.stop()

    def test_2_2_2_file_not_found_returns_500(self):
        # Don't create marketplace.json
        server = ServerFixture(self.skills_dir, self.tmp / 'nonexistent.json')
        server.start()
        try:
            status, body, _ = server.get('/api/marketplace')
            self.assertEqual(status, 500)
            self.assertFalse(body['ok'])
        finally:
            server.stop()

    def test_2_2_3_malformed_json_returns_500(self):
        self.mkt_path.write_text('not valid json', encoding='utf-8')
        server = ServerFixture(self.skills_dir, self.mkt_path)
        server.start()
        try:
            status, body, _ = server.get('/api/marketplace')
            self.assertEqual(status, 500)
        finally:
            server.stop()

    def test_2_2_4_content_type_is_json(self):
        make_marketplace(self.mkt_path, [])
        server = ServerFixture(self.skills_dir, self.mkt_path)
        server.start()
        try:
            _, _, headers = server.get('/api/marketplace')
            self.assertIn('application/json', headers.get('Content-Type', ''))
        finally:
            server.stop()


# ── 2.3 POST /api/install ────────────────────────────────────────────────────

class TestPostInstall(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.skills_dir = self.tmp / 'skills'
        self.skills_dir.mkdir()
        self.server = ServerFixture(skills_dir=self.skills_dir)
        self.server.start()

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _post_install(self, skills, patch_run=True, run_ok=True, run_output='done'):
        """Helper: POST /api/install, optionally mocking _run."""
        import web_installer as wi
        if patch_run:
            with patch.object(wi, '_run', return_value=(run_ok, run_output)) as mock_run:
                status, body, _ = self.server.post('/api/install', {'skills': skills})
                return status, body, mock_run
        return self.server.post('/api/install', {'skills': skills}) + (None,)

    def test_2_3_1_valid_skill_calls_correct_command(self):
        # Must use 'sync-local --skills <name> -y'
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(True, 'ok')) as mock_run:
            self.server.post('/api/install', {'skills': ['git-commit']})
        args = mock_run.call_args[0]
        self.assertIn('sync-local', args)
        self.assertIn('--skills', args)
        self.assertIn('git-commit', args)
        self.assertIn('-y', args)

    def test_2_3_2_multiple_skills_all_in_single_command(self):
        # All skills go in one sync-local --skills call
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(True, 'ok')) as mock_run:
            self.server.post('/api/install', {'skills': ['git-commit', 'ts-dev']})
        args = mock_run.call_args[0]
        self.assertIn('sync-local', args)
        self.assertIn('--skills', args)
        self.assertIn('git-commit', args)
        self.assertIn('ts-dev', args)

    def test_2_3_3_empty_skills_returns_400(self):
        status, body, _ = self.server.post('/api/install', {'skills': []})
        self.assertEqual(status, 400)

    def test_2_3_4_missing_skills_key_returns_400(self):
        status, body, _ = self.server.post('/api/install', {})
        self.assertEqual(status, 400)

    def test_2_3_5_path_traversal_returns_400(self):
        status, body, _ = self.server.post('/api/install', {'skills': ['../etc/passwd']})
        self.assertEqual(status, 400)

    def test_2_3_6_shell_metacharacters_returns_400(self):
        status, body, _ = self.server.post('/api/install', {'skills': ['git-commit; rm -rf /']})
        self.assertEqual(status, 400)

    def test_2_3_7_success_returns_200_with_output(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(True, 'installed git-commit')):
            status, body, _ = self.server.post('/api/install', {'skills': ['git-commit']})
        self.assertEqual(status, 200)
        self.assertTrue(body['ok'])
        self.assertIn('output', body)

    def test_2_3_8_subprocess_failure_returns_500(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(False, 'error: not found')):
            status, body, _ = self.server.post('/api/install', {'skills': ['git-commit']})
        self.assertEqual(status, 500)

    def test_2_3_11_subprocess_failure_with_multiple_skills_returns_500(self):
        # sync-local --skills failure returns 500
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(False, 'error: skill not found')):
            status, body, _ = self.server.post('/api/install', {'skills': ['git-commit', 'ts-dev']})
        self.assertEqual(status, 500)

    def test_2_3_9_valid_name_pattern_passes(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(True, 'ok')):
            status, body, _ = self.server.post('/api/install', {'skills': ['java-dev']})
        self.assertEqual(status, 200)

    def test_2_3_10_non_json_body_returns_400(self):
        req = urlrequest.Request(
            f'{self.server.url}/api/install',
            data=b'plain text',
            headers={'Content-Type': 'text/plain'},
            method='POST',
        )
        try:
            with urlrequest.urlopen(req, timeout=5):
                pass
            self.fail('Expected HTTPError')
        except urlerror.HTTPError as e:
            self.assertEqual(e.code, 400)


# ── 2.4 POST /api/uninstall ──────────────────────────────────────────────────

class TestPostUninstall(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.skills_dir = self.tmp / 'skills'
        self.skills_dir.mkdir()
        self.server = ServerFixture(skills_dir=self.skills_dir)
        self.server.start()

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_2_4_1_valid_skill_calls_uninstall_command(self):
        import web_installer as wi
        calls = []
        with patch.object(wi, '_run', side_effect=lambda *a: calls.append(a) or (True, 'ok')):
            self.server.post('/api/uninstall', {'skills': ['ts-dev']})
        self.assertEqual(len(calls), 1)
        self.assertIn('uninstall', calls[0])
        self.assertIn('ts-dev', calls[0])

    def test_2_4_2_multiple_skills_each_gets_own_uninstall_call(self):
        import web_installer as wi
        calls = []
        with patch.object(wi, '_run', side_effect=lambda *a: calls.append(a) or (True, 'ok')):
            self.server.post('/api/uninstall', {'skills': ['ts-dev', 'ts-code-review']})
        self.assertEqual(len(calls), 2, 'Expected one _run call per skill')
        removed = [c[1] for c in calls]
        self.assertIn('ts-dev', removed)
        self.assertIn('ts-code-review', removed)

    def test_2_4_3_empty_list_returns_400(self):
        status, body, _ = self.server.post('/api/uninstall', {'skills': []})
        self.assertEqual(status, 400)

    def test_2_4_4_path_traversal_returns_400(self):
        status, body, _ = self.server.post('/api/uninstall', {'skills': ['../../secrets']})
        self.assertEqual(status, 400)

    def test_2_4_5_success_returns_200(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(True, 'removed')):
            status, body, _ = self.server.post('/api/uninstall', {'skills': ['ts-dev']})
        self.assertEqual(status, 200)
        self.assertTrue(body['ok'])

    def test_2_4_6_subprocess_failure_returns_500(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(False, 'error')):
            status, body, _ = self.server.post('/api/uninstall', {'skills': ['ts-dev']})
        self.assertEqual(status, 500)

    def test_2_4_7_non_json_body_returns_400(self):
        req = urlrequest.Request(
            f'{self.server.url}/api/uninstall',
            data=b'plain text',
            headers={'Content-Type': 'text/plain'},
            method='POST',
        )
        try:
            with urlrequest.urlopen(req, timeout=5):
                pass
            self.fail('Expected HTTPError')
        except urlerror.HTTPError as e:
            self.assertEqual(e.code, 400)


# ── 2.5 POST /api/update ─────────────────────────────────────────────────────

class TestPostUpdate(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.skills_dir = self.tmp / 'skills'
        self.skills_dir.mkdir()
        self.server = ServerFixture(skills_dir=self.skills_dir)
        self.server.start()

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_2_5_1_correct_command_executed(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(True, 'ok')) as mock_run:
            self.server.post('/api/update', {})
        args = mock_run.call_args[0]
        self.assertIn('sync-local', args)
        self.assertIn('--all', args)
        self.assertIn('-y', args)

    def test_2_5_2_success_returns_200(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(True, 'updated')):
            status, body, _ = self.server.post('/api/update', {})
        self.assertEqual(status, 200)
        self.assertTrue(body['ok'])

    def test_2_5_3_failure_returns_500(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(False, 'error')):
            status, body, _ = self.server.post('/api/update', {})
        self.assertEqual(status, 500)

    def test_2_5_4_extra_body_fields_ignored(self):
        import web_installer as wi
        with patch.object(wi, '_run', return_value=(True, 'ok')) as mock_run:
            status, body, _ = self.server.post('/api/update', {'extra': 'field'})
        self.assertEqual(status, 200)


# ── 2.6 Version detection ─────────────────────────────────────────────────────

class TestVersionDetection(unittest.TestCase):

    def test_2_6_1_same_version_not_outdated(self):
        self.assertFalse(is_outdated('1.0.0', '1.0.0'))

    def test_2_6_2_older_version_is_outdated(self):
        self.assertTrue(is_outdated('1.0.0', '1.0.1'))

    def test_2_6_3_newer_version_not_outdated(self):
        self.assertFalse(is_outdated('1.0.1', '1.0.0'))

    def test_2_6_4_snapshot_older_than_release(self):
        # SNAPSHOT is treated as pre-release (older than the release)
        self.assertTrue(is_outdated('1.0.0-SNAPSHOT', '1.0.0'))

    def test_2_6_4b_release_not_older_than_snapshot(self):
        self.assertFalse(is_outdated('1.0.0', '1.0.0-SNAPSHOT'))

    def test_2_6_state_includes_outdated_field(self):
        """read_installed_state() returns outdated list from marketplace comparison."""
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / 'skills'
            mkt_path   = Path(tmp) / 'marketplace.json'
            make_skill(skills_dir, 'git-commit', version='1.0.0')
            make_marketplace(mkt_path, [{'name': 'git-commit', 'version': '1.0.1'}])
            import web_installer as wi
            orig_sd, orig_mp = wi.SKILLS_DIR, wi.MARKETPLACE_PATH
            wi.SKILLS_DIR, wi.MARKETPLACE_PATH = skills_dir, mkt_path
            try:
                _,  _, outdated, _ = read_installed_state()
                self.assertIn('git-commit', outdated)
            finally:
                wi.SKILLS_DIR, wi.MARKETPLACE_PATH = orig_sd, orig_mp

    def test_2_6_5_missing_plugin_json_not_outdated(self):
        """Skills without plugin.json should not be flagged as outdated."""
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / 'skills'
            mkt_path   = Path(tmp) / 'marketplace.json'
            make_skill(skills_dir, 'ts-dev')  # no version
            make_marketplace(mkt_path, [{'name': 'ts-dev', 'version': '1.0.0'}])
            import web_installer as wi
            orig_sd, orig_mp = wi.SKILLS_DIR, wi.MARKETPLACE_PATH
            wi.SKILLS_DIR, wi.MARKETPLACE_PATH = skills_dir, mkt_path
            try:
                _,  _, outdated, _ = read_installed_state()
                self.assertNotIn('ts-dev', outdated)
            finally:
                wi.SKILLS_DIR, wi.MARKETPLACE_PATH = orig_sd, orig_mp

    def test_2_6_6_skill_not_in_marketplace_not_outdated(self):
        """Installed skill absent from marketplace should not crash or be flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / 'skills'
            mkt_path   = Path(tmp) / 'marketplace.json'
            make_skill(skills_dir, 'local-only', version='1.0.0')
            make_marketplace(mkt_path, [])  # empty plugins
            import web_installer as wi
            orig_sd, orig_mp = wi.SKILLS_DIR, wi.MARKETPLACE_PATH
            wi.SKILLS_DIR, wi.MARKETPLACE_PATH = skills_dir, mkt_path
            try:
                installed, _, outdated, _ = read_installed_state()
                self.assertIn('local-only', installed)
                self.assertNotIn('local-only', outdated)
            finally:
                wi.SKILLS_DIR, wi.MARKETPLACE_PATH = orig_sd, orig_mp


# ── 2.7 Static file serving ───────────────────────────────────────────────────

class TestStaticFileServing(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.skills_dir = self.tmp / 'skills'
        self.skills_dir.mkdir()
        self.server = ServerFixture(skills_dir=self.skills_dir)
        self.server.start()

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_2_7_1_root_serves_index_html(self):
        status, body, headers = self.server.get('/')
        self.assertEqual(status, 200)
        self.assertIn('text/html', headers.get('Content-Type', ''))
        # body is bytes here since content-type is HTML
        self.assertIn(b'cc-praxis', body)

    def test_2_7_2_unknown_path_returns_404(self):
        status, body, _ = self.server.get('/nonexistent')
        self.assertEqual(status, 404)

    def test_2_7_3_index_html_returns_html_content_type(self):
        status, body, headers = self.server.get('/')
        self.assertIn('text/html', headers.get('Content-Type', ''))

    def test_2_7_4_path_traversal_returns_404(self):
        # URL-encoded path traversal
        req = urlrequest.Request(f'{self.server.url}/%2E%2E%2F%2E%2E%2Fetc%2Fpasswd')
        try:
            with urlrequest.urlopen(req, timeout=5) as resp:
                self.assertNotEqual(resp.status, 200)
        except urlerror.HTTPError as e:
            self.assertIn(e.code, (400, 404))


# ── validate_skill_names unit tests ──────────────────────────────────────────

class TestValidateSkillNames(unittest.TestCase):

    def test_valid_single_name(self):
        ok, _ = validate_skill_names(['git-commit'])
        self.assertTrue(ok)

    def test_valid_multiple_names(self):
        ok, _ = validate_skill_names(['git-commit', 'ts-dev', 'java-code-review'])
        self.assertTrue(ok)

    def test_empty_list_invalid(self):
        ok, err = validate_skill_names([])
        self.assertFalse(ok)
        self.assertIn('empty', err)

    def test_not_a_list_invalid(self):
        ok, err = validate_skill_names('git-commit')
        self.assertFalse(ok)

    def test_path_traversal_invalid(self):
        ok, _ = validate_skill_names(['../etc/passwd'])
        self.assertFalse(ok)

    def test_shell_metacharacter_invalid(self):
        ok, _ = validate_skill_names(['git; rm -rf /'])
        self.assertFalse(ok)

    def test_uppercase_invalid(self):
        ok, _ = validate_skill_names(['Git-Commit'])
        self.assertFalse(ok)

    def test_name_too_short_invalid(self):
        ok, _ = validate_skill_names(['a'])  # must have at least one hyphen segment
        self.assertFalse(ok)

    def test_name_with_valid_hyphens(self):
        ok, _ = validate_skill_names(['java-code-review'])
        self.assertTrue(ok)

    def test_name_starting_with_digit_invalid(self):
        ok, _ = validate_skill_names(['1git-commit'])
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()
