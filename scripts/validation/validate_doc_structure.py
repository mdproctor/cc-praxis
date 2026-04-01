#!/usr/bin/env python3
"""
Check whether a primary document warrants a modularisation nudge.

Reads the nudge threshold from the project's CLAUDE.md if present,
otherwise uses the default (400 lines). Outputs a JSON result so
calling skills can decide whether and how to surface the suggestion.

Usage:
    python validate_doc_structure.py <doc_path> [--claude-md <path>]

Exit codes:
    0 — no nudge needed
    1 — nudge recommended (doc exceeds threshold)
    2 — already modular (has linked modules — suggest reviewing structure)
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_THRESHOLD = 400


def read_threshold(claude_md_path: Path) -> int:
    """
    Read the nudge threshold from CLAUDE.md § Document Structure.
    Returns DEFAULT_THRESHOLD if not found or not configured.
    """
    if not claude_md_path.exists():
        return DEFAULT_THRESHOLD

    content = claude_md_path.read_text()
    match = re.search(r'\*\*Threshold:\*\*\s*(\d+)\s*lines?', content, re.IGNORECASE)
    if match:
        return int(match.group(1))

    return DEFAULT_THRESHOLD


def is_nudge_enabled(claude_md_path: Path) -> bool:
    """Return False if user has explicitly disabled nudges in CLAUDE.md."""
    if not claude_md_path.exists():
        return True

    content = claude_md_path.read_text()
    match = re.search(r'\*\*Modular doc nudge:\*\*\s*(\w+)', content, re.IGNORECASE)
    if match:
        return match.group(1).lower() != 'disabled'
    return True


def count_sections(lines: list[str]) -> list[str]:
    """Return list of section headings (## level only)."""
    return [l.lstrip('#').strip() for l in lines if re.match(r'^## ', l)]


def find_module_links(content: str) -> list[str]:
    """Find markdown links to other .md files (module links)."""
    links = re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', content)
    return [path for _, path in links if not path.startswith('http')]


def analyse(doc_path: Path, claude_md_path: Path) -> dict:
    """
    Analyse a primary document and return a structure nudge assessment.
    """
    if not doc_path.exists():
        return {"error": f"Document not found: {doc_path}"}

    content = doc_path.read_text()
    lines = content.splitlines()
    threshold = read_threshold(claude_md_path)
    nudge_enabled = is_nudge_enabled(claude_md_path)
    sections = count_sections(lines)
    module_links = find_module_links(content)
    already_modular = len(module_links) > 0
    line_count = len(lines)

    result = {
        "doc": str(doc_path),
        "line_count": line_count,
        "threshold": threshold,
        "sections": sections,
        "section_count": len(sections),
        "module_links": module_links,
        "already_modular": already_modular,
        "nudge_enabled": nudge_enabled,
        "nudge": False,
        "review_structure": False,
        "reason": None,
    }

    if not nudge_enabled:
        result["reason"] = "nudge disabled by user"
        return result

    if already_modular:
        # Already split — check if any module links are very large
        # or if structure could be improved (heuristic: many sections)
        if len(sections) > 8:
            result["review_structure"] = True
            result["reason"] = (
                f"Already modular with {len(module_links)} linked module(s), "
                f"but primary doc still has {len(sections)} sections — "
                f"consider moving more sections to dedicated modules"
            )
        else:
            result["reason"] = f"Already modular ({len(module_links)} linked modules)"
        return result

    if line_count >= threshold:
        result["nudge"] = True
        result["reason"] = (
            f"Document is {line_count} lines ({line_count - threshold} over the "
            f"{threshold}-line threshold) with {len(sections)} sections. "
            f"As it grows, collaborators will increasingly step on each other's changes."
        )

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc", help="Path to primary document to check")
    parser.add_argument("--claude-md", default="CLAUDE.md",
                        help="Path to CLAUDE.md for threshold config (default: ./CLAUDE.md)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    doc_path = Path(args.doc)
    claude_md_path = Path(args.claude_md)

    result = analyse(doc_path, claude_md_path)

    if args.json or result.get("error"):
        print(json.dumps(result, indent=2))
        if result.get("error"):
            return 3
        if result["review_structure"]:
            return 2
        if result["nudge"]:
            return 1
        return 0

    # Human-readable output
    if result.get("error"):
        print(f"Error: {result['error']}", file=sys.stderr)
        return 3

    if result["nudge"]:
        print(f"📄 {result['reason']}")
        print(f"   Sections: {', '.join(result['sections'][:5])}"
              + (" ..." if len(result['sections']) > 5 else ""))
        return 1

    if result["review_structure"]:
        print(f"🔍 {result['reason']}")
        return 2

    print(f"✅ {doc_path.name} is {result['line_count']} lines "
          f"(threshold: {result['threshold']}) — no action needed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
