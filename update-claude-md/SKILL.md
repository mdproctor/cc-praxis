---
name: update-claude-md
description: >
  Use when CLAUDE.md needs updating due to workflow or convention changes, or
  when invoked automatically by git-commit/java-git-commit when commits
  affect build commands, testing patterns, naming conventions, or repository
  structure.
slash-command: false
---

# Update CLAUDE.md

You are an expert at maintaining repository guidance documentation. Your job is
to keep CLAUDE.md accurate when workflows, conventions, or repository structure
changes.

## Purpose

**CLAUDE.md** documents how Claude Code should work in this repository:
- Build commands and development workflows
- Testing patterns and commands
- Naming conventions and code organization
- Repository-specific tools and processes
- Project conventions that aren't obvious from code

**Not covered here:** Software architecture (that's DESIGN.md via update-design)

## Core Rules

- CLAUDE.md lives at repository root
- **Never apply changes without explicit user confirmation** (a plain "YES" or equivalent)
- **Never modify the Project Type section** — this is user-configured and defines repository behavior (type: skills, type: java, type: blog, type: custom, type: generic)
- Focus on **workflow and convention changes**: new tools, build commands, testing
  patterns, naming conventions, repository structure changes
- Keep prose concise and professional. Prefer bullet points and tables
- Do not mention AI, LLMs, or tooling attribution in the document

## Workflow

### Step 0: Refresh config-architecture.md (daily)

Before updating CLAUDE.md, ensure the local config architecture map is current.

Projects can provide a project-specific config-architecture by adding to their CLAUDE.md:
```
**Config architecture:** https://raw.githubusercontent.com/<owner>/<repo>/main/docs/config-architecture.md
```
If present, that URL is used. Otherwise falls back to the generic cc-praxis version.

```bash
CONFIG_FILE="$HOME/.claude/config-architecture.md"
GENERIC_URL="https://raw.githubusercontent.com/mdproctor/cc-praxis/main/docs/config-architecture.md"

# Check for project-specific config-architecture URL in CLAUDE.md
PROJECT_URL=$(grep -m1 "^\*\*Config architecture:\*\*" CLAUDE.md 2>/dev/null | sed 's/\*\*Config architecture:\*\* *//')
GITHUB_URL="${PROJECT_URL:-$GENERIC_URL}"

if [ ! -f "$CONFIG_FILE" ]; then
  NEEDS_UPDATE=true
else
  FILE_AGE=$(( $(date +%s) - $(date -r "$CONFIG_FILE" +%s 2>/dev/null || stat -c %Y "$CONFIG_FILE" 2>/dev/null || echo 0) ))
  [ "$FILE_AGE" -ge 86400 ] && NEEDS_UPDATE=true || NEEDS_UPDATE=false
fi

if [ "$NEEDS_UPDATE" = "true" ]; then
  CONTENT=$(curl -sf --max-time 5 "$GITHUB_URL")
  if [ -n "$CONTENT" ]; then
    echo "$CONTENT" > "$CONFIG_FILE"
    echo "✅ config-architecture.md refreshed"
  else
    echo "⚠️  Could not fetch config-architecture.md — keeping existing copy"
  fi
fi
```

This step is silent on success when the file is fresh (< 24h old). Network failures are non-fatal — existing copy is kept.

### Step 1: Check if CLAUDE.md exists

```bash
ls CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found"
```

- If found → proceed to Step 1a
- If not found → check if this is the type of repo that needs one:
  - Skills repository? (has */SKILL.md files)
  - Complex build setup? (has build.gradle, pom.xml, package.json, etc.)
  - If yes → propose creating starter CLAUDE.md from [starter-templates.md](starter-templates.md), ask user to confirm
  - If no → skip (repo may not need CLAUDE.md)

### Step 1a: Check for modular structure

Check whether sibling docs exist that CLAUDE.md routes content to:

```bash
[ -f "docs/GOTCHAS.md" ] && echo "gotchas: yes" || echo "gotchas: no"
[ -f "docs/FLYWAY.md" ]  && echo "flyway: yes"  || echo "flyway: no"
[ -f "scripts/README.md" ] && echo "scripts-readme: yes" || echo "scripts-readme: no"
```

If any module files are present, the document is modular. Continue with the standard single-file workflow for CLAUDE.md itself, but apply **Step 4e** routing before adding any new content — new gotchas, Flyway notes, and script docs must go to their module file, not accumulate in CLAUDE.md.

### Step 2: Read current content

Read the full CLAUDE.md so you understand the existing structure before proposing changes.

### Step 3: Collect changes to analyze

In priority order:
1. **Staged changes**: `git diff --staged` (prefer this)
2. **Recent commit**: `git diff HEAD~1 HEAD` (if nothing staged)
3. **User-provided description** passed in context

### Step 4: Identify workflow/convention impact

Map changes to CLAUDE.md sections:

| Change type | Likely CLAUDE.md section |
|---|---|
| New build tool or command | Build/Development commands |
| New testing framework or test commands | Testing section |
| Package/module structure change | Repository Structure |
| New naming convention introduced | Naming Conventions |
| New development tool (linter, formatter) | Development Tools |
| CI/CD pipeline changes | Build/CI section |
| New environment variable required | Configuration/Setup |
| Git workflow changes (hooks, branch strategy) | Git Workflow |
| New skill added (skills repo) | Skill list, Naming Conventions |
| Skill renamed (skills repo) | Update all references |
| New skill cross-reference pattern (skills repo) | Editing Skills section |

**What to skip:**
- **Project Type section** — never modify this user-configured section
- Code implementation details (that's for DESIGN.md)
- Architecture changes (that's for DESIGN.md)
- Individual bug fixes that don't change workflow
- Formatting/style changes

### Step 4a: Check for framework changes (UNIVERSAL)

**Framework changes = infrastructure that affects multiple files or introduces new capabilities.**

**Red flags that warrant CLAUDE.md documentation:**

| Pattern | CLAUDE.md Impact |
|---------|------------------|
| **New scripts/ or tools/ files** | Document in Development Tools or Repository Structure |
| **New validation/testing infrastructure** | Document in Testing section or Quality Assurance |
| **Same pattern applied across multiple files** | Framework change, document the pattern |
| **New automation or sync capabilities** | Document in workflow sections |
| **New quality gates or pre-commit hooks** | Document in Git Workflow or Development Tools |
| **New dependency management patterns** | Document in Dependencies section |

**Example:**
- **What happened:** A new linter or validator added to the CI pipeline
- **Framework change:** All commits now require passing lint checks before merge
- **CLAUDE.md impact:** Should document the new quality gate under Development Tools or Workflow

**If you detect framework changes, include them in proposals even if no direct workflow/convention changes.**

**This check applies to ALL project types** (skills/java/blog/custom/generic).

### Step 4b: Check for missing Work Tracking section

Run `python3 ~/.claude/skills/project-init/ctx.py` if not already run this session.
Read `ISSUES_STATUS` from the output.

If `ISSUES_STATUS` is `absent`, prompt:

> **Enable GitHub issue tracking for this repo? (YES / n)**
>
> Adds automatic behaviours: flag cross-cutting tasks before starting, check staged changes for commit splits, and link every commit to a GitHub issue for clean release notes.
>
> Default: **YES** — type **YES** to enable, type **n** to skip.

If **YES** → propose adding to CLAUDE.md (include in the Step 5 proposal block):
```markdown
## Work Tracking

**Issue tracking:** enabled
**GitHub repo:** [owner/repo]
**Changelog:** GitHub Releases (run `gh release create --generate-notes` at milestones)

**Automatic behaviours (Claude follows these when this section is present):**
- Before starting any significant task, check if it spans multiple concerns.
  If it does, help break it into separate issues before beginning work.
- When staging changes before a commit, check if they span multiple issues.
  If they do, suggest splitting the commit using `git add -p`.
```

Fill `[owner/repo]` from `git remote get-url origin`. This is a one-time addition — once present, this check passes silently.

If **n** → skip silently.

### Step 4c: Check for missing Writing Style Guide section

```bash
ls blog/ 2>/dev/null | head -1
```

If `blog/` exists (meaning write-content has been used in this workspace), check whether CLAUDE.md already contains the Writing Style Guide requirement.

Read `HAS_WRITING_STYLE_REF` from the ctx.py output (already run in Step 4b).

If `blog/` exists **and** the requirement is absent from CLAUDE.md, propose adding:

```markdown
## Writing Style Guide

**The writing style guide at `~/claude-workspace/writing-styles/blog-technical.md` is mandatory for all blog and diary entries.** Load it in full before drafting. Complete the pre-draft voice classification (I / we / Claude-named) before generating any prose. Do not show a draft without verifying it against the style guide.
```

This is a one-time addition per project — once present, this check passes silently.

### Step 4d: Check for missing Name field (workspace CLAUDE.md)

Check whether this is a workspace CLAUDE.md (has `## Session Start` with `add-dir`):

```bash
grep -l "add-dir" CLAUDE.md 2>/dev/null
```

If it is a workspace CLAUDE.md, read `PROJECT_NAME` from the ctx.py output (already run in Step 4b).

If `PROJECT_NAME` is **empty**, derive it from the H1 heading:

```bash
head -3 CLAUDE.md | grep "^# " | sed 's/^# //' | sed 's/ Workspace$//'
```

Propose adding immediately after the H1 heading:

```markdown
**Name:** <derived-name>
```

This field is required by `write-content` to auto-populate the `projects:` frontmatter
field in blog entries. Without it, write-content will stop and prompt the user.

This is a one-time addition per workspace — once present, this check passes silently.

### Step 4e: Route new content to the correct module file

Before adding any new content, check the routing table:

| Content category | Target file |
|---|---|
| Pitfall, gotcha, workaround, non-obvious behaviour, common mistake | `docs/GOTCHAS.md` |
| Flyway migration, V-number, migration prerequisite, datasource config | `docs/FLYWAY.md` |
| Build script, expected test times, script invocation | `scripts/README.md` |
| Build command, test command, git workflow convention | `CLAUDE.md` |
| Active epic, issue tracking state, work tracking | `CLAUDE.md` |
| Architecture, SPI contracts, domain model | `docs/ARCHITECTURE.md` (never `CLAUDE.md`) |

**The rule:** If content matches a module file category, route it there. Never add gotchas, Flyway notes, or script docs to CLAUDE.md. Only rules that need to be in active working memory belong in CLAUDE.md.

When proposing an update that routes to a module file, include it as a separate change block (or as the sole change if CLAUDE.md itself needs no update).

---

### Step 4f: Check for missing ARC42STORIES.MD reference

Read `HAS_ARC42STORIES` from the ctx.py output (already run in Step 4b).

If `HAS_ARC42STORIES=yes`, check whether CLAUDE.md already references it:

```bash
grep -c "ARC42STORIES" CLAUDE.md 2>/dev/null
```

If ARC42STORIES.MD exists **and** CLAUDE.md has zero mentions, propose adding two things:

1. A `design` row in the Routing table (if a Routing table exists):
   ```markdown
   | design     | project     | journal in workspace `design/`; merge target is project `ARC42STORIES.MD` |
   ```

2. A living-docs block after the Routing table:
   ```markdown
   Living docs — check for drift after significant changes:
   - `ARC42STORIES.MD` — primary architecture record; check §9–10 after module, SPI, or structural changes
   ```

This is a one-time addition — once present, this check passes silently.

### Step 5: Propose updates

**For single-file CLAUDE.md:**

Format each proposed change as a clear before/after block:

```
## Section: <Section Name>

**Replace:**
> <exact existing text, or "(new section)">

**With:**
> <your proposed replacement text>

**Reason:** <one-sentence rationale>
```

**For modular CLAUDE.md:** see [modular-handling.md](modular-handling.md) § Step 5.

Group related changes. Show summary at top if many changes.

### Step 6: Confirm and apply

End every proposal with exactly:

> **Does this look good?**
> Reply **YES** to apply all changes, **NO** to discard, or describe what to adjust.

When user confirms YES:

1. Apply **only** the proposed changes
2. **Validate links (if module files present):** Check that any markdown links from CLAUDE.md to module files resolve:
   ```bash
   python3 ~/.claude/skills/update-claude-md/check_links.py CLAUDE.md
   ```
   If broken links are found, fix them before staging.
3. **Skip `validate_document.py`** — this script is not present in all projects and is optional.
4. **If no broken links:**
   - Print brief summary: "✅ Updated sections: Build Commands, Testing"
   - Document is ready for staging

**For modular CLAUDE.md:** see [modular-handling.md](modular-handling.md) § Step 6.

**Validation checks for modular groups:**
- Link integrity: All `[links](file.md)` and `[links](file.md#section)` resolve
- Completeness: No orphaned modules (unreferenced from primary)
- No duplication: Substantial paragraphs not duplicated across files
- Individual file validation: Each file passes single-file corruption checks

---

## Common Pitfalls

Avoid these mistakes when updating CLAUDE.md:

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Modifying Project Type section | Breaks repository behavior, user-configured | Never touch this section, skip it entirely |
| Applying changes without confirmation | User loses control | Always wait for explicit YES |
| Documenting architecture in CLAUDE.md | Wrong file - DESIGN.md is for architecture | Focus on workflow/conventions only |
| Over-documenting obvious things | Clutter, maintenance burden | Only document non-obvious workflows |
| Not updating CLAUDE.md when adding tools | Claude doesn't know about new tools | Update when workflow changes |
| Copying command help text verbatim | Duplicate of `--help` output | Summarize common use cases |

## Document Structure Check

*This check is part of the `performance` and `docs-sync` categories in `project-health`. For a full analysis: `/project-health performance docs-sync`. See [docs/project-health.md](../docs/project-health.md).*

After applying updates, run:

```bash
python scripts/validation/validate_doc_structure.py CLAUDE.md
```

If exit code 1 or 2, follow the nudge workflow described in `java-update-design` § Document Structure Check — same conversation, same threshold adjustment, same CLAUDE.md persistence pattern.

## Success Criteria

CLAUDE.md update is complete when:

- ✅ config-architecture.md checked and refreshed if stale (Step 0)
- ✅ CLAUDE.md located and read
- ✅ Workflow/convention changes identified from staged diff
- ✅ Proposed updates formatted as before/after blocks
- ✅ User confirmed with explicit **YES**
- ✅ Changes applied to CLAUDE.md
- ✅ **Document validation passed** (no CRITICAL corruption)
- ✅ File ready for staging (or user confirmed no changes needed)

**Not complete until** all criteria met, validation passed, and CLAUDE.md reflects current workflows.

## Skill Chaining

**Invoked by:** [`git-commit`] when committing in any repository, [`java-git-commit`] alongside update-design, [`git-commit`] when committing blog changes, [`custom-git-commit`] when committing custom project changes, [`work-end`] as part of Step 3b pre-close sweep, [`handover`] as part of the session wrap checklist (mid-work sessions), [`write-content`] on the first blog entry ever in a project (adds the mandatory Writing Style Guide section)

**Invokes:** None (terminal skill in the chain)

**Can be invoked independently:** User can run `/update-claude-md` directly to sync CLAUDE.md without committing

**Starter templates:** see [starter-templates.md](starter-templates.md) — used when creating CLAUDE.md from scratch.
