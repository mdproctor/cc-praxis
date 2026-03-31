"""
Skill installer for marketplace.

Downloads skills from GitHub repositories using git sparse checkout
and installs them to the .marketplace directory.
"""

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any


def fetch_skill_files(repository: str, path: str, ref: str) -> tuple[Path, Path]:
    """
    Fetch skill files from GitHub using sparse checkout.

    Args:
        repository: GitHub repository URL
        path: Subdirectory path within repo
        ref: Git reference

    Returns:
        Tuple of (skill_dir, temp_root) where:
        - skill_dir: Path to directory containing skill files
        - temp_root: Path to temporary directory (for cleanup)

    Raises:
        RuntimeError: If git operations fail
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="claude-skill-install-"))

    try:
        # Initialize git
        subprocess.run(
            ["git", "init"],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "remote", "add", "origin", repository],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "core.sparseCheckout", "true"],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )

        # Configure sparse checkout
        sparse_file = tmpdir / ".git" / "info" / "sparse-checkout"
        sparse_file.parent.mkdir(parents=True, exist_ok=True)
        sparse_file.write_text(f"{path}/*\n")

        # Fetch
        subprocess.run(
            ["git", "fetch", "--depth=1", "origin", ref],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "checkout", ref],
            cwd=tmpdir,
            check=True,
            capture_output=True
        )

        skill_dir = tmpdir / path

        # Validate fetched directory exists
        if not skill_dir.exists():
            raise RuntimeError(
                f"Skill directory {path} not found after checkout from {repository}@{ref}"
            )

        return skill_dir, tmpdir

    except subprocess.CalledProcessError as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        stderr = e.stderr.decode() if e.stderr else ""
        raise RuntimeError(
            f"Failed to fetch skill from {repository}/{path}@{ref}: {e}\n{stderr}"
        ) from e
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise RuntimeError(
            f"Failed to fetch skill from {repository}/{path}@{ref}: {e}"
        ) from e


def install_skill(
    skill_metadata: Dict[str, Any],
    marketplace_dir: Path,
    ref: str
) -> None:
    """
    Install skill to marketplace directory.

    Args:
        skill_metadata: Skill metadata (name, repository, etc.)
        marketplace_dir: Path to .marketplace directory
        ref: Git reference to install

    Raises:
        ValueError: If skill metadata is invalid or marketplace_dir doesn't exist
        RuntimeError: If installation fails
    """
    # Validate metadata
    try:
        name = skill_metadata["name"]
        repository = skill_metadata["repository"]
    except KeyError as e:
        raise ValueError(f"Invalid skill metadata: missing required field {e}") from e

    # Validate marketplace directory exists
    if not marketplace_dir.exists():
        raise ValueError(f"Marketplace directory does not exist: {marketplace_dir}")
    if not marketplace_dir.is_dir():
        raise ValueError(f"Marketplace path is not a directory: {marketplace_dir}")

    # Fetch files
    temp_skill_dir, temp_root = fetch_skill_files(repository, name, ref)

    try:
        # Use atomic installation pattern to prevent data loss
        install_dir = marketplace_dir / name
        temp_install_dir = marketplace_dir / f".{name}.tmp"

        # Copy to temporary location first
        if temp_install_dir.exists():
            shutil.rmtree(temp_install_dir)

        shutil.copytree(temp_skill_dir, temp_install_dir)

        # Atomic swap: remove old and rename new
        if install_dir.exists():
            shutil.rmtree(install_dir)

        temp_install_dir.rename(install_dir)

    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_root, ignore_errors=True)
