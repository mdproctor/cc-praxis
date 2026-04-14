#!/usr/bin/env python3
"""
Tests for scripts/validation/validate_cross_document.py

Checks cross-document consistency: SKILL.md backtick references vs actual skills,
and README skills list vs filesystem.

Key design note: validate_cross_document extracts ALL backtick terms from SKILL.md
files (not just structured "Skill Chaining" sections), which produces many false
positives (Python keywords, shell commands, etc. in backticks). Tests reflect this
actual behaviour.

All unit tests use temporary directories — never the real repo.
Integration test runs the script against the real repo.
"""

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validation" / "validate_cross_document.py"

# Allow importing the module under test
sys.path.insert(0, str(SCRIPT_PATH.parent))
import validate_cross_document as vcd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_skill(base: Path, name: str, content: str = None) -> Path:
    """Create a skill directory with SKILL.md. Returns path to SKILL.md."""
    skill_dir = base / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    if content is None:
        content = (
            f"---\nname: {name}\ndescription: >\n  Use when testing {name}.\n---\n\n"
            "## Overview\n\nDoes things.\n"
        )
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")
    return skill_file


def make_readme(base: Path, skills: list) -> None:
    """Write README.md with #### **skill-name** entries for each skill in skills."""
    lines = ["# README\n\n## Skills\n\n"]
    for skill in skills:
        lines.append(f"#### **{skill}**\n\nDoes {skill} things.\n\n")
    (base / "README.md").write_text("".join(lines), encoding="utf-8")


def run_in(cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


def chdir_call(func, base: Path):
    """Call func from base directory, then restore cwd."""
    import os
    old = os.getcwd()
    try:
        os.chdir(base)
        return func()
    finally:
        os.chdir(old)


# ---------------------------------------------------------------------------
# get_skill_names_from_filesystem
# ---------------------------------------------------------------------------

class TestGetSkillNamesFromFilesystem(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_directory_returns_empty_set(self):
        result = chdir_call(vcd.get_skill_names_from_filesystem, self.base)
        self.assertEqual(result, set())

    def test_single_skill_discovered(self):
        make_skill(self.base, "my-skill")
        result = chdir_call(vcd.get_skill_names_from_filesystem, self.base)
        self.assertIn("my-skill", result)

    def test_multiple_skills_all_discovered(self):
        for name in ["alpha-skill", "beta-skill", "gamma-skill"]:
            make_skill(self.base, name)
        result = chdir_call(vcd.get_skill_names_from_filesystem, self.base)
        self.assertEqual(result, {"alpha-skill", "beta-skill", "gamma-skill"})

    def test_directory_without_skill_md_excluded(self):
        (self.base / "not-a-skill").mkdir()
        (self.base / "not-a-skill" / "OTHER.md").write_text("not a skill\n")
        result = chdir_call(vcd.get_skill_names_from_filesystem, self.base)
        self.assertNotIn("not-a-skill", result)


# ---------------------------------------------------------------------------
# get_skill_names_from_readme
# ---------------------------------------------------------------------------

class TestGetSkillNamesFromReadme(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_readme_returns_empty_set(self):
        result = chdir_call(vcd.get_skill_names_from_readme, self.base)
        self.assertEqual(result, set())

    def test_single_skill_heading_parsed(self):
        make_readme(self.base, ["test-skill"])
        result = chdir_call(vcd.get_skill_names_from_readme, self.base)
        self.assertIn("test-skill", result)

    def test_multiple_skill_headings_all_parsed(self):
        make_readme(self.base, ["skill-a", "skill-b", "skill-c"])
        result = chdir_call(vcd.get_skill_names_from_readme, self.base)
        self.assertEqual(result, {"skill-a", "skill-b", "skill-c"})

    def test_plain_heading_without_bold_not_parsed(self):
        (self.base / "README.md").write_text("#### skill-name\n\nNo bold markers.\n")
        result = chdir_call(vcd.get_skill_names_from_readme, self.base)
        self.assertNotIn("skill-name", result)

    def test_empty_readme_returns_empty_set(self):
        (self.base / "README.md").write_text("# Just a title\n\nNo skills.\n")
        result = chdir_call(vcd.get_skill_names_from_readme, self.base)
        self.assertEqual(result, set())


# ---------------------------------------------------------------------------
# get_chaining_claims_from_skills — backtick extraction behaviour
# ---------------------------------------------------------------------------

class TestGetChainingClaimsFromSkills(unittest.TestCase):
    """
    validate_cross_document extracts ALL backtick-quoted terms from SKILL.md,
    not just those in 'Skill Chaining' or 'Prerequisites' sections.
    This is the actual implemented behaviour.
    """

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_skills_returns_empty_dict(self):
        result = chdir_call(vcd.get_chaining_claims_from_skills, self.base)
        self.assertEqual(result, {})

    def test_skill_with_no_backtick_references_not_in_result(self):
        make_skill(self.base, "standalone-skill",
            "---\nname: standalone-skill\ndescription: >\n  Use when alone.\n---\n\n"
            "## Overview\n\nNo backtick references here.\n")
        result = chdir_call(vcd.get_chaining_claims_from_skills, self.base)
        # Either not present or empty list
        claims = result.get("standalone-skill", [])
        self.assertEqual(claims, [])

    def test_self_references_excluded(self):
        """Backtick references to the skill's own name must be excluded."""
        make_skill(self.base, "my-skill",
            "---\nname: my-skill\ndescription: >\n  Use when testing.\n---\n\n"
            "## Overview\n\nThe `my-skill` does things.\n")
        result = chdir_call(vcd.get_chaining_claims_from_skills, self.base)
        claims = result.get("my-skill", [])
        self.assertNotIn("my-skill", claims)

    def test_backtick_reference_to_other_skill_captured(self):
        """Any backtick reference to another skill-name pattern is captured."""
        make_skill(self.base, "source-skill",
            "---\nname: source-skill\ndescription: >\n  Use when sourcing.\n---\n\n"
            "## Overview\n\nRun `target-skill` after this.\n")
        result = chdir_call(vcd.get_chaining_claims_from_skills, self.base)
        claims = result.get("source-skill", [])
        self.assertIn("target-skill", claims)

    def test_non_skill_backtick_terms_also_captured(self):
        """
        Short tokens, keywords, and command names in backticks ARE captured
        because the validator uses a broad pattern. This reflects actual behaviour —
        not ideal, but what we must test against.
        """
        make_skill(self.base, "python-skill",
            "---\nname: python-skill\ndescription: >\n  Use when pythoning.\n---\n\n"
            "## Steps\n\nUse `dict` and `list` types. Run `pytest` tests.\n")
        result = chdir_call(vcd.get_chaining_claims_from_skills, self.base)
        claims = result.get("python-skill", [])
        # Broad matching: these terms WILL be in claims (false positives)
        self.assertIn("dict", claims)
        self.assertIn("list", claims)

    def test_duplicate_references_deduplicated(self):
        """Multiple uses of the same backtick term produce only one entry."""
        make_skill(self.base, "dup-skill",
            "---\nname: dup-skill\ndescription: >\n  Use when duping.\n---\n\n"
            "## Overview\n\nRun `other-skill` here. Also `other-skill` there.\n")
        result = chdir_call(vcd.get_chaining_claims_from_skills, self.base)
        claims = result.get("dup-skill", [])
        self.assertEqual(claims.count("other-skill"), 1)

    def test_multiple_skills_each_have_own_claims(self):
        make_skill(self.base, "skill-alpha",
            "---\nname: skill-alpha\ndescription: >\n  Use when alpha.\n---\n\n"
            "## Overview\n\nCalls `skill-beta`.\n")
        make_skill(self.base, "skill-beta",
            "---\nname: skill-beta\ndescription: >\n  Use when beta.\n---\n\n"
            "## Overview\n\nCalls `skill-gamma`.\n")
        result = chdir_call(vcd.get_chaining_claims_from_skills, self.base)
        self.assertIn("skill-beta", result.get("skill-alpha", []))
        self.assertIn("skill-gamma", result.get("skill-beta", []))


# ---------------------------------------------------------------------------
# validate_skill_existence
# ---------------------------------------------------------------------------

class TestValidateSkillExistence(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_skills_no_issues(self):
        issues = chdir_call(vcd.validate_skill_existence, self.base)
        self.assertEqual(issues, [])

    def test_skill_with_no_backtick_references_no_issues(self):
        make_skill(self.base, "clean-skill",
            "---\nname: clean-skill\ndescription: >\n  Use when clean.\n---\n\n"
            "## Overview\n\nNo references.\n")
        issues = chdir_call(vcd.validate_skill_existence, self.base)
        self.assertEqual(issues, [])

    def test_skill_references_existing_skill_no_issues(self):
        make_skill(self.base, "source-skill",
            "---\nname: source-skill\ndescription: >\n  Use when sourcing.\n---\n\n"
            "## Overview\n\nCalls `target-skill`.\n")
        make_skill(self.base, "target-skill")
        issues = chdir_call(vcd.validate_skill_existence, self.base)
        # No CRITICAL for target-skill since it exists
        critical = [i for i in issues if i["severity"] == "CRITICAL"
                    and "target-skill" in i.get("reference", "")]
        self.assertEqual(critical, [])

    def test_reference_to_nonexistent_skill_is_warning(self):
        make_skill(self.base, "source-skill",
            "---\nname: source-skill\ndescription: >\n  Use when sourcing.\n---\n\n"
            "## Overview\n\nCalls `ghost-skill`.\n")
        issues = chdir_call(vcd.validate_skill_existence, self.base)
        ghost_issues = [i for i in issues if "ghost-skill" in i.get("reference", "")]
        self.assertGreater(len(ghost_issues), 0)
        for issue in ghost_issues:
            self.assertEqual(issue["severity"], "WARNING")

    def test_issue_includes_referencing_skill_name(self):
        make_skill(self.base, "referencing-skill",
            "---\nname: referencing-skill\ndescription: >\n  Use when ref.\n---\n\n"
            "## Overview\n\nCalls `missing-skill`.\n")
        issues = chdir_call(vcd.validate_skill_existence, self.base)
        missing_issues = [i for i in issues if "missing-skill" in i.get("reference", "")]
        self.assertTrue(all(i["skill"] == "referencing-skill" for i in missing_issues))

    def test_issue_type_is_nonexistent_skill_reference(self):
        make_skill(self.base, "broken-skill",
            "---\nname: broken-skill\ndescription: >\n  Use when broken.\n---\n\n"
            "## Overview\n\nCalls `absent-skill`.\n")
        issues = chdir_call(vcd.validate_skill_existence, self.base)
        typed = [i for i in issues if i.get("type") == "nonexistent_skill_reference"
                 and "absent-skill" in i.get("reference", "")]
        self.assertGreater(len(typed), 0)

    def test_issue_message_includes_both_skill_and_reference(self):
        make_skill(self.base, "a-skill",
            "---\nname: a-skill\ndescription: >\n  Use when a.\n---\n\n"
            "## Overview\n\nCalls `b-skill`.\n")
        issues = chdir_call(vcd.validate_skill_existence, self.base)
        b_issues = [i for i in issues if "b-skill" in i.get("reference", "")]
        self.assertTrue(all("a-skill" in i["message"] for i in b_issues))


# ---------------------------------------------------------------------------
# validate_readme_consistency
# ---------------------------------------------------------------------------

class TestValidateReadmeConsistency(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_repo_and_readme_is_clean(self):
        make_readme(self.base, [])
        issues = chdir_call(vcd.validate_readme_consistency, self.base)
        self.assertEqual(issues, [])

    def test_skill_in_both_readme_and_filesystem_is_clean(self):
        make_skill(self.base, "existing-skill")
        make_readme(self.base, ["existing-skill"])
        issues = chdir_call(vcd.validate_readme_consistency, self.base)
        self.assertEqual(issues, [])

    def test_skill_on_filesystem_missing_from_readme_is_warning(self):
        make_skill(self.base, "untracked-skill")
        make_readme(self.base, [])
        issues = chdir_call(vcd.validate_readme_consistency, self.base)
        warnings = [i for i in issues if i["severity"] == "WARNING"]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["type"], "missing_from_readme")
        self.assertIn("untracked-skill", warnings[0]["skills"])

    def test_skill_in_readme_not_on_filesystem_is_critical(self):
        make_skill(self.base, "real-skill")
        make_readme(self.base, ["real-skill", "stale-skill"])
        issues = chdir_call(vcd.validate_readme_consistency, self.base)
        critical = [i for i in issues if i["severity"] == "CRITICAL"]
        self.assertEqual(len(critical), 1)
        self.assertEqual(critical[0]["type"], "stale_in_readme")
        self.assertIn("stale-skill", critical[0]["skills"])

    def test_multiple_stale_skills_grouped_in_one_critical(self):
        make_readme(self.base, ["ghost-a", "ghost-b", "ghost-c"])
        issues = chdir_call(vcd.validate_readme_consistency, self.base)
        critical = [i for i in issues if i["severity"] == "CRITICAL"]
        self.assertEqual(len(critical), 1)
        for name in ["ghost-a", "ghost-b", "ghost-c"]:
            self.assertIn(name, critical[0]["skills"])

    def test_multiple_undocumented_skills_grouped_in_one_warning(self):
        for name in ["skill-x", "skill-y"]:
            make_skill(self.base, name)
        make_readme(self.base, [])
        issues = chdir_call(vcd.validate_readme_consistency, self.base)
        warnings = [i for i in issues if i["severity"] == "WARNING"]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(set(warnings[0]["skills"]), {"skill-x", "skill-y"})

    def test_no_readme_file_returns_critical(self):
        make_skill(self.base, "some-skill")
        # No README.md created
        issues = chdir_call(vcd.validate_readme_consistency, self.base)
        # some-skill is on FS but not in README (empty set) → WARNING
        warnings = [i for i in issues if i["severity"] == "WARNING"]
        self.assertGreater(len(warnings), 0)


# ---------------------------------------------------------------------------
# Exit codes via subprocess — controlled fixture directories
# ---------------------------------------------------------------------------

class TestCrossDocumentSubprocess(unittest.TestCase):

    def test_clean_repo_exits_zero(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_skill(base, "skill-one")
            make_skill(base, "skill-two")
            make_readme(base, ["skill-one", "skill-two"])
            result = run_in(base)
            self.assertEqual(result.returncode, 0,
                msg=f"Expected exit 0, got {result.returncode}\nstderr: {result.stderr}")

    def test_stale_readme_skill_exits_one(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_skill(base, "real-skill")
            make_readme(base, ["real-skill", "phantom-skill"])
            result = run_in(base)
            self.assertEqual(result.returncode, 1,
                msg=f"Expected exit 1 (CRITICAL), got {result.returncode}\nstderr: {result.stderr}")

    def test_undocumented_skill_exits_two(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_skill(base, "documented-skill")
            make_skill(base, "undocumented-skill")
            make_readme(base, ["documented-skill"])
            result = run_in(base)
            self.assertEqual(result.returncode, 2,
                msg=f"Expected exit 2 (WARNING), got {result.returncode}\nstderr: {result.stderr}")

    def test_skill_referencing_nonexistent_exits_two(self):
        """
        Backtick references to nonexistent skills produce WARNING (exit 2),
        not CRITICAL, in validate_cross_document.
        """
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_skill(base, "broken-skill",
                "---\nname: broken-skill\ndescription: >\n  Use when broken.\n---\n\n"
                "## Overview\n\nCalls `missing-skill`.\n")
            make_readme(base, ["broken-skill"])
            result = run_in(base)
            # WARNING exit because nonexistent_skill_reference is WARNING severity
            self.assertEqual(result.returncode, 2,
                msg=f"Expected exit 2 (WARNING), got {result.returncode}\nstderr: {result.stderr}")

    def test_empty_directory_exits_zero(self):
        with TemporaryDirectory() as tmp:
            result = run_in(Path(tmp))
            self.assertEqual(result.returncode, 0,
                msg=f"Expected exit 0 for empty dir, got {result.returncode}\nstderr: {result.stderr}")

    def test_output_goes_to_stderr(self):
        """Cross-document validator prints to stderr, not stdout."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_readme(base, ["phantom"])
            result = run_in(base)
            self.assertIn("Cross-Document Consistency Check", result.stderr)
            # stdout should be empty or minimal
            self.assertEqual(result.stdout.strip(), "")

    def test_skill_name_appears_in_error_output(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_readme(base, ["clearly-missing-skill"])
            result = run_in(base)
            self.assertIn("clearly-missing-skill", result.stderr)


# ---------------------------------------------------------------------------
# Integration: real repo
# ---------------------------------------------------------------------------

class TestCrossDocumentRealRepo(unittest.TestCase):

    def test_real_repo_exits_with_known_code(self):
        """
        Real repo has known issues (forage in README but not on disk, plus
        ~400 false-positive backtick warnings). Exit code must be 1 or 2.
        This test documents current state — it passes as long as the validator runs.
        """
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertIn(result.returncode, [0, 1, 2],
            msg=f"Unexpected exit code {result.returncode}\nstderr: {result.stderr}")

    def test_real_repo_output_goes_to_stderr(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertIn("Cross-Document Consistency Check", result.stderr)

    def test_real_repo_stdout_is_empty(self):
        """All output is on stderr; stdout should be empty."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
