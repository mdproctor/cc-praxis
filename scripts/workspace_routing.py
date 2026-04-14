#!/usr/bin/env python3
"""
Workspace routing config resolver — three-layer routing algorithm.

Parses the ## Routing sections from CLAUDE.md files and resolves
effective routing destinations for each artifact type.

Layer 1 (built-in):  project            ← default when nothing configured
Layer 2 (global):    ~/.claude/CLAUDE.md  ## Routing **Default destination:**
Layer 3 (workspace): <workspace>/CLAUDE.md  ## Routing table (per-artifact)

Resolution: Layer 3 wins → Layer 2 → Layer 1.
"""

from __future__ import annotations

import re
from typing import Optional

# Known artifact types for resolve_all()
ARTIFACTS = ('adr', 'blog', 'design', 'snapshots')

# Valid values at each layer
VALID_LAYER2_VALUES = frozenset({'project', 'workspace'})

# At Layer 3, 'alternative <path>' is also valid
_VALID_LAYER3_SCALARS = frozenset({'project', 'workspace'})

# Deprecated vocabulary that triggers a warning and falls through
_DEPRECATED_VALUES = frozenset({'base', 'project repo'})
_DEPRECATED_KEYS = frozenset({'design-journal'})

VALID_LAYER3_VALUES = _VALID_LAYER3_SCALARS | {'alternative <path>'}  # doc only


def _is_valid_layer3_value(value: str) -> bool:
    if value in _VALID_LAYER3_SCALARS:
        return True
    if value.startswith('alternative ') and len(value) > len('alternative '):
        # Must have a path: starts with / or ~
        path = value[len('alternative '):].strip()
        return path.startswith('/') or path.startswith('~')
    return False


def _is_deprecated(value: str) -> bool:
    return value.lower() in {v.lower() for v in _DEPRECATED_VALUES}


def parse_global_routing(content: str) -> tuple[Optional[str], list[str]]:
    """
    Parse the ## Routing section from a global CLAUDE.md string.

    Returns (destination, warnings):
        destination — 'workspace', 'project', or None (absent/invalid)
        warnings    — list of human-readable warning strings
    """
    warnings: list[str] = []

    # Find ## Routing section (exact heading, standalone line)
    section_match = re.search(r'^## Routing\s*$', content, re.MULTILINE)
    if not section_match:
        return None, warnings

    # Extract content from ## Routing to next ## heading (or end)
    section_start = section_match.end()
    next_section = re.search(r'^## ', content[section_start:], re.MULTILINE)
    section_content = content[section_start:section_start + next_section.start()] \
        if next_section else content[section_start:]

    # Find **Default destination:** line
    dest_match = re.search(
        r'^\*\*Default destination:\*\*\s*(.+)$',
        section_content,
        re.MULTILINE,
    )
    if not dest_match:
        return None, warnings

    value = dest_match.group(1).strip()

    # Check deprecated vocabulary
    if _is_deprecated(value):
        warnings.append(
            f"Routing config uses deprecated value {value!r}. "
            f"Replace with: project | workspace. Falling through to next layer."
        )
        return None, warnings

    # Check valid Layer 2 values
    if value not in VALID_LAYER2_VALUES:
        warnings.append(
            f"Invalid global routing value {value!r}. "
            f"Valid values: project | workspace. "
            f"Ignoring Layer 2 — falling through to Layer 1."
        )
        return None, warnings

    return value, warnings


def parse_workspace_routing(content: str) -> tuple[dict, list[str]]:
    """
    Parse the ## Routing section from a workspace CLAUDE.md string.

    Returns (table, warnings):
        table    — dict mapping artifact name → destination string
        warnings — list of human-readable warning strings

    Only valid artifact rows are included; invalid/deprecated rows are
    skipped and produce a warning.
    """
    table: dict = {}
    warnings: list[str] = []

    section_match = re.search(r'^## Routing\s*$', content, re.MULTILINE)
    if not section_match:
        return table, warnings

    section_start = section_match.end()
    next_section = re.search(r'^## ', content[section_start:], re.MULTILINE)
    section_content = content[section_start:section_start + next_section.start()] \
        if next_section else content[section_start:]

    # Parse markdown table rows (skip header and separator rows)
    for line in section_content.splitlines():
        line = line.strip()
        if not line.startswith('|') or not line.endswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 2:
            continue
        artifact, destination = cells[0].strip(), cells[1].strip()

        # Skip header row
        if artifact.lower() in ('artifact', ''):
            continue
        # Skip separator rows (contain only dashes)
        if re.match(r'^[-:]+$', artifact):
            continue

        # Check deprecated keys
        if artifact in _DEPRECATED_KEYS:
            warnings.append(
                f"Routing config uses deprecated key {artifact!r}. "
                f"Replace with: design. Falling through to next layer."
            )
            continue

        # Check deprecated destination values
        if _is_deprecated(destination):
            warnings.append(
                f"Routing config for {artifact!r} uses deprecated value {destination!r}. "
                f"Replace with: project | workspace | alternative <path>. "
                f"Falling through to next layer."
            )
            continue

        # Validate destination value
        if not _is_valid_layer3_value(destination):
            # Check specifically for bare 'alternative' with no path
            if destination == 'alternative':
                warnings.append(
                    f"Routing config for {artifact!r}: "
                    f"'alternative' requires a path (e.g. 'alternative ~/my-repo/'). "
                    f"Falling through to next layer."
                )
            else:
                warnings.append(
                    f"Invalid routing value {destination!r} for {artifact!r}. "
                    f"Valid values: project | workspace | alternative <path>. "
                    f"Falling through to next layer."
                )
            continue

        table[artifact] = destination

    return table, warnings


class WorkspaceRouter:
    """
    Resolves effective routing destination for each artifact using the
    three-layer algorithm.

    Layer 1 (built-in): 'project'
    Layer 2 (global):   layer2_default (str | None)
    Layer 3 (workspace): layer3_table (dict artifact → dest)
    """

    _LAYER1_DEFAULT = 'project'

    def __init__(
        self,
        layer2_default: Optional[str] = None,
        layer3_table: Optional[dict] = None,
    ):
        self._layer2 = layer2_default
        self._layer3 = layer3_table or {}

    def resolve(self, artifact: str) -> str:
        """Resolve the effective destination for an artifact."""
        dest, _ = self.resolve_with_source(artifact)
        return dest

    def resolve_with_source(self, artifact: str) -> tuple[str, int]:
        """
        Resolve destination and return (destination, layer_number).

        layer_number is 1, 2, or 3 indicating which layer provided the value.
        """
        if artifact in self._layer3:
            return self._layer3[artifact], 3
        if self._layer2 is not None:
            return self._layer2, 2
        return self._LAYER1_DEFAULT, 1

    def resolve_all(self) -> dict:
        """Resolve destinations for all known artifact types."""
        return {artifact: self.resolve(artifact) for artifact in ARTIFACTS}
