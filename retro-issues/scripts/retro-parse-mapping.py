#!/usr/bin/env python3
"""
Parse docs/retro-issues.md and emit a JSON commit→issue-ref mapping.

ONE-TIME use during retro-issues optional commit amendment step.

Usage: python3 retro-parse-mapping.py [path-to-retro-issues.md]
Output: JSON to stdout: { "abc1234": "Refs #12", "def5678": "Closes #12" }
Exit 0: success. Exit 1: file not found or parse error.
"""
import json
import re
import sys
from pathlib import Path


def parse_retro_doc(path: Path) -> dict[str, str]:
    """Return {short_hash: ref_string} for all non-excluded commits."""
    text = path.read_text()
    mapping: dict[str, str] = {}
    current_issue: int | None = None
    current_commits: list[str] = []
    in_excluded = False

    def flush(issue_num: int, commits: list[str]) -> None:
        for i, h in enumerate(commits):
            short = h[:7]
            ref = "Closes" if i == len(commits) - 1 else "Refs"
            mapping[short] = f"{ref} #{issue_num}"

    for line in text.splitlines():
        # Stop collecting when we hit the Excluded Commits section
        if "## Excluded Commits" in line:
            if current_issue is not None and current_commits:
                flush(current_issue, current_commits)
            current_issue = None
            current_commits = []
            in_excluded = True
            continue

        if in_excluded:
            continue

        # Issue header: "#### Issue #12: ..." or "### Issue #12: ..."
        issue_match = re.search(r"#+\s+Issue\s+#(\d+):", line)
        if issue_match:
            if current_issue is not None and current_commits:
                flush(current_issue, current_commits)
                current_commits = []
            current_issue = int(issue_match.group(1))
            continue

        # Commit line: "- `abc1234` 2024-01-15 — message"
        if current_issue is not None:
            commit_match = re.search(r"`([0-9a-f]{7,40})`", line)
            if commit_match:
                current_commits.append(commit_match.group(1))

    # Flush last issue
    if current_issue is not None and current_commits:
        flush(current_issue, current_commits)

    return mapping


def main() -> None:
    doc_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/retro-issues.md")
    if not doc_path.exists():
        print(f"ERROR: {doc_path} not found", file=sys.stderr)
        sys.exit(1)
    try:
        mapping = parse_retro_doc(doc_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(mapping, indent=2))


if __name__ == "__main__":
    main()
