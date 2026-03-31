# tests/marketplace/test_cli_integration.py
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch


def test_cli_install_downloads_skill_with_dependencies():
    """CLI install should fetch skill and dependencies"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Mock registry
        mock_registry = {
            "version": "1.0",
            "skills": [
                {
                    "name": "java-dev",
                    "repository": "https://github.com/mdproctor/claude-skills",
                    "path": "java-dev",
                    "defaultRef": "v1.0.0"
                },
                {
                    "name": "quarkus-flow-dev",
                    "repository": "https://github.com/mdproctor/claude-skills",
                    "path": "quarkus-flow-dev",
                    "defaultRef": "v1.2.0"
                }
            ]
        }

        with patch('scripts.marketplace.cli.fetch_registry', return_value=mock_registry):
            with patch('scripts.marketplace.cli.build_dependency_graph') as mock_graph:
                with patch('scripts.marketplace.cli.install_skill') as mock_install:
                    with patch('scripts.marketplace.cli.validate_skill') as mock_validate:
                        with patch('builtins.input', return_value='Y'):
                            # Mock dependency graph
                            mock_graph.return_value = [
                                {
                                    "name": "java-dev",
                                    "version": "1.0.0",
                                    "repository": "https://github.com/mdproctor/claude-skills",
                                    "dependencies": []
                                },
                                {
                                    "name": "quarkus-flow-dev",
                                    "version": "1.2.0",
                                    "repository": "https://github.com/mdproctor/claude-skills",
                                    "dependencies": [{"name": "java-dev"}]
                                }
                            ]

                            from scripts.marketplace.cli import install_command

                            result = install_command("quarkus-flow-dev", marketplace_dir, snapshot=False)

                            # Verify both skills installed
                            assert mock_install.call_count == 2
                            assert mock_validate.call_count == 2  # Once per skill
                            assert result == 0  # Success exit code


def test_cli_install_respects_user_cancellation():
    """CLI install should return 1 if user cancels"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        mock_registry = {
            "version": "1.0",
            "skills": [
                {
                    "name": "java-dev",
                    "repository": "https://github.com/mdproctor/claude-skills",
                    "path": "java-dev",
                    "defaultRef": "v1.0.0"
                }
            ]
        }

        with patch('scripts.marketplace.cli.fetch_registry', return_value=mock_registry):
            with patch('scripts.marketplace.cli.build_dependency_graph') as mock_graph:
                with patch('scripts.marketplace.cli.install_skill') as mock_install:
                    with patch('builtins.input', return_value='n'):  # User cancels
                        mock_graph.return_value = [
                            {
                                "name": "java-dev",
                                "version": "1.0.0",
                                "repository": "https://github.com/mdproctor/claude-skills",
                                "dependencies": []
                            }
                        ]

                        from scripts.marketplace.cli import install_command

                        result = install_command("java-dev", marketplace_dir, snapshot=False)

                        # Should not install
                        assert mock_install.call_count == 0
                        assert result == 1  # Cancelled exit code


def test_cli_install_handles_errors_gracefully():
    """CLI install should return 1 and print error message on failure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        with patch('scripts.marketplace.cli.fetch_registry', side_effect=RuntimeError("Network error")):
            from scripts.marketplace.cli import install_command

            result = install_command("java-dev", marketplace_dir, snapshot=False)

            assert result == 1  # Error exit code


def test_cli_uninstall_removes_skill():
    """CLI uninstall should remove skill directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Create installed skill
        skill_dir = marketplace_dir / "java-dev"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: java-dev\n---\n")

        from scripts.marketplace.cli import uninstall_command

        with patch('builtins.input', return_value='y'):  # Auto-confirm
            result = uninstall_command("java-dev", marketplace_dir)

        # Verify removed
        assert not skill_dir.exists()
        assert result == 0


def test_cli_uninstall_warns_about_dependents():
    """CLI uninstall should warn if other skills depend on it"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Create java-dev
        java_dev = marketplace_dir / "java-dev"
        java_dev.mkdir()
        (java_dev / "SKILL.md").write_text("---\nname: java-dev\n---\n")
        (java_dev / "skill.json").write_text(json.dumps({
            "name": "java-dev",
            "version": "1.0.0",
            "dependencies": []
        }))

        # Create quarkus-flow-dev that depends on java-dev
        quarkus = marketplace_dir / "quarkus-flow-dev"
        quarkus.mkdir()
        (quarkus / "SKILL.md").write_text("---\nname: quarkus-flow-dev\n---\n")
        (quarkus / "skill.json").write_text(json.dumps({
            "name": "quarkus-flow-dev",
            "version": "1.2.0",
            "dependencies": [{"name": "java-dev"}]
        }))

        from scripts.marketplace.cli import uninstall_command

        # Cancel uninstall
        with patch('builtins.input', return_value='n'):
            result = uninstall_command("java-dev", marketplace_dir)

        # Verify not removed
        assert java_dev.exists()
        assert result == 1  # Cancelled
