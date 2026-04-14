"""
Tests for scripts/validate_all.py

Focuses on:
- VALIDATORS dict structure correctness
- Validator script files exist on disk
- run_validator() exit-code interpretation
- Timeout handling
"""

import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validate_all import VALIDATORS, run_validator

REPO_ROOT = Path(__file__).parent.parent
VALIDATION_DIR = REPO_ROOT / "scripts" / "validation"

# ---------------------------------------------------------------------------
# VALIDATORS dict structure
# ---------------------------------------------------------------------------

REQUIRED_KEYS = {"script", "name", "target"}
KNOWN_TIERS = {"commit", "push", "ci"}


class TestValidatorsStructure:
    def test_all_known_tiers_present(self):
        for tier in KNOWN_TIERS:
            assert tier in VALIDATORS, f"Tier '{tier}' missing from VALIDATORS"

    def test_every_entry_has_required_keys(self):
        for tier, entries in VALIDATORS.items():
            for entry in entries:
                missing = REQUIRED_KEYS - entry.keys()
                assert not missing, (
                    f"Validator '{entry.get('script', '?')}' in tier '{tier}' "
                    f"is missing keys: {missing}"
                )

    def test_script_names_are_strings(self):
        for tier, entries in VALIDATORS.items():
            for entry in entries:
                assert isinstance(entry["script"], str), (
                    f"'script' must be a string in {entry}"
                )

    def test_name_values_are_strings(self):
        for tier, entries in VALIDATORS.items():
            for entry in entries:
                assert isinstance(entry["name"], str), (
                    f"'name' must be a string in {entry}"
                )

    def test_target_is_string_or_none(self):
        for tier, entries in VALIDATORS.items():
            for entry in entries:
                assert entry["target"] is None or isinstance(entry["target"], str), (
                    f"'target' must be str or None in {entry}"
                )

    def test_commit_tier_is_not_empty(self):
        assert len(VALIDATORS["commit"]) > 0

    def test_push_tier_is_not_empty(self):
        assert len(VALIDATORS["push"]) > 0

    def test_ci_tier_is_not_empty(self):
        assert len(VALIDATORS["ci"]) > 0


# ---------------------------------------------------------------------------
# Validator script files exist on disk
# ---------------------------------------------------------------------------

class TestValidatorScriptsExist:
    @pytest.mark.parametrize(
        "script_name",
        [entry["script"] for tier_entries in VALIDATORS.values() for entry in tier_entries],
    )
    def test_script_file_exists(self, script_name):
        script_path = VALIDATION_DIR / script_name
        assert script_path.exists(), (
            f"Validator script not found on disk: {script_path}\n"
            f"Registered in VALIDATORS but file is missing."
        )

    def test_commit_tier_script_references_are_valid(self):
        """All commit-tier scripts must be files that actually exist."""
        for entry in VALIDATORS["commit"]:
            path = VALIDATION_DIR / entry["script"]
            assert path.is_file(), f"Missing commit-tier script: {path}"

    def test_push_tier_script_references_are_valid(self):
        for entry in VALIDATORS["push"]:
            path = VALIDATION_DIR / entry["script"]
            assert path.is_file(), f"Missing push-tier script: {path}"

    def test_ci_tier_script_references_are_valid(self):
        for entry in VALIDATORS["ci"]:
            path = VALIDATION_DIR / entry["script"]
            assert path.is_file(), f"Missing ci-tier script: {path}"


# ---------------------------------------------------------------------------
# run_validator() — exit code interpretation
# ---------------------------------------------------------------------------

class TestRunValidatorExitCodes:
    def _make_validator(self, script="validate_frontmatter.py", name="Test", target=None):
        return {"script": script, "name": name, "target": target}

    def test_exit_code_0_means_passed(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "All good"
        mock_result.stderr = ""

        with patch("scripts.validate_all.subprocess.run", return_value=mock_result):
            result = run_validator(self._make_validator())

        assert result["passed"] is True
        assert result["exit_code"] == 0

    def test_exit_code_1_means_critical_failure(self):
        """exit code 1 = CRITICAL — must set passed=False."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "CRITICAL: bad frontmatter"
        mock_result.stderr = ""

        with patch("scripts.validate_all.subprocess.run", return_value=mock_result):
            result = run_validator(self._make_validator())

        assert result["passed"] is False
        assert result["exit_code"] == 1

    def test_exit_code_2_means_warning_but_still_passed(self):
        """exit code 2 = WARNING — must NOT be treated as a hard failure."""
        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_result.stdout = "WARNING: something to review"
        mock_result.stderr = ""

        with patch("scripts.validate_all.subprocess.run", return_value=mock_result):
            result = run_validator(self._make_validator())

        assert result["passed"] is True
        assert result["exit_code"] == 2

    def test_exit_code_3_means_note_still_passed(self):
        """exit code 3 = NOTE — must NOT block the build."""
        mock_result = MagicMock()
        mock_result.returncode = 3
        mock_result.stdout = "NOTE: minor suggestion"
        mock_result.stderr = ""

        with patch("scripts.validate_all.subprocess.run", return_value=mock_result):
            result = run_validator(self._make_validator())

        assert result["passed"] is True
        assert result["exit_code"] == 3

    def test_result_includes_name(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("scripts.validate_all.subprocess.run", return_value=mock_result):
            result = run_validator(self._make_validator(name="MyValidator"))

        assert result["name"] == "MyValidator"

    def test_result_includes_output(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "stdout content"
        mock_result.stderr = "stderr content"

        with patch("scripts.validate_all.subprocess.run", return_value=mock_result):
            result = run_validator(self._make_validator())

        assert "stdout content" in result["output"]
        assert "stderr content" in result["output"]

    def test_target_appended_to_command_when_not_none(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("scripts.validate_all.subprocess.run", return_value=mock_result) as mock_run:
            run_validator(self._make_validator(target="scripts/"))

        cmd = mock_run.call_args[0][0]
        assert "scripts/" in cmd

    def test_target_not_appended_when_none(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("scripts.validate_all.subprocess.run", return_value=mock_result) as mock_run:
            run_validator(self._make_validator(target=None))

        cmd = mock_run.call_args[0][0]
        # Command should only have 2 elements: python3 + script path
        assert len(cmd) == 2


# ---------------------------------------------------------------------------
# Timeout handling
# ---------------------------------------------------------------------------

class TestTimeoutHandling:
    def test_timeout_expired_produces_failed_result(self):
        with patch(
            "scripts.validate_all.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="python3", timeout=120),
        ):
            result = run_validator({"script": "validate_frontmatter.py", "name": "Slow", "target": None})

        assert result["passed"] is False
        assert result["exit_code"] == -1
        assert "Timeout" in result["output"] or "timeout" in result["output"].lower()

    def test_timeout_result_includes_name(self):
        with patch(
            "scripts.validate_all.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="python3", timeout=120),
        ):
            result = run_validator({"script": "validate_frontmatter.py", "name": "SlowCheck", "target": None})

        assert result["name"] == "SlowCheck"

    def test_unexpected_exception_produces_failed_result(self):
        with patch(
            "scripts.validate_all.subprocess.run",
            side_effect=OSError("binary not found"),
        ):
            result = run_validator({"script": "validate_frontmatter.py", "name": "Broken", "target": None})

        assert result["passed"] is False
        assert result["exit_code"] == -1
        assert "binary not found" in result["output"]
