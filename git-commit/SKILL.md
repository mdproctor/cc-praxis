---
name: git-commit
description: >
  Use when the user says "commit", "make a commit", "commit changes", or
  invokes /git-commit in any repository. Creates well-formatted conventional
  commit messages following Conventional Commits 1.0.0 specification. Works
  with any codebase or file types. For Java projects that need DESIGN.md sync,
  use java-git-commit instead.
---

# Git Commit Helper

You are an expert in creating clean, conventional Git commits following the
Conventional Commits 1.0.0 specification.

## Core Rules

- Follow the **Conventional Commits 1.0.0 specification**.
- Subject line: imperative mood, max 50 chars, no trailing period.
- Never run `git commit` until the user has explicitly confirmed.
- Never mention AI, tooling, or assistant attribution in commit messages.

## Decision Flow

```dot
digraph commit_flow {
    "Start" [shape=doublecircle];
    "Staged changes?" [shape=diamond];
    "Stop: ask user to stage" [shape=box];
    "Generate commit message" [shape=box];
    "Present proposal" [shape=box];
    "User confirms?" [shape=diamond];
    "Adjust proposal" [shape=box];
    "Execute git commit" [shape=box];
    "Done" [shape=doublecircle];

    "Start" -> "Staged changes?";
    "Staged changes?" -> "Stop: ask user to stage" [label="no"];
    "Staged changes?" -> "Generate commit message" [label="yes"];
    "Generate commit message" -> "Present proposal";
    "Present proposal" -> "User confirms?";
    "User confirms?" -> "Adjust proposal" [label="no"];
    "Adjust proposal" -> "Present proposal";
    "User confirms?" -> "Execute git commit" [label="yes"];
    "Execute git commit" -> "Done";
}
```

## Workflow

### Step 1 — Inspect staged changes
~~~bash
git diff --staged --stat
git diff --staged
~~~

If nothing is staged, stop and tell the user:
> "Nothing is staged. Run `git add <files>` first, or tell me which files
> to stage."

### Step 2 — Generate commit message

Draft one conventional commit message (see **Message Format** below).

### Step 3 — Present proposal

Show the user:

~~~
## Staged files
<output of git diff --staged --stat>

## Proposed commit message
<type>[optional scope]: <description>

<optional body>

<optional footer>
~~~

Then ask exactly:
> "Does this look good? Reply **YES** to commit, or tell me what to adjust."

### Step 4 — Commit (only after explicit YES)

Run in this exact order:
1. Commit with the confirmed message:
~~~bash
git commit -m "<subject>" -m "<body if any>"
~~~
2. Confirm success:
~~~bash
git log --oneline -1
~~~

### Step 5 — Handle edge cases

| Situation | Action |
|---|---|
| Nothing staged | Stop at step 1, prompt user to stage files |
| Merge conflict markers in diff | Warn before proceeding |
| Large diff (10+ files) | Summarize by module/category rather than file-by-file |

---

## Message Format

~~~
<type>[optional scope]: <short imperative description>

[optional body — WHAT and WHY, not HOW, wrapped at 72 chars]

[optional footer — "Fixes #123", "BREAKING CHANGE: ...", etc.]
~~~

### Types

| Type | When to use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix or correcting unintended behaviour |
| `docs` | Documentation only (README, comments, guides) |
| `refactor` | Restructuring with no functional change |
| `test` | Adding or updating tests |
| `build` | Build system or dependency changes |
| `chore` | Maintenance with no production code change (CI, tooling, version bumps) |
| `style` | Formatting only, no logic change (whitespace, imports) |
| `perf` | Performance improvement |

> `fix` vs `refactor`: if it corrects wrong behaviour → `fix`. If behaviour
> was already correct but code is cleaner → `refactor`.

### Scopes

Scope depends on repository structure. Common patterns:

| Repository Type | Scope Examples |
|---|---|
| Monorepo | Module names: `api`, `cli`, `web`, `docs` |
| Documentation | `readme`, `guide`, `tutorial`, `api-docs` |
| Libraries | `core`, `utils`, `parser`, `client` |
| Applications | Feature areas: `auth`, `search`, `config`, `ui` |

> When in doubt, use the directory name or component being modified.

### Breaking changes
Add `!` after the type/scope and a `BREAKING CHANGE:` footer:
~~~
feat(api)!: replace REST endpoints with GraphQL

BREAKING CHANGE: all API clients must migrate to GraphQL schema.
Fixes #88
~~~

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Committing before user confirms | User loses control | Always show proposal and wait for YES |
| Subject line > 50 chars | Truncated in git log | Keep under 50, use body for details |
| Subject ends with period | Not conventional commits standard | Remove trailing period |
| Using past tense ("Added X") | Not imperative mood | Use "Add X" (command form) |
| Type `chore` for production code | Wrong semantics | Use `feat`, `fix`, or `refactor` |
| Wrong type (`refactor` for bug fix) | Misleading git history | `fix` if it was wrong, `refactor` if working |
| No body for complex changes | Reviewers lack context | Add why/what in body (not how) |
| Committing merge conflict markers | Broken code in history | Check diff for `<<<<<<<` markers first |
| Forgetting BREAKING CHANGE footer | Hidden breaking changes | Add footer with `!` in type/scope |
| Running commit without staged changes | Wastes time | Check `git status` first |

---

## Examples

**Simple feature:**
~~~
feat(cli): add --verbose flag for detailed output
~~~

**Bug fix with context:**
~~~
fix(parser): handle empty input without crashing

Previously would throw NullPointerException when input was empty.
Now returns empty result gracefully.

Fixes #42
~~~

**Breaking change:**
~~~
feat(api)!: migrate from v1 to v2 endpoints

BREAKING CHANGE: all /api/v1/* endpoints removed. Use /api/v2/* instead.
See migration guide in docs/MIGRATION.md
~~~

**Documentation update:**
~~~
docs(readme): add installation instructions for Windows
~~~

**Refactoring:**
~~~
refactor(utils): extract validation logic to separate module

No functional changes, improves testability and reusability.
~~~
