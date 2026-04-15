import pytest
import sys
from test_base import is_critical, is_warning, is_note
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validation.validate_naming import (
    validate_skill_naming,
    categorize_skill,
)

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers — compare by severity name to avoid module-identity issues
# ---------------------------------------------------------------------------




def make_skill(tmp_path: Path, skill_name: str) -> Path:
    """Create a minimal SKILL.md at tmp_path/<skill_name>/SKILL.md."""
    skill_dir = tmp_path / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        f"---\nname: {skill_name}\ndescription: Use when testing.\n---\n\n# Body\n"
    )
    return skill_file


# ---------------------------------------------------------------------------
# categorize_skill unit tests
# ---------------------------------------------------------------------------

class TestCategorizeSkill:
    def test_single_word_principles_categorised(self):
        # Pattern is ^[a-z]+-principles$ — only single-word prefix matches
        category, matches = categorize_skill("java-principles")
        assert matches is True
        assert category == "principles"

    def test_multi_word_principles_not_matched_by_pattern(self):
        # "code-review-principles" has multiple hyphens before -principles:
        # the validator pattern ^[a-z]+-principles$ does NOT match this.
        # It falls through to uncategorized (NOTE, not CRITICAL).
        _category, matches = categorize_skill("code-review-principles")
        assert matches is False  # current validator limitation

    def test_language_java_prefix(self):
        category, matches = categorize_skill("java-dev")
        assert matches is True
        assert category == "language"

    def test_language_python_prefix(self):
        category, matches = categorize_skill("python-code-review")
        assert matches is True
        assert category == "language"

    def test_language_typescript_prefix(self):
        # typescript is in the pattern as "typescript"
        category, matches = categorize_skill("typescript-dev")
        assert matches is True

    def test_tool_maven_prefix(self):
        category, matches = categorize_skill("maven-dependency-update")
        assert matches is True
        assert category == "tool"

    def test_tool_npm_prefix(self):
        category, matches = categorize_skill("npm-dependency-update")
        assert matches is True
        assert category == "tool"

    def test_framework_quarkus_prefix(self):
        category, matches = categorize_skill("quarkus-flow-dev")
        assert matches is True
        assert category == "framework"

    def test_workflow_git_prefix(self):
        category, matches = categorize_skill("git-commit")
        assert matches is True
        assert category == "workflow"

    def test_uncategorised_returns_false(self):
        _category, matches = categorize_skill("random-thing-that-fits-no-pattern")
        assert matches is False

    def test_superpowers_namespace(self):
        category, matches = categorize_skill("superpowers:brainstorming")
        assert matches is True
        assert category == "superpowers"

    def test_external_namespace(self):
        category, matches = categorize_skill("frontend-design:frontend-design")
        assert matches is True
        assert category == "external"


# ---------------------------------------------------------------------------
# validate_skill_naming unit tests
# ---------------------------------------------------------------------------

class TestValidateSkillNaming:
    def test_underscore_in_name_is_critical(self, tmp_path):
        skill = make_skill(tmp_path, "java_dev")
        issues = validate_skill_naming(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("underscore" in i.message.lower() for i in critical)

    def test_hyphenated_name_passes_no_critical(self, tmp_path):
        skill = make_skill(tmp_path, "java-dev")
        issues = validate_skill_naming(skill)
        critical = [i for i in issues if is_critical(i)]
        assert critical == []

    def test_valid_principles_skill_passes(self, tmp_path):
        skill = make_skill(tmp_path, "code-review-principles")
        issues = validate_skill_naming(skill)
        critical = [i for i in issues if is_critical(i)]
        assert critical == []

    def test_valid_tool_skill_passes(self, tmp_path):
        skill = make_skill(tmp_path, "maven-dependency-update")
        issues = validate_skill_naming(skill)
        critical = [i for i in issues if is_critical(i)]
        assert critical == []

    def test_valid_framework_skill_passes(self, tmp_path):
        skill = make_skill(tmp_path, "quarkus-flow-dev")
        issues = validate_skill_naming(skill)
        critical = [i for i in issues if is_critical(i)]
        assert critical == []

    def test_unknown_pattern_is_note_not_critical(self, tmp_path):
        # A skill name that fits no standard pattern gets a NOTE, not CRITICAL
        skill = make_skill(tmp_path, "totally-custom-skill")
        issues = validate_skill_naming(skill)
        critical = [i for i in issues if is_critical(i)]
        assert critical == []
        notes = [i for i in issues if is_note(i)]
        assert len(notes) >= 1

    def test_ambiguous_name_with_multiple_type_indicators_is_warning(self, tmp_path):
        # "java-maven-dependency" has both language (java) and tool (maven)
        skill = make_skill(tmp_path, "java-maven-dependency")
        issues = validate_skill_naming(skill)
        warnings = [i for i in issues if is_warning(i)]
        assert len(warnings) >= 1
        assert any("ambiguous" in i.message.lower() for i in warnings)

    def test_non_ambiguous_quarkus_java_skill(self, tmp_path):
        # "quarkus-flow-dev" — quarkus (framework) and java not both present
        # but quarkus itself is framework, 'java' as a literal part is not in name
        skill = make_skill(tmp_path, "quarkus-flow-dev")
        issues = validate_skill_naming(skill)
        warnings = [i for i in issues if is_warning(i)]
        ambiguous_warnings = [i for i in warnings if "ambiguous" in i.message.lower()]
        assert ambiguous_warnings == []


# ---------------------------------------------------------------------------
# Happy path: real skills pass the validator
# ---------------------------------------------------------------------------

class TestRealSkillsPassNaming:
    def test_real_skills_no_critical_issues(self):
        """All current skills in the repository must pass naming validation."""
        result = subprocess.run(
            ["python3", "scripts/validation/validate_naming.py"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        # Exit code 0 = clean, 3 = NOTE only (both acceptable for naming)
        assert result.returncode in (0, 3), (
            f"Naming validator reported CRITICAL or WARNING issues:\n"
            f"{result.stdout}\n{result.stderr}"
        )
