---
name: issue-workflow
description: >
  Use when setting up GitHub issue tracking, when a user request spans
  multiple concerns that should be separate issues, or when staged changes
  span multiple issues and should be split. Also invoked by git-commit
  during CLAUDE.md setup, and automatically when Work Tracking is enabled.
---

# Issue Workflow

Helps teams work against GitHub issues cleanly: detecting when tasks are too
broad, suggesting commit splits when staged changes span multiple concerns,
and managing GitHub releases as the changelog.

## When This Skill Is Invoked

| Context | Trigger | What it does |
|---------|---------|--------------|
| `/issue-workflow` | User calls directly | Setup mode — configure issue tracking in CLAUDE.md |
| New project setup | `git-commit` Step 0 chains here | Setup mode — optional offer during CLAUDE.md creation |
| User makes a request | CLAUDE.md instructs Claude to check | Task intake — detect if request spans multiple issues |
| Pre-commit | `git-commit` Step 2 chains here | Commit analysis — suggest splits if changes span concerns |

---

## Mode 1: Setup

Run when the user calls `/issue-workflow` directly, or when `git-commit` offers
it during CLAUDE.md initialisation.

### Step 1 — Detect GitHub repository

```bash
git remote get-url origin
```

Extract `owner/repo` from the URL. If it fails or is not a GitHub URL:
> ⚠️ Could not detect a GitHub repository. Issue tracking requires a GitHub
> remote. Please set one up and run `/issue-workflow` again.

Stop if no GitHub remote found.

### Step 2 — Check GitHub CLI availability

```bash
gh auth status
```

If not available or not authenticated:
> ⚠️ The GitHub CLI (`gh`) is required for issue tracking. Install it from
> https://cli.github.com/ and run `gh auth login`, then try again.

Stop if `gh` is not usable.

### Step 3 — Ask about scope

> **Issue tracking setup**
>
> I can link all your work to GitHub issues automatically. This gives you:
> - Clean release notes generated directly from closed issues (`gh release create --generate-notes`)
> - Commit messages that reference issues (`Refs #12`, `Closes #34`)
> - Automatic detection when a task spans multiple issues, so you can break it down before starting
> - Suggestions to split commits when staged changes cover multiple concerns
>
> **How would you like to proceed?**
>
> 1. **Start fresh** — configure issue tracking for ongoing work only
> 2. **Include past work** — I'll read the git history and help create issues for significant past work too
> 3. **Skip** — no issue tracking for this project

Wait for user choice. If 3, stop.

### Step 4 — Set up standard labels

Check existing labels:
```bash
gh label list --repo {owner/repo}
```

Suggest creating the standard set if missing. These labels map to changelog
sections when GitHub generates release notes:

| Label | Changelog section | When to use |
|-------|------------------|-------------|
| `enhancement` | ✨ New Features | New capability or improvement |
| `bug` | 🐛 Bug Fixes | Something was broken |
| `documentation` | 📚 Documentation | Docs only, no code change |
| `performance` | ⚡ Performance | Faster, leaner, cheaper |
| `security` | 🔒 Security | Security fix or hardening |
| `refactor` | 🔧 Internal | Code change, no user-visible effect |

Offer to create any missing labels:
```bash
gh label create "enhancement" --color "#84b6eb" --description "New feature or improvement"
gh label create "bug" --color "#d73a4a" --description "Something is broken"
gh label create "documentation" --color "#0075ca" --description "Documentation only"
gh label create "performance" --color "#e4e669" --description "Performance improvement"
gh label create "security" --color "#e11d48" --description "Security fix or hardening"
gh label create "refactor" --color "#6e6e6e" --description "Code change without user-visible effect"
```

### Step 5 — Write configuration to CLAUDE.md

Add or update the `## Work Tracking` section in CLAUDE.md:

```markdown
## Work Tracking

**Issue tracking:** enabled
**GitHub repo:** {owner/repo}
**Changelog:** GitHub Releases (run `gh release create --generate-notes` at milestones)

**Automatic behaviours (Claude follows these when this section is present):**
- Before starting any significant task, check if it spans multiple concerns.
  If it does, help break it into separate issues before beginning work.
- When staging changes before a commit, check if they span multiple issues.
  If they do, suggest splitting the commit using `git add -p`.
- All commits must reference an issue: `Refs #N` (ongoing) or `Closes #N` (done).
  Never commit without an issue reference unless the change is truly trivial
  (e.g. fixing a typo).
```

Stage and confirm:
> ✅ Work Tracking configured in CLAUDE.md
>
> From now on:
> - I'll check every task for cross-cutting concerns before starting
> - I'll check every staged commit for issue-spanning changes before committing
> - All commits will reference a GitHub issue
>
> Run `gh release create --generate-notes` at milestones to generate your changelog.

### Step 6 — Past work reconstruction (if user chose option 2)

Read recent git history:
```bash
git log --oneline --no-merges -50
```

Group commits into logical themes. For each theme, suggest an already-closed
issue to create:

> I found these themes in your recent history:
>
> 1. **Skills infrastructure** (12 commits) — install/uninstall wizards, marketplace, sync-local
> 2. **Blog support** (6 commits) — blog project type, blog-git-commit skill, commit validation
> 3. **Documentation quality** (8 commits) — CSO fixes, validator improvements, README overhaul
>
> Create GitHub issues for these? I'll mark them as already closed.
> Reply YES, or tell me which ones to include.

For each confirmed theme, create a closed issue:
```bash
gh issue create \
  --title "{suggested title}" \
  --body "{summary of what was done}" \
  --label "{appropriate label}" \
  --repo {owner/repo}

gh issue close {number} --comment "Completed in earlier development phase."
```

---

## Mode 2: Task Intake — Cross-Cutting Detection

This mode runs **automatically** whenever Work Tracking is enabled in CLAUDE.md
and the user makes a significant request. Claude checks the request before
starting work.

### Detection heuristics

A task likely spans multiple issues when it:

| Signal | Example |
|--------|---------|
| Uses "and" connecting distinct domains | "Add the new skill **and** update the README **and** fix the validator" |
| Touches multiple architectural layers | "Add feature + write tests + update docs + fix unrelated bug" |
| Would need multiple issue titles to describe | Each part would be a separate GitHub issue on its own |
| Affects 3+ unrelated directories | `src/`, `docs/`, `scripts/`, `tests/` with different concerns |
| Mixes a new capability with an existing fix | "While we're at it, also fix..." |

### Workflow

When a cross-cutting task is detected:

> ⚠️ **This looks like it spans multiple concerns:**
>
> 1. **{Concern A}** — {brief description}
> 2. **{Concern B}** — {brief description}
> 3. **{Concern C}** — {brief description}
>
> Working on all of these together risks a large mixed commit that's hard to
> review and impossible to revert cleanly.
>
> **How would you like to proceed?**
>
> a) **Break it down** — I'll create issues for each and tackle them in order
> b) **Create an umbrella issue** — one parent issue with sub-tasks listed
> c) **Proceed as one** — if these genuinely belong together, tell me why

If user chooses **a** or **b**, run issue selection/creation (see below).

If user chooses **c**, note the reason and continue — don't ask again for this
session.

### When NOT to flag cross-cutting

Don't flag these — they belong together:
- Code change + its tests
- Feature + its documentation
- Bug fix + a regression test for it
- Refactor + updating the affected imports

The test: **would reverting one part but not the other leave the repo in a valid state?** If yes, they're separate concerns.

---

## Mode 3: Pre-Commit — Commit Split Detection

This mode runs automatically during `git-commit` Step 2 when Work Tracking is
enabled. Analyse staged changes before generating the commit message.

### Step 1 — Analyse staged changes

```bash
git diff --staged --stat
git diff --staged --name-only
```

Group changed files by concern:

```python
# Heuristic grouping
concerns = {
    "new feature": files in new directories or with new exports,
    "bug fix": files with purely corrective changes,
    "documentation": *.md, *.txt, docs/,
    "configuration": *.yml, *.json, *.toml, Makefile,
    "tests": *Test*, *_test.*, tests/,
    "refactor": same files as a feature but no new public API,
}
```

### Step 2 — Detect split candidates

Flag for splitting when staged changes include **two or more independent concerns**
where each could stand alone as a meaningful commit.

Do NOT flag:
- Feature + its own tests (these belong together)
- Bug fix + its regression test
- Single-concern changes across many files (a rename touches many files but is one thing)

**Flag these patterns:**
- A new feature AND an unrelated bug fix
- Multiple unrelated bug fixes
- Documentation update AND a code change to a different area
- Config change AND a feature in a completely unrelated module

### Step 3 — Surface the suggestion

When a split is warranted:

> 📦 **These staged changes look like they span two separate concerns:**
>
> **Concern 1:** {description} — {list of files}
> **Concern 2:** {description} — {list of files}
>
> Splitting them gives you:
> - Cleaner issue references in each commit
> - Independent revert capability
> - More accurate GitHub release notes
>
> **Options:**
>
> a) **Split** — I'll guide you through `git add -p` or `git restore --staged`
> b) **Keep together** — commit as-is (I'll note both issue refs in the message)
> c) **Show me the diff first** — let me see what's in each group

If user chooses **a**, guide through splitting:

```bash
# Option A: unstage one concern, commit the other first
git restore --staged {files for concern 2}

# Or use interactive staging for fine-grained control
git add -p {files that mix concerns}
```

Then commit the first concern, re-stage the second, commit that.

If user chooses **b**, include both issue refs:
```
feat: add blog-git-commit skill and fix validator count

Refs #45, Refs #31
```

---

## Issue Selection / Creation

Used in both Mode 2 (task intake) and during `git-commit` when an issue
reference is needed.

### Step 1 — List open issues

```bash
gh issue list --state open --limit 15 --repo {owner/repo}
```

Show the list and ask:
> Which issue does this relate to? Enter the number, or:
> - **N** for "none of these — create a new one"
> - **S** for "show more issues"

### Step 2 — Match automatically when obvious

Before asking, check if any open issue title closely matches:
- The staged files (e.g. issue titled "blog-git-commit skill" and `blog-git-commit/` files staged)
- The user's request description

If a strong match is found:
> This looks like it relates to **#45: Add blog-git-commit skill**. Is that right?
> (YES / NO — show full list instead)

### Step 3 — Create new issue when needed

If no existing issue fits:
> Let me create one. Based on what you're working on, I'd suggest:
>
> **Title:** {suggested title}
> **Label:** {suggested label}
>
> Adjust the title or say YES to create it.

```bash
gh issue create \
  --title "{confirmed title}" \
  --label "{label}" \
  --repo {owner/repo}
```

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Creating an issue per commit | Issues represent *outcomes*, commits represent *steps* | One issue = one meaningful user-visible change |
| Using vague issue titles | GitHub generates changelog from titles — "fix stuff" is useless | Title should describe the outcome: "Add X", "Fix Y when Z" |
| Wrong label | Wrong changelog section in release notes | `bug` = broken thing fixed, `enhancement` = new capability |
| Skipping issue ref on "small" commits | "Small" commits accumulate — release notes become gaps | Ref an issue even for small changes; create a catch-all issue if needed |
| One giant issue for everything | Can never be closed cleanly | One issue = one thing that can be independently released or reverted |

---

## Skill Chaining

**Invoked by:** User via `/issue-workflow`, or chained from `git-commit` during
project setup (Step 0) or pre-commit (Step 2).

**Invokes:** Nothing — this skill is a terminal in the chain.

**CLAUDE.md integration:** Writes `## Work Tracking` section. Once present,
Claude reads it at session start and applies the automatic behaviours for all
subsequent work in that session without needing to invoke this skill explicitly.
