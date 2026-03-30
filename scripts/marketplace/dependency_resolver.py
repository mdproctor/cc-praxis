"""
Dependency resolver for skill marketplace.

Builds dependency graphs by recursively resolving skill dependencies
and ordering them for installation (dependencies first).
"""

import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any


def fetch_skill_metadata(repository: str, path: str, ref: str) -> Dict[str, Any]:
    """
    Fetch skill.json from GitHub repository using sparse checkout.

    Args:
        repository: GitHub repository URL
        path: Subdirectory path within repo
        ref: Git reference (tag, branch, commit)

    Returns:
        Parsed skill.json metadata

    Raises:
        subprocess.CalledProcessError: If git operations fail
        FileNotFoundError: If skill.json doesn't exist
        json.JSONDecodeError: If skill.json is malformed
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Initialize git repo
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

        # Configure sparse checkout for skill.json only
        sparse_file = tmpdir / ".git" / "info" / "sparse-checkout"
        sparse_file.write_text(f"{path}/skill.json\n")

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

        # Read skill.json
        skill_json_path = tmpdir / path / "skill.json"
        with open(skill_json_path) as f:
            return json.load(f)


def build_dependency_graph(
    skill_name: str,
    registry: Dict[str, Any],
    repository: str = "https://github.com/mdproctor/claude-skills",
    ref: str = "main"
) -> List[Dict[str, Any]]:
    """
    Build dependency graph for skill, resolving transitive dependencies.

    Uses depth-first search to resolve all dependencies and returns them
    in installation order (dependencies before dependents).

    Args:
        skill_name: Name of skill to install
        registry: Registry data (for looking up skills)
        repository: Default repository URL
        ref: Default git reference

    Returns:
        List of skills in dependency order (dependencies first)

    Raises:
        subprocess.CalledProcessError: If git operations fail
        FileNotFoundError: If skill metadata cannot be found
        json.JSONDecodeError: If skill.json is malformed
        ValueError: If circular dependency is detected
    """
    visited = set()
    active = set()  # Currently being processed
    graph = []

    def visit(name: str, repo: str, git_ref: str):
        """Visit a skill node and recursively visit its dependencies."""
        if name in active:
            raise ValueError(f"Circular dependency detected: {name}")

        if name in visited:
            return

        active.add(name)
        visited.add(name)

        # Fetch metadata
        metadata = fetch_skill_metadata(repo, name, git_ref)

        # Visit dependencies first (depth-first)
        for dep in metadata.get("dependencies", []):
            visit(dep["name"], dep["repository"], dep["ref"])

        active.remove(name)
        # Add to graph after dependencies
        graph.append(metadata)

    visit(skill_name, repository, ref)
    return graph
