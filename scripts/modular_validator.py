#!/usr/bin/env python3
"""
Modular Document Validator

Cross-module validation for document groups:
- Link integrity (all links point to existing files/sections)
- Completeness (no orphaned modules, bidirectional references)
- Duplication detection (same content in multiple modules)
- Contradiction detection (semantic conflicts - requires Claude analysis)

Universal across all project types (skills, java, blog, custom, generic).
"""

import re
from pathlib import Path
from typing import List, Dict, Set
from collections import Counter

# Import document discovery types
try:
    from scripts.document_discovery import DocumentGroup
except ImportError:
    # Fallback for testing
    DocumentGroup = None


class ValidationResult:
    """Results from a validation check"""

    def __init__(self, check_name: str):
        self.check_name = check_name
        self.critical: List[str] = []
        self.warnings: List[str] = []
        self.notes: List[str] = []

    def add_critical(self, message: str):
        self.critical.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_note(self, message: str):
        self.notes.append(message)

    def has_critical(self) -> bool:
        return len(self.critical) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def has_issues(self) -> bool:
        return self.has_critical() or self.has_warnings()

    def __str__(self):
        lines = [f"Validation: {self.check_name}"]

        if self.critical:
            lines.append("  CRITICAL:")
            for msg in self.critical:
                lines.append(f"    - {msg}")

        if self.warnings:
            lines.append("  WARNING:")
            for msg in self.warnings:
                lines.append(f"    - {msg}")

        if self.notes:
            lines.append("  NOTE:")
            for msg in self.notes:
                lines.append(f"    - {msg}")

        return '\n'.join(lines)


def validate_document_group(group) -> List[ValidationResult]:
    """
    Orchestrate all validation for a document group.

    1. Run validate_document() on each file (existing validator)
    2. Run cross-module checks (link integrity, completeness, duplication)
    3. Aggregate results

    Args:
        group: DocumentGroup to validate

    Returns:
        List of ValidationResult objects
    """
    results = []

    # Phase 1: Individual file validation (delegate to existing validator)
    from scripts.validate_document import validate_document

    for file_path in group.all_files():
        file_issues = validate_document(file_path)

        if file_issues['critical'] or file_issues['warnings']:
            result = ValidationResult(f"Document: {file_path.name}")

            for issue in file_issues['critical']:
                result.add_critical(issue)

            for issue in file_issues['warnings']:
                result.add_warning(issue)

            results.append(result)

    # Phase 2: Cross-module validation
    results.append(validate_link_integrity(group))
    results.append(check_completeness(group))
    results.append(find_duplication(group))

    # Filter out results with no issues
    return [r for r in results if r.has_issues() or r.notes]


def validate_link_integrity(group) -> ValidationResult:
    """
    Check all markdown links point to existing files and sections.

    Args:
        group: DocumentGroup to validate

    Returns:
        ValidationResult with link integrity issues
    """
    result = ValidationResult("Link Integrity")

    # Check each file in the group
    for file_path in group.all_files():
        if not file_path.exists():
            result.add_critical(f"{file_path}: File does not exist")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for link_text, link_target in links:
            # Skip external URLs
            if link_target.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                continue

            # Split anchor if present
            parts = link_target.split('#')
            file_part = parts[0]
            anchor_part = parts[1] if len(parts) > 1 else None

            # Skip pure anchors (internal to same file)
            if not file_part:
                if anchor_part:
                    # Check anchor exists in current file
                    if not check_anchor_exists(file_path, anchor_part):
                        result.add_warning(
                            f"{file_path.name}: Link to #{anchor_part} - section not found"
                        )
                continue

            # Resolve file path
            target_path = (file_path.parent / file_part).resolve()

            # Check file exists
            if not target_path.exists():
                result.add_critical(
                    f"{file_path.name}: Link to {file_part} - file not found"
                )
                continue

            # Check anchor exists if specified
            if anchor_part:
                if not check_anchor_exists(target_path, anchor_part):
                    result.add_warning(
                        f"{file_path.name}: Link to {file_part}#{anchor_part} - section not found"
                    )

    return result


def check_anchor_exists(file_path: Path, anchor: str) -> bool:
    """
    Check if an anchor (section header) exists in a file.

    Args:
        file_path: File to check
        anchor: Anchor name (e.g., "architecture" for #architecture)

    Returns:
        True if anchor exists, False otherwise
    """
    if not file_path.exists():
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Generate anchor from header text (GitHub style)
    # "## Architecture Overview" → "architecture-overview"
    headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)

    for header in headers:
        # Convert to anchor format
        header_anchor = header.lower()
        header_anchor = re.sub(r'[^\w\s-]', '', header_anchor)
        header_anchor = re.sub(r'[-\s]+', '-', header_anchor)
        header_anchor = header_anchor.strip('-')

        if header_anchor == anchor.lower():
            return True

    return False


def check_completeness(group) -> ValidationResult:
    """
    Ensure no orphaned modules, all references are bidirectional.

    Args:
        group: DocumentGroup to validate

    Returns:
        ValidationResult with completeness issues
    """
    result = ValidationResult("Completeness")

    if not group.modules:
        # Single-file group, no completeness checks needed
        return result

    # Check if primary file references all modules
    primary_refs = get_referenced_files(group.primary_file)

    for module in group.modules:
        if module.relationship == "directory-pattern":
            # Directory pattern modules don't need explicit reference
            continue

        if module.path not in primary_refs:
            result.add_warning(
                f"{module.path.name}: Module not referenced from {group.primary_file.name}"
            )

    # Check if modules reference back to primary (bidirectional)
    for module in group.modules:
        if not module.path.exists():
            continue

        module_refs = get_referenced_files(module.path)

        # Check if module references primary or other modules
        has_refs = group.primary_file in module_refs or any(
            m.path in module_refs for m in group.modules if m.path != module.path
        )

        if not has_refs:
            result.add_note(
                f"{module.path.name}: Module doesn't reference any other group files (consider adding context links)"
            )

    return result


def get_referenced_files(file_path: Path) -> Set[Path]:
    """
    Get all files referenced from a markdown file.

    Args:
        file_path: File to analyze

    Returns:
        Set of referenced file paths
    """
    if not file_path.exists():
        return set()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    referenced = set()

    # Find markdown links
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

    for link_text, link_target in links:
        # Skip external URLs
        if link_target.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
            continue

        # Skip pure anchors
        if link_target.startswith('#'):
            continue

        # Remove anchor
        link_target = link_target.split('#')[0]

        if not link_target:
            continue

        # Resolve path
        target_path = (file_path.parent / link_target).resolve()

        if target_path.exists():
            referenced.add(target_path)

    return referenced


def find_duplication(group) -> ValidationResult:
    """
    Detect duplicate content across modules.

    Args:
        group: DocumentGroup to validate

    Returns:
        ValidationResult with duplication issues
    """
    result = ValidationResult("Duplication")

    if not group.modules:
        # Single-file group, no duplication checks needed
        return result

    # Extract paragraphs from each file
    file_paragraphs: Dict[Path, List[str]] = {}

    for file_path in group.all_files():
        if not file_path.exists():
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into paragraphs (non-empty blocks separated by blank lines)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        # Only consider substantial paragraphs (>100 chars)
        paragraphs = [p for p in paragraphs if len(p) > 100]

        file_paragraphs[file_path] = paragraphs

    # Find duplicates
    paragraph_locations: Dict[str, List[Path]] = {}

    for file_path, paragraphs in file_paragraphs.items():
        for paragraph in paragraphs:
            if paragraph not in paragraph_locations:
                paragraph_locations[paragraph] = []
            paragraph_locations[paragraph].append(file_path)

    # Report duplicates
    for paragraph, locations in paragraph_locations.items():
        if len(locations) > 1:
            files = ', '.join(f.name for f in locations)
            preview = paragraph[:80] + '...' if len(paragraph) > 80 else paragraph
            result.add_note(
                f"Duplicate content found in {files}: \"{preview}\""
            )

    return result


def detect_contradictions(group) -> ValidationResult:
    """
    Find semantic conflicts across modules (requires Claude analysis).

    This is expensive and should only run on explicit user request
    (deep analysis mode). Not implemented yet - placeholder for future.

    Args:
        group: DocumentGroup to validate

    Returns:
        ValidationResult with contradiction issues
    """
    result = ValidationResult("Contradictions (Semantic)")

    # Future implementation: Use Claude API to analyze documents for contradictions
    # For now, just return empty result
    result.add_note("Semantic contradiction detection not yet implemented (requires Claude analysis)")

    return result
