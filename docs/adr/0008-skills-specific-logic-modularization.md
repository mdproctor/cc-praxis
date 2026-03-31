# ADR-0008: Skills-Specific Logic Must Not Load in Non-Skills Projects

**Status:** Accepted

**Date:** 2026-03-30

**Context:** Token optimization for skills repository workflows

---

## Decision

Move skills-repository-specific workflows (SKILL.md validation, README synchronization) from portable skills to modular documentation files that only load in type: skills projects.

**Before (portable skills):**
```
skills/skill-review/SKILL.md (loads in all projects)
skills/skills-update-readme/SKILL.md (loads in all projects)
```

**After (modular documentation):**
```
skill-validation.md (only loads in type: skills)
readme-sync.md (only loads in type: skills)
```

**Key difference:** Modular files are referenced from CLAUDE.md (which loads automatically), but only when working in type: skills projects.

---

## Context

### The Problem

Skills for skills-repository management contained heavy reference material:

**skill-review/SKILL.md:**
- SKILL.md frontmatter validation rules (~150 lines)
- CSO compliance checklist (~100 lines)
- Flowchart validation procedures (~80 lines)
- Cross-reference verification (~120 lines)
- Deep analysis procedures (~200 lines)
- Common pitfalls tables (~150 lines)
**Total: ~800 lines**

**skills-update-readme/SKILL.md:**
- README section mapping tables (~150 lines)
- Skills section patterns (~200 lines)
- Chaining reference patterns (~100 lines)
- Edge case handling (~150 lines)
**Total: ~600 lines**

**Combined: ~1400 lines loaded in EVERY project (java, custom, generic)** <!-- nocheck:project-types -->

**The waste:**
- Java project (no SKILL.md files): Loads 1400 lines of irrelevant skills-specific logic
- Custom project (working groups): Loads 1400 lines of irrelevant skills-specific logic
- Generic project (simple scripts): Loads 1400 lines of irrelevant skills-specific logic

**Token cost:** ~70KB wasted per conversation in non-skills projects

## Decision Drivers

- **Token efficiency** - Don't load skills-specific logic in non-skills projects
- **Modularity** - Keep domain-specific logic domain-scoped
- **Maintainability** - Easier to update when not mixed with portable skills
- **Clarity** - Separation makes purpose obvious (portable vs repository-specific)
- **Scalability** - Pattern extends to other domain-specific workflows

## Considered Options

### Option 1: Keep Everything as Portable Skills (REJECTED)

**Approach:** skill-review and skills-update-readme as normal skills

**Pros:**
- Consistent (everything is a skill)
- Familiar pattern

**Cons:**
- ❌ Wastes ~70KB tokens in java/custom/generic projects <!-- nocheck:project-types -->
- ❌ Skills load even when never used
- ❌ Mixes portable skills with repository-specific workflows
- ❌ Doesn't scale (what about java-specific workflows?)

### Option 2: Create Separate Skill Collection for Skills Development (REJECTED)

**Approach:** Two skill collections - one for general use, one for skills development

```
claude-skills/          # General skills
claude-skills-dev/      # Skills development (skill-review, etc.)
```

**Pros:**
- Complete separation
- Zero token waste in general collection

**Cons:**
- ❌ Fragmentation (two collections to maintain)
- ❌ Discovery problem (which collection to use?)
- ❌ Duplication (some skills needed in both)
- ❌ Versioning complexity (keep both in sync)

### Option 3: Use Conditional Loading in Skills (REJECTED)

**Approach:** Skills check project type and early-exit

```markdown
# skill-review/SKILL.md

## Step 0: Check project type

```bash
cat CLAUDE.md | grep "Type: skills"
```

If not type: skills → exit early
```

**Pros:**
- Skills stay portable
- Exit early saves some processing

**Cons:**
- ❌ Still loads full skill body into context (~800 lines)
- ❌ Token waste (loading to check type)
- ❌ Complexity (every skill needs type check)
- ❌ Doesn't actually save tokens (loaded before executing)

### Option 4: Modularize as Documentation Files (ACCEPTED)

**Approach:** Move to modular documentation files referenced from CLAUDE.md

**Structure:**
```
skill-validation.md      # SKILL.md validation workflow
readme-sync.md          # README.md synchronization workflow
CLAUDE.md               # References these when needed
```

**CLAUDE.md references:**
```markdown
## Pre-Commit Checklist for Skills

**MANDATORY checks when committing changes to this repository:**

- [ ] **SKILL.md files modified?** → Follow skill-validation.md workflow
- [ ] **Skill changes detected?** → Follow readme-sync.md workflow (MANDATORY)
```

**git-commit (in type: skills mode):**
```markdown
### Step 1a — Review skills (if SKILL.md changes)

Check if any SKILL.md files are staged.

**If SKILL.md files found:**
- Follow the `skill-validation.md` workflow to validate structure
```

**Pros:**
- ✅ Zero token waste in non-skills projects (not loaded)
- ✅ CLAUDE.md loads automatically, references files when needed
- ✅ Clear separation (portable skills vs repository-specific workflows)
- ✅ Easy to maintain (all skills-specific logic in one place)
- ✅ Scales (can do same for java-specific workflows)

**Cons:**
- ⚠️ Not discoverable via skill list (but that's the point)
- ⚠️ Different invocation pattern (follow workflow vs invoke skill)

## Decision Outcome

**Chosen option:** Modularize as Documentation Files

**Implementation:**

### 1. Files Created

**skill-validation.md** (~400 lines):
- Frontmatter validation
- CSO compliance checking
- Flowchart validation
- Cross-reference verification
- Deep analysis procedures
- Only loads in type: skills projects

**readme-sync.md** (~300 lines):
- README section mapping
- Skills section patterns
- Chaining reference patterns
- Only loads in type: skills projects

### 2. CLAUDE.md References

**Added to CLAUDE.md § Skills-Repository-Specific Documentation:**
```markdown
Skills-repository-specific logic (SKILL.md validation, README synchronization)
is NOT implemented as portable skills. Instead, it lives in standalone
documentation files at the repository root:

| File | Purpose | Used By |
|------|---------|---------|
| **skill-validation.md** | SKILL.md validation workflow | `git-commit` when type: skills |
| **readme-sync.md** | README.md synchronization workflow | `git-commit` when type: skills |

**Why modularized (not skills):**
- These workflows only apply to THIS repository
- Loading them as skills wastes tokens in all other projects
- Heavy reference material (checklists, tables, patterns)
- CLAUDE.md loads automatically in every conversation
- git-commit references these when operating in type: skills mode
```

### 3. git-commit Integration

**Added type-aware invocation:**
```markdown
### Step 1a — Review skills (if SKILL.md changes)

**If type: skills AND SKILL.md files staged:**
- Follow the `skill-validation.md` workflow
- If CRITICAL findings → stop and ask user to fix

### Step 2b — Sync README.md (if skills repo)

**If type: skills AND skill changes detected:**
- **MANDATORY:** Follow the `readme-sync.md` workflow
- Let workflow decide if changes warrant documentation
```

### 4. Token Savings

**Before modularization:**
- skill-review: ~800 lines
- skills-update-readme: ~600 lines
- Total: ~1400 lines loaded in ALL projects

**After modularization:**
- skill-validation.md: ~400 lines (only in type: skills)
- readme-sync.md: ~300 lines (only in type: skills)
- Total in skills projects: ~700 lines
- Total in other projects: 0 lines

**Savings:** ~70KB per conversation in non-skills projects

## Consequences

### Positive

✅ **Massive token savings** - ~70KB per conversation in java/custom/generic projects <!-- nocheck:project-types -->
✅ **Clear separation** - Portable skills vs repository-specific workflows
✅ **Easier maintenance** - All skills-specific logic in dedicated files
✅ **Scalability** - Pattern extends to java-specific, custom-specific workflows
✅ **CLAUDE.md loads automatically** - No manual skill invocation needed
✅ **Domain-scoped** - Skills logic only loads where relevant

### Negative

⚠️ **Not in skill list** - Can't be invoked as `/skill-validation`
⚠️ **Different pattern** - "Follow workflow" vs "invoke skill"
⚠️ **Less discoverable** - Need to know about CLAUDE.md references

### Neutral

📝 **git-commit knows when to reference** - Type-aware invocation
📝 **Can still be read standalone** - Markdown files are navigable
📝 **Future: Could package as skills** - If we want cross-repository portability

## Validation

Success criteria for this ADR:

- ✅ skill-validation.md created (skills-specific logic)
- ✅ readme-sync.md created (skills-specific logic)
- ✅ CLAUDE.md documents pattern
- ✅ git-commit references workflows when type: skills
- ✅ Zero token waste in non-skills projects
- ✅ Token savings measured (~70KB)

## Extensibility Pattern

**This pattern extends to other project types:**

### Java-Specific Workflows (Future)

```
java-bom-validation.md      # Maven BOM alignment checks
java-test-coverage.md       # Java test coverage validation
CLAUDE.md                   # References when type: java
```

**CLAUDE.md § Java-Repository-Specific:**
```markdown
Java-repository-specific workflows live in:
- java-bom-validation.md (BOM alignment, dependency conflicts)
- java-test-coverage.md (minimum coverage, test quality)

Referenced by java-git-commit when appropriate.
```

### Custom-Specific Workflows (Future)

```
milestone-alignment.md      # Check changes match current milestone
bibliography-sync.md        # Sync papers/*.pdf to Bibliography section
CLAUDE.md                   # References when type: custom
```

**Result:** Each project type has domain-specific workflows that only load when relevant.

## Related Decisions

- **ADR-0008:** Skills-Specific Logic Modularization (this ADR establishes the pattern)
- **Token Optimization** (CLAUDE.md § Frontmatter Requirements)
- **Project Type Awareness** (CLAUDE.md § Project Type)

## Notes

**What we learned:**

Not everything should be a portable skill. Domain-specific workflows belong in domain-specific documentation.

**Key principle:**
> "If it only applies in one project type, don't make it a portable skill."

**The pattern:**
1. **Portable skills** - Work across all project types (git-commit, update-claude-md, code-review-principles)
2. **Modular workflows** - Work in one project type (skill-validation.md, readme-sync.md for type: skills)
3. **CLAUDE.md** - Bridges the two (loads automatically, references modular workflows when needed)

**Token economics:**
- Portable skills: Worth loading everywhere (high reuse)
- Modular workflows: Only worth loading in specific context (low reuse)

**Analogy:**
- Portable skills = Standard library (java.util, java.lang)
- Modular workflows = Domain-specific library (only imported when needed)

**Quote from token optimization review:**
> "Why are we loading 800 lines of SKILL.md validation in a Java project? There are no SKILL.md files here."

That question led to this ADR.

**Future consideration:**
If we need skills-specific workflows in OTHER projects (e.g., a project that consumes these skills), we could:
1. Package skill-validation.md as a proper skill
2. Make it conditional (check for SKILL.md files before loading)
3. Or keep it modular and copy when needed

For now, modular is correct - it only applies to THIS repository.
