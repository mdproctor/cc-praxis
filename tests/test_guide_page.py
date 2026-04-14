#!/usr/bin/env python3
"""
Structural tests for docs/guide.html.

Unit tests: file exists, frontmatter, nav link.
Integration tests: all 12 sections present, sidebar steps match sections,
  prompt blocks, install callouts, what-it-does boxes, no placeholder text.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GUIDE_PATH = REPO_ROOT / 'docs' / 'guide.html'
DEFAULT_LAYOUT = REPO_ROOT / 'docs' / '_layouts' / 'default.html'

SECTION_COUNT = 12

SECTION_TITLES = [
    'CLAUDE.md Setup',
    'Workspace Setup',
    'Java Development',
    'Code Review',
    'Smart Commits',
    'Brainstorming',
    'Ideas',
    'Issues',
    'Design Documentation',
    'Closing an Epic',
    'Session Handover',
    'Project Diary',
]


def load_guide() -> str:
    return GUIDE_PATH.read_text(encoding='utf-8')


class TestGuideExists(unittest.TestCase):
    """Unit: file exists and has correct Jekyll setup."""

    def test_guide_file_exists(self):
        self.assertTrue(GUIDE_PATH.exists(), 'docs/guide.html does not exist')

    def test_guide_has_jekyll_frontmatter(self):
        content = load_guide()
        self.assertTrue(content.startswith('---'), 'guide.html must start with YAML frontmatter')

    def test_guide_has_correct_layout(self):
        content = load_guide()
        self.assertIn('layout: default', content)

    def test_guide_has_correct_permalink(self):
        content = load_guide()
        self.assertIn('permalink: /guide/', content)

    def test_guide_has_correct_title(self):
        content = load_guide()
        self.assertIn('title:', content)
        self.assertIn('Getting Started', content)


class TestNavLink(unittest.TestCase):
    """Unit: default.html nav includes Guide link."""

    def test_default_layout_has_guide_link(self):
        content = DEFAULT_LAYOUT.read_text(encoding='utf-8')
        self.assertIn('/guide/', content, "default.html nav must link to /guide/")

    def test_guide_nav_label(self):
        content = DEFAULT_LAYOUT.read_text(encoding='utf-8')
        self.assertIn('Guide', content, "nav must show 'Guide' label")

    def test_guide_active_state_logic(self):
        content = DEFAULT_LAYOUT.read_text(encoding='utf-8')
        self.assertIn("'/guide/'", content, "guide link must have active-state logic")


class TestSectionStructure(unittest.TestCase):
    """Integration: all 12 sections present with correct IDs."""

    def setUp(self):
        self.content = load_guide()

    def test_has_twelve_sections(self):
        count = len(re.findall(r'id="java-section-\d+"', self.content))
        self.assertEqual(count, SECTION_COUNT,
                         f'Expected {SECTION_COUNT} section IDs, found {count}')

    def test_all_section_ids_sequential(self):
        for n in range(1, SECTION_COUNT + 1):
            self.assertIn(f'id="java-section-{n}"', self.content,
                          f'Missing id="java-section-{n}"')

    def test_all_data_section_attributes(self):
        for n in range(1, SECTION_COUNT + 1):
            self.assertIn(f'data-section="{n}"', self.content,
                          f'Missing data-section="{n}"')

    def test_sidebar_has_twelve_steps(self):
        count = len(re.findall(r'data-step="\d+"', self.content))
        self.assertEqual(count, SECTION_COUNT,
                         f'Sidebar needs {SECTION_COUNT} data-step entries, found {count}')

    def test_sidebar_steps_are_sequential(self):
        for n in range(1, SECTION_COUNT + 1):
            self.assertIn(f'data-step="{n}"', self.content,
                          f'Missing sidebar data-step="{n}"')

    def test_section_titles_present(self):
        for title in SECTION_TITLES:
            self.assertIn(title, self.content,
                          f'Expected section title not found: {title!r}')


class TestSectionContent(unittest.TestCase):
    """Integration: each section has required content blocks."""

    def setUp(self):
        self.content = load_guide()

    def test_twelve_what_it_does_boxes(self):
        count = self.content.count('what-it-does')
        self.assertEqual(count, SECTION_COUNT,
                         f'Expected {SECTION_COUNT} what-it-does boxes, found {count}')

    def test_twelve_prompt_blocks(self):
        count = self.content.count('prompt-block')
        self.assertEqual(count, SECTION_COUNT,
                         f'Expected {SECTION_COUNT} prompt-block elements, found {count}')

    def test_ten_install_callouts(self):
        count = self.content.count('install-callout')
        self.assertEqual(count, 10,
                         f'Expected 10 install-callout boxes (sections 3-12), found {count}')

    def test_section_next_links(self):
        # 11 sections have "Next →" links; the last section (12) has a completion message instead
        count = self.content.count('section-next')
        self.assertGreaterEqual(count, 11,
                                f'Expected at least 11 section-next links (last section omits it), found {count}')

    def test_no_placeholder_text(self):
        for placeholder in ('TBD', 'TODO', 'Lorem ipsum', 'placeholder'):
            self.assertNotIn(placeholder, self.content,
                             f'Found placeholder text {placeholder!r} in guide')

    def test_all_prompts_are_non_empty(self):
        blocks = re.findall(
            r'class="[^"]*prompt-block[^"]*"[^>]*>(.*?)</div>',
            self.content,
            re.DOTALL,
        )
        for i, block in enumerate(blocks, 1):
            self.assertGreater(len(block.strip()), 10,
                               f'Prompt block {i} appears empty')


class TestJavaScript(unittest.TestCase):
    """Unit: guide JS components are present."""

    def setUp(self):
        self.content = load_guide()

    def test_intersection_observer_present(self):
        self.assertIn('IntersectionObserver', self.content,
                      'Guide must use IntersectionObserver for scroll tracking')

    def test_progress_bar_element_present(self):
        self.assertIn('guide-progress-fill', self.content)

    def test_active_class_logic_present(self):
        self.assertIn("classList.add('active'", self.content,
                      "JS must call classList.add('active') for scroll tracking")

    def test_done_class_logic_present(self):
        self.assertIn("classList.add('done'", self.content,
                      "JS must call classList.add('done') for completed steps")


class TestTabStructure(unittest.TestCase):
    """Integration: guide has three language tabs."""

    def setUp(self):
        self.content = load_guide()

    def test_tab_bar_present(self):
        self.assertIn('guide-tab-bar', self.content)

    def test_three_language_tabs(self):
        for lang in ('java', 'typescript', 'python'):
            self.assertIn(f'data-lang="{lang}"', self.content,
                          f'Missing tab for {lang}')

    def test_three_panes(self):
        for lang in ('java', 'typescript', 'python'):
            self.assertIn(f'id="pane-{lang}"', self.content,
                          f'Missing pane for {lang}')

    def test_hash_routing_js_present(self):
        self.assertIn('hashchange', self.content)
        self.assertIn('getLang', self.content)

    def test_java_pane_is_default(self):
        import re
        java_pane = re.search(r'id="pane-java"[^>]*>', self.content)
        self.assertIsNotNone(java_pane)
        self.assertNotIn('display:none', java_pane.group(0))

    def test_typescript_pane_hidden_by_default(self):
        import re
        ts_pane = re.search(r'id="pane-typescript"[^>]*>', self.content)
        self.assertIsNotNone(ts_pane)
        self.assertIn('display:none', ts_pane.group(0))

    def test_python_pane_hidden_by_default(self):
        import re
        py_pane = re.search(r'id="pane-python"[^>]*>', self.content)
        self.assertIsNotNone(py_pane)
        self.assertIn('display:none', py_pane.group(0))
