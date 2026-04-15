import pytest
import sys
from test_base import is_critical, is_warning, is_note
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validation.validate_project_types import (
    extract_canonical_types,
    find_hardcoded_lists,
    _build_list_pattern,
    validate,
)

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers — compare by severity name to avoid module-identity issues
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_claude_md(tmp_path: Path, types: list) -> Path:
    """Write a CLAUDE.md with a Project Types table listing the given types."""
    rows = "\n".join(
        f"| **`{t}`** | Description for {t} |" for t in types
    )
    content = (
        "# CLAUDE.md\n\n"
        "## Project Type Awareness\n\n"
        "| Type | When to Use |\n"
        "|------|-------------|\n"
        + rows + "\n\n"
        "## Other Section\n\nSome other content.\n"
    )
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(content)
    return claude_md


def make_file(tmp_path: Path, name: str, content: str) -> Path:
    f = tmp_path / name
    f.write_text(content)
    return f


# ---------------------------------------------------------------------------
# extract_canonical_types unit tests
# ---------------------------------------------------------------------------

class TestExtractCanonicalTypes:
    def test_extracts_types_from_valid_claude_md(self, tmp_path):
        write_claude_md(tmp_path, ["skills", "java", "blog", "generic"])
        types, error = extract_canonical_types(tmp_path)
        assert error == ""
        assert set(types) == {"skills", "java", "blog", "generic"}

    def test_missing_claude_md_returns_error(self, tmp_path):
        types, error = extract_canonical_types(tmp_path)
        assert error != ""
        assert types == []

    def test_claude_md_without_project_types_table_returns_error(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("# No table here\n")
        types, error = extract_canonical_types(tmp_path)
        assert error != ""
        assert types == []

    def test_single_type_still_extracted(self, tmp_path):
        write_claude_md(tmp_path, ["skills"])
        types, error = extract_canonical_types(tmp_path)
        assert error == ""
        assert "skills" in types

    def test_three_types_all_extracted(self, tmp_path):
        write_claude_md(tmp_path, ["alpha", "beta", "gamma"])
        types, error = extract_canonical_types(tmp_path)
        assert error == ""
        assert set(types) == {"alpha", "beta", "gamma"}


# ---------------------------------------------------------------------------
# _build_list_pattern and find_hardcoded_lists unit tests
# ---------------------------------------------------------------------------

class TestFindHardcodedLists:
    def test_complete_pipe_list_no_issues(self, tmp_path):
        canonical = ["skills", "java", "blog", "generic"]
        pattern = _build_list_pattern(canonical)
        content = "Choices: skills | java | blog | generic\n"  # nocheck:project-types
        f = make_file(tmp_path, "complete.md", content)
        issues = find_hardcoded_lists(f, canonical, pattern)
        assert issues == []

    def test_missing_type_in_pipe_list_is_critical(self, tmp_path):
        canonical = ["skills", "java", "blog", "generic"]
        pattern = _build_list_pattern(canonical)
        # "generic" is missing — only 3 listed, pattern requires 3+
        content = "Choices: skills | java | blog\n"  # nocheck:project-types
        f = make_file(tmp_path, "incomplete.md", content)
        issues = find_hardcoded_lists(f, canonical, pattern)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("generic" in i.message for i in critical)

    def test_suppress_marker_skips_line(self, tmp_path):
        canonical = ["skills", "java", "blog", "generic"]
        pattern = _build_list_pattern(canonical)
        f = make_file(
            tmp_path, "suppressed.md",
            "Choices: skills | java | blog  # nocheck:project-types\n"
        )
        issues = find_hardcoded_lists(f, canonical, pattern)
        assert issues == []

    def test_two_types_in_prose_not_flagged(self, tmp_path):
        canonical = ["skills", "java", "blog", "generic"]
        pattern = _build_list_pattern(canonical)
        # Only 2 types mentioned — not a 3+ consecutive delimited list
        f = make_file(
            tmp_path, "prose.md",
            "This applies to java and skills projects primarily.\n"
        )
        issues = find_hardcoded_lists(f, canonical, pattern)
        assert issues == []

    def test_complete_comma_list_no_issues(self, tmp_path):
        canonical = ["skills", "java", "blog", "generic"]
        pattern = _build_list_pattern(canonical)
        content = "Types: skills, java, blog, generic\n"  # nocheck:project-types
        f = make_file(tmp_path, "comma.md", content)
        issues = find_hardcoded_lists(f, canonical, pattern)
        assert issues == []

    def test_missing_type_in_comma_list_is_critical(self, tmp_path):
        canonical = ["skills", "java", "blog", "generic"]
        pattern = _build_list_pattern(canonical)
        # Missing "blog"
        content = "Types: skills, java, generic\n"  # nocheck:project-types
        f = make_file(tmp_path, "comma_incomplete.md", content)
        issues = find_hardcoded_lists(f, canonical, pattern)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("blog" in i.message for i in critical)

    def test_html_suppression_marker_skips_line(self, tmp_path):
        canonical = ["skills", "java", "blog", "generic"]
        pattern = _build_list_pattern(canonical)
        f = make_file(
            tmp_path, "html_suppressed.md",
            "Choices: skills | java | blog <!-- nocheck:project-types -->\n"
        )
        issues = find_hardcoded_lists(f, canonical, pattern)
        assert issues == []

    def test_custom_types_missing_one_is_flagged(self, tmp_path):
        canonical = ["alpha", "beta", "gamma", "delta"]
        pattern = _build_list_pattern(canonical)
        f = make_file(
            tmp_path, "custom.md",
            "Options: alpha | beta | gamma\n"  # delta missing
        )
        issues = find_hardcoded_lists(f, canonical, pattern)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("delta" in i.message for i in critical)

    def test_custom_types_all_present_passes(self, tmp_path):
        canonical = ["alpha", "beta", "gamma", "delta"]
        pattern = _build_list_pattern(canonical)
        f = make_file(
            tmp_path, "custom_full.md",
            "Options: alpha | beta | gamma | delta\n"
        )
        issues = find_hardcoded_lists(f, canonical, pattern)
        assert issues == []


# ---------------------------------------------------------------------------
# validate() full-run tests
# ---------------------------------------------------------------------------

class TestValidateFull:
    def test_validate_returns_result_object(self):
        result = validate()
        assert result.validator_name == "Project Type List Consistency"
        assert result.files_checked >= 0

    def test_current_repo_passes_with_no_critical(self):
        """The real repository must pass project type list consistency."""
        result = validate()
        critical = [i for i in result.issues if is_critical(i)]
        assert critical == [], (
            "Project type validation found CRITICAL issues:\n"
            + "\n".join(str(i) for i in critical)
        )


# ---------------------------------------------------------------------------
# Happy path: subprocess invocation
# ---------------------------------------------------------------------------

class TestProjectTypesViaSubprocess:
    def test_validator_exits_cleanly_on_real_repo(self):
        result = subprocess.run(
            ["python3", "scripts/validation/validate_project_types.py", "--verbose"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode in (0, 3), (
            f"Project-types validator reported unexpected issues:\n"
            f"{result.stdout}\n{result.stderr}"
        )
