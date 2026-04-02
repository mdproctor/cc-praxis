# blog-project-health — Design Document

**Status:** Design phase — not yet implemented as a skill
**Skill name (planned):** `blog-project-health`
**Slash command (planned):** `/blog-project-health`
**Invoked by:** [`project-health`](project-health.md) when `type: blog` declared in CLAUDE.md

This document tracks the blog-specific health checks that augment the universal checks in `project-health`.

---

## Purpose

Runs after `project-health` completes its universal checks. Adds GitHub Pages / Jekyll-specific correctness and refinement checks that only make sense for blog projects.

Follows the same pattern as `blog-git-commit` extending `git-commit`.

---

## Prerequisite

**This skill builds on [`project-health`](project-health.md).** When invoked directly (e.g. `/blog-project-health`), it runs all universal checks first then its own additions — identical output to `project-health` auto-chaining to this skill. Either entry point produces the same result.

---

## Augmentations to Universal Checks

These extend the universal categories with blog-specific items:

| Universal check | Quality additions | Refinement additions |
|----------------|------------------|---------------------|
| `primary-doc` | All posts in `_posts/` follow `YYYY-MM-DD-title.md` filename convention; Jekyll front matter valid on all posts | Could post metadata (categories, tags) be standardised for better navigation and filtering? |
| `artifacts` | `_posts/` directory exists; `_config.yml` present; `_layouts/` and `_includes/` present if referenced | Is `_config.yml` lean, or has it accumulated unused config? |
| `conventions` | Jekyll conventions documented in CLAUDE.md; blog commit types valid (post/edit/draft/asset/config); 72-char subject limit enforced | Could commit type guidance be expressed more briefly? |
| `framework` | Jekyll Liquid syntax correct in layouts/includes; no deprecated Jekyll features; front matter schema matches `_config.yml` | Could layout templates be simplified or better composed? |

---

## Blog-Specific Categories

These categories only exist for blog projects and are not present in `project-health`:

### `blog-content` — Content Quality & Consistency

**Quality** — Is the blog content consistent and correct?
- [ ] All posts have required front matter (title, date, layout at minimum)
- [ ] Post dates in front matter match filename dates
- [ ] No broken internal links between posts
- [ ] No images referenced that don't exist in `assets/` or equivalent
- [ ] Draft posts are in `_drafts/` not `_posts/` (unless intentionally published)
- [ ] No post uses hardcoded relative links to other posts by date/title (would break on rename)
- [ ] Archive pages (yearly/monthly) only exist for periods where posts actually exist

**Refinement** — Could content organisation be better?
- [ ] Are posts consistently categorised and tagged?
- [ ] Are there categories with only one post that could be merged with related ones?
- [ ] Could a series of related posts be better linked to each other?

### `blog-structure` — Site Structure

**Quality** — Is the Jekyll site structure correct?
- [ ] All layouts referenced in front matter exist in `_layouts/`
- [ ] All includes referenced in layouts exist in `_includes/`
- [ ] No orphaned layout or include files
- [ ] Pagination configured correctly if enabled

**Refinement** — Could the site structure be cleaner?
- [ ] Are there layouts that are nearly identical and could be merged with parameters?
- [ ] Could include files be better named or better organised?
- [ ] Are there images in `assets/` that are no longer referenced by any post or layout?
- [ ] Are there CSS or JavaScript files in `assets/` that are no longer used?

---

## Output Format

Same severity rating as `project-health`, prefixed with `[blog]`:

```
### HIGH (should fix)
- [blog][primary-doc] _posts/2026-01-15-intro.md: front matter missing 'layout' field
- [blog][blog-content] assets/images/diagram.png referenced in post but file does not exist

### LOW (nice to fix)
- [blog][blog-structure] _layouts/wide.html and _layouts/full.html are nearly identical
```
