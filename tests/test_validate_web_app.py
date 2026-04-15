#!/usr/bin/env python3
"""
Tests for scripts/validation/validate_web_app.py

Covers:
- extract_chain_js — parse CHAIN constant from HTML
- extract_skillmd_chains — extract chaining from SKILL.md content
- Missing overview card detection (CRITICAL)
- Missing CHAIN JS entry detection (CRITICAL)
- CHAIN children mismatch (CRITICAL for missing, WARNING for extra)
- CHAIN parents mismatch (CRITICAL for missing, WARNING for extra)
- docs/index.html missing entirely (CRITICAL)
- Integration: real repo passes (exit code 0 or 2, never 1)
- Integration: subprocess exit codes

NOTE ON WORKTREE PATHS:
find_all_skill_files() skips paths containing directories that start with '.'
The worktree lives at .worktrees/test-push-tier which contains '.worktrees'
so subprocess integration tests use cwd=MAIN_REPO_ROOT, not REPO_ROOT.
"""

import json
import subprocess
import sys
from test_base import is_critical, is_warning, is_note
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).parent.parent
MAIN_REPO_ROOT = Path("/Users/mdproctor/claude/cc-praxis")
SCRIPT_PATH = REPO_ROOT / "scripts" / "validation" / "validate_web_app.py"
HTML_PATH = REPO_ROOT / "docs" / "index.html"

sys.path.insert(0, str(SCRIPT_PATH.parent))
from validate_web_app import (
    extract_chain_js,
    extract_skillmd_chains,
    ALL_SKILLS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_minimal_html(skill_name: str, chains_to: list = None, invoked_by: list = None) -> str:
    """Build a minimal HTML string with one overview card and a CHAIN entry."""
    chains_to = chains_to or []
    invoked_by = invoked_by or []

    children_str = ",".join(f"'{s}'" for s in chains_to)
    parents_str = ",".join(f"'{s}'" for s in invoked_by)

    chain_entry = (
        f"  '{skill_name}': {{parents:[{parents_str}],children:[{children_str}]}}"
    )
    return (
        "<html><body>\n"
        f'<div id="ov-{skill_name}">Overview</div>\n'
        "</body></html>\n"
        "<script>\n"
        "const CHAIN = {\n"
        f"{chain_entry}\n"
        "};\n"
        "</script>\n"
    )


def make_skill_file(tmp_path: Path, name: str, content: str) -> Path:
    """Create a SKILL.md in a properly-named skill directory."""
    skill_dir = tmp_path / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    f = skill_dir / "SKILL.md"
    f.write_text(content, encoding="utf-8")
    return f




# ---------------------------------------------------------------------------
# extract_chain_js
# ---------------------------------------------------------------------------

class TestExtractChainJs(unittest.TestCase):

    def test_extracts_single_skill_entry(self):
        html = (
            "const CHAIN = {\n"
            "  'adr': {parents:['git-commit'],children:['java-dev']}\n"
            "};"
        )
        chain = extract_chain_js(html)
        self.assertIn("adr", chain)
        self.assertEqual(chain["adr"]["parents"], ["git-commit"])
        self.assertEqual(chain["adr"]["children"], ["java-dev"])

    def test_extracts_multiple_entries(self):
        html = (
            "const CHAIN = {\n"
            "  'adr': {parents:['git-commit'],children:[]},\n"
            "  'java-dev': {parents:[],children:['adr']}\n"
            "};"
        )
        chain = extract_chain_js(html)
        self.assertIn("adr", chain)
        self.assertIn("java-dev", chain)

    def test_empty_parents_and_children(self):
        html = "const CHAIN = {\n  'solo-skill': {parents:[],children:[]}\n};"
        chain = extract_chain_js(html)
        self.assertEqual(chain["solo-skill"]["parents"], [])
        self.assertEqual(chain["solo-skill"]["children"], [])

    def test_missing_chain_returns_empty_dict(self):
        html = "<html><body>No CHAIN here</body></html>"
        chain = extract_chain_js(html)
        self.assertEqual(chain, {})

    def test_real_html_has_chain_entries(self):
        """The real docs/index.html must have a CHAIN constant."""
        if not HTML_PATH.exists():
            self.skipTest("docs/index.html not found")
        html = HTML_PATH.read_text(encoding="utf-8")
        chain = extract_chain_js(html)
        # Should have substantial entries — 30+ skills
        self.assertGreater(len(chain), 30,
            msg="Real HTML CHAIN has fewer entries than expected — was regeneration skipped?")

    def test_real_html_chain_has_known_skills(self):
        """Known skills must appear in the CHAIN constant."""
        if not HTML_PATH.exists():
            self.skipTest("docs/index.html not found")
        html = HTML_PATH.read_text(encoding="utf-8")
        chain = extract_chain_js(html)
        for skill in ("git-commit", "adr", "java-dev", "update-claude-md"):
            self.assertIn(skill, chain, msg=f"'{skill}' missing from CHAIN in docs/index.html")


# ---------------------------------------------------------------------------
# extract_skillmd_chains
# ---------------------------------------------------------------------------

class TestExtractSkillmdChains(unittest.TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.test_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_chaining_section_returns_empty(self):
        f = make_skill_file(self.test_dir, "git-commit", "# A skill\n\nNo chaining.\n")
        result = extract_skillmd_chains(f)
        self.assertEqual(result["chains_to"], [])
        self.assertEqual(result["invoked_by"], [])

    def test_chains_to_extracted(self):
        # git-commit is a known ALL_SKILLS member
        content = (
            "# A skill\n\n"
            "## Skill Chaining\n\n"
            "**Chains to `git-commit`:** for final commit.\n"
        )
        f = make_skill_file(self.test_dir, "adr", content)
        result = extract_skillmd_chains(f)
        self.assertIn("git-commit", result["chains_to"])

    def test_invoked_by_extracted(self):
        content = (
            "# A skill\n\n"
            "## Skill Chaining\n\n"
            "**Triggered by `java-dev`:** when review requested.\n"
        )
        f = make_skill_file(self.test_dir, "java-code-review", content)
        result = extract_skillmd_chains(f)
        self.assertIn("java-dev", result["invoked_by"])

    def test_unknown_skills_filtered_out(self):
        # A reference to a non-existent skill should not appear in result
        content = (
            "## Skill Chaining\n\n"
            "Chains to `nonexistent-skill`: not real.\n"
        )
        f = make_skill_file(self.test_dir, "git-commit", content)
        result = extract_skillmd_chains(f)
        self.assertNotIn("nonexistent-skill", result["chains_to"])

    def test_known_non_skill_terms_filtered_out(self):
        # docs-sync and similar non-skill terms should not appear
        content = (
            "## Skill Chaining\n\n"
            "Chains to `docs-sync`: internal term.\n"
        )
        f = make_skill_file(self.test_dir, "git-commit", content)
        result = extract_skillmd_chains(f)
        self.assertNotIn("docs-sync", result["chains_to"])

    def test_unreadable_file_returns_empty(self):
        # Pass a path that doesn't exist
        missing = self.test_dir / "ghost-skill" / "SKILL.md"
        result = extract_skillmd_chains(missing)
        self.assertEqual(result["chains_to"], [])
        self.assertEqual(result["invoked_by"], [])


# ---------------------------------------------------------------------------
# Integration: main() logic via constructed inputs
# ---------------------------------------------------------------------------

class TestWebAppValidatorLogic(unittest.TestCase):
    """
    Tests using a minimal HTML fixture and a temp skill directory.
    We import and call main() indirectly by constructing the inputs
    that main() would use, then calling the relevant checks directly.
    """

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.test_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_overview_card_present_passes_card_check(self):
        html = make_minimal_html("git-commit")
        self.assertIn('id="ov-git-commit"', html)

    def test_overview_card_missing_is_detectable(self):
        html = make_minimal_html("adr")
        # If we check for a skill NOT in the HTML, it should be missing
        self.assertNotIn('id="ov-java-dev"', html)

    def test_chain_entry_present_passes_chain_check(self):
        html = make_minimal_html("git-commit", chains_to=["adr"], invoked_by=[])
        chain = extract_chain_js(html)
        self.assertIn("git-commit", chain)
        self.assertIn("adr", chain["git-commit"]["children"])

    def test_chain_children_match_detected(self):
        html = make_minimal_html("git-commit", chains_to=["adr"])
        chain = extract_chain_js(html)
        js_children = set(chain["git-commit"]["children"])
        md_children = {"adr"}
        missing = md_children - js_children
        self.assertEqual(missing, set())

    def test_chain_children_missing_detectable(self):
        # HTML has git-commit with no children, but SKILL.md says chains_to adr
        html = make_minimal_html("git-commit", chains_to=[])
        chain = extract_chain_js(html)
        js_children = set(chain["git-commit"]["children"])
        md_children = {"adr"}
        missing = md_children - js_children
        self.assertIn("adr", missing)

    def test_chain_children_extra_detectable(self):
        # HTML has extra child not in SKILL.md
        html = make_minimal_html("git-commit", chains_to=["java-dev"])
        chain = extract_chain_js(html)
        js_children = set(chain["git-commit"]["children"])
        md_children: set = set()
        extra = js_children - md_children
        self.assertIn("java-dev", extra)

    def test_all_skills_set_nonempty(self):
        self.assertGreater(len(ALL_SKILLS), 30)

    def test_all_skills_contains_known_skills(self):
        for skill in ("git-commit", "adr", "java-dev", "project-health"):
            self.assertIn(skill, ALL_SKILLS)


# ---------------------------------------------------------------------------
# Integration: subprocess exit codes
# ---------------------------------------------------------------------------

class TestSubprocessExitCodes(unittest.TestCase):

    def _run(self, cwd=None, extra_args=None) -> subprocess.CompletedProcess:
        args = [sys.executable, str(SCRIPT_PATH)] + (extra_args or [])
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=str(cwd or MAIN_REPO_ROOT),
        )

    def test_real_repo_no_critical_issues(self):
        """Real repo must not have CRITICAL web app drift (blocks push)."""
        if not MAIN_REPO_ROOT.exists():
            self.skipTest("Main repo root not found")
        result = self._run()
        self.assertNotEqual(result.returncode, 1,
            msg=f"CRITICAL drift detected in real repo:\n{result.stdout}\n{result.stderr}")

    def test_real_repo_exits_cleanly_or_with_warnings(self):
        """Real repo may have warnings (exit 2) but must not be CRITICAL (exit 1)."""
        if not MAIN_REPO_ROOT.exists():
            self.skipTest("Main repo root not found")
        result = self._run()
        self.assertIn(result.returncode, [0, 2, 3],
            msg=f"Unexpected exit code {result.returncode}:\n{result.stdout}")

    def test_json_output_is_parseable(self):
        if not MAIN_REPO_ROOT.exists():
            self.skipTest("Main repo root not found")
        result = self._run(extra_args=["--json"])
        data = json.loads(result.stdout)
        self.assertIn("validator_name", data)
        self.assertIn("issues", data)
        self.assertIn("files_checked", data)

    def test_json_output_files_checked_nonzero(self):
        if not MAIN_REPO_ROOT.exists():
            self.skipTest("Main repo root not found")
        result = self._run(extra_args=["--json"])
        data = json.loads(result.stdout)
        self.assertGreater(data["files_checked"], 0,
            msg="Validator checked 0 files — skill file discovery likely broken")

    def test_missing_html_exits_one(self):
        """If docs/index.html does not exist, validator must exit 1 (CRITICAL)."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Create a minimal CLAUDE.md so find_skills_root() anchors here
            (tmp_path / "CLAUDE.md").write_text("# Test\n")
            # No docs/index.html
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=str(tmp_path),
            )
            self.assertEqual(result.returncode, 1,
                msg="Missing index.html should produce CRITICAL exit code 1")


# ---------------------------------------------------------------------------
# Real HTML structure assertions
# ---------------------------------------------------------------------------

class TestRealHtmlStructure(unittest.TestCase):
    """Assertions about docs/index.html that should hold after regeneration."""

    def setUp(self):
        if not HTML_PATH.exists():
            self.skipTest("docs/index.html not found")
        self.html = HTML_PATH.read_text(encoding="utf-8")

    def test_html_has_chain_constant(self):
        self.assertIn("const CHAIN = {", self.html)

    def test_html_has_overview_cards_for_known_skills(self):
        for skill in ("git-commit", "adr", "java-dev", "project-health"):
            self.assertIn(f'id="ov-{skill}"', self.html,
                msg=f"Missing overview card for '{skill}' — regenerate web app data")

    def test_html_overview_card_count_matches_all_skills_scale(self):
        import re
        cards = re.findall(r'id="ov-[^"]+"', self.html)
        self.assertGreater(len(cards), 30,
            msg=f"Only {len(cards)} overview cards found — expected 30+")

    def test_chain_count_matches_overview_card_count(self):
        import re
        cards = re.findall(r'id="ov-([^"]+)"', self.html)
        chain = extract_chain_js(self.html)
        # Every skill with an overview card should also be in CHAIN
        for skill_name in cards:
            if skill_name in ALL_SKILLS:
                self.assertIn(skill_name, chain,
                    msg=f"'{skill_name}' has overview card but no CHAIN entry")

    def test_no_skill_in_chain_without_overview_card(self):
        chain = extract_chain_js(self.html)
        for skill_name in chain:
            if skill_name in ALL_SKILLS:
                self.assertIn(f'id="ov-{skill_name}"', self.html,
                    msg=f"'{skill_name}' in CHAIN but has no overview card")
