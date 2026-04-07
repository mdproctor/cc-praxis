---
name: git-commit
description: >
  Use when user wants to create a commit NOW - says "commit this", "commit
  these changes", "create a commit", or invokes /git-commit. Does NOT
  apply to discussions about past commits or questions about whether to commit.
---

# Git Commit Helper

You are an expert in creating clean, conventional Git commits following the
Conventional Commits 1.0.0 specification.

## ⛔ ABSOLUTE RULE — NO EXCEPTIONS

**NEVER add AI attribution to commit messages unless the user explicitly asks for it in that specific commit.**

This means NO:
- `Co-Authored-By: Claude`
- `Generated-by:` anything
- `AI-assisted:` anything
- Any mention of Claude, AI, LLMs, or tooling in the commit message

Commit messages describe **WHAT changed and WHY**. Not who or what wrote them. This rule cannot be overridden by any other instruction in this skill.

---

## Core Rules

- Follow the **Conventional Commits 1.0.0 specification**.
- Subject line: imperative mood, max 50 chars, no trailing period.
- Never run `git commit` until the user has explicitly confirmed.

## Workflow

### Step 0 — Verify or Setup Project Type

**Read CLAUDE.md for project type:**
```bash
cat CLAUDE.md 2>/dev/null | grep -A 2 "## Project Type"
```

**If CLAUDE.md exists and has Project Type declaration:**

Extract the type (skills | java | blog | custom | generic).

**Route based on type:**
- **type: skills** → Continue with Step 1 (this skill handles skills repos)
- **type: java** → STOP and tell user:
  > This is a type: java project. Please use `java-git-commit` instead:
  > `/java-git-commit` or say "java commit"

- **type: blog** → STOP and tell user:
  > This is a type: blog project. Please use `blog-git-commit` instead:
  > `/blog-git-commit` or say "blog commit"

- **type: custom** → STOP and tell user:
  > This is a type: custom project. Please use `custom-git-commit` instead:
  > `/custom-git-commit` or say "custom commit"

- **type: generic** → Continue with Step 1 (this skill handles generic repos)

**If CLAUDE.md missing or no Project Type section:**

Interactively set up project type:

> I notice this repository doesn't have a Project Type declared in CLAUDE.md.
> Let me help you set this up - it only takes a moment.
>
> **What kind of project is this?**
>
> 1. **Skills repository** - Claude Code skills (has */SKILL.md files)
> 2. **Java project** - Maven/Gradle (has pom.xml or build.gradle)
> 3. **Blog** - GitHub Pages blog (Jekyll, date-prefixed posts)
> 4. **Custom project** - Working groups, research, docs, etc.
> 5. **Generic project** - No special handling needed
>
> Reply with the number (1-5) or type the name.

Wait for user response.

**For the full per-type CLAUDE.md creation dialogs**, read **[project-type-setup.md](project-type-setup.md)** and follow the instructions for the user's chosen type, then continue to Step 1.

---

### Step 0b — Offer issue tracking (when absent)

Check if CLAUDE.md already has Work Tracking configured:
```bash
grep -q "Issue tracking.*enabled" CLAUDE.md 2>/dev/null && echo "exists" || echo "absent"
```

**If absent** (whether CLAUDE.md is freshly created or already exists), ask:

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
git diff --staged
```

If nothing is staged, stop and tell the user:
> "Nothing is staged. Run `git add <files>` first, or tell me which files
> to stage."

### Step 1a — Review skills (if SKILL.md changes)

Check if any SKILL.md files are staged:
```bash
git diff --staged --name-only | grep 'SKILL.md$'
```

**If SKILL.md files found:**
- Follow the `skill-validation.md` workflow to validate structure and conventions
- If CRITICAL findings exist → stop and ask user to fix before continuing
- If only WARNING/NOTE findings → hold them, continue to Step 2

**If no SKILL.md files:**
- Skip to Step 1c

### Step 1c — Validate documentation files

Check for staged .md files (excluding SKILL.md which was validated in Step 1a):
```bash
git diff --staged --name-only | grep '\.md$' | grep -v 'SKILL\.md$'
```

**For each .md file found:**
```bash
python scripts/validate_document.py <file>
```

**Handle validation results:**
- **Exit code 1 (CRITICAL issues):**
  - BLOCK commit
  - Show issues to user
  - Ask user to fix corruption manually
  - Stop workflow
- **Exit code 2 (WARNING issues):**
  - Show warnings to user
  - Ask if they want to proceed anyway
  - If NO → stop workflow
  - If YES → continue to Step 2
- **Exit code 0 (no issues):**
  - Continue to Step 2

**This step runs for ALL project types** (skills, java, blog, custom, generic).

**If no .md files found:**
- Continue to Step 2

### Step 2 — Issue linking and commit split check (if Work Tracking enabled)

Check if Work Tracking is configured:
```bash
grep -q "Issue tracking.*enabled" CLAUDE.md 2>/dev/null && echo "enabled" || echo "disabled"
```

**If enabled:**

**2a — Check for commit split candidates**

Invoke the `issue-workflow` skill's pre-commit analysis on the staged diff.
If it detects changes spanning multiple concerns, surface the split suggestion
and wait for the user's response before continuing.

**2b — Link to an issue**

```bash
gh issue list --state open --limit 15
```

Check if any open issue title obviously matches the staged changes. If yes:
> This looks like it relates to **#{N}: {title}** — correct?
> (YES · NO — show full list)

If no obvious match, show the list and ask the user to select or create one.
Once an issue is confirmed, include it in the commit:
- Work in progress: append `Refs #{N}` to the commit body
- Completing the issue: append `Closes #{N}` to the commit body

**If not enabled or user has no `gh` CLI:**

Skip this step entirely — no issue linking required.

---

### Step 3 — Generate commit message

Analyze the staged changes and draft one conventional commit message (see **[commit-format.md](commit-format.md)**).

Hold it — don't show it yet.

### Step 4 — Sync CLAUDE.md (if exists)

Check if CLAUDE.md exists:
```bash
ls CLAUDE.md 2>/dev/null
```

**If CLAUDE.md exists:**
- Invoke the `update-claude-md` skill, passing the staged diff
- It will analyze workflow/convention changes and propose CLAUDE.md updates
- Hold those proposals too

**If CLAUDE.md doesn't exist:**
- Skip to Step 5

### Step 5 — Sync README.md (if skills repo)

Check if README.md exists and skill changes detected:
```bash
ls README.md 2>/dev/null && git diff --staged --name-only | grep -E '(SKILL\.md|^[^/]+/$)'
```

**If README.md exists and skill changes found:**
- **MANDATORY:** Follow the `readme-sync.md` workflow, passing the staged diff
- **Do NOT skip this step** — let readme-sync.md decide if changes warrant documentation
- **Do NOT rationalize** "just internal changes" or "not significant enough"
- It will analyze skill collection changes and propose README.md updates
- Hold those proposals too

**If README.md doesn't exist or no skill changes:**
- Skip to Step 6 (present proposal)

### Step 6 — Present proposal

**If skill validation, CLAUDE.md, or README.md updates proposed**, show consolidated proposal:
```
## Staged files
<output of git diff --staged --stat>

## Skill review findings (if any)
<output from skill-validation.md workflow>

## Proposed commit message
<type>[optional scope]: <description>

<optional body>

<optional footer>

## Proposed CLAUDE.md updates (if any)
<output from update-claude-md skill>

## Proposed README.md updates (if any)
<output from readme-sync.md workflow>
```

**Otherwise**, show standard proposal:
```
## Staged files
<output of git diff --staged --stat>

## Proposed commit message
<type>[optional scope]: <description>

<optional body>

<optional footer>
```

Then ask exactly:
> "Does this look good? Reply **YES** to commit, or tell me what to adjust."

### Step 7 — Commit (only after explicit YES)

**If documentation updates were proposed**, run in this exact order:
1. Let update-claude-md apply its changes (if proposed)
2. Apply README.md changes per readme-sync.md workflow (if proposed)
3. Stage updated files: `git add CLAUDE.md README.md` (only files that were changed)
4. Commit with the confirmed message:
```bash
git commit -m "<subject>" -m "<body if any>"
```
5. Confirm success:
```bash
git log --oneline -1
```

**If no documentation updates**, run in this exact order:
1. Commit with the confirmed message:
```bash
git commit -m "<subject>" -m "<body if any>"
```
2. Confirm success:
```bash
git log --oneline -1
```

### Step 8 — Handle edge cases

| Situation | Action |
|---|---|
| Nothing staged | Stop at step 1, prompt user to stage files |
| Merge conflict markers in diff | Warn before proceeding |
| Large diff (10+ files) | Summarize by module/category rather than file-by-file |

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Adding AI attribution (Co-Authored-By, Generated-by, etc.) | Violates Core Rules; user didn't ask for it | Never add attribution unless user explicitly requests |
| Committing before user confirms | User loses control | Always show proposal and wait for YES |
| Subject line > 50 chars | Truncated in git log | Keep under 50, use body for details |
| Subject ends with period | Not conventional commits standard | Remove trailing period |
| Using past tense ("Added X") | Not imperative mood (wrong mental model for git revert/cherry-pick) | Use "Add X" (command form) |
| Type `chore` for production code | Wrong semantics | Use `feat`, `fix`, or `refactor` |
| Wrong type (`refactor` for bug fix) | Misleading git history | `fix` if it was wrong, `refactor` if working |
| Vague scope (`(skills)`, `(stuff)`) | Unclear what changed, hard to search history | Use specific component name or omit scope entirely |
| Wrong scope level (too broad/narrow) | Misleading - doesn't match actual change scope | Choose primary affected component, omit if 5+ components |
| Inconsistent scope names | Hard to track changes across commits | Stick to established component names in the repo |
| No body for complex changes | Reviewers lack context | Add why/what in body (not how) |
| Committing merge conflict markers | Broken code in history | Check diff for `<<<<<<<` markers first |
| Forgetting BREAKING CHANGE footer | Hidden breaking changes | Add footer with `!` in type/scope |
| Running commit without staged changes | Wastes time | Check `git status` first |

## Success Criteria

Commit is complete when:

- ✅ All files staged (or user confirmed which files to stage)
- ✅ Commit message generated and presented to user
- ✅ Documentation updates applied (if CLAUDE.md, README.md, or skill review needed)
- ✅ User confirmed with explicit **YES**
- ✅ Commit executed successfully
- ✅ `git log --oneline -1` confirms commit exists

**Not complete until** all criteria met and commit confirmed in git log.

## Skill Chaining

**Invoked by:** User says "commit", "make a commit", or invokes `/git-commit`

**Routes to specialized skills based on CLAUDE.md declaration:**
- type: java → Redirects to `java-git-commit`
- type: custom → Redirects to `custom-git-commit`
- type: skills → Handles directly (this skill)
- type: generic → Handles directly (this skill)

**Invokes (when handling directly):**
- Follows `skill-validation.md` workflow for SKILL.md validation (automatic if SKILL.md files staged, type: skills only)
- [`update-claude-md`] for workflow sync (automatic if CLAUDE.md exists)
- Follows `readme-sync.md` workflow for skill collection sync (automatic if README.md exists and skill changes detected, type: skills only)

**Interactive setup:** If CLAUDE.md missing or no Project Type declared, guides user through setup and creates CLAUDE.md

**Can be invoked independently:** Yes, this is the entry point for all commit workflows. It reads project type and routes accordingly.

## Message Format

See **[commit-format.md](commit-format.md)** for the full format spec, types table, scope guidance, and real scope decision examples.

## Examples

See **[commit-examples.md](commit-examples.md)** for concrete examples of well-formed commits across all common scenarios.
