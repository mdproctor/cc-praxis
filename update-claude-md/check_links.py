#!/usr/bin/env python3
"""
Check for broken relative links in CLAUDE.md (or any markdown file).
Reports links of the form [text](docs/path) where the target file doesn't exist.

Usage: python3 ~/.claude/skills/update-claude-md/check_links.py [file]
       Defaults to CLAUDE.md in the current directory.
"""
import sys
import re
from pathlib import Path

target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("CLAUDE.md")

if not target.exists():
    print(f"File not found: {target}", file=sys.stderr)
    sys.exit(1)

text = target.read_text()
base = target.parent

# Find all markdown links with relative paths (not http/https/#)
links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
broken = []
for label, href in links:
    if href.startswith(("http", "#", "mailto")):
        continue
    resolved = (base / href).resolve()
    if not resolved.exists():
        broken.append(f"BROKEN LINK: [{label}]({href})")

if broken:
    for b in broken:
        print(b)
    sys.exit(1)
else:
    print("All links OK.")
    sys.exit(0)
