"""
Shared base classes and helpers for the cc-praxis test suite.

Severity helpers
----------------
is_critical(issue), is_warning(issue), is_note(issue) — check ValidationIssue
severity by name. Used across all validator test files; defined here once.

Base classes
------------
TempDirTestCase, DualTempDirTestCase — setUp/tearDown for temporary directories.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


# ---------------------------------------------------------------------------
# Severity helpers — import these instead of redefining in each test file
# ---------------------------------------------------------------------------

def is_critical(issue) -> bool:
    """Return True if the ValidationIssue has CRITICAL severity."""
    return issue.severity.name == "CRITICAL"


def is_warning(issue) -> bool:
    """Return True if the ValidationIssue has WARNING severity."""
    return issue.severity.name == "WARNING"


def is_note(issue) -> bool:
    """Return True if the ValidationIssue has NOTE severity."""
    return issue.severity.name == "NOTE"


class TempDirTestCase(unittest.TestCase):
    """Base class for tests that need a temporary working directory.

    Provides self.test_dir (Path) pointing to a fresh temp directory.
    Automatically cleaned up after each test.
    """

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()


class DualTempDirTestCase(unittest.TestCase):
    """Base class for tests that need two temporary directories.

    Provides self.repo and self.skills (Path) pointing to fresh temp
    directories. Automatically cleaned up after each test. Used for tests
    that simulate a repo + installed skills directory pair.
    """

    def setUp(self):
        self.repo_tmp = TemporaryDirectory()
        self.skills_tmp = TemporaryDirectory()
        self.repo = Path(self.repo_tmp.name)
        self.skills = Path(self.skills_tmp.name)

    def tearDown(self):
        self.repo_tmp.cleanup()
        self.skills_tmp.cleanup()
