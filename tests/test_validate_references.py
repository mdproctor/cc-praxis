"""
Tests for scripts/validation/validate_references.py

Uses temporary skill directories — does not rely on the real skills directory.
"""

import sys
import pytest
from pathlib import Path

# Allow imports from the repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

# validate_references inserts scripts/ onto sys.path itself, so Severity comes
# from utils.common (without the "scripts." prefix).  We match that here to
# avoid a two-module-identity split that would cause severity comparisons to fail.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scripts.validation.validate_references import (
    validate_skill_references,
    extract_structured_references,
    KNOWN_NON_SKILLS,
)
from utils.common import Severity  # same module identity as used inside validate_references


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_skill(tmp_path: Path, name: str, content: str) -> Path:
    """Create a minimal skill directory and return the SKILL.md path."""
    skill_dir = tmp_path / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")
    return skill_file


def make_index(*skill_paths: Path) -> dict:
    """Build a skill_index dict from a list of SKILL.md paths."""
    return {p.parent.name: p for p in skill_paths}


# ---------------------------------------------------------------------------
# extract_structured_references
# ---------------------------------------------------------------------------

class TestExtractStructuredReferences:
    def test_empty_content_returns_empty_set(self):
        assert extract_structured_references("") == set()

    def test_reference_in_skill_chaining_section_is_captured(self):
        content = (
            "## Skill Chaining\n\n"
            "**Chains to `java-dev`:** after the build passes.\n"
        )
        refs = extract_structured_references(content)
        assert "java-dev" in refs

    def test_reference_in_prerequisites_section_is_captured(self):
        content = (
            "## Prerequisites\n\n"
            "**This skill builds on `code-review-principles`.**\n"
        )
        refs = extract_structured_references(content)
        assert "code-review-principles" in refs

    def test_reference_outside_structured_sections_is_ignored(self):
        content = (
            "## Overview\n\n"
            "This works with `java-dev` in various ways.\n\n"
            "## Usage\n\n"
            "Call `git-commit` after finishing.\n"
        )
        refs = extract_structured_references(content)
        assert refs == set()

    def test_non_skill_backtick_terms_not_flagged(self):
        """File names, shell commands, and short tokens must not be returned."""
        content = (
            "## Skill Chaining\n\n"
            "See `README.md`, run `git commit`, check `pom.xml`.\n"
        )
        refs = extract_structured_references(content)
        # These have file extensions or are single-segment — should all be excluded
        assert "README.md" not in refs
        assert "pom.xml" not in refs

    def test_known_non_skills_excluded(self):
        """Terms in KNOWN_NON_SKILLS must never appear in the result."""
        for term in KNOWN_NON_SKILLS:
            content = f"## Skill Chaining\n\n**Chains to `{term}`.**\n"
            refs = extract_structured_references(content)
            assert term not in refs, f"KNOWN_NON_SKILLS term '{term}' should be excluded"

    def test_multiple_references_in_one_section_all_captured(self):
        content = (
            "## Skill Chaining\n\n"
            "Chains to `java-dev` and `java-code-review` for review.\n"
        )
        refs = extract_structured_references(content)
        assert "java-dev" in refs
        assert "java-code-review" in refs


# ---------------------------------------------------------------------------
# validate_skill_references — valid skill
# ---------------------------------------------------------------------------

class TestValidateSkillReferencesValid:
    def test_valid_skill_with_no_cross_refs_passes(self, tmp_path):
        content = (
            "---\nname: my-skill\ndescription: >\n  Use when testing.\n---\n\n"
            "## Overview\n\nThis skill does something.\n"
        )
        skill_path = make_skill(tmp_path, "my-skill", content)
        skill_index = make_index(skill_path)
        issues = validate_skill_references(skill_path, skill_index)
        assert issues == []

    def test_valid_reference_to_existing_skill_passes(self, tmp_path):
        target_content = (
            "---\nname: target-skill\ndescription: >\n  Use when target.\n---\n\n"
            "## Skill Chaining\n\n**Triggered by `source-skill`:** for processing.\n"
        )
        source_content = (
            "---\nname: source-skill\ndescription: >\n  Use when source.\n---\n\n"
            "## Skill Chaining\n\n**Chains to `target-skill`:** after init.\n"
        )
        target_path = make_skill(tmp_path, "target-skill", target_content)
        source_path = make_skill(tmp_path, "source-skill", source_content)
        skill_index = make_index(source_path, target_path)

        issues = validate_skill_references(source_path, skill_index)
        # No CRITICAL issues — reference exists
        critical = [i for i in issues if i.severity == Severity.CRITICAL]
        assert critical == []


# ---------------------------------------------------------------------------
# validate_skill_references — missing reference (CRITICAL)
# ---------------------------------------------------------------------------

class TestMissingSkillReference:
    def test_reference_to_nonexistent_skill_is_critical(self, tmp_path):
        content = (
            "---\nname: my-skill\ndescription: >\n  Use when testing.\n---\n\n"
            "## Prerequisites\n\n"
            "**This skill builds on `ghost-skill`.**\n"
        )
        skill_path = make_skill(tmp_path, "my-skill", content)
        # ghost-skill is NOT in the index
        skill_index = make_index(skill_path)

        issues = validate_skill_references(skill_path, skill_index)
        critical = [i for i in issues if i.severity == Severity.CRITICAL]
        assert len(critical) >= 1
        assert any("ghost-skill" in i.message for i in critical)

    def test_multiple_missing_references_all_reported(self, tmp_path):
        content = (
            "---\nname: my-skill\ndescription: >\n  Use when testing.\n---\n\n"
            "## Prerequisites\n\n"
            "Builds on `alpha-beta` and `gamma-delta`.\n"
        )
        skill_path = make_skill(tmp_path, "my-skill", content)
        skill_index = make_index(skill_path)

        issues = validate_skill_references(skill_path, skill_index)
        critical = [i for i in issues if i.severity == Severity.CRITICAL]
        missing = {i.message for i in critical}
        assert any("alpha-beta" in m for m in missing)
        assert any("gamma-delta" in m for m in missing)

    def test_exit_code_is_1_for_missing_reference(self, tmp_path):
        """ValidationResult.exit_code must be 1 when CRITICAL issues exist."""
        from utils.common import ValidationResult  # noqa: match module identity, ValidationIssue
        content = (
            "---\nname: my-skill\ndescription: >\n  Use when testing.\n---\n\n"
            "## Prerequisites\n\n"
            "Builds on `no-such-skill`.\n"
        )
        skill_path = make_skill(tmp_path, "my-skill", content)
        skill_index = make_index(skill_path)

        issues = validate_skill_references(skill_path, skill_index)
        result = ValidationResult(validator_name="test", issues=issues)
        assert result.exit_code == 1


# ---------------------------------------------------------------------------
# validate_skill_references — bidirectional inconsistency (WARNING)
# ---------------------------------------------------------------------------

class TestBidirectionalInconsistency:
    def test_chains_to_without_backref_is_warning(self, tmp_path):
        """A → B but B does not mention A should produce a WARNING."""
        target_content = (
            "---\nname: b-skill\ndescription: >\n  Use when b.\n---\n\n"
            "## Overview\n\nDoes B things. No mention of a-skill here.\n"
        )
        source_content = (
            "---\nname: a-skill\ndescription: >\n  Use when a.\n---\n\n"
            "## Skill Chaining\n\n**Chains to `b-skill`:** for processing.\n"
        )
        target_path = make_skill(tmp_path, "b-skill", target_content)
        source_path = make_skill(tmp_path, "a-skill", source_content)
        skill_index = make_index(source_path, target_path)

        issues = validate_skill_references(source_path, skill_index)
        warnings = [i for i in issues if i.severity == Severity.WARNING]
        assert len(warnings) >= 1
        assert any("b-skill" in i.message for i in warnings)

    def test_bidirectional_refs_produce_no_warnings(self, tmp_path):
        """A → B and B mentions A back — no WARNING expected."""
        target_content = (
            "---\nname: b-skill\ndescription: >\n  Use when b.\n---\n\n"
            "## Skill Chaining\n\n**Triggered by `a-skill`:** for kickoff.\n"
        )
        source_content = (
            "---\nname: a-skill\ndescription: >\n  Use when a.\n---\n\n"
            "## Skill Chaining\n\n**Chains to `b-skill`:** for processing.\n"
        )
        target_path = make_skill(tmp_path, "b-skill", target_content)
        source_path = make_skill(tmp_path, "a-skill", source_content)
        skill_index = make_index(source_path, target_path)

        issues = validate_skill_references(source_path, skill_index)
        warnings = [i for i in issues if i.severity == Severity.WARNING]
        # No bidirectional warning — b-skill mentions a-skill
        assert all("b-skill" not in i.message or "doesn't mention" not in i.message
                   for i in warnings)


# ---------------------------------------------------------------------------
# validate_skill_references — issue counts via ValidationResult
# ---------------------------------------------------------------------------

class TestIssueCountsViaValidationResult:
    def test_clean_skill_has_zero_critical_zero_warning(self, tmp_path):
        from scripts.utils.common import ValidationResult
        content = (
            "---\nname: clean-skill\ndescription: >\n  Use when clean.\n---\n\n"
            "## Overview\n\nNo references to validate.\n"
        )
        skill_path = make_skill(tmp_path, "clean-skill", content)
        skill_index = make_index(skill_path)

        issues = validate_skill_references(skill_path, skill_index)
        result = ValidationResult(validator_name="test", issues=issues)
        assert result.critical_count == 0
        assert result.warning_count == 0
        assert result.passed is True

    def test_missing_ref_increments_critical_count(self, tmp_path):
        from utils.common import ValidationResult  # noqa: match module identity
        content = (
            "---\nname: broken-skill\ndescription: >\n  Use when broken.\n---\n\n"
            "## Prerequisites\n\n"
            "Builds on `missing-skill`.\n"
        )
        skill_path = make_skill(tmp_path, "broken-skill", content)
        skill_index = make_index(skill_path)

        issues = validate_skill_references(skill_path, skill_index)
        result = ValidationResult(validator_name="test", issues=issues)
        assert result.critical_count >= 1
        assert result.passed is False
