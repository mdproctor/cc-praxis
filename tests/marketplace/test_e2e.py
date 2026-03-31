"""
End-to-end integration tests for marketplace CLI.

These tests verify the complete workflow using real subprocess execution.
They require network access to fetch from GitHub and are marked @pytest.mark.slow.

Run with: pytest tests/marketplace/test_e2e.py -v -m slow
Skip with: pytest -m "not slow"
"""

import pytest
import tempfile
import json
import subprocess
import sys
import os
from pathlib import Path


def get_test_env():
    """Get environment with PYTHONPATH set to repository root."""
    env = os.environ.copy()
    repo_root = Path(__file__).parent.parent.parent.absolute()
    env["PYTHONPATH"] = str(repo_root)
    return env


@pytest.mark.slow
@pytest.mark.skip(reason="Requires registry to be published (Task 20)")
def test_e2e_install_real_skill():
    """End-to-end test: Install real skill from GitHub (requires network)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Run CLI as subprocess with PYTHONPATH set
        result = subprocess.run(
            [
                sys.executable,
                "scripts/marketplace/cli.py",
                "install",
                "code-review-principles",
                "--marketplace-dir",
                str(marketplace_dir)
            ],
            input="y\n",  # Auto-confirm installation
            capture_output=True,
            text=True,
            env=get_test_env()
        )

        # Verify success
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Verify files exist
        skill_dir = marketplace_dir / "code-review-principles"
        assert skill_dir.exists(), "Skill directory not created"
        assert (skill_dir / "SKILL.md").exists(), "SKILL.md not found"
        assert (skill_dir / "skill.json").exists(), "skill.json not found"

        # Verify metadata
        with open(skill_dir / "skill.json") as f:
            metadata = json.load(f)

        assert metadata["name"] == "code-review-principles"
        assert "version" in metadata
        assert "repository" in metadata


@pytest.mark.slow
@pytest.mark.skip(reason="Requires registry to be published (Task 20)")
def test_e2e_full_workflow():
    """End-to-end: Install, list, uninstall"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Step 1: Install skill
        install_result = subprocess.run(
            [
                sys.executable,
                "scripts/marketplace/cli.py",
                "install",
                "code-review-principles",
                "--marketplace-dir",
                str(marketplace_dir)
            ],
            input="y\n",
            capture_output=True,
            text=True,
            env=get_test_env()
        )
        assert install_result.returncode == 0, f"Install failed: {install_result.stderr}"
        assert "Successfully installed" in install_result.stdout

        # Step 2: List installed skills
        list_result = subprocess.run(
            [
                sys.executable,
                "scripts/marketplace/cli.py",
                "list",
                "--marketplace-dir",
                str(marketplace_dir)
            ],
            capture_output=True,
            text=True,
            env=get_test_env()
        )
        assert list_result.returncode == 0, f"List failed: {list_result.stderr}"
        assert "code-review-principles" in list_result.stdout
        assert "1 skill(s) installed" in list_result.stdout

        # Step 3: Uninstall skill
        uninstall_result = subprocess.run(
            [
                sys.executable,
                "scripts/marketplace/cli.py",
                "uninstall",
                "code-review-principles",
                "--marketplace-dir",
                str(marketplace_dir)
            ],
            input="y\n",
            capture_output=True,
            text=True,
            env=get_test_env()
        )
        assert uninstall_result.returncode == 0, f"Uninstall failed: {uninstall_result.stderr}"
        assert not (marketplace_dir / "code-review-principles").exists(), "Skill not removed"
        assert "Uninstalled code-review-principles" in uninstall_result.stdout


@pytest.mark.slow
@pytest.mark.skip(reason="Requires registry to be published (Task 20)")
def test_e2e_install_with_dependencies():
    """End-to-end: Install skill with dependencies (requires network)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Install java-code-review (depends on code-review-principles and java-dev)
        result = subprocess.run(
            [
                sys.executable,
                "scripts/marketplace/cli.py",
                "install",
                "java-code-review",
                "--marketplace-dir",
                str(marketplace_dir)
            ],
            input="y\n",
            capture_output=True,
            text=True,
            env=get_test_env()
        )

        # Verify success
        assert result.returncode == 0, f"Install failed: {result.stderr}"

        # Verify all skills installed (dependencies + target)
        expected_skills = ["code-review-principles", "java-dev", "java-code-review"]
        for skill_name in expected_skills:
            skill_dir = marketplace_dir / skill_name
            assert skill_dir.exists(), f"Skill {skill_name} not installed"
            assert (skill_dir / "SKILL.md").exists()
            assert (skill_dir / "skill.json").exists()

        # Verify output shows dependency resolution
        assert "requires:" in result.stdout or "Successfully installed 3 skill(s)" in result.stdout


@pytest.mark.slow
@pytest.mark.skip(reason="Requires registry to be published (Task 20)")
def test_e2e_cancel_installation():
    """End-to-end: User cancels installation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Run CLI and cancel
        result = subprocess.run(
            [
                sys.executable,
                "scripts/marketplace/cli.py",
                "install",
                "code-review-principles",
                "--marketplace-dir",
                str(marketplace_dir)
            ],
            input="n\n",  # Cancel installation
            capture_output=True,
            text=True,
            env=get_test_env()
        )

        # Verify cancelled (exit code 1)
        assert result.returncode == 1
        assert "Cancelled" in result.stdout

        # Verify skill not installed
        assert not (marketplace_dir / "code-review-principles").exists()


@pytest.mark.slow
def test_e2e_list_empty_marketplace():
    """End-to-end: List skills in empty marketplace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable,
                "scripts/marketplace/cli.py",
                "list",
                "--marketplace-dir",
                str(marketplace_dir)
            ],
            capture_output=True,
            text=True,
            env=get_test_env()
        )

        assert result.returncode == 0
        assert "0 skills installed" in result.stdout
