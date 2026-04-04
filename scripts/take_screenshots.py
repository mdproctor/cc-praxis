#!/usr/bin/env python3
"""
Take UI screenshots for SKILL-MANAGER.md using Playwright.
Saves cropped PNGs to docs/images/.

Usage: python3 scripts/take_screenshots.py
"""

import sys
import threading
import time
from http.server import HTTPServer
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import web_installer as wi
from web_installer import InstallerHandler

OUT = ROOT / 'docs' / 'images'
OUT.mkdir(exist_ok=True)

# ── Server ──────────────────────────────────────────────────────────────

server = HTTPServer(('127.0.0.1', 0), InstallerHandler)
PORT = server.server_address[1]
URL = f'http://127.0.0.1:{PORT}'
threading.Thread(target=server.serve_forever, daemon=True).start()
print(f'Server on :{PORT}')

# ── Playwright ───────────────────────────────────────────────────────────

from playwright.sync_api import sync_playwright

# Partial install state — looks like a realistic new user with some things installed
PARTIAL_INSTALLED = [
    'git-commit', 'update-claude-md', 'adr', 'project-health', 'project-refine',  # Core full
    # Principles: nothing
    'java-dev', 'java-code-review', 'java-security-audit', 'java-git-commit', 'maven-dependency-update',  # Java partial (5/10)
    'ts-dev', 'ts-code-review', 'ts-security-audit', 'npm-dependency-update', 'ts-project-health',  # TypeScript full
    # Python: nothing
    'issue-workflow',  # one extra
]

# Mock versions for outdated indicator
MOCK_VERSIONS = {
    'java-dev': '1.0.0',
    'ts-dev': '1.0.0',
}
MOCK_AVAILABLE = {
    'java-dev': '1.0.1',
    'ts-dev': '1.1.0',
}

INJECT_PARTIAL = f"""
    INSTALLED.clear();
    {PARTIAL_INSTALLED}.forEach(s => INSTALLED.add(s));
    Object.assign(VERSIONS, {MOCK_VERSIONS});
    Object.assign(AVAILABLE, {MOCK_AVAILABLE});
    updateAllBadges();
    updateInstallSummary();
    if (typeof updateBundleStates === 'function') {{
        fetch('/api/state').then(r => r.json()).then(d => {{
            if (d.bundles) updateBundleStates(d.bundles);
        }});
    }}
"""

# Inject state that looks fully loaded
INJECT_STATE_CALL = """
    INSTALLED.clear();
    %s.forEach(s => INSTALLED.add(s));
    Object.keys(VERSIONS).forEach(k => delete VERSIONS[k]);
    Object.assign(VERSIONS, %s);
    Object.assign(AVAILABLE, %s);
    updateAllBadges();
    updateInstallSummary();
""" % (
    str(PARTIAL_INSTALLED),
    str(MOCK_VERSIONS),
    str(MOCK_AVAILABLE),
)


def ss(page, name, locator=None, padding=0):
    """Take a screenshot, optionally of a specific element."""
    path = str(OUT / f'{name}.png')
    if locator:
        el = page.locator(locator).first
        el.screenshot(path=path)
    else:
        page.screenshot(path=path)
    print(f'  ✓ {name}.png')


def open_install_expand_all(page):
    """Open Install tab and expand all bundles."""
    page.click('#tab-install')
    page.wait_for_timeout(400)
    page.evaluate("BUNDLE_IDS.forEach(id => document.getElementById(id).classList.add('open'))")
    page.wait_for_timeout(200)


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 1100, 'height': 800})
    page = ctx.new_page()

    page.goto(URL)
    page.wait_for_load_state('networkidle')

    # ── 1. Header (About tab active) ─────────────────────────────────────
    print('Taking: header')
    page.evaluate("setView('about')")
    page.wait_for_timeout(300)
    ss(page, 'header', '.header')

    # ── 2. Install tab header with controls ──────────────────────────────
    print('Taking: header-install')
    page.evaluate("setView('install')")
    page.wait_for_timeout(300)
    ss(page, 'header-install', '.header')

    # ── 3. Browse — nav bar with search ──────────────────────────────────
    print('Taking: nav-bar')
    page.evaluate("setView('browse')")
    page.wait_for_timeout(300)
    ss(page, 'nav-bar', '.nav-bar')

    # ── 4. Browse — a skill card (java-dev) ──────────────────────────────
    print('Taking: browse-skill-card')
    page.evaluate(INJECT_STATE_CALL)
    page.wait_for_timeout(300)
    # Expand the Java bundle
    page.evaluate("document.getElementById('b-java').classList.add('open')")
    page.wait_for_timeout(200)
    ss(page, 'browse-skill-card', '#ov-java-dev')

    # ── 5. Browse — git-commit card (good chain example, root skill) ──────
    print('Taking: browse-git-commit-card')
    page.evaluate("document.getElementById('b-core').classList.add('open')")
    page.wait_for_timeout(200)
    ss(page, 'browse-git-commit-card', '#ov-git-commit')

    # ── 6. Chain graph — open java-git-commit chain ───────────────────────
    print('Taking: chain-graph')
    # Navigate to browse, inject state, open Java bundle, click Chain on java-git-commit
    page.evaluate("document.getElementById('b-java').classList.add('open')")
    page.wait_for_timeout(200)
    chain_btn = page.locator('#chain-btn-java-git-commit')
    chain_btn.click()
    page.wait_for_timeout(500)
    # Screenshot the skill card + the chain row together
    card = page.locator('#ov-java-git-commit')
    card.screenshot(path=str(OUT / 'chain-graph.png'))
    print('  ✓ chain-graph.png')
    # Close the chain
    page.locator('.chain-row-close').first.click()
    page.wait_for_timeout(200)

    # ── 7. Chain graph — git-commit (shows root ⊙ omitted, children) ─────
    print('Taking: chain-graph-git-commit')
    page.evaluate("document.getElementById('b-core').classList.add('open')")
    page.wait_for_timeout(200)
    page.locator('#chain-btn-git-commit').click()
    page.wait_for_timeout(500)
    page.locator('#ov-git-commit').screenshot(path=str(OUT / 'chain-graph-git-commit.png'))
    print('  ✓ chain-graph-git-commit.png')
    page.locator('.chain-row-close').first.click()
    page.wait_for_timeout(200)

    # ── 8. Install tab — sync bar ─────────────────────────────────────────
    print('Taking: install-sync-bar')
    open_install_expand_all(page)
    page.evaluate(INJECT_STATE_CALL)
    page.wait_for_timeout(400)
    ss(page, 'install-sync-bar', '.sync-bar')

    # ── 9. Install tab — bundle headers (collapsed, showing states) ───────
    print('Taking: install-bundles-collapsed')
    page.evaluate("BUNDLE_IDS.forEach(id => document.getElementById(id).classList.remove('open'))")
    page.wait_for_timeout(200)
    # Screenshot the area from sync bar down through bundle list
    page.evaluate("""
        window.scrollTo(0, 0);
    """)
    page.wait_for_timeout(200)
    # Crop to just the bundles area
    container = page.locator('.container')
    # Take a screenshot of just the install view portion
    page.screenshot(path=str(OUT / 'install-bundles-collapsed.png'),
                    clip={'x': 0, 'y': 100, 'width': 1100, 'height': 520})
    print('  ✓ install-bundles-collapsed.png')

    # ── 10. Install tab — Java bundle expanded showing skill rows ─────────
    print('Taking: install-java-expanded')
    page.evaluate("document.getElementById('b-java').classList.add('open')")
    page.wait_for_timeout(300)
    page.evaluate("document.getElementById('b-java').scrollIntoView()")
    page.wait_for_timeout(200)
    java_bundle = page.locator('#b-java')
    java_bundle.screenshot(path=str(OUT / 'install-java-expanded.png'))
    print('  ✓ install-java-expanded.png')

    # ── 11. Install modal — bundle install ────────────────────────────────
    print('Taking: modal-install-bundle')
    # Click install on Python bundle (nothing installed)
    page.evaluate("BUNDLE_IDS.forEach(id => document.getElementById(id).classList.remove('open'))")
    page.wait_for_timeout(200)
    # Open the Python install modal
    page.evaluate("openModal('install-python')")
    page.wait_for_timeout(400)
    modal = page.locator('#overlay .modal')
    modal.screenshot(path=str(OUT / 'modal-install-bundle.png'))
    print('  ✓ modal-install-bundle.png')
    page.evaluate("closeModal()")
    page.wait_for_timeout(200)

    # ── 12. Install modal — single skill with dependency ──────────────────
    print('Taking: modal-install-skill-dep')
    # Install ts-code-review — has dependency on code-review-principles
    # First remove code-review-principles from installed set to trigger dep warning
    page.evaluate("""
        INSTALLED.delete('code-review-principles');
        updateAllBadges();
    """)
    page.wait_for_timeout(200)
    page.evaluate("openModal('install-skill', 'ts-code-review')")
    page.wait_for_timeout(400)
    modal = page.locator('#overlay .modal')
    modal.screenshot(path=str(OUT / 'modal-install-skill-dep.png'))
    print('  ✓ modal-install-skill-dep.png')
    page.evaluate("closeModal()")
    page.wait_for_timeout(200)
    # Restore state
    page.evaluate(INJECT_STATE_CALL)
    page.wait_for_timeout(200)

    # ── 13. Update modal ──────────────────────────────────────────────────
    print('Taking: modal-update')
    page.evaluate("openModal('update-all')")
    page.wait_for_timeout(400)
    update_modal = page.locator('#update-overlay .modal')
    update_modal.screenshot(path=str(OUT / 'modal-update.png'))
    print('  ✓ modal-update.png')
    page.evaluate("closeUpdateModal()")
    page.wait_for_timeout(200)

    # ── 14. Mode toggle ───────────────────────────────────────────────────
    print('Taking: mode-toggle')
    toggle = page.locator('.header-right')
    toggle.screenshot(path=str(OUT / 'mode-toggle.png'))
    print('  ✓ mode-toggle.png')

    # ── 15. Show Command modal ────────────────────────────────────────────
    print('Taking: modal-show-command')
    page.evaluate("autoExecute = false; document.getElementById('btn-manual').classList.add('active'); document.getElementById('btn-auto').classList.remove('active');")
    page.evaluate("openModal('install-python')")
    page.wait_for_timeout(400)
    modal = page.locator('#overlay .modal')
    modal.screenshot(path=str(OUT / 'modal-show-command.png'))
    print('  ✓ modal-show-command.png')
    page.evaluate("closeModal()")
    page.wait_for_timeout(200)
    page.evaluate("autoExecute = true; document.getElementById('btn-auto').classList.add('active'); document.getElementById('btn-manual').classList.remove('active');")

    # ── 16. Search filtering ──────────────────────────────────────────────
    print('Taking: search-filtered')
    page.evaluate("setView('browse')")
    page.wait_for_timeout(300)
    search = page.locator('#search-input')
    search.fill('security')
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / 'search-filtered.png'),
                    clip={'x': 0, 'y': 50, 'width': 1100, 'height': 550})
    print('  ✓ search-filtered.png')
    search.fill('')
    page.wait_for_timeout(200)

    # ── 17. About tab hero ────────────────────────────────────────────────
    print('Taking: about-hero')
    page.evaluate("setView('about')")
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / 'about-hero.png'),
                    clip={'x': 0, 'y': 52, 'width': 1100, 'height': 520})
    print('  ✓ about-hero.png')

    browser.close()
    server.shutdown()

print(f'\nAll screenshots saved to docs/images/')
