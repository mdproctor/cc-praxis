# git-commit — Project Type Setup

Referenced by `git-commit/SKILL.md` Step 0 when CLAUDE.md is missing or has no Project Type.
Contains the full interactive setup flow for each project type.

---

## If 1 (skills)

Create or update CLAUDE.md:
```markdown
## Commit Messages

**NEVER add AI attribution to commit messages** (no `Co-Authored-By: Claude`, no `Generated-by:`, no AI mentions) unless the user explicitly requests it for a specific commit. Commit messages describe WHAT changed and WHY only.

## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.

## Project Type

**Type:** skills
```

Stage CLAUDE.md:
```bash
git add CLAUDE.md
```

Tell user:
> ✅ Created CLAUDE.md with type: skills
>
> This enables:
> - Automatic SKILL.md validation (skill-validation.md workflow)
> - README.md synchronization (readme-sync.md workflow)
> - CLAUDE.md synchronization (update-claude-md)
>
> Note: I've staged CLAUDE.md - it will be included in this commit.
>
> Proceeding with your commit...

Continue to Step 1.

---

## If 2 (java)

Create or update CLAUDE.md:
```markdown
## Commit Messages

**NEVER add AI attribution to commit messages** (no `Co-Authored-By: Claude`, no `Generated-by:`, no AI mentions) unless the user explicitly requests it for a specific commit. Commit messages describe WHAT changed and WHY only.

## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.

## Project Type

**Type:** java
```

Stage CLAUDE.md, then tell user:
> ✅ Created CLAUDE.md with type: java
>
> This is a Java project. For best results, please use `java-git-commit`
> instead of `git-commit`. It provides:
> - DESIGN.md synchronization
> - Java-specific code review
> - Java-specific commit scopes
>
> Would you like me to:
> 1. Continue with basic commit (not recommended for Java)
> 2. Switch to java-git-commit (recommended)
>
> Reply with 1 or 2.

Wait for response. If 2, stop and tell user to invoke java-git-commit.
If 1, continue to Step 1 (but warn about missing DESIGN.md sync).

---

## If 3 (blog)

Create or update CLAUDE.md:
```markdown
## Commit Messages

**NEVER add AI attribution to commit messages** (no `Co-Authored-By: Claude`, no `Generated-by:`, no AI mentions) unless the user explicitly requests it for a specific commit. Commit messages describe WHAT changed and WHY only.

## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.

## Project Type

**Type:** blog
```

Stage CLAUDE.md, then tell user:
> ✅ Created CLAUDE.md with type: blog
>
> This enables GitHub Pages blog conventions:
> - Post filename validation (`YYYY-MM-DD-title.md`)
> - Jekyll-aware commits
>
> Note: A primary sync document (e.g. an index or archive page) can be
> configured later when you know what it will be.
>
> Proceeding with your commit...

Continue to Step 1.

---

## If 4 (custom)

Prompt for configuration:
> Great! Custom projects need a bit more configuration.
>
> **What's your primary document?** (The main document that should stay
> synchronized with changes)
>
> Examples:
> - `docs/vision.md` (working groups)
> - `THESIS.md` (research)
> - `docs/api-design.md` (API docs)
>
> Enter the path:

Wait for response (get primary_doc_path).

> **What's your current milestone?** (e.g., "Phase 1 - Discovery",
> "Chapter 3 - Methodology", "Version 2.1.0")
>
> Enter milestone name:

Wait for response (get milestone).

Create CLAUDE.md:
```markdown
## Commit Messages

**NEVER add AI attribution to commit messages** (no `Co-Authored-By: Claude`, no `Generated-by:`, no AI mentions) unless the user explicitly requests it for a specific commit. Commit messages describe WHAT changed and WHY only.

## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.

## Project Type

**Type:** custom
**Primary Document:** {primary_doc_path}

**Sync Strategy:** bidirectional-consistency

**Sync Rules:**
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| [Add your rules here] | [Section name] | [What to update] |

**Consistency Checks:**
- [Add your checks here]

**Current Milestone:** {milestone}
```

Stage CLAUDE.md, then tell user:
> ✅ Created CLAUDE.md with type: custom
>
> I've added a template Sync Rules table. You'll need to fill this in to
> enable automatic document synchronization.
>
> For now, I'll proceed with basic commit without auto-sync. You can
> configure sync rules anytime by editing CLAUDE.md.
>
> Would you like to:
> 1. Continue with basic commit now
> 2. Edit CLAUDE.md to add sync rules first
>
> Reply with 1 or 2.

If 1, continue to Step 1. If 2, stop and let user edit.

---

## If 5 (generic)

Create or update CLAUDE.md:
```markdown
## Commit Messages

**NEVER add AI attribution to commit messages** (no `Co-Authored-By: Claude`, no `Generated-by:`, no AI mentions) unless the user explicitly requests it for a specific commit. Commit messages describe WHAT changed and WHY only.

## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.

## Project Type

**Type:** generic
```

Stage CLAUDE.md, then tell user:
> ✅ Created CLAUDE.md with type: generic
>
> This enables basic conventional commits with optional CLAUDE.md sync.
>
> Note: I've staged CLAUDE.md - it will be included in this commit.
>
> Proceeding with your commit...

Continue to Step 1.
