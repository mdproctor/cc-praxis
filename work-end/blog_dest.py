#!/usr/bin/env python3
"""
Resolve blog destination from ~/.claude/blog-routing.yaml and publish
unpublished entries from the workspace blog directory.

Usage: python3 ~/.claude/skills/work-end/blog_dest.py <workspace_blog_dir> <branch_name>

Outputs:
  BLOG_DEST=/resolved/path/to/destination
  BLOG_REPO=/resolved/path/to/git/repo
  BLOG_SUBDIR=subdir-name
  UNPUBLISHED=entry1.md,entry2.md   (comma-separated, empty if none)

Copies unpublished entries to the destination directory.
Caller is responsible for git add / commit / push.
"""
import sys
import os
import re
import shutil
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed — run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: blog_dest.py <workspace_blog_dir> <branch_name>", file=sys.stderr)
    sys.exit(1)

workspace_blog = Path(sys.argv[1])
branch_name = sys.argv[2]

routing_path = Path.home() / ".claude" / "blog-routing.yaml"
if not routing_path.exists():
    print(f"ERROR: {routing_path} not found", file=sys.stderr)
    sys.exit(1)

cfg = yaml.safe_load(routing_path.read_text())
dest_key = cfg.get("defaults", {}).get("destinations", [None])[0]
if not dest_key:
    print("ERROR: no default destination in blog-routing.yaml", file=sys.stderr)
    sys.exit(1)

dest_cfg = cfg["destinations"][dest_key]
dest_path = Path(os.path.expanduser(dest_cfg["path"] + dest_cfg.get("subdir", ""))).resolve()
blog_repo = dest_path.parent
blog_subdir = dest_path.name

print(f"BLOG_DEST={dest_path}")
print(f"BLOG_REPO={blog_repo}")
print(f"BLOG_SUBDIR={blog_subdir}")

# Find entries in workspace blog not yet in destination
ws_entries = sorted(p.name for p in workspace_blog.glob("*.md") if p.name != "INDEX.md") if workspace_blog.exists() else []
dest_entries = set(p.name for p in dest_path.glob("*")) if dest_path.exists() else set()

unpublished = [e for e in ws_entries if e not in dest_entries]

if unpublished:
    dest_path.mkdir(parents=True, exist_ok=True)
    for entry in unpublished:
        shutil.copy2(workspace_blog / entry, dest_path / entry)
    print(f"UNPUBLISHED={','.join(unpublished)}")
else:
    print("UNPUBLISHED=")
