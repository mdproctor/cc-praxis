# scripts/marketplace/registry.py
import json
import requests
from typing import Dict, Any

REGISTRY_URL = "https://raw.githubusercontent.com/mdproctor/claude-skill-registry/main/registry.json"

def fetch_registry(registry_url: str = REGISTRY_URL) -> Dict[str, Any]:
    """
    Fetch registry.json from GitHub.

    Args:
        registry_url: URL to registry.json (default: official registry)

    Returns:
        Parsed registry data

    Raises:
        RuntimeError: If fetch or parse fails
    """
    try:
        response = requests.get(registry_url, timeout=30)
        response.raise_for_status()
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch registry from {registry_url}: {e}")


def find_skill(registry: Dict[str, Any], skill_name: str) -> Dict[str, Any]:
    """
    Find skill entry in registry by name.

    Args:
        registry: Parsed registry data
        skill_name: Name of skill to find

    Returns:
        Skill registry entry

    Raises:
        ValueError: If skill not found
    """
    for skill in registry["skills"]:
        if skill["name"] == skill_name:
            return skill

    raise ValueError(f"Skill '{skill_name}' not found in registry")
