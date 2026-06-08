#!/usr/bin/env python3
"""
Tests for workspace-init/create_symlinks.py

Covers: happy path, idempotent re-run, pre-existing symlinks, non-symlink
path conflicts, missing dirs, .gitignore update behaviour.
"""

import subprocess
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parent.parent / "workspace-init" / "create_symlinks.py"


def run(workspace: Path, project: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(workspace), str(project)],
        capture_output=True, text=True,
    )


def parse_output(result: subprocess.CompletedProcess) -> dict:
    return dict(line.split("=", 1) for line in result.stdout.strip().splitlines() if "=" in line)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestHappyPath:

    def test_creates_proj_symlink_in_workspace(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        result = run(ws, proj)
        assert result.returncode == 0
        assert (ws / "proj").is_symlink()
        assert (ws / "proj").resolve() == proj

    def test_creates_wksp_symlink_in_project(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        result = run(ws, proj)
        assert result.returncode == 0
        assert (proj / "wksp").is_symlink()
        assert (proj / "wksp").resolve() == ws

    def test_adds_wksp_to_gitignore_when_absent(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        run(ws, proj)
        gitignore = proj / ".gitignore"
        assert gitignore.exists()
        assert "wksp" in gitignore.read_text().splitlines()

    def test_output_contains_all_keys(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        result = run(ws, proj)
        out = parse_output(result)
        assert "PROJ_SYMLINK" in out
        assert "WKSP_SYMLINK" in out
        assert "GITIGNORE_UPDATED" in out

    def test_gitignore_updated_yes_when_newly_added(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        result = run(ws, proj)
        out = parse_output(result)
        assert out["GITIGNORE_UPDATED"] == "yes"

    def test_gitignore_updated_no_when_already_present(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        (proj / ".gitignore").write_text("wksp\n")
        result = run(ws, proj)
        out = parse_output(result)
        assert out["GITIGNORE_UPDATED"] == "no"

    def test_preserves_existing_gitignore_content(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        (proj / ".gitignore").write_text("*.pyc\n__pycache__\n")
        run(ws, proj)
        content = (proj / ".gitignore").read_text()
        assert "*.pyc" in content
        assert "__pycache__" in content
        assert "wksp" in content


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

class TestIdempotency:

    def test_reruns_cleanly_when_symlinks_already_exist(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        run(ws, proj)
        result = run(ws, proj)  # second run
        assert result.returncode == 0
        assert (ws / "proj").resolve() == proj
        assert (proj / "wksp").resolve() == ws

    def test_updates_stale_symlink_to_correct_target(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        other = tmp_path / "other"
        ws.mkdir(); proj.mkdir(); other.mkdir()
        # Create a stale proj/ pointing at wrong target
        (ws / "proj").symlink_to(other)
        result = run(ws, proj)
        assert result.returncode == 0
        assert (ws / "proj").resolve() == proj


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestErrorCases:

    def test_exits_1_when_workspace_missing(self, tmp_path):
        proj = tmp_path / "project"
        proj.mkdir()
        result = run(tmp_path / "nonexistent", proj)
        assert result.returncode == 1
        assert "ERROR=" in result.stdout

    def test_exits_1_when_project_missing(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        result = run(ws, tmp_path / "nonexistent")
        assert result.returncode == 1
        assert "ERROR=" in result.stdout

    def test_exits_1_when_proj_path_is_regular_file(self, tmp_path):
        ws = tmp_path / "workspace"
        proj = tmp_path / "project"
        ws.mkdir(); proj.mkdir()
        (ws / "proj").write_text("not a symlink")  # regular file
        result = run(ws, proj)
        assert result.returncode == 1
        assert "ERROR=" in result.stdout

    def test_exits_1_when_no_args(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True,
        )
        assert result.returncode == 1

    def test_exits_1_when_only_one_arg(self, tmp_path):
        ws = tmp_path / "workspace"
        ws.mkdir()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(ws)],
            capture_output=True, text=True,
        )
        assert result.returncode == 1
