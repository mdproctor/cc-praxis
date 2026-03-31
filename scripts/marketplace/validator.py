import json
import re
from pathlib import Path


def validate_skill(skill_dir: Path) -> None:
    """
    Validate skill directory contains valid SKILL.md and skill.json.

    Args:
        skill_dir: Path to skill directory

    Raises:
        ValueError: If validation fails
    """
    # Check SKILL.md exists
    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.exists():
        raise ValueError(f"SKILL.md not found in {skill_dir}")

    # Check skill.json exists
    skill_json_path = skill_dir / "skill.json"
    if not skill_json_path.exists():
        raise ValueError(f"skill.json not found in {skill_dir}")

    # Parse skill.json
    try:
        with open(skill_json_path) as f:
            metadata = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in skill.json: {e}")

    # Validate required fields
    if "name" not in metadata:
        raise ValueError("skill.json missing 'name' field")

    # Validate name matches directory
    expected_name = skill_dir.name
    actual_name = metadata["name"]
    if actual_name != expected_name:
        raise ValueError(
            f"Name mismatch: directory is '{expected_name}' but "
            f"skill.json has '{actual_name}'"
        )

    # Parse frontmatter from SKILL.md
    skill_md_content = skill_md_path.read_text()
    match = re.match(r'^---\s*\n(.*?)\n---', skill_md_content, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md missing frontmatter")

    frontmatter = match.group(1)
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if not name_match:
        raise ValueError("SKILL.md frontmatter missing 'name' field")

    frontmatter_name = name_match.group(1).strip()
    if frontmatter_name != actual_name:
        raise ValueError(
            f"Name mismatch: SKILL.md has '{frontmatter_name}' but "
            f"skill.json has '{actual_name}'"
        )
