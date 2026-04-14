import pytest
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validation.validate_structure import (
    validate_skill_structure,
    find_referenced_files,
    find_all_files_in_skill,
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


def make_skill(
    tmp_path: Path,
    skill_name: str,
    body: str = "## Skill Chaining\n\nNo chains.\n",
    add_command: bool = True,
) -> Path:
    """
    Create a minimal skill directory.

    add_command: if True, also creates commands/<skill_name>.md (the slash command file).
    """
    skill_dir = tmp_path / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\n"
        f"name: {skill_name}\n"
        "description: Use when testing.\n"
        "---\n\n"
        + body
    )

    if add_command:
        cmd_dir = skill_dir / "commands"
        cmd_dir.mkdir()
        (cmd_dir / f"{skill_name}.md").write_text(f"# /{skill_name}\n")

    return skill_file


# ---------------------------------------------------------------------------
# find_referenced_files unit tests
# ---------------------------------------------------------------------------

class TestFindReferencedFiles:
    def test_no_references_returns_empty(self):
        content = "# Just text with no links or file references.\n"
        refs = find_referenced_files(content)
        assert refs == set()

    def test_markdown_link_is_found(self):
        content = "See [reference](reference.md) for details.\n"
        refs = find_referenced_files(content)
        assert "reference.md" in refs

    def test_http_url_not_included(self):
        content = "See [GitHub](https://github.com/foo) for details.\n"
        refs = find_referenced_files(content)
        assert not any(r.startswith("http") for r in refs)

    def test_backtick_file_path_is_found(self):
        content = "Read `scripts/foo.py` for more info.\n"
        refs = find_referenced_files(content)
        assert "scripts/foo.py" in refs

    def test_see_filename_pattern_is_found(self):
        content = "See funcDSL-reference.md for DSL docs.\n"
        refs = find_referenced_files(content)
        assert "funcDSL-reference.md" in refs

    def test_multiple_references_all_found(self):
        content = (
            "See [ref1](docs/ref1.md) and `scripts/helper.py`.\n"
        )
        refs = find_referenced_files(content)
        assert "docs/ref1.md" in refs
        assert "scripts/helper.py" in refs


# ---------------------------------------------------------------------------
# find_all_files_in_skill unit tests
# ---------------------------------------------------------------------------

class TestFindAllFilesInSkill:
    def test_only_command_file_in_empty_skill(self, tmp_path):
        skill = make_skill(tmp_path, "test-skill")
        skill_dir = skill.parent
        all_files = find_all_files_in_skill(skill_dir)
        # Should contain only commands/<skill_name>.md
        assert len(all_files) == 1
        assert any("commands" in str(f) for f in all_files)

    def test_extra_file_is_found(self, tmp_path):
        skill = make_skill(tmp_path, "test-skill")
        skill_dir = skill.parent
        extra = skill_dir / "extra-reference.md"
        extra.write_text("# Extra reference\n")
        all_files = find_all_files_in_skill(skill_dir)
        names = {f.name for f in all_files}
        assert "extra-reference.md" in names

    def test_skill_md_itself_not_included(self, tmp_path):
        skill = make_skill(tmp_path, "test-skill")
        skill_dir = skill.parent
        all_files = find_all_files_in_skill(skill_dir)
        names = {f.name for f in all_files}
        assert "SKILL.md" not in names


# ---------------------------------------------------------------------------
# validate_skill_structure integration tests
# ---------------------------------------------------------------------------

class TestValidateSkillStructure:
    def test_valid_skill_with_command_file_passes(self, tmp_path):
        skill = make_skill(tmp_path, "good-skill", add_command=True)
        issues = validate_skill_structure(skill)
        critical = [i for i in issues if is_critical(i)]
        assert critical == []

    def test_missing_command_file_is_critical(self, tmp_path):
        skill = make_skill(tmp_path, "no-command", add_command=False)
        issues = validate_skill_structure(skill)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1
        assert any("command" in i.message.lower() or "commands/" in i.message
                   for i in critical)

    def test_referenced_file_exists_no_warning(self, tmp_path):
        body = "## Overview\n\nSee [reference](reference.md) for details.\n"
        skill = make_skill(tmp_path, "ref-skill", body=body)
        skill_dir = skill.parent
        # Create the referenced file
        (skill_dir / "reference.md").write_text("# Reference\n")
        issues = validate_skill_structure(skill)
        warnings = [i for i in issues if is_warning(i)]
        # No missing-reference warning
        assert not any("reference.md" in i.message for i in warnings)

    def test_referenced_file_missing_is_warning(self, tmp_path):
        body = "## Overview\n\nSee [missing-file](missing-file.md) for details.\n"
        skill = make_skill(tmp_path, "missing-ref-skill", body=body)
        issues = validate_skill_structure(skill)
        warnings = [i for i in issues if is_warning(i)]
        assert any("missing-file.md" in i.message for i in warnings)

    def test_orphaned_extra_file_is_note(self, tmp_path):
        skill = make_skill(tmp_path, "orphan-skill")
        skill_dir = skill.parent
        # Create an extra file not referenced in SKILL.md
        (skill_dir / "orphaned-doc.md").write_text("# Orphaned\n")
        issues = validate_skill_structure(skill)
        notes = [i for i in issues if is_note(i)]
        assert any(
            "orphan" in i.message.lower() or "orphaned-doc.md" in i.message
            for i in notes
        )

    def test_file_in_unexpected_subdir_is_note(self, tmp_path):
        skill = make_skill(tmp_path, "subdir-skill")
        skill_dir = skill.parent
        weird_dir = skill_dir / "weird-subdir"
        weird_dir.mkdir()
        (weird_dir / "stuff.md").write_text("# Stuff\n")
        issues = validate_skill_structure(skill)
        notes = [i for i in issues if is_note(i)]
        assert any(
            "weird-subdir" in i.message or "unexpected" in i.message.lower()
            for i in notes
        )

    def test_file_in_expected_subdir_not_flagged_unexpected(self, tmp_path):
        skill = make_skill(tmp_path, "standard-skill")
        skill_dir = skill.parent
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "helper.py").write_text("# helper\n")
        issues = validate_skill_structure(skill)
        notes = [i for i in issues if is_note(i)]
        # Should NOT flag 'scripts/' as unexpected
        assert not any(
            "scripts" in i.message and "unexpected" in i.message.lower()
            for i in notes
        )

    def test_command_file_name_must_match_skill_name(self, tmp_path):
        """Wrong command filename is treated same as missing command."""
        skill_dir = tmp_path / "named-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            "---\nname: named-skill\ndescription: Use when testing.\n---\n\n# Body\n"
        )
        cmd_dir = skill_dir / "commands"
        cmd_dir.mkdir()
        # Create a command file with WRONG name
        (cmd_dir / "wrong-name.md").write_text("# Wrong\n")
        issues = validate_skill_structure(skill_file)
        critical = [i for i in issues if is_critical(i)]
        assert len(critical) >= 1


# ---------------------------------------------------------------------------
# Happy path: real skills pass the validator
# ---------------------------------------------------------------------------

class TestRealSkillsPassStructure:
    def test_real_skills_no_critical_issues(self):
        """All current skills must have their slash command files in place."""
        result = subprocess.run(
            ["python3", "scripts/validation/validate_structure.py"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode != 1, (
            f"Structure validator reported CRITICAL issues:\n"
            f"{result.stdout}\n{result.stderr}"
        )
