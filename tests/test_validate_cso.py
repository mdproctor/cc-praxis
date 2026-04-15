import pytest
import sys
from test_base import is_critical, is_warning, is_note
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validation.validate_cso import (
    validate_skill_cso,
    check_workflow_keywords,
    check_tool_names,
    check_process_patterns,
)


# ---------------------------------------------------------------------------
# Helpers — compare by severity name to avoid module-identity issues
# ---------------------------------------------------------------------------



def make_skill(tmp_path: Path, skill_name: str, description: str) -> Path:
    """Create a minimal SKILL.md fixture inside a correctly-named directory."""
    skill_dir = tmp_path / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        f"---\nname: {skill_name}\ndescription: >\n  {description}\n---\n\n# Body\n"
    )
    return skill_file


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

class TestCheckWorkflowKeywords:
    def test_no_keywords_returns_empty(self):
        assert check_workflow_keywords("Use when the user needs a review") == []

    def test_detects_step(self):
        found = check_workflow_keywords("Dispatches subagents step by step")
        assert "step" in found

    def test_detects_invoke(self):
        found = check_workflow_keywords("Use when invoke is needed")
        assert "invoke" in found

    def test_detects_execute(self):
        found = check_workflow_keywords("Use when execute is required")
        assert "execute" in found

    def test_detects_run(self):
        found = check_workflow_keywords("Automatically run the tests")
        assert "run" in found

    def test_detects_start(self):
        found = check_workflow_keywords("Use when start is mentioned")
        assert "start" in found

    def test_detects_then(self):
        found = check_workflow_keywords("First do X then do Y")
        assert "then" in found

    def test_multiple_keywords_all_returned(self):
        found = check_workflow_keywords("run and execute and invoke")
        assert "run" in found
        assert "execute" in found
        assert "invoke" in found

    def test_case_insensitive(self):
        found = check_workflow_keywords("Use when RUN is mentioned")
        assert "run" in found


class TestCheckToolNames:
    def test_no_tool_names_returns_empty(self):
        assert check_tool_names("Use when the user needs to review code") == []

    def test_detects_Read(self):
        found = check_tool_names("Use when Read is needed")
        assert "Read" in found

    def test_detects_Bash(self):
        found = check_tool_names("Use the Bash tool to run commands")
        assert "Bash" in found

    def test_detects_Agent(self):
        found = check_tool_names("Dispatches via Agent")
        assert "Agent" in found

    def test_detects_Write(self):
        found = check_tool_names("Use Write to save files")
        assert "Write" in found


class TestCheckProcessPatterns:
    def test_no_patterns_returns_empty(self):
        assert check_process_patterns("Use when the user needs help with code") == []

    def test_detects_step_number(self):
        found = check_process_patterns("In step 1 do the first thing")
        assert len(found) > 0

    def test_detects_phase_number(self):
        found = check_process_patterns("Phase 2 of the workflow")
        assert len(found) > 0

    def test_detects_per_task(self):
        found = check_process_patterns("dispatches subagent per task")
        assert len(found) > 0

    def test_detects_for_each(self):
        found = check_process_patterns("for each file in the list")
        assert len(found) > 0

    def test_detects_then_invoke(self):
        found = check_process_patterns("then invoke the validator")
        assert len(found) > 0


# ---------------------------------------------------------------------------
# Integration tests using validate_skill_cso()
# ---------------------------------------------------------------------------

class TestValidateSkillCso:
    def test_valid_description_passes(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "good-skill",
            "Use when the user needs a code review for Python files.",
        )
        issues = validate_skill_cso(skill)
        assert issues == []

    def test_workflow_keywords_are_critical(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "workflow-skill",
            "Use when executing plans - dispatches subagent per task with invoke between tasks",
        )
        issues = validate_skill_cso(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1

    def test_description_over_500_chars_is_warning(self, tmp_path):
        long_desc = "Use when " + ("the user needs help with something specific. " * 15)
        assert len(long_desc) > 500
        skill = make_skill(tmp_path, "long-skill", long_desc)
        issues = validate_skill_cso(skill)
        warnings = [i for i in issues if is_warning(i)]
        assert len(warnings) >= 1
        assert any("chars" in i.message or "500" in i.message for i in warnings)

    def test_description_at_exactly_500_chars_does_not_warn(self, tmp_path):
        # 500 chars should NOT trigger warning (> 500 triggers it)
        desc = "Use when " + "x" * (500 - len("Use when "))
        assert len(desc) == 500
        skill = make_skill(tmp_path, "ok-length-skill", desc)
        issues = validate_skill_cso(skill)
        warnings = [i for i in issues if is_warning(i)]
        assert all("500" not in i.message for i in warnings)

    def test_tool_name_in_description_is_critical(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "tool-skill",
            "Use when the Bash tool is needed for shell operations",
        )
        issues = validate_skill_cso(skill)
        critical = [i for i in issues if is_critical(i)]
        # "Bash" triggers tool name check
        assert len(critical) >= 1
        assert any("Bash" in i.message or "tool" in i.message.lower() for i in critical)

    def test_process_pattern_per_task_is_critical(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "process-skill",
            "Use when executing implementation plans - dispatches subagent per task",
        )
        issues = validate_skill_cso(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1

    def test_multiple_violations_all_reported(self, tmp_path):
        # Triggers: workflow keyword (run/execute), process pattern (step 1, per task)
        skill = make_skill(
            tmp_path,
            "multi-violation-skill",
            "Use when step 1 is to run things in step 2 for each task and execute",
        )
        issues = validate_skill_cso(skill)
        critical = [i for i in issues if is_critical(i)]
        # Should have at least 2 distinct CRITICAL issues (workflow keywords + process patterns)
        assert len(critical) >= 2

    def test_missing_description_returns_no_issues(self, tmp_path):
        """Frontmatter without description: CSO validator defers to frontmatter validator."""
        skill_dir = tmp_path / "no-desc-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("---\nname: no-desc-skill\n---\n\n# Body\n")
        issues = validate_skill_cso(skill_file)
        # CSO should skip gracefully (no description key)
        assert issues == []

    def test_missing_frontmatter_returns_no_issues(self, tmp_path):
        """No frontmatter at all: CSO defers, does not crash."""
        skill_dir = tmp_path / "no-fm-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("# No frontmatter here\n")
        issues = validate_skill_cso(skill_file)
        assert issues == []

    def test_invoke_keyword_is_critical(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "invoke-skill",
            "Use when the git-commit skill should invoke automatically",
        )
        issues = validate_skill_cso(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("invoke" in i.message.lower() for i in critical)

    def test_then_run_pattern_is_critical(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "then-skill",
            "Use when then running the validator after completing the review",
        )
        issues = validate_skill_cso(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
