import pytest
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validation.validate_sections import (
    validate_skill_sections,
    is_artifact_producing,
    is_major_skill,
    is_layered_skill,
)

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers — compare by severity name to avoid module-identity issues
# ---------------------------------------------------------------------------

def is_critical(issue) -> bool:
    return issue.severity.name == "CRITICAL"


def is_warning(issue) -> bool:
    return issue.severity.name == "WARNING"


def is_note(issue) -> bool:
    return issue.severity.name == "NOTE"


def make_skill(tmp_path: Path, skill_name: str, body: str) -> Path:
    """Write a SKILL.md inside a correctly-named subdirectory."""
    skill_dir = tmp_path / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    full_content = (
        "---\n"
        f"name: {skill_name}\n"
        "description: Use when testing.\n"
        "---\n\n"
        + body
    )
    skill_file.write_text(full_content)
    return skill_file


# ---------------------------------------------------------------------------
# Fixture bodies
# ---------------------------------------------------------------------------

VALID_BODY = """\
## Skill Chaining

**Triggered by nothing:** This is a standalone skill.

## Overview

Does something useful.
"""

BODY_WITH_PREREQUISITES = """\
## Prerequisites

**This skill builds on `code-review-principles`**.

## Overview

Extends the foundation.
"""

BODY_WITH_SUCCESS_CRITERIA_AND_CHAINING = """\
## Skill Chaining

**Chains to git-commit:** After this skill completes.

## Success Criteria

- ✅ Review completed
- ✅ Issues documented

## Overview

Does a review.
"""

BODY_ARTIFACT_NO_SUCCESS_CRITERIA = """\
## Skill Chaining

**Triggered by user:** User says commit.

## Overview

Creates a commit but lacks success criteria.
"""

BODY_WITH_COMMON_PITFALLS = """\
## Skill Chaining

**Triggered by user.**

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skip review | Misses bugs | Always review |

## Overview

Major skill with pitfalls documented.
"""


# ---------------------------------------------------------------------------
# Helper function unit tests
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_is_artifact_producing_commit(self):
        assert is_artifact_producing("git-commit") is True

    def test_is_artifact_producing_update(self):
        assert is_artifact_producing("update-claude-md") is True

    def test_is_artifact_producing_create(self):
        assert is_artifact_producing("skill-create") is True

    def test_is_artifact_producing_code_review_is_false(self):
        assert is_artifact_producing("java-code-review") is False

    def test_is_major_skill_by_name_review(self):
        assert is_major_skill("java-code-review", "short") is True

    def test_is_major_skill_by_word_count(self):
        big_content = "word " * 600
        assert is_major_skill("some-skill", big_content) is True

    def test_is_major_skill_short_content_no_keyword(self):
        assert is_major_skill("my-skill", "short content here") is False

    def test_is_layered_skill_has_prerequisites_section(self):
        sections = {"Prerequisites": "Builds on code-review-principles"}
        assert is_layered_skill("anything", sections) is True

    def test_is_layered_skill_java_prefix(self):
        assert is_layered_skill("java-code-review", {}) is True

    def test_is_layered_skill_python_prefix(self):
        assert is_layered_skill("python-dev", {}) is True

    def test_is_layered_skill_simple_name_no_prefix(self):
        assert is_layered_skill("adr", {}) is False


# ---------------------------------------------------------------------------
# validate_skill_sections integration tests
# ---------------------------------------------------------------------------

class TestValidateSkillSections:
    def test_valid_skill_with_chaining_passes(self, tmp_path):
        skill = make_skill(tmp_path, "good-skill", VALID_BODY)
        issues = validate_skill_sections(skill)
        critical = [i for i in issues if is_critical(i)]
        assert critical == []

    def test_valid_skill_with_prerequisites_passes_chaining_check(self, tmp_path):
        skill = make_skill(tmp_path, "python-dev", BODY_WITH_PREREQUISITES)
        issues = validate_skill_sections(skill)
        # Should NOT warn about missing Skill Chaining when Prerequisites is present
        assert not any(
            "chaining" in i.message.lower() and "missing" in i.message.lower()
            for i in issues
        )

    def test_missing_both_chaining_and_prerequisites_is_warning(self, tmp_path):
        body = "## Overview\n\nDoes something but has no chaining or prerequisites.\n"
        skill = make_skill(tmp_path, "lonely-skill", body)
        issues = validate_skill_sections(skill)
        warnings = [i for i in issues if is_warning(i)]
        assert len(warnings) >= 1
        assert any(
            "chaining" in i.message.lower() or "prerequisites" in i.message.lower()
            for i in warnings
        )

    def test_artifact_producing_with_success_criteria_passes(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "git-commit",
            BODY_WITH_SUCCESS_CRITERIA_AND_CHAINING,
        )
        issues = validate_skill_sections(skill)
        # Must not warn about missing Success Criteria
        assert not any(
            "success criteria" in i.message.lower() and "missing" in i.message.lower()
            for i in issues
        )

    def test_artifact_producing_missing_success_criteria_is_warning(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "git-commit",
            BODY_ARTIFACT_NO_SUCCESS_CRITERIA,
        )
        issues = validate_skill_sections(skill)
        warnings = [i for i in issues if is_warning(i)]
        assert any("success criteria" in i.message.lower() for i in warnings)

    def test_success_criteria_without_checkboxes_is_note(self, tmp_path):
        body = (
            "## Skill Chaining\n\nTriggered by user.\n\n"
            "## Success Criteria\n\nComplete when all done.\n"
        )
        skill = make_skill(tmp_path, "update-claude-md", body)
        issues = validate_skill_sections(skill)
        notes = [i for i in issues if is_note(i)]
        assert any("checkbox" in i.message.lower() for i in notes)

    def test_major_skill_missing_common_pitfalls_is_note(self, tmp_path):
        body = (
            "## Skill Chaining\n\nTriggered by user.\n\n"
            "## Overview\n\n"
            + "detail " * 600
        )
        skill = make_skill(tmp_path, "big-review-skill", body)
        issues = validate_skill_sections(skill)
        notes = [i for i in issues if is_note(i)]
        assert any(
            "common pitfalls" in i.message.lower() or "pitfall" in i.message.lower()
            for i in notes
        )

    def test_common_pitfalls_with_correct_table_passes(self, tmp_path):
        skill = make_skill(tmp_path, "java-code-review", BODY_WITH_COMMON_PITFALLS)
        issues = validate_skill_sections(skill)
        # Should not note a missing pitfalls table
        assert not any(
            "common pitfalls" in i.message.lower() and "missing" in i.message.lower()
            for i in issues
        )

    def test_common_pitfalls_without_table_format_is_note(self, tmp_path):
        body = (
            "## Skill Chaining\n\nTriggered by user.\n\n"
            "## Common Pitfalls\n\nJust a paragraph, no table.\n\n"
            "## Overview\n\n"
            + "word " * 600
        )
        skill = make_skill(tmp_path, "java-dev", body)
        issues = validate_skill_sections(skill)
        notes = [i for i in issues if is_note(i)]
        assert any("table" in i.message.lower() for i in notes)

    def test_non_artifact_non_major_skill_minimal_passes_no_warnings(self, tmp_path):
        """A simple non-artifact skill only needs Skill Chaining or Prerequisites."""
        body = "## Skill Chaining\n\nNo chains.\n"
        skill = make_skill(tmp_path, "adr", body)
        issues = validate_skill_sections(skill)
        warnings = [i for i in issues if is_warning(i)]
        critical = [i for i in issues if is_critical(i)]
        assert warnings == []
        assert critical == []

    def test_success_criteria_with_checkboxes_passes(self, tmp_path):
        body = (
            "## Skill Chaining\n\nTriggered by user.\n\n"
            "## Success Criteria\n\n"
            "- ✅ Review completed\n"
            "- ✅ Changes committed\n"
        )
        skill = make_skill(tmp_path, "git-commit", body)
        issues = validate_skill_sections(skill)
        # No note about checkboxes
        assert not any(
            "checkbox" in i.message.lower()
            for i in issues
        )


# ---------------------------------------------------------------------------
# Happy path: real skills pass the validator
# ---------------------------------------------------------------------------

class TestRealSkillsPassSections:
    def test_real_skills_no_critical_issues(self):
        """All current skills must pass without CRITICAL severity issues."""
        result = subprocess.run(
            ["python3", "scripts/validation/validate_sections.py"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        # Exit code 1 = CRITICAL — not acceptable
        assert result.returncode != 1, (
            f"Sections validator reported CRITICAL issues:\n"
            f"{result.stdout}\n{result.stderr}"
        )
