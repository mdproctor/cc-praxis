#!/usr/bin/env python3
"""
Context resolver for git-squash.
Prints KEY=value lines for the current branch, commit ranges, and upstream state.

Usage: python3 ~/.claude/skills/git-squash/ctx.py
       python3 ~/.claude/skills/git-squash/ctx.py --rebase-todo <base> <branch>
       python3 ~/.claude/skills/git-squash/ctx.py --compaction-targets <base> <branch> <step>
"""
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

def run(*cmd, check=False):
    r = subprocess.run(list(cmd), capture_output=True, text=True)
    return r.stdout.strip()

def git(*args):
    return run("git", *args)

if len(sys.argv) > 1 and sys.argv[1] == "--rebase-todo":
    # Output rebase todo lines for each commit in range
    base, branch = sys.argv[2], sys.argv[3]
    commits = git("log", "--format=%H %s", f"{base}..{branch}")
    for line in reversed(commits.splitlines()):
        sha, _, subject = line.partition(" ")
        print(f"pick {sha[:7]} {subject}")
    sys.exit(0)

if len(sys.argv) > 1 and sys.argv[1] == "--compaction-targets":
    # Output every Nth commit SHA for compaction targets
    base, branch, step = sys.argv[2], sys.argv[3], int(sys.argv[4])
    commits = git("log", "--format=%H", f"{base}..{branch}").splitlines()
    for i, sha in enumerate(commits, 1):
        if i % step == 0:
            print(sha)
    sys.exit(0)

# Default: output squash context
orig_branch = git("branch", "--show-current")
ts = datetime.now().strftime("%Y%m%d-%H%M%S")
work_branch = f"squash/wip-{orig_branch}-{ts}"

# Upstream remote
upstream = git("remote").splitlines()
upstream_remote = next((r for r in upstream if r in ("upstream", "origin")), upstream[0] if upstream else "origin")

# Project base branch from CLAUDE.md
claude_text = Path("CLAUDE.md").read_text() if Path("CLAUDE.md").exists() else ""
m = re.search(r'\*\*Project base branch:\*\*\s*`([^`]+)`', claude_text)
base_branch = m.group(1) if m else "main"

# Workspace path (if applicable)
workspace_root = run("git", "rev-parse", "--show-toplevel")
meta_path = Path(workspace_root) / "design" / ".meta"
meta_sha = ""
if meta_path.exists():
    for line in meta_path.read_text().splitlines():
        if line.startswith("project-sha:"):
            meta_sha = line.partition(": ")[2].strip()

# Commit count ranges
unpushed_count = git("log", "--oneline", "@{u}..HEAD", "2>/dev/null") if True else ""
try:
    unpushed_lines = git("log", "--oneline", "@{u}..HEAD")
    unpushed_count = str(len(unpushed_lines.splitlines())) if unpushed_lines else "0"
    unpushed_range = "@{u}..HEAD"
except Exception:
    unpushed_count = "0"
    unpushed_range = ""

try:
    safe_lines = git("log", "--oneline", f"{upstream_remote}/{base_branch}..HEAD")
    safe_count = str(len(safe_lines.splitlines())) if safe_lines else "0"
    safe_range = f"{upstream_remote}/{base_branch}..HEAD"
except Exception:
    safe_count = "0"
    safe_range = f"origin/{base_branch}..HEAD"

if meta_sha:
    all_lines = git("log", "--oneline", f"{meta_sha}..HEAD")
    all_count = str(len(all_lines.splitlines())) if all_lines else "0"
    all_range = f"{meta_sha}..HEAD"
    all_label = "full branch from start"
else:
    all_lines = git("log", "--oneline", f"origin/{base_branch}..HEAD")
    all_count = str(len(all_lines.splitlines())) if all_lines else "0"
    all_range = f"origin/{base_branch}..HEAD"
    all_label = "full branch"

print(f"ORIG_BRANCH={orig_branch}")
print(f"WORK_BRANCH={work_branch}")
print(f"BASE_BRANCH={base_branch}")
print(f"UPSTREAM_REMOTE={upstream_remote}")
print(f"META_SHA={meta_sha}")
print(f"UNPUSHED_COUNT={unpushed_count}")
print(f"UNPUSHED_RANGE={unpushed_range}")
print(f"SAFE_COUNT={safe_count}")
print(f"SAFE_RANGE={safe_range}")
print(f"ALL_COUNT={all_count}")
print(f"ALL_RANGE={all_range}")
print(f"ALL_LABEL={all_label}")
