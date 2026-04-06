"""Unit tests for retro-parse-mapping.py"""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("retro-issues/scripts/retro-parse-mapping.py")
FIXTURES = Path("tests/fixtures/retro/parser")


def run_parser(fixture_name: str) -> dict[str, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / fixture_name)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Parser failed: {result.stderr}"
    return json.loads(result.stdout)


def test_basic_two_commit_issue_refs_and_closes() -> None:
    """First commit gets Refs, last commit gets Closes."""
    mapping = run_parser("basic.md")
    assert mapping["abc1234"] == "Refs #12"
    assert mapping["def5678"] == "Closes #12"


def test_basic_single_commit_issue_gets_closes() -> None:
    """Single-commit issues always get Closes, not Refs."""
    mapping = run_parser("basic.md")
    assert mapping["cafe012"] == "Closes #13"


def test_basic_standalone_issue() -> None:
    """Standalone issues outside epics are also mapped."""
    mapping = run_parser("basic.md")
    assert mapping["beef456"] == "Closes #20"


def test_basic_excluded_commits_absent() -> None:
    """Commits in the Excluded table must not appear in the mapping."""
    mapping = run_parser("basic.md")
    assert "dead890" not in mapping


def test_tbd_placeholders_skipped() -> None:
    """Issues with #TBD have no real number — commits should not appear."""
    mapping = run_parser("tbd_placeholders.md")
    assert "aaa1111" not in mapping
    assert "bbb2222" not in mapping


def test_excluded_only_produces_empty_mapping() -> None:
    """A file with only excluded commits produces an empty mapping."""
    mapping = run_parser("excluded_only.md")
    assert mapping == {}


def test_nonexistent_file_exits_nonzero() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "nonexistent_file.md"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr
