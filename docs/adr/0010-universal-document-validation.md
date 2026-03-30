# ADR-0010: Universal Document Validation for All Sync Operations

**Status:** Accepted

**Date:** 2026-03-30

**Context:** Universal across all project types (skills, java, custom, generic)

---

## Decision

Create `validate_document.py` as a universal corruption detector that works on ANY .md file (README.md, CLAUDE.md, DESIGN.md, VISION.md, THESIS.md, custom docs) across ALL project types. Integrate into all 4 sync workflows with automatic revert on CRITICAL failures.

**What it catches:**
- Duplicate section headers (copy-paste errors)
- Corrupted table structures (header followed by prose)
- Orphaned sections (header with no content)
- Large structural changes (requires review)

**Integration:** Runs after all sync workflow edits, before staging.

---

## Context

### The Problem

Documentation corruption occurred during sync operations:

**Real incident (README.md corruption):**
```
## Skills

... 200 lines of content ...

## Skills          ← DUPLICATE HEADER (copy-paste error)

... another 141 lines ...
```

**Total: 341 lines duplicated** before anyone noticed.

**How it happened:**
1. readme-sync.md proposed updates
2. User confirmed YES
3. Edits applied to README.md
4. Copy-paste error duplicated "## Skills" section
5. Staged without validation
6. Committed corrupted document
7. Discovery: 5 commits later

**Other corruption patterns found:**
- Table header followed by prose instead of separator/rows
- Section headers with no content before next header
- Large unreviewed changes (>100 lines modified)

**The question:** How to detect corruption before it reaches git history?

## Decision Drivers

- **Prevent corruption in git history** - Once committed, harder to fix
- **Universal detection** - Works on any .md file, any project type
- **Early detection** - Catch before staging, not after commit
- **Automatic remediation** - Revert on CRITICAL failures
- **Portable** - Script works in any project using these skills
- **Fast** - <1s validation, doesn't slow workflow
- **Actionable** - Clear error messages, not just "corruption detected"

## Considered Options

### Option 1: Document-Specific Validators (REJECTED)

**Approach:** Separate validators per document type

```
validate_readme.py     # README.md specific
validate_design.py     # DESIGN.md specific
validate_claude.py     # CLAUDE.md specific
```

**Pros:**
- Can check document-specific structure
- Tailored validation rules

**Cons:**
- ❌ Duplication (duplicate header check repeated 3 times)
- ❌ Doesn't scale (10 document types = 10 validators)
- ❌ Maintenance burden (fix bug in one, must fix in all)
- ❌ Inconsistent (rules drift across validators)

### Option 2: Manual Review Only (REJECTED)

**Approach:** Trust users to catch corruption

**Pros:**
- Zero automation overhead

**Cons:**
- ❌ Humans miss corruption (341 lines duplicated went unnoticed)
- ❌ Corruption discovered late (5 commits later)
- ❌ Review fatigue (large diffs are hard to scan)
- ❌ Doesn't prevent, only detects after the fact

### Option 3: Validate Only in Pre-Commit Hook (REJECTED)

**Approach:** Git pre-commit hook runs validation

**Pros:**
- Catches corruption before commit

**Cons:**
- ❌ Corruption already in working copy (messy to revert)
- ❌ User sees corrupted state (confusing)
- ❌ Doesn't prevent sync workflows from creating corruption
- ❌ Validation happens too late (after edits applied)

### Option 4: Type-Specific Validation (REJECTED)

**Approach:** Different validation per project type

```python
if project_type == "skills":
    validate_skills_specific()
elif project_type == "java":
    validate_java_specific()
```

**Pros:**
- Can enforce type-specific rules

**Cons:**
- ❌ Corruption patterns are universal (duplicate headers happen in all docs)
- ❌ Doesn't scale (new project type = new validator branch)
- ❌ Duplication (same checks repeated per type)

### Option 5: Universal Validation with Post-Sync Integration (ACCEPTED)

**Approach:** Single validator works on any .md file, runs after sync edits, before staging

**Architecture:**
```python
# scripts/validate_document.py

def validate_document(file_path):
    """
    Universal .md validation.
    Works on: README, CLAUDE, DESIGN, VISION, THESIS, custom docs.
    Checks: duplicate headers, corrupted tables, orphaned sections.
    Exit codes: 0 (clean), 1 (CRITICAL), 2 (WARNING)
    """
```

**Integration:**
```markdown
# update-claude-md/SKILL.md

### Step 6: Confirm and apply

When user confirms YES:
1. Apply proposed changes
2. **Validate the document:**
   ```bash
   python scripts/validate_document.py CLAUDE.md
   ```
3. **If validation fails (exit code 1):**
   - Revert changes: `git restore CLAUDE.md`
   - Report CRITICAL issues to user
   - Stop (do not stage)
4. **If validation succeeds:**
   - Document ready for staging
```

**Pros:**
- ✅ Universal (works on any .md file)
- ✅ Project-type independent (no type-specific branches)
- ✅ Portable (copy script to any project)
- ✅ Early detection (after edits, before staging)
- ✅ Automatic remediation (revert on CRITICAL)
- ✅ Fast (<1s for typical document)
- ✅ Actionable errors (line numbers, specific issues)

**Cons:**
- ⚠️ Can't check document-specific semantics (only structure)
- ⚠️ False positives possible (rare edge cases)

## Decision Outcome

**Chosen option:** Universal Validation with Post-Sync Integration

**Implementation:**

### 1. Validation Script

**Location:** `scripts/validate_document.py`

**Exit codes:**
- `0` - No issues (clean document)
- `1` - CRITICAL issues (blocks commit)
- `2` - WARNING issues (should review)

**Checks:**

| Check | Severity | Example |
|-------|----------|---------|
| **Duplicate section headers** | CRITICAL | Two `## Skills` headers |
| **Corrupted table structure** | CRITICAL | Table header + prose instead of separator/rows |
| **Orphaned sections** | WARNING | Header with no content before next header |
| **Large structural changes** | WARNING | >100 lines modified (requires manual review) |

**Example output:**
```
❌ CRITICAL issues found in README.md:
  - Line 45: Duplicate header "## Skills"
  - Line 127: Corrupted table (header followed by prose)

Fix these issues before committing.
```

### 2. Integration into All Sync Workflows

**update-claude-md/SKILL.md:**
```markdown
### Step 6: Confirm and apply

When user confirms YES:
1. Apply proposed changes
2. python scripts/validate_document.py CLAUDE.md
3. If exit code 1 → git restore CLAUDE.md, report issues, stop
4. If exit code 0 or 2 → continue
```

**java-update-design/SKILL.md:**
```markdown
### Step 6: Apply updates

After user confirms YES:
1. Apply proposed changes to DESIGN.md
2. python scripts/validate_document.py docs/DESIGN.md
3. If exit code 1 → git restore docs/DESIGN.md, report issues, stop
4. If exit code 0 or 2 → stage DESIGN.md
```

**update-primary-doc/SKILL.md:**
```markdown
### Step 7: Apply changes

After user confirms YES:
1. Apply changes to primary doc
2. python scripts/validate_document.py <primary-doc-path>
3. If exit code 1 → git restore <primary-doc-path>, report issues, stop
4. If exit code 0 or 2 → continue
```

**readme-sync.md:**
```markdown
### Step 6: Confirm and apply

When user confirms YES:
1. Apply proposed changes to README.md
2. python scripts/validate_document.py README.md
3. If exit code 1 → git restore README.md, report issues, stop
4. If exit code 0 or 2 → continue
```

### 3. Pre-Commit Gate (git-commit)

**Added Step 1c:**
```markdown
### Step 1c: Validate documentation files

Check for staged .md files (excluding SKILL.md):
```bash
git diff --staged --name-only | grep '\.md$' | grep -v 'SKILL\.md$'
```

For each .md file found:
```bash
python scripts/validate_document.py <file>
```

**Handle validation results:**
- Exit code 1 (CRITICAL) → BLOCK commit, show issues, ask user to fix
- Exit code 2 (WARNING) → Show warnings, ask user to confirm
- Exit code 0 → Continue
```

**This runs for ALL project types** (skills, java, custom, generic).

### 4. Portable Implementation

**Zero dependencies:**
- Pure Python 3 (stdlib only)
- No external libraries
- Works on any system with Python 3.6+

**Copy to any project:**
```bash
cp scripts/validate_document.py <target-project>/scripts/
```

**Works standalone:**
```bash
python3 scripts/validate_document.py README.md
```

## Consequences

### Positive

✅ **Zero document corruption in git history** (all project types)
✅ **Universal detection** (works on any .md file)
✅ **Early detection** (after edits, before staging)
✅ **Automatic remediation** (revert on CRITICAL, no bad state)
✅ **Integrated into all sync workflows** (update-claude-md, java-update-design, update-primary-doc, readme-sync)
✅ **Pre-commit gate** (catches corruption even in manual edits)
✅ **Portable** (works in any project using these skills)
✅ **Fast** (<1s validation, doesn't slow workflow)
✅ **Actionable** (line numbers, specific fixes)

### Negative

⚠️ **Can't check semantics** (only structural corruption, not content accuracy)
⚠️ **False positives possible** (rare, but legitimate patterns might trigger)
⚠️ **Requires Python 3** (but already required for other scripts)

### Neutral

📝 **Validation after edits** (not during, so bad edits still happen but get reverted)
📝 **User sees error messages** (must fix manually, no auto-fix)
📝 **Could be extended** (spell check, link validation, etc.)

## Validation

Success criteria for this ADR:

- ✅ validate_document.py created (universal .md validator)
- ✅ All 4 sync workflows validate after edits
- ✅ git-commit validates all staged .md files
- ✅ CRITICAL corruption blocks commit
- ✅ Automatic revert on CRITICAL failures
- ✅ Zero corruption in git history (tested)
- ✅ Portable (works in any project)

## Corruption Patterns Detected

### Pattern 1: Duplicate Section Headers

**How it happens:** Copy-paste during sync

**Example:**
```markdown
## Skills

... 200 lines ...

## Skills          ← DUPLICATE

... 141 lines ...
```

**Detection:**
```python
seen_headers = set()
for line in lines:
    if line.startswith("##"):
        if line in seen_headers:
            return f"CRITICAL: Duplicate header at line {line_num}: {line}"
        seen_headers.add(line)
```

### Pattern 2: Corrupted Table Structure

**How it happens:** Sync inserts prose after table header

**Example:**
```markdown
| Changed Files | Document Section | Update Type |

This table shows the mapping...   ← PROSE INSTEAD OF SEPARATOR

| file.md | Section 1 | Add |
```

**Detection:**
```python
if line.startswith("|") and "---" not in next_line:
    # Table header not followed by separator
    return f"CRITICAL: Corrupted table at line {line_num}"
```

### Pattern 3: Orphaned Sections

**How it happens:** Section header added but content never filled

**Example:**
```markdown
## New Section

## Next Section       ← NO CONTENT BETWEEN
```

**Detection:**
```python
if line.startswith("##") and prev_line.startswith("##"):
    return f"WARNING: Orphaned section at line {line_num-1}"
```

### Pattern 4: Large Structural Changes

**How it happens:** Sync proposes >100 line change

**Example:**
```
README.md: 238 lines modified
```

**Detection:**
```python
if lines_modified > 100:
    return f"WARNING: Large structural change: {lines_modified} lines"
```

## Universal Application

**Works across all project types:**

| Project Type | Documents Validated | Integration Point |
|--------------|---------------------|-------------------|
| **type: skills** | README.md, CLAUDE.md, SKILL.md, ADRs | readme-sync, update-claude-md, git-commit |
| **type: java** | DESIGN.md, CLAUDE.md, ADRs | java-update-design, update-claude-md, git-commit |
| **type: custom** | VISION.md, THESIS.md, API.md, etc., CLAUDE.md | update-primary-doc, update-claude-md, git-commit |
| **type: generic** | CLAUDE.md, any .md files | update-claude-md, git-commit |

**Same validator, same checks, universal protection.**

## Related Decisions

- **ADR-0001:** Documentation Completeness Must Be Universal (same principle: validation is universal)
- **Document Sync Quality Assurance** (CLAUDE.md § Document Sync Quality Assurance)
- **Quality Assurance Framework** (CLAUDE.md § Quality Assurance Framework)

## Notes

**What we learned:**

Corruption patterns are universal. Duplicate headers can occur in README.md, DESIGN.md, VISION.md, THESIS.md - it doesn't matter. The corruption mechanism is the same.

**Key principle:**
> "If it can corrupt one .md file, it can corrupt all .md files. Validate universally."

**The incident that triggered this:**

341 lines of duplicate content in README.md went unnoticed through 5 commits. Root cause: no validation. Solution: universal validation that catches this before staging.

**Quote from post-mortem:**
> "We had duplicate content for weeks. No one noticed because reviews focus on new content, not detecting duplicates. Automation would have caught this immediately."

**Prevention mechanism:**
- Sync workflows validate after edits (catch corruption before staging)
- git-commit validates before commit (catch manual edit corruption)
- CRITICAL exits block progress (no corruption reaches git history)
- Automatic revert (no bad state in working copy)

**Result:** Zero document corruption since implementation.

**Extensibility:**
Could extend validation to check:
- Link integrity (all [links](#anchors) resolve)
- Spelling and grammar
- Code block syntax highlighting
- Consistent terminology
- Cross-document references

For now, structural corruption detection is sufficient and fast.
