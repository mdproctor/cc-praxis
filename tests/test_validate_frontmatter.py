import pytest
import sys
from test_base import is_critical, is_warning, is_note
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validation.validate_frontmatter import (
    validate_skill_frontmatter,
    validate_frontmatter_content,
)


# ---------------------------------------------------------------------------
# Helpers — compare by severity name to avoid module-identity issues
# ---------------------------------------------------------------------------



def make_skill(tmp_path: Path, skill_name: str, content: str) -> Path:
    """Write a SKILL.md inside a correctly-named subdirectory."""
    skill_dir = tmp_path / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content)
    return skill_file


def valid_skill_content(skill_name: str, description: str = None) -> str:
    desc = description or "Use when the user needs a code review."
    return (
        "---\n"
        f"name: {skill_name}\n"
        "description: >\n"
        f"  {desc}\n"
        "---\n\n"
        "# Body\n"
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestValidSkillPasses:
    def test_valid_skill_no_issues(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "java-dev",
            valid_skill_content("java-dev"),
        )
        issues = validate_skill_frontmatter(skill)
        assert issues == []

    def test_valid_skill_with_description_starting_use_when(self, tmp_path):
        skill = make_skill(
            tmp_path,
            "git-commit",
            valid_skill_content("git-commit", "Use when the user says commit this."),
        )
        issues = validate_skill_frontmatter(skill)
        assert issues == []

    def test_exit_code_zero_for_clean_skill(self, tmp_path):
        skill = make_skill(tmp_path, "python-dev", valid_skill_content("python-dev"))
        issues = validate_skill_frontmatter(skill)
        assert not any(is_critical(i) or is_warning(i) for i in issues)


# ---------------------------------------------------------------------------
# Missing / bad frontmatter
# ---------------------------------------------------------------------------

class TestMissingFrontmatter:
    def test_no_frontmatter_is_critical(self, tmp_path):
        skill = make_skill(tmp_path, "no-fm", "# Just a body\n")
        issues = validate_skill_frontmatter(skill)
        assert any(is_critical(i) for i in issues)

    def test_unclosed_frontmatter_is_critical(self, tmp_path):
        content = "---\nname: bad-skill\ndescription: Use when something.\n"
        skill = make_skill(tmp_path, "bad-skill", content)
        issues = validate_skill_frontmatter(skill)
        assert any(is_critical(i) for i in issues)

    def test_invalid_yaml_is_critical(self, tmp_path):
        # Use a truly invalid YAML structure that PyYAML will reject
        content = "---\nname: [unclosed bracket\n---\n"
        skill = make_skill(tmp_path, "invalid-yaml", content)
        issues = validate_skill_frontmatter(skill)
        assert any(is_critical(i) for i in issues)


# ---------------------------------------------------------------------------
# Missing required fields
# ---------------------------------------------------------------------------

class TestMissingRequiredFields:
    def test_missing_name_field_is_critical(self, tmp_path):
        content = "---\ndescription: Use when the user needs help.\n---\n\n# Body\n"
        skill = make_skill(tmp_path, "missing-name", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("name" in i.message.lower() for i in critical)

    def test_missing_description_field_is_critical(self, tmp_path):
        content = "---\nname: missing-desc\n---\n\n# Body\n"
        skill = make_skill(tmp_path, "missing-desc", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("description" in i.message.lower() or "missing" in i.message.lower()
                   for i in critical)


# ---------------------------------------------------------------------------
# Name validation
# ---------------------------------------------------------------------------

class TestNameValidation:
    def test_name_with_underscores_is_critical(self, tmp_path):
        # Directory uses hyphens; name field has underscores
        content = (
            "---\n"
            "name: java_dev\n"
            "description: Use when something.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "java-dev", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        # Should flag either name mismatch or underscores
        assert any(
            "underscore" in i.message.lower()
            or "spaces" in i.message.lower()
            or "mismatch" in i.message.lower()
            for i in critical
        )

    def test_name_with_spaces_is_critical(self, tmp_path):
        content = (
            "---\n"
            "name: java dev\n"
            "description: Use when something.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "java-dev", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1

    def test_name_not_matching_directory_is_critical(self, tmp_path):
        content = (
            "---\n"
            "name: wrong-name\n"
            "description: Use when something.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "correct-name", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("mismatch" in i.message.lower() or "wrong-name" in i.message
                   for i in critical)

    def test_name_matching_directory_passes(self, tmp_path):
        content = valid_skill_content("my-skill")
        skill = make_skill(tmp_path, "my-skill", content)
        issues = validate_skill_frontmatter(skill)
        assert issues == []


# ---------------------------------------------------------------------------
# Description validation
# ---------------------------------------------------------------------------

class TestDescriptionValidation:
    def test_description_not_starting_use_when_is_critical(self, tmp_path):
        content = (
            "---\n"
            "name: bad-desc\n"
            "description: This skill does X and Y.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "bad-desc", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("use when" in i.message.lower() for i in critical)

    def test_description_over_500_chars_is_warning(self, tmp_path):
        long_desc = "Use when " + ("this specific condition occurs repeatedly. " * 15)
        assert len(long_desc) > 500
        content = (
            "---\n"
            "name: long-desc\n"
            f"description: {long_desc}\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "long-desc", content)
        issues = validate_skill_frontmatter(skill)
        warnings = [i for i in issues if is_warning(i)]
        assert len(warnings) >= 1
        assert any("500" in i.message or "long" in i.message.lower() for i in warnings)

    def test_description_with_I_pronoun_is_critical(self, tmp_path):
        content = (
            "---\n"
            "name: pronoun-skill\n"
            "description: Use when I need to review code.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "pronoun-skill", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("pronoun" in i.message.lower() or "personal" in i.message.lower()
                   for i in critical)

    def test_description_with_you_pronoun_is_critical(self, tmp_path):
        content = (
            "---\n"
            "name: you-skill\n"
            "description: Use when you want to commit changes.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "you-skill", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1

    def test_description_with_my_pronoun_is_critical(self, tmp_path):
        content = (
            "---\n"
            "name: my-skill\n"
            "description: Use when my code needs review.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "my-skill", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1

    def test_description_with_your_pronoun_is_critical(self, tmp_path):
        content = (
            "---\n"
            "name: your-skill\n"
            "description: Use when your code has issues.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "your-skill", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1


# ---------------------------------------------------------------------------
# Multiple violations
# ---------------------------------------------------------------------------

class TestMultipleViolations:
    def test_multiple_issues_all_reported(self, tmp_path):
        # Name mismatch + description doesn't start with "Use when" + has pronoun
        content = (
            "---\n"
            "name: wrong-name\n"
            "description: This is my skill for doing things.\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "correct-name", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        # Should have: name mismatch, missing "Use when", personal pronoun
        assert len(critical) >= 2

    def test_extra_field_in_frontmatter_is_critical(self, tmp_path):
        content = (
            "---\n"
            "name: extra-field\n"
            "description: Use when something.\n"
            "tags:\n"
            "  - java\n"
            "  - review\n"
            "---\n\n# Body\n"
        )
        skill = make_skill(tmp_path, "extra-field", content)
        issues = validate_skill_frontmatter(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("unexpected" in i.message.lower() or "tags" in i.message.lower()
                   for i in critical)
