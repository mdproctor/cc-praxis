#!/usr/bin/env python3
"""
Unit tests for generate_skill_metadata.py - Skill Scanner

Tests skill directory scanning (Task 1 of marketplace implementation).
"""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestSkillScanner(unittest.TestCase):
    """Test skill directory scanning"""

    def test_scan_finds_skill_directories(self):
        """Scanner should find directories containing SKILL.md files"""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test skill directories
            (tmpdir / "java-dev").mkdir()
            (tmpdir / "java-dev" / "SKILL.md").write_text("---\nname: java-dev\n---\n")

            (tmpdir / "quarkus-flow-dev").mkdir()
            (tmpdir / "quarkus-flow-dev" / "SKILL.md").write_text("---\nname: quarkus-flow-dev\n---\n")

            # Create non-skill directory (should be excluded)
            (tmpdir / "scripts").mkdir()
            (tmpdir / "scripts" / "test.py").write_text("# not a skill")

            from scripts.generate_skill_metadata import scan_for_skills

            skills = scan_for_skills(tmpdir)

            self.assertEqual(len(skills), 2)
            self.assertIn(tmpdir / "java-dev", skills)
            self.assertIn(tmpdir / "quarkus-flow-dev", skills)
            self.assertNotIn(tmpdir / "scripts", skills)


class TestFrontmatterParser(unittest.TestCase):
    """Test SKILL.md frontmatter parsing"""

    def test_parse_frontmatter_extracts_name(self):
        """Parser should extract name from SKILL.md frontmatter"""
        skill_md = """---
name: java-dev
description: >
  Use when writing Java code
---

# Java Development

Content here...
"""
        from scripts.generate_skill_metadata import parse_frontmatter

        name = parse_frontmatter(skill_md)

        self.assertEqual(name, "java-dev")

    def test_parse_frontmatter_raises_on_missing_name(self):
        """Parser should raise error if name field missing"""
        skill_md = """---
description: No name field
---
"""
        from scripts.generate_skill_metadata import parse_frontmatter

        with self.assertRaisesRegex(ValueError, "Missing 'name' field"):
            parse_frontmatter(skill_md)


class TestDependencyParser(unittest.TestCase):
    """Test SKILL.md dependency parsing"""

    def test_parse_dependencies_finds_single_dependency(self):
        """Parser should extract dependencies from Prerequisites section"""
        skill_md = """---
name: quarkus-flow-dev
---

## Prerequisites

**This skill builds on [`java-dev`]**.

Apply all rules from java-dev.
"""
        from scripts.generate_skill_metadata import parse_dependencies

        deps = parse_dependencies(skill_md)

        self.assertEqual(deps, ["java-dev"])

    def test_parse_dependencies_finds_multiple_dependencies(self):
        """Parser should extract multiple dependencies"""
        skill_md = """---
name: quarkus-flow-testing
---

## Prerequisites

**This skill builds on [`java-dev`] and [`quarkus-flow-dev`]**.
"""
        from scripts.generate_skill_metadata import parse_dependencies

        deps = parse_dependencies(skill_md)

        self.assertEqual(set(deps), {"java-dev", "quarkus-flow-dev"})

    def test_parse_dependencies_returns_empty_for_no_prereqs(self):
        """Parser should return empty list if no Prerequisites section"""
        skill_md = """---
name: java-dev
---

# Java Development

No prerequisites.
"""
        from scripts.generate_skill_metadata import parse_dependencies

        deps = parse_dependencies(skill_md)

        self.assertEqual(deps, [])


class TestSkillJsonGenerator(unittest.TestCase):
    """Test skill.json metadata generation"""

    def test_generate_skill_json_creates_metadata(self):
        """Generator should create valid skill.json file"""
        import json
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create skill directory with SKILL.md
            skill_dir = tmpdir / "java-dev"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: java-dev
---

# Java Development
""")

            from scripts.generate_skill_metadata import generate_skill_json

            generate_skill_json(
                skill_dir=skill_dir,
                repository_url="https://github.com/mdproctor/claude-skills",
                version="1.0.0",
                dependencies=[]
            )

            # Verify skill.json created
            skill_json_path = skill_dir / "skill.json"
            self.assertTrue(skill_json_path.exists())

            # Verify content
            with open(skill_json_path) as f:
                data = json.load(f)

            self.assertEqual(data, {
                "name": "java-dev",
                "version": "1.0.0",
                "repository": "https://github.com/mdproctor/claude-skills",
                "dependencies": []
            })

    def test_generate_skill_json_includes_dependencies(self):
        """Generator should include dependency references"""
        import json
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            skill_dir = tmpdir / "quarkus-flow-dev"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: quarkus-flow-dev
---

## Prerequisites

**This skill builds on [`java-dev`]**.
""")

            from scripts.generate_skill_metadata import generate_skill_json

            generate_skill_json(
                skill_dir=skill_dir,
                repository_url="https://github.com/mdproctor/claude-skills",
                version="1.2.0",
                dependencies=[
                    {
                        "name": "java-dev",
                        "repository": "https://github.com/mdproctor/claude-skills",
                        "ref": "v1.0.0"
                    }
                ]
            )

            skill_json_path = skill_dir / "skill.json"
            with open(skill_json_path) as f:
                data = json.load(f)

            self.assertEqual(data["dependencies"], [
                {
                    "name": "java-dev",
                    "repository": "https://github.com/mdproctor/claude-skills",
                    "ref": "v1.0.0"
                }
            ])

    def test_generate_skill_json_raises_on_missing_skill_md(self):
        """Generator should raise FileNotFoundError if SKILL.md doesn't exist"""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create skill directory WITHOUT SKILL.md
            skill_dir = tmpdir / "java-dev"
            skill_dir.mkdir()

            from scripts.generate_skill_metadata import generate_skill_json

            with self.assertRaisesRegex(FileNotFoundError, "SKILL.md not found"):
                generate_skill_json(
                    skill_dir=skill_dir,
                    repository_url="https://github.com/mdproctor/claude-skills",
                    version="1.0.0",
                    dependencies=[]
                )

    def test_generate_skill_json_raises_on_malformed_frontmatter(self):
        """Generator should raise ValueError if frontmatter is invalid"""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            skill_dir = tmpdir / "java-dev"
            skill_dir.mkdir()
            # SKILL.md with missing name field
            (skill_dir / "SKILL.md").write_text("""---
description: No name field
---

# Java Development
""")

            from scripts.generate_skill_metadata import generate_skill_json

            with self.assertRaisesRegex(ValueError, "Missing 'name' field"):
                generate_skill_json(
                    skill_dir=skill_dir,
                    repository_url="https://github.com/mdproctor/claude-skills",
                    version="1.0.0",
                    dependencies=[]
                )

    def test_generate_skill_json_raises_on_nonexistent_dir(self):
        """Generator should raise ValueError if skill_dir doesn't exist"""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Reference non-existent directory
            skill_dir = tmpdir / "does-not-exist"

            from scripts.generate_skill_metadata import generate_skill_json

            with self.assertRaisesRegex(ValueError, "does not exist"):
                generate_skill_json(
                    skill_dir=skill_dir,
                    repository_url="https://github.com/mdproctor/claude-skills",
                    version="1.0.0",
                    dependencies=[]
                )

    def test_generate_skill_json_raises_on_file_instead_of_dir(self):
        """Generator should raise ValueError if skill_dir is a file"""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create a FILE instead of directory
            skill_file = tmpdir / "not-a-dir"
            skill_file.write_text("I'm a file")

            from scripts.generate_skill_metadata import generate_skill_json

            with self.assertRaisesRegex(ValueError, "Not a directory"):
                generate_skill_json(
                    skill_dir=skill_file,
                    repository_url="https://github.com/mdproctor/claude-skills",
                    version="1.0.0",
                    dependencies=[]
                )

    def test_generate_skill_json_raises_on_permission_error(self):
        """Generator should raise IOError if SKILL.md cannot be read"""
        import os
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            skill_dir = tmpdir / "test-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("---\nname: test\n---")

            # Remove read permissions
            os.chmod(skill_md, 0o000)

            from scripts.generate_skill_metadata import generate_skill_json

            try:
                with self.assertRaisesRegex(IOError, "Failed to read"):
                    generate_skill_json(
                        skill_dir=skill_dir,
                        repository_url="https://github.com/mdproctor/claude-skills",
                        version="1.0.0",
                        dependencies=[]
                    )
            finally:
                # Restore permissions for cleanup
                os.chmod(skill_md, 0o644)


class TestMainCLI(unittest.TestCase):
    """Test main CLI function"""

    def test_main_generates_metadata_for_all_skills(self):
        """Main function should generate skill.json for all discovered skills"""
        import json
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create multiple skills
            for skill_name in ["java-dev", "quarkus-flow-dev"]:
                skill_dir = tmpdir / skill_name
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"""---
name: {skill_name}
---

# Skill
""")

            from scripts.generate_skill_metadata import main

            # Run main with test directory
            result = main(
                root_dir=tmpdir,
                repository_url="https://github.com/test/repo",
                version="1.0.0"
            )

            # Verify skill.json created for each
            assert (tmpdir / "java-dev" / "skill.json").exists()
            assert (tmpdir / "quarkus-flow-dev" / "skill.json").exists()

            # Verify return value
            assert result == 2  # Number of skills processed

            # Verify content of generated files
            with open(tmpdir / "java-dev" / "skill.json") as f:
                data = json.load(f)
            assert data["name"] == "java-dev"
            assert data["version"] == "1.0.0"
            assert data["repository"] == "https://github.com/test/repo"


if __name__ == '__main__':
    unittest.main()
