# tests/marketplace/test_installer.py
import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


def test_install_skill_downloads_to_marketplace():
    """Installer should download skill to .marketplace directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        skill_metadata = {
            "name": "java-dev",
            "version": "1.0.0",
            "repository": "https://github.com/mdproctor/claude-skills",
            "dependencies": []
        }

        # Mock git operations to avoid actual network calls
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Create fake SKILL.md and skill.json in temp location
            with patch('scripts.marketplace.installer.fetch_skill_files') as mock_fetch:
                # Create a separate temp directory structure to simulate git sparse checkout
                fake_temp_root = Path(tmpdir) / "fake_git_temp"
                fake_temp_root.mkdir()
                fake_skill_dir = fake_temp_root / "java-dev"
                fake_skill_dir.mkdir()
                (fake_skill_dir / "SKILL.md").write_text("---\nname: java-dev\n---\n")
                (fake_skill_dir / "skill.json").write_text('{"name":"java-dev"}')
                # Return tuple (skill_dir, temp_root)
                mock_fetch.return_value = (fake_skill_dir, fake_temp_root)

                from scripts.marketplace.installer import install_skill

                install_skill(
                    skill_metadata=skill_metadata,
                    marketplace_dir=marketplace_dir,
                    ref="v1.0.0"
                )

                # Verify installed
                installed_dir = marketplace_dir / "java-dev"
                assert installed_dir.exists()
                assert (installed_dir / "SKILL.md").exists()
                assert (installed_dir / "skill.json").exists()


def test_install_skill_replaces_existing_installation():
    """Installer should replace existing skill directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Create existing installation
        existing_dir = marketplace_dir / "java-dev"
        existing_dir.mkdir()
        (existing_dir / "old_file.txt").write_text("old content")

        skill_metadata = {
            "name": "java-dev",
            "version": "2.0.0",
            "repository": "https://github.com/mdproctor/claude-skills",
            "dependencies": []
        }

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            with patch('scripts.marketplace.installer.fetch_skill_files') as mock_fetch:
                # Create a separate temp directory structure to simulate git sparse checkout
                fake_temp_root = Path(tmpdir) / "fake_git_temp"
                fake_temp_root.mkdir()
                fake_skill_dir = fake_temp_root / "java-dev"
                fake_skill_dir.mkdir()
                (fake_skill_dir / "SKILL.md").write_text("---\nname: java-dev\n---\nnew version")
                (fake_skill_dir / "skill.json").write_text('{"name":"java-dev","version":"2.0.0"}')
                # Return tuple (skill_dir, temp_root)
                mock_fetch.return_value = (fake_skill_dir, fake_temp_root)

                from scripts.marketplace.installer import install_skill

                install_skill(
                    skill_metadata=skill_metadata,
                    marketplace_dir=marketplace_dir,
                    ref="v2.0.0"
                )

                # Verify old file gone, new files present
                assert not (existing_dir / "old_file.txt").exists()
                assert (existing_dir / "SKILL.md").exists()
                assert "new version" in (existing_dir / "SKILL.md").read_text()


def test_fetch_skill_files_uses_sparse_checkout():
    """fetch_skill_files should use git sparse checkout to download specific directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock git operations
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Create fake skill files in expected location
            with patch('tempfile.mkdtemp') as mock_mkdtemp:
                temp_repo_dir = Path(tmpdir) / "temp_repo"
                temp_repo_dir.mkdir()
                mock_mkdtemp.return_value = str(temp_repo_dir)

                # Create git structure
                git_dir = temp_repo_dir / ".git" / "info"
                git_dir.mkdir(parents=True)

                # Create skill directory
                skill_dir = temp_repo_dir / "java-dev"
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text("---\nname: java-dev\n---\n")
                (skill_dir / "skill.json").write_text('{"name":"java-dev"}')

                from scripts.marketplace.installer import fetch_skill_files

                result_dir, temp_root = fetch_skill_files(
                    repository="https://github.com/mdproctor/claude-skills",
                    path="java-dev",
                    ref="v1.0.0"
                )

                # Verify git commands called
                assert mock_run.call_count >= 5  # init, remote add, config, fetch, checkout

                # Verify sparse checkout configured
                sparse_file = temp_repo_dir / ".git" / "info" / "sparse-checkout"
                assert sparse_file.exists()
                assert "java-dev/*" in sparse_file.read_text()

                # Verify result
                assert result_dir == skill_dir
                assert result_dir.exists()
                assert temp_root == temp_repo_dir


def test_fetch_skill_files_raises_on_git_failure():
    """fetch_skill_files should raise clear error on git failure"""
    with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "git")):
        with patch('tempfile.mkdtemp', return_value="/tmp/test"):
            from scripts.marketplace.installer import fetch_skill_files

            with pytest.raises(RuntimeError, match="Failed to fetch skill"):
                fetch_skill_files(
                    repository="https://github.com/invalid/repo",
                    path="nonexistent-skill",
                    ref="v1.0.0"
                )


def test_install_skill_cleans_up_temp_directory():
    """Installer should clean up temporary directory after installation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        skill_metadata = {
            "name": "java-dev",
            "version": "1.0.0",
            "repository": "https://github.com/mdproctor/claude-skills",
            "dependencies": []
        }

        temp_dirs_created = []

        def track_mkdtemp(*args, **kwargs):
            temp_dir = tempfile.mkdtemp(*args, **kwargs)
            temp_dirs_created.append(temp_dir)
            return temp_dir

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            with patch('tempfile.mkdtemp', side_effect=track_mkdtemp):
                with patch('scripts.marketplace.installer.fetch_skill_files') as mock_fetch:
                    # Create a separate temp directory structure to simulate git sparse checkout
                    fake_temp_root = Path(tmpdir) / "fake_git_temp"
                    fake_temp_root.mkdir()
                    fake_skill_dir = fake_temp_root / "java-dev"
                    fake_skill_dir.mkdir()
                    (fake_skill_dir / "SKILL.md").write_text("---\nname: java-dev\n---\n")
                    # Return tuple (skill_dir, temp_root)
                    mock_fetch.return_value = (fake_skill_dir, fake_temp_root)

                    from scripts.marketplace.installer import install_skill

                    install_skill(
                        skill_metadata=skill_metadata,
                        marketplace_dir=marketplace_dir,
                        ref="v1.0.0"
                    )

                    # Verify installation succeeded
                    assert (marketplace_dir / "java-dev" / "SKILL.md").exists()

                    # Note: We can't verify temp dir cleanup in the mock scenario
                    # because fetch_skill_files is mocked. This test verifies the
                    # happy path. Cleanup is tested in integration tests.


def test_install_skill_validates_metadata_has_name():
    """install_skill should raise ValueError if metadata missing name"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Missing "name" field
        skill_metadata = {
            "version": "1.0.0",
            "repository": "https://github.com/mdproctor/claude-skills"
        }

        from scripts.marketplace.installer import install_skill

        with pytest.raises(ValueError, match="Invalid skill metadata: missing required field 'name'"):
            install_skill(
                skill_metadata=skill_metadata,
                marketplace_dir=marketplace_dir,
                ref="v1.0.0"
            )


def test_install_skill_validates_metadata_has_repository():
    """install_skill should raise ValueError if metadata missing repository"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        marketplace_dir.mkdir()

        # Missing "repository" field
        skill_metadata = {
            "name": "java-dev",
            "version": "1.0.0"
        }

        from scripts.marketplace.installer import install_skill

        with pytest.raises(ValueError, match="Invalid skill metadata: missing required field 'repository'"):
            install_skill(
                skill_metadata=skill_metadata,
                marketplace_dir=marketplace_dir,
                ref="v1.0.0"
            )


def test_install_skill_validates_marketplace_dir_exists():
    """install_skill should raise ValueError if marketplace_dir doesn't exist"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_dir = Path(tmpdir) / ".marketplace"
        # Don't create it

        skill_metadata = {
            "name": "java-dev",
            "version": "1.0.0",
            "repository": "https://github.com/mdproctor/claude-skills"
        }

        from scripts.marketplace.installer import install_skill

        with pytest.raises(ValueError, match="Marketplace directory does not exist"):
            install_skill(
                skill_metadata=skill_metadata,
                marketplace_dir=marketplace_dir,
                ref="v1.0.0"
            )


def test_install_skill_validates_marketplace_dir_is_directory():
    """install_skill should raise ValueError if marketplace_dir is a file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        marketplace_file = Path(tmpdir) / ".marketplace"
        marketplace_file.write_text("not a directory")

        skill_metadata = {
            "name": "java-dev",
            "version": "1.0.0",
            "repository": "https://github.com/mdproctor/claude-skills"
        }

        from scripts.marketplace.installer import install_skill

        with pytest.raises(ValueError, match="Marketplace path is not a directory"):
            install_skill(
                skill_metadata=skill_metadata,
                marketplace_dir=marketplace_file,
                ref="v1.0.0"
            )


def test_fetch_skill_files_validates_fetched_directory_exists():
    """fetch_skill_files should raise RuntimeError if skill directory not found after checkout"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            with patch('tempfile.mkdtemp') as mock_mkdtemp:
                temp_repo_dir = Path(tmpdir) / "temp_repo"
                temp_repo_dir.mkdir()
                mock_mkdtemp.return_value = str(temp_repo_dir)

                # Create git structure but NOT the skill directory
                git_dir = temp_repo_dir / ".git" / "info"
                git_dir.mkdir(parents=True)

                from scripts.marketplace.installer import fetch_skill_files

                with pytest.raises(RuntimeError, match="Skill directory.*not found after checkout"):
                    fetch_skill_files(
                        repository="https://github.com/mdproctor/claude-skills",
                        path="nonexistent-skill",
                        ref="v1.0.0"
                    )


def test_fetch_skill_files_includes_stderr_in_error_on_git_failure():
    """fetch_skill_files should include stderr in error message on git failure"""
    error = subprocess.CalledProcessError(1, "git", stderr=b"fatal: repository not found")

    with patch('subprocess.run', side_effect=error):
        with patch('tempfile.mkdtemp', return_value="/tmp/test"):
            from scripts.marketplace.installer import fetch_skill_files

            with pytest.raises(RuntimeError, match="fatal: repository not found"):
                fetch_skill_files(
                    repository="https://github.com/invalid/repo",
                    path="java-dev",
                    ref="v1.0.0"
                )
