#!/usr/bin/env python3
"""
3-layer artifact routing resolver for cc-praxis workspaces.

Layer 1 (built-in default): project
Layer 2 (global):           ~/.claude/CLAUDE.md  §## Routing **Default destination:**
Layer 3 (workspace):        <workspace>/CLAUDE.md §## Routing table (per-artifact)

Resolution: Layer 3 wins → Layer 2 → Layer 1.

Usage:
    python3 ~/.claude/skills/project-init/routing.py <global_claude_md> <workspace_claude_md> [<artifact>]

    <artifact>  one of: adr blog design snapshots specs plans
                if omitted, resolves all known artifacts

Output (KEY=value lines):
    Single artifact:   DESTINATION=workspace  LAYER=2
    All artifacts:     ADR=project  BLOG=workspace  DESIGN=workspace  ...

    LAYER values: 1=built-in, 2=global, 3=workspace

Exit codes:
    0  success
    1  bad arguments or file read error
"""

import re
import sys
from pathlib import Path

KNOWN_ARTIFACTS = ("adr", "blog", "design", "snapshots", "specs", "plans")
VALID_L2 = frozenset({"project", "workspace"})
DEPRECATED_VALUES = frozenset({"base", "project repo"})
DEPRECATED_KEYS = frozenset({"design-journal"})


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_layer2(text: str) -> str | None:
    """Extract global default destination from CLAUDE.md text."""
    m = re.search(r"^## Routing\s*$", text, re.MULTILINE)
    if not m:
        return None
    section = text[m.end():]
    next_section = re.search(r"^##", section, re.MULTILINE)
    body = section[: next_section.start()] if next_section else section
    dm = re.search(r"\*\*Default destination:\*\*\s*(\S+)", body)
    if not dm:
        return None
    value = dm.group(1).strip()
    if value in DEPRECATED_VALUES:
        return None  # deprecated — fall through to layer 1
    return value if value in VALID_L2 else None


def parse_layer3(text: str) -> dict[str, str]:
    """Extract per-artifact routing table from workspace CLAUDE.md text."""
    m = re.search(r"^## Routing\s*$", text, re.MULTILINE)
    if not m:
        return {}
    section = text[m.end():]
    next_section = re.search(r"^##", section, re.MULTILINE)
    body = section[: next_section.start()] if next_section else section

    table: dict[str, str] = {}
    for row in re.finditer(r"^\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|", body, re.MULTILINE):
        key = row.group(1).strip().lower()
        value = row.group(2).strip()
        if key in ("artifact", "---", ""):
            continue
        if key in DEPRECATED_KEYS:
            continue
        if value in DEPRECATED_VALUES:
            continue
        if value in VALID_L2 or value.startswith("alternative "):
            table[key] = value
    return table


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def resolve(artifact: str, layer2: str | None, layer3: dict[str, str]) -> tuple[str, int]:
    """Resolve routing for one artifact. Returns (destination, layer_number)."""
    if artifact in layer3:
        return layer3[artifact], 3
    if layer2 is not None:
        return layer2, 2
    return "project", 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    global_md_path = Path(sys.argv[1])
    workspace_md_path = Path(sys.argv[2])
    artifact_arg = sys.argv[3].lower() if len(sys.argv) > 3 else None

    global_text = global_md_path.read_text() if global_md_path.exists() else ""
    workspace_text = workspace_md_path.read_text() if workspace_md_path.exists() else ""

    layer2 = parse_layer2(global_text)
    layer3 = parse_layer3(workspace_text)

    if artifact_arg:
        dest, layer = resolve(artifact_arg, layer2, layer3)
        print(f"DESTINATION={dest}")
        print(f"LAYER={layer}")
    else:
        for artifact in KNOWN_ARTIFACTS:
            dest, _ = resolve(artifact, layer2, layer3)
            print(f"{artifact.upper()}={dest}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
