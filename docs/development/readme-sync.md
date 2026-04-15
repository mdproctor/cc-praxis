# README.md Synchronization (Skills Repositories)

Maintains README.md documentation in sync with skill collection changes in skills
repositories. Detects when skills are added, removed, renamed, or chained differently,
and proposes updates to keep documentation accurate.

**Only for type: skills repositories.**

This workflow is invoked by `git-commit` when:
- CLAUDE.md declares `type: skills`
- README.md exists
- Staged changes include SKILL.md files or skill directory changes

**Do NOT use for:**
- type: java repositories (no automatic README sync)
- type: custom repositories (no automatic README sync)
- type: generic repositories (no automatic README sync)

## Prerequisites

**This skill extends `update-primary-doc`** with skills-repository-specific knowledge:

- **update-primary-doc**: Generic document sync patterns (read path, match files, propose updates, validate)

**Skills-specific additions:**
- Hardcoded Primary Document: `README.md`
- Hardcoded skill collection mappings:
  - New/removed SKILL.md → Update "Skills" section
  - Skill renamed → Update all references (Skills, Chaining table, Repository Structure)
  - New skill chaining → Update "Skill Chaining Reference" table
  - New features added → Update "Key Features" section

## Core Rules

- **Only operates in type: skills repositories** — other project types don't use automatic README sync
- README.md lives at repository root. Never move or rename it.
- **Never apply changes without explicit user confirmation** (a plain "YES" or equivalent).
- Focus on **skill collection changes**: new/removed skills, chaining modifications,
  feature additions, structural changes.
- Keep prose concise and professional. Preserve user's voice.
- Do not mention AI, LLMs, or tooling attribution in the document.

## Workflow

### Step 1: Locate README.md

```bash
ls README.md 2>/dev/null || echo "No README.md found"
```

- If found → proceed to Step 1a.
- If not found → this is not a skills repository (or README doesn't exist yet).

### Step 1a: Discover document group

**After locating README.md, discover modular structure:**

```python
from scripts.document_discovery import discover_document_group
from pathlib import Path

group = discover_document_group(Path("README.md"))
```

**This discovers:**
- Primary file: `README.md`
- Optional modules via:
  - Markdown links: `[Skills Guide](docs/readme/skills.md)`
  - Include directives: `<!-- include: chaining.md -->`
  - Section references: `§ Examples in docs/readme/examples.md`
  - Directory pattern: `docs/readme/*.md` files

**Cache behavior:**
- First sync: Discovers modules, caches in `.doc-cache.json`
- Subsequent syncs: Uses cache (fast path, <10ms)
- Cache invalidation: Automatic on structure changes (new links, new files)

**Result:**
- Single-file README.md → `group.modules` is empty (backwards compatible)
- Modular README.md → `group.modules` contains linked files

**Continue with all files in the group (primary + modules).**

### Step 2: Read current content

Read the full file to understand existing structure before proposing any changes.

**If modular (group.modules not empty):**
- Read README.md (primary file)
- Read each module file
- Understand how content is split across files

### Step 3: Collect the changes to analyze

In priority order:
1. **Staged changes**: `git diff --staged` (prefer this — it's what will be committed)
2. **Recent commit**: `git diff HEAD~1 HEAD` (if nothing staged)
3. **User-provided description** passed in context
4. Ask the user if none of the above yields anything useful.

### Step 4: Identify README impact

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

### Step 4a: Check for framework changes

**Framework changes = same pattern applied across multiple skills or new infrastructure.**

**If ANY of these are true, README.md likely needs updates:**

| Pattern | README.md Impact |
|---------|------------------|
| **New scripts/ files in staged changes** | Document in Repository Structure section |
| **CLAUDE.md gained new major sections** | May warrant Key Features section entry |
| **Multiple SKILL.md files modified with same pattern** | Framework change, document it |
| **New validation/testing infrastructure** | Update Skill Quality & Validation section |
| **New chaining pattern across skills** | Update How Skills Work Together section |
| **New documentation sync capability** | Update Key Features section |

**Recent example (learned from regression):**
- **What happened:** Validation added to 4 sync workflows (update-claude-md, java-update-design, update-primary-doc, readme-sync.md)
- **Framework change:** All sync workflows now validate documents before staging
- **README.md impact:** Should have updated:
  - Key Features: "Universal document validation"
  - Skill Quality & Validation: Document validation framework
  - Repository Structure: scripts/validate_document.py

**If you detect framework changes, include them in proposals even if no direct skill collection changes (new/removed/renamed skills).**

### Step 5: Propose updates

**For single-file README.md:**

Format each proposed change as a clear before/after block:

```
## Section: <Section Name>

**Replace:**
> <exact existing text, or "(new entry)">

**With:**
> <your proposed replacement text>

**Reason:** <one-sentence rationale>
```

**For modular README.md (primary + modules):**

Group proposals by file:

```
## Proposed README.md updates

### Section: Skills
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/readme/skills.md updates

### Section: Language-Specific Skills
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/readme/chaining.md updates

### Section: Automatic Invocations
**Replace:**
> (new entry)

**With:**
> | `java-git-commit` | `java-update-design` | Always (if docs/DESIGN.md exists) |

**Reason:** New automatic chaining relationship documented
```

**Routing logic:**
- New skill → Update `docs/readme/skills.md` (if exists), else README.md § Skills
- New chaining → Update `docs/readme/chaining.md` (if exists), else README.md § Skill Chaining Reference
- New features → Update `docs/readme/features.md` (if exists), else README.md § Key Features
- Repository structure → Update README.md (primary always has high-level structure)

If adding a brand-new section, say "Add after `<Section Name>`:" and show the
full new section.

Group related changes. If there are many, summarize them as a numbered list at
the top, then show each in detail below.

### Step 6: Confirm and apply

End every proposal with exactly:

> **Does this look good?**
> Reply **YES** to apply all changes, **NO** to discard, or describe what to adjust.

When the user confirms with YES (or a clear equivalent):

**For single-file README.md:**
1. Apply **only** the proposed changes — no extras.
2. **Validate the document:**
   ```bash
   python scripts/validate_document.py README.md
   ```
3. **If validation fails (exit code 1):**
   - Revert changes: `git restore README.md`
   - Report CRITICAL issues to user
   - Ask user to fix manually
   - Stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print a brief summary of what was written, e.g. "✅ Updated sections: Skills, Skill Chaining Reference."
   - Document is ready for staging

**For modular README.md (primary + modules):**
1. Apply proposed changes to ALL affected files (primary + modules)
2. **Validate entire document group:**
   ```python
   from scripts.validate_document import validate_document_group
   from scripts.document_discovery import discover_document_group
   from pathlib import Path

   group = discover_document_group(Path("README.md"))
   issues = validate_document_group(group)
   ```
3. **If validation fails (CRITICAL issues):**
   - Revert ALL modified files:
     ```bash
     git restore README.md docs/readme/skills.md docs/readme/chaining.md
     ```
   - Report CRITICAL issues to user
   - Ask user to fix manually
   - Stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print summary: "✅ Updated files: README.md, docs/readme/skills.md, docs/readme/chaining.md"
   - All modified files ready for staging

**Validation checks for modular groups:**
- Link integrity: All `[links](file.md)` and `[links](file.md#section)` resolve
- Completeness: No orphaned modules (unreferenced from primary)
- No duplication: Substantial paragraphs not duplicated across files
- Individual file validation: Each file passes single-file corruption checks

---

## Common Pitfalls

Avoid these mistakes when updating README.md:

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Using in non-skills repositories | Wrong project type, no auto-sync | Only invoke for type: skills repositories |
| Applying changes without confirmation | User loses control of docs | Always wait for explicit YES |
| Updating for internal refactors | Creates noise in README | Only update for user-visible changes |
| Missing renamed skill in chaining table | Broken references | Search and replace all occurrences |
| Copying skill verbatim into README | Duplication, maintenance burden | Summarize key features only |
| Not reading README first | Proposals conflict with structure | Always read full file before proposing |
| Mentioning AI/tools in README | Breaks professional standards | Never mention Claude, AI, or tooling |
| Incomplete chaining updates | README diverges from actual chaining | When skill chaining changes, update table AND "How Skills Work Together" |

## Success Criteria

README.md update is complete when:

- ✅ README.md located and read
- ✅ Skill collection changes identified from staged diff
- ✅ Proposed updates formatted as before/after blocks
- ✅ User confirmed with explicit **YES**
- ✅ Changes applied to README.md
- ✅ **Document validation passed** (no CRITICAL corruption)
- ✅ File ready for staging (or user confirmed no changes needed)

**Not complete until** all criteria met, validation passed, and README.md reflects current skill collection.

## Skill Chaining

**Invoked by:** [`git-commit`] when committing in skills repositories (automatic only if README.md exists AND skill changes detected via staged SKILL.md files or skill directory changes)

**Invokes:** None (terminal workflow in the chain)

**Can be invoked independently:** User can request README sync directly without committing

**Works alongside:** `update-claude-md` — while update-claude-md handles workflow guidance (CLAUDE.md), this handles public-facing documentation (README.md)

**Note:** This workflow is specific to skills repositories. For code repositories, README updates are typically manual or handled by project-specific documentation tools.

## Edge Cases

| Situation | Action |
|-----------|--------|
| No staged changes and no diff provided | Run `git log --oneline -5` to show recent commits and ask which to analyze |
| README has no obvious matching section | Suggest best-fit section or propose new one |
| Large diffs (10+ skills changed) | Summarize themes rather than skill-by-skill; ask user to confirm scope |
| Skill renamed | Update ALL references (Skills section, Chaining table, How Skills Work Together, Repository Structure) |
| Generic `-principles` skill added | Note in Skills section that it's "not invoked directly, referenced via Prerequisites" |
| Cross-reference in SKILL.md but not README | Add to Skill Chaining Reference table |
