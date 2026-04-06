# ADR-0002: Project-Type-Specific Skills Must Use Type Prefix in Name

**Status:** Accepted
**Date:** 2026-03-30
**Deciders:** Mark Proctor, Claude (Sonnet 4.5)
**Context:** Naming inconsistency discovered - some project-specific skills lacked type prefix

---

## Context and Problem Statement

During naming consistency review, discovered that some project-type-specific skills did not follow the established naming convention used by `java-git-commit` and `custom-git-commit`.

**Inconsistencies found:**
- ❌ `update-design` (Java-only) → Should be `java-update-design`
- ❌ `update-primary-doc` (custom-only) → Should be `custom-update-primary-doc`
- ❌ `readme-sync.md` (skills-only workflow) → Should be `skills-update-readme` skill

**The established pattern** (from `git-commit` routing):
- `git-commit` (generic router)
- `java-git-commit` (Java-specific) ✓
- `custom-git-commit` (custom-specific) ✓

**Why this matters:**
- **Clarity** - Name indicates scope at a glance
- **Consistency** - All project-specific skills follow same pattern
- **Scalability** - Easy to add new project types (python-*, go-*, etc.)
- **Discoverability** - Can find all Java skills with `ls java-*`

## Decision Drivers

- **Consistency** - Established pattern exists, should apply everywhere
- **Clarity** - User knows skill scope from name alone
- **Scalability** - Pattern extends cleanly to future project types
- **Maintainability** - Easier to manage when naming is systematic
- **Incrementalism risk** - Creating skills one-at-a-time leads to pattern drift

## Considered Options

### Option 1: Keep current names (REJECTED)
Accept inconsistency, don't rename.

**Pros:**
- No breaking changes
- No reference updates needed

**Cons:**
- Naming remains inconsistent
- Pattern not established as standard
- Future skills may continue the inconsistency
- Harder to discover project-specific skills

### Option 2: Rename to follow convention (ACCEPTED)
Systematically rename all project-specific skills to include type prefix.

**Pros:**
- Establishes clear, consistent pattern
- Makes skill scope obvious from name
- Easy to extend to new project types
- Discoverable (can glob java-*, custom-*, skills-*)
- Aligns with existing git-commit pattern

**Cons:**
- Requires updating all references
- Git history shows rename
- One-time migration effort

### Option 3: Use suffixes instead of prefixes (REJECTED)
Example: `update-design-java`, `update-primary-doc-custom`

**Pros:**
- Groups by function rather than type

**Cons:**
- Breaks established pattern (git-commit → java-git-commit uses prefix)
- Harder to glob (`*-java` matches too broadly)
- Less clear visually

## Decision Outcome

**Chosen option:** Option 2 - Rename to follow type-prefix convention

**Naming convention established:**

| Scope | Naming Pattern | Examples |
|-------|----------------|----------|
| **Universal** (all types) | No prefix | `update-claude-md`, `git-commit` |
| **Java-specific** (type: java only) | `java-*` | `java-update-design`, `java-git-commit` |
| **Custom-specific** (type: custom only) | `custom-*` | `custom-update-primary-doc`, `custom-git-commit` |
| **Skills-specific** (type: skills only) | `skills-*` | `skills-update-readme` |
| **Generic foundations** | No prefix | `code-review-principles`, `dependency-management-principles` |

**Implementation:**

1. **Renames executed:**
   - `update-design/` → `java-update-design/`
   - `update-primary-doc/` → `custom-update-primary-doc/`
   - `readme-sync.md` → `skills-update-readme/SKILL.md`

2. **References updated in:**
   - All skill files (git-commit, java-git-commit, custom-git-commit)
   - Documentation (CLAUDE.md, README.md)

3. **Prevention mechanisms added:**
   - CLAUDE.md § Naming Conventions (documentation)
   - `scripts/validate_naming.py` (automated checking)
   - skill-review deep analysis (manual verification)

## Consequences

### Positive

- ✅ **Naming is now consistent** across all skills
- ✅ **Pattern is clear** for future skill authors
- ✅ **Scope is obvious** from skill name alone
- ✅ **Discoverable** via glob patterns (`java-*`, `custom-*`, `skills-*`)
- ✅ **Scalable** - easy to add `python-*`, `go-*`, `rust-*` skills
- ✅ **Self-documenting** - follows principle of least surprise

### Negative

- ⚠️ **Git history shows renames** - but git handles this well with `-M` flag
- ⚠️ **One-time migration effort** - already completed
- ⚠️ **Longer names** - but clarity outweighs brevity

### Neutral

- 📝 **Future project types inherit pattern** - e.g., `python-git-commit`, `python-update-design`
- 📝 **Validation script needs maintenance** - update indicators when new patterns emerge

## Validation

Success criteria for this ADR:

- ✅ All Java-specific skills prefixed with `java-`
- ✅ All custom-specific skills prefixed with `custom-`
- ✅ All skills-specific skills prefixed with `skills-`
- ✅ Universal skills have NO prefix
- ✅ Naming convention documented in CLAUDE.md
- ✅ Automated validation script exists
- ✅ skill-review includes naming check

## Related Decisions

- Established pattern: `git-commit` → `java-git-commit`, `custom-git-commit`
- ADR-0001: Documentation Completeness Must Be Universal (same root cause: incremental development blindness)

## Root Cause: Incremental Development Blindness

**Why we missed this:**
1. **Created skills one-at-a-time** - didn't review full set for patterns
2. **Focused on functionality** - validated behavior, not naming
3. **No automated checks** - pattern violations undetected
4. **No naming documentation** - no reference to check against
5. **Context window limits** - didn't see all skill names simultaneously

**Why this is a universal problem:**
- Same issue as ADR-0001 (missed documentation updates)
- Incremental work without systematic review leads to drift
- Human/AI memory is fallible, automation is not
- Patterns must be explicit, not assumed

## Prevention Mechanisms

### 1. Documentation (CLAUDE.md § Naming Conventions)

```markdown
## Naming Conventions

**Project-type-specific skills MUST use type prefix:**
- `java-*` for type: java only
- `custom-*` for type: custom only
- `skills-*` for type: skills only

**Universal skills use NO prefix:**
- `update-claude-md` (works in ALL project types)

**Check when creating a skill:**
1. Does this work in ALL project types? → No prefix
2. Does this work in ONE project type only? → Add type prefix
```

### 2. Automated Validation (scripts/validate_naming.py)

Scans all SKILL.md files, detects project-type specificity from content, validates name matches convention.

Exit code 1 if violations found.

### 3. Pre-Commit Integration

Can be added to git hooks or CI:
```bash
python3 scripts/validate_naming.py || exit 1
```

### 4. skill-review Enhancement

Deep analysis now includes naming convention check.

### 5. README Consistency Check

Future: `scripts/check_readme_sync.py` verifies skill names in README match actual directories.

## Examples for Future Project Types

**Adding Python support:**

Create skills following the pattern:
- `python-git-commit` - Python-specific commits
- `python-update-design` - Architecture doc sync
- `python-code-review` - Python-specific review

**All immediately discoverable:** `ls python-*` shows all Python skills.

**Adding Go support:**

Create skills following the pattern:
- `go-git-commit`
- `go-update-design`
- `go-code-review`

**Pattern is self-evident.**

## Notes

**Quote from user that triggered this ADR:**
> "you may want to rename a file. for example if update-design is java specific, maybe have the java prefix - like we do with git-commit and java-git-commit. Look for other places this naming convention for specific project types should be applied."

**Key insight:**
The pattern was established (git-commit → java-git-commit) but not applied consistently because it wasn't **explicitly documented as a convention**. Documentation + automation prevent drift.

**Related to ADR-0001:**
Both issues stem from incremental development without systematic review. Prevention requires:
1. Explicit documentation of patterns
2. Automated validation
3. Systematic review checklists
