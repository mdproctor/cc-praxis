#!/usr/bin/env python3
"""
Remove a branch entry from the workspace pause stack (.pause-stack).

Usage: python3 ~/.claude/skills/project-init/remove_from_stack.py <stack_file> <branch_name>

Exits 0 on success. Exits 1 if the stack file doesn't exist.
Prints a summary of what was removed.
"""
import sys
import re
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: remove_from_stack.py <stack_file> <branch_name>", file=sys.stderr)
    sys.exit(1)

stack_file = Path(sys.argv[1])
branch_name = sys.argv[2]

if not stack_file.exists():
    print(f"Stack file not found: {stack_file}", file=sys.stderr)
    sys.exit(1)

original = stack_file.read_text()
# Remove the block for this branch: "- branch: NAME\n" plus indented continuation lines
pattern = rf'^- branch: {re.escape(branch_name)}\n(?:  .*\n)*'
updated = re.sub(pattern, '', original, flags=re.MULTILINE)

if updated == original:
    print(f"Branch '{branch_name}' not found in stack.")
else:
    stack_file.write_text(updated)
    print(f"Removed '{branch_name}' from pause stack.")
