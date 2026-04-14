import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validation.validate_blog_frontmatter import validate_blog_entry_frontmatter


def test_valid_diary_entry():
    frontmatter = {
        'layout': 'post',
        'title': 'Test Entry',
        'date': '2026-04-14',
        'type': 'phase-update',
        'entry_type': 'note',
        'subtype': 'diary',
        'projects': ['cc-praxis'],
    }
    assert validate_blog_entry_frontmatter(frontmatter) == []


def test_valid_article():
    frontmatter = {
        'layout': 'post',
        'title': 'Test Article',
        'date': '2026-04-14',
        'entry_type': 'article',
        'projects': ['cc-praxis'],
        'tags': ['quarkus'],
    }
    assert validate_blog_entry_frontmatter(frontmatter) == []


def test_article_with_multiple_projects():
    frontmatter = {
        'layout': 'post',
        'title': 'Test Article',
        'date': '2026-04-14',
        'entry_type': 'article',
        'projects': ['cc-praxis', 'quarkus-flow'],
        'tags': ['quarkus', 'skills'],
    }
    assert validate_blog_entry_frontmatter(frontmatter) == []


def test_tags_optional():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'article',
        'projects': ['cc-praxis'],
    }
    assert validate_blog_entry_frontmatter(frontmatter) == []


def test_missing_entry_type():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'type': 'phase-update',
        'projects': ['cc-praxis'],
    }
    errors = validate_blog_entry_frontmatter(frontmatter)
    assert any('entry_type' in e for e in errors)


def test_invalid_entry_type():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'diary',  # wrong — diary is a subtype, not an entry_type
        'projects': ['cc-praxis'],
    }
    errors = validate_blog_entry_frontmatter(frontmatter)
    assert any('entry_type' in e for e in errors)


def test_missing_projects():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'note',
        'subtype': 'diary',
    }
    errors = validate_blog_entry_frontmatter(frontmatter)
    assert any('projects' in e for e in errors)


def test_empty_projects():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'note',
        'subtype': 'diary',
        'projects': [],
    }
    errors = validate_blog_entry_frontmatter(frontmatter)
    assert any('projects' in e for e in errors)


def test_projects_not_a_list():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'note',
        'subtype': 'diary',
        'projects': 'cc-praxis',  # should be a list
    }
    errors = validate_blog_entry_frontmatter(frontmatter)
    assert any('projects' in e for e in errors)


def test_note_missing_subtype():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'note',
        'projects': ['cc-praxis'],
    }
    errors = validate_blog_entry_frontmatter(frontmatter)
    assert any('subtype' in e for e in errors)


def test_article_no_subtype_required():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'article',
        'projects': ['cc-praxis'],
    }
    assert validate_blog_entry_frontmatter(frontmatter) == []


def test_tags_must_be_list():
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'article',
        'projects': ['cc-praxis'],
        'tags': 'quarkus',  # should be a list
    }
    errors = validate_blog_entry_frontmatter(frontmatter)
    assert any('tags' in e for e in errors)


def test_article_no_type_field_required():
    """Articles don't need the narrative 'type' field (day-zero, phase-update, etc.)"""
    frontmatter = {
        'layout': 'post',
        'title': 'Test',
        'date': '2026-04-14',
        'entry_type': 'article',
        'projects': ['cc-praxis'],
    }
    assert validate_blog_entry_frontmatter(frontmatter) == []
