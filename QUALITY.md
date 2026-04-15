# Quality & Validation Framework

**Comprehensive quality assurance for all project types using these skills.**

This framework ensures reliability, consistency, and correctness across all documentation and code — whether you're maintaining Claude Code skills, building Java applications, writing research papers, or managing working group documentation.

---

## Table of Contents

- [Why Quality Matters](#why-quality-matters)
- [Quality Protection by Project Type](#quality-protection-by-project-type)
- [The Architecture: Scripts + Claude](#the-architecture-scripts--claude)
- [Tiered Validation](#tiered-validation)
- [What Gets Checked](#what-gets-checked)
- [Modular Documentation](#modular-documentation)
- [When Validation Runs](#when-validation-runs)
- [User Experience](#user-experience)
- [Implementation Status](#implementation-status)

---

## Why Quality Matters

**Quality issues in AI-guided development compound exponentially.** One bad instruction, one corrupted document, one missed safety check affects every subsequent decision.

### Without This Framework

**In Java projects:**
- ❌ Resource leaks slip through (file handles, connections left open)
- ❌ Blocking I/O on Vert.x event loop (runtime failures)
- ❌ OWASP vulnerabilities undetected (SQL injection, XSS, auth bypass)
- ❌ DESIGN.md drifts from code (architecture docs become lies)
- ❌ BOM version drift (dependency hell, runtime classpath conflicts)

**In custom projects:**
- ❌ VISION.md out of sync with catalog (team works from stale understanding)
- ❌ THESIS.md missing experimental results (research becomes incoherent)
- ❌ API design doc diverges from OpenAPI spec (implementation confusion)

**In skills projects:**
- ❌ Invalid Mermaid → skill fails to load → workflow blocked
- ❌ CSO violation → Claude ignores skill body → "expensive wallpaper"
- ❌ Broken cross-references → runtime errors when skills chain

**In all projects:**
- ❌ Corrupted tables in README/CLAUDE.md → parsing fails, docs unusable
- ❌ Duplicate headers → navigation breaks, search confusion
- ❌ Stale workflow instructions → commands fail, frustration, lost time
- ❌ Modular docs break silently → broken links, orphaned modules, sync only updates primary
- ❌ Large single-file docs → unmaintainable, merge conflicts, cognitive overload

### With This Framework

**In Java projects:**
- ✅ java-code-review blocks commits with resource leaks (CRITICAL findings)
- ✅ Event loop safety enforced (Red Flags section prevents rationalization)
- ✅ Security audit catches OWASP Top 10 before merge
- ✅ DESIGN.md auto-synced with architecture changes (validated before staging)
- ✅ BOM alignment checked on every dependency update

**In custom projects:**
- ✅ Primary document stays synchronized (corruption detection prevents drift)
- ✅ Sync rules enforced (file changes reflected in VISION/THESIS/API docs)
- ✅ User-configured validation (project-specific consistency)

**In skills projects:**
- ✅ Structural errors caught at creation (pre-commit gates)
- ✅ CSO compliance enforced (descriptions trigger correctly)
- ✅ Cross-reference integrity verified bidirectionally

**In all projects:**
- ✅ Document corruption prevented automatically (pre-commit + post-sync)
- ✅ Automatic revert on corruption (never reaches git history)
- ✅ Consistent quality (regression prevention, pressure-tested)
- ✅ Modular documentation with integrity guarantees (link validation, atomic sync, completeness checks)
- ✅ Split large docs without breaking (automatic discovery, cross-file validation, backwards compatible)

**Real impact:** The java-dev skill was tested under combined time pressure, authority pressure, and sunk cost bias — it successfully prevented resource leaks that baseline Claude (without the skill) introduced. This framework ensures that level of reliability across all project types.

---

## Quality Protection by Project Type

**Every project using these skills gets comprehensive quality protection tailored to its needs.**

### Universal Protection (All Project Types)

**Applies to:** skills, java, blog, custom, generic

| Protection | What It Prevents | When It Runs |
|------------|------------------|--------------|
| **Document corruption detection** | Duplicate headers, broken tables, orphaned sections | Pre-commit (all .md files) + post-sync (all sync workflows) |
| **CLAUDE.md sync accuracy** | Stale workflows, outdated commands, incorrect conventions | After update-claude-md applies changes |
| **Pre-commit gates** | Committing broken documentation | git-commit Step 1c (all project types) |
| **Automatic revert on corruption** | Corrupted docs reaching git history | All sync workflows validate before staging |
| **Link validation** | Broken internal/external links, missing anchors | On-demand or CI |
| **Example validation** | Code examples with syntax errors, broken commands | On-demand or CI |
| **Cross-document consistency** | Contradictions across CLAUDE.md, README.md, docs | On-demand (deep analysis) |

### Type: Java (Java/Maven/Gradle Projects)

**Applies to:** Projects with `pom.xml` or `build.gradle` that declare `type: java` in CLAUDE.md

| Protection | What It Prevents | When It Runs |
|------------|------------------|--------------|
| **java-code-review blocking** | Resource leaks, concurrency bugs, safety violations | Before commits (CRITICAL findings block) |
| **java-security-audit** | OWASP Top 10 vulnerabilities (injection, auth, crypto) | When security-critical code detected |
| **DESIGN.md sync accuracy** | Architecture docs drifting from code | After java-update-design applies changes |
| **DESIGN.md enforcement** | Missing architecture documentation | java-git-commit blocks if docs/DESIGN.md doesn't exist |
| **BOM alignment verification** | Version drift, dependency conflicts | maven-dependency-update workflow |
| **Quarkus event loop safety** | Blocking I/O on event loop threads | java-dev Red Flags section |
| **ADR enforcement** | Major upgrades without documenting decisions | maven-dependency-update detects major versions |

**Example:** Your Java project commits are protected by code review that blocks on resource leaks, security audit for auth code, DESIGN.md kept in sync with architecture changes, and BOM alignment checks preventing version drift.

### Type: Custom (Working Groups, Research, Documentation)

**Applies to:** Projects that declare `type: custom` in CLAUDE.md with user-configured sync rules

| Protection | What It Prevents | When It Runs |
|------------|------------------|--------------|
| **Primary doc sync accuracy** | VISION.md/THESIS.md/API.md drifting from work | After update-primary-doc applies changes |
| **User-configured validation** | Project-specific consistency violations | Custom validators in CLAUDE.md |
| **Sync rules enforcement** | File changes not reflected in primary doc | custom-git-commit reads Sync Rules table |
| **Milestone tracking** | Work not aligned with current phase/chapter | Commit messages reference current milestone |

**Example:** Your working group's VISION.md stays synchronized with catalog entries, research THESIS.md reflects experimental results, API design doc stays current with OpenAPI spec changes.

### Type: Skills (Skills Repositories)

**Applies to:** Repositories with `*/SKILL.md` files that declare `type: skills` in CLAUDE.md

| Protection | What It Prevents | When It Runs |
|------------|------------------|--------------|
| **SKILL.md structural validation** | Invalid frontmatter, broken flowcharts, missing sections | docs/development/skill-validation.md workflow (pre-commit) |
| **CSO compliance** | "Expensive wallpaper" (Claude ignores skill body) | validate_cso.py checks descriptions |
| **Cross-reference integrity** | Broken skill chains, dangling references | validate_references.py (bidirectional) |
| **README.md sync accuracy** | Skill catalog drifting from actual skills | After docs/development/readme-sync.md applies changes |
| **Naming convention enforcement** | Inconsistent skill hierarchy | validate_naming.py checks prefixes |
| **Flowchart validation** | Invalid Mermaid syntax | validate_flowcharts.py (PUSH tier) |

**Example:** This skills repository prevents skills with workflow summaries in descriptions, invalid Mermaid syntax, broken cross-references, and README drift.

### Type: Generic (Simple Projects)

**Applies to:** Projects that declare `type: generic` in CLAUDE.md or have no type declaration

| Protection | What It Prevents | When It Runs |
|------------|------------------|--------------|
| **Document corruption detection** | Same as universal | Pre-commit + post-sync |
| **CLAUDE.md sync (optional)** | Workflow docs drifting | After update-claude-md (if exists) |

---

## The Architecture: Scripts + Claude

**CRITICAL: Scripts cannot replace deep thought. This framework combines automated checks (fast, mechanical) with AI-assisted analysis (semantic, strategic).**

### Division of Labor

**Scripts** are **gatekeepers** — fast, always running, catch corruption:
- Check syntax, structure, format
- Validate links, references, file existence
- Detect duplicate headers, broken tables, orphaned sections
- Run in <2 seconds for commit-level checks
- Block CRITICAL mechanical errors

**Claude** is the **architect** — selective, deep analysis, ensure quality:
- Semantic contradictions ("Always X" vs "Never X" in same doc)
- Logical soundness (does workflow actually work?)
- Strategic completeness (missing error handling, edge cases)
- Cross-document consistency (do docs tell same story?)
- Quality judgment (is this explanation clear? best structure?)

**Hybrid approach** — scripts flag, Claude judges:
- Scripts identify potential issues quickly
- Claude provides semantic understanding and fixes
- User controls when deep analysis runs
- Both work together for comprehensive quality

### What Scripts CAN Check (Automated)

**Mechanical/Structural validation (no intelligence needed):**

| Check Type | Example | Universal |
|------------|---------|-----------|
| **Syntax errors** | Broken markdown, invalid YAML, malformed tables | ✅ All .md files |
| **Format violations** | Duplicate headers, missing sections, heading hierarchy | ✅ All .md files |
| **Broken references** | Links to non-existent files/sections, missing anchors | ✅ All documentation |
| **File existence** | "see docs/MISSING.md" when file doesn't exist | ✅ All referenced files |
| **Pattern matching** | CSO violations (SKILL.md), code block language tags | ✅ Universal where applicable |
| **Simple rules** | Frontmatter schema, table structure, list formatting | ✅ Type-specific + universal |

**Type-specific automated checks:**

| Project Type | Additional Checks | Why Type-Specific |
|--------------|------------------|-------------------|
| **type: skills** | SKILL.md frontmatter, CSO compliance, flowchart syntax | SKILL.md format is skills-specific |
| **type: java** | Java syntax, import organization, DESIGN.md required sections | Code structure rules |
| **type: custom** | User-defined validation rules (configurable) | User knows their domain |
| **type: generic** | None (universal checks only) | Minimal overhead |

### What Scripts CANNOT Check (Requires Claude)

**Semantic/Strategic analysis (requires understanding):**

| Check Type | Why Scripts Fail | Claude's Role |
|------------|------------------|---------------|
| **Semantic contradictions** | Scripts see valid paragraphs, can't detect "Always X" vs "Never X" conflict | Reads both, understands contradiction |
| **Logical flow** | Scripts see numbers, can't detect missing Step 3 in "Step 1, 2, 4" | Simulates execution, notices gap |
| **Nonsensical content** | Scripts see valid sentence, can't detect wrong tool for wrong job | Knows semantic meaning, detects error |
| **Strategic completeness** | Scripts can't know what SHOULD be there | Knows best practices, identifies gaps |
| **Cross-document consistency** | Scripts flag mentions, can't determine semantic conflict | Understands meaning, detects contradiction |
| **Quality judgment** | Subjective assessment | Applies judgment, suggests improvements |

### Example: Hybrid in Action

**Scenario: Potential contradiction detected**

```bash
# Scripts run during pre-push
python scripts/validate_consistency.py --level push

⚠️  WARNING: Potential contradiction detected:
   - git-commit/SKILL.md:24: "Never add attribution"
   - CLAUDE.md:156: "All commits include Co-Authored-By"

   Run deep analysis to verify? (Y/n)
```

**User invokes Claude:**
```
User: "Review git-commit skill for contradictions"

Claude analyzes:
1. Reads git-commit/SKILL.md full context
2. Reads CLAUDE.md § Committing changes
3. Understands git-commit changed rules recently
4. Reports: CRITICAL - CLAUDE.md is stale, needs update
```

**Result:** Script flagged issue (pattern matching), Claude provided semantic fix.

---

## Tiered Validation

**Proportional cost: light checks for small changes, heavy checks for big changes, heaviest for sharing.**

**Implementation:** 3 automated tiers matching `validate_all.py --tier <commit|push|ci>`

### COMMIT Tier (Pre-commit Hook) — <2s

**When:** Before `git commit`
**Goal:** Catch corruption before git history

**Checks:**
- ✅ **Duplicate section headers** (CRITICAL)
- ✅ **Corrupted table structures** (CRITICAL)
- ✅ **Orphaned sections** (WARNING)
- ✅ **Dangling references** ("see § X" where X doesn't exist)
- ✅ **Example syntax** (bash/python, no execution)
- ✅ **Cross-file links** (CLAUDE.md#section exists)
- ✅ Heading hierarchy (no skipped levels)
- ✅ Code blocks have language tags
- ✅ Basic markdown syntax

**Exit:** Blocks on CRITICAL, warns on WARNING (user can proceed)

**Example:**
```bash
git commit -m "docs: update readme"

# → Pre-commit hook runs automatically
🔍 Running commit-level validation...
✅ No duplicate headers
✅ No corrupted tables
✅ All links valid
✅ Validation passed (1.2s)
```

### PUSH Tier (Pre-push Hook) — <30s

**When:** Before `git push`
**Goal:** Ensure quality before sharing with others

**Checks:**
- ✅ All COMMIT tier checks
- ✅ **Cross-document consistency** (CLAUDE.md vs README.md vs SKILL.md)
- ✅ **Terminology consistency** ("primary doc" vs "main document")
- ✅ **Duplication detection** (same content in multiple files)
- ✅ **Structural quality** (markdownlint rules)
- ✅ **Spelling** (aspell/hunspell)

**Exit:** Blocks on CRITICAL, shows WARNING/NOTE summary

**Example:**
```bash
git push origin main

# → Pre-push hook runs
🔍 Running push-level validation...
✅ Cross-document consistency checked
⚠️  Terminology inconsistency: "primary doc" vs "main document" (3 files)
✅ Push validation passed (12s)
```

### CI Tier (GitHub Actions / Scheduled) — <5min

**When:** GitHub PR, scheduled nightly, before releases
**Goal:** Comprehensive analysis, catch everything

**Checks:**
- ✅ All COMMIT tier checks
- ✅ All PUSH tier checks
- ✅ **Functional tests** (git worktree isolation, skill execution)
- ✅ **Python quality** (mypy, flake8, bandit)
- ✅ **External URL validation** (HTTP requests)
- ✅ **Example execution** (run bash examples in sandbox)
- ✅ **Readability scoring** (Flesch-Kincaid)
- ✅ **Grammar** (LanguageTool)
- ✅ **Accessibility** (WCAG guidelines)

**Exit:** Fails PR if CRITICAL, comments with suggestions

**Example:**
```yaml
# In CI (GitHub Actions)
- name: Run full validation
  run: python scripts/validate_all.py --tier ci --verbose

# → Results posted as PR comment
```

### Performance Budget

| Tier | Target Time | Max Acceptable | Validators |
|------|-------------|----------------|------------|
| COMMIT | <1s | <2s | 7 validators |
| PUSH | <10s | <30s | 6 validators + tests |
| CI | <2min | <5min | All + functional tests |

**Optimization strategies:**
- Cache results (don't re-check unchanged files)
- Accumulative tiers (PUSH includes COMMIT, CI includes both)
- Parallel execution (multiple files concurrently)
- Incremental mode (only changed sections)
- Short-circuit on CRITICAL (fail fast)

---

## What Gets Checked

### Universal Checks (All Project Types)

**Document corruption (CRITICAL):**
- Duplicate section headers
- Corrupted table structures (header followed by prose)
- Orphaned sections (header with no content)
- Large structural changes (>100 lines modified)

**Link integrity (WARNING):**
- Internal anchor links (`[link](#section)`)
- Cross-document links (`[link](CLAUDE.md#section)`)
- File path references (`see docs/file.md`)
- External URLs (optional, can be slow)

**Code quality (WARNING):**
- Code blocks have language tags
- Bash/Python syntax validation
- Example commands don't use deprecated flags

**Structural quality (NOTE):**
- Heading hierarchy (no skipped levels)
- List formatting consistency
- Table formatting
- Line ending consistency (LF vs CRLF)

### Type-Specific Checks

**Type: skills only:**
- SKILL.md frontmatter (name, description fields)
- CSO compliance (description format)
- Flowchart syntax (Mermaid validation via mmdc, PUSH tier)
- Cross-reference integrity (bidirectional)
- Naming conventions (prefixes, hierarchies)

**Type: java only:**
- DESIGN.md exists (blocks commit if missing)
- DESIGN.md required sections present
- Java code safety (resource leaks, concurrency)
- OWASP Top 10 (for security-critical code)
- BOM alignment (dependency version drift)

**Type: custom only:**
- Primary document exists (path from CLAUDE.md)
- Sync Rules table format valid
- User-configured consistency checks

### Planned Checks (Roadmap)

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full planned check roadmap.

---

## Modular Documentation Quality Assurance

**Ensuring modular documentation maintains integrity across files with comprehensive cross-file validation.**

When documents split into modules (DESIGN.md → architecture.md + api.md + components.md), new failure modes emerge: broken links, orphaned modules, sync only updating primary file, duplicated content, inconsistent information. This framework prevents all of them.

**See README.md § Modular Documentation for user-facing feature explanation.**

### What Can Go Wrong

**Without cross-module validation:**

| Failure Mode | Impact | Example |
|--------------|--------|---------|
| **Broken links** | Users click link, 404, lose trust | `[API](api.md)` but `api.md` doesn't exist |
| **Invalid anchors** | Links go to file but wrong section | `[Auth](api.md#security)` but no `## Security` header |
| **Orphaned modules** | Module exists but nobody finds it | `components.md` exists but not linked from DESIGN.md |
| **Sync only updates primary** | Modules become stale | Code changes update DESIGN.md but not api.md |
| **Duplicate content** | Maintenance burden, conflicts | Same paragraph in DESIGN.md and architecture.md |
| **Inconsistent info** | Contradictions between files | DESIGN.md says 3-tier, architecture.md says 4-layer |

**All of these are prevented by the validation framework.**

### Cross-Module Validation Checks

**Link Integrity (CRITICAL):**
- Every `[link](file.md)` points to a file that exists
- Every `[link](file.md#section)` points to a section that exists in that file
- Anchor generation matches GitHub-style (lowercase, dashes, special chars removed)
- Broken links **block commit** (exit code 1)

**Anchor Resolution (WARNING):**
- File exists but section header doesn't match anchor
- Example: `[Link](api.md#authentication)` but only `## Auth` exists
- Reports warning, doesn't block (might be intentional abbreviation)

**Completeness (WARNING):**
- All module files referenced from primary (no orphans)
- Bidirectional references encouraged (module links back to primary or siblings)
- Orphaned modules reported as WARNING (might be work-in-progress)

**No Duplication (NOTE):**
- Substantial paragraphs (>100 chars) not duplicated across files
- Fuzzy matching detects near-duplicates
- Reports NOTE (duplication might be intentional for context)

**Document Structure (CRITICAL):**
- Each file individually validated (no duplicate headers within file)
- No corrupted tables in any module
- No orphaned sections in any module

### Atomic Validation and Revert

**The key insight: All files or none.**

When sync workflows update modular documents:

1. **Discover group:** Find all modules via links/includes/refs
2. **Propose updates:** User sees changes to ALL affected files
3. **Apply ALL changes:** Update primary + all modules together
4. **Validate entire group:** Run all cross-module checks
5. **If ANY check fails CRITICAL:**
   - `git restore DESIGN.md docs/design/architecture.md docs/design/api.md`
   - Revert **ALL files**, not just the one with the error
   - Report issues to user
   - **Nothing reaches git staging**

**This prevents partial corruption** - you never get DESIGN.md updated but api.md left stale.

### Test Coverage

**Unit tests (57 tests total):**

**test_document_discovery.py (21 tests):**
- Backwards compatibility: Single file returns empty modules list
- Markdown link parsing: `[text](file.md)` detection
- Include directive parsing: `<!-- include: file.md -->` detection
- Section reference parsing: `§ Section in file.md` detection
- Directory pattern: `docs/design/*.md` auto-discovery
- Circular reference detection: A→B→A cycle prevention
- Multiple reference types: Combines links + includes + directory patterns
- Cache key consistency: Same structure produces same key

**test_document_cache.py (13 tests):**
- Cache hit: Cached group returned when structure unchanged
- Cache invalidation: Structure change triggers re-discovery
- Cache valid after content change: Only structure matters for cache
- Corruption recovery: Invalid JSON triggers cache deletion and re-discovery

**test_modular_validator.py (23 tests):**
- Link integrity - all valid: No issues when links resolve
- Link integrity - broken link: `[Missing](missing.md)` → CRITICAL
- Link integrity - broken anchor: `[Link](file.md#nonexistent)` → WARNING
- Anchor exists: Verifies GitHub-style anchor generation
- Completeness - orphaned module: Module not referenced → WARNING
- Completeness - directory pattern: Auto-discovered modules don't need explicit reference
- Completeness - bidirectional: Module doesn't reference back → NOTE
- Duplication - duplicate paragraphs: Same >100 char content → NOTE
- Duplication - short content ignored: <100 char content not flagged
- Document group validation: Aggregates all checks, filters clean results

### Performance Characteristics

**Discovery performance:**
- First sync: ~100ms (parse primary, resolve links, check files)
- Cached sync: <10ms (read .doc-cache.json, deserialize)
- Cache invalidation: Automatic when structure changes (SHA256 mismatch)

**Validation performance:**
- Single-file validation: ~50ms (regex patterns, table parsing)
- Modular group validation: ~100-200ms (depends on module count)
- Link integrity check: ~10ms per file (filesystem lookups)
- Duplication detection: ~50ms per file pair (fuzzy matching)

**No performance penalty for single-file documents** - empty modules list short-circuits group validation.

### Integration Points

**All sync workflows integrate modular validation:**

| Workflow | Document | Validation Trigger |
|----------|----------|-------------------|
| **java-update-design** | DESIGN.md + modules | After applying proposals, before staging |
| **update-claude-md** | CLAUDE.md + modules | After applying proposals, before staging |
| **update-primary-doc** | User-configured + modules | After applying proposals, before staging |
| **docs/development/readme-sync.md** | README.md + modules | After applying proposals, before staging |

**git-commit universal validation:**
- Step 1c: Validates ALL staged .md files (single-file validation)
- Modular groups: Validated by sync workflows that created them

### Implementation

**Scripts (3 new files, 57 tests):**
- `scripts/document_discovery.py` (~400 lines) - Hybrid discovery via links/includes/refs/directory patterns
- `scripts/document_group_cache.py` (~200 lines) - SHA256-based caching with 24-hour expiration
- `scripts/modular_validator.py` (~350 lines) - Cross-module validation orchestration

**Extended scripts:**
- `scripts/validate_document.py` - Added `validate_document_group()` entry point

**Skills updated (4 workflows):**
- `java-update-design/SKILL.md` - Step 1a: discover group, Step 6: validate group
- `update-claude-md/SKILL.md` - Step 1a: discover group, Step 6: validate group
- `update-primary-doc/SKILL.md` - Step 1a: discover group, Step 7: validate group
- `docs/development/readme-sync.md` - Step 1a: discover group, Step 6: validate group

### Philosophy: Excellence in Documentation

**This framework embodies our belief in excellence:**

**Maintainability:**
- Large docs can split without losing sync
- Each module focused, easier to understand and edit
- Parallel editing (no merge conflicts)

**Reliability:**
- Cross-file integrity guaranteed
- Atomic updates (all files or none)
- Automatic revert on corruption

**Universality:**
- Same mechanism for all project types
- No type-specific branches in validation logic
- Backwards compatible (opt-in, not forced migration)

**Trust:**
- Users can split docs confidently knowing sync workflows handle it
- Links validated automatically
- No silent failures (broken links block commit)

**This is quality assurance at the documentation structure level** - ensuring not just that individual files are valid, but that the entire document group maintains coherence and integrity.

---

## When Validation Runs

### Automated (Always Running)

**Pre-commit (blocks CRITICAL issues):**
```bash
git commit -m "..."

# → .git/hooks/pre-commit runs automatically
# → validates all staged .md files
# → blocks if CRITICAL corruption detected
```

**Applies to:**
- All projects: Document corruption (git-commit Step 1c)
- Type: skills: SKILL.md structural validation
- Type: java: Code review (blocks on CRITICAL findings)

**Post-sync (automatic revert on failure):**
```bash
# After any sync workflow applies changes:
# → update-claude-md, java-update-design, update-primary-doc, docs/development/readme-sync.md
# → validates modified document
# → if CRITICAL issues → git restore <file> + stop
```

**Applies to:**
- All projects (if CLAUDE.md exists): update-claude-md
- Type: java: java-update-design
- Type: custom: update-primary-doc
- Type: skills: docs/development/readme-sync.md

**Pre-push (cross-document checks):**
```bash
git push origin main

# → .git/hooks/pre-push runs automatically
# → cross-document consistency, terminology, duplication
# → blocks if CRITICAL, warns on other issues
```

### User-Invoked (Selective)

**On-demand deep analysis:**
```bash
# Review specific skill
/skill-review java-code-review/SKILL.md

# Review staged code
/java-code-review

# Full repository validation
python scripts/validate_all.py

# Validate specific document
python scripts/validate_document.py docs/DESIGN.md
```

**When to invoke:**
- Before major changes (refactoring, restructuring)
- After significant additions (new skills, new features)
- When scripts flag WARNING that needs judgment
- Before releases or milestones
- Scheduled (weekly/monthly quality checks)

### CI/CD (Comprehensive)

**GitHub Actions (on PR, push, schedule):**
```yaml
# .github/workflows/validate-docs.yml
- name: Run full validation
  run: python scripts/validate_all.py --level full

# → Runs all automated checks
# → Optionally runs Claude deep analysis
# → Posts results as PR comment or artifact
```

---

## User Experience

### Developer Workflow

**Scenario: Editing README.md**

```bash
# 1. Edit file
vim README.md

# 2. Save triggers quick validation (editor plugin, optional)
# ✅ Quick checks pass (100ms)

# 3. Git add and commit
git add README.md
git commit -m "docs: update readme"

# → Pre-commit hook runs
# 🔍 Running commit-level validation...
# ✅ Validation passed

# 4. Push
git push origin main

# → Pre-push hook runs
# 🔍 Running push-level validation...
# ⚠️  Warnings:
#   - Terminology inconsistency: "primary doc" vs "main document" (3 files)
# ✅ Push validation passed (warnings don't block)

# 5. PR triggers CI
# → Full validation runs in GitHub Actions
# → Results posted as PR comment
```

**Scenario: Quick fix, bypass checks**

```bash
# Emergency typo fix
git commit -m "fix: typo in readme"
git push --no-verify  # Skip pre-push for urgent fix

# CI will still catch issues, but doesn't block immediate push
```

**Scenario: Deep analysis before release**

```bash
# Before major release, run comprehensive validation
python scripts/validate_all.py --level full --verbose

# Outputs comprehensive report:
# - 0 CRITICAL issues
# - 3 WARNING issues (terminology inconsistencies)
# - 12 NOTE suggestions (could improve examples)
# - Readability: Grade 11.2 (target: 10-12) ✅
# - Accessibility: 94% compliant
```

### Claude Deep Analysis Workflow

**When scripts flag potential issue:**

```bash
python scripts/validate_consistency.py

⚠️  WARNING: Possible contradiction:
   - git-commit/SKILL.md: "Never add attribution"
   - CLAUDE.md: "All commits include Co-Authored-By"

Run deep analysis? (Y/n) Y
```

**User invokes Claude:**

```
User: "Review git-commit for contradictions"

Claude:
1. Reads git-commit/SKILL.md full context
2. Reads CLAUDE.md § Committing changes
3. Semantic analysis: CLAUDE.md is stale
4. Reports fix: Update CLAUDE.md line 156
```

**Result:** Scripts identified potential issue, Claude provided understanding and fix.

---

## Implementation Status

### Currently Implemented ✅

**Universal (all project types):**
- ✅ `validate_document.py` — Document corruption detection
- ✅ Pre-commit validation (git-commit Step 1c)
- ✅ Post-sync validation (all sync workflows)
- ✅ Automatic revert on corruption
- ✅ Modular documentation support (primary + modules)

**Validation Infrastructure (19 validators across 3 tiers):**

**COMMIT Tier (<2s budget):**
- ✅ `validate_frontmatter.py` — YAML structure, required fields
- ✅ `validate_cso.py` — Description CSO compliance
- ✅ `validate_references.py` — Cross-reference integrity
- ✅ `validate_naming.py` — Naming conventions
- ✅ `validate_sections.py` — Required sections by type
- ✅ `validate_structure.py` — File organization
- ✅ `validate_project_types.py` — Project type list consistency
- ✅ `validate_blog_frontmatter.py` — Blog post frontmatter (layout, title, date, type fields)

**PUSH Tier (<30s budget):**
- ✅ `validate_flowcharts.py` — Mermaid syntax via mmdc (puppeteer, too slow for COMMIT), semantic labels
- ✅ `validate_cross_document.py` — Cross-document consistency
- ✅ `validate_temporal.py` — Stale references (deprecated tools, moved files)
- ✅ `validate_usability.py` — Readability, dense paragraphs, ambiguous pronouns
- ✅ `validate_edge_cases.py` — Edge case coverage, error handling
- ✅ `validate_behavior.py` — Behavioral consistency (invocation claims, blocking logic)
- ✅ `validate_readme_sync.py` — README/CLAUDE.md sync validation
- ✅ `validate_links.py` — External URL reachability (parallel HTTP, skip 403/429)
- ✅ `validate_examples.py` — Code fence balance (CRITICAL) + YAML/JSON syntax (WARNING)

**CI Tier (<5min budget):**
- ✅ `validate_python_quality.py` — mypy, flake8, bandit (static analysis)

**Test Infrastructure:**
- ✅ `run_skill_tests.py` — Functional test runner with git worktree isolation
- ✅ `run_regression_tests.py` — Regression test runner (prevents known issues)
- ✅ `test_coverage.py` — Coverage reporting (95% skills, 79 scenarios)
- ✅ `validate_all.py` — Master orchestrator with tier support

**Test Coverage Status:**
- ✅ 95% skill coverage (18/19 skills, 79 test scenarios)
- ✅ CI tier: 14 skills, 67 functional test scenarios
- ✅ PUSH tier: 4 foundation skills, 12 content validation scenarios
- ✅ Tier-appropriate testing (functional for invoke-able, content for foundation)

**Type: skills:**
- ✅ SKILL.md frontmatter validation (docs/development/skill-validation.md workflow)
- ✅ CSO compliance checking (prevents expensive wallpaper)
- ✅ Flowchart syntax validation (Mermaid, PUSH tier)
- ✅ Cross-reference integrity (bidirectional verification)
- ✅ README.md sync (docs/development/readme-sync.md)
- ✅ Comprehensive quality review complete (278 issues found, 2 CRITICAL fixed)

**Type: java:**
- ✅ Code review (java-code-review)
- ✅ Security audit (java-security-audit)
- ✅ DESIGN.md sync (java-update-design)
- ✅ DESIGN.md enforcement (blocks if missing)
- ✅ BOM alignment (maven-dependency-update)
- ✅ Modular DESIGN.md support (primary + architecture/api/data-model modules)

**Type: custom:**
- ✅ Primary document sync (update-primary-doc)
- ✅ Sync Rules enforcement (custom-git-commit)
- ✅ Modular document support (VISION.md, THESIS.md, etc. + modules)
- ✅ Table-driven sync configuration

**Comprehensive Quality Review (Completed 2026-03-30):**
- ✅ 26 commits created (validation + test infrastructure + fixes)
- ✅ 278 issues found and triaged (2 CRITICAL fixed immediately)
- ✅ ~2,800 lines of validation code
- ✅ ~1,500 lines of documentation
- ✅ All validators tested and working
- ✅ See `docs/comprehensive-quality-review-complete.md` for full report

### Planned Implementation

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full validation framework roadmap.

---

## Summary

**This framework provides:**

1. ✅ **Universal protection** — All .md files, all project types
2. ✅ **Type-specific validation** — Java code, SKILL.md, primary docs
3. ✅ **Tiered approach** — Fast for small, heavy for big, heaviest for sharing
4. ✅ **Hybrid validation** — Scripts catch corruption, Claude ensures quality
5. ✅ **Proportional cost** — Quick checks don't slow iteration
6. ✅ **Safety gates** — Corruption never reaches git history
7. ✅ **Continuous improvement** — Roadmap for world-class quality

**Benefits:**
- Developer-friendly (fast feedback, can bypass for emergencies)
- Comprehensive (nothing escapes CI full validation)
- Incremental (fix CRITICAL now, NOTE later)
- Extensible (add checks as needed)
- Universal (same principles, all project types)

**Result:** Production-grade quality by default, not by remembering to check.

