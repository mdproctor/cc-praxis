#!/usr/bin/env python3
"""
Compute SHA-256 hashes of H2 section headings in a DESIGN.md file.
Output: a pipe-separated string of hash:heading pairs, suitable for storing
in .meta as design-section-hashes.

Usage: python3 ~/.claude/skills/project-init/section_hashes.py /path/to/DESIGN.md

Returns empty string if the file does not exist.
"""
import sys
import hashlib
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: section_hashes.py <design_md_path>", file=sys.stderr)
    sys.exit(1)

path = Path(sys.argv[1])
if not path.exists():
    print("")
    sys.exit(0)

parts = []
for line in path.read_text().splitlines():
    if line.startswith("## "):
        h = hashlib.sha256(line.encode()).hexdigest()[:8]
        parts.append(f"{h}:{line}")

print("|".join(parts))
