#!/usr/bin/env python3
"""
Scan git branches for Flyway V-number conflicts.

Reads all migration filenames from every branch (local + remote) and finds
the highest claimed V-number, then computes next-safe = max + 1.

Usage:
    python3 ~/.claude/skills/work-start/flyway_scan.py <project_path> [<base_branch>]

    <project_path>   absolute path to the project git repo
    <base_branch>    branch to always include (default: main)

Output (KEY=value lines):
    NEXT_SAFE_V=<N>          next V-number with no conflicts
    MAX_V=<N>                highest V-number found (0 if none)
    CONFLICT=yes|no          yes if two branches claim the same V-number
    CONFLICT_V=<N>           first conflicting V-number (only when CONFLICT=yes)
    CONFLICT_BRANCHES=<a,b>  branches claiming the conflicting V (only when CONFLICT=yes)
    SCAN_COMPLETE=yes|no     no if git fetch failed (offline)

Exit codes:
    0  success (even if conflicts found — caller decides how to handle)
    1  project path does not exist or is not a git repo
"""

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

V_PATTERN = re.compile(r"[Vv](\d+(?:\.\d+)?)__")


def run_git(*args: str, cwd: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True, cwd=cwd,
    )
    return result.returncode, result.stdout.strip()


def _version_key(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def scan(project_path: Path, base_branch: str = "main") -> dict:
    # Fetch remotes (best-effort)
    fetch_rc, _ = run_git("fetch", "--all", "--quiet", cwd=str(project_path))
    scan_complete = fetch_rc == 0

    # Collect all branch refs
    _, branch_output = run_git(
        "branch", "-a", "--format=%(refname:short)", cwd=str(project_path)
    )
    branches = [b.strip() for b in branch_output.splitlines() if b.strip()]
    if base_branch not in branches:
        branches = [base_branch] + branches

    # Map V-number → set of branches claiming it
    v_to_branches: dict[str, set[str]] = defaultdict(set)
    max_v: str | None = None

    for branch in branches:
        if branch == base_branch:
            # For the base branch, count all migrations in the tree
            rc, file_list = run_git(
                "ls-tree", "-r", "--name-only", branch, cwd=str(project_path)
            )
        else:
            # For feature branches, only count migrations ADDED on this branch
            # (not inherited from base) to avoid false conflicts on shared history
            rc, file_list = run_git(
                "log", "--name-only", "--diff-filter=A",
                "--format=", f"{base_branch}..{branch}",
                cwd=str(project_path)
            )
        if rc != 0:
            continue
        for filepath in file_list.splitlines():
            if not filepath.strip():
                continue
            filename = Path(filepath).name
            m = V_PATTERN.match(filename)
            if m:
                v = m.group(1)
                v_to_branches[v].add(branch)
                if max_v is None or _version_key(v) > _version_key(max_v):
                    max_v = v

    # Find conflicts (same V claimed by >1 branch)
    conflict_v: str | None = None
    conflict_branches: list[str] = []
    for v, claiming in sorted(v_to_branches.items(), key=lambda x: _version_key(x[0])):
        if len(claiming) > 1:
            conflict_v = v
            conflict_branches = sorted(claiming)
            break

    # Compute next-safe
    if max_v is None:
        next_safe = 1
        max_int = 0
    else:
        # Only handle integer V-numbers for next-safe; compound (1.1) → use max int part
        try:
            max_int = int(max_v.split(".")[0])
        except ValueError:
            max_int = 0
        next_safe = max_int + 1

    return {
        "next_safe": next_safe,
        "max_v": max_v or "0",
        "conflict": conflict_v is not None,
        "conflict_v": conflict_v or "",
        "conflict_branches": conflict_branches,
        "scan_complete": scan_complete,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    project_path = Path(sys.argv[1]).resolve()
    base_branch = sys.argv[2] if len(sys.argv) > 2 else "main"

    if not project_path.is_dir():
        print(f"ERROR=Project path does not exist: {project_path}", file=sys.stderr)
        return 1

    rc, _ = run_git("rev-parse", "--git-dir", cwd=str(project_path))
    if rc != 0:
        print(f"ERROR=Not a git repository: {project_path}", file=sys.stderr)
        return 1

    result = scan(project_path, base_branch)

    print(f"NEXT_SAFE_V={result['next_safe']}")
    print(f"MAX_V={result['max_v']}")
    print(f"CONFLICT={'yes' if result['conflict'] else 'no'}")
    if result["conflict"]:
        print(f"CONFLICT_V={result['conflict_v']}")
        print(f"CONFLICT_BRANCHES={','.join(result['conflict_branches'])}")
    print(f"SCAN_COMPLETE={'yes' if result['scan_complete'] else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
