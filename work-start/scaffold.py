#!/usr/bin/env python3
"""
Create the workspace branch scaffold: design/.meta and design/JOURNAL.md.

Called by work-start Step 9 after branch creation. Replaces mkdir + heredoc
blocks that trigger Claude Code permission prompts.

Usage:
    python3 ~/.claude/skills/work-start/scaffold.py \\
        <workspace_path> \\
        branch=<name> \\
        project-sha=<sha> \\
        date=<YYYY-MM-DD> \\
        [issue=<N>] \\
        [issue-repo=<owner/repo>] \\
        [covers=<N,M,...>] \\
        [flyway-next-v=<N|none|unknown>] \\
        [design-repo=<workspace|project|cross-repo:name>] \\
        [design-section-hashes=<pipe-sep-pairs>]

Output (KEY=value lines):
    META_PATH=/abs/path/to/design/.meta
    JOURNAL_PATH=/abs/path/to/design/JOURNAL.md
    CREATED=yes|no   (no = files already existed and were left unchanged)

Exit codes:
    0  success
    1  missing required args or I/O error
"""

import sys
from datetime import date
from pathlib import Path


REQUIRED = {"branch", "project-sha"}


def parse_args(args: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for arg in args:
        if "=" in arg:
            k, _, v = arg.partition("=")
            result[k.strip()] = v.strip()
    return result


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    workspace = Path(sys.argv[1]).resolve()
    params = parse_args(sys.argv[2:])

    missing = REQUIRED - params.keys()
    if missing:
        print(f"ERROR=Missing required params: {', '.join(sorted(missing))}", file=sys.stderr)
        return 1

    if not workspace.is_dir():
        print(f"ERROR=Workspace path does not exist: {workspace}", file=sys.stderr)
        return 1

    design_dir = workspace / "design"
    design_dir.mkdir(parents=True, exist_ok=True)

    meta_path = design_dir / ".meta"
    journal_path = design_dir / "JOURNAL.md"

    # Don't overwrite if already exists (idempotent)
    if meta_path.exists() and journal_path.exists():
        print(f"META_PATH={meta_path}")
        print(f"JOURNAL_PATH={journal_path}")
        print("CREATED=no")
        return 0

    branch = params["branch"]
    today = params.get("date", date.today().isoformat())

    meta_lines = [
        f"branch: {branch}",
        f"project-sha: {params.get('project-sha', '')}",
        f"date: {today}",
        f"issue: {params.get('issue', '')}",
        f"issue-repo: {params.get('issue-repo', '')}",
        f"covers: {params.get('covers', params.get('issue', ''))}",
        f"flyway-next-v: {params.get('flyway-next-v', 'unknown')}",
        f"design-repo: {params.get('design-repo', 'project')}",
        f"design-section-hashes: {params.get('design-section-hashes', '')}",
    ]

    try:
        meta_path.write_text("\n".join(meta_lines) + "\n")
        journal_path.write_text(f"# Design Journal — {branch}\n")
    except OSError as e:
        print(f"ERROR=Failed to write scaffold: {e}", file=sys.stderr)
        return 1

    print(f"META_PATH={meta_path}")
    print(f"JOURNAL_PATH={journal_path}")
    print("CREATED=yes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
