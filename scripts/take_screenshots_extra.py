#!/usr/bin/env python3
"""
Extra screenshots for underdocumented features in SKILL-MANAGER.md.
"""

import sys, threading
from http.server import HTTPServer
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import web_installer as wi
from web_installer import InstallerHandler

OUT = ROOT / 'docs' / 'images'
OUT.mkdir(exist_ok=True)

server = HTTPServer(('127.0.0.1', 0), InstallerHandler)
PORT = server.server_address[1]
URL  = f'http://127.0.0.1:{PORT}'
threading.Thread(target=server.serve_forever, daemon=True).start()
print(f'Server on :{PORT}')

PARTIAL_INSTALLED = [
    'git-commit', 'update-claude-md', 'adr', 'project-health', 'project-refine',
    'java-dev', 'java-code-review', 'java-security-audit', 'java-git-commit', 'maven-dependency-update',
    'ts-dev', 'ts-code-review', 'ts-security-audit', 'npm-dependency-update', 'ts-project-health',
    'issue-workflow',
]
MOCK_VERSIONS  = {'java-dev': '1.0.0', 'ts-dev': '1.0.0'}
MOCK_AVAILABLE = {'java-dev': '1.0.1', 'ts-dev': '1.1.0'}

SET_STATE = f"""
    INSTALLED.clear();
    {PARTIAL_INSTALLED}.forEach(s => INSTALLED.add(s));
    Object.keys(VERSIONS).forEach(k => delete VERSIONS[k]);
    Object.assign(VERSIONS, {MOCK_VERSIONS});
    Object.assign(AVAILABLE, {MOCK_AVAILABLE});
    updateAllBadges();
    updateInstallSummary();
"""

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_page(viewport={'width': 1100, 'height': 800})
    page = ctx

    page.goto(URL)
    page.wait_for_load_state('networkidle')
    page.evaluate(SET_STATE)
    page.wait_for_timeout(300)

    # ── 1. Nudge box (first-time user guidance) ──────────────────────────
    print('Taking: nudge-box')
    page.evaluate("setView('install')")
    page.wait_for_timeout(300)
    # Show the nudge (it may be dismissed; reset it)
    page.evaluate("document.getElementById('nudge').style.display = 'flex'")
    page.wait_for_timeout(200)
    nudge = page.locator('#nudge')
    nudge.screenshot(path=str(OUT / 'nudge-box.png'))
    print('  ✓ nudge-box.png')

    # ── 2. Checking… loading state (sync bar before state loads) ─────────
    print('Taking: loading-state')
    page.evaluate("""
        const sub = document.getElementById('sync-bar-sub');
        if (sub) sub.textContent = 'Checking\u2026';
        const badge = document.getElementById('header-install-badge');
        if (badge) badge.style.display = 'none';
    """)
    page.wait_for_timeout(100)
    page.locator('.sync-bar').screenshot(path=str(OUT / 'loading-state.png'))
    print('  ✓ loading-state.png')
    # Restore
    page.evaluate(SET_STATE)
    page.wait_for_timeout(300)

    # ── 3. Success banner after install ──────────────────────────────────
    print('Taking: success-banner')
    page.evaluate("""
        showSuccessBanner('Skills installed — open a new Claude Code session to use them.');
    """)
    page.wait_for_timeout(200)
    page.locator('#success-banner').screenshot(path=str(OUT / 'success-banner.png'))
    print('  ✓ success-banner.png')
    page.evaluate("document.getElementById('success-banner').style.display = 'none'")

    # ── 4. Outdated skill row in Install tab ──────────────────────────────
    print('Taking: outdated-row')
    page.evaluate("BUNDLE_IDS.forEach(id => document.getElementById(id).classList.remove('open'))")
    page.evaluate("document.getElementById('b-java').classList.add('open')")
    page.wait_for_timeout(300)
    page.evaluate("document.getElementById('b-java').scrollIntoView()")
    page.wait_for_timeout(200)
    # Find the java-dev row and screenshot it + the one below for context
    java_dev_row = page.locator('.skill-row').filter(has=page.locator('.skill-name:text-is("java-dev")')).first
    java_dev_row.screenshot(path=str(OUT / 'outdated-row.png'))
    print('  ✓ outdated-row.png')

    # ── 5. Browse card with Install button visible ────────────────────────
    print('Taking: browse-card-with-install')
    page.evaluate("setView('browse')")
    page.wait_for_timeout(300)
    # Open Python bundle so we can see a not-installed skill with Install button
    page.evaluate("document.getElementById('b-python').classList.add('open')")
    page.wait_for_timeout(200)
    page.evaluate("document.getElementById('ov-python-dev').scrollIntoView()")
    page.wait_for_timeout(200)
    page.locator('#ov-python-dev').screenshot(path=str(OUT / 'browse-card-with-install.png'))
    print('  ✓ browse-card-with-install.png')

    # ── 6. Chain graph grandchildren expanded ────────────────────────────
    print('Taking: chain-grandchildren')
    # git-commit has java-git-commit as a child, and java-git-commit has children
    page.evaluate("document.getElementById('b-core').classList.add('open')")
    page.wait_for_timeout(200)
    page.evaluate("document.getElementById('ov-git-commit').scrollIntoView()")
    page.wait_for_timeout(200)
    page.locator('#chain-btn-git-commit').click()
    page.wait_for_timeout(600)
    # Expand grandchildren of java-git-commit (first gc toggle)
    gc_toggles = page.locator('.chain-gc-toggle')
    count = gc_toggles.count()
    if count > 0:
        gc_toggles.first.click()
        page.wait_for_timeout(400)
    page.locator('#ov-git-commit').screenshot(path=str(OUT / 'chain-grandchildren.png'))
    print('  ✓ chain-grandchildren.png')
    page.locator('.chain-row-close').first.click()
    page.wait_for_timeout(200)

    # ── 7. Chain graph: click to navigate (show java-code-review chain) ──
    print('Taking: chain-navigate')
    # Open core bundle, click chain on git-commit, then click java-git-commit child
    page.evaluate("document.getElementById('ov-git-commit').scrollIntoView()")
    page.wait_for_timeout(200)
    page.locator('#chain-btn-git-commit').click()
    page.wait_for_timeout(600)
    # Click the java-git-commit child link to navigate
    java_link = page.locator('.chain-name.clickable').filter(has_text='java-git-commit').first
    if java_link.count() > 0:
        java_link.click()
        page.wait_for_timeout(700)
        # Screenshot the newly opened chain for java-git-commit
        java_card = page.locator('#ov-java-git-commit')
        java_card.screenshot(path=str(OUT / 'chain-navigate.png'))
        print('  ✓ chain-navigate.png')
        page.locator('.chain-row-close').first.click()
        page.wait_for_timeout(200)
    else:
        print('  ⚠ chain-navigate: java-git-commit link not found, skipping')

    # ── 8. Smart uninstall modal (partial bundle → shows only installed) ──
    print('Taking: modal-smart-uninstall')
    page.evaluate("setView('install')")
    page.wait_for_timeout(300)
    # Java is partial (5 of 10 installed). Click Uninstall on java bundle header.
    # It should show only the 5 installed, not all 10.
    page.evaluate("openModal('uninstall-java')")
    page.wait_for_timeout(400)
    modal = page.locator('#overlay .modal')
    modal.screenshot(path=str(OUT / 'modal-smart-uninstall.png'))
    print('  ✓ modal-smart-uninstall.png')
    page.evaluate("closeModal()")
    page.wait_for_timeout(200)

    # ── 9. Install tab — install-only-missing (partial Java, Install modal) ─
    print('Taking: modal-smart-install')
    page.evaluate("openModal('install-java')")
    page.wait_for_timeout(400)
    modal = page.locator('#overlay .modal')
    modal.screenshot(path=str(OUT / 'modal-smart-install.png'))
    print('  ✓ modal-smart-install.png')
    page.evaluate("closeModal()")
    page.wait_for_timeout(200)

    # ── 10. About tab — hero section ─────────────────────────────────────
    print('Taking: about-cta')
    page.evaluate("setView('about')")
    page.wait_for_timeout(300)
    # Scroll to the bottom CTA
    page.evaluate("document.getElementById('about-cta').scrollIntoView()")
    page.wait_for_timeout(300)
    page.locator('#about-cta').screenshot(path=str(OUT / 'about-cta.png'))
    print('  ✓ about-cta.png')

    browser.close()
    server.shutdown()

print(f'\nExtra screenshots saved to docs/images/')
