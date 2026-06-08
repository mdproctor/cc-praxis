#!/usr/bin/env python3
"""
Tests for work-start/flyway_scan.py

Uses real git repos (tmp_path) with migration files. Covers: no migrations,
single branch, conflict detection, compound V-numbers, offline scan flag,
bad project path.
"""

import subprocess
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parent.parent / "work-start" / "flyway_scan.py"


def run(project: Path, base_branch: str = "main") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(project), base_branch],
        capture_output=True, text=True,
    )


def parse(result: subprocess.CompletedProcess) -> dict:
    return dict(line.split("=", 1) for line in result.stdout.strip().splitlines() if "=" in line)


def git(*args, cwd: Path) -> None:
    subprocess.run(["git"] + list(args), cwd=str(cwd), capture_output=True, check=True)


def make_repo(path: Path) -> Path:
    path.mkdir(parents=True)
    git("init", cwd=path)
    git("config", "user.email", "test@test.com", cwd=path)
    git("config", "user.name", "Test", cwd=path)
    return path


def commit_migration(repo: Path, v: str, name: str = "migration") -> None:
    f = repo / f"V{v}__{name}.sql"
    f.write_text(f"-- V{v}\n")
    git("add", ".", cwd=repo)
    git("commit", "-m", f"add V{v}", cwd=repo)


# ---------------------------------------------------------------------------
# No migrations
# ---------------------------------------------------------------------------

class TestNoMigrations:

    def test_next_safe_is_1_with_no_migrations(self, tmp_path):
        repo = make_repo(tmp_path / "repo")
        # Need at least one commit for git ls-tree to work
        (repo / "README.md").write_text("hello\n")
        git("add", ".", cwd=repo)
        git("commit", "-m", "init", cwd=repo)
        result = run(repo)
        out = parse(result)
        assert out["NEXT_SAFE_V"] == "1"
        assert out["MAX_V"] == "0"
        assert out["CONFLICT"] == "no"

    def test_empty_repo_returns_next_safe_1(self, tmp_path):
        repo = make_repo(tmp_path / "repo")
        (repo / "README.md").write_text("hello\n")
        git("add", ".", cwd=repo)
        git("commit", "-m", "init", cwd=repo)
        out = parse(run(repo))
        assert out["NEXT_SAFE_V"] == "1"


# ---------------------------------------------------------------------------
# Single branch
# ---------------------------------------------------------------------------

class TestSingleBranch:

    def test_max_v_is_highest_migration(self, tmp_path):
        repo = make_repo(tmp_path / "repo")
        commit_migration(repo, "1", "init")
        commit_migration(repo, "2", "add_users")
        commit_migration(repo, "5", "add_orders")
        out = parse(run(repo))
        assert out["MAX_V"] == "5"
        assert out["NEXT_SAFE_V"] == "6"
        assert out["CONFLICT"] == "no"

    def test_next_safe_increments_from_max(self, tmp_path):
        repo = make_repo(tmp_path / "repo")
        commit_migration(repo, "10", "big_schema")
        out = parse(run(repo))
        assert out["NEXT_SAFE_V"] == "11"


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:

    def test_detects_conflict_on_two_branches(self, tmp_path):
        repo = make_repo(tmp_path / "repo")
        commit_migration(repo, "1", "init")
        # Branch A claims V2
        git("checkout", "-b", "branch-a", cwd=repo)
        commit_migration(repo, "2", "branch_a_migration")
        # Main also claims V2
        git("checkout", "main", cwd=repo)
        commit_migration(repo, "2", "main_migration")
        out = parse(run(repo))
        assert out["CONFLICT"] == "yes"
        assert out["CONFLICT_V"] == "2"
        assert "branch-a" in out.get("CONFLICT_BRANCHES", "")
        assert "main" in out.get("CONFLICT_BRANCHES", "")

    def test_no_conflict_when_branches_use_different_versions(self, tmp_path):
        repo = make_repo(tmp_path / "repo")
        commit_migration(repo, "1", "init")
        git("checkout", "-b", "feature", cwd=repo)
        commit_migration(repo, "2", "feature_migration")
        git("checkout", "main", cwd=repo)
        commit_migration(repo, "3", "main_migration")
        out = parse(run(repo))
        assert out["CONFLICT"] == "no"
        assert out["MAX_V"] == "3"
        assert out["NEXT_SAFE_V"] == "4"


# ---------------------------------------------------------------------------
# Compound V-numbers
# ---------------------------------------------------------------------------

class TestCompoundVersions:

    def test_handles_compound_v_number(self, tmp_path):
        repo = make_repo(tmp_path / "repo")
        (repo / "V2.1__compound.sql").write_text("-- compound\n")
        git("add", ".", cwd=repo)
        git("commit", "-m", "compound migration", cwd=repo)
        out = parse(run(repo))
        assert out["MAX_V"] == "2.1"
        assert out["NEXT_SAFE_V"] == "3"  # uses int part of compound


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestErrorCases:

    def test_exits_1_for_missing_project_path(self, tmp_path):
        result = run(tmp_path / "nonexistent")
        assert result.returncode == 1

    def test_exits_1_for_non_git_directory(self, tmp_path):
        not_git = tmp_path / "notgit"
        not_git.mkdir()
        result = run(not_git)
        assert result.returncode == 1

    def test_exits_1_when_no_args(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 1
