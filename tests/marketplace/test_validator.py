import pytest
import tempfile
import json
from pathlib import Path


def test_validate_skill_passes_for_valid_skill():
    """Validator should pass for skill with SKILL.md and skill.json"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "java-dev"
        skill_dir.mkdir()

        (skill_dir / "SKILL.md").write_text("""---
name: java-dev
---

# Java Development
""")

        (skill_dir / "skill.json").write_text(json.dumps({
            "name": "java-dev",
            "version": "1.0.0",
            "repository": "https://github.com/test/repo",
            "dependencies": []
        }))

        from scripts.marketplace.validator import validate_skill

        # Should not raise
        validate_skill(skill_dir)


def test_validate_skill_raises_on_missing_skill_md():
    """Validator should raise if SKILL.md missing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "java-dev"
        skill_dir.mkdir()

        from scripts.marketplace.validator import validate_skill

        with pytest.raises(ValueError, match="SKILL.md not found"):
            validate_skill(skill_dir)


def test_validate_skill_raises_on_missing_skill_json():
    """Validator should raise if skill.json missing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "java-dev"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: java-dev\n---\n")

        from scripts.marketplace.validator import validate_skill

        with pytest.raises(ValueError, match="skill.json not found"):
            validate_skill(skill_dir)


def test_validate_skill_raises_on_name_mismatch():
    """Validator should raise if skill.json name doesn't match directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "java-dev"
        skill_dir.mkdir()

        (skill_dir / "SKILL.md").write_text("---\nname: java-dev\n---\n")
        (skill_dir / "skill.json").write_text(json.dumps({
            "name": "wrong-name",
            "version": "1.0.0",
            "repository": "https://github.com/test/repo",
            "dependencies": []
        }))

        from scripts.marketplace.validator import validate_skill

        with pytest.raises(ValueError, match="Name mismatch"):
            validate_skill(skill_dir)
