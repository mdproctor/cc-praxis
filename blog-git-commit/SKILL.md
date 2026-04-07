---
name: blog-git-commit
description: >
  Use when committing changes to a type: blog repository (GitHub Pages /
  Jekyll). Invoked automatically by git-commit for type: blog, or directly
  via /blog-git-commit. Applies blog-specific commit conventions.
---

# Blog Git Commit

Conventional commit workflow for GitHub Pages / Jekyll blog repositories.

## Commit Conventions

Blog commits adapt Conventional Commits for content, not code:

```
<type>[optional scope]: <description>

[optional body — abstract or summary of the post/change]
```

### Types

| Type | When to use |
|------|-------------|
| `post` | New blog post added to `_posts/` |
| `edit` | Update to an existing published post |
| `draft` | Work-in-progress post (not yet published) |
| `asset` | Images, CSS, JS, or other non-post files |
| `config` | `_config.yml`, layouts, includes, Gemfile changes |

**Never use code commit types** (`feat`, `fix`, `refactor`, `docs`, `chore`, etc.) — they don't map to blog content.

### Scopes (optional)

Use the topic area when it adds value for filtering history:
`post(java)`, `edit(mcp)`, `draft(quarkus)`, `asset(claude-code)`, `config`

### Subject length

Max **72 chars** (not 50 — blog titles are naturally longer).

### No imperative mood

Blog titles are descriptive, not commands. "Add guide to X" is fine; so is "Why X matters" or "Getting started with X".

### No trailing period

Titles don't end with `.` — `?` is fine for question-form titles.

### Body

Use the body for an abstract or brief summary of what the post covers. Especially useful for `post` and `edit` types.

## Workflow

### Step 0b — Offer issue tracking (when absent)

Check if CLAUDE.md already has Work Tracking configured:
```bash
grep -q "Issue tracking.*enabled" CLAUDE.md 2>/dev/null && echo "exists" || echo "absent"
```

**If absent**, ask:

> **Enable GitHub issue tracking for this repo? (YES / n)**
>
> Enables automatic behaviours:
> - Flag tasks that span multiple concerns and help break them into issues before starting
> - Check staged changes for commit splits before committing
> - All commits reference a GitHub issue, so release notes generate cleanly
>
> Default: **YES** — press Enter to enable, type **n** to skip.

If **YES** or Enter → invoke the `issue-workflow` skill in Setup mode before continuing.
If **n** → continue immediately. Do not ask again this session.

---

### Step 1 — Inspect staged changes

```bash
git diff --staged --stat
git diff --staged --name-only
```

If nothing staged, stop and ask the user to stage files first.

### Step 2 — Detect commit type from staged files

| Staged files | Suggested type |
|---|---|
| New `_posts/YYYY-MM-DD-*.md` | `post` |
| Modified `_posts/YYYY-MM-DD-*.md` | `edit` |
| New/modified `_drafts/*.md` or `*.md` without date prefix | `draft` |
| `assets/`, images, `.css`, `.js` | `asset` |
| `_config.yml`, `_layouts/`, `_includes/`, `Gemfile` | `config` |
| Mixed types | Ask user which type best describes the primary change |

### Step 3 — Infer scope from post front matter

If a post is staged, check its front matter for `categories` or `tags`:

```yaml
---
categories: [java, claude-code]
tags: [mcp, refactoring]
---
```

Suggest the primary category as scope (e.g., `post(java)`). If no clear primary, omit scope.

### Step 4 — Validate post filename (for `post` and `draft` types)

Post filenames must follow: `YYYY-MM-DD-title-with-hyphens.md`

If a staged `.md` file in `_posts/` doesn't match this pattern:
> ⚠️ Post filename doesn't follow Jekyll convention: `{filename}`
> Expected: `YYYY-MM-DD-title-with-hyphens.md`
> Fix the filename before committing.

Stop workflow until fixed.

### Step 5 — Draft commit message

Generate a message following the conventions above. Hold it — don't show yet.

### Step 6 — Validate message

Run the validator:

```bash
python scripts/validation/validate_blog_commit.py <<< "<proposed message>"
```

If validation fails, adjust the message to fix all errors before proceeding.

### Step 7 — Present proposal

```
## Staged files
<git diff --staged --stat output>

## Proposed commit message
<type>[scope]: <description>

<body if any>

Does this look good? Reply YES to commit, or tell me what to adjust.
```

### Step 8 — Commit (only after explicit YES)

```bash
git commit -m "<subject>" -m "<body if any>"
git log --oneline -1
```

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Using `feat` or `docs` | Code types don't describe content | Use `post`, `edit`, `draft`, `asset`, or `config` |
| Subject > 72 chars | Too long | Shorten the description; details go in the body |
| Trailing period | Convention violation | Remove the `.` |
| No blank line before body | Malformed message | Add empty line between subject and body |
| Empty scope `()` | Ambiguous | Use `post(java)` or omit scope entirely `post:` |
| Committing post with wrong filename | Jekyll won't publish it | Rename to `YYYY-MM-DD-title.md` first |
| Missing date prefix on post | Jekyll ignores the file | Add date prefix before staging |

## Success Criteria

Commit is complete when:

- ✅ Staged files inspected and type correctly identified
- ✅ Post filenames validated (for post/draft types)
- ✅ Commit message passes `validate_blog_commit.py`
- ✅ User confirmed with explicit **YES**
- ✅ Commit executed and confirmed in `git log --oneline -1`

## Skill Chaining

**Invoked by:** `git-commit` when `type: blog` declared in CLAUDE.md, or directly via `/blog-git-commit`

**Invokes:** `update-claude-md` if CLAUDE.md exists and workflow/convention changes detected
