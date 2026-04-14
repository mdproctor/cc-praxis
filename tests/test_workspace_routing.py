#!/usr/bin/env python3
"""
Tests for scripts/workspace_routing.py — three-layer routing config resolver.

Covers:
- Layer 1 default: project (built-in, nothing configured)
- Layer 2: global ~/.claude/CLAUDE.md ## Routing **Default destination:**
- Layer 3: workspace CLAUDE.md ## Routing table (per-artifact)
- Resolution algorithm: Layer 3 wins, then Layer 2, then Layer 1
- Edge cases: missing sections, empty tables, invalid values, deprecated vocab
- Warning messages for deprecated or invalid values
"""

import sys
import textwrap
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.workspace_routing import (
    WorkspaceRouter,
    parse_global_routing,
    parse_workspace_routing,
    VALID_LAYER2_VALUES,
    VALID_LAYER3_VALUES,
)

ARTIFACTS = ('adr', 'blog', 'design', 'snapshots')


# ---------------------------------------------------------------------------
# Unit: parse_global_routing
# ---------------------------------------------------------------------------

class TestParseGlobalRouting:

    def test_valid_workspace_default(self):
        content = textwrap.dedent("""\
            ## Some Section
            stuff

            ## Routing
            **Default destination:** workspace

            ## Other Section
        """)
        result, warnings = parse_global_routing(content)
        assert result == 'workspace'
        assert warnings == []

    def test_valid_project_default(self):
        content = textwrap.dedent("""\
            ## Routing
            **Default destination:** project
        """)
        result, warnings = parse_global_routing(content)
        assert result == 'project'
        assert warnings == []

    def test_no_routing_section_returns_none(self):
        content = "## Other Section\nstuff\n"
        result, warnings = parse_global_routing(content)
        assert result is None
        assert warnings == []

    def test_routing_section_no_default_line_returns_none(self):
        content = textwrap.dedent("""\
            ## Routing
            Some text but no **Default destination:** line.
        """)
        result, warnings = parse_global_routing(content)
        assert result is None
        assert warnings == []

    def test_invalid_value_returns_none_with_warning(self):
        content = textwrap.dedent("""\
            ## Routing
            **Default destination:** alternative ~/some/path
        """)
        result, warnings = parse_global_routing(content)
        assert result is None
        assert len(warnings) == 1
        assert 'alternative' in warnings[0].lower() or 'invalid' in warnings[0].lower()

    def test_deprecated_base_value_returns_none_with_warning(self):
        content = textwrap.dedent("""\
            ## Routing
            **Default destination:** base
        """)
        result, warnings = parse_global_routing(content)
        assert result is None
        assert any('deprecated' in w.lower() or 'base' in w.lower() for w in warnings)

    def test_deprecated_project_repo_value_returns_none_with_warning(self):
        content = textwrap.dedent("""\
            ## Routing
            **Default destination:** project repo
        """)
        result, warnings = parse_global_routing(content)
        assert result is None
        assert any('deprecated' in w.lower() or 'project repo' in w.lower() for w in warnings)

    def test_whitespace_trimmed_from_value(self):
        content = textwrap.dedent("""\
            ## Routing
            **Default destination:**   workspace
        """)
        result, warnings = parse_global_routing(content)
        assert result == 'workspace'

    def test_routing_section_mid_document(self):
        content = textwrap.dedent("""\
            # CLAUDE.md

            ## Session Start
            add-dir ~/project/

            ## Work Tracking
            Issue tracking: enabled
            GitHub repo: owner/repo

            ## Routing
            **Default destination:** workspace

            ## Other
            stuff
        """)
        result, warnings = parse_global_routing(content)
        assert result == 'workspace'


# ---------------------------------------------------------------------------
# Unit: parse_workspace_routing
# ---------------------------------------------------------------------------

class TestParseWorkspaceRouting:

    def test_valid_table_all_workspace(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact   | Destination |
            |------------|-------------|
            | adr        | workspace   |
            | design     | workspace   |
            | blog       | project     |
            | snapshots  | workspace   |
        """)
        table, warnings = parse_workspace_routing(content)
        assert table['adr'] == 'workspace'
        assert table['design'] == 'workspace'
        assert table['blog'] == 'project'
        assert table['snapshots'] == 'workspace'
        assert warnings == []

    def test_valid_alternative_path(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination              |
            |----------|--------------------------|
            | blog     | alternative ~/my-blog/   |
        """)
        table, warnings = parse_workspace_routing(content)
        assert table['blog'] == 'alternative ~/my-blog/'
        assert warnings == []

    def test_alternative_with_absolute_path(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination            |
            |----------|------------------------|
            | blog     | alternative /home/user/blog/ |
        """)
        table, warnings = parse_workspace_routing(content)
        assert table['blog'] == 'alternative /home/user/blog/'

    def test_no_routing_section_returns_empty(self):
        content = "## Session Start\nadd-dir ~/project/\n"
        table, warnings = parse_workspace_routing(content)
        assert table == {}
        assert warnings == []

    def test_routing_section_empty_table_returns_empty(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination |
            |----------|-------------|
        """)
        table, warnings = parse_workspace_routing(content)
        assert table == {}

    def test_partial_table_only_some_artifacts(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination |
            |----------|-------------|
            | adr      | workspace   |
        """)
        table, warnings = parse_workspace_routing(content)
        assert table == {'adr': 'workspace'}
        assert 'blog' not in table

    def test_invalid_value_skipped_with_warning(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination |
            |----------|-------------|
            | adr      | nowhere     |
        """)
        table, warnings = parse_workspace_routing(content)
        assert 'adr' not in table
        assert len(warnings) == 1
        assert 'adr' in warnings[0].lower() or 'nowhere' in warnings[0].lower()

    def test_deprecated_base_value_skipped_with_warning(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination |
            |----------|-------------|
            | design   | base        |
        """)
        table, warnings = parse_workspace_routing(content)
        assert 'design' not in table
        assert any('deprecated' in w.lower() or 'base' in w.lower() for w in warnings)

    def test_deprecated_project_repo_value_skipped_with_warning(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination |
            |----------|-------------|
            | design   | project repo |
        """)
        table, warnings = parse_workspace_routing(content)
        assert 'design' not in table
        assert any('deprecated' in w.lower() or 'project repo' in w.lower() for w in warnings)

    def test_deprecated_design_journal_key_skipped_with_warning(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact       | Destination |
            |----------------|-------------|
            | design-journal | workspace   |
        """)
        table, warnings = parse_workspace_routing(content)
        assert 'design-journal' not in table
        assert any('deprecated' in w.lower() or 'design-journal' in w.lower() for w in warnings)

    def test_alternative_without_path_skipped_with_warning(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination |
            |----------|-------------|
            | blog     | alternative |
        """)
        table, warnings = parse_workspace_routing(content)
        assert 'blog' not in table
        assert len(warnings) == 1

    def test_extra_whitespace_trimmed(self):
        content = textwrap.dedent("""\
            ## Routing

            | Artifact   | Destination   |
            |------------|---------------|
            | adr        |   workspace   |
        """)
        table, warnings = parse_workspace_routing(content)
        assert table['adr'] == 'workspace'


# ---------------------------------------------------------------------------
# Unit: WorkspaceRouter.resolve
# ---------------------------------------------------------------------------

class TestWorkspaceRouterResolve:

    def _make_router(self, layer2=None, layer3=None):
        return WorkspaceRouter(layer2_default=layer2, layer3_table=layer3 or {})

    def test_layer1_default_is_project(self):
        router = self._make_router()
        for artifact in ARTIFACTS:
            assert router.resolve(artifact) == 'project'

    def test_layer2_overrides_layer1(self):
        router = self._make_router(layer2='workspace')
        for artifact in ARTIFACTS:
            assert router.resolve(artifact) == 'workspace'

    def test_layer3_overrides_layer2(self):
        router = self._make_router(layer2='workspace', layer3={'adr': 'project'})
        assert router.resolve('adr') == 'project'
        assert router.resolve('design') == 'workspace'

    def test_layer3_overrides_layer1_without_layer2(self):
        router = self._make_router(layer3={'blog': 'workspace'})
        assert router.resolve('blog') == 'workspace'
        assert router.resolve('adr') == 'project'

    def test_layer3_partial_table_falls_through_remaining(self):
        router = self._make_router(layer2='workspace', layer3={'adr': 'project'})
        assert router.resolve('adr') == 'project'    # Layer 3
        assert router.resolve('blog') == 'workspace'  # Layer 2
        assert router.resolve('design') == 'workspace'

    def test_alternative_path_propagates_from_layer3(self):
        router = self._make_router(
            layer2='workspace',
            layer3={'blog': 'alternative ~/my-blog/'}
        )
        assert router.resolve('blog') == 'alternative ~/my-blog/'

    def test_unknown_artifact_falls_to_defaults(self):
        router = self._make_router(layer2='workspace')
        assert router.resolve('unknown-artifact') == 'workspace'

    def test_resolve_all_returns_dict_for_all_known_artifacts(self):
        router = self._make_router(layer2='workspace', layer3={'adr': 'project'})
        result = router.resolve_all()
        for artifact in ARTIFACTS:
            assert artifact in result
        assert result['adr'] == 'project'
        assert result['blog'] == 'workspace'

    def test_resolve_returns_layer_source(self):
        router = self._make_router(layer2='workspace', layer3={'adr': 'project'})
        dest, source = router.resolve_with_source('adr')
        assert dest == 'project'
        assert source == 3

        dest, source = router.resolve_with_source('blog')
        assert dest == 'workspace'
        assert source == 2

        dest, source = router.resolve_with_source('design')
        assert dest == 'workspace'
        assert source == 2

    def test_resolve_with_source_layer1(self):
        router = self._make_router()
        dest, source = router.resolve_with_source('adr')
        assert dest == 'project'
        assert source == 1


# ---------------------------------------------------------------------------
# Integration: parse from CLAUDE.md text and resolve
# ---------------------------------------------------------------------------

class TestWorkspaceRoutingIntegration:

    def test_global_only_all_workspace(self):
        global_content = textwrap.dedent("""\
            ## Routing
            **Default destination:** workspace
        """)
        layer2, warnings = parse_global_routing(global_content)
        assert warnings == []
        router = WorkspaceRouter(layer2_default=layer2)
        assert router.resolve('adr') == 'workspace'
        assert router.resolve('design') == 'workspace'

    def test_workspace_overrides_global(self):
        global_content = textwrap.dedent("""\
            ## Routing
            **Default destination:** workspace
        """)
        workspace_content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination |
            |----------|-------------|
            | blog     | project     |
        """)
        layer2, _ = parse_global_routing(global_content)
        layer3, _ = parse_workspace_routing(workspace_content)
        router = WorkspaceRouter(layer2_default=layer2, layer3_table=layer3)
        assert router.resolve('blog') == 'project'    # Layer 3 override
        assert router.resolve('adr') == 'workspace'   # Layer 2 default

    def test_no_config_everywhere_returns_project(self):
        global_content = "## Other Section\nstuff\n"
        workspace_content = "## Session Start\nadd-dir ~/project/\n"
        layer2, _ = parse_global_routing(global_content)
        layer3, _ = parse_workspace_routing(workspace_content)
        router = WorkspaceRouter(layer2_default=layer2, layer3_table=layer3)
        for artifact in ARTIFACTS:
            assert router.resolve(artifact) == 'project'

    def test_warnings_propagate_from_both_layers(self):
        global_content = textwrap.dedent("""\
            ## Routing
            **Default destination:** base
        """)
        workspace_content = textwrap.dedent("""\
            ## Routing

            | Artifact | Destination  |
            |----------|--------------|
            | adr      | project repo |
        """)
        _, global_warnings = parse_global_routing(global_content)
        _, ws_warnings = parse_workspace_routing(workspace_content)
        assert len(global_warnings) >= 1
        assert len(ws_warnings) >= 1

    def test_design_routing_workspace_needs_workspace_sha(self):
        """
        When design → workspace, epic-start must record workspace/main HEAD SHA.
        Verify the resolved routing makes this deterministic.
        """
        global_content = textwrap.dedent("""\
            ## Routing
            **Default destination:** workspace
        """)
        layer2, _ = parse_global_routing(global_content)
        router = WorkspaceRouter(layer2_default=layer2)
        dest = router.resolve('design')
        assert dest == 'workspace', \
            "design routed to workspace → epic-start must use workspace/main SHA"
