#!/usr/bin/env python3
"""Tests for scripts/validation/validate_doc_structure.py"""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "validation"))
from validate_doc_structure import (
    analyse, read_threshold, is_nudge_enabled,
    count_sections, find_module_links, DEFAULT_THRESHOLD
)


def make_doc(directory: Path, name: str, lines: int,
             sections: list[str] = None, links: list[str] = None) -> Path:
    """Create a test document with the specified number of lines."""
    path = directory / name
    content = []

    # Add sections
    if sections:
        for section in sections:
            content.append(f"## {section}")
            content.append("")
            # Fill section with content lines
            per_section = max(1, (lines - len(sections) * 3) // len(sections))
            content.extend([f"Content line {i}" for i in range(per_section)])
            content.append("")
    else:
        content.extend([f"Line {i}" for i in range(lines)])

    # Pad to requested line count (before adding links so they aren't sliced off)
    while len(content) < lines:
        content.append("padding")
    content = content[:lines]

    # Add module links after padding (always preserved)
    if links:
        content.append("")
        for link in links:
            content.append(f"See [{link}]({link}.md) for details.")

    path.write_text("\n".join(content))
    return path


def make_claude_md(directory: Path, threshold: int = None,
                   nudge_enabled: bool = True) -> Path:
    path = directory / "CLAUDE.md"
    parts = ["# CLAUDE.md\n\n## Document Structure\n"]
    nudge_val = "enabled" if nudge_enabled else "disabled"
    parts.append(f"**Modular doc nudge:** {nudge_val}")
    if threshold is not None:
        parts.append(f"**Threshold:** {threshold} lines")
    path.write_text("\n".join(parts))
    return path


class TestReadThreshold(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_when_no_claude_md(self):
        self.assertEqual(read_threshold(self.d / "missing.md"), DEFAULT_THRESHOLD)

    def test_reads_configured_threshold(self):
        make_claude_md(self.d, threshold=600)
        self.assertEqual(read_threshold(self.d / "CLAUDE.md"), 600)

    def test_default_when_section_absent(self):
        (self.d / "CLAUDE.md").write_text("# CLAUDE.md\n\nNo structure section here.")
        self.assertEqual(read_threshold(self.d / "CLAUDE.md"), DEFAULT_THRESHOLD)

    def test_reads_various_threshold_values(self):
        for threshold in (200, 400, 800, 1000):
            make_claude_md(self.d, threshold=threshold)
            self.assertEqual(read_threshold(self.d / "CLAUDE.md"), threshold)


class TestIsNudgeEnabled(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_enabled_by_default_when_no_claude_md(self):
        self.assertTrue(is_nudge_enabled(self.d / "missing.md"))

    def test_enabled_when_configured(self):
        make_claude_md(self.d, nudge_enabled=True)
        self.assertTrue(is_nudge_enabled(self.d / "CLAUDE.md"))

    def test_disabled_when_configured(self):
        make_claude_md(self.d, nudge_enabled=False)
        self.assertFalse(is_nudge_enabled(self.d / "CLAUDE.md"))


class TestCountSections(unittest.TestCase):

    def test_counts_h2_sections(self):
        lines = ["# Title", "## Section 1", "content", "## Section 2", "more content"]
        self.assertEqual(count_sections(lines), ["Section 1", "Section 2"])

    def test_ignores_h1_and_h3(self):
        lines = ["# Title", "### Subsection", "## Real Section"]
        self.assertEqual(count_sections(lines), ["Real Section"])

    def test_empty_document(self):
        self.assertEqual(count_sections([]), [])


class TestFindModuleLinks(unittest.TestCase):

    def test_finds_md_links(self):
        content = "See [Architecture](docs/architecture.md) for details."
        self.assertEqual(find_module_links(content), ["docs/architecture.md"])

    def test_ignores_external_urls(self):
        content = "See [GitHub](https://github.com/foo/bar.md) for details."
        self.assertEqual(find_module_links(content), [])

    def test_finds_multiple_links(self):
        content = (
            "[Architecture](docs/arch.md)\n"
            "[API](docs/api.md)\n"
            "[External](https://example.com)"
        )
        links = find_module_links(content)
        self.assertIn("docs/arch.md", links)
        self.assertIn("docs/api.md", links)
        self.assertEqual(len(links), 2)

    def test_no_links(self):
        self.assertEqual(find_module_links("Just plain text."), [])


class TestAnalyseNudge(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_nudge_below_threshold(self):
        doc = make_doc(self.d, "DESIGN.md", lines=300)
        claude_md = make_claude_md(self.d, threshold=400)
        result = analyse(doc, claude_md)
        self.assertFalse(result["nudge"])
        self.assertFalse(result["review_structure"])

    def test_nudge_at_threshold(self):
        doc = make_doc(self.d, "DESIGN.md", lines=400)
        claude_md = make_claude_md(self.d, threshold=400)
        result = analyse(doc, claude_md)
        self.assertTrue(result["nudge"])

    def test_nudge_above_threshold(self):
        doc = make_doc(self.d, "DESIGN.md", lines=600)
        claude_md = make_claude_md(self.d, threshold=400)
        result = analyse(doc, claude_md)
        self.assertTrue(result["nudge"])
        self.assertIn("600", result["reason"])

    def test_no_nudge_when_disabled(self):
        doc = make_doc(self.d, "DESIGN.md", lines=800)
        claude_md = make_claude_md(self.d, threshold=400, nudge_enabled=False)
        result = analyse(doc, claude_md)
        self.assertFalse(result["nudge"])

    def test_uses_default_threshold_without_claude_md(self):
        doc = make_doc(self.d, "DESIGN.md", lines=DEFAULT_THRESHOLD + 10)
        result = analyse(doc, self.d / "missing.md")
        self.assertTrue(result["nudge"])
        self.assertEqual(result["threshold"], DEFAULT_THRESHOLD)

    def test_custom_threshold_from_claude_md(self):
        # At 399 lines with threshold 600 — no nudge
        doc = make_doc(self.d, "DESIGN.md", lines=399)
        claude_md = make_claude_md(self.d, threshold=600)
        result = analyse(doc, claude_md)
        self.assertFalse(result["nudge"])

    def test_error_when_doc_missing(self):
        result = analyse(self.d / "missing.md", self.d / "CLAUDE.md")
        self.assertIn("error", result)


class TestAnalyseModular(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_already_modular_no_nudge(self):
        doc = make_doc(self.d, "DESIGN.md", lines=600,
                       links=["docs/architecture", "docs/api"])
        claude_md = make_claude_md(self.d, threshold=400)
        result = analyse(doc, claude_md)
        self.assertTrue(result["already_modular"])
        self.assertFalse(result["nudge"])

    def test_already_modular_many_sections_suggests_review(self):
        sections = [f"Section {i}" for i in range(9)]
        doc = make_doc(self.d, "DESIGN.md", lines=600,
                       sections=sections, links=["docs/arch"])
        claude_md = make_claude_md(self.d, threshold=400)
        result = analyse(doc, claude_md)
        self.assertTrue(result["already_modular"])
        self.assertTrue(result["review_structure"])
        self.assertFalse(result["nudge"])

    def test_module_links_detected(self):
        doc = make_doc(self.d, "DESIGN.md", lines=100,
                       links=["docs/architecture", "docs/api"])
        result = analyse(doc, self.d / "CLAUDE.md")
        self.assertTrue(result["already_modular"])
        self.assertIn("docs/architecture.md", result["module_links"])

    def test_section_names_in_result(self):
        sections = ["Architecture", "API", "Data Model"]
        doc = make_doc(self.d, "DESIGN.md", lines=500, sections=sections)
        claude_md = make_claude_md(self.d, threshold=400)
        result = analyse(doc, claude_md)
        self.assertTrue(result["nudge"])
        self.assertIn("Architecture", result["sections"])
        self.assertIn("API", result["sections"])


class TestThresholdAdjustment(unittest.TestCase):
    """Verify threshold values persist correctly — the core of 'remember user preference'."""

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_threshold_increase_suppresses_nudge(self):
        """User says 'too frequent' — threshold bumped — same doc no longer nudges."""
        doc = make_doc(self.d, "DESIGN.md", lines=450)

        # With default threshold (400): nudge fires
        make_claude_md(self.d, threshold=400)
        result = analyse(doc, self.d / "CLAUDE.md")
        self.assertTrue(result["nudge"])

        # User adjusts to 600: nudge suppressed
        make_claude_md(self.d, threshold=600)
        result = analyse(doc, self.d / "CLAUDE.md")
        self.assertFalse(result["nudge"])

    def test_threshold_decrease_triggers_nudge(self):
        """User says 'too late' — threshold lowered — smaller doc now nudges."""
        doc = make_doc(self.d, "DESIGN.md", lines=250)

        # With default threshold (400): no nudge
        make_claude_md(self.d, threshold=400)
        result = analyse(doc, self.d / "CLAUDE.md")
        self.assertFalse(result["nudge"])

        # User adjusts to 200: nudge fires
        make_claude_md(self.d, threshold=200)
        result = analyse(doc, self.d / "CLAUDE.md")
        self.assertTrue(result["nudge"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
