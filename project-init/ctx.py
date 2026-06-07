#!/usr/bin/env python3
"""
Work-end context resolver.
Prints all values needed by work-end as KEY=value lines.
Run from the workspace directory: python3 ~/.claude/skills/work-end/ctx.py
"""
import subprocess, re, sys
from pathlib import Path

def run(*cmd, cwd=None):
    return subprocess.run(list(cmd), capture_output=True, text=True, cwd=cwd).stdout.strip()

workspace = run("git", "rev-parse", "--show-toplevel")
if not workspace:
    print("ERROR: not in a git repository", file=sys.stderr)
    sys.exit(1)

proj_symlink = Path(workspace) / "proj"
project = str(proj_symlink.resolve()) if proj_symlink.exists() else workspace
single_repo = workspace == project

claude_md = Path(project) / "CLAUDE.md"
claude_text = claude_md.read_text() if claude_md.exists() else ""

m = re.search(r"GitHub repo:\s*(\S+)", claude_text)
owner_repo = m.group(1) if m else ""

m = re.search(r"\*\*Project base branch:\*\*\s*`([^`]+)`", claude_text)
base_branch = m.group(1) if m else "main"

meta_path = Path(workspace) / "design" / ".meta"
meta = {}
if meta_path.exists():
    for line in meta_path.read_text().splitlines():
        if ": " in line:
            k, _, v = line.partition(": ")
            meta[k.strip()] = v.strip()

branch_name = meta.get("branch", "")
project_sha = meta.get("project-sha", "")
issue_n = meta.get("issue", "")
issue_repo = meta.get("issue-repo", owner_repo)
covers = meta.get("covers", issue_n)
current_branch = run("git", "-C", workspace, "branch", "--show-current")

print(f"WORKSPACE={workspace}")
print(f"PROJECT={project}")
print(f"SINGLE_REPO={'yes' if single_repo else 'no'}")
print(f"OWNER_REPO={owner_repo}")
print(f"BASE_BRANCH={base_branch}")
print(f"CURRENT_BRANCH={current_branch}")
print(f"BRANCH_NAME={branch_name}")
print(f"PROJECT_SHA={project_sha}")
print(f"ISSUE_N={issue_n}")
print(f"ISSUE_REPO={issue_repo}")
print(f"COVERS={covers}")
