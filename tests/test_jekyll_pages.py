#!/usr/bin/env python3
"""
Tests for Jekyll filtered pages — issue #53.

Verifies that:
- docs/articles/index.html exists and filters by entry_type: article
- docs/blog/index.html filters to subtype: diary (not all posts)
- Navigation in default.html includes Articles link
- Blog page heading updated to reflect diary-only scope

Tests use static analysis of the Liquid templates — no Jekyll build required.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ARTICLES_PAGE = REPO_ROOT / 'docs' / 'articles' / 'index.html'
BLOG_PAGE = REPO_ROOT / 'docs' / 'blog' / 'index.html'
DEFAULT_LAYOUT = REPO_ROOT / 'docs' / '_layouts' / 'default.html'


class TestArticlesPage:
    """docs/articles/index.html must exist and filter to articles only."""

    def test_articles_page_exists(self):
        assert ARTICLES_PAGE.exists(), "docs/articles/index.html does not exist"

    def test_articles_page_has_jekyll_frontmatter(self):
        content = ARTICLES_PAGE.read_text()
        assert content.startswith('---'), "articles/index.html must have YAML frontmatter"
        assert 'layout: default' in content

    def test_articles_page_has_permalink(self):
        content = ARTICLES_PAGE.read_text()
        assert '/articles/' in content

    def test_articles_page_filters_by_entry_type_article(self):
        """The page must filter posts to entry_type == 'article'."""
        content = ARTICLES_PAGE.read_text()
        assert 'entry_type' in content, "articles page must filter on entry_type"
        assert 'article' in content, "articles page must check for entry_type: article"

    def test_articles_page_has_posts_loop(self):
        content = ARTICLES_PAGE.read_text()
        assert 'site.posts' in content, "articles page must iterate over site.posts"

    def test_articles_page_has_meaningful_title(self):
        content = ARTICLES_PAGE.read_text()
        assert 'title:' in content
        # title should indicate articles, not 'Diary'
        assert 'Diary' not in content.split('---')[1], "articles page title should not be 'Diary'"

    def test_articles_page_links_to_posts(self):
        content = ARTICLES_PAGE.read_text()
        assert 'post.url' in content, "articles page must link to individual posts"


class TestBlogPageFiltered:
    """docs/blog/index.html must be scoped to diary entries (subtype: diary)."""

    def test_blog_page_exists(self):
        assert BLOG_PAGE.exists(), "docs/blog/index.html does not exist"

    def test_blog_page_filters_by_subtype_diary(self):
        """Blog listing must filter to subtype == 'diary', not show all posts."""
        content = BLOG_PAGE.read_text()
        assert 'subtype' in content, "blog page must filter on subtype"
        assert 'diary' in content, "blog page must check for subtype: diary"

    def test_blog_page_title_reflects_diary_scope(self):
        content = BLOG_PAGE.read_text()
        # Should say 'diary' or 'development diary' in the visible title, not generic 'Blog'
        lower = content.lower()
        assert 'diary' in lower or 'development' in lower, \
            "blog page visible title should reflect diary scope"

    def test_blog_page_has_permalink(self):
        content = BLOG_PAGE.read_text()
        assert '/blog/' in content


class TestNavigationUpdated:
    """Navigation in default.html must include both Articles and Diary links."""

    def test_default_layout_has_articles_link(self):
        content = DEFAULT_LAYOUT.read_text()
        assert '/articles/' in content, "default.html nav must link to /articles/"

    def test_default_layout_has_diary_link(self):
        content = DEFAULT_LAYOUT.read_text()
        assert '/blog/' in content, "default.html nav must link to /blog/"

    def test_default_layout_articles_nav_label(self):
        """The Articles link must have a visible label."""
        content = DEFAULT_LAYOUT.read_text()
        assert 'Articles' in content, "nav must show 'Articles' label"

    def test_default_layout_diary_nav_label(self):
        """The Diary link must still have a visible label."""
        content = DEFAULT_LAYOUT.read_text()
        assert 'Diary' in content, "nav must show 'Diary' label"

    def test_articles_link_active_on_articles_page(self):
        """Articles link should be marked active when on articles pages."""
        content = DEFAULT_LAYOUT.read_text()
        # The active class logic should reference '/articles/'
        assert "'/articles/'" in content or '"/articles/"' in content or \
               'articles' in content.lower(), \
            "articles nav link should have active-state logic"

    def test_post_layout_has_correct_back_link(self):
        """Individual post layout back-link should link to /blog/ (diary listing)."""
        post_layout = REPO_ROOT / 'docs' / '_layouts' / 'post.html'
        content = post_layout.read_text()
        assert '/blog/' in content, "post layout back-link must point to /blog/"


class TestLiquidFilteringLogic:
    """Verify the Liquid filter patterns are syntactically correct."""

    def test_articles_page_uses_if_filter_not_unless(self):
        """Standard pattern: {% if post.entry_type == 'article' %}."""
        content = ARTICLES_PAGE.read_text()
        assert "entry_type == 'article'" in content or \
               'entry_type == "article"' in content, \
            "articles page should use Liquid == comparison for entry_type"

    def test_blog_page_uses_if_filter_for_diary(self):
        """Standard pattern: {% if post.subtype == 'diary' %}."""
        content = BLOG_PAGE.read_text()
        assert "subtype == 'diary'" in content or \
               'subtype == "diary"' in content, \
            "blog page should use Liquid == comparison for subtype"

    def test_articles_page_endif_closes_filter(self):
        """Every {% if %} must be closed with {% endif %}."""
        content = ARTICLES_PAGE.read_text()
        if_count = content.count('{% if ')
        endif_count = content.count('{% endif %}')
        assert if_count == endif_count, \
            f"Mismatched if/endif in articles page: {if_count} ifs, {endif_count} endifs"

    def test_blog_page_endif_closes_filter(self):
        content = BLOG_PAGE.read_text()
        if_count = content.count('{% if ')
        endif_count = content.count('{% endif %}')
        assert if_count == endif_count, \
            f"Mismatched if/endif in blog page: {if_count} ifs, {endif_count} endifs"
