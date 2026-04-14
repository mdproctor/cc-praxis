"""YAML parsing utilities for skill frontmatter."""

import re
import yaml
from pathlib import Path
from typing import Optional, Dict, Tuple


def extract_frontmatter(file_path: Path) -> Tuple[Optional[Dict], Optional[str], int]:
    """
    Extract YAML frontmatter from a SKILL.md or blog entry file.

    Returns:
        (frontmatter_dict, error_message, end_line_number)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for frontmatter delimiters
        if not content.startswith('---\n'):
            return None, "Missing frontmatter (file doesn't start with '---')", 0

        # Find end of frontmatter
        match = re.search(r'\n---\n', content[4:])
        if not match:
            return None, "Frontmatter not properly closed (missing closing '---')", 0

        end_pos = match.start() + 4
        end_line = content[:end_pos].count('\n')
        frontmatter_text = content[4:end_pos]

        # Parse YAML using PyYAML for proper type handling
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return None, "Frontmatter did not parse to a dictionary", 0

        return frontmatter, None, end_line

    except yaml.YAMLError as e:
        return None, f"YAML parsing error: {str(e)}", 0
    except Exception as e:
        return None, f"Error parsing file: {str(e)}", 0


def validate_yaml_structure(frontmatter: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate basic YAML structure.

    Returns:
        (is_valid, error_message)
    """
    required_fields = ['name', 'description']

    for field in required_fields:
        if field not in frontmatter:
            return False, f"Missing required field: {field}"

    # Check for unexpected fields
    allowed_fields = ['name', 'description', 'compatibility']
    for field in frontmatter.keys():
        if field not in allowed_fields:
            return False, f"Unexpected field: {field} (only name, description, compatibility allowed)"

    return True, None
