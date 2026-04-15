# Getting Started Guide — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 12-section Java developer getting-started guide at `docs/guide.html` with sticky numbered sidebar, scroll-tracking active state, progress bar, and a full test suite (structural + Playwright e2e).

**Architecture:** Jekyll page at permalink `/guide/` using the existing `default` layout, with all CSS and JS self-contained. Structural tests parse the raw HTML file. Playwright e2e tests strip Jekyll frontmatter and serve the guide via Python HTTP server for real browser interaction testing.

**Tech Stack:** Jekyll (HTML page), Python pytest (structural tests), Playwright (e2e), IntersectionObserver API (scroll tracking), Python http.server (Playwright fixture).

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `docs/guide.html` | CREATE | 12-section guide with sidebar, CSS, JS |
| `docs/_layouts/default.html` | MODIFY | Add "Guide" nav link |
| `tests/test_guide_page.py` | CREATE | Structural unit + integration tests |
| `tests/test_guide_ui.py` | CREATE | Playwright e2e scroll/sidebar tests |

---

## CSS Classes and Data Attributes (reference for all tasks)

```
.guide-wrap          — outer flex container (sidebar + content)
.guide-sidebar       — sticky left sidebar (220px)
.guide-step          — one numbered step, data-step="N" (N = 1..12)
.guide-step.active   — currently in-view step (purple circle, subtitle shown)
.guide-step.done     — scrolled-past step (purple outline + checkmark)
.guide-content       — scrollable right content area
.guide-progress-bar  — thin top bar container
.guide-progress-fill — purple fill, width driven by JS (data-progress attr)
.guide-section       — each <section> element, data-section="N"
.what-it-does        — indigo "WHAT THIS DOES" box
.install-callout     — "INSTALL THIS SKILL" dark box (sections 3–12 only)
.prompt-block        — "PROMPT TO TRY" dark monospace box
.section-next        — "Next: X →" transition at bottom of each section
```

IDs: `section-1` through `section-12` on each `<section>` element.

---

## Task 1: Structural test suite — RED

**Files:**
- Create: `tests/test_guide_page.py`

- [ ] **Step 1: Write the test file**

```python
#!/usr/bin/env python3
"""
Structural tests for docs/guide.html.

Unit tests: file exists, frontmatter, nav link.
Integration tests: all 12 sections present, sidebar steps match sections,
  prompt blocks, install callouts, what-it-does boxes, no placeholder text.
"""

import re
import sys
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
        count = len(re.findall(r'id="section-\d+"', self.content))
        self.assertEqual(count, SECTION_COUNT,
                         f'Expected {SECTION_COUNT} section IDs, found {count}')

    def test_all_section_ids_sequential(self):
        for n in range(1, SECTION_COUNT + 1):
            self.assertIn(f'id="section-{n}"', self.content,
                          f'Missing id="section-{n}"')

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
        # Sections 1 and 2 (CLAUDE.md setup, workspace) are setup steps, not skills
        count = self.content.count('install-callout')
        self.assertEqual(count, 10,
                         f'Expected 10 install-callout boxes (sections 3-12), found {count}')

    def test_twelve_section_next_links(self):
        # All sections except last have a "Next" link; last has a summary
        count = self.content.count('section-next')
        self.assertGreaterEqual(count, 11,
                                f'Expected at least 11 section-next links, found {count}')

    def test_no_placeholder_text(self):
        for placeholder in ('TBD', 'TODO', 'Lorem ipsum', 'placeholder'):
            self.assertNotIn(placeholder, self.content,
                             f'Found placeholder text {placeholder!r} in guide')

    def test_all_prompts_are_non_empty(self):
        # Extract prompt-block divs and check none are empty
        blocks = re.findall(
            r'class="prompt-block"[^>]*>(.*?)</div>',
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
        self.assertIn('active', self.content)

    def test_done_class_logic_present(self):
        self.assertIn('done', self.content)
```

- [ ] **Step 2: Run tests to confirm they all fail**

```bash
cd /Users/mdproctor/claude/cc-praxis
python3 -m pytest tests/test_guide_page.py -v 2>&1 | tail -20
```

Expected: All tests FAIL with `FileNotFoundError` or `AssertionError`. The file `docs/guide.html` does not exist yet.

- [ ] **Step 3: Commit the failing tests**

```bash
git add tests/test_guide_page.py
git commit -m "test(guide): structural test suite — RED"
```

---

## Task 2: Guide page skeleton — GREEN for structural tests

**Files:**
- Create: `docs/guide.html`

- [ ] **Step 1: Create the guide page**

Write the complete `docs/guide.html`. This is a large file — write it in full, do not truncate.

```html
---
layout: default
title: Getting Started
permalink: /guide/
---
<style>
  /* ── Layout ─────────────────────────────────────────────────── */
  .guide-wrap {
    display: flex;
    min-height: calc(100vh - 56px);
    max-width: 1100px;
    margin: 0 auto;
  }

  /* ── Sidebar ─────────────────────────────────────────────────── */
  .guide-sidebar {
    width: 220px;
    flex-shrink: 0;
    padding: 2rem 1.25rem 2rem 1.5rem;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid #e5e7eb;
    background: white;
  }
  .guide-sidebar-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #9ca3af;
    text-transform: uppercase;
    margin-bottom: 1.25rem;
  }
  .guide-step {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 1rem;
    cursor: pointer;
    text-decoration: none;
    color: inherit;
  }
  .guide-step-circle {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #e5e7eb;
    color: #9ca3af;
    font-size: 10px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
    transition: background 0.2s, border 0.2s;
  }
  .guide-step-text { flex: 1; }
  .guide-step-title {
    font-size: 12px;
    color: #9ca3af;
    font-weight: 500;
    line-height: 1.3;
    transition: color 0.2s;
  }
  .guide-step-sub {
    font-size: 10px;
    color: #d1d5db;
    margin-top: 2px;
    display: none;
  }

  /* Active step */
  .guide-step.active .guide-step-circle {
    background: #4f46e5;
    color: white;
  }
  .guide-step.active .guide-step-title { color: #111827; font-weight: 700; }
  .guide-step.active .guide-step-sub { display: block; color: #6b7280; }

  /* Done step */
  .guide-step.done .guide-step-circle {
    background: white;
    border: 2px solid #4f46e5;
    color: #4f46e5;
    font-size: 13px;
  }
  .guide-step.done .guide-step-title { color: #6b7280; }

  /* ── Content area ────────────────────────────────────────────── */
  .guide-content {
    flex: 1;
    min-width: 0;
    padding: 2.5rem 3rem 4rem;
  }

  /* Progress bar */
  .guide-progress-bar {
    height: 3px;
    background: #e5e7eb;
    border-radius: 2px;
    margin-bottom: 2.5rem;
    overflow: hidden;
  }
  .guide-progress-fill {
    height: 100%;
    background: #4f46e5;
    border-radius: 2px;
    transition: width 0.3s ease;
    width: 0%;
  }

  /* Section */
  .guide-section {
    margin-bottom: 5rem;
    scroll-margin-top: 2rem;
  }
  .guide-step-label {
    font-size: 11px;
    font-weight: 600;
    color: #4f46e5;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
  }
  .guide-section h2 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #111827;
    margin: 0 0 0.3rem;
    letter-spacing: -0.02em;
    line-height: 1.2;
  }
  .guide-section-sub {
    font-size: 0.9rem;
    color: #6b7280;
    margin: 0 0 1.75rem;
    line-height: 1.5;
  }

  /* What it does box */
  .what-it-does {
    background: #eef2ff;
    border-left: 3px solid #4f46e5;
    border-radius: 0 6px 6px 0;
    padding: 0.875rem 1.1rem;
    margin-bottom: 1.5rem;
  }
  .what-it-does-label {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #4338ca;
    text-transform: uppercase;
    margin-bottom: 5px;
  }
  .what-it-does p {
    font-size: 13px;
    color: #312e81;
    margin: 0;
    line-height: 1.6;
  }

  /* Install callout */
  .install-callout {
    background: #1e1b4b;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }
  .install-callout-label {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #6b7280;
    text-transform: uppercase;
    flex-shrink: 0;
  }
  .install-callout code {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
    color: #86efac;
  }

  /* Prose */
  .guide-section p {
    font-size: 14px;
    color: #374151;
    line-height: 1.75;
    margin-bottom: 1rem;
  }
  .guide-section ul {
    font-size: 14px;
    color: #374151;
    line-height: 1.75;
    padding-left: 1.5rem;
    margin-bottom: 1rem;
  }
  .guide-section li { margin-bottom: 0.3rem; }
  .guide-section code {
    background: #f3f4f6;
    color: #4338ca;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 12px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }
  .guide-section strong { color: #111827; font-weight: 600; }

  /* Priority table */
  .priority-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1.5rem;
    font-size: 13px;
  }
  .priority-table th {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #6b7280;
    border-bottom: 2px solid #e5e7eb;
    padding: 0.5rem 0.75rem;
    text-align: left;
  }
  .priority-table td {
    border-bottom: 1px solid #f3f4f6;
    padding: 0.5rem 0.75rem;
    color: #374151;
    vertical-align: top;
  }
  .priority-table td:first-child { font-weight: 600; color: #111827; }

  /* Prompt block */
  .prompt-block {
    background: #111827;
    border-radius: 6px;
    padding: 0.875rem 1.1rem;
    margin-bottom: 1.25rem;
  }
  .prompt-block-label {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #4b5563;
    text-transform: uppercase;
    margin-bottom: 6px;
  }
  .prompt-block p {
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    font-size: 12px !important;
    color: #e5e7eb !important;
    margin: 0 !important;
    line-height: 1.6 !important;
  }

  /* Code block */
  .code-block {
    background: #1e1b4b;
    border-radius: 6px;
    padding: 0.875rem 1.1rem;
    margin-bottom: 1.5rem;
    overflow-x: auto;
  }
  .code-block pre {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
    color: #e5e7eb;
    margin: 0;
    line-height: 1.7;
  }
  .code-block .c { color: #6b7280; } /* comment */
  .code-block .k { color: #a5b4fc; } /* key */
  .code-block .v { color: #86efac; } /* value */
  .code-block .s { color: #fde68a; } /* string / annotation */

  /* Next link */
  .section-next {
    display: flex;
    justify-content: flex-end;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #f3f4f6;
  }
  .section-next a {
    font-size: 13px;
    font-weight: 600;
    color: #4f46e5;
    text-decoration: none;
  }
  .section-next a:hover { color: #3730a3; }

  /* Routing diagram */
  .routing-diagram {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    font-size: 13px;
    color: #374151;
  }
  .routing-diagram .dest {
    display: inline-block;
    background: #eef2ff;
    color: #4338ca;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    font-family: monospace;
    margin: 2px;
  }

  /* Preamble */
  .guide-preamble {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 3rem;
  }
  .guide-preamble h3 {
    font-size: 14px;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.75rem;
  }
  .guide-preamble ol {
    font-size: 13px;
    color: #374151;
    padding-left: 1.25rem;
    margin: 0;
    line-height: 1.75;
  }
  .guide-preamble code {
    background: #e5e7eb;
    color: #1e1b4b;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 11px;
    font-family: monospace;
  }

  /* Mobile */
  @media (max-width: 768px) {
    .guide-sidebar { display: none; }
    .guide-content { padding: 1.5rem 1.25rem 3rem; }
  }
</style>

<div class="guide-wrap">

  <!-- ── Sidebar ──────────────────────────────────────────────── -->
  <nav class="guide-sidebar" aria-label="Guide sections">
    <div class="guide-sidebar-label">Getting Started</div>

    <a class="guide-step active" data-step="1" href="#section-1">
      <div class="guide-step-circle">1</div>
      <div class="guide-step-text">
        <div class="guide-step-title">CLAUDE.md Setup</div>
        <div class="guide-step-sub">Your configuration hub</div>
      </div>
    </a>

    <a class="guide-step" data-step="2" href="#section-2">
      <div class="guide-step-circle">2</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Workspace Setup</div>
        <div class="guide-step-sub">Separate code from methodology</div>
      </div>
    </a>

    <a class="guide-step" data-step="3" href="#section-3">
      <div class="guide-step-circle">3</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Java Development</div>
        <div class="guide-step-sub">Safety-first rules</div>
      </div>
    </a>

    <a class="guide-step" data-step="4" href="#section-4">
      <div class="guide-step-circle">4</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Code Review</div>
        <div class="guide-step-sub">Catches problems early</div>
      </div>
    </a>

    <a class="guide-step" data-step="5" href="#section-5">
      <div class="guide-step-circle">5</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Smart Commits</div>
        <div class="guide-step-sub">Design sync built in</div>
      </div>
    </a>

    <a class="guide-step" data-step="6" href="#section-6">
      <div class="guide-step-circle">6</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Brainstorming</div>
        <div class="guide-step-sub">Design before code</div>
      </div>
    </a>

    <a class="guide-step" data-step="7" href="#section-7">
      <div class="guide-step-circle">7</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Ideas &amp; Decisions</div>
        <div class="guide-step-sub">Park and record</div>
      </div>
    </a>

    <a class="guide-step" data-step="8" href="#section-8">
      <div class="guide-step-circle">8</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Issues &amp; Epics</div>
        <div class="guide-step-sub">Automatic tracking</div>
      </div>
    </a>

    <a class="guide-step" data-step="9" href="#section-9">
      <div class="guide-step-circle">9</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Design Documentation</div>
        <div class="guide-step-sub">Journal and snapshots</div>
      </div>
    </a>

    <a class="guide-step" data-step="10" href="#section-10">
      <div class="guide-step-circle">10</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Closing an Epic</div>
        <div class="guide-step-sub">Merge, route, close</div>
      </div>
    </a>

    <a class="guide-step" data-step="11" href="#section-11">
      <div class="guide-step-circle">11</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Session Handover</div>
        <div class="guide-step-sub">Resume in one message</div>
      </div>
    </a>

    <a class="guide-step" data-step="12" href="#section-12">
      <div class="guide-step-circle">12</div>
      <div class="guide-step-text">
        <div class="guide-step-title">Project Diary</div>
        <div class="guide-step-sub">Honest in-the-moment writing</div>
      </div>
    </a>
  </nav>

  <!-- ── Content ──────────────────────────────────────────────── -->
  <div class="guide-content">

    <!-- Progress bar -->
    <div class="guide-progress-bar">
      <div class="guide-progress-fill" id="guide-progress"></div>
    </div>

    <!-- Prerequisites preamble -->
    <div class="guide-preamble">
      <h3>Before you start</h3>
      <ol>
        <li><strong>Claude Code installed</strong> — <a href="https://claude.ai/code">claude.ai/code</a></li>
        <li><strong>cc-praxis marketplace added</strong> — run in Claude Code:<br>
          <code>/plugin marketplace add github.com/mdproctor/cc-praxis</code></li>
        <li><strong>Install skills as you go</strong> — each section below tells you which skill to install. You don't need to install everything upfront.</li>
      </ol>
    </div>

    <!-- ── Section 1: CLAUDE.md Setup ──────────────────────────── -->
    <section class="guide-section" id="section-1" data-section="1">
      <div class="guide-step-label">Step 1 of 12</div>
      <h2>CLAUDE.md Setup</h2>
      <p class="guide-section-sub">Your configuration hub — Claude reads this at the start of every session.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Creates the file that every cc-praxis skill reads first. Sets your project type, GitHub repo, and work tracking preferences. Without it, skills can't route to the right workflows.</p>
      </div>

      <p>CLAUDE.md is not a skill — it's configuration. Claude Code reads it automatically at the start of every session, so anything you put in it becomes part of Claude's working context for the entire conversation.</p>

      <p>If your project doesn't have one yet, the fastest way is to ask Claude directly. Open Claude Code in your project root and say:</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>"Set up a CLAUDE.md for my Java project. It's a Quarkus REST API tracked on GitHub at owner/repo. Enable issue tracking."</p>
      </div>

      <p>Claude will create the file and ask a few clarifying questions. The key field to check is <code>type: java</code> — this single line tells every cc-praxis skill which workflow to activate:</p>

      <div class="code-block"><pre><span class="c"># CLAUDE.md</span>
<span class="k">type:</span> <span class="v">java</span>
<span class="k">GitHub repo:</span> <span class="v">owner/repo</span>

<span class="c">## Work Tracking</span>
<span class="k">Issue tracking:</span> <span class="v">enabled</span>
<span class="k">GitHub repo:</span> <span class="v">owner/repo</span></pre></div>

      <p>The <code>## Work Tracking</code> section is what enables automatic issue linking in commits. Once it's there, Claude will check for an active issue before writing code and link every commit to it automatically.</p>

      <div class="section-next">
        <a href="#section-2">Next: Workspace Setup →</a>
      </div>
    </section>

    <!-- ── Section 2: Workspace Setup ──────────────────────────── -->
    <section class="guide-section" id="section-2" data-section="2">
      <div class="guide-step-label">Step 2 of 12</div>
      <h2>Workspace Setup</h2>
      <p class="guide-section-sub">Separate methodology artifacts from your project code.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Creates a companion git repository alongside your project that stores ADRs, design journals, snapshots, and session handovers — keeping your project repo focused on code.</p>
      </div>

      <p>You can start with just a project (simplest — no workspace needed). But if you want a clean project repo with no methodology artifacts committed to it, a workspace is worth setting up early.</p>

      <p><strong>Three modes:</strong></p>
      <ul>
        <li><strong>Project only</strong> — everything stays in the project repo. Simplest start.</li>
        <li><strong>Project + workspace</strong> — ADRs, design docs, snapshots, and handovers live in a separate git repo at <code>~/claude/private/&lt;project&gt;/</code>.</li>
        <li><strong>Alternative path</strong> — artifacts route to any git repo you specify.</li>
      </ul>

      <p>To create a workspace, open Claude Code in your project directory and run:</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>/workspace-init</p>
      </div>

      <p>The skill asks for a project name, privacy setting, and your project path, then creates the workspace directory with all subdirectories.</p>

      <p><strong>Artifact routing</strong> — where files go at epic close is controlled by the <code>## Routing</code> table in your workspace CLAUDE.md. Configure this before your first epic:</p>

      <div class="code-block"><pre><span class="c">## Routing</span>

<span class="c">| Artifact   | Destination |</span>
<span class="c">|------------|-------------|</span>
<span class="k">adr</span>        <span class="v">workspace</span>
<span class="k">design</span>     <span class="v">workspace</span>
<span class="k">blog</span>       <span class="v">project</span>
<span class="k">snapshots</span>  <span class="v">workspace</span></pre></div>

      <p>Valid destinations: <code>project</code> · <code>workspace</code> · <code>alternative ~/path/to/repo/</code></p>

      <div class="section-next">
        <a href="#section-3">Next: Java Development →</a>
      </div>
    </section>

    <!-- ── Section 3: Java Development ─────────────────────────── -->
    <section class="guide-section" id="section-3" data-section="3">
      <div class="guide-step-label">Step 3 of 12</div>
      <h2>Java Development</h2>
      <p class="guide-section-sub">Safety-first rules for every Java file you write.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Loads development rules covering safety, concurrency, performance, and code quality — in that exact priority order. Triggers automatically when you ask Claude to implement or fix Java code.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install this skill</span>
        <code>scripts/claude-skill install java-dev</code>
      </div>

      <p>The skill enforces a strict priority order that should never be violated:</p>

      <table class="priority-table">
        <thead>
          <tr><th>Priority</th><th>Area</th><th>Example rule</th></tr>
        </thead>
        <tbody>
          <tr><td>1 — Safety</td><td>Resources, classloaders, file descriptors</td><td>Always use try-with-resources — "it will close automatically" has exhausted FD limits in production</td></tr>
          <tr><td>2 — Concurrency</td><td>Thread ownership, shared state</td><td>Document which thread owns each field; never share mutable state without explicit synchronisation</td></tr>
          <tr><td>3 — Performance</td><td>Allocations, blocking calls</td><td>Never block the Vert.x event loop — use <code>@Blocking</code> or <code>executeBlocking</code></td></tr>
          <tr><td>4 — Code Quality</td><td>Readability, naming, structure</td><td>One concept per method; name things what they are</td></tr>
        </tbody>
      </table>

      <p>The skill also covers Quarkus-specific patterns: CDI injection, reactive streams, native compilation concerns, and <code>@QuarkusTest</code> integration testing patterns.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>"Implement a Quarkus REST endpoint to fetch orders by customer ID, with proper error handling."</p>
      </div>

      <div class="section-next">
        <a href="#section-4">Next: Code Review →</a>
      </div>
    </section>

    <!-- ── Section 4: Code Review ───────────────────────────────── -->
    <section class="guide-section" id="section-4" data-section="4">
      <div class="guide-step-label">Step 4 of 12</div>
      <h2>Code Review</h2>
      <p class="guide-section-sub">Catches problems before they reach the repository.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Reviews staged changes against safety, concurrency, performance, and testing checklists. Triggers automatically before <code>java-git-commit</code> if no review has been done in the current session.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install this skill</span>
        <code>scripts/claude-skill install java-code-review</code>
      </div>

      <p>The most important thing to know: <strong>you don't need to invoke this manually.</strong> When you run <code>/java-git-commit</code>, if no review has happened yet in this session, the commit skill runs the review automatically before proceeding.</p>

      <p>Reviews produce findings in three tiers:</p>
      <ul>
        <li><strong>CRITICAL</strong> — blocks the commit. Safety violations, silent data corruption, missing transaction boundaries.</li>
        <li><strong>WARNING</strong> — review recommended before committing. Performance anti-patterns, test gaps, missing error handling.</li>
        <li><strong>NOTE</strong> — informational. Style suggestions, minor naming issues.</li>
      </ul>

      <p>If the review finds security-critical code — authentication, payments, PII handling — it automatically escalates to <code>java-security-audit</code> for a full OWASP Top 10 check.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>"Review my changes." &nbsp;or&nbsp; /java-code-review</p>
      </div>

      <div class="section-next">
        <a href="#section-5">Next: Smart Commits →</a>
      </div>
    </section>

    <!-- ── Section 5: Smart Commits ─────────────────────────────── -->
    <section class="guide-section" id="section-5" data-section="5">
      <div class="guide-step-label">Step 5 of 12</div>
      <h2>Smart Commits</h2>
      <p class="guide-section-sub">Commits that keep your design document in sync automatically.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Routes every Java commit through design document sync, enforces Java-specific conventional commit scopes, and links to the active GitHub issue. Replaces plain <code>git commit</code> for Java projects.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install this skill</span>
        <code>scripts/claude-skill install java-git-commit</code>
      </div>

      <p>Always use <code>/java-git-commit</code> instead of plain <code>git commit</code> in Java projects. The skill does three things automatically before writing the commit message:</p>
      <ol>
        <li>Runs <code>java-code-review</code> if no review has been done this session</li>
        <li>Runs <code>java-update-design</code> to sync the design document</li>
        <li>Proposes a conventional commit message with Java-specific scopes</li>
      </ol>

      <p>Java-specific commit scopes (not generic <code>api</code> or <code>backend</code>):</p>

      <div class="code-block"><pre><span class="v">feat(service)</span>:   add order validation with retry
<span class="v">fix(repository)</span>: correct null handling in findByCustomerId
<span class="v">feat(rest)</span>:      expose /orders/{id} endpoint
<span class="v">chore(config)</span>:   increase connection pool size
<span class="v">test(service)</span>:   add edge cases for validation logic</pre></div>

      <p><strong>On an epic branch:</strong> <code>java-update-design</code> writes to <code>design/JOURNAL.md</code> (not to DESIGN.md directly). The journal accumulates through the epic and merges into DESIGN.md at epic close — explained in sections 9 and 10.</p>

      <p>With Work Tracking enabled, the commit message includes <code>Refs #N</code> or <code>Closes #N</code> automatically based on the active issue.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>/java-git-commit</p>
      </div>

      <div class="section-next">
        <a href="#section-6">Next: Brainstorming →</a>
      </div>
    </section>

    <!-- ── Section 6: Brainstorming ─────────────────────────────── -->
    <section class="guide-section" id="section-6" data-section="6">
      <div class="guide-step-label">Step 6 of 12</div>
      <h2>Brainstorming</h2>
      <p class="guide-section-sub">Design before you code. Every feature, every time.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Guides a structured design conversation that produces a written spec in <code>specs/</code>, then hands off to a step-by-step implementation plan. No code is written until the spec is approved.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install this skill</span>
        <code>scripts/claude-skill install install-skills</code>
        <span style="color:#6b7280; font-size:11px;">then select superpowers:brainstorming from the list</span>
      </div>

      <p>The hard gate is the most important thing about this skill: <strong>no code is written until the spec is approved.</strong> This applies even to features that seem simple. "Simple" features are exactly where unexamined assumptions cause the most rework.</p>

      <p>The flow is: context exploration → clarifying questions (one at a time) → 2–3 approaches with trade-offs → design sections for approval → written spec → implementation plan. The implementation plan is what drives the actual coding.</p>

      <p>Specs land in <code>specs/</code> in your workspace (if configured) or project. They become the input to <code>writing-plans</code>, which produces a TDD task list for implementation.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>"Let's brainstorm the order validation feature. I want idempotent validation with retry logic."</p>
      </div>

      <div class="section-next">
        <a href="#section-7">Next: Ideas &amp; Decisions →</a>
      </div>
    </section>

    <!-- ── Section 7: Ideas & Decisions ─────────────────────────── -->
    <section class="guide-section" id="section-7" data-section="7">
      <div class="guide-step-label">Step 7 of 12</div>
      <h2>Ideas &amp; Decisions</h2>
      <p class="guide-section-sub">Park undecided thoughts. Record decided ones permanently.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Two skills at different decision readiness levels. <code>idea-log</code> captures possibilities before they're decided. <code>adr</code> records the decision once made — immutably, with a status lifecycle.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install these skills</span>
        <code>scripts/claude-skill install idea-log adr</code>
      </div>

      <p><strong>idea-log</strong> maintains <code>IDEAS.md</code> — a living list of possibilities that haven't been decided yet. Ideas can be active, promoted to an ADR or issue, or discarded. The skill flags ideas that have been sitting for 90+ days during review.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try (idea-log)</div>
        <p>"Log this idea: cache order lookups in Redis — not decided yet, just worth remembering."</p>
      </div>

      <p><strong>adr</strong> (Architecture Decision Records) are triggered automatically when you make a significant choice: major version upgrade, adopting a new library, choosing between viable patterns, or deliberately deviating from defaults. ADRs are <em>append-only</em> — never rewrite an accepted ADR. If a decision is superseded, create a new ADR and mark the old one <code>Superseded by ADR-NNNN</code>.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try (adr)</div>
        <p>"Create an ADR for our decision to use Panache over plain JPA for the repository layer."</p>
      </div>

      <div class="section-next">
        <a href="#section-8">Next: Issues &amp; Epics →</a>
      </div>
    </section>

    <!-- ── Section 8: Issues & Epics ────────────────────────────── -->
    <section class="guide-section" id="section-8" data-section="8">
      <div class="guide-step-label">Step 8 of 12</div>
      <h2>Issues &amp; Epics</h2>
      <p class="guide-section-sub">Four-phase tracking that runs automatically once enabled.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Wires GitHub issue tracking into every session. Phase 0 is one-time setup. After that, Phases 1–3 fire automatically at the right moments — before implementation, before each coding session, and before each commit.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install this skill</span>
        <code>scripts/claude-skill install issue-workflow</code>
      </div>

      <p>Run Phase 0 once to configure issue tracking:</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try (Phase 0 — one time)</div>
        <p>/issue-workflow</p>
      </div>

      <p>This creates standard GitHub labels (including <code>epic</code>), writes <code>## Work Tracking</code> to CLAUDE.md, and offers to reconstruct issues from git history.</p>

      <p>After that, three phases run automatically:</p>
      <ul>
        <li><strong>Phase 1 (pre-implementation)</strong> — when a plan is ready, creates an epic + child issues before any code is written. Each issue gets: Context, What, Acceptance Criteria, Notes.</li>
        <li><strong>Phase 2 (task intake, automatic)</strong> — before writing code, Claude checks for an active issue. If none, drafts one and assesses epic placement: active epic → fits DoD → other open epics → standalone.</li>
        <li><strong>Phase 3 (pre-commit, automatic)</strong> — verifies issue linkage on staged changes; suggests splitting commits that span multiple concerns.</li>
      </ul>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try (Phase 1)</div>
        <p>"We're starting the order validation feature — set up the epic and issue structure from this spec."</p>
      </div>

      <div class="section-next">
        <a href="#section-9">Next: Design Documentation →</a>
      </div>
    </section>

    <!-- ── Section 9: Design Documentation ──────────────────────── -->
    <section class="guide-section" id="section-9" data-section="9">
      <div class="guide-step-label">Step 9 of 12</div>
      <h2>Design Documentation</h2>
      <p class="guide-section-sub">Two records for two purposes: the living journal and the immutable snapshot.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Maintains two distinct design artifacts: <code>JOURNAL.md</code> accumulates narrative during an epic and merges into DESIGN.md at close. Design snapshots are immutable point-in-time records — never edited after creation.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install these skills</span>
        <code>scripts/claude-skill install java-update-design design-snapshot</code>
      </div>

      <p><strong>JOURNAL.md</strong> is created by <code>epic-start</code> and lives in <code>design/JOURNAL.md</code> on your workspace branch. Every <code>/java-git-commit</code> on an epic branch appends an entry to it automatically. Entries use <code>§SectionName</code> anchors that match headings in your DESIGN.md — this is the key used for the three-way merge at epic close.</p>

      <div class="code-block"><pre><span class="c">### 2026-04-14 · §Architecture</span>

<span class="v">Moved order validation out of the REST layer into a dedicated</span>
<span class="v">OrderValidationService. The endpoint now delegates entirely —</span>
<span class="v">validation logic is testable without spinning up HTTP.</span></pre></div>

      <p><strong>Design snapshots</strong> are different — they're immutable dated records of where the design stands at a particular moment. Use them before a major pivot, at the end of a phase, or any time you want a "save point" you can rewind to. A snapshot is never edited after creation; if the design moves on, create a new one.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>"Take a design snapshot before we change the repository layer architecture."</p>
      </div>

      <div class="section-next">
        <a href="#section-10">Next: Closing an Epic →</a>
      </div>
    </section>

    <!-- ── Section 10: Closing an Epic ──────────────────────────── -->
    <section class="guide-section" id="section-10" data-section="10">
      <div class="guide-step-label">Step 10 of 12</div>
      <h2>Closing an Epic</h2>
      <p class="guide-section-sub">Branch cleanup, design merge, artifact routing — all in one confirmed workflow.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Closes the epic branch: routes artifacts per your routing config, merges JOURNAL.md into project DESIGN.md via three-way merge, posts specs to the GitHub issue, closes the issue, and cleans up branches. Nothing executes until you confirm the plan.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install this skill</span>
        <code>scripts/claude-skill install epic-close</code>
      </div>

      <p>Before doing anything, <code>/epic-close</code> shows you what it plans to do:</p>

      <div class="code-block"><pre><span class="v">Resolved routing for this epic:</span>
  <span class="k">adr</span>       → <span class="v">workspace</span>   (Layer 3 workspace override)
  <span class="k">blog</span>      → <span class="v">project</span>     (Layer 1 default)
  <span class="k">design</span>    → <span class="v">workspace</span>   (Layer 2 global default)
  <span class="k">snapshots</span> → <span class="v">workspace</span>   (Layer 3 workspace override)

<span class="v">Proceed? (y/n)</span></pre></div>

      <p>The JOURNAL.md merge is where the three-way merge happens. It uses the SHA recorded by <code>epic-start</code> as the baseline, compares against the current DESIGN.md, and applies your journal entries section by section. Each <code>§SectionName</code> anchor in the journal targets the matching heading in DESIGN.md.</p>

      <p>After routing and merging, the skill posts your selected specs as comments to the GitHub issue, closes it, and offers to delete the epic branches on both the project and workspace repos.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>/epic-close</p>
      </div>

      <div class="section-next">
        <a href="#section-11">Next: Session Handover →</a>
      </div>
    </section>

    <!-- ── Section 11: Session Handover ─────────────────────────── -->
    <section class="guide-section" id="section-11" data-section="11">
      <div class="guide-step-label">Step 11 of 12</div>
      <h2>Session Handover</h2>
      <p class="guide-section-sub">End every session with a handoff. Resume any session in one message.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Produces a committed <code>HANDOFF.md</code> — a concise pointer document (&lt;500 tokens) that gives the next Claude session enough context to resume immediately. Git history is the archive; HANDOFF.md is just the delta.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install this skill</span>
        <code>scripts/claude-skill install handover</code>
      </div>

      <p>Before writing the handover, Claude presents a wrap checklist:</p>

      <div class="code-block"><pre><span class="v">Session wrap — create before writing the handover?</span>

[<span class="s">x</span>] 1  write-blog       capture this session's work as a diary entry
[ ] 2  design-snapshot  freeze the current design state
[<span class="s">x</span>] 3  update-claude-md sync any new workflow conventions
[<span class="s">x</span>] 4  forage sweep     check for gotchas, techniques, undocumented

<span class="v">Type numbers to toggle, "all", or Enter to proceed:</span></pre></div>

      <p>The <strong>forage sweep</strong> (step 4) runs while context is still full — it's a scan of the session for three types of knowledge worth preserving: gotchas (bugs that silently fail or have misleading symptoms), techniques (non-obvious approaches that worked), and undocumented behaviors found only through trial and error.</p>

      <p>HANDOFF.md uses a <strong>delta-first principle</strong>: only sections that changed since the last handover are written in full. Unchanged sections reference git history: <code>*Unchanged — git show HEAD~1:HANDOFF.md*</code>. This keeps the file small across long-running epics.</p>

      <p>To resume a session: read <code>HANDOFF.md</code> and run <code>git log --oneline -6</code>. That's enough to pick up in the next message. If the handover is more than a week old, check freshness first: <code>git log -1 --format="%ar" -- HANDOFF.md</code>.</p>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>"Create a handover." &nbsp;or&nbsp; /handover</p>
      </div>

      <div class="section-next">
        <a href="#section-12">Next: Project Diary →</a>
      </div>
    </section>

    <!-- ── Section 12: Project Diary ────────────────────────────── -->
    <section class="guide-section" id="section-12" data-section="12">
      <div class="guide-step-label">Step 12 of 12</div>
      <h2>Project Diary</h2>
      <p class="guide-section-sub">Honest in-the-moment writing — not a polished retrospective.</p>

      <div class="what-it-does">
        <div class="what-it-does-label">What this does</div>
        <p>Writes diary entries in your personal voice capturing what you believed at the time — including failed attempts, rejected approaches, and mid-build pivots. Entries are never edited after writing; corrections become new entries.</p>
      </div>

      <div class="install-callout">
        <span class="install-callout-label">Install this skill</span>
        <code>scripts/claude-skill install write-blog</code>
      </div>

      <p>The most common mistake with the diary is writing it like a retrospective — smooth narrative, everything working, no dead ends. That's not what this is. The value is in the iteration: what you tried first, why it failed, what you found out.</p>

      <p><strong>Voice</strong> is configured from a personal style guide. Set the path in your environment:</p>

      <div class="code-block"><pre><span class="c"># In ~/.zshrc or ~/.bashrc</span>
<span class="k">export</span> <span class="v">PERSONAL_WRITING_STYLES_PATH=~/writing-styles/</span></pre></div>

      <p>Without it, the skill uses a bundled fallback voice: peer-to-peer, direct, ~17-word sentences. You can create a personal guide at any time — the skill picks it up automatically.</p>

      <p><strong>Entry metadata</strong> (added at write time) drives routing and filtering:</p>

      <div class="code-block"><pre><span class="k">entry_type:</span> <span class="v">note</span>        <span class="c"># article | note</span>
<span class="k">subtype:</span>    <span class="v">diary</span>       <span class="c"># for notes; omit for articles</span>
<span class="k">projects:</span>   <span class="v">[my-project]</span>
<span class="k">tags:</span>       <span class="v">[quarkus, validation]</span></pre></div>

      <p>The site shows two filtered pages: <code>/blog/</code> for diary entries, <code>/articles/</code> for topic-driven articles. Publishing to external platforms is handled by <code>publish-blog</code>, which reads <code>blog-routing.yaml</code> to decide which entry goes where.</p>

      <p><strong>A sample entry excerpt</strong> — notice the failed first approach and the actual fix:</p>

      <div class="code-block"><pre><span class="v">The first attempt at idempotency used a database unique constraint</span>
<span class="v">on (orderId, customerId). I thought it was clean. It wasn't — the</span>
<span class="v">constraint fired a DataIntegrityViolationException that Quarkus</span>
<span class="v">wrapped in a 500, not the 409 I wanted. Took two hours to find</span>
<span class="v">that the exception handler I'd written wasn't in scope for the</span>
<span class="v">transaction boundary.</span>

<span class="v">We switched to an explicit idempotency key check before insert.</span>
<span class="v">Less clever, completely obvious, works correctly. The exception</span>
<span class="v">handler is still there — now it catches things I didn't anticipate.</span></pre></div>

      <div class="prompt-block">
        <div class="prompt-block-label">Prompt to try</div>
        <p>"Write a blog entry for today's session — we implemented order validation with retry logic."</p>
      </div>

      <div class="section-next" style="border-top: 2px solid #4f46e5; padding-top: 1.5rem; margin-top: 2rem;">
        <span style="font-size: 13px; color: #4f46e5; font-weight: 700;">✓ You've covered the full Java workflow. Start with CLAUDE.md and install skills as you need them.</span>
      </div>
    </section>

  </div><!-- /.guide-content -->
</div><!-- /.guide-wrap -->

<script>
(function() {
  const steps = Array.from(document.querySelectorAll('.guide-step'));
  const sections = Array.from(document.querySelectorAll('.guide-section'));
  const progressFill = document.getElementById('guide-progress');
  const total = sections.length;

  function setActive(index) {
    steps.forEach((step, i) => {
      step.classList.remove('active', 'done');
      if (i < index) step.classList.add('done');
      if (i === index) step.classList.add('active');
    });
    // Update circle content for done steps
    steps.forEach((step, i) => {
      const circle = step.querySelector('.guide-step-circle');
      if (step.classList.contains('done')) {
        circle.textContent = '✓';
      } else {
        circle.textContent = i + 1;
      }
    });
    // Progress bar
    const pct = Math.round(((index + 1) / total) * 100);
    progressFill.style.width = pct + '%';
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const n = parseInt(entry.target.dataset.section, 10);
        setActive(n - 1);
      }
    });
  }, { threshold: 0.25, rootMargin: '-10% 0px -60% 0px' });

  sections.forEach(s => observer.observe(s));
  setActive(0);
})();
</script>
```

- [ ] **Step 2: Run structural tests**

```bash
cd /Users/mdproctor/claude/cc-praxis
python3 -m pytest tests/test_guide_page.py -v 2>&1 | tail -30
```

Expected: Most tests PASS. The nav tests (`TestNavLink`) will FAIL because `default.html` hasn't been updated yet. Check which tests fail and fix before proceeding.

If nav tests fail, that's expected — they're addressed in Task 3.
If content tests fail, inspect the failing assertion and fix the HTML.

- [ ] **Step 3: Commit the guide page**

```bash
git add docs/guide.html
git commit -m "feat(guide): 12-section getting started guide with sidebar nav"
```

---

## Task 3: Add Guide nav link — GREEN for nav tests

**Files:**
- Modify: `docs/_layouts/default.html`

- [ ] **Step 1: Find the current nav in default.html**

```bash
grep -n "header-nav\|Articles\|Diary\|GitHub" /Users/mdproctor/claude/cc-praxis/docs/_layouts/default.html
```

- [ ] **Step 2: Add Guide link before Articles**

Find the line containing the Articles nav link and add Guide before it:

```html
<a href="{{ '/guide/' | relative_url }}" {% if page.url contains '/guide/' %}class="active"{% endif %}>Guide</a>
```

The nav should now read (in order): **Guide · Articles · Diary · GitHub ↗**

- [ ] **Step 3: Run nav tests**

```bash
python3 -m pytest tests/test_guide_page.py::TestNavLink -v
```

Expected: All 3 nav tests PASS.

- [ ] **Step 4: Run full structural suite**

```bash
python3 -m pytest tests/test_guide_page.py -v 2>&1 | tail -15
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/_layouts/default.html
git commit -m "feat(guide): add Guide link to site nav"
```

---

## Task 4: Playwright e2e tests — RED

**Files:**
- Create: `tests/test_guide_ui.py`

- [ ] **Step 1: Write the Playwright test file**

```python
#!/usr/bin/env python3
"""
Playwright end-to-end tests for docs/guide.html.

Serves the raw guide.html (with frontmatter stripped) via Python HTTP server.
Tests sidebar scroll tracking, progress bar advancement, checkmark on
completed steps, and prompt block visibility.

Run:
    python3 -m pytest tests/test_guide_ui.py -v
"""

import http.server
import re
import sys
import tempfile
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
    """Remove Jekyll frontmatter (--- ... ---) and wrap in minimal HTML."""
    # Strip frontmatter block
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
  /* Provide enough height to scroll */
  .guide-section {{ min-height: 100vh; }}
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
        self.page.wait_for_timeout(300)  # Let IntersectionObserver fire

    def tearDown(self):
        self.page.close()

    # ── Happy path: initial state ─────────────────────────────────────────────

    def test_page_loads(self):
        title = self.page.title()
        self.assertIn('Getting Started', title)

    def test_sidebar_renders_twelve_steps(self):
        steps = self.page.query_selector_all('.guide-step')
        self.assertEqual(len(steps), SECTION_COUNT,
                         f'Expected {SECTION_COUNT} sidebar steps')

    def test_first_step_active_on_load(self):
        first_step = self.page.query_selector('[data-step="1"]')
        self.assertIsNotNone(first_step)
        classes = first_step.get_attribute('class')
        self.assertIn('active', classes,
                      'First step should be active on page load')

    def test_progress_bar_visible(self):
        fill = self.page.query_selector('#guide-progress')
        self.assertIsNotNone(fill)
        width = fill.evaluate('el => el.style.width')
        # Should have some width set (section 1 = ~8%)
        self.assertTrue(len(width) > 0 and width != '0%',
                        f'Progress bar should have non-zero width, got: {width!r}')

    def test_twelve_prompt_blocks_visible(self):
        blocks = self.page.query_selector_all('.prompt-block')
        self.assertEqual(len(blocks), SECTION_COUNT,
                         f'Expected {SECTION_COUNT} prompt blocks, found {len(blocks)}')

    def test_ten_install_callouts_visible(self):
        callouts = self.page.query_selector_all('.install-callout')
        self.assertEqual(len(callouts), 10,
                         f'Expected 10 install callouts, found {len(callouts)}')

    # ── Happy path: scroll to section 3 ──────────────────────────────────────

    def test_scroll_to_section_3_activates_step_3(self):
        self.page.evaluate("""
            document.querySelector('#section-3').scrollIntoView({behavior: 'instant'});
        """)
        self.page.wait_for_timeout(400)

        step3 = self.page.query_selector('[data-step="3"]')
        classes = step3.get_attribute('class')
        self.assertIn('active', classes,
                      'Step 3 should be active after scrolling to section 3')

    def test_scroll_to_section_3_marks_steps_1_2_done(self):
        self.page.evaluate("""
            document.querySelector('#section-3').scrollIntoView({behavior: 'instant'});
        """)
        self.page.wait_for_timeout(400)

        for step_n in (1, 2):
            step = self.page.query_selector(f'[data-step="{step_n}"]')
            classes = step.get_attribute('class')
            self.assertIn('done', classes,
                          f'Step {step_n} should be "done" after scrolling past it')

    def test_scroll_to_section_3_shows_checkmarks_on_done_steps(self):
        self.page.evaluate("""
            document.querySelector('#section-3').scrollIntoView({behavior: 'instant'});
        """)
        self.page.wait_for_timeout(400)

        for step_n in (1, 2):
            circle = self.page.query_selector(f'[data-step="{step_n}"] .guide-step-circle')
            text = circle.inner_text().strip()
            self.assertEqual(text, '✓',
                             f'Done step {step_n} circle should show ✓, got {text!r}')

    def test_scroll_to_section_3_advances_progress_bar(self):
        initial_width = self.page.evaluate(
            "parseFloat(document.getElementById('guide-progress').style.width)"
        )

        self.page.evaluate("""
            document.querySelector('#section-3').scrollIntoView({behavior: 'instant'});
        """)
        self.page.wait_for_timeout(400)

        new_width = self.page.evaluate(
            "parseFloat(document.getElementById('guide-progress').style.width)"
        )
        self.assertGreater(new_width, initial_width,
                           f'Progress bar should advance: {initial_width}% → {new_width}%')

    # ── Happy path: scroll to last section ───────────────────────────────────

    def test_scroll_to_section_12_marks_all_prior_done(self):
        self.page.evaluate("""
            document.querySelector('#section-12').scrollIntoView({behavior: 'instant'});
        """)
        self.page.wait_for_timeout(400)

        step12 = self.page.query_selector('[data-step="12"]')
        classes = step12.get_attribute('class')
        self.assertIn('active', classes, 'Step 12 should be active at last section')

        for step_n in range(1, 12):
            step = self.page.query_selector(f'[data-step="{step_n}"]')
            classes = step.get_attribute('class')
            self.assertIn('done', classes,
                          f'Step {step_n} should be done when at section 12')

    def test_progress_bar_near_full_at_last_section(self):
        self.page.evaluate("""
            document.querySelector('#section-12').scrollIntoView({behavior: 'instant'});
        """)
        self.page.wait_for_timeout(400)

        width = self.page.evaluate(
            "parseFloat(document.getElementById('guide-progress').style.width)"
        )
        self.assertGreater(width, 90, f'Progress should be >90% at last section, got {width}%')

    # ── Happy path: sidebar nav click ────────────────────────────────────────

    def test_clicking_step_5_scrolls_to_section_5(self):
        step5 = self.page.query_selector('[data-step="5"]')
        step5.click()
        self.page.wait_for_timeout(400)

        # Section 5 should now be visible in viewport
        is_visible = self.page.evaluate("""
            () => {
                const el = document.querySelector('#section-5');
                const rect = el.getBoundingClientRect();
                return rect.top < window.innerHeight && rect.bottom > 0;
            }
        """)
        self.assertTrue(is_visible, 'Section 5 should be in viewport after clicking step 5')

    # ── Happy path: content visibility ───────────────────────────────────────

    def test_all_what_it_does_boxes_visible(self):
        boxes = self.page.query_selector_all('.what-it-does')
        self.assertEqual(len(boxes), SECTION_COUNT)
        for i, box in enumerate(boxes, 1):
            self.assertTrue(box.is_visible(), f'What-it-does box {i} should be visible')

    def test_preamble_visible(self):
        preamble = self.page.query_selector('.guide-preamble')
        self.assertIsNotNone(preamble)
        self.assertTrue(preamble.is_visible())
        text = preamble.inner_text()
        self.assertIn('Before you start', text)

    def test_sidebar_step_subtitles_hidden_for_inactive_steps(self):
        # Subtitles should only be visible for the active step
        self.page.wait_for_timeout(200)
        subs = self.page.query_selector_all('.guide-step-sub')
        visible_count = sum(1 for s in subs if s.is_visible())
        self.assertEqual(visible_count, 1,
                         f'Only 1 subtitle should be visible (active step), found {visible_count}')

    def test_step_1_subtitle_visible_on_load(self):
        sub = self.page.query_selector('[data-step="1"] .guide-step-sub')
        self.assertTrue(sub.is_visible(), 'Step 1 subtitle should be visible on load')
```

- [ ] **Step 2: Run Playwright tests to confirm RED**

```bash
cd /Users/mdproctor/claude/cc-praxis
python3 -m pytest tests/test_guide_ui.py -v 2>&1 | tail -30
```

Expected: Several tests FAIL. Possible failures:
- `test_first_step_active_on_load` — JS may not fire before timeout
- `test_scroll_to_section_3_*` — IntersectionObserver threshold may differ when served raw
- `test_sidebar_step_subtitles_hidden_for_inactive_steps` — CSS `display:none` check

If ALL pass, the implementation is already correct — that's also a valid outcome.
If specific tests fail, note which ones for Task 5.

- [ ] **Step 3: Commit the Playwright tests**

```bash
git add tests/test_guide_ui.py
git commit -m "test(guide): Playwright e2e test suite — scroll tracking, progress bar, checkmarks"
```

---

## Task 5: Fix Playwright failures — GREEN for all e2e tests

**Files:**
- Modify: `docs/guide.html` (JS section only, if needed)

- [ ] **Step 1: Run Playwright tests and identify failures**

```bash
python3 -m pytest tests/test_guide_ui.py -v --tb=short 2>&1 | grep -E "FAILED|PASSED|ERROR"
```

- [ ] **Step 2: Fix IntersectionObserver timing if needed**

If scroll tests fail due to timing, the rootMargin in the JS needs adjustment for the stripped-frontmatter context. The current observer config:

```javascript
}, { threshold: 0.25, rootMargin: '-10% 0px -60% 0px' });
```

If sections are tall enough (`min-height: 100vh` in the test CSS), the IntersectionObserver should fire correctly. If not, reduce the rootMargin bottom value:

```javascript
}, { threshold: 0.1, rootMargin: '0px 0px -30% 0px' });
```

- [ ] **Step 3: Fix subtitle visibility if needed**

If `test_sidebar_step_subtitles_hidden_for_inactive_steps` fails, verify the CSS `display: none` on `.guide-step-sub` is correct and the JS doesn't inadvertently show all subtitles. The rule:

```css
.guide-step-sub { display: none; }
.guide-step.active .guide-step-sub { display: block; color: #6b7280; }
```

- [ ] **Step 4: Run full suite — all tests must pass**

```bash
python3 -m pytest tests/test_guide_page.py tests/test_guide_ui.py -v 2>&1 | tail -20
```

Expected: All tests PASS. Count should be 30+ tests.

- [ ] **Step 5: Run full project test suite**

```bash
python3 -m pytest tests/ --tb=line 2>&1 | tail -5
```

Expected: All 1110+ tests pass, no regressions.

- [ ] **Step 6: Commit fixes**

```bash
git add docs/guide.html
git commit -m "fix(guide): JS observer tuning for e2e test reliability"
```

(Skip this commit if no fixes were needed.)

---

## Task 6: Final integration and close

**Files:** none new

- [ ] **Step 1: Run complete test suite one final time**

```bash
python3 -m pytest tests/ -q --tb=short 2>&1 | tail -8
```

Expected output pattern:
```
1140+ passed, 1 warning in Xs
```

- [ ] **Step 2: Verify guide renders in browser (manual)**

```bash
# Start the existing web installer server which also serves docs/
cd /Users/mdproctor/claude/cc-praxis
python3 scripts/web_installer.py &
open http://localhost:8765
```

Navigate to the Guide tab/link. Verify:
- [ ] Sidebar shows 12 numbered steps
- [ ] Scrolling highlights the active step
- [ ] Steps scrolled past show ✓ checkmark
- [ ] Progress bar advances
- [ ] All prompt blocks are visible
- [ ] "Next →" links are present

Stop the server when done: `kill %1`

- [ ] **Step 3: Close GitHub issues**

```bash
gh issue close 52 53 56 --repo mdproctor/cc-praxis 2>/dev/null || true
# (Already closed — this is a no-op)
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git status  # verify nothing unexpected
git commit -m "feat(guide): getting started guide — 12 sections, sidebar nav, Playwright e2e tests"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|-----------------|------|
| 12 sections with correct IDs | Task 2 |
| Sticky sidebar with numbered circles | Task 2 |
| IntersectionObserver scroll tracking | Task 2 |
| Progress bar | Task 2 |
| Completed step checkmarks (✓) | Task 2 |
| Prerequisites preamble | Task 2 |
| "WHAT THIS DOES" boxes (12) | Task 2 |
| "INSTALL THIS SKILL" callouts (10) | Task 2 |
| "PROMPT TO TRY" blocks (12) | Task 2 |
| "Next →" transitions (11+) | Task 2 |
| Guide nav link in default.html | Task 3 |
| Structural unit tests | Task 1 |
| Playwright e2e: scroll/active | Task 4 |
| Playwright e2e: progress bar | Task 4 |
| Playwright e2e: checkmarks | Task 4 |
| Playwright e2e: nav click | Task 4 |
| All 12 section titles | Task 2 |
| Sample diary entry (section 12) | Task 2 |

**Placeholder scan:** No TBD, TODO, or placeholder content in any task. All code blocks complete.

**Type consistency:** CSS classes and data attributes used consistently across guide HTML, structural tests, and Playwright tests:
- `.guide-step` + `data-step="N"` — ✓ consistent
- `.guide-section` + `data-section="N"` + `id="section-N"` — ✓ consistent
- `.guide-step-circle`, `.guide-step-sub`, `.guide-step.active`, `.guide-step.done` — ✓ consistent
- `#guide-progress` (progress fill element) — ✓ consistent
- `.what-it-does`, `.install-callout`, `.prompt-block`, `.section-next` — ✓ consistent
