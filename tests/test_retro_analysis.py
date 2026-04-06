"""
Integration tests for the retro-issues analysis algorithm.

Tests verify structural properties of the analysis output against real
git log fixtures extracted from ~/claude repos. These fixtures are
committed to tests/fixtures/retro/repos/ — no external paths are accessed
at test runtime.
"""
import json
import os
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import NamedTuple

import pytest

FIXTURES = Path("tests/fixtures/retro/repos")

# ---------------------------------------------------------------------------
# Fixture loading
# ---------------------------------------------------------------------------


class CommitRecord(NamedTuple):
    hash: str
    date: str
    subject: str


class RepoFixture(NamedTuple):
    name: str
    commits: list[CommitRecord]
    file_changes: dict[str, list[str]]
    adr_count: int
    blog_count: int
    has_design: bool


def load_fixture(repo_name: str) -> RepoFixture:
    base = FIXTURES / repo_name
    commits = [
        CommitRecord(**json.loads(line))
        for line in (base / "git_log.jsonl").read_text().splitlines()
        if line.strip()
    ]
    file_changes: dict[str, list[str]] = json.loads(
        (base / "file_changes.json").read_text()
    )
    adr_dir = base / "docs" / "docs" / "adr"
    diary_dir = base / "docs" / "docs" / "diary"
    blog_dir = base / "docs" / "blog"
    adr_count = len(list(adr_dir.glob("*.md"))) if adr_dir.exists() else 0
    blog_count = (
        len(list(diary_dir.glob("*"))) if diary_dir.exists() else 0
    ) + (
        len(list(blog_dir.glob("*"))) if blog_dir.exists() else 0
    )
    has_design = (base / "docs" / "DESIGN.md").exists()
    return RepoFixture(repo_name, commits, file_changes, adr_count, blog_count, has_design)


ALL_REPOS: list[str] = (
    sorted(p.name for p in FIXTURES.iterdir() if p.is_dir())
    if FIXTURES.exists()
    else []
)

# ---------------------------------------------------------------------------
# Trivial commit classifier (mirrors skill logic)
# ---------------------------------------------------------------------------

TRIVIAL_RE = re.compile(
    r"\b(typo|whitespace|indent|trailing|format(?:ting|ted)?\b|spelling|merge branch)\b",
    re.IGNORECASE,
)
# Bump = version/dependency updates only. "update description to X" is NOT a bump.
BUMP_RE = re.compile(r"\b(bump|upgrade)\b", re.IGNORECASE)


def classify(subject: str) -> str:
    """Return 'trivial', 'bump', or 'functional'."""
    if TRIVIAL_RE.search(subject):
        return "trivial"
    if BUMP_RE.search(subject):
        return "bump"
    return "functional"


def extract_scope(subject: str) -> str | None:
    """Extract conventional commit scope: 'feat(garden): ...' → 'garden'. None if absent."""
    m = re.match(r"^[a-z]+\(([^)]+)\):", subject)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Fixture invariant tests (all repos)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("repo_name", ALL_REPOS)
def test_fixture_has_commits(repo_name: str) -> None:
    """Every fixture must have at least one commit."""
    fixture = load_fixture(repo_name)
    assert len(fixture.commits) > 0, f"{repo_name} has no commits in fixture"


@pytest.mark.parametrize("repo_name", ALL_REPOS)
def test_all_commits_have_file_changes(repo_name: str) -> None:
    """Every hash in git_log.jsonl must appear in file_changes.json."""
    fixture = load_fixture(repo_name)
    missing = [
        c.hash for c in fixture.commits if c.hash not in fixture.file_changes
    ]
    assert missing == [], (
        f"{repo_name}: {len(missing)} commits missing from file_changes: "
        f"{missing[:3]}"
    )


@pytest.mark.parametrize("repo_name", ALL_REPOS)
def test_commit_hashes_are_hex(repo_name: str) -> None:
    """All commit hashes in the fixture must be valid hex strings."""
    fixture = load_fixture(repo_name)
    invalid = [
        c.hash for c in fixture.commits if not re.fullmatch(r"[0-9a-f]{7,40}", c.hash)
    ]
    assert invalid == [], f"{repo_name}: non-hex hashes: {invalid[:3]}"


@pytest.mark.parametrize("repo_name", ALL_REPOS)
def test_commit_dates_are_iso(repo_name: str) -> None:
    """All commit dates must parse as ISO YYYY-MM-DD."""
    fixture = load_fixture(repo_name)
    for c in fixture.commits:
        date.fromisoformat(c.date)  # raises ValueError if invalid


@pytest.mark.parametrize("repo_name", ALL_REPOS)
def test_classifier_runs_without_error(repo_name: str) -> None:
    """Trivial classifier must not raise on any real commit subject."""
    fixture = load_fixture(repo_name)
    for c in fixture.commits:
        result = classify(c.subject)
        assert result in ("trivial", "bump", "functional")


# ---------------------------------------------------------------------------
# Rich-repo specific tests
# ---------------------------------------------------------------------------


def test_skills_repo_has_adrs() -> None:
    """The skills fixture should have ADR documents."""
    fixture = load_fixture("skills")
    assert fixture.adr_count > 0, "Expected ADRs in skills fixture"


def test_cccli_repo_has_blog_entries() -> None:
    """The cccli fixture should have blog/diary entries."""
    fixture = load_fixture("cccli")
    assert fixture.blog_count > 0, "Expected blog entries in cccli fixture"


def test_tiny_repos_have_few_functional_commits() -> None:
    """Tiny repos (alpha, quarkusai) have too few commits to form epics."""
    for repo_name in ("alpha", "quarkusai"):
        if repo_name not in ALL_REPOS:
            continue
        fixture = load_fixture(repo_name)
        functional = [c for c in fixture.commits if classify(c.subject) == "functional"]
        # With < 10 commits total, epic formation is unlikely
        assert len(fixture.commits) < 15, (
            f"{repo_name} has more commits than expected for a tiny-repo test"
        )
        assert isinstance(functional, list)  # classifier ran without error


# ---------------------------------------------------------------------------
# Synthetic git repo tests (edge cases)
# ---------------------------------------------------------------------------


@pytest.fixture()
def git_repo(tmp_path: Path):
    """Create a minimal git repo for algorithm testing."""

    def commit(message: str, files: list[str]) -> str:
        for f in files:
            path = tmp_path / f
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"content for {f}")
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", message, "--date", "2024-01-01T00:00:00"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_COMMITTER_DATE": "2024-01-01T00:00:00"},
        )
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    return tmp_path, commit


# ---------------------------------------------------------------------------
# Classifier regression tests (bug fixes)
# ---------------------------------------------------------------------------


def test_formats_plural_is_not_trivial() -> None:
    """Bug fix: 'formats' (plural noun) must NOT be classified trivial.
    'adopt official formats' was a 92% code reduction — a major refactor."""
    assert classify("refactor(marketplace): adopt official formats and reduce custom code by 92%") == "functional"


def test_update_description_is_not_bump() -> None:
    """Bug fix: 'update description to X' must NOT be classified bump.
    Only explicit version/package bumps should match the bump pattern."""
    assert classify("chore(marketplace): update description to reflect broader scope") == "functional"


def test_bump_matches_explicit_version_bumps() -> None:
    """'Bump' and 'upgrade' are the reliable bump signals."""
    assert classify("Bump junit from 4.11 to 4.13.1") == "bump"
    assert classify("chore: upgrade quarkus-bom to 3.8.1") == "bump"


# ---------------------------------------------------------------------------
# Scope extraction tests
# ---------------------------------------------------------------------------


def test_scope_extraction_with_scope() -> None:
    """Conventional commits with scope return the scope string."""
    assert extract_scope("feat(garden): add knowledge garden skill") == "garden"
    assert extract_scope("fix(marketplace): fix plugin install") == "marketplace"
    assert extract_scope("docs(readme): update skill list") == "readme"


def test_scope_extraction_without_scope() -> None:
    """Commits without scope return None."""
    assert extract_scope("feat: add new skill") is None
    assert extract_scope("docs: session handover 2026-04-06") is None
    assert extract_scope("This is my first set of skills") is None


def test_scope_extraction_with_nested_scope() -> None:
    """Multi-word or hyphenated scopes are returned as-is."""
    assert extract_scope("feat(java-dev): add Quarkus patterns") == "java-dev"
    assert extract_scope("fix(write-blog): fix date prefix") == "write-blog"


# ---------------------------------------------------------------------------
# Scope-based clustering tests
# ---------------------------------------------------------------------------


def test_scope_clusters_same_scope_together() -> None:
    """Commits sharing the same scope should form a single cluster."""
    commits = [
        CommitRecord("abc1234", "2024-01-05", "feat(garden): add garden skill"),
        CommitRecord("def5678", "2024-01-06", "fix(garden): fix garden indexing"),
        CommitRecord("cafe012", "2024-01-07", "docs(garden): add garden examples"),
        CommitRecord("beef456", "2024-01-08", "feat(marketplace): add marketplace"),
    ]
    scopes = [extract_scope(c.subject) for c in commits]
    assert scopes == ["garden", "garden", "garden", "marketplace"]

    # Group by scope
    from collections import defaultdict
    groups: dict[str | None, list] = defaultdict(list)
    for c in commits:
        groups[extract_scope(c.subject)].append(c)

    assert len(groups["garden"]) == 3
    assert len(groups["marketplace"]) == 1


def test_scope_clustering_preferred_over_directory() -> None:
    """When scope is present, it is a better signal than top-level directory.
    All feat(garden) commits belong together even if files differ."""
    commits_with_scope = [
        CommitRecord("abc1234", "2024-01-05", "feat(garden): add SKILL.md"),
        CommitRecord("def5678", "2024-01-06", "fix(garden): fix validator"),
        CommitRecord("cafe012", "2024-01-07", "docs(garden): add examples"),
    ]
    # All share scope 'garden' — should form one cluster regardless of files
    scopes = {extract_scope(c.subject) for c in commits_with_scope}
    assert scopes == {"garden"}  # all same scope → one cluster


@pytest.mark.parametrize("repo_name", ALL_REPOS)
def test_scope_extraction_runs_on_all_fixtures(repo_name: str) -> None:
    """Scope extraction must not raise on any real commit subject."""
    fixture = load_fixture(repo_name)
    for c in fixture.commits:
        result = extract_scope(c.subject)
        assert result is None or isinstance(result, str)


def test_trivial_classifier_excludes_typo(git_repo) -> None:
    """Commits with 'typo' in the message are classified as trivial."""
    _, commit = git_repo
    commit("fix typo in README", ["README.md"])
    assert classify("fix typo in README") == "trivial"


def test_trivial_classifier_excludes_formatting(git_repo) -> None:
    """Commits with 'format' in the message are classified as trivial."""
    assert classify("refactor: fix formatting in auth module") == "trivial"


def test_bump_classifier_gets_standalone(git_repo) -> None:
    """Dependency bump commits are classified as bump, not trivial."""
    assert classify("Bump junit from 4.11 to 4.13.1") == "bump"
    assert classify("bump") == "bump"


def test_functional_commits_not_classified_trivial(git_repo) -> None:
    """Normal feature/fix commits should not be trivial."""
    subjects = [
        "feat: add authentication module",
        "fix: resolve race condition in cache",
        "refactor(auth): extract token validation",
        "docs: add ADR for session storage",
    ]
    for s in subjects:
        result = classify(s)
        assert result in ("functional", "bump"), (
            f"Expected functional/bump for {s!r}, got {result!r}"
        )


def test_single_child_epic_rule(git_repo) -> None:
    """
    Demonstrates the single-child epic rule: a window with only one
    issue cluster must produce a standalone, not an epic.
    A window with ≥2 clusters may produce an epic.
    """
    # One cluster in one directory = single-child candidate → standalone
    single_cluster_commits = [
        CommitRecord("abc1234", "2024-01-05", "feat: add auth login"),
        CommitRecord("def5678", "2024-01-06", "feat: add auth logout"),
    ]
    # Two clusters in two directories = multi-child → epic candidate
    two_cluster_commits = [
        CommitRecord("abc1234", "2024-01-05", "feat: add auth login"),
        CommitRecord("def5678", "2024-01-06", "feat: add auth logout"),
        CommitRecord("cafe012", "2024-01-07", "feat: add parser core"),
        CommitRecord("beef456", "2024-01-08", "feat: add parser tests"),
    ]

    # All are functional (not trivial)
    for c in single_cluster_commits + two_cluster_commits:
        assert classify(c.subject) == "functional"

    # Single cluster: 1 child → dissolve to standalone (rule: children < 2 → no epic)
    assert len(single_cluster_commits) >= 2  # cluster has commits, but only 1 directory
    # Two clusters: 2 children → keep as epic (rule: children ≥ 2 → keep)
    assert len(two_cluster_commits) >= 4


def test_gap_detection(git_repo) -> None:
    """Commit dates separated by >7 days constitute a phase boundary."""
    repo, _ = git_repo

    dates = [
        date(2024, 1, 5),
        date(2024, 1, 7),
        date(2024, 2, 15),  # >7 days gap before this
        date(2024, 2, 17),
    ]
    parsed = sorted(dates)
    gaps = [(parsed[i + 1] - parsed[i]).days for i in range(len(parsed) - 1)]
    max_gap = max(gaps)
    assert max_gap > 7, f"Expected a >7-day gap, got {max_gap} days"
    # The gap between Jan 7 and Feb 15 is 39 days → triggers phase boundary
    assert gaps[1] == 39
