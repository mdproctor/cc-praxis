---
name: blog-project-health
description: >
  Use when health-checking a type: blog (GitHub Pages / Jekyll) project,
  or when invoked automatically by project-health on blog project type detection.
---

# blog-project-health

Health checks for GitHub Pages / Jekyll blog projects. Runs all universal
checks from `project-health` first, then adds blog-specific checks for Jekyll
structure, post conventions, content quality, and site integrity.

## Prerequisites

**This skill builds on `project-health`.** Apply all universal checks first:

- All universal categories: `docs-sync`, `consistency`, `logic`, `config`,
  `security`, `release`, `user-journey`, `git`, `primary-doc`, `artifacts`,
  `conventions`, `framework`
- Same tier system (1-4) and named aliases (`--commit`, `--standard`,
  `--prerelease`, `--deep`)
- Same output format — blog-specific findings are prefixed with `[blog]`

When invoked directly (`/blog-project-health`), run universal checks first,
then blog-specific checks. Output is combined — identical to `project-health`
auto-chaining here.

---

## Tier System

Inherited from `project-health` — see [check-categories.md](../project-health/check-categories.md#tier-system).
Blog-specific categories (`blog-content`, `blog-structure`) run at tier 3+.

---

## Type-Specific Scan Targets

In addition to the universal document scan, include:

- `_config.yml` — Jekyll site configuration
- `_posts/` — all post files (recursive)
- `_drafts/` — draft post files
- `_layouts/` — layout templates
- `_includes/` — reusable includes
- `assets/` — images, CSS, JavaScript

---

## Augmentations to Universal Checks

These extend universal categories with blog-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] All posts in `_posts/` follow `YYYY-MM-DD-title.md` filename convention
- [ ] Jekyll front matter is valid on all posts (parseable YAML)

**Refinement (tier 4):**
- [ ] Could post metadata (categories, tags) be standardised for better navigation?

### `artifacts` augmentations

**Quality:**
- [ ] `_posts/` directory exists
- [ ] `_config.yml` is present
- [ ] `_layouts/` and `_includes/` directories exist if referenced by any post or config

**Refinement (tier 4):**
- [ ] Is `_config.yml` lean, or has it accumulated unused config?

### `conventions` augmentations

**Quality:**
- [ ] Jekyll conventions are documented in CLAUDE.md
- [ ] Blog commit types are valid (post/edit/draft/asset/config) — see `blog-git-commit`
- [ ] Commit subject line 72-char limit enforced (blog convention)

**Refinement (tier 4):**
- [ ] Could commit type guidance be expressed more briefly in CLAUDE.md?

### `framework` augmentations

**Quality:**
- [ ] Jekyll Liquid syntax is correct in `_layouts/` and `_includes/` files
- [ ] No deprecated Jekyll features used (e.g. `pygments`, removed `permalink` formats)
- [ ] Front matter schema in posts matches fields defined or expected by `_config.yml`

**Refinement (tier 4):**
- [ ] Could layout templates be simplified or better composed?

---

## Blog-Specific Categories

These categories are only checked for type: blog projects (tier 3+).

### `blog-content` — Content Quality and Consistency

**Quality** — Is blog content consistent and correct?
- [ ] All posts have required front matter (title, date, layout at minimum)
- [ ] Post dates in front matter match filename dates
- [ ] No broken internal links between posts (posts referencing other posts by path)
- [ ] No images referenced in posts that don't exist in `assets/` or equivalent
- [ ] Draft posts are in `_drafts/` not `_posts/` (unless intentionally published)
- [ ] No post uses hardcoded relative links to other posts by date/title (breaks on rename)
- [ ] Archive pages (yearly/monthly) only exist for periods where posts actually exist

**Refinement (tier 4):**
- [ ] Are posts consistently categorised and tagged?
- [ ] Are there categories with only one post that could be merged with related ones?
- [ ] Could a series of related posts be better linked to each other?

### `blog-structure` — Site Structure

**Quality** — Is the Jekyll site structure correct?
- [ ] All layouts referenced in front matter exist in `_layouts/`
- [ ] All includes referenced in layouts exist in `_includes/`
- [ ] No orphaned layout or include files (defined but never referenced)
- [ ] Pagination configured correctly if enabled in `_config.yml`

**Refinement (tier 4):**
- [ ] Are there layouts that are nearly identical and could be merged with parameters?
- [ ] Could include files be better named or better organised?
- [ ] Are there images in `assets/` no longer referenced by any post or layout?
- [ ] Are there CSS or JavaScript files in `assets/` that are no longer used?

---

## Output Format

Universal findings appear without a prefix. Blog-specific findings use `[blog]`:

```
## project-health report — blog-content, blog-structure, primary-doc [augmented]

### HIGH (should fix)
- [blog][primary-doc] _posts/2026-01-15-intro.md: front matter missing 'layout' field
- [blog][blog-content] assets/images/diagram.png referenced in post but file does not exist

### MEDIUM (worth fixing)
- [blog][conventions] CLAUDE.md does not document blog commit type conventions

### LOW (nice to fix)
- [blog][blog-structure] _layouts/wide.html and _layouts/full.html are nearly identical

### PASS
✅ docs-sync, consistency, security, git
```

Severity scale: see [check-categories.md](../project-health/check-categories.md#severity-scale).

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Blog-specific checks don't replace universal ones | Always run universal checks first (prerequisite) |
| Checking only `_posts/` root | Posts can be in subdirectories | Scan `_posts/` recursively |
| Treating draft in `_posts/` as error | May be intentionally published | Check `published: false` front matter before flagging |
| Flagging every unused asset | Images may be used by external links or layouts | Check layouts AND posts before calling an asset orphaned |
| Reporting Liquid errors without context | Template errors cascade | Report the root file first, note secondary effects separately |

---

## Skill Chaining

**Invoked by:** `project-health` automatically when `type: blog` detected in CLAUDE.md

**Can be invoked directly:** Yes — `/blog-project-health` runs universal checks first, then blog-specific checks, producing identical output to the auto-chained flow

**Prerequisite for:** Nothing currently chains from this skill

**Related skills:**
- `blog-git-commit` — commit conventions this skill validates (conventions category)
- `project-health` — universal prerequisite foundation
