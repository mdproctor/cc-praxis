#!/usr/bin/env python3
"""
Tests for scripts/validation/validate_examples.py

Covers:
- Balanced fence checking (CRITICAL for unclosed fences)
- YAML block validation (WARNING for invalid YAML, skip for templates)
- JSON block validation (WARNING for invalid JSON, skip for templates)
- Template marker detection (skip blocks with {placeholder}, <X>, [Add ...)
- extract_fenced_blocks — only returns yaml/json blocks
- has_template_markers
- validate_skill_file as integration point
- Exit codes via subprocess
"""

import json
import subprocess
import sys
from test_base import is_critical, is_warning, is_note
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validation" / "validate_examples.py"

sys.path.insert(0, str(SCRIPT_PATH.parent))
from validate_examples import (
    has_template_markers,
    extract_fenced_blocks,
    check_balanced_fences,
    check_yaml_block,
    check_json_block,
    validate_skill_file,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_skill_file(tmp_path: Path, name: str, content: str) -> Path:
    """Create a SKILL.md in a properly-named skill directory."""
    skill_dir = tmp_path / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    f = skill_dir / "SKILL.md"
    f.write_text(content, encoding="utf-8")
    return f




# ---------------------------------------------------------------------------
# has_template_markers
# ---------------------------------------------------------------------------

class TestHasTemplateMarkers(unittest.TestCase):

    def test_curly_brace_placeholder_detected(self):
        self.assertTrue(has_template_markers("name: {your-name}"))

    def test_angle_bracket_tag_detected(self):
        self.assertTrue(has_template_markers("value: <MyValue>"))

    def test_add_bracket_placeholder_detected(self):
        self.assertTrue(has_template_markers("- [Add your item here]"))

    def test_your_bracket_placeholder_detected(self):
        self.assertTrue(has_template_markers("- [Your content]"))

    def test_todo_bracket_placeholder_detected(self):
        self.assertTrue(has_template_markers("- [TODO: fill this in]"))

    def test_clean_content_has_no_markers(self):
        self.assertFalse(has_template_markers("name: real-skill-name\nvalue: 42"))

    def test_empty_string_has_no_markers(self):
        self.assertFalse(has_template_markers(""))

    def test_plain_brackets_without_keyword_not_detected(self):
        # [something] without Add/Your/TODO should NOT be flagged
        self.assertFalse(has_template_markers("- [completed task]"))


# ---------------------------------------------------------------------------
# extract_fenced_blocks
# ---------------------------------------------------------------------------

class TestExtractFencedBlocks(unittest.TestCase):

    def test_yaml_block_extracted(self):
        content = "```yaml\nname: foo\n```"
        blocks = extract_fenced_blocks(content)
        self.assertEqual(len(blocks), 1)
        lang, block_content, start_line = blocks[0]
        self.assertEqual(lang, "yaml")
        self.assertIn("name: foo", block_content)

    def test_json_block_extracted(self):
        content = '```json\n{"key": "value"}\n```'
        blocks = extract_fenced_blocks(content)
        self.assertEqual(len(blocks), 1)
        lang, _, _ = blocks[0]
        self.assertEqual(lang, "json")

    def test_python_block_not_extracted(self):
        # Only yaml/json blocks are returned
        content = "```python\nprint('hello')\n```"
        blocks = extract_fenced_blocks(content)
        self.assertEqual(blocks, [])

    def test_bash_block_not_extracted(self):
        content = "```bash\necho hello\n```"
        blocks = extract_fenced_blocks(content)
        self.assertEqual(blocks, [])

    def test_unlabelled_block_not_extracted(self):
        content = "```\nsome content\n```"
        blocks = extract_fenced_blocks(content)
        self.assertEqual(blocks, [])

    def test_start_line_is_one_based(self):
        content = "```yaml\nfoo: bar\n```"
        blocks = extract_fenced_blocks(content)
        _, _, start_line = blocks[0]
        self.assertEqual(start_line, 1)  # line 1 (1-based)

    def test_start_line_correct_when_preceded_by_text(self):
        content = "# Header\n\nSome text.\n\n```yaml\nfoo: bar\n```"
        blocks = extract_fenced_blocks(content)
        self.assertEqual(len(blocks), 1)
        _, _, start_line = blocks[0]
        # The fence open is on line 5 (1-based)
        self.assertEqual(start_line, 5)

    def test_multiple_blocks_extracted(self):
        content = "```yaml\na: 1\n```\n\n```json\n{\"b\": 2}\n```"
        blocks = extract_fenced_blocks(content)
        langs = [b[0] for b in blocks]
        self.assertIn("yaml", langs)
        self.assertIn("json", langs)
        self.assertEqual(len(blocks), 2)

    def test_unclosed_block_not_returned(self):
        # Unclosed block — extract_fenced_blocks does not close it
        content = "```yaml\nfoo: bar\n"
        blocks = extract_fenced_blocks(content)
        self.assertEqual(blocks, [])


# ---------------------------------------------------------------------------
# check_balanced_fences
# ---------------------------------------------------------------------------

class TestCheckBalancedFences(unittest.TestCase):

    def test_no_fences_passes(self):
        content = "# No code here\n\nJust text."
        issues = check_balanced_fences(content, Path("test/SKILL.md"))
        self.assertEqual(issues, [])

    def test_balanced_fences_pass(self):
        content = "```bash\necho hi\n```"
        issues = check_balanced_fences(content, Path("test/SKILL.md"))
        self.assertEqual(issues, [])

    def test_unclosed_fence_is_critical(self):
        content = "```yaml\nfoo: bar\n"
        issues = check_balanced_fences(content, Path("test/SKILL.md"))
        self.assertEqual(len(issues), 1)
        self.assertTrue(is_critical(issues[0]))

    def test_unclosed_fence_message(self):
        content = "```\nsome content\n"
        issues = check_balanced_fences(content, Path("test/SKILL.md"))
        self.assertIn("unclosed", issues[0].message.lower())

    def test_two_fences_balanced(self):
        content = "```python\nprint()\n```\n\n```bash\necho\n```"
        issues = check_balanced_fences(content, Path("test/SKILL.md"))
        self.assertEqual(issues, [])

    def test_three_fences_unbalanced_is_critical(self):
        content = "```python\nprint()\n```\n\n```bash\necho\n"
        issues = check_balanced_fences(content, Path("test/SKILL.md"))
        self.assertEqual(len(issues), 1)
        self.assertTrue(is_critical(issues[0]))

    def test_unclosed_fence_reports_open_line_number(self):
        content = "Line 1\nLine 2\n```yaml\nfoo: bar\n"
        issues = check_balanced_fences(content, Path("test/SKILL.md"))
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 3)


# ---------------------------------------------------------------------------
# check_yaml_block
# ---------------------------------------------------------------------------

class TestCheckYamlBlock(unittest.TestCase):

    def test_valid_yaml_returns_none(self):
        result = check_yaml_block("name: foo\nvalue: 42", Path("test/SKILL.md"), 1)
        self.assertIsNone(result)

    def test_invalid_yaml_returns_warning(self):
        bad_yaml = "key: :\n  bad: : nesting"
        result = check_yaml_block(bad_yaml, Path("test/SKILL.md"), 5)
        self.assertIsNotNone(result)
        self.assertTrue(is_warning(result))

    def test_invalid_yaml_preserves_start_line(self):
        bad_yaml = "key: :\n  bad:"
        result = check_yaml_block(bad_yaml, Path("test/SKILL.md"), 10)
        self.assertEqual(result.line_number, 10)

    def test_template_markers_skip_validation(self):
        # Block with {placeholder} should be skipped even if invalid YAML
        template_block = "name: {your-name}\nvalue: {placeholder}"
        result = check_yaml_block(template_block, Path("test/SKILL.md"), 1)
        self.assertIsNone(result)

    def test_valid_yaml_multiline(self):
        yaml_block = "items:\n  - one\n  - two\ncount: 2"
        result = check_yaml_block(yaml_block, Path("test/SKILL.md"), 1)
        self.assertIsNone(result)

    def test_invalid_yaml_message_mentions_yaml(self):
        bad_yaml = "key: :\n  misindent:"
        result = check_yaml_block(bad_yaml, Path("test/SKILL.md"), 1)
        if result:
            self.assertIn("YAML", result.message)


# ---------------------------------------------------------------------------
# check_json_block
# ---------------------------------------------------------------------------

class TestCheckJsonBlock(unittest.TestCase):

    def test_valid_json_returns_none(self):
        result = check_json_block('{"key": "value", "num": 42}', Path("test/SKILL.md"), 1)
        self.assertIsNone(result)

    def test_invalid_json_returns_warning(self):
        # Use trailing comma in array — invalid JSON without curly braces (no template match)
        bad_json = '[1, 2, 3,]'
        result = check_json_block(bad_json, Path("test/SKILL.md"), 5)
        self.assertIsNotNone(result)
        self.assertTrue(is_warning(result))

    def test_invalid_json_preserves_start_line(self):
        # Unclosed array — invalid JSON that doesn't trigger template detection
        bad_json = '[invalid json here'
        result = check_json_block(bad_json, Path("test/SKILL.md"), 12)
        self.assertIsNotNone(result)
        self.assertEqual(result.line_number, 12)

    def test_template_markers_skip_validation(self):
        template_block = '{"name": "{skill-name}", "type": "<MyType>"}'
        result = check_json_block(template_block, Path("test/SKILL.md"), 1)
        self.assertIsNone(result)

    def test_valid_json_array(self):
        result = check_json_block('[1, 2, 3]', Path("test/SKILL.md"), 1)
        self.assertIsNone(result)

    def test_invalid_json_message_mentions_json(self):
        bad_json = '{not valid json'
        result = check_json_block(bad_json, Path("test/SKILL.md"), 1)
        if result:
            self.assertIn("JSON", result.message)


# ---------------------------------------------------------------------------
# validate_skill_file — integration
# ---------------------------------------------------------------------------

class TestValidateSkillFile(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.test_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_file_no_issues(self):
        f = make_skill_file(self.test_dir, "clean-skill", "# No code blocks here\n")
        issues = validate_skill_file(f)
        self.assertEqual(issues, [])

    def test_valid_yaml_block_no_issues(self):
        content = "# Skill\n\n```yaml\nname: foo\nvalue: bar\n```\n"
        f = make_skill_file(self.test_dir, "yaml-skill", content)
        issues = validate_skill_file(f)
        self.assertEqual(issues, [])

    def test_invalid_yaml_block_produces_warning(self):
        content = "# Skill\n\n```yaml\nkey: :\n  bad:\n```\n"
        f = make_skill_file(self.test_dir, "bad-yaml-skill", content)
        issues = validate_skill_file(f)
        warnings = [i for i in issues if is_warning(i)]
        self.assertGreater(len(warnings), 0)

    def test_valid_json_block_no_issues(self):
        content = '# Skill\n\n```json\n{"key": "value"}\n```\n'
        f = make_skill_file(self.test_dir, "json-skill", content)
        issues = validate_skill_file(f)
        self.assertEqual(issues, [])

    def test_invalid_json_block_produces_warning(self):
        # Use trailing comma in array — avoids template marker false-skip
        content = '# Skill\n\n```json\n[1, 2, 3,]\n```\n'
        f = make_skill_file(self.test_dir, "bad-json-skill", content)
        issues = validate_skill_file(f)
        warnings = [i for i in issues if is_warning(i)]
        self.assertGreater(len(warnings), 0)

    def test_unclosed_fence_produces_critical(self):
        content = "# Skill\n\n```yaml\nname: foo\n"
        f = make_skill_file(self.test_dir, "unclosed-skill", content)
        issues = validate_skill_file(f)
        criticals = [i for i in issues if is_critical(i)]
        self.assertGreater(len(criticals), 0)

    def test_multiple_issues_all_reported(self):
        # Two bad yaml blocks; both should be flagged
        content = (
            "# Skill\n\n"
            "```yaml\nkey: :\n  bad:\n```\n\n"
            "```yaml\nother: :\n  also-bad:\n```\n"
        )
        f = make_skill_file(self.test_dir, "multi-issue-skill", content)
        issues = validate_skill_file(f)
        warnings = [i for i in issues if is_warning(i)]
        self.assertGreaterEqual(len(warnings), 2)

    def test_template_yaml_block_skipped(self):
        content = "# Skill\n\n```yaml\nname: {your-name}\n```\n"
        f = make_skill_file(self.test_dir, "template-skill", content)
        issues = validate_skill_file(f)
        # Template blocks are skipped — no warnings
        warnings = [i for i in issues if is_warning(i)]
        self.assertEqual(warnings, [])

    def test_python_block_not_checked(self):
        # Python blocks with syntax errors should NOT be flagged (only yaml/json are checked)
        content = "# Skill\n\n```python\ndef broken(\n```\n"
        f = make_skill_file(self.test_dir, "python-skill", content)
        issues = validate_skill_file(f)
        warnings = [i for i in issues if is_warning(i)]
        self.assertEqual(warnings, [])

    def test_bash_block_not_checked(self):
        content = "# Skill\n\n```bash\necho 'hello'\n```\n"
        f = make_skill_file(self.test_dir, "bash-skill", content)
        issues = validate_skill_file(f)
        self.assertEqual(issues, [])

    def test_inline_code_not_checked(self):
        # Inline `code` should never be flagged
        content = "# Skill\n\nUse `yaml` or `json` as needed.\n"
        f = make_skill_file(self.test_dir, "inline-skill", content)
        issues = validate_skill_file(f)
        self.assertEqual(issues, [])


# ---------------------------------------------------------------------------
# Exit codes via subprocess
# ---------------------------------------------------------------------------

class TestExitCodes(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.test_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *files) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH)] + [str(f) for f in files],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

    def test_clean_file_exits_zero(self):
        f = make_skill_file(self.test_dir, "clean-exit", "# Clean\n\nNo code.\n")
        result = self._run(f)
        self.assertEqual(result.returncode, 0)

    def test_invalid_yaml_exits_two(self):
        content = "# Skill\n\n```yaml\nkey: :\n  bad:\n```\n"
        f = make_skill_file(self.test_dir, "warn-exit", content)
        result = self._run(f)
        self.assertEqual(result.returncode, 2)

    def test_unclosed_fence_exits_one(self):
        content = "# Skill\n\n```yaml\nname: foo\n"
        f = make_skill_file(self.test_dir, "crit-exit", content)
        result = self._run(f)
        self.assertEqual(result.returncode, 1)

    def test_json_output_flag_produces_parseable_json(self):
        f = make_skill_file(self.test_dir, "json-out", "# Clean\n")
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--json", str(f)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("validator_name", data)
        self.assertIn("issues", data)

    def test_real_skill_files_pass(self):
        """A sample of real SKILL.md files should pass validation."""
        skill_files = list((REPO_ROOT / "git-commit").glob("SKILL.md"))
        if not skill_files:
            self.skipTest("No real skill files found in expected location")
        result = self._run(*skill_files)
        # May exit 0, 2, or 3 — never 1 (CRITICAL)
        self.assertNotEqual(result.returncode, 1,
            msg=f"Real skill file has CRITICAL fence issue:\n{result.stdout}")
