#!/usr/bin/env python3
"""
Blog routing config resolver.

Loads and merges blog-routing.yaml configs (global + per-project),
then resolves destination names for a blog entry based on its frontmatter.

Rule semantics:
- Match fields use AND logic across fields (entry_type AND tags AND projects must all match).
- For list fields (tags, projects), a rule matches if there is ANY overlap with the entry's list.
- Multiple matching rules: destinations are unioned (not first-match-wins).
- No matching rules: entry goes to defaults.destinations (or [] if not configured).
- Project config extends global: project rules are appended, destinations are merged
  (project wins on conflict), project defaults override global defaults.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Optional

import yaml


def load_routing_config(config_path: Path) -> dict:
    """
    Load and parse a blog-routing.yaml file.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file contains invalid YAML.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Routing config not found: {config_path}")
    try:
        text = config_path.read_text(encoding='utf-8')
        config = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {config_path}: {exc}") from exc
    return config or {}


def merge_configs(global_config: dict, project_config: Optional[dict]) -> dict:
    """
    Merge a project routing config on top of the global config.

    - Project destinations override global destinations on key conflict.
    - Project rules are appended to global rules (additive, not replacing).
    - Project defaults override global defaults when present.
    - If project_config is None, the global config is returned unchanged.
    """
    if project_config is None:
        return global_config

    merged = copy.deepcopy(global_config)

    # Merge destinations (project wins on key conflict)
    project_destinations = project_config.get('destinations') or {}
    merged.setdefault('destinations', {}).update(project_destinations)

    # Append project rules (global rules stay intact)
    project_rules = project_config.get('rules') or []
    merged.setdefault('rules', []).extend(project_rules)

    # Project defaults override global defaults
    if 'defaults' in project_config:
        merged['defaults'] = copy.deepcopy(project_config['defaults'])

    return merged


def _rule_matches(rule: dict, entry: dict) -> bool:
    """
    Return True if the rule's match criteria are satisfied by the entry.

    AND logic across fields:
    - Scalar fields (entry_type): exact string match.
    - List fields (tags, projects): any overlap between rule list and entry list.
    """
    match = rule.get('match', {})
    for field, rule_value in match.items():
        entry_value = entry.get(field)
        if isinstance(rule_value, list):
            # List field: match if any overlap
            entry_list = entry_value if isinstance(entry_value, list) else []
            if not set(rule_value) & set(entry_list):
                return False
        else:
            # Scalar field: exact match
            if entry_value != rule_value:
                return False
    return True


class BlogRouter:
    """
    Resolves blog entry destinations using a (merged) routing config.
    """

    def __init__(self, config: dict):
        self._config = config

    def resolve_destinations(self, entry: dict) -> list[str]:
        """
        Resolve destination names for a blog entry.

        Applies all matching rules (AND logic per rule, union across rules).
        Falls back to defaults.destinations when no rules match.
        Deduplicates while preserving first-encounter order.
        """
        matched: list[str] = []
        for rule in self._config.get('rules', []):
            if _rule_matches(rule, entry):
                for dest in rule.get('destinations', []):
                    if dest not in matched:
                        matched.append(dest)

        if matched:
            return matched

        defaults = self._config.get('defaults', {})
        return list(defaults.get('destinations', []))

    def get_destination_config(self, name: str) -> dict:
        """
        Return the config dict for a named destination.

        Raises:
            KeyError: if the destination name is not in the config.
        """
        destinations = self._config.get('destinations', {})
        if name not in destinations:
            raise KeyError(f"Unknown destination: {name!r}")
        return destinations[name]
