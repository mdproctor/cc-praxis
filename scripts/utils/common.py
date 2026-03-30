"""Common utilities for validation scripts."""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = 1  # Must fix before commit
    WARNING = 2   # Should fix before commit
    NOTE = 3      # Improve when possible


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: Severity
    file_path: str
    line_number: Optional[int]
    message: str
    fix_suggestion: Optional[str] = None

    def __str__(self) -> str:
        """Format issue for display."""
        severity_str = self.severity.name
        location = f"{self.file_path}"
        if self.line_number:
            location += f":{self.line_number}"

        result = f"[{severity_str}] {location}: {self.message}"
        if self.fix_suggestion:
            result += f"\n  Fix: {self.fix_suggestion}"
        return result

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON output."""
        return {
            'severity': self.severity.name,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'message': self.message,
            'fix_suggestion': self.fix_suggestion
        }


@dataclass
class ValidationResult:
    """Results of a validation run."""
    validator_name: str
    issues: List[ValidationIssue]
    files_checked: int

    @property
    def critical_count(self) -> int:
        """Count of critical issues."""
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def warning_count(self) -> int:
        """Count of warning issues."""
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def note_count(self) -> int:
        """Count of note issues."""
        return sum(1 for i in self.issues if i.severity == Severity.NOTE)

    @property
    def passed(self) -> bool:
        """True if no critical issues."""
        return self.critical_count == 0

    @property
    def exit_code(self) -> int:
        """Appropriate exit code based on issues."""
        if self.critical_count > 0:
            return 1
        elif self.warning_count > 0:
            return 2
        elif self.note_count > 0:
            return 3
        return 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON output."""
        return {
            'validator_name': self.validator_name,
            'files_checked': self.files_checked,
            'critical_count': self.critical_count,
            'warning_count': self.warning_count,
            'note_count': self.note_count,
            'passed': self.passed,
            'issues': [issue.to_dict() for issue in self.issues]
        }


def find_skills_root() -> Path:
    """Find the skills repository root directory."""
    # Start from current directory
    current = Path.cwd()

    # Walk up until we find CLAUDE.md or README.md
    while current != current.parent:
        if (current / 'CLAUDE.md').exists() or (current / 'README.md').exists():
            return current
        current = current.parent

    # Default to current directory
    return Path.cwd()


def find_all_skill_files() -> List[Path]:
    """Find all SKILL.md files in the repository."""
    skills_root = find_skills_root()
    skill_files = []

    # Find all SKILL.md files
    for skill_md in skills_root.glob('*/SKILL.md'):
        # Skip hidden directories and common non-skill directories
        if not any(part.startswith('.') for part in skill_md.parts):
            if 'node_modules' not in skill_md.parts and 'venv' not in skill_md.parts:
                skill_files.append(skill_md)

    return sorted(skill_files)


def get_skill_name_from_path(skill_path: Path) -> str:
    """Extract skill name from path (directory name)."""
    return skill_path.parent.name


def read_file_with_line_numbers(file_path: Path) -> List[Tuple[int, str]]:
    """Read file and return list of (line_number, content) tuples."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [(i + 1, line.rstrip('\n')) for i, line in enumerate(f)]
    except Exception as e:
        return []


def print_summary(result: ValidationResult, verbose: bool = False):
    """Print validation result summary."""
    print(f"\n{result.validator_name}")
    print("=" * len(result.validator_name))
    print(f"Files checked: {result.files_checked}")
    print(f"Critical: {result.critical_count}, Warning: {result.warning_count}, Note: {result.note_count}")

    if result.passed:
        print("✅ PASSED")
    else:
        print("❌ FAILED")

    if verbose and result.issues:
        print("\nIssues:")
        for issue in sorted(result.issues, key=lambda x: (x.severity.value, x.file_path)):
            print(f"  {issue}")


def format_issues_by_severity(issues: List[ValidationIssue]) -> str:
    """Format issues grouped by severity."""
    if not issues:
        return "✅ No issues found"

    output = []

    critical = [i for i in issues if i.severity == Severity.CRITICAL]
    if critical:
        output.append("\n### CRITICAL Issues (Must Fix Before Commit)")
        for issue in critical:
            output.append(f"- {issue}")

    warnings = [i for i in issues if i.severity == Severity.WARNING]
    if warnings:
        output.append("\n### WARNING Issues (Should Fix Before Commit)")
        for issue in warnings:
            output.append(f"- {issue}")

    notes = [i for i in issues if i.severity == Severity.NOTE]
    if notes:
        output.append("\n### NOTE Issues (Improve When Possible)")
        for issue in notes:
            output.append(f"- {issue}")

    return "\n".join(output)
