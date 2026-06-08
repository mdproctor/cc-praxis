#!/usr/bin/env python3
"""
Tests for project-init/stack.py

Covers: depth on empty/populated/missing stack, list output format,
push creates entry, push is idempotent, push auto-timestamps, pop
removes correct entry, pop on absent branch, pop on missing file,
round-trip integrity.
"""

import subprocess
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parent.parent / "project-init" / "stack.py"


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + list(args),
        capture_output=True, text=True,
    )


def parse_output(result: subprocess.CompletedProcess) -> dict:
    return dict(line.split("=", 1) for line in result.stdout.strip().splitlines() if "=" in line)


def push(stack_file: Path, branch: str, issue: str = "42",
         wip_project: str = "no", wip_workspace: str = "no") -> subprocess.CompletedProcess:
    return run("push", str(stack_file),
               f"branch={branch}", f"issue={issue}",
               f"wip_project={wip_project}", f"wip_workspace={wip_workspace}")


# ---------------------------------------------------------------------------
# depth
# ---------------------------------------------------------------------------

class TestDepth:

    def test_depth_zero_when_file_missing(self, tmp_path):
        result = run("depth", str(tmp_path / ".pause-stack"))
        assert result.returncode == 0
        assert result.stdout.strip() == "0"

    def test_depth_zero_on_empty_file(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        stack.write_text("")
        result = run("depth", str(stack))
        assert result.stdout.strip() == "0"

    def test_depth_one_after_single_push(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth")
        result = run("depth", str(stack))
        assert result.stdout.strip() == "1"

    def test_depth_increments_per_push(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth")
        push(stack, "issue-43-billing")
        push(stack, "issue-44-reporting")
        result = run("depth", str(stack))
        assert result.stdout.strip() == "3"


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

class TestList:

    def test_list_empty_stack(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        result = run("list", str(stack))
        assert result.returncode == 0
        out = parse_output(result)
        assert out["ENTRY_COUNT"] == "0"

    def test_list_single_entry_fields(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth", issue="42", wip_project="yes")
        result = run("list", str(stack))
        out = parse_output(result)
        assert out["ENTRY_COUNT"] == "1"
        assert out["ENTRY_1_BRANCH"] == "issue-42-auth"
        assert out["ENTRY_1_ISSUE"] == "42"
        assert out["ENTRY_1_WIP_PROJECT"] == "yes"

    def test_list_preserves_insertion_order(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-10-first")
        push(stack, "issue-20-second")
        push(stack, "issue-30-third")
        result = run("list", str(stack))
        out = parse_output(result)
        assert out["ENTRY_1_BRANCH"] == "issue-10-first"
        assert out["ENTRY_2_BRANCH"] == "issue-20-second"
        assert out["ENTRY_3_BRANCH"] == "issue-30-third"

    def test_list_includes_paused_timestamp(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth")
        result = run("list", str(stack))
        out = parse_output(result)
        # Should have a non-empty timestamp
        assert out.get("ENTRY_1_PAUSED", "") != ""


# ---------------------------------------------------------------------------
# push
# ---------------------------------------------------------------------------

class TestPush:

    def test_push_returns_new_depth(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        result = push(stack, "issue-42-auth")
        out = parse_output(result)
        assert out["STACK_DEPTH"] == "1"

    def test_push_creates_stack_file_if_missing(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        assert not stack.exists()
        push(stack, "issue-42-auth")
        assert stack.exists()

    def test_push_creates_parent_dirs(self, tmp_path):
        stack = tmp_path / "design" / ".pause-stack"
        push(stack, "issue-42-auth")
        assert stack.exists()

    def test_push_is_idempotent_for_same_branch(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth")
        push(stack, "issue-42-auth")  # second push same branch
        result = run("depth", str(stack))
        assert result.stdout.strip() == "1"

    def test_push_adds_auto_timestamp_when_paused_absent(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth")
        result = run("list", str(stack))
        out = parse_output(result)
        paused = out.get("ENTRY_1_PAUSED", "")
        assert "T" in paused  # ISO 8601 format check

    def test_push_preserves_explicit_paused_value(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        run("push", str(stack), "branch=issue-42", "paused=2026-01-01T00:00:00Z")
        result = run("list", str(stack))
        out = parse_output(result)
        assert out["ENTRY_1_PAUSED"] == "2026-01-01T00:00:00Z"

    def test_push_requires_branch(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        result = run("push", str(stack), "issue=42")
        assert result.returncode == 1


# ---------------------------------------------------------------------------
# pop
# ---------------------------------------------------------------------------

class TestPop:

    def test_pop_removes_named_branch(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth")
        push(stack, "issue-43-billing")
        result = run("pop", str(stack), "issue-42-auth")
        out = parse_output(result)
        assert out["REMOVED"] == "yes"
        assert out["STACK_DEPTH"] == "1"
        # Verify the right branch remains
        list_result = run("list", str(stack))
        list_out = parse_output(list_result)
        assert list_out["ENTRY_1_BRANCH"] == "issue-43-billing"

    def test_pop_returns_removed_no_when_branch_absent(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth")
        result = run("pop", str(stack), "nonexistent-branch")
        out = parse_output(result)
        assert out["REMOVED"] == "no"
        assert out["STACK_DEPTH"] == "1"

    def test_pop_on_missing_file_returns_removed_no(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        result = run("pop", str(stack), "anything")
        out = parse_output(result)
        assert out["REMOVED"] == "no"
        assert out["STACK_DEPTH"] == "0"

    def test_pop_leaves_other_entries_intact(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-10-first")
        push(stack, "issue-20-middle")
        push(stack, "issue-30-last")
        run("pop", str(stack), "issue-20-middle")
        list_result = run("list", str(stack))
        list_out = parse_output(list_result)
        assert list_out["ENTRY_COUNT"] == "2"
        branches = {list_out.get("ENTRY_1_BRANCH"), list_out.get("ENTRY_2_BRANCH")}
        assert "issue-10-first" in branches
        assert "issue-30-last" in branches
        assert "issue-20-middle" not in branches

    def test_pop_last_entry_leaves_empty_stack(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth")
        run("pop", str(stack), "issue-42-auth")
        result = run("depth", str(stack))
        assert result.stdout.strip() == "0"


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------

class TestRoundTrip:

    def test_push_then_list_then_pop_round_trip(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        push(stack, "issue-42-auth", issue="42", wip_project="yes", wip_workspace="no")
        push(stack, "issue-43-billing", issue="43", wip_project="no", wip_workspace="yes")

        # Verify list
        list_result = run("list", str(stack))
        list_out = parse_output(list_result)
        assert list_out["ENTRY_COUNT"] == "2"
        assert list_out["ENTRY_1_WIP_PROJECT"] == "yes"
        assert list_out["ENTRY_2_WIP_WORKSPACE"] == "yes"

        # Pop one
        run("pop", str(stack), "issue-42-auth")
        depth_result = run("depth", str(stack))
        assert depth_result.stdout.strip() == "1"

        # Remaining entry is correct
        final_list = run("list", str(stack))
        final_out = parse_output(final_list)
        assert final_out["ENTRY_1_BRANCH"] == "issue-43-billing"

    def test_file_not_corrupted_after_multiple_operations(self, tmp_path):
        stack = tmp_path / ".pause-stack"
        for i in range(5):
            push(stack, f"issue-{i}-branch")
        for i in range(0, 5, 2):
            run("pop", str(stack), f"issue-{i}-branch")
        result = run("depth", str(stack))
        assert result.stdout.strip() == "2"
