---
name: update-readme
description: >
  Use when skill changes occur (new skills, renamed skills, modified chaining,
  new features added) in a skills repository. Keeps README.md in sync with skill
  collection changes by analyzing skill modifications and proposing targeted updates
  to skill descriptions, chaining tables, and feature lists.
---

# Update README

Maintains README.md documentation in sync with skill collection changes in skills
repositories. Detects when skills are added, removed, renamed, or chained differently,
and proposes surgical updates to keep documentation accurate.

## Rules

- README.md lives at repository root. Never move or rename it.
- **Never apply changes without explicit user confirmation** (a plain "YES" or equivalent).
- Focus on **skill collection changes**: new/removed skills, chaining modifications,
  feature additions, structural changes.
- Keep prose concise and professional. Preserve user's voice.
- Do not mention AI, LLMs, or tooling attribution in the document.

## Workflow

### 1. Locate README.md

```bash
ls README.md 2>/dev/null || echo "No README.md found"
```

- If found → proceed.
- If not found → this is not a skills repository (or README doesn't exist yet).

### 2. Read current content

Read the full file to understand existing structure before proposing any changes.

### 3. Collect the changes to analyze

In priority order:
1. **Staged changes**: `git diff --staged` (prefer this — it's what will be committed)
2. **Recent commit**: `git diff HEAD~1 HEAD` (if nothing staged)
3. **User-provided description** passed in context
4. Ask the user if none of the above yields anything useful.

### 4. Identify README impact

Map each change to a README.md section:

| Change type | Likely README.md section |
|---|---|
| New skill added | Skills section (add description) |
| Skill removed | Skills section (remove description) |
| Skill renamed | All references (update name everywhere) |
| New skill chaining | Skill Chaining Reference table |
| Skill chaining removed | Skill Chaining Reference table |
| New feature added to skill | Key Features section |
| New flowchart added | Key Features section |
| New Prerequisites section | How Skills Work Together section |
| Repository structure change | Repository Structure section |
| New supporting file added | Repository Structure section |

**What to skip:**
Skip the following changes, unless they signal a broader pattern:
- Internal refactoring of skill content (no new features)
- Documentation fixes (typos, formatting)
- CLAUDE.md updates (not part of README)
- Test files or eval data

### 5. Propose updates

Format each proposed change as a clear before/after block:

```
## Section: <Section Name>

**Replace:**
> <exact existing text, or "(new entry)">

**With:**
> <your proposed replacement text>

**Reason:** <one-sentence rationale>
```

If adding a brand-new section, say "Add after `<Section Name>`:" and show the
full new section.

Group related changes. If there are many, summarize them as a numbered list at
the top, then show each in detail below.

### 6. Confirm and apply

End every proposal with exactly:

> **Does this look good?**
> Reply **YES** to apply all changes, **NO** to discard, or describe what to adjust.

When the user confirms with YES (or a clear equivalent):
- Apply **only** the proposed changes — no extras.
- Print a brief summary of what was written, e.g. "✅ Updated sections: Skills, Skill Chaining Reference."

---

## Skills Section Patterns

When adding a new skill to the README Skills section:

### Generic Foundation Skills

```markdown
#### **skill-name**
Universal [domain] principles covering [key concepts]. Language-agnostic [purpose].

**Features:**
- [Key concept 1]
- [Key concept 2]
- [Key concept 3]

**Extended by:** language-specific-skill (and future extensions)
```

### Language/Framework-Specific Skills

```markdown
#### **language-skill-name**
[Purpose] for [language/framework] applications:
- [Key feature 1]
- [Key feature 2]
- [Key feature 3]

Builds on skill-name-principles with [language]-specific [aspects].

**Features:**
- [Notable sections/tables]
- [Integration patterns]

**Triggers:** [When to use]
```

### Documentation/Workflow Skills

```markdown
#### **skill-name**
[Purpose]:
- [What it maintains 1]
- [What it maintains 2]
- [What it maintains 3]

**Features:**
- [Key sections]
- [Notable patterns]

Invoked automatically by `other-skill` or independently. [Additional context].
```

---

## Skill Chaining Reference Patterns

When updating the Skill Chaining Reference table:

### Adding new chaining relationship

```markdown
| `from-skill` | `to-skill` | When |
```

**Verify bidirectional reference:** If `from-skill` chains to `to-skill`, check if
`to-skill/SKILL.md` mentions being invoked by `from-skill`.

### Automatic invocation

```markdown
| `skill-name` | `invoked-skill` | Always (automatic if conditions) |
```

### Conditional invocation

```markdown
| `skill-name` | `invoked-skill` | When [specific condition] |
```

### Companion skills (not direct chaining)

```markdown
| `skill-name` | (companion: `other-skill`) | [Relationship description] |
```

---

## Edge Cases

| Situation | Action |
|-----------|--------|
| No staged changes and no diff provided | Run `git log --oneline -5` to show recent commits and ask which to analyze |
| README has no obvious matching section | Suggest best-fit section or propose new one |
| Large diffs (10+ skills changed) | Summarize themes rather than skill-by-skill; ask user to confirm scope |
| Skill renamed | Update ALL references (Skills section, Chaining table, How Skills Work Together, Repository Structure) |
| Generic `-principles` skill added | Note in Skills section that it's "not invoked directly, referenced via Prerequisites" |
| Cross-reference in SKILL.md but not README | Add to Skill Chaining Reference table |

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Applying changes without confirmation | User loses control of docs | Always wait for explicit YES |
| Updating for internal refactors | Creates noise in README | Only update for user-visible changes |
| Missing renamed skill in chaining table | Broken references | Search and replace all occurrences |
| Copying skill verbatim into README | Duplication, maintenance burden | Summarize key features only |
| Rewriting entire sections | Destroys user's voice | Surgical updates — preserve existing prose |
| Not reading README first | Proposals conflict with structure | Always read full file before proposing |
| Mentioning AI/tools in README | Breaks professional standards | Never mention Claude, AI, or tooling |
| Incomplete chaining updates | README diverges from actual chaining | When skill chaining changes, update table AND "How Skills Work Together" |

---

## Success Criteria

README.md update is complete when:

- ✅ README.md located and read
- ✅ Skill collection changes identified from staged diff
- ✅ Proposed updates formatted as before/after blocks
- ✅ User confirmed with explicit **YES**
- ✅ Changes applied to README.md
- ✅ File ready for staging (or user confirmed no changes needed)

**Not complete until** all criteria met and README.md reflects current skill collection.

---

## Skill Chaining

- **Invoked automatically by `git-commit`**: When committing in skills repositories,
  git-commit should invoke update-readme (if README.md exists and skill changes detected)
  to keep skill documentation in sync.
- **Works alongside `update-claude-md`**: While update-claude-md handles workflow
  guidance (CLAUDE.md), update-readme handles public-facing documentation (README.md).
- **Can be invoked independently**: User can run `/update-readme` directly when they
  want to sync README.md without committing.

**Note:** This skill is specific to skills repositories. For code repositories,
README updates are typically manual or handled by project-specific documentation tools.
