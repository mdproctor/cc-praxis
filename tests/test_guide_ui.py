#!/usr/bin/env python3
"""
Playwright end-to-end tests for docs/guide.html.

Serves the raw guide.html (with frontmatter stripped) via Python HTTP server.
Tests sidebar scroll tracking, progress bar advancement, checkmarks on
completed steps, and prompt block visibility.

Run:
    python3 -m pytest tests/test_guide_ui.py -v
"""

import http.server
import re
import sys
import threading
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GUIDE_PATH = REPO_ROOT / 'docs' / 'guide.html'

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

SECTION_COUNT = 12


def _strip_frontmatter(html: str) -> str:
    """Remove Jekyll frontmatter (--- ... ---) and wrap in minimal HTML page."""
    if html.startswith('---'):
        end = html.index('---', 3)
        html = html[end + 3:].lstrip('\n')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Getting Started</title>
<style>
  body {{ font-family: sans-serif; margin: 0; padding: 0; background: #f3f4f6; }}
  .guide-section {{ min-height: 120vh; }}
</style>
</head>
<body>
{html}
</body>
</html>"""


class _GuideHandler(http.server.BaseHTTPRequestHandler):
    """Serves the preprocessed guide HTML."""
    _content: bytes = b''

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(_GuideHandler._content)))
        self.end_headers()
        self.wfile.write(_GuideHandler._content)

    def log_message(self, *args):
        pass  # Suppress request logging


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, 'playwright not installed')
class TestGuideScrollBehavior(unittest.TestCase):
    """E2E: sidebar active state, progress bar, and checkmarks on scroll."""

    @classmethod
    def setUpClass(cls):
        raw = GUIDE_PATH.read_text(encoding='utf-8')
        _GuideHandler._content = _strip_frontmatter(raw).encode('utf-8')

        cls._server = http.server.HTTPServer(('127.0.0.1', 0), _GuideHandler)
        cls._port = cls._server.server_address[1]
        cls._base_url = f'http://127.0.0.1:{cls._port}'
        cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
        cls._thread.start()

        cls._pw = sync_playwright().start()
        cls._browser = cls._pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls._browser.close()
        cls._pw.stop()
        cls._server.shutdown()

    def setUp(self):
        self.page = self._browser.new_page(viewport={'width': 1280, 'height': 800})
        self.page.goto(self._base_url, wait_until='domcontentloaded')
        self.page.wait_for_timeout(300)

    def tearDown(self):
        self.page.close()

    # ── Happy path: initial state ─────────────────────────────────────────────

    def test_page_loads(self):
        title = self.page.title()
        self.assertIn('Getting Started', title)

    def test_sidebar_renders_twelve_steps(self):
        steps = self.page.query_selector_all('#sidebar-java .guide-step')
        self.assertEqual(len(steps), SECTION_COUNT,
                         f'Expected {SECTION_COUNT} sidebar steps')

    def test_first_step_active_on_load(self):
        first_step = self.page.query_selector('#sidebar-java [data-step="1"]')
        self.assertIsNotNone(first_step)
        classes = first_step.get_attribute('class')
        self.assertIn('active', classes,
                      'First step should be active on page load')

    def test_progress_bar_visible(self):
        fill = self.page.query_selector('#guide-progress')
        self.assertIsNotNone(fill, 'Element #guide-progress must exist')
        width = fill.evaluate('el => el.style.width')
        self.assertTrue(len(width) > 0 and width != '0%',
                        f'Progress bar should have non-zero width, got: {width!r}')

    def test_twelve_prompt_blocks_visible(self):
        blocks = self.page.query_selector_all('#pane-java .prompt-block')
        self.assertEqual(len(blocks), SECTION_COUNT,
                         f'Expected {SECTION_COUNT} prompt blocks, found {len(blocks)}')

    def test_ten_install_callouts_visible(self):
        callouts = self.page.query_selector_all('#pane-java .install-callout')
        self.assertEqual(len(callouts), 10,
                         f'Expected 10 install callouts, found {len(callouts)}')

    # ── Happy path: scroll to section 3 ──────────────────────────────────────

    def test_scroll_to_section_3_activates_step_3(self):
        self.page.evaluate(
            "document.querySelector('#java-section-3').scrollIntoView({behavior: 'instant'})"
        )
        self.page.wait_for_timeout(500)

        step3 = self.page.query_selector('#sidebar-java [data-step="3"]')
        classes = step3.get_attribute('class')
        self.assertIn('active', classes,
                      'Step 3 should be active after scrolling to section 3')

    def test_scroll_to_section_3_marks_steps_1_2_done(self):
        self.page.evaluate(
            "document.querySelector('#java-section-3').scrollIntoView({behavior: 'instant'})"
        )
        self.page.wait_for_timeout(500)

        for step_n in (1, 2):
            step = self.page.query_selector(f'#sidebar-java [data-step="{step_n}"]')
            classes = step.get_attribute('class')
            self.assertIn('done', classes,
                          f'Step {step_n} should be "done" after scrolling past it')

    def test_scroll_to_section_3_shows_checkmarks_on_done_steps(self):
        self.page.evaluate(
            "document.querySelector('#java-section-3').scrollIntoView({behavior: 'instant'})"
        )
        self.page.wait_for_timeout(500)

        for step_n in (1, 2):
            circle = self.page.query_selector(f'#sidebar-java [data-step="{step_n}"] .guide-step-circle')
            text = circle.inner_text().strip()
            self.assertEqual(text, '✓',
                             f'Done step {step_n} circle should show ✓, got {text!r}')

    def test_scroll_to_section_3_advances_progress_bar(self):
        initial_width = self.page.evaluate(
            "parseFloat(document.getElementById('guide-progress').style.width) || 0"
        )
        self.page.evaluate(
            "document.querySelector('#java-section-3').scrollIntoView({behavior: 'instant'})"
        )
        self.page.wait_for_timeout(500)

        new_width = self.page.evaluate(
            "parseFloat(document.getElementById('guide-progress').style.width)"
        )
        self.assertGreater(new_width, initial_width,
                           f'Progress bar should advance: {initial_width}% → {new_width}%')

    # ── Happy path: scroll to last section ───────────────────────────────────

    def test_scroll_to_section_12_activates_step_12(self):
        self.page.evaluate(
            "document.querySelector('#java-section-12').scrollIntoView({behavior: 'instant'})"
        )
        self.page.wait_for_timeout(600)

        step12 = self.page.query_selector('#sidebar-java [data-step="12"]')
        classes = step12.get_attribute('class')
        self.assertIn('active', classes, 'Step 12 should be active at last section')

    def test_scroll_to_section_12_marks_prior_steps_done(self):
        self.page.evaluate(
            "document.querySelector('#java-section-12').scrollIntoView({behavior: 'instant'})"
        )
        self.page.wait_for_timeout(600)

        for step_n in range(1, 12):
            step = self.page.query_selector(f'#sidebar-java [data-step="{step_n}"]')
            classes = step.get_attribute('class')
            self.assertIn('done', classes,
                          f'Step {step_n} should be done when at section 12')

    def test_progress_bar_near_full_at_last_section(self):
        self.page.evaluate(
            "document.querySelector('#java-section-12').scrollIntoView({behavior: 'instant'})"
        )
        self.page.wait_for_timeout(600)

        width = self.page.evaluate(
            "parseFloat(document.getElementById('guide-progress').style.width)"
        )
        self.assertGreater(width, 90,
                           f'Progress should be >90% at last section, got {width}%')

    # ── Happy path: sidebar nav click ────────────────────────────────────────

    def test_clicking_step_5_scrolls_to_section_5(self):
        step5 = self.page.query_selector('#sidebar-java [data-step="5"]')
        step5.click()
        self.page.wait_for_timeout(600)

        is_visible = self.page.evaluate("""
            () => {
                const el = document.querySelector('#java-section-5');
                const rect = el.getBoundingClientRect();
                return rect.top < window.innerHeight && rect.bottom > 0;
            }
        """)
        self.assertTrue(is_visible,
                        'Section 5 should be in viewport after clicking step 5')

    # ── Happy path: content visibility ───────────────────────────────────────

    def test_all_what_it_does_boxes_visible(self):
        boxes = self.page.query_selector_all('#pane-java .what-it-does')
        self.assertEqual(len(boxes), SECTION_COUNT)
        for i, box in enumerate(boxes, 1):
            self.assertTrue(box.is_visible(),
                            f'What-it-does box {i} should be visible')

    def test_preamble_visible(self):
        preamble = self.page.query_selector('#pane-java .guide-intro, #pane-java .guide-preamble')
        self.assertIsNotNone(preamble, 'Prerequisites preamble must exist')
        self.assertTrue(preamble.is_visible())

    def test_step_1_subtitle_visible_on_load(self):
        sub = self.page.query_selector('#sidebar-java [data-step="1"] .guide-step-sub')
        self.assertIsNotNone(sub, 'Step 1 must have a subtitle element')
        self.assertTrue(sub.is_visible(),
                        'Step 1 subtitle should be visible on load (step 1 is active)')

    def test_step_2_subtitle_hidden_on_load(self):
        sub = self.page.query_selector('#sidebar-java [data-step="2"] .guide-step-sub')
        self.assertIsNotNone(sub, 'Step 2 must have a subtitle element')
        self.assertFalse(sub.is_visible(),
                         'Step 2 subtitle should be hidden on load (not active)')


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, 'playwright not installed')
class TestGuideTabSwitching(unittest.TestCase):
    """E2E: tab bar switches panes, resets sidebar, updates hash."""

    @classmethod
    def setUpClass(cls):
        raw = GUIDE_PATH.read_text(encoding='utf-8')
        _GuideHandler._content = _strip_frontmatter(raw).encode('utf-8')
        cls._server = http.server.HTTPServer(('127.0.0.1', 0), _GuideHandler)
        cls._port = cls._server.server_address[1]
        cls._base_url = f'http://127.0.0.1:{cls._port}'
        cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
        cls._thread.start()
        cls._pw = sync_playwright().start()
        cls._browser = cls._pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls._browser.close()
        cls._pw.stop()
        cls._server.shutdown()

    def setUp(self):
        self.page = self._browser.new_page(viewport={'width': 1280, 'height': 800})
        self.page.goto(self._base_url, wait_until='domcontentloaded')
        self.page.wait_for_timeout(400)

    def tearDown(self):
        self.page.close()

    def test_three_tabs_visible(self):
        tabs = self.page.query_selector_all('.guide-tab')
        self.assertEqual(len(tabs), 3, 'Expected 3 language tabs')

    def test_java_tab_active_on_load(self):
        java_tab = self.page.query_selector('[data-lang="java"]')
        self.assertIn('active', java_tab.get_attribute('class'))

    def test_java_pane_visible_on_load(self):
        self.assertTrue(self.page.query_selector('#pane-java').is_visible())

    def test_typescript_pane_hidden_on_load(self):
        self.assertFalse(self.page.query_selector('#pane-typescript').is_visible())

    def test_python_pane_hidden_on_load(self):
        self.assertFalse(self.page.query_selector('#pane-python').is_visible())

    def test_click_typescript_tab_shows_ts_pane(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(300)
        self.assertTrue(self.page.query_selector('#pane-typescript').is_visible())

    def test_click_typescript_tab_hides_java_pane(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(300)
        self.assertFalse(self.page.query_selector('#pane-java').is_visible())

    def test_click_typescript_tab_marks_ts_active(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(300)
        ts_tab = self.page.query_selector('[data-lang="typescript"]')
        self.assertIn('active', ts_tab.get_attribute('class'))

    def test_click_typescript_tab_updates_hash(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(300)
        self.assertIn('#typescript', self.page.url)

    def test_click_python_tab_shows_py_pane(self):
        self.page.click('[data-lang="python"]')
        self.page.wait_for_timeout(300)
        self.assertTrue(self.page.query_selector('#pane-python').is_visible())

    def test_click_python_tab_updates_hash(self):
        self.page.click('[data-lang="python"]')
        self.page.wait_for_timeout(300)
        self.assertIn('#python', self.page.url)

    def test_switch_back_to_java_from_typescript(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(300)
        self.page.click('[data-lang="java"]')
        self.page.wait_for_timeout(300)
        self.assertTrue(self.page.query_selector('#pane-java').is_visible())
        self.assertFalse(self.page.query_selector('#pane-typescript').is_visible())

    def test_direct_link_to_typescript_via_hash(self):
        self.page.goto(self._base_url + '#typescript', wait_until='domcontentloaded')
        self.page.wait_for_timeout(500)
        self.assertTrue(self.page.query_selector('#pane-typescript').is_visible())
        self.assertFalse(self.page.query_selector('#pane-java').is_visible())

    def test_direct_link_to_python_via_hash(self):
        self.page.goto(self._base_url + '#python', wait_until='domcontentloaded')
        self.page.wait_for_timeout(500)
        self.assertTrue(self.page.query_selector('#pane-python').is_visible())

    def test_typescript_sidebar_has_twelve_steps(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(300)
        steps = self.page.query_selector_all('#sidebar-typescript .guide-step')
        self.assertEqual(len(steps), 12, 'TypeScript sidebar must have 12 steps')

    def test_python_sidebar_has_twelve_steps(self):
        self.page.click('[data-lang="python"]')
        self.page.wait_for_timeout(300)
        steps = self.page.query_selector_all('#sidebar-python .guide-step')
        self.assertEqual(len(steps), 12, 'Python sidebar must have 12 steps')
