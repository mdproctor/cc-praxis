#!/usr/bin/env python3
"""Revert subtype: log → subtype: diary in YAML frontmatter.

Idempotent — files already at subtype: diary are untouched.
Re-run during eventual consistency period as active sessions pick up the fix.

Usage:
    python3 scripts/revert_diary_subtype.py           # dry-run (default)
    python3 scripts/revert_diary_subtype.py --apply   # apply changes
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path.home() / "claude"

SKIP_PARTS = {".git", "_site", "adr"}
SKIP_DIR_NAMES = {"superpowers"}   # skips specs/, plans/, snapshots/ under superpowers/
SKIP_FILENAMES = {"HANDOFF.md"}

FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n?(.*)', re.DOTALL)
SUBTYPE_LOG_RE = re.compile(r'^subtype: log$', re.MULTILINE)


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_PARTS:
        return True
    if path.name in SKIP_FILENAMES:
        return True
    # Skip anything inside a 'superpowers' directory
    for part in path.parts:
        if part in SKIP_DIR_NAMES:
            return True
    return False


def process(path: Path, apply: bool) -> bool:
    """Return True if file was changed (or would change in dry-run)."""
    try:
        raw = path.read_bytes()
    except (PermissionError, OSError):
        return False

    content = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")

    m = FRONTMATTER_RE.match(content)
    if not m:
        return False

    frontmatter, body = m.group(1), m.group(2)

    if "subtype: log" not in frontmatter:
        return False

    new_frontmatter = SUBTYPE_LOG_RE.sub("subtype: diary", frontmatter)
    new_content = f"---\n{new_frontmatter}\n---\n{body}"

    if apply:
        path.write_text(new_content, encoding="utf-8")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true",
                        help="Apply changes (default is dry-run)")
    args = parser.parse_args()

    by_repo: dict[str, list[Path]] = {}

    for md in ROOT.rglob("*.md"):
        if should_skip(md):
            continue
        if process(md, apply=args.apply):
            try:
                rel = md.relative_to(ROOT)
                repo_key = str(Path(*rel.parts[:2])) if len(rel.parts) > 2 else rel.parts[0]
            except ValueError:
                repo_key = "?"
            by_repo.setdefault(repo_key, []).append(md)

    action = "Changed" if args.apply else "Would change"
    total = 0
    for repo_key in sorted(by_repo):
        files = by_repo[repo_key]
        print(f"\n{repo_key}: {len(files)} file(s)")
        for f in sorted(files):
            print(f"  {f.relative_to(ROOT)}")
        total += len(files)

    print(f"\n{action}: {total} file(s) total")
    if not args.apply:
        print("Re-run with --apply to apply changes.")


if __name__ == "__main__":
    main()
