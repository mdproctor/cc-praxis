#!/usr/bin/env python3
"""
Functional test runner for Claude Code skills (TIER: CI)

Executes skill tests in isolated git worktrees to verify behavior.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List
import subprocess
import shutil
import tempfile


def create_test_worktree(base_dir: Path) -> Path:
    """
    Create isolated git worktree for test execution.

    Args:
        base_dir: Base directory for worktree creation

    Returns:
        Path to created worktree

    Raises:
        RuntimeError: If not in a git repository
        subprocess.CalledProcessError: If worktree creation fails
    """
    # Verify we're in a git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=base_dir,
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Not in a git repository - worktree creation requires git")

    # Create temporary directory for worktree
    worktree_path = Path(tempfile.mkdtemp(prefix="skill_test_", dir=base_dir))

    # Create git worktree
    subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "HEAD"],
        check=True,
        capture_output=True
    )

    return worktree_path


def cleanup_worktree(worktree_path: Path) -> None:
    """
    Remove git worktree and clean up files.

    Args:
        worktree_path: Path to worktree to remove
    """
    try:
        # Remove git worktree
        subprocess.run(
            ["git", "worktree", "remove", str(worktree_path), "--force"],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        # If worktree removal fails, still try to clean up directory
        pass

    # Clean up directory if it still exists
    if worktree_path.exists():
        shutil.rmtree(worktree_path)


def load_test_cases(skill_name: str) -> List[Dict]:
    """
    Load test cases from skill's test_cases.json file.

    Args:
        skill_name: Name of skill to load tests for

    Returns:
        List of test case dictionaries

    Raises:
        FileNotFoundError: If test_cases.json doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    test_file = Path(skill_name) / "tests" / "test_cases.json"

    if not test_file.exists():
        raise FileNotFoundError(f"Error: No test cases found for {skill_name}")

    with open(test_file, 'r') as f:
        data = json.load(f)

    return data.get("tests", [])


def execute_test(test_case: Dict, worktree_path: Path) -> Dict:
    """
    Execute a single test case in isolated worktree.

    Args:
        test_case: Test case dictionary from test_cases.json
        worktree_path: Path to isolated worktree

    Returns:
        Test result dictionary with id, description, passed, details
    """
    # For now, just return structure - actual execution in next task
    return {
        "id": test_case["id"],
        "description": test_case["description"],
        "passed": False,  # Placeholder
        "details": "Not yet implemented"
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run functional tests for Claude Code skills"
    )
    parser.add_argument(
        "skill",
        help="Skill name to test (e.g., java-git-commit)"
    )
    parser.add_argument(
        "--test",
        help="Run specific test by ID"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )

    args = parser.parse_args()

    try:
        # Load test cases
        test_cases = load_test_cases(args.skill)

        # Filter to specific test if requested
        if args.test:
            test_cases = [t for t in test_cases if t["id"] == args.test]
            if not test_cases:
                print(f"Error: Test '{args.test}' not found", file=sys.stderr)
                sys.exit(1)

        # Output based on format
        if args.json:
            # JSON output
            output = {
                "skill": args.skill,
                "test_count": len(test_cases),
                "tests": test_cases
            }
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            print(f"Found {len(test_cases)} test(s) for {args.skill}")
            for test in test_cases:
                print(f"  - {test['id']}: {test['description']}")

    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in test file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
