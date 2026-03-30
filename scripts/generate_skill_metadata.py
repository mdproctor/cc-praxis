#!/usr/bin/env python3
"""
Skill Metadata Generator - Tasks 1-4

Task 1: Scans a directory structure to find all skill directories (those containing SKILL.md files).
Task 2: Parses SKILL.md frontmatter to extract skill name.
Task 3: Parses SKILL.md Prerequisites section to extract dependencies.
Task 4: Generates skill.json metadata file combining frontmatter + external inputs.

Part of the skill marketplace implementation (Tasks 1-4 of 20).
"""

import json
import re
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

    # Write skill.json
    skill_json_path = skill_dir / "skill.json"
    with open(skill_json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
