#!/usr/bin/env python3
"""
Create bidirectional navigation symlinks between workspace and project repos.

  workspace/proj  →  project directory
  project/wksp    →  workspace directory

Also ensures 'wksp' is in the project's .gitignore (committed, not .git/info/exclude).

Usage:
    python3 ~/.claude/skills/workspace-init/create_symlinks.py <workspace_path> <project_path>

Output (KEY=value lines):
    PROJ_SYMLINK=/abs/path/to/workspace/proj
    WKSP_SYMLINK=/abs/path/to/project/wksp
    GITIGNORE_UPDATED=yes|no
    ERROR=<message>   (only on failure — always accompanied by exit code 1)

Exit codes:
    0  success
    1  failure (ERROR line printed to stdout; detail on stderr)
"""

import sys
import os
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("ERROR=Usage: create_symlinks.py <workspace_path> <project_path>")
        print("Usage: create_symlinks.py <workspace_path> <project_path>", file=sys.stderr)
        return 1

    workspace = Path(sys.argv[1]).resolve()
    project = Path(sys.argv[2]).resolve()

    if not workspace.is_dir():
        print(f"ERROR=Workspace path does not exist: {workspace}")
        print(f"Workspace path does not exist: {workspace}", file=sys.stderr)
        return 1

    if not project.is_dir():
        print(f"ERROR=Project path does not exist: {project}")
        print(f"Project path does not exist: {project}", file=sys.stderr)
        return 1

    proj_symlink = workspace / "proj"
    wksp_symlink = project / "wksp"

    # Create workspace/proj → project
    try:
        if proj_symlink.is_symlink():
            proj_symlink.unlink()
        elif proj_symlink.exists():
            print(f"ERROR=Cannot create proj/ symlink — path exists and is not a symlink: {proj_symlink}")
            return 1
        proj_symlink.symlink_to(project)
    except OSError as e:
        print(f"ERROR=Failed to create proj/ symlink: {e}")
        print(f"Failed to create proj/ symlink: {e}", file=sys.stderr)
        return 1

    # Create project/wksp → workspace
    try:
        if wksp_symlink.is_symlink():
            wksp_symlink.unlink()
        elif wksp_symlink.exists():
            print(f"ERROR=Cannot create wksp/ symlink — path exists and is not a symlink: {wksp_symlink}")
            return 1
        wksp_symlink.symlink_to(workspace)
    except OSError as e:
        print(f"ERROR=Failed to create wksp/ symlink: {e}")
        print(f"Failed to create wksp/ symlink: {e}", file=sys.stderr)
        return 1

    # Verify both symlinks resolve correctly
    if not proj_symlink.resolve().is_dir():
        print(f"ERROR=proj/ symlink created but does not resolve to a directory")
        return 1
    if not wksp_symlink.resolve().is_dir():
        print(f"ERROR=wksp/ symlink created but does not resolve to a directory")
        return 1

    # Ensure 'wksp' is in project .gitignore
    gitignore = project / ".gitignore"
    gitignore_updated = False
    try:
        existing = gitignore.read_text() if gitignore.exists() else ""
        lines = existing.splitlines()
        if "wksp" not in lines:
            with gitignore.open("a") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write("wksp\n")
            gitignore_updated = True
    except OSError as e:
        # Non-fatal — symlinks are created, gitignore update failed
        print(f"WARNING=Could not update .gitignore: {e}", file=sys.stderr)

    print(f"PROJ_SYMLINK={proj_symlink}")
    print(f"WKSP_SYMLINK={wksp_symlink}")
    print(f"GITIGNORE_UPDATED={'yes' if gitignore_updated else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
