# Skill Architecture Reference

Reference for skill authors working in this repository. Covers structure,
naming, chaining patterns, and consistency rules.

---

## Frontmatter Requirements

Every `SKILL.md` requires YAML frontmatter with exactly two fields:

```yaml
---
name: skill-name-with-hyphens
description: >
  Use when [specific triggering conditions and symptoms]
---
```

**Critical: Claude Search Optimization (CSO)**

The `description` field determines when Claude loads the skill:

- **Start with "Use when..."** to focus on triggering conditions
- **NEVER summarize the skill's workflow** in the description
- Describe the *problem* or *symptoms*, not the solution
- Keep under 500 characters if possible
- Third person only (no "I" or "you")

❌ Bad: `description: Use when executing plans - dispatches subagent per task with code review between tasks`

✅ Good: `description: Use when executing implementation plans with independent tasks in the current session`

---

## Naming Conventions

Skills follow a hierarchical naming pattern:

**Generic principles skills** (suffix: `-principles`):
- `code-review-principles` — language-agnostic review checklist
- `security-audit-principles` — universal OWASP Top 10
- `dependency-management-principles` — universal BOM patterns
- `observability-principles` — universal logging/tracing/metrics

**Language-specific skills** (prefix: language name):
- `java-dev`, `java-code-review`, `java-security-audit`, `java-git-commit`

**Tool-specific skills** (prefix: tool name):
- `maven-dependency-update`, `npm-dependency-update`, `pip-dependency-update`

**Framework-specific skills** (prefix: framework name):
- `quarkus-flow-dev`, `quarkus-flow-testing`, `quarkus-observability`

**Extending to New Languages:**
1. Canonical names — `go-dev` not `golang-dev`, `ts-dev` not `javascript-dev`
2. 1-word base suffix — `*-dev`, `*-code-review`, `*-security-audit`
3. Tool prefix for tools — `cargo-*`, `npm-*`, `pip-*`, `gomod-*`
4. Framework prefix for frameworks — `react-*`, `vue-*`, `django-*`
5. Consistency over brevity — match existing patterns

---

## Skill Chaining

Skills explicitly reference each other to create workflows:

1. **Add cross-references in "Skill Chaining" sections** (capitalized C)
2. **Make references bidirectional** when appropriate
3. **Use Prerequisites sections** for layered skills
4. **Generic principles skills are never invoked directly** — referenced via Prerequisites only

Example patterns:
```
# Java repositories:
java-dev → java-code-review → java-git-commit → java-update-design + update-claude-md

# Any repository:
git-commit → update-claude-md (automatic)
```

---

## Canonical Path Resolution Block

Several workspace-aware skills resolve paths via symlinks. The canonical form
— identical across all of them — is:

```bash
WORKSPACE=$(git rev-parse --show-toplevel 2>/dev/null)
PROJECT=$(readlink -f proj 2>/dev/null)
[ -z "$PROJECT" ] && { echo "⚠️ No proj/ symlink found. Run workspace-init to set up."; exit 1; }
```

Do not use CLAUDE.md parsing for path detection. The `proj/` → project and
`wksp/` → workspace symlinks are the single source of truth.

Verify consistency with:
```bash
grep -l "readlink -f proj" ~/claude/cc-praxis/*/SKILL.md
```

---

## Supporting Files

When skill content exceeds ~200 words or includes heavy reference material,
use named subdirectories that describe their purpose:

```
skill-name/
  SKILL.md              # Main workflow (required)
  reference-name.md     # Heavy API/reference docs
  forms/                # Form-specific guidance (if skill has content types)
  modes/                # Mode-specific constraint sets (if skill has writing modes)
  voice/                # Voice and style defaults
  commands/             # Slash command files
```

Prefer named directories over a generic `defaults/` — the directory name
should signal what the files inside govern. `write-content` uses `forms/`,
`modes/`, and `voice/` rather than `defaults/` so the taxonomy is visible
from the directory structure alone.

---

## Skills-Repository-Specific Documentation

Skills-specific logic lives in standalone docs, not portable skills:

| File | Purpose | Used By |
|------|---------|---------|
| `docs/development/skill-validation.md` | SKILL.md validation workflow | `git-commit` when type: skills |
| `docs/development/readme-sync.md` | README.md sync workflow | `git-commit` when type: skills |

**When git-commit operates in type: skills mode:**
1. Staged SKILL.md files → follow `skill-validation.md`
2. Skill collection changes → follow `readme-sync.md`

---

## Flowcharts

Use Mermaid `flowchart TD` notation when:
- Decision points are non-obvious
- Process has loops where you might stop too early
- "When to use A vs B" decisions exist

Never for: reference material (use tables), code examples, linear instructions.
Flowcharts must have semantic labels, not generic ones like `step1`.

---

## Success Criteria Pattern

Skills that produce artifacts include explicit Success Criteria sections:

```markdown
## Success Criteria

Task is complete when:
- ✅ User has confirmed with **YES**
- ✅ Compilation succeeds
- ✅ Changes committed

**Not complete until** all criteria met.
```

---

## Consistency Patterns

### Section Naming
- "Skill Chaining" (capitalized C)
- "Prerequisites" (for layered skills)
- "Success Criteria" (for artifact-producing skills)
- "Common Pitfalls" (table: Mistake | Why It's Wrong | Fix)

### Cross-Reference Format

```markdown
## Prerequisites
**This skill builds on `skill-name`**. Apply all rules from:
- **skill-name**: [specific rules that apply]
```

### Common Pitfalls Tables

```markdown
| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| [Anti-pattern] | [Consequence] | [Correct approach] |
```

---

## Developer-Only Skills

Some skills require a cloned repository and are not available to marketplace users:

- ✅ In skill directory (auto-discovered by devs)
- ❌ NOT in `marketplace.json`
- ❌ NOT in README.md
- ✅ SKILL.md includes a prominent DEV-ONLY note

**Current developer-only skills:** `sync-local`

**When adding:** create in skills dir, skip marketplace.json and README, add DEV-ONLY note.

---

## Third-Party Skill Exclusion

Only document skills authored by the repository owner:

- ✅ Document only user-authored skills in README.md and CLAUDE.md
- ❌ Never document third-party skills (superpowers:*, external repos)
- ✅ Add third-party skills to .gitignore immediately

**Implementation:**
1. Add to .gitignore with comment: `# Third-party skill from [source]`
2. Remove all references from README.md and CLAUDE.md
3. Verify: `grep -r "skill-name" README.md CLAUDE.md`
