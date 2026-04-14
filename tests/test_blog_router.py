#!/usr/bin/env python3
"""
Tests for scripts/blog_router.py — blog routing config resolver.

Coverage:
- Unit: BlogRouter.resolve_destinations (rules, AND logic, union, defaults)
- Unit: merge_configs (extends, project adds to global, destination override)
- Unit: BlogRouter.get_destination_config (lookup, merged destinations)
- Unit: load_routing_config (valid YAML, missing file, invalid YAML)
- Integration: full resolver pipeline with global-only and global+project configs
- Edge cases: empty tags/projects, case sensitivity, deduplication
"""

import pytest
import tempfile
import textwrap
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.blog_router import BlogRouter, load_routing_config, merge_configs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

GLOBAL_CONFIG = {
    'version': 1,
    'destinations': {
        'personal-blog': {'type': 'git', 'path': '~/blog/', 'subdir': '_posts/'},
        'quarkus-blog': {'type': 'git', 'path': '~/quarkus-community-blog/', 'subdir': '_posts/'},
    },
    'defaults': {
        'destinations': ['personal-blog'],
    },
    'rules': [
        {
            'match': {'tags': ['quarkus']},
            'destinations': ['quarkus-blog', 'personal-blog'],
        },
    ],
}

PROJECT_CONFIG = {
    'extends': '~/.claude/blog-routing.yaml',
    'destinations': {
        'project-blog': {'type': 'git', 'path': '~/cc-praxis-blog/', 'subdir': '_posts/'},
    },
    'rules': [
        {
            'match': {'entry_type': 'article', 'projects': ['cc-praxis']},
            'destinations': ['personal-blog', 'project-blog'],
        },
    ],
}

DIARY_ENTRY = {
    'entry_type': 'note',
    'subtype': 'diary',
    'projects': ['cc-praxis'],
    'tags': [],
}

QUARKUS_ARTICLE = {
    'entry_type': 'article',
    'projects': ['quarkus-flow'],
    'tags': ['quarkus', 'java'],
}

CC_PRAXIS_ARTICLE = {
    'entry_type': 'article',
    'projects': ['cc-praxis'],
    'tags': ['skills'],
}


# ---------------------------------------------------------------------------
# Unit: BlogRouter.resolve_destinations — rules and defaults
# ---------------------------------------------------------------------------

class TestResolveDestinations:

    def test_no_rules_returns_default_destinations(self):
        config = {
            'version': 1,
            'destinations': {'personal-blog': {'type': 'git', 'path': '~/blog/'}},
            'defaults': {'destinations': ['personal-blog']},
            'rules': [],
        }
        router = BlogRouter(config)
        assert router.resolve_destinations(DIARY_ENTRY) == ['personal-blog']

    def test_no_match_uses_defaults(self):
        router = BlogRouter(GLOBAL_CONFIG)
        entry = {'entry_type': 'note', 'projects': ['cc-praxis'], 'tags': []}
        assert router.resolve_destinations(entry) == ['personal-blog']

    def test_rule_match_by_entry_type(self):
        config = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'articles-blog': {'type': 'git', 'path': '~/articles/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [
                {'match': {'entry_type': 'article'}, 'destinations': ['articles-blog']},
            ],
        }
        router = BlogRouter(config)
        entry = {'entry_type': 'article', 'projects': ['proj'], 'tags': []}
        assert router.resolve_destinations(entry) == ['articles-blog']

    def test_rule_match_by_single_tag(self):
        router = BlogRouter(GLOBAL_CONFIG)
        entry = {'entry_type': 'note', 'projects': ['other'], 'tags': ['quarkus']}
        dests = router.resolve_destinations(entry)
        assert 'quarkus-blog' in dests
        assert 'personal-blog' in dests

    def test_rule_match_by_partial_tag_overlap(self):
        """Entry with one of the rule's tags is enough to match."""
        config = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'java-blog': {'type': 'git', 'path': '~/java/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [
                {'match': {'tags': ['quarkus', 'java']}, 'destinations': ['java-blog']},
            ],
        }
        router = BlogRouter(config)
        entry = {'entry_type': 'note', 'projects': [], 'tags': ['java']}
        assert 'java-blog' in router.resolve_destinations(entry)

    def test_rule_match_by_project(self):
        config = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'project-blog': {'type': 'git', 'path': '~/project/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [
                {'match': {'projects': ['cc-praxis']}, 'destinations': ['project-blog']},
            ],
        }
        router = BlogRouter(config)
        entry = {'entry_type': 'note', 'projects': ['cc-praxis'], 'tags': []}
        assert 'project-blog' in router.resolve_destinations(entry)

    def test_rule_and_logic_entry_type_and_tags_both_required(self):
        """Rule with entry_type AND tags: only matches when BOTH conditions are met."""
        config = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'specific-blog': {'type': 'git', 'path': '~/specific/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [
                {
                    'match': {'entry_type': 'article', 'tags': ['quarkus']},
                    'destinations': ['specific-blog'],
                },
            ],
        }
        router = BlogRouter(config)

        # Both conditions met → matches
        matching = {'entry_type': 'article', 'projects': [], 'tags': ['quarkus']}
        assert 'specific-blog' in router.resolve_destinations(matching)

        # Only entry_type matches → no match, falls to defaults
        only_type = {'entry_type': 'article', 'projects': [], 'tags': ['python']}
        assert router.resolve_destinations(only_type) == ['personal-blog']

        # Only tag matches → no match, falls to defaults
        only_tag = {'entry_type': 'note', 'projects': [], 'tags': ['quarkus']}
        assert router.resolve_destinations(only_tag) == ['personal-blog']

    def test_multiple_matching_rules_union_destinations(self):
        """When multiple rules match, their destinations are unioned."""
        config = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'quarkus-blog': {'type': 'git', 'path': '~/quarkus/'},
                'project-blog': {'type': 'git', 'path': '~/project/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [
                {'match': {'tags': ['quarkus']}, 'destinations': ['quarkus-blog']},
                {'match': {'projects': ['cc-praxis']}, 'destinations': ['project-blog']},
            ],
        }
        router = BlogRouter(config)
        entry = {'entry_type': 'article', 'projects': ['cc-praxis'], 'tags': ['quarkus']}
        dests = router.resolve_destinations(entry)
        assert 'quarkus-blog' in dests
        assert 'project-blog' in dests

    def test_duplicate_destinations_are_deduplicated(self):
        """Multiple matching rules pointing to the same destination produce one entry."""
        config = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'quarkus-blog': {'type': 'git', 'path': '~/quarkus/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [
                {'match': {'tags': ['quarkus']}, 'destinations': ['personal-blog', 'quarkus-blog']},
                {'match': {'entry_type': 'article'}, 'destinations': ['personal-blog']},
            ],
        }
        router = BlogRouter(config)
        entry = {'entry_type': 'article', 'projects': [], 'tags': ['quarkus']}
        dests = router.resolve_destinations(entry)
        assert dests.count('personal-blog') == 1

    def test_empty_tags_dont_match_tag_rule(self):
        """Entry with no tags cannot match a tag-based rule."""
        router = BlogRouter(GLOBAL_CONFIG)
        entry = {'entry_type': 'article', 'projects': ['cc-praxis'], 'tags': []}
        # quarkus rule should NOT match
        dests = router.resolve_destinations(entry)
        assert 'quarkus-blog' not in dests

    def test_empty_projects_dont_match_project_rule(self):
        config = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'project-blog': {'type': 'git', 'path': '~/project/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [
                {'match': {'projects': ['cc-praxis']}, 'destinations': ['project-blog']},
            ],
        }
        router = BlogRouter(config)
        entry = {'entry_type': 'note', 'projects': [], 'tags': []}
        assert router.resolve_destinations(entry) == ['personal-blog']

    def test_entry_type_match_is_case_sensitive(self):
        """entry_type matching is exact — 'Article' does not match 'article'."""
        router = BlogRouter(GLOBAL_CONFIG)
        # GLOBAL_CONFIG has no entry_type rule, but let's verify case sensitivity explicitly
        config = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'articles-blog': {'type': 'git', 'path': '~/articles/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [
                {'match': {'entry_type': 'article'}, 'destinations': ['articles-blog']},
            ],
        }
        router = BlogRouter(config)
        entry_upper = {'entry_type': 'Article', 'projects': [], 'tags': []}
        assert router.resolve_destinations(entry_upper) == ['personal-blog']

    def test_missing_defaults_returns_empty_list(self):
        """If no defaults.destinations configured and no rules match, return empty."""
        config = {
            'version': 1,
            'destinations': {'personal-blog': {'type': 'git', 'path': '~/blog/'}},
            'rules': [],
        }
        router = BlogRouter(config)
        entry = {'entry_type': 'note', 'projects': [], 'tags': []}
        assert router.resolve_destinations(entry) == []


# ---------------------------------------------------------------------------
# Unit: merge_configs
# ---------------------------------------------------------------------------

class TestMergeConfigs:

    def test_project_rules_added_to_global_rules(self):
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        assert len(merged['rules']) == len(GLOBAL_CONFIG['rules']) + len(PROJECT_CONFIG['rules'])

    def test_global_rules_still_apply_after_merge(self):
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        global_rule_matches = [r for r in merged['rules'] if 'tags' in r.get('match', {})]
        assert len(global_rule_matches) >= 1

    def test_project_rules_present_after_merge(self):
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        project_rule_matches = [r for r in merged['rules']
                                if 'entry_type' in r.get('match', {}) and 'projects' in r.get('match', {})]
        assert len(project_rule_matches) >= 1

    def test_project_destinations_added_to_global(self):
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        assert 'project-blog' in merged['destinations']
        assert 'personal-blog' in merged['destinations']
        assert 'quarkus-blog' in merged['destinations']

    def test_project_destination_overrides_global_destination(self):
        """Project can redefine a destination that already exists in global."""
        global_cfg = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/old-blog/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [],
        }
        project_cfg = {
            'extends': '~/.claude/blog-routing.yaml',
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/new-blog/'},
            },
            'rules': [],
        }
        merged = merge_configs(global_cfg, project_cfg)
        assert merged['destinations']['personal-blog']['path'] == '~/new-blog/'

    def test_project_defaults_override_global_defaults(self):
        global_cfg = {
            'version': 1,
            'destinations': {
                'personal-blog': {'type': 'git', 'path': '~/blog/'},
                'project-blog': {'type': 'git', 'path': '~/project/'},
            },
            'defaults': {'destinations': ['personal-blog']},
            'rules': [],
        }
        project_cfg = {
            'extends': '~/.claude/blog-routing.yaml',
            'defaults': {'destinations': ['project-blog']},
            'rules': [],
        }
        merged = merge_configs(global_cfg, project_cfg)
        assert merged['defaults']['destinations'] == ['project-blog']

    def test_merge_with_no_project_config_returns_global(self):
        merged = merge_configs(GLOBAL_CONFIG, None)
        assert merged == GLOBAL_CONFIG

    def test_merge_project_without_rules_key(self):
        """Project config without a 'rules' key doesn't break the merge."""
        project_cfg = {
            'extends': '~/.claude/blog-routing.yaml',
            'destinations': {'extra-blog': {'type': 'git', 'path': '~/extra/'}},
        }
        merged = merge_configs(GLOBAL_CONFIG, project_cfg)
        assert merged['rules'] == GLOBAL_CONFIG['rules']
        assert 'extra-blog' in merged['destinations']


# ---------------------------------------------------------------------------
# Unit: BlogRouter.get_destination_config
# ---------------------------------------------------------------------------

class TestGetDestinationConfig:

    def test_get_known_destination(self):
        router = BlogRouter(GLOBAL_CONFIG)
        dest = router.get_destination_config('personal-blog')
        assert dest['type'] == 'git'
        assert '~/blog/' in dest['path']

    def test_get_unknown_destination_raises(self):
        router = BlogRouter(GLOBAL_CONFIG)
        with pytest.raises(KeyError):
            router.get_destination_config('nonexistent-blog')

    def test_get_merged_destination_from_project(self):
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        router = BlogRouter(merged)
        dest = router.get_destination_config('project-blog')
        assert dest['path'] == '~/cc-praxis-blog/'


# ---------------------------------------------------------------------------
# Unit: load_routing_config
# ---------------------------------------------------------------------------

class TestLoadRoutingConfig:

    def test_load_valid_minimal_config(self, tmp_path):
        config_file = tmp_path / 'blog-routing.yaml'
        config_file.write_text(textwrap.dedent("""\
            version: 1
            destinations:
              personal-blog:
                type: git
                path: ~/blog/
                subdir: _posts/
            defaults:
              destinations: [personal-blog]
            rules: []
        """))
        config = load_routing_config(config_file)
        assert config['version'] == 1
        assert 'personal-blog' in config['destinations']
        assert config['defaults']['destinations'] == ['personal-blog']
        assert config['rules'] == []

    def test_load_config_with_rules(self, tmp_path):
        config_file = tmp_path / 'blog-routing.yaml'
        config_file.write_text(textwrap.dedent("""\
            version: 1
            destinations:
              personal-blog:
                type: git
                path: ~/blog/
              quarkus-blog:
                type: git
                path: ~/quarkus/
            defaults:
              destinations: [personal-blog]
            rules:
              - match:
                  tags: [quarkus]
                destinations: [quarkus-blog, personal-blog]
        """))
        config = load_routing_config(config_file)
        assert len(config['rules']) == 1
        assert config['rules'][0]['match']['tags'] == ['quarkus']
        assert 'quarkus-blog' in config['rules'][0]['destinations']

    def test_load_missing_file_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_routing_config(tmp_path / 'nonexistent.yaml')

    def test_load_invalid_yaml_raises_value_error(self, tmp_path):
        config_file = tmp_path / 'bad.yaml'
        config_file.write_text('version: 1\ndestinations: [\nunclosed bracket')
        with pytest.raises(ValueError):
            load_routing_config(config_file)

    def test_load_config_with_extends_field(self, tmp_path):
        config_file = tmp_path / 'project-routing.yaml'
        config_file.write_text(textwrap.dedent("""\
            extends: ~/.claude/blog-routing.yaml
            destinations:
              project-blog:
                type: git
                path: ~/project/
            rules:
              - match:
                  entry_type: article
                destinations: [project-blog]
        """))
        config = load_routing_config(config_file)
        assert config['extends'] == '~/.claude/blog-routing.yaml'
        assert 'project-blog' in config['destinations']


# ---------------------------------------------------------------------------
# Integration: full routing pipeline
# ---------------------------------------------------------------------------

class TestBlogRouterIntegration:

    def test_global_only_diary_routes_to_personal(self):
        router = BlogRouter(GLOBAL_CONFIG)
        dests = router.resolve_destinations(DIARY_ENTRY)
        assert dests == ['personal-blog']

    def test_global_only_quarkus_article_routes_to_both(self):
        router = BlogRouter(GLOBAL_CONFIG)
        dests = router.resolve_destinations(QUARKUS_ARTICLE)
        assert set(dests) == {'quarkus-blog', 'personal-blog'}

    def test_project_config_extends_global_rules(self):
        """Project rules are additive — global quarkus rule still fires."""
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        router = BlogRouter(merged)
        dests = router.resolve_destinations(QUARKUS_ARTICLE)
        assert 'quarkus-blog' in dests

    def test_cc_praxis_article_triggers_project_rule(self):
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        router = BlogRouter(merged)
        dests = router.resolve_destinations(CC_PRAXIS_ARTICLE)
        assert 'project-blog' in dests
        assert 'personal-blog' in dests

    def test_cc_praxis_article_with_quarkus_tag_routes_to_all_three(self):
        """Quarkus tag triggers global rule, cc-praxis project triggers project rule."""
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        router = BlogRouter(merged)
        entry = {
            'entry_type': 'article',
            'projects': ['cc-praxis'],
            'tags': ['quarkus', 'skills'],
        }
        dests = router.resolve_destinations(entry)
        assert 'quarkus-blog' in dests
        assert 'personal-blog' in dests
        assert 'project-blog' in dests

    def test_diary_entry_with_project_config_still_uses_defaults(self):
        """Diary entries don't match any rules → use defaults."""
        merged = merge_configs(GLOBAL_CONFIG, PROJECT_CONFIG)
        router = BlogRouter(merged)
        dests = router.resolve_destinations(DIARY_ENTRY)
        assert dests == ['personal-blog']

    def test_load_and_route_from_yaml_files(self, tmp_path):
        """End-to-end: load configs from disk, resolve destinations."""
        global_file = tmp_path / 'global-routing.yaml'
        global_file.write_text(textwrap.dedent("""\
            version: 1
            destinations:
              personal-blog:
                type: git
                path: ~/blog/
                subdir: _posts/
              quarkus-blog:
                type: git
                path: ~/quarkus/
                subdir: _posts/
            defaults:
              destinations: [personal-blog]
            rules:
              - match:
                  tags: [quarkus]
                destinations: [quarkus-blog, personal-blog]
        """))

        project_file = tmp_path / 'project-routing.yaml'
        project_file.write_text(textwrap.dedent("""\
            extends: ~/.claude/blog-routing.yaml
            destinations:
              project-blog:
                type: git
                path: ~/cc-praxis-blog/
                subdir: _posts/
            rules:
              - match:
                  entry_type: article
                  projects: [cc-praxis]
                destinations: [personal-blog, project-blog]
        """))

        global_config = load_routing_config(global_file)
        project_config = load_routing_config(project_file)
        merged = merge_configs(global_config, project_config)
        router = BlogRouter(merged)

        quarkus_cc = {
            'entry_type': 'article',
            'projects': ['cc-praxis'],
            'tags': ['quarkus'],
        }
        dests = router.resolve_destinations(quarkus_cc)
        assert set(dests) == {'personal-blog', 'quarkus-blog', 'project-blog'}

    def test_dest_config_accessible_after_merge(self, tmp_path):
        """get_destination_config works on destinations from both global and project."""
        global_file = tmp_path / 'global.yaml'
        global_file.write_text(textwrap.dedent("""\
            version: 1
            destinations:
              personal-blog:
                type: git
                path: ~/blog/
            defaults:
              destinations: [personal-blog]
            rules: []
        """))
        project_file = tmp_path / 'project.yaml'
        project_file.write_text(textwrap.dedent("""\
            extends: ~/.claude/blog-routing.yaml
            destinations:
              project-blog:
                type: git
                path: ~/project/
            rules: []
        """))
        merged = merge_configs(load_routing_config(global_file), load_routing_config(project_file))
        router = BlogRouter(merged)

        assert router.get_destination_config('personal-blog')['path'] == '~/blog/'
        assert router.get_destination_config('project-blog')['path'] == '~/project/'
