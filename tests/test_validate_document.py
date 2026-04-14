"""
Tests for scripts/validate_document.py

Creates temporary markdown files — does not rely on any real project documents.
"""

import sys
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validate_document import (
    validate_document,
    find_duplicate_headers,
    find_corrupted_tables,
    find_orphaned_sections,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_doc(tmp_path: Path, content: str) -> Path:
    """Write content to a temporary .md file and return the path."""
    p = tmp_path / "doc.md"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# find_duplicate_headers
# ---------------------------------------------------------------------------

class TestFindDuplicateHeaders:
    def test_no_duplicates_returns_empty(self, tmp_path):
        doc = write_doc(tmp_path, "## Alpha\n\nContent.\n\n## Beta\n\nContent.\n")
        assert find_duplicate_headers(doc) == []

    def test_duplicate_header_detected_with_line_numbers(self, tmp_path):
        doc = write_doc(tmp_path, "## Alpha\n\nContent.\n\n## Alpha\n\nMore.\n")
        dupes = find_duplicate_headers(doc)
        assert len(dupes) == 1
        header, lines = dupes[0]
        assert header == "## Alpha"
        assert len(lines) == 2
        assert 1 in lines
        assert 5 in lines

    def test_headers_inside_code_blocks_not_flagged(self, tmp_path):
        content = "## Real Header\n\nContent.\n\n```\n## Not a header\n```\n\n## Another\n\nContent.\n"
        doc = write_doc(tmp_path, content)
        assert find_duplicate_headers(doc) == []

    def test_h1_and_h3_not_counted_as_h2_duplicates(self, tmp_path):
        content = "# Title\n\n## Alpha\n\n### Sub\n\n## Beta\n\nContent.\n"
        doc = write_doc(tmp_path, content)
        assert find_duplicate_headers(doc) == []

    def test_three_occurrences_reported_correctly(self, tmp_path):
        content = "## Dup\n\nA.\n\n## Dup\n\nB.\n\n## Dup\n\nC.\n"
        doc = write_doc(tmp_path, content)
        dupes = find_duplicate_headers(doc)
        assert len(dupes) == 1
        header, lines = dupes[0]
        assert len(lines) == 3


# ---------------------------------------------------------------------------
# find_corrupted_tables
# ---------------------------------------------------------------------------

class TestFindCorruptedTables:
    def test_valid_table_passes(self, tmp_path):
        content = (
            "## Section\n\n"
            "| Col A | Col B |\n"
            "| ----- | ----- |\n"
            "| val1  | val2  |\n"
        )
        doc = write_doc(tmp_path, content)
        assert find_corrupted_tables(doc) == []

    def test_table_without_separator_row_is_detected(self, tmp_path):
        content = (
            "## Section\n\n"
            "| Col A | Col B |\n"
            "This is prose, not a separator row.\n"
        )
        doc = write_doc(tmp_path, content)
        corrupted = find_corrupted_tables(doc)
        assert len(corrupted) >= 1
        assert corrupted[0]["line"] is not None

    def test_tables_inside_code_blocks_not_flagged(self, tmp_path):
        content = (
            "## Section\n\n"
            "```\n"
            "| Col A | Col B |\n"
            "Prose after table header in code block.\n"
            "```\n"
        )
        doc = write_doc(tmp_path, content)
        assert find_corrupted_tables(doc) == []

    def test_table_followed_by_blank_line_is_fine(self, tmp_path):
        """A lone header row followed by a blank line is treated as an ended table, not corruption."""
        content = "| Col A | Col B |\n\nProse continues here.\n"
        doc = write_doc(tmp_path, content)
        assert find_corrupted_tables(doc) == []


# ---------------------------------------------------------------------------
# validate_document (full integration)
# ---------------------------------------------------------------------------

class TestValidateDocument:
    def test_valid_document_returns_no_issues(self, tmp_path):
        content = (
            "## Introduction\n\nThis is a valid document.\n\n"
            "## Usage\n\nUse it like this.\n\n"
            "| Key | Value |\n"
            "| --- | ----- |\n"
            "| a   | b     |\n"
        )
        doc = write_doc(tmp_path, content)
        result = validate_document(doc)
        assert result["critical"] == []

    def test_duplicate_header_is_critical(self, tmp_path):
        content = "## Section\n\nContent.\n\n## Section\n\nMore content.\n"
        doc = write_doc(tmp_path, content)
        result = validate_document(doc)
        assert len(result["critical"]) >= 1
        assert any("Section" in c for c in result["critical"])

    def test_corrupted_table_is_critical(self, tmp_path):
        content = (
            "## Section\n\n"
            "| Col A | Col B |\n"
            "Prose where separator should be.\n"
        )
        doc = write_doc(tmp_path, content)
        result = validate_document(doc)
        assert len(result["critical"]) >= 1

    def test_multiple_issues_all_reported(self, tmp_path):
        """Both a duplicate header and a corrupted table must be reported."""
        content = (
            "## Dup\n\nContent.\n\n"
            "## Dup\n\nMore content.\n\n"
            "| A | B |\n"
            "Not a separator.\n"
        )
        doc = write_doc(tmp_path, content)
        result = validate_document(doc)
        assert len(result["critical"]) >= 2

    def test_empty_document_handled_gracefully(self, tmp_path):
        doc = write_doc(tmp_path, "")
        result = validate_document(doc)
        # Should not raise; no critical issues for empty document
        assert isinstance(result, dict)
        assert "critical" in result
        assert "warnings" in result
        assert result["critical"] == []

    def test_nonexistent_file_returns_critical(self, tmp_path):
        missing = tmp_path / "nonexistent.md"
        result = validate_document(missing)
        assert len(result["critical"]) >= 1
        assert any("not found" in c.lower() or "nonexistent" in c for c in result["critical"])

    def test_headers_in_code_blocks_not_flagged_as_duplicates(self, tmp_path):
        content = (
            "## Real Section\n\n"
            "```\n"
            "## Real Section\n"
            "```\n\n"
            "## Another Section\n\nContent.\n"
        )
        doc = write_doc(tmp_path, content)
        result = validate_document(doc)
        assert result["critical"] == []

    def test_orphaned_section_is_warning(self, tmp_path):
        content = (
            "## HasContent\n\nSome text here.\n\n"
            "## EmptySection\n\n"
            "## AlsoHasContent\n\nMore text.\n"
        )
        doc = write_doc(tmp_path, content)
        result = validate_document(doc)
        assert len(result["warnings"]) >= 1
