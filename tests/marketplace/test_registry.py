# tests/marketplace/test_registry.py
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

def test_fetch_registry_downloads_from_github():
    """Fetcher should download registry.json from GitHub raw URL"""
    mock_response = Mock()
    mock_response.text = json.dumps({
        "version": "1.0",
        "updated": "2026-03-30T22:30:00Z",
        "skills": []
    })
    mock_response.raise_for_status = Mock()

    with patch('requests.get', return_value=mock_response) as mock_get:
        from scripts.marketplace.registry import fetch_registry

        registry = fetch_registry()

        # Verify correct URL called
        mock_get.assert_called_once_with(
            "https://raw.githubusercontent.com/mdproctor/claude-skill-registry/main/registry.json",
            timeout=30
        )

        # Verify parsed data
        assert registry["version"] == "1.0"
        assert "skills" in registry


def test_fetch_registry_raises_on_network_error():
    """Fetcher should raise clear error on network failure"""
    with patch('requests.get', side_effect=Exception("Network error")):
        from scripts.marketplace.registry import fetch_registry

        with pytest.raises(RuntimeError, match="Failed to fetch registry"):
            fetch_registry()


def test_find_skill_returns_entry_when_found():
    """Lookup should return skill entry from registry"""
    registry = {
        "version": "1.0",
        "skills": [
            {
                "name": "java-dev",
                "repository": "https://github.com/mdproctor/claude-skills",
                "path": "java-dev",
                "defaultRef": "v1.0.0",
                "snapshotRef": "main"
            },
            {
                "name": "quarkus-flow-dev",
                "repository": "https://github.com/mdproctor/claude-skills",
                "path": "quarkus-flow-dev",
                "defaultRef": "v1.2.0",
                "snapshotRef": "main"
            }
        ]
    }

    from scripts.marketplace.registry import find_skill

    entry = find_skill(registry, "java-dev")

    assert entry["name"] == "java-dev"
    assert entry["defaultRef"] == "v1.0.0"


def test_find_skill_raises_when_not_found():
    """Lookup should raise error if skill not in registry"""
    registry = {
        "version": "1.0",
        "skills": []
    }

    from scripts.marketplace.registry import find_skill

    with pytest.raises(ValueError, match="Skill 'unknown-skill' not found"):
        find_skill(registry, "unknown-skill")
