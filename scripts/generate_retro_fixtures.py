#!/usr/bin/env python3
"""
ONE-TIME developer tool: extract retro-issues test fixtures from ~/claude repos.

Run this once on a machine that has ~/claude. Commit the output to
tests/fixtures/retro/repos/. Tests never call this script — they use
the committed fixtures directly.

Usage: python3 scripts/generate_retro_fixtures.py [--max-commits N]
Output: tests/fixtures/retro/repos/{repo-name}/
  git_log.jsonl       — one JSON object per line: {hash, date, subject}
  file_changes.json   — {hash: [changed_file_paths]}
  docs/               — copied ADRs, blog entries, DESIGN.md if present

After running: git add tests/fixtures/retro/ && git commit
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / "claude"
FIXTURES_DIR = Path("tests/fixtures/retro/repos")
DOC_SOURCES = [
    ("docs/adr", "docs/adr"),
    ("docs/diary", "docs/diary"),
    ("blog", "blog"),
    ("DESIGN.md", "DESIGN.md"),
    # CLAUDE.md excluded — process docs aren't used by retro analysis and
    # may contain stale content that confuses validators
]


def run(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL)


def get_repos() -> list[Path]:
    return sorted(
        p.parent
        for p in CLAUDE_DIR.glob("*/.git")
        if p.parent.is_dir()
    )


def export_git_log(repo: Path, out_dir: Path, max_commits: int | None) -> list[str]:
    """Write git_log.jsonl and return list of commit hashes."""
    cmd = ["git", "log", "--no-merges", "--format=%H|%ad|%s", "--date=short"]
    if max_commits:
        cmd += [f"-{max_commits}"]
    log = run(cmd, cwd=repo)
    hashes = []
    with (out_dir / "git_log.jsonl").open("w") as f:
        for line in log.splitlines():
            if "|" not in line:
                continue
            parts = line.split("|", 2)
            if len(parts) == 3:
                entry = {
                    "hash": parts[0].strip(),
                    "date": parts[1].strip(),
                    "subject": parts[2].strip(),
                }
                f.write(json.dumps(entry) + "\n")
                hashes.append(entry["hash"])
    return hashes


def export_file_changes(repo: Path, out_dir: Path, hashes: list[str]) -> None:
    """Write file_changes.json mapping each hash to its changed files."""
    changes: dict[str, list[str]] = {}
    for h in hashes:
        try:
            files = run(
                ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", h],
                cwd=repo,
            )
            changes[h] = [f.strip() for f in files.splitlines() if f.strip()]
        except subprocess.CalledProcessError:
            changes[h] = []
    (out_dir / "file_changes.json").write_text(json.dumps(changes, indent=2))


def copy_docs(repo: Path, out_dir: Path) -> None:
    """Copy available documentation files into the fixture."""
    for src_rel, dst_rel in DOC_SOURCES:
        src = repo / src_rel
        dst = out_dir / "docs" / dst_rel
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def check_size(out_dir: Path) -> int:
    """Return size of file_changes.json in bytes."""
    fc = out_dir / "file_changes.json"
    return fc.stat().st_size if fc.exists() else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-commits",
        type=int,
        default=None,
        help="Limit commits per repo (default: all)",
    )
    args = parser.parse_args()

    if not CLAUDE_DIR.exists():
        print(f"ERROR: {CLAUDE_DIR} not found. Run this on a machine with ~/claude repos.")
        sys.exit(1)

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    repos = get_repos()
    print(f"Found {len(repos)} repos under {CLAUDE_DIR}")

    total_size = 0
    for repo in repos:
        name = repo.name
        out_dir = FIXTURES_DIR / name
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"  {name}...", end=" ", flush=True)
        hashes = export_git_log(repo, out_dir, args.max_commits)
        export_file_changes(repo, out_dir, hashes)
        copy_docs(repo, out_dir)
        size = check_size(out_dir)
        total_size += size
        size_str = f"{size // 1024}KB" if size > 1024 else f"{size}B"
        print(f"{len(hashes)} commits, file_changes={size_str}")

        if size > 1_000_000:
            print(f"    ⚠️  file_changes.json is {size // 1024}KB — consider --max-commits 200")

    print(f"\nFixtures written to {FIXTURES_DIR}")
    print(f"Total size: {total_size // 1024}KB")
    print("\nNext step:")
    print("  git add tests/fixtures/retro/")
    print("  git commit -m \"test(retro-issues): add repo fixtures extracted from ~/claude\"")


if __name__ == "__main__":
    main()
