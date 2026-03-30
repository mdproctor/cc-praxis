"""
Tests for dependency resolver graph builder.
"""

import pytest
from unittest.mock import Mock, patch


def test_build_graph_single_skill_no_deps():
    """Graph builder should handle skill with no dependencies"""
    mock_skill_json = {
        "name": "java-dev",
        "version": "1.0.0",
        "repository": "https://github.com/mdproctor/claude-skills",
        "dependencies": []
    }

    with patch('scripts.marketplace.dependency_resolver.fetch_skill_metadata', return_value=mock_skill_json):
        from scripts.marketplace.dependency_resolver import build_dependency_graph

        graph = build_dependency_graph("java-dev", registry={})

        assert len(graph) == 1
        assert graph[0]["name"] == "java-dev"
        assert graph[0]["dependencies"] == []


def test_build_graph_with_single_dependency():
    """Graph builder should resolve single dependency"""
    java_dev_metadata = {
        "name": "java-dev",
        "version": "1.0.0",
        "repository": "https://github.com/mdproctor/claude-skills",
        "dependencies": []
    }

    quarkus_flow_metadata = {
        "name": "quarkus-flow-dev",
        "version": "1.2.0",
        "repository": "https://github.com/mdproctor/claude-skills",
        "dependencies": [
            {
                "name": "java-dev",
                "repository": "https://github.com/mdproctor/claude-skills",
                "ref": "v1.0.0"
            }
        ]
    }

    def mock_fetch(repo, path, ref):
        if path == "quarkus-flow-dev":
            return quarkus_flow_metadata
        elif path == "java-dev":
            return java_dev_metadata
        raise ValueError(f"Unknown skill: {path}")

    with patch('scripts.marketplace.dependency_resolver.fetch_skill_metadata', side_effect=mock_fetch):
        from scripts.marketplace.dependency_resolver import build_dependency_graph

        graph = build_dependency_graph("quarkus-flow-dev", registry={})

        # Should include both skills
        assert len(graph) == 2

        # java-dev should come first (dependency)
        assert graph[0]["name"] == "java-dev"
        assert graph[1]["name"] == "quarkus-flow-dev"


def test_build_graph_detects_circular_dependency():
    """Graph builder should detect circular dependencies"""
    skill_a = {
        "name": "skill-a",
        "version": "1.0.0",
        "repository": "https://github.com/test/repo",
        "dependencies": [
            {
                "name": "skill-b",
                "repository": "https://github.com/test/repo",
                "ref": "main"
            }
        ]
    }

    skill_b = {
        "name": "skill-b",
        "version": "1.0.0",
        "repository": "https://github.com/test/repo",
        "dependencies": [
            {
                "name": "skill-a",  # Circular!
                "repository": "https://github.com/test/repo",
                "ref": "main"
            }
        ]
    }

    def mock_fetch(repo, path, ref):
        if path == "skill-a":
            return skill_a
        elif path == "skill-b":
            return skill_b
        raise ValueError(f"Unknown skill: {path}")

    with patch('scripts.marketplace.dependency_resolver.fetch_skill_metadata', side_effect=mock_fetch):
        from scripts.marketplace.dependency_resolver import build_dependency_graph

        with pytest.raises(ValueError, match="Circular dependency detected"):
            build_dependency_graph("skill-a", registry={})


def test_detect_conflict_raises_on_version_mismatch():
    """Conflict detector should raise error when same skill required with different refs"""
    from scripts.marketplace.dependency_resolver import detect_conflicts

    graph = [
        {
            "name": "java-dev",
            "version": "1.0.0",
            "dependencies": [],
            "ref": "v1.0.0"
        },
        {
            "name": "java-dev",
            "version": "2.0.0",
            "dependencies": [],
            "ref": "v2.0.0"
        }
    ]

    with pytest.raises(RuntimeError, match="Dependency conflict"):
        detect_conflicts(graph)


def test_detect_conflict_passes_on_same_ref():
    """Conflict detector should allow same skill with same ref"""
    from scripts.marketplace.dependency_resolver import detect_conflicts

    graph = [
        {
            "name": "java-dev",
            "version": "1.0.0",
            "dependencies": [],
            "ref": "v1.0.0"
        },
        {
            "name": "quarkus-flow-dev",
            "version": "1.2.0",
            "dependencies": [],
            "ref": "v1.2.0"
        }
    ]

    # Should not raise
    detect_conflicts(graph)
