#!/usr/bin/env python3
"""
Tests for project-init/routing.py

Covers: layer precedence, all artifact defaults, deprecated vocab,
invalid values, missing files, alternative paths, single-artifact mode.
"""

import subprocess
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parent.parent / "project-init" / "routing.py"


def run(global_md: Path, workspace_md: Path, artifact: str | None = None) -> subprocess.CompletedProcess:
    args = [sys.executable, str(SCRIPT), str(global_md), str(workspace_md)]
    if artifact:
        args.append(artifact)
    return subprocess.run(args, capture_output=True, text=True)


def parse(result: subprocess.CompletedProcess) -> dict:
    return dict(line.split("=", 1) for line in result.stdout.strip().splitlines() if "=" in line)


def write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# Layer 1 — built-in defaults (no config)
# ---------------------------------------------------------------------------

class TestLayer1Defaults:

    def test_all_artifacts_default_to_project(self, tmp_path):
        g = tmp_path / "global.md"; g.write_text("# nothing\n")
        w = tmp_path / "workspace.md"; w.write_text("# nothing\n")
        out = parse(run(g, w))
        for artifact in ("ADR", "BLOG", "DESIGN", "SNAPSHOTS", "SPECS", "PLANS"):
            assert out[artifact] == "project"

    def test_missing_files_default_to_project(self, tmp_path):
        out = parse(run(tmp_path / "missing.md", tmp_path / "also-missing.md"))
        assert out["DESIGN"] == "project"


# ---------------------------------------------------------------------------
# Layer 2 — global default destination
# ---------------------------------------------------------------------------

class TestLayer2Global:

    def test_workspace_default_overrides_layer1(self, tmp_path):
        g = write(tmp_path / "g.md", "## Routing\n**Default destination:** workspace\n")
        w = write(tmp_path / "w.md", "# nothing\n")
        out = parse(run(g, w))
        for artifact in ("ADR", "BLOG", "DESIGN"):
            assert out[artifact] == "workspace"

    def test_project_default_is_same_as_layer1(self, tmp_path):
        g = write(tmp_path / "g.md", "## Routing\n**Default destination:** project\n")
        w = write(tmp_path / "w.md", "# nothing\n")
        out = parse(run(g, w))
        assert out["DESIGN"] == "project"

    def test_deprecated_base_falls_through_to_layer1(self, tmp_path):
        g = write(tmp_path / "g.md", "## Routing\n**Default destination:** base\n")
        w = write(tmp_path / "w.md", "# nothing\n")
        out = parse(run(g, w))
        assert out["DESIGN"] == "project"

    def test_invalid_global_value_falls_through_to_layer1(self, tmp_path):
        g = write(tmp_path / "g.md", "## Routing\n**Default destination:** elsewhere\n")
        w = write(tmp_path / "w.md", "# nothing\n")
        out = parse(run(g, w))
        assert out["DESIGN"] == "project"


# ---------------------------------------------------------------------------
# Layer 3 — workspace per-artifact table
# ---------------------------------------------------------------------------

class TestLayer3Workspace:

    def test_workspace_table_overrides_global(self, tmp_path):
        g = write(tmp_path / "g.md", "## Routing\n**Default destination:** workspace\n")
        w = write(tmp_path / "w.md", (
            "## Routing\n\n"
            "| Artifact | Destination |\n"
            "|----------+-------------|\n"
            "| adr      | project     |\n"
        ))
        out = parse(run(g, w))
        assert out["ADR"] == "project"
        assert out["BLOG"] == "workspace"  # layer 2 default

    def test_alternative_path_preserved(self, tmp_path):
        g = write(tmp_path / "g.md", "# nothing\n")
        w = write(tmp_path / "w.md", (
            "## Routing\n\n"
            "| Artifact | Destination                  |\n"
            "|----------+------------------------------|\n"
            "| blog     | alternative ~/my-blog/posts/ |\n"
        ))
        out = parse(run(g, w))
        assert out["BLOG"] == "alternative ~/my-blog/posts/"

    def test_deprecated_design_journal_key_ignored(self, tmp_path):
        g = write(tmp_path / "g.md", "# nothing\n")
        w = write(tmp_path / "w.md", (
            "## Routing\n\n"
            "| Artifact       | Destination |\n"
            "|----------------+-------------|\n"
            "| design-journal | workspace   |\n"
            "| design         | workspace   |\n"
        ))
        out = parse(run(g, w))
        assert "DESIGN-JOURNAL" not in out
        assert out["DESIGN"] == "workspace"

    def test_partial_table_other_artifacts_fall_to_global(self, tmp_path):
        g = write(tmp_path / "g.md", "## Routing\n**Default destination:** workspace\n")
        w = write(tmp_path / "w.md", (
            "## Routing\n\n"
            "| Artifact | Destination |\n"
            "|----------+-------------|\n"
            "| blog     | project     |\n"
        ))
        out = parse(run(g, w))
        assert out["BLOG"] == "project"     # layer 3
        assert out["ADR"] == "workspace"    # layer 2 fallback
        assert out["DESIGN"] == "workspace" # layer 2 fallback


# ---------------------------------------------------------------------------
# Single-artifact mode
# ---------------------------------------------------------------------------

class TestSingleArtifact:

    def test_single_artifact_returns_destination_and_layer(self, tmp_path):
        g = write(tmp_path / "g.md", "## Routing\n**Default destination:** workspace\n")
        w = write(tmp_path / "w.md", "# nothing\n")
        result = run(g, w, "design")
        out = parse(result)
        assert out["DESTINATION"] == "workspace"
        assert out["LAYER"] == "2"

    def test_layer1_reported_when_no_config(self, tmp_path):
        g = write(tmp_path / "g.md", "# nothing\n")
        w = write(tmp_path / "w.md", "# nothing\n")
        out = parse(run(g, w, "adr"))
        assert out["DESTINATION"] == "project"
        assert out["LAYER"] == "1"

    def test_layer3_reported_when_workspace_table_matches(self, tmp_path):
        g = write(tmp_path / "g.md", "## Routing\n**Default destination:** project\n")
        w = write(tmp_path / "w.md", (
            "## Routing\n\n"
            "| Artifact | Destination |\n"
            "|----------+-------------|\n"
            "| blog     | workspace   |\n"
        ))
        out = parse(run(g, w, "blog"))
        assert out["DESTINATION"] == "workspace"
        assert out["LAYER"] == "3"

    def test_no_args_prints_usage(self, tmp_path):
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 1
