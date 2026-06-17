"""Tests for project-init/ctx.py — context field extraction and path resolution."""

import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parent.parent / "project-init" / "ctx.py"


def run_ctx(cwd: Path) -> subprocess.CompletedProcess:
    """Execute ctx.py in the given directory."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


def parse(result: subprocess.CompletedProcess) -> dict:
    """Parse ctx.py output into a dict."""
    return dict(
        line.split("=", 1)
        for line in result.stdout.strip().splitlines()
        if "=" in line
    )


def init_repo(path: Path, claude_md: str = "") -> Path:
    """Initialize a git repo with optional CLAUDE.md content."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@test.com"], capture_output=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )
    if claude_md:
        (path / "CLAUDE.md").write_text(claude_md)
    return path


class TestPathResolution:
    """Test workspace/project path resolution via symlinks."""

    def test_single_repo_mode(self, tmp_path):
        """No symlinks → WORKSPACE==PROJECT, SINGLE_REPO=yes."""
        repo = init_repo(tmp_path / "repo")
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["WORKSPACE"] == data["PROJECT"]
        assert data["SINGLE_REPO"] == "yes"

    def test_workspace_with_proj_symlink(self, tmp_path):
        """proj/ in workspace → WORKSPACE != PROJECT."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)

        result = run_ctx(workspace)
        data = parse(result)

        assert result.returncode == 0
        assert data["WORKSPACE"] == str(workspace)
        assert data["PROJECT"] == str(project)
        assert data["SINGLE_REPO"] == "no"

    def test_project_with_wksp_symlink(self, tmp_path):
        """wksp/ in project → WORKSPACE != PROJECT."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (project / "wksp").symlink_to(workspace)

        result = run_ctx(project)
        data = parse(result)

        assert result.returncode == 0
        assert data["WORKSPACE"] == str(workspace)
        assert data["PROJECT"] == str(project)
        assert data["SINGLE_REPO"] == "no"

    def test_returns_resolved_paths_not_symlink_paths(self, tmp_path):
        """Verify resolved paths, not symlink paths, are returned."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)
        out = parse(run_ctx(workspace))
        assert Path(out["PROJECT"]).resolve() == project.resolve()
        assert Path(out["WORKSPACE"]).resolve() == workspace.resolve()

    def test_current_branch_captured(self, tmp_path):
        """CURRENT_BRANCH reflects the active git branch."""
        repo = init_repo(tmp_path / "project")
        subprocess.run(["git", "-C", str(repo), "checkout", "-b", "feat/test-branch"], capture_output=True)
        out = parse(run_ctx(repo))
        assert out["CURRENT_BRANCH"] == "feat/test-branch"


class TestClaudeMdParsing:
    """Test CLAUDE.md field extraction."""

    def test_owner_repo_extracted(self, tmp_path):
        """Extract OWNER_REPO from 'GitHub repo: owner/name'."""
        claude_md = """
# Project

GitHub repo: mdproctor/cc-praxis
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["OWNER_REPO"] == "mdproctor/cc-praxis"

    def test_owner_repo_empty_when_missing(self, tmp_path):
        """OWNER_REPO empty when CLAUDE.md has no GitHub repo."""
        repo = init_repo(tmp_path / "repo", "# Project\n\nNo repo info here.")
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["OWNER_REPO"] == ""

    def test_base_branch_extracted(self, tmp_path):
        """Extract BASE_BRANCH from '**Project base branch:** `develop`'."""
        claude_md = """
# Project

**Project base branch:** `develop`
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["BASE_BRANCH"] == "develop"

    def test_base_branch_defaults_to_main(self, tmp_path):
        """BASE_BRANCH defaults to 'main' when not specified."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["BASE_BRANCH"] == "main"


class TestMetaParsing:
    """Test .meta file parsing."""

    def test_meta_fields_extracted(self, tmp_path):
        """Extract all 5 fields from .meta."""
        meta_content = """branch: issue-123-test-feature
project-sha: abc123def456
issue: 123
issue-repo: owner/repo
covers: 42,43
"""
        repo = init_repo(tmp_path / "repo")
        (repo / "design").mkdir()
        (repo / "design" / ".meta").write_text(meta_content)

        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["BRANCH_NAME"] == "issue-123-test-feature"
        assert data["PROJECT_SHA"] == "abc123def456"
        assert data["ISSUE_N"] == "123"
        assert data["ISSUE_REPO"] == "owner/repo"
        assert data["COVERS"] == "42,43"

    def test_meta_missing_returns_empty(self, tmp_path):
        """All meta fields empty when .meta missing."""
        repo = init_repo(tmp_path / "repo")
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["BRANCH_NAME"] == ""
        assert data["PROJECT_SHA"] == ""
        assert data["ISSUE_N"] == ""
        assert data["ISSUE_REPO"] == ""
        assert data["COVERS"] == ""

    def test_covers_defaults_to_issue(self, tmp_path):
        """COVERS falls back to ISSUE_N value when covers field absent."""
        meta_content = """branch: issue-99-something
issue: 99
"""
        repo = init_repo(tmp_path / "repo")
        (repo / "design").mkdir()
        (repo / "design" / ".meta").write_text(meta_content)

        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["ISSUE_N"] == "99"
        assert data["COVERS"] == "99"

    def test_issue_repo_defaults_to_owner_repo(self, tmp_path):
        """ISSUE_REPO falls back to OWNER_REPO when issue-repo absent."""
        claude_md = "GitHub repo: mdproctor/cc-praxis"
        meta_content = """branch: issue-123-test
issue: 123
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        (repo / "design").mkdir()
        (repo / "design" / ".meta").write_text(meta_content)

        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["OWNER_REPO"] == "mdproctor/cc-praxis"
        assert data["ISSUE_REPO"] == "mdproctor/cc-praxis"

    def test_meta_read_from_workspace_not_project(self, tmp_path):
        """Verify .meta is read from workspace, not project, in dual-repo mode."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)
        (workspace / "design").mkdir()
        (workspace / "design" / ".meta").write_text("branch: ws-branch\nissue: 42\n")
        (project / "design").mkdir()
        (project / "design" / ".meta").write_text("branch: proj-branch\nissue: 999\n")
        out = parse(run_ctx(workspace))
        assert out["ISSUE_N"] == "42"
        assert out["BRANCH_NAME"] == "ws-branch"

    def test_malformed_meta_lines_skipped(self, tmp_path):
        """Lines without ': ' separator are silently ignored."""
        repo = init_repo(tmp_path / "project")
        (repo / "design").mkdir()
        (repo / "design" / ".meta").write_text(
            "branch: good-branch\n"
            "this line has no separator\n"
            "issue: 42\n"
        )
        out = parse(run_ctx(repo))
        assert out["BRANCH_NAME"] == "good-branch"
        assert out["ISSUE_N"] == "42"


class TestFastPathChecks:
    """Test fast-path yes/no checks."""

    def test_claude_ok_yes_when_project_type_present(self, tmp_path):
        """CLAUDE_OK=yes when CLAUDE.md has '## Project Type' section."""
        claude_md = """
# Project

## Project Type

**Type:** java
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["CLAUDE_OK"] == "yes"

    def test_claude_ok_no_when_missing(self, tmp_path):
        """CLAUDE_OK=no when CLAUDE.md absent or has no project type."""
        repo = init_repo(tmp_path / "repo")
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["CLAUDE_OK"] == "no"

    def test_workspace_ok_yes_with_symlink(self, tmp_path):
        """WORKSPACE_OK=yes when proj/ or wksp/ symlink present."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)

        result = run_ctx(workspace)
        data = parse(result)

        assert result.returncode == 0
        assert data["WORKSPACE_OK"] == "yes"

    def test_workspace_ok_yes_when_declined(self, tmp_path):
        """WORKSPACE_OK=yes when CLAUDE.md has 'workspace: declined'."""
        claude_md = """
# Project

workspace: declined
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["WORKSPACE_OK"] == "yes"

    def test_workspace_ok_no_when_neither(self, tmp_path):
        """WORKSPACE_OK=no when no symlink and not declined."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["WORKSPACE_OK"] == "no"

    def test_issues_ok_yes_when_enabled(self, tmp_path):
        """ISSUES_STATUS=enabled when 'Issue tracking: enabled' in CLAUDE.md."""
        claude_md = """
## Work Tracking

Issue tracking: enabled
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["ISSUES_STATUS"] == "enabled"
        assert "ISSUES_OK" not in data

    def test_issues_ok_yes_when_declined(self, tmp_path):
        """ISSUES_STATUS=declined when 'Issue tracking: declined' in CLAUDE.md."""
        claude_md = """
## Work Tracking

Issue tracking: declined
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["ISSUES_STATUS"] == "declined"
        assert "ISSUES_OK" not in data

    def test_issues_ok_no_when_absent(self, tmp_path):
        """ISSUES_STATUS=absent when no Work Tracking section."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        result = run_ctx(repo)
        data = parse(result)

        assert result.returncode == 0
        assert data["ISSUES_STATUS"] == "absent"
        assert "ISSUES_OK" not in data


class TestProjectType:
    """Test PROJECT_TYPE field extraction."""

    def test_project_type_from_type_prefix(self, tmp_path):
        """PROJECT_TYPE extracted from 'type: java' format."""
        claude_md = """
## Project Type

type: java
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["PROJECT_TYPE"] == "java"

    def test_project_type_from_bold_format(self, tmp_path):
        """PROJECT_TYPE extracted from '**Type:** skills' format."""
        claude_md = """
## Project Type

**Type:** skills
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["PROJECT_TYPE"] == "skills"

    def test_project_type_empty_when_no_section(self, tmp_path):
        """PROJECT_TYPE empty when no Project Type section."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        data = parse(run_ctx(repo))
        assert data["PROJECT_TYPE"] == ""

    def test_project_type_empty_when_section_but_no_type(self, tmp_path):
        """PROJECT_TYPE empty when section exists but no type line."""
        claude_md = """
## Project Type

Some other content here.
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["PROJECT_TYPE"] == ""


class TestIssuesStatus:
    """Test ISSUES_STATUS field (replaces ISSUES_OK)."""

    def test_issues_status_enabled(self, tmp_path):
        """ISSUES_STATUS=enabled when tracking enabled."""
        claude_md = """
## Work Tracking

Issue tracking: enabled
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["ISSUES_STATUS"] == "enabled"
        assert "ISSUES_OK" not in data

    def test_issues_status_declined(self, tmp_path):
        """ISSUES_STATUS=declined when tracking declined."""
        claude_md = """
## Work Tracking

Issue tracking: declined
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["ISSUES_STATUS"] == "declined"
        assert "ISSUES_OK" not in data

    def test_issues_status_absent(self, tmp_path):
        """ISSUES_STATUS=absent when no Work Tracking section."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        data = parse(run_ctx(repo))
        assert data["ISSUES_STATUS"] == "absent"
        assert "ISSUES_OK" not in data


class TestHasMeta:
    """Test HAS_META field."""

    def test_has_meta_yes(self, tmp_path):
        """HAS_META=yes when design/.meta exists in workspace."""
        repo = init_repo(tmp_path / "repo")
        (repo / "design").mkdir()
        (repo / "design" / ".meta").write_text("branch: test\n")
        data = parse(run_ctx(repo))
        assert data["HAS_META"] == "yes"

    def test_has_meta_no(self, tmp_path):
        """HAS_META=no when design/.meta absent."""
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["HAS_META"] == "no"


class TestDesignRepoKey:
    """Test DESIGN_REPO_KEY field."""

    def test_design_repo_key_from_meta(self, tmp_path):
        """DESIGN_REPO_KEY extracted from .meta."""
        repo = init_repo(tmp_path / "repo")
        (repo / "design").mkdir()
        (repo / "design" / ".meta").write_text("design-repo: mdproctor/design-repo\n")
        data = parse(run_ctx(repo))
        assert data["DESIGN_REPO_KEY"] == "mdproctor/design-repo"

    def test_design_repo_key_empty_when_no_meta(self, tmp_path):
        """DESIGN_REPO_KEY empty when .meta absent."""
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["DESIGN_REPO_KEY"] == ""


class TestFileExistenceChecks:
    """Test file existence yes/no fields."""

    def test_has_arc42stories_yes(self, tmp_path):
        """HAS_ARC42STORIES=yes when ARC42STORIES.MD exists in project."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)
        (project / "ARC42STORIES.MD").write_text("# Stories\n")
        data = parse(run_ctx(workspace))
        assert data["HAS_ARC42STORIES"] == "yes"

    def test_has_arc42stories_no(self, tmp_path):
        """HAS_ARC42STORIES=no when file absent."""
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["HAS_ARC42STORIES"] == "no"

    def test_has_project_artifacts_yes(self, tmp_path):
        """HAS_PROJECT_ARTIFACTS=yes when section present in CLAUDE.md."""
        claude_md = """
## Project Artifacts

Paths that are project content.
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["HAS_PROJECT_ARTIFACTS"] == "yes"

    def test_has_project_artifacts_no(self, tmp_path):
        """HAS_PROJECT_ARTIFACTS=no when section absent."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        data = parse(run_ctx(repo))
        assert data["HAS_PROJECT_ARTIFACTS"] == "no"

    def test_workspace_declined_yes(self, tmp_path):
        """WORKSPACE_DECLINED=yes when workspace declined in CLAUDE.md."""
        claude_md = """
workspace: declined
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["WORKSPACE_DECLINED"] == "yes"

    def test_workspace_declined_no(self, tmp_path):
        """WORKSPACE_DECLINED=no when not declined."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        data = parse(run_ctx(repo))
        assert data["WORKSPACE_DECLINED"] == "no"

    def test_has_platform_doc_yes_project(self, tmp_path):
        """HAS_PLATFORM_DOC=yes when docs/PLATFORM.md in project."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)
        (project / "docs").mkdir()
        (project / "docs" / "PLATFORM.md").write_text("# Platform\n")
        data = parse(run_ctx(workspace))
        assert data["HAS_PLATFORM_DOC"] == "yes"

    def test_has_platform_doc_yes_workspace(self, tmp_path):
        """HAS_PLATFORM_DOC=yes when docs/PLATFORM.md in workspace."""
        repo = init_repo(tmp_path / "repo")
        (repo / "docs").mkdir()
        (repo / "docs" / "PLATFORM.md").write_text("# Platform\n")
        data = parse(run_ctx(repo))
        assert data["HAS_PLATFORM_DOC"] == "yes"

    def test_has_platform_doc_yes_workspace_docs(self, tmp_path):
        """HAS_PLATFORM_DOC=yes when workspace/docs/PLATFORM.md exists."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)
        (workspace / "docs").mkdir()
        (workspace / "docs" / "PLATFORM.md").write_text("# Platform\n")
        data = parse(run_ctx(workspace))
        assert data["HAS_PLATFORM_DOC"] == "yes"

    def test_has_platform_doc_no(self, tmp_path):
        """HAS_PLATFORM_DOC=no when absent from all locations."""
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["HAS_PLATFORM_DOC"] == "no"

    def test_has_protocols_dir_yes_project(self, tmp_path):
        """HAS_PROTOCOLS_DIR=yes when docs/protocols/ in project."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)
        (project / "docs" / "protocols").mkdir(parents=True)
        data = parse(run_ctx(workspace))
        assert data["HAS_PROTOCOLS_DIR"] == "yes"

    def test_has_protocols_dir_yes_workspace(self, tmp_path):
        """HAS_PROTOCOLS_DIR=yes when docs/protocols/ in workspace."""
        repo = init_repo(tmp_path / "repo")
        (repo / "docs" / "protocols").mkdir(parents=True)
        data = parse(run_ctx(repo))
        assert data["HAS_PROTOCOLS_DIR"] == "yes"

    def test_has_protocols_dir_yes_workspace_docs(self, tmp_path):
        """HAS_PROTOCOLS_DIR=yes when workspace/docs/protocols/ exists."""
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)
        (workspace / "docs" / "protocols").mkdir(parents=True)
        data = parse(run_ctx(workspace))
        assert data["HAS_PROTOCOLS_DIR"] == "yes"

    def test_has_protocols_dir_no(self, tmp_path):
        """HAS_PROTOCOLS_DIR=no when absent from all locations."""
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["HAS_PROTOCOLS_DIR"] == "no"

    def test_has_blog_routing_yes_home(self, tmp_path, monkeypatch):
        """HAS_BLOG_ROUTING=yes when ~/.claude/blog-routing.yaml exists."""
        tmp_home = tmp_path / "home"
        tmp_home.mkdir()
        monkeypatch.setenv("HOME", str(tmp_home))
        (tmp_home / ".claude").mkdir()
        (tmp_home / ".claude" / "blog-routing.yaml").write_text("# routing\n")
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["HAS_BLOG_ROUTING"] == "yes"

    def test_has_blog_routing_yes_project(self, tmp_path, monkeypatch):
        """HAS_BLOG_ROUTING=yes when project/blog-routing.yaml exists."""
        monkeypatch.setenv("HOME", str(tmp_path / "fakehome"))
        project = init_repo(tmp_path / "project")
        workspace = init_repo(tmp_path / "workspace")
        (workspace / "proj").symlink_to(project)
        (project / "blog-routing.yaml").write_text("# routing\n")
        data = parse(run_ctx(workspace))
        assert data["HAS_BLOG_ROUTING"] == "yes"

    def test_has_blog_routing_yes_workspace(self, tmp_path, monkeypatch):
        """HAS_BLOG_ROUTING=yes when workspace/blog-routing.yaml exists."""
        monkeypatch.setenv("HOME", str(tmp_path / "fakehome"))
        repo = init_repo(tmp_path / "repo")
        (repo / "blog-routing.yaml").write_text("# routing\n")
        data = parse(run_ctx(repo))
        assert data["HAS_BLOG_ROUTING"] == "yes"

    def test_has_blog_routing_no(self, tmp_path, monkeypatch):
        """HAS_BLOG_ROUTING=no when absent from all locations."""
        monkeypatch.setenv("HOME", str(tmp_path / "fakehome"))
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["HAS_BLOG_ROUTING"] == "no"

    def test_has_writing_style_ref_yes_writing_style(self, tmp_path):
        """HAS_WRITING_STYLE_REF=yes when CLAUDE.md mentions 'writing style' with .md reference."""
        claude_md = """
The writing-style.md guide is mandatory.
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["HAS_WRITING_STYLE_REF"] == "yes"

    def test_has_writing_style_ref_yes_blog_technical(self, tmp_path):
        """HAS_WRITING_STYLE_REF=yes when CLAUDE.md mentions 'blog-technical'."""
        claude_md = """
Load ~/claude-workspace/writing-styles/blog-technical.md before drafting.
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["HAS_WRITING_STYLE_REF"] == "yes"

    def test_has_writing_style_ref_no(self, tmp_path):
        """HAS_WRITING_STYLE_REF=no when no style reference."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        data = parse(run_ctx(repo))
        assert data["HAS_WRITING_STYLE_REF"] == "no"


class TestClaudeMdFields:
    """Test CLAUDE.md field extraction."""

    def test_blog_dir_extracted(self, tmp_path):
        """BLOG_DIR extracted from '**Blog directory:** `path`'."""
        claude_md = """
**Blog directory:** `/Users/mdproctor/claude/public/cc-praxis/blog/`
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["BLOG_DIR"] == "/Users/mdproctor/claude/public/cc-praxis/blog/"

    def test_blog_dir_empty_when_missing(self, tmp_path):
        """BLOG_DIR empty when not in CLAUDE.md."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        data = parse(run_ctx(repo))
        assert data["BLOG_DIR"] == ""

    def test_project_name_extracted(self, tmp_path):
        """PROJECT_NAME extracted from '**Name:** cc-praxis'."""
        claude_md = """
**Name:** cc-praxis
"""
        repo = init_repo(tmp_path / "repo", claude_md)
        data = parse(run_ctx(repo))
        assert data["PROJECT_NAME"] == "cc-praxis"

    def test_project_name_empty_when_missing(self, tmp_path):
        """PROJECT_NAME empty when not in CLAUDE.md."""
        repo = init_repo(tmp_path / "repo", "# Project\n")
        data = parse(run_ctx(repo))
        assert data["PROJECT_NAME"] == ""


class TestMetaNewFields:
    """Test new .meta field extraction."""

    def test_flyway_next_v_from_meta(self, tmp_path):
        """FLYWAY_NEXT_V extracted from .meta."""
        repo = init_repo(tmp_path / "repo")
        (repo / "design").mkdir()
        (repo / "design" / ".meta").write_text("flyway-next-v: V2025.06.18.1234\n")
        data = parse(run_ctx(repo))
        assert data["FLYWAY_NEXT_V"] == "V2025.06.18.1234"

    def test_flyway_next_v_empty_when_no_meta(self, tmp_path):
        """FLYWAY_NEXT_V empty when .meta absent."""
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["FLYWAY_NEXT_V"] == ""

    def test_meta_section_hashes_from_meta(self, tmp_path):
        """META_SECTION_HASHES extracted from .meta."""
        repo = init_repo(tmp_path / "repo")
        (repo / "design").mkdir()
        (repo / "design" / ".meta").write_text("design-section-hashes: abc123,def456\n")
        data = parse(run_ctx(repo))
        assert data["META_SECTION_HASHES"] == "abc123,def456"

    def test_meta_section_hashes_empty_when_no_meta(self, tmp_path):
        """META_SECTION_HASHES empty when .meta absent."""
        repo = init_repo(tmp_path / "repo")
        data = parse(run_ctx(repo))
        assert data["META_SECTION_HASHES"] == ""
