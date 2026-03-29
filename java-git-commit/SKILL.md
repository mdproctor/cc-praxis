---
name: java-git-commit
description: >
  Use when the user says "commit", "smart commit", "update design and commit",
  or invokes /java-git-commit. Creates conventional commits for Java changes
  with automatic DESIGN.md synchronization via update-design skill. Always
  proposes everything for review before touching the repo.
---

# Java Git Commit Helper with Design Document Sync

You are an expert Java developer specializing in clean, conventional Git
commits for Java/Spring/Maven/Gradle projects while keeping DESIGN.md in sync.

## Core Rules

- Follow the **Conventional Commits 1.0.0 specification**.
- Never mention AI, Claude, or any tooling attribution in commit messages or
  design updates.
- Never add author attribution unless explicitly requested.
- Subject line: imperative mood, max 50 chars, no trailing period.
- Always sync DESIGN.md before committing — the design doc is part of the
  commit, not an afterthought.
- Never run `git commit` until the user has explicitly confirmed.

## Decision Flow

```dot
digraph commit_flow {
    "Start" [shape=doublecircle];
    "Staged changes?" [shape=diamond];
    "Stop: ask user to stage" [shape=box];
    "Generate commit message" [shape=box];
    "Invoke update-design" [shape=box];
    "Present consolidated proposal" [shape=box];
    "User confirms?" [shape=diamond];
    "Apply DESIGN.md changes" [shape=box];
    "Stage DESIGN.md" [shape=box];
    "Execute git commit" [shape=box];
    "Done" [shape=doublecircle];
    "Adjust proposal" [shape=box];

    "Start" -> "Staged changes?";
    "Staged changes?" -> "Stop: ask user to stage" [label="no"];
    "Staged changes?" -> "Generate commit message" [label="yes"];
    "Generate commit message" -> "Invoke update-design";
    "Invoke update-design" -> "Present consolidated proposal";
    "Present consolidated proposal" -> "User confirms?";
    "User confirms?" -> "Adjust proposal" [label="no"];
    "Adjust proposal" -> "Present consolidated proposal";
    "User confirms?" -> "Apply DESIGN.md changes" [label="yes"];
    "Apply DESIGN.md changes" -> "Stage DESIGN.md";
    "Stage DESIGN.md" -> "Execute git commit";
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
> "Nothing is staged. Run `git add <files>` first, or let me know which files
> to stage."

### Step 2 — Generate commit message
Draft one conventional commit message (see **Message Format** below).
Hold it — don't show it yet.

### Step 3 — Sync DESIGN.md
Invoke the `/update-design` skill, passing the staged diff.
It will return proposed DESIGN.md changes. Hold those too.

### Step 4 — Present everything together
Show the user a single consolidated proposal:

~~~
## Staged files
<output of git diff --staged --stat>

## Proposed commit message
<type>[scope]: <description>

<optional body>

<optional footer>

## Proposed DESIGN.md updates
<output from update-design skill>
~~~

Then ask exactly:
> "Does everything look good? Reply **YES** to apply the DESIGN.md updates,
> stage them, and commit. Or tell me what to adjust."

### Step 5 — Apply and commit (only after explicit YES)

Run in this exact order:
1. Let update-design apply its changes to `docs/DESIGN.md`
2. Stage the updated file:
~~~bash
git add docs/DESIGN.md
~~~
3. Commit with the confirmed message:
~~~bash
git commit -m "<subject>" -m "<body if any>"
~~~
4. Confirm success:
~~~bash
git log --oneline -1
~~~

> If update-design found no changes needed, skip steps 1–2 and commit
> the originally staged files as-is.

### Step 6 — Handle edge cases

| Situation | Action |
|---|---|
| Nothing staged | Stop at step 1, prompt user to stage files |
| Merge conflict markers in diff | Warn before proceeding |
| Only test files staged | Suggest `test` type, note DESIGN.md likely unchanged |
| Only `pom.xml` / `build.gradle` changed | Suggest `build` type, check for new deps that need design doc mention |
| Large diff (10+ files) | Summarize by layer/module rather than file-by-file |
| update-design finds no changes needed | Note this clearly, skip DESIGN.md staging |

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
| `feat` | New feature or capability (new API, endpoint, functionality) |
| `fix` | Bug fix or correcting unintended behaviour |
| `refactor` | Restructuring with no functional change (extract class, rename, reorganise) |
| `test` | Adding or updating tests (unit, integration, e2e) |
| `docs` | Documentation only (Javadoc, README, comments) |
| `perf` | Performance improvement (caching, query optimisation, reduced allocations) |
| `build` | Build system or dependency changes (Maven, Gradle, BOM, packaging) |
| `chore` | Maintenance with no production code change (CI, tooling, version bumps) |
| `style` | Formatting only, no logic change (whitespace, imports, code style) |

> `fix` vs `refactor`: if it corrects wrong behaviour → `fix`. If behaviour
> was already correct but code is cleaner → `refactor`.

### Scopes

| Kind | Examples |
|---|---|
| Module | `core`, `api`, `common`, `utils`, `domain`, `infrastructure` |
| Layer | `controller`, `service`, `repository`, `config`, `mapper`, `scheduler`, `listener` |
| Subsystem | `security`, `cache`, `events`, `messaging`, `auth`, `plugin-loader` |
| Build | `maven`, `gradle`, `deps`, `ci`, `docker`, `bom` |

> When in doubt, use the Java class name (e.g. `PluginManager`) or the
> Maven/Gradle module name.

### Breaking changes
Add `!` after the type/scope and a `BREAKING CHANGE:` footer:
~~~
feat(api)!: replace userId with UUID across all endpoints

BREAKING CHANGE: all callers must update userId fields to UUID format.
Fixes #88
~~~

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Committing before user confirms | User loses control | Always show proposal and wait for YES |
| Skipping DESIGN.md sync | Design doc drifts from code | Always invoke update-design first |
| Subject line > 50 chars | Truncated in git log | Keep under 50, use body for details |
| Subject ends with period | Not conventional commits standard | Remove trailing period |
| Using past tense ("Added X") | Not imperative mood | Use "Add X" (command form) |
| Type `chore` for production code | Wrong semantics | Use `feat`, `fix`, or `refactor` |
| Wrong type (`refactor` for bug fix) | Misleading git history | `fix` if it was wrong, `refactor` if it was working |
| No body for complex changes | Reviewers lack context | Add why/what in body (not how) |
| Committing merge conflict markers | Broken code in history | Check diff for `<<<<<<<` markers first |
| Forgetting BREAKING CHANGE footer | Hidden breaking changes | Add footer with `!` in type/scope |
| Running commit without staged changes | Wastes time | Check `git status` first |