#!/usr/bin/env python3
"""
Web installer server for cc-praxis skills.

Serves the skill manager UI at http://localhost:8765 and provides
a local API for reading installation state and executing skill operations.

Usage:
    python3 scripts/web_installer.py [--port PORT] [--no-browser]

API endpoints:
    GET  /                  Serve docs/index.html
    GET  /api/state         Current installed skills and versions
    GET  /api/marketplace   Marketplace skill catalogue
    POST /api/install       Install skills  {"skills": ["git-commit", ...]}
    POST /api/uninstall     Uninstall skills {"skills": ["git-commit", ...]}
    POST /api/uninstall-all Uninstall all skills {}
    POST /api/update        Update all skills to latest {}

Version comparison rule:
    A SNAPSHOT version (e.g. "1.0.0-SNAPSHOT") is treated as older than its
    release counterpart ("1.0.0"). A skill with no plugin.json is not flagged
    as outdated — the version is simply unknown.
"""

import argparse
import json
import re
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Timer

SKILLS_ROOT = Path(__file__).parent.parent
import os as _os
SKILLS_DIR = Path(_os.environ.get('CLAUDE_SKILLS_DIR', str(Path.home() / '.claude' / 'skills')))
MARKETPLACE_PATH = SKILLS_ROOT / '.claude-plugin' / 'marketplace.json'
HTML_PATH = SKILLS_ROOT / 'docs' / 'index.html'

DEFAULT_PORT = 8765

# Allowlist: valid skill name pattern
_VALID_SKILL = re.compile(r'^[a-z][a-z0-9-]{1,39}$')


# ── Version comparison ────────────────────────────────────────────────────────

def _version_tuple(version: str) -> tuple:
    """
    Convert a version string to a comparable tuple.

    "1.0.0"          → (1, 0, 0, 1)   (1 = release)
    "1.0.0-SNAPSHOT" → (1, 0, 0, 0)   (0 = pre-release, older than release)
    """
    is_snapshot = 'SNAPSHOT' in version.upper()
    numeric_part = re.sub(r'[^0-9.]', '', version)
    parts = [int(x) for x in numeric_part.split('.') if x.isdigit()]
    # Pad to at least 3 components
    while len(parts) < 3:
        parts.append(0)
    # Append release flag: 0 = SNAPSHOT (pre-release), 1 = release
    parts.append(0 if is_snapshot else 1)
    return tuple(parts)


def is_outdated(installed_version: str, available_version: str) -> bool:
    """Return True if installed_version is older than available_version."""
    try:
        return _version_tuple(installed_version) < _version_tuple(available_version)
    except Exception:
        return False


# ── Skill state ───────────────────────────────────────────────────────────────

def read_installed_state() -> tuple[list, dict, list]:
    """
    Scan SKILLS_DIR and return (installed, versions, outdated).

    installed: sorted list of skill names with SKILL.md present
    versions:  {name: version_string} for skills with plugin.json
    outdated:  list of names where installed version < marketplace version
    """
    installed: list[str] = []
    versions: dict[str, str] = {}

    if SKILLS_DIR.exists():
        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if not skill_dir.is_dir():
                continue
            if not (skill_dir / 'SKILL.md').exists():
                continue
            name = skill_dir.name
            if not _VALID_SKILL.match(name):
                continue
            installed.append(name)
            plugin_file = skill_dir / 'plugin.json'
            if plugin_file.exists():
                try:
                    data = json.loads(plugin_file.read_text(encoding='utf-8'))
                    ver = data.get('version')
                    if ver:
                        versions[name] = str(ver)
                except (json.JSONDecodeError, OSError):
                    pass  # version unknown

    # Compute outdated list and bundle state against marketplace
    outdated: list[str] = []
    bundles: dict = {}
    try:
        marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding='utf-8'))
        avail_versions = {p['name']: p.get('version', '') for p in marketplace.get('plugins', [])}
        for name in installed:
            inst_ver = versions.get(name)
            avail_ver = avail_versions.get(name)
            if inst_ver and avail_ver and is_outdated(inst_ver, avail_ver):
                outdated.append(name)
        # Per-bundle installed count and state
        installed_set = set(installed)
        for bundle in marketplace.get('bundles', []):
            bname  = bundle['name']
            skills = bundle.get('skills', [])
            count  = sum(1 for s in skills if s in installed_set)
            total  = len(skills)
            if total == 0:
                state = 'empty'
            elif count == 0:
                state = 'empty'
            elif count == total:
                state = 'full'
            else:
                state = 'partial'
            bundles[bname] = {'installed': count, 'total': total, 'state': state, 'skills': skills}
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass  # best-effort

    return installed, versions, outdated, bundles


# ── Subprocess execution ──────────────────────────────────────────────────────

def _run(*args: str) -> tuple[bool, str]:
    """Run the claude-skill script. Returns (success, combined_output)."""
    cmd = [sys.executable, str(SKILLS_ROOT / 'scripts' / 'claude-skill')] + list(args)
    # Propagate CLAUDE_SKILLS_DIR so the subprocess targets the same directory
    # we're using (critical for tests that redirect to a temp directory).
    import os as _os
    env = _os.environ.copy()
    env['CLAUDE_SKILLS_DIR'] = str(SKILLS_DIR)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(SKILLS_ROOT),
            timeout=120,
            env=env,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, 'command timed out after 120s'
    except OSError as exc:
        return False, str(exc)


# ── Input validation ──────────────────────────────────────────────────────────

def validate_skill_names(names: object) -> tuple[bool, str]:
    """Validate a skill names list. Returns (ok, error_message)."""
    if not isinstance(names, list):
        return False, '"skills" must be an array'
    if not names:
        return False, '"skills" array must not be empty'
    for name in names:
        if not isinstance(name, str) or not _VALID_SKILL.match(name):
            return False, f'invalid skill name: {name!r}'
    return True, ''


# ── HTTP handler ──────────────────────────────────────────────────────────────

class InstallerHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            self._serve_file(HTML_PATH, 'text/html; charset=utf-8')
        elif path == '/api/state':
            self._handle_state()
        elif path == '/api/marketplace':
            self._handle_marketplace()
        else:
            self._send_json({'error': 'not found'}, 404)

    def do_POST(self) -> None:
        path = self.path.split('?')[0]
        if path == '/api/install':
            self._handle_install()
        elif path == '/api/uninstall':
            self._handle_uninstall()
        elif path == '/api/uninstall-all':
            self._handle_uninstall_all()
        elif path == '/api/update':
            self._handle_update()
        else:
            self._send_json({'error': 'not found'}, 404)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _read_json_body(self) -> dict:
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode('utf-8'))

    def _send_json(self, data: object, status: int = 200) -> None:
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', 'http://localhost')
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str) -> None:
        self._send_json({'ok': False, 'error': message}, status)

    def _serve_file(self, path: Path, content_type: str) -> None:
        try:
            content = path.read_bytes()
        except FileNotFoundError:
            self._send_json({'error': f'{path.name} not found'}, 404)
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    # ── route handlers ────────────────────────────────────────────────────────

    def _handle_state(self) -> None:
        installed, versions, outdated, bundles = read_installed_state()
        self._send_json({
            'installed': installed,
            'versions': versions,
            'outdated': outdated,
            'bundles': bundles,
        })

    def _handle_marketplace(self) -> None:
        try:
            data = json.loads(MARKETPLACE_PATH.read_text(encoding='utf-8'))
            self._send_json(data)
        except FileNotFoundError:
            self._send_error(500, 'marketplace.json not found')
        except json.JSONDecodeError:
            self._send_error(500, 'marketplace.json is malformed')

    def _handle_install(self) -> None:
        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, ValueError):
            return self._send_error(400, 'invalid JSON body')

        if 'skills' not in body:
            return self._send_error(400, 'missing "skills" key')

        ok, err = validate_skill_names(body['skills'])
        if not ok:
            return self._send_error(400, err)

        success, output = _run('sync-local', '--skills', *body['skills'], '-y')
        if success:
            self._send_json({'ok': True, 'output': output})
        else:
            self._send_error(500, output)

    def _handle_uninstall(self) -> None:
        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, ValueError):
            return self._send_error(400, 'invalid JSON body')

        if 'skills' not in body:
            return self._send_error(400, 'missing "skills" key')

        ok, err = validate_skill_names(body['skills'])
        if not ok:
            return self._send_error(400, err)

        outputs = []
        for skill in body['skills']:
            success, output = _run('uninstall', skill)
            outputs.append(output)
            if not success:
                return self._send_error(500, output)
        self._send_json({'ok': True, 'output': '\n'.join(outputs)})

    def _handle_uninstall_all(self) -> None:
        success, output = _run('uninstall-all', '-y')
        if success:
            self._send_json({'ok': True, 'output': output})
        else:
            self._send_error(500, output)

    def _handle_update(self) -> None:
        success, output = _run('sync-local', '--all', '-y')
        if success:
            self._send_json({'ok': True, 'output': output})
        else:
            self._send_error(500, output)

    def log_message(self, fmt: str, *args) -> None:
        pass  # suppress per-request log noise


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description='cc-praxis web installer — skill manager UI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help=f'Port to listen on (default: {DEFAULT_PORT})')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not open browser automatically')
    args = parser.parse_args()

    server = HTTPServer(('127.0.0.1', args.port), InstallerHandler)
    url = f'http://localhost:{args.port}'
    print(f'cc-praxis installer  →  {url}')
    print('Press Ctrl+C to stop.\n')

    if not args.no_browser:
        Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')


if __name__ == '__main__':
    main()
