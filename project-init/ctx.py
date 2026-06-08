#!/usr/bin/env python3
"""
Context resolver for cc-praxis workspace-aware skills.
Prints KEY=value lines consumed by work-start, work-end, work-pause, work-resume, handover etc.
Works whether Claude opened in the workspace or the project repo.

  project repo  has wksp/ → workspace
  workspace     has proj/ → project
  single-repo   has neither (no separate workspace)
"""
import subprocess, re, sys
from pathlib import Path

def run(*cmd, cwd=None):
    return subprocess.run(list(cmd), capture_output=True, text=True, cwd=cwd).stdout.strip()

cwd_root = run("git", "rev-parse", "--show-toplevel")
if not cwd_root:
    print("ERROR: not in a git repository", file=sys.stderr)
    sys.exit(1)

proj_symlink = Path(cwd_root) / "proj"
wksp_symlink = Path(cwd_root) / "wksp"

if proj_symlink.exists():
    # Claude opened in workspace — proj/ points to project
    workspace = cwd_root
    project = str(proj_symlink.resolve())
elif wksp_symlink.exists():
    # Claude opened in project repo — wksp/ points to workspace
    project = cwd_root
    workspace = str(wksp_symlink.resolve())
else:
    # Single-repo mode — no separate workspace configured
    workspace = cwd_root
    project = cwd_root

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

# project-init fast-path checks
cwd = Path.cwd()
claude_md_cwd = cwd / "CLAUDE.md"
cwd_text = claude_md_cwd.read_text() if claude_md_cwd.exists() else ""

claude_ok = "yes" if "## Project Type" in cwd_text else "no"

wksp_ok_symlink = (cwd / "wksp").is_symlink() and (cwd / "wksp").is_dir()
proj_ok_symlink = (cwd / "proj").is_symlink() and (cwd / "proj").is_dir()
wksp_declined = "workspace: declined" in cwd_text
workspace_ok = "yes" if (wksp_ok_symlink or proj_ok_symlink or wksp_declined) else "no"

issues_ok = "yes" if ("Issue tracking: enabled" in cwd_text or "Issue tracking: declined" in cwd_text) else "no"

print(f"CLAUDE_OK={claude_ok}")
print(f"WORKSPACE_OK={workspace_ok}")
print(f"ISSUES_OK={issues_ok}")
