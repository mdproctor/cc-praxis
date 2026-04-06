#!/usr/bin/env python3
"""
Amend historical commit messages using a hash→ref mapping.

Requires: git-filter-repo (brew install git-filter-repo / pip install git-filter-repo)
Must be run from the root of the git repository, on a dedicated amendment branch
(NOT on main). See retro-issues skill Step 10 for the full safe workflow.

Usage: python3 retro-amend-commits.py <mapping.json>
  mapping.json: {"abc1234": "Refs #12", "def5678": "Closes #12", ...}

Exit 0: success. Exit 1: error.
"""
import json
import sys
from pathlib import Path


def load_mapping(path: str) -> dict[bytes, bytes]:
    raw: dict[str, str] = json.loads(Path(path).read_text())
    return {k.encode(): v.encode() for k, v in raw.items()}


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: retro-amend-commits.py <mapping.json>", file=sys.stderr)
        sys.exit(1)

    try:
        import git_filter_repo as fr
    except ImportError:
        print(
            "ERROR: git-filter-repo not installed.\n"
            "  brew install git-filter-repo  OR  pip install git-filter-repo",
            file=sys.stderr,
        )
        sys.exit(1)

    mapping = load_mapping(sys.argv[1])
    if not mapping:
        print("ERROR: mapping is empty — nothing to amend", file=sys.stderr)
        sys.exit(1)

    def commit_callback(commit):  # type: ignore[no-untyped-def]
        short = commit.original_id[:7]
        ref = mapping.get(short)
        if ref:
            msg = commit.message
            if not msg.endswith(b"\n"):
                msg += b"\n"
            commit.message = msg + b"\n" + ref + b"\n"

    args = fr.FilteringOptions.parse_args(["--force"], error_on_empty=False)
    fr.RepoFilter(args, commit_callback=commit_callback).run()


if __name__ == "__main__":
    main()
