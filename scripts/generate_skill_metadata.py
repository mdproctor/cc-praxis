#!/usr/bin/env python3
"""
Skill Metadata Generator - Tasks 1-5

Task 1: Scans a directory structure to find all skill directories (those containing SKILL.md files).
Task 2: Parses SKILL.md frontmatter to extract skill name.
Task 3: Parses SKILL.md Prerequisites section to extract dependencies.
Task 4: Generates skill.json metadata file combining frontmatter + external inputs.
Task 5: Main CLI for metadata generation - orchestrates all functions.

Part of the skill marketplace implementation (Tasks 1-5 of 20).
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List


def scan_for_skills(root_dir: Path) -> List[Path]:
    """
    Scan directory for skill directories (containing SKILL.md).

    Excludes: .git, docs, scripts, tests, __pycache__, .claude

    Args:
        root_dir: Directory to scan for skills

    Returns:
        Sorted list of skill directory paths
    """
    excluded_dirs = {'.git', 'docs', 'scripts', 'tests', '__pycache__', '.claude'}
    skills = []

    for item in root_dir.iterdir():
        if not item.is_dir():
            continue
        if item.name in excluded_dirs:
            continue
        if (item / "SKILL.md").exists():
            skills.append(item)

    return sorted(skills)


def parse_frontmatter(skill_md_content: str) -> str:
    """
    Parse SKILL.md frontmatter to extract name.

    Args:
        skill_md_content: Full SKILL.md file content

    Returns:
        Skill name from frontmatter

    Raises:
        ValueError: If frontmatter missing or name field not found
    """
    # Extract frontmatter between --- markers
    match = re.match(r'^---\s*\n(.*?)\n---', skill_md_content, re.DOTALL)
    if not match:
        raise ValueError("No frontmatter found in SKILL.md")

    frontmatter = match.group(1)

    # Extract name field
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if not name_match:
        raise ValueError("Missing 'name' field in frontmatter")

    return name_match.group(1).strip()


def parse_dependencies(skill_md_content: str) -> List[str]:
    """
    Parse SKILL.md to extract dependency skill names.

    Looks for Prerequisites section with patterns like:
    - "builds on [`java-dev`]"
    - "extends [`code-review-principles`]"

    Args:
        skill_md_content: Full SKILL.md file content

    Returns:
        List of dependency skill names
    """
    # Find Prerequisites section
    prereq_match = re.search(
        r'^## Prerequisites\s*\n(.*?)(?=^##|\Z)',
        skill_md_content,
        re.MULTILINE | re.DOTALL
    )

    if not prereq_match:
        return []

    prereq_section = prereq_match.group(1)

    # Extract skill names from backtick references: [`skill-name`]
    dependencies = re.findall(r'\[`([^`]+)`\]', prereq_section)

    return dependencies


def generate_skill_json(
    skill_dir: Path,
    repository_url: str,
    version: str,
    dependencies: List[Dict[str, str]]
) -> None:
    """
    Generate skill.json metadata file.

    Args:
        skill_dir: Path to skill directory
        repository_url: GitHub repository URL
        version: Skill version (semver or semver-SNAPSHOT)
        dependencies: List of dependency objects with name, repository, ref

    Raises:
        ValueError: If skill_dir doesn't exist or is not a directory
        FileNotFoundError: If SKILL.md doesn't exist in skill_dir
        IOError: If SKILL.md cannot be read due to permissions or I/O error
    """
    # Validate input parameters
    if not skill_dir.exists():
        raise ValueError(f"Skill directory does not exist: {skill_dir}")
    if not skill_dir.is_dir():
        raise ValueError(f"Not a directory: {skill_dir}")

    # Check SKILL.md exists
    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    # Read SKILL.md with error handling
    try:
        skill_md_content = skill_md_path.read_text()
    except (OSError, PermissionError) as e:
        raise IOError(f"Failed to read {skill_md_path}: {e}")

    # Extract name from frontmatter
    name = parse_frontmatter(skill_md_content)

    # Create metadata object
    metadata = {
        "name": name,
        "version": version,
        "repository": repository_url,
        "dependencies": dependencies
    }

    # Write skill.json with error handling
    skill_json_path = skill_dir / "skill.json"
    try:
        with open(skill_json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    except (OSError, PermissionError) as e:
        raise IOError(f"Failed to write {skill_json_path}: {e}")


def main(
    root_dir: Path = None,
    repository_url: str = "https://github.com/mdproctor/claude-skills",
    version: str = "1.0.0-SNAPSHOT"
) -> int:
    """
    Generate skill.json metadata for all skills in repository.

    Args:
        root_dir: Root directory to scan (default: script parent directory)
        repository_url: GitHub repository URL
        version: Default version for skills

    Returns:
        Number of skills processed
    """
    if root_dir is None:
        root_dir = Path(__file__).parent.parent

    print(f"Scanning for skills in {root_dir}...")
    skills = scan_for_skills(root_dir)
    print(f"Found {len(skills)} skills\n")

    if not skills:
        print("No skills found.")
        return 0

    print("Generating skill metadata...")

    for skill_dir in skills:
        skill_md_path = skill_dir / "SKILL.md"
        skill_md_content = skill_md_path.read_text()

        # Extract name
        name = parse_frontmatter(skill_md_content)

        # Extract dependencies
        dep_names = parse_dependencies(skill_md_content)

        # Build dependency objects (simplified for v1 - all same repo, version TBD)
        dependencies = [
            {
                "name": dep_name,
                "repository": repository_url,
                "ref": "main"  # Snapshot for now
            }
            for dep_name in dep_names
        ]

        # Generate skill.json
        generate_skill_json(
            skill_dir=skill_dir,
            repository_url=repository_url,
            version=version,
            dependencies=dependencies
        )

        deps_str = f", {len(dependencies)} dependencies" if dependencies else ", 0 dependencies"
        print(f"  ✓ {name}/skill.json (v{version}{deps_str})")

    print(f"\nGenerated metadata for {len(skills)} skills.")
    return len(skills)


if __name__ == "__main__":
    count = main()
    sys.exit(0 if count > 0 else 1)
