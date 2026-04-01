#!/usr/bin/env python3
"""
Generate missing commands/<skill-name>.md files for all skills.

Each skill needs a commands/<skill-name>.md to register a slash command
in Claude Code's UI. This script creates any that are missing, deriving
the description from the skill's frontmatter.

Usage:
    python scripts/generate_commands.py          # create missing only
    python scripts/generate_commands.py --all    # overwrite all
"""

import re
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.common import find_all_skill_files, get_skill_name_from_path


def extract_description(skill_path: Path) -> str:
    """Extract a short description from the skill's frontmatter for the command."""
    content = skill_path.read_text()
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return f"Invoke the {skill_path.parent.name} skill"

    frontmatter = match.group(1)
    desc_match = re.search(r'^description:\s*>?\s*\n?(.*?)(?=^\w|\Z)', frontmatter,
                            re.MULTILINE | re.DOTALL)
    if not desc_match:
        return f"Invoke the {skill_path.parent.name} skill"

    # Collapse multiline description to single line, strip leading spaces
    raw = desc_match.group(1)
    lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    description = ' '.join(lines)

    # Truncate to a reasonable length for a command description
    if len(description) > 100:
        description = description[:97] + '...'

    return description


def generate_command(skill_path: Path, overwrite: bool = False) -> str:
    """
    Create commands/<skill-name>.md if missing (or if overwrite=True).
    Returns 'created', 'skipped', or 'updated'.
    """
    skill_name = get_skill_name_from_path(skill_path)
    cmd_dir = skill_path.parent / 'commands'
    cmd_file = cmd_dir / f'{skill_name}.md'

    if cmd_file.exists() and not overwrite:
        return 'skipped'

    description = extract_description(skill_path)
    status = 'updated' if cmd_file.exists() else 'created'

    cmd_dir.mkdir(exist_ok=True)
    cmd_file.write_text(
        f'---\ndescription: "{description}"\n---\n\nInvoke the `{skill_name}` skill.\n'
    )
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true',
                        help='Regenerate all command files (default: missing only)')
    args = parser.parse_args()

    skill_files = find_all_skill_files()
    counts = {'created': 0, 'updated': 0, 'skipped': 0}

    for skill_path in skill_files:
        status = generate_command(skill_path, overwrite=args.all)
        counts[status] += 1
        if status != 'skipped':
            print(f"  {status}: {get_skill_name_from_path(skill_path)}")

    print(f"\n{counts['created']} created, {counts['updated']} updated, "
          f"{counts['skipped']} already present")


if __name__ == '__main__':
    main()
