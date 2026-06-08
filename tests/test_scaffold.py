#!/usr/bin/env python3
"""
Tests for work-start/scaffold.py

Covers: happy path field writing, idempotency, missing workspace,
missing required params, defaults, .meta format correctness.
"""

import subprocess
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parent.parent / "work-start" / "scaffold.py"


def run(workspace: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(workspace)] + list(extra_args),
        capture_output=True, text=True,
    )


def parse(result: subprocess.CompletedProcess) -> dict:
    return dict(line.split("=", 1) for line in result.stdout.strip().splitlines() if "=" in line)


def required_args(**overrides) -> list[str]:
    defaults = {
        "branch": "issue-42-auth-flow",
        "project-sha": "abc1234",
        "date": "2026-06-08",
    }
    defaults.update(overrides)
    return [f"{k}={v}" for k, v in defaults.items()]


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestHappyPath:

    def test_creates_design_directory(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args())
        assert (ws / "design").is_dir()

    def test_creates_meta_file(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args())
        assert (ws / "design" / ".meta").exists()

    def test_creates_journal_md(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args())
        assert (ws / "design" / "JOURNAL.md").exists()

    def test_journal_contains_branch_heading(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args(branch="issue-99-payments"))
        content = (ws / "design" / "JOURNAL.md").read_text()
        assert "issue-99-payments" in content

    def test_meta_contains_all_required_fields(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args(branch="issue-42-auth", **{"project-sha": "deadbeef"}))
        meta = (ws / "design" / ".meta").read_text()
        assert "branch: issue-42-auth" in meta
        assert "project-sha: deadbeef" in meta

    def test_meta_optional_fields_written(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args(
            issue="42",
            covers="42,43",
            **{"flyway-next-v": "17", "design-repo": "workspace"}
        ))
        meta = (ws / "design" / ".meta").read_text()
        assert "issue: 42" in meta
        assert "covers: 42,43" in meta
        assert "flyway-next-v: 17" in meta
        assert "design-repo: workspace" in meta

    def test_output_contains_meta_and_journal_paths(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        result = run(ws, *required_args())
        out = parse(result)
        assert "META_PATH" in out
        assert "JOURNAL_PATH" in out
        assert out["CREATED"] == "yes"

    def test_creates_nested_design_dir(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        # design/ doesn't exist yet
        run(ws, *required_args())
        assert (ws / "design" / ".meta").exists()


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

class TestIdempotency:

    def test_second_run_does_not_overwrite(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args(branch="issue-42-auth"))
        # Manually modify the meta
        meta = ws / "design" / ".meta"
        meta.write_text("branch: modified\n")
        run(ws, *required_args(branch="issue-42-auth"))
        assert "modified" in meta.read_text()  # not overwritten

    def test_second_run_returns_created_no(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args())
        result = run(ws, *required_args())
        out = parse(result)
        assert out["CREATED"] == "no"


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

class TestDefaults:

    def test_flyway_defaults_to_unknown(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args())
        meta = (ws / "design" / ".meta").read_text()
        assert "flyway-next-v: unknown" in meta

    def test_design_repo_defaults_to_project(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args())
        meta = (ws / "design" / ".meta").read_text()
        assert "design-repo: project" in meta

    def test_covers_defaults_to_issue_when_given(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        run(ws, *required_args(issue="55"))
        meta = (ws / "design" / ".meta").read_text()
        assert "covers: 55" in meta


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestErrorCases:

    def test_exits_1_when_workspace_missing(self, tmp_path):
        result = run(tmp_path / "nonexistent", *required_args())
        assert result.returncode == 1

    def test_exits_1_when_branch_missing(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        result = run(ws, "project-sha=abc")
        assert result.returncode == 1

    def test_exits_1_when_project_sha_missing(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        result = run(ws, "branch=issue-42")
        assert result.returncode == 1

    def test_exits_1_when_no_args(self, tmp_path):
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 1
