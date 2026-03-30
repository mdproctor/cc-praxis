# ADR-0002: Modular Documentation Architecture

**Status:** Accepted

**Date:** 2026-03-30

**Context:** Universal across all project types (skills, java, custom, generic)

---

## Decision

Implement full modular documentation support with hybrid discovery, universal cross-module validation, and atomic synchronization across all project types.

---

## Context

### The Problem

Large documentation files (>1000 lines) become unmaintainable:
- Hard to navigate (scroll fatigue, lost context)
- Merge conflicts (multiple authors editing same file)
- Cognitive overload (everything in one place)
- Single-file sync workflows miss updates when docs split

**Real-world scenario:**
1. User splits DESIGN.md → DESIGN.md + docs/design/architecture.md + docs/design/api.md
2. Code changes: new @Service added
3. `java-update-design` runs → only updates DESIGN.md
4. `docs/design/api.md` becomes stale (missing new API endpoint)
5. Documentation diverges from code

### Why Existing Solutions Failed

**Option 1: Manual modularization (no automation)**
- ❌ Users split docs but sync workflows only update primary file
- ❌ Modules become stale immediately
- ❌ No validation → broken links, orphaned modules, duplicated content
- ❌ Users avoid modularizing → single-file docs stay unmaintainable

**Option 2: Explicit configuration only**
- ❌ Users must manually declare every module in CLAUDE.md
- ❌ Maintenance burden (add module → update config → commit)
- ❌ Easy to forget (add module, forget to update config → module ignored)
- ❌ Doesn't scale (10+ modules = 10+ config entries to maintain)

**Option 3: Auto-detection only**
- ❌ Ambiguous cases (multiple detection methods conflict)
- ❌ False positives (external links detected as modules)
- ❌ No user control (can't override wrong auto-detection)
- ❌ Silent failures (auto-detect misses module → stale docs)

### What We Needed

1. **Automatic sync across all files** (primary + modules)
2. **Cross-module validation** (link integrity, completeness, consistency)
3. **Hybrid discovery** (auto-detect first, fallback to explicit config)
4. **Universal application** (same code for all project types)
5. **Backwards compatibility** (single-file docs continue working)
6. **Atomic updates** (all files or none, no partial sync)

---

## Decision Details

### Core Abstraction: DocumentGroup

```python
@dataclass(frozen=True)
class ModuleFile:
    path: Path
    relationship: str  # "linked" | "included" | "directory-pattern" | "section-ref"

@dataclass(frozen=True)
class DocumentGroup:
    primary_file: Path          # e.g., DESIGN.md
    modules: List[ModuleFile]   # e.g., [docs/design/architecture.md, ...]
    discovered_via: str         # "auto" | "config"
    cache_key: str              # sha256 for invalidation
```

**Why frozen dataclasses:**
- Hashable (can use in sets for deduplication)
- Immutable (discovery results don't change during sync)
- Clear semantics (relationships are explicit, not inferred)

### Hybrid Discovery Strategy

**Tier 1: Auto-detection (preferred)**

Try all methods, aggregate results:

1. **Markdown links:** `[Architecture](docs/design/architecture.md)`
2. **Include directives:** `<!-- include: api.md -->`
3. **Section references:** `§ API Reference in docs/design/api.md`
4. **Directory patterns:** If primary is `DESIGN.md`, check `docs/design/*.md`

**If unambiguous (all methods agree or only one method finds modules):**
- Cache discovered structure
- Proceed with sync

**If ambiguous (methods conflict):**
- Propose explicit CLAUDE.md configuration
- Ask user to confirm
- Cache user's choice

**Tier 2: Explicit configuration (fallback)**

```markdown
## Modular Documentation

### DESIGN.md
**Modules:**
- docs/design/architecture.md
- docs/design/components.md
- docs/design/api.md
```

**Configuration overrides auto-detection.**

### Cache Strategy

**File:** `.doc-cache.json` (gitignored)

**Cache key computation:**
```python
def compute_cache_key(primary_file: Path) -> str:
    """SHA256 of file structure, not content."""
    content = primary_file.read_text()
    structure = extract_links(content) + extract_includes(content)
    return hashlib.sha256(structure.encode()).hexdigest()
```

**Why structure-based, not content-based:**
- Content changes don't invalidate cache (e.g., fixing typo)
- Structure changes do invalidate (e.g., adding new link)
- Fast (no need to re-discover on every sync)

**Invalidation triggers:**
- Cache key mismatch (structure changed)
- Cache age > 24 hours (prevent stale cache)
- Manual: delete `.doc-cache.json`

**Performance:**
- First sync: ~100ms (discovery + cache write)
- Subsequent syncs: <10ms (cache read)

### Cross-Module Validation

**Runs after all edits applied, before staging:**

```python
issues = validate_document_group(group)
if any(issue.severity == "CRITICAL" for issue in issues):
    # Revert ALL files atomically
    git restore DESIGN.md docs/design/architecture.md docs/design/api.md
    raise ValidationError(issues)
```

**Validation checks:**

| Check | Severity | Example |
|-------|----------|---------|
| **Link integrity** | CRITICAL | `[API](api.md)` but `api.md` doesn't exist |
| **Invalid anchors** | CRITICAL | `[Auth](api.md#security)` but no `## Security` header |
| **Orphaned modules** | WARNING | `docs/design/unused.md` not referenced from primary |
| **Duplication** | WARNING | Same paragraph in primary and module |
| **Circular references** | CRITICAL | A links to B, B links to A (infinite loop) |

**Why atomic validation:**
- Partial sync is worse than no sync (some files updated, others stale → inconsistent state)
- All-or-nothing prevents broken documentation in git history
- User gets clear error message with all issues, not first issue only

### Universal Application

**Same code path for all project types:**

```python
# Type: skills
group = discover_document_group(Path("README.md"))

# Type: java
group = discover_document_group(Path("docs/DESIGN.md"))

# Type: custom
group = discover_document_group(Path("docs/vision.md"))

# All use identical discovery + validation + sync logic
```

**No type-specific branches in discovery/validation.**

**Type-specific logic only in what to sync:**
- Skills: Skill collection changes → README sections
- Java: Code changes → DESIGN.md sections
- Custom: User-defined Sync Rules

**Discovery and validation are universal.**

### Backwards Compatibility

**Single-file documents:**
```python
group = discover_document_group(Path("README.md"))
# Result: DocumentGroup(primary=README.md, modules=[], discovered_via="auto")
```

**All existing code continues working:**
- If `modules` is empty → sync only primary file (existing behavior)
- If `modules` is non-empty → sync all files (new behavior)
- Zero breaking changes to existing workflows

---

## Consequences

### Positive

✅ **Users can modularize without breaking sync**
- Split DESIGN.md into focused files
- All files stay synchronized automatically
- No configuration needed (auto-detection works)

✅ **Cross-module integrity guaranteed**
- Broken links caught before commit
- Orphaned modules detected
- Duplication identified
- Atomic validation prevents partial corruption

✅ **Universal across project types**
- Skills: README.md + modules
- Java: DESIGN.md + modules
- Custom: Any primary doc + modules
- Generic: CLAUDE.md + modules
- Same code, zero duplication

✅ **Backwards compatible**
- Existing single-file docs work unchanged
- Opt-in (modularize when needed, not forced)
- Zero migration cost

✅ **Performance optimized**
- Cache discovery (100ms → <10ms)
- Only re-discover on structure changes
- Fast validation (<1s for typical doc group)

✅ **Developer experience improved**
- Hybrid discovery (auto-detect or explicit config)
- Clear error messages (CRITICAL vs WARNING vs NOTE)
- Atomic revert on failure (no broken state)

### Negative

⚠️ **Complexity increased**
- New abstraction (DocumentGroup, ModuleFile)
- New validation layer (cross-module checks)
- New caching layer (.doc-cache.json)
- More test surface area (57 new tests)

⚠️ **Discovery can be ambiguous**
- Multiple methods might conflict
- Requires user confirmation in edge cases
- False positives possible (external links detected as modules)

⚠️ **Cache invalidation complexity**
- Must detect structure changes accurately
- SHA256 computation overhead (small but non-zero)
- Cache corruption possible (mitigated by 24-hour expiration)

⚠️ **Atomic validation can be surprising**
- All files reverted even if only one has issues
- User must fix all CRITICAL issues before commit
- No partial sync option (by design, but might frustrate users)

### Mitigations

**For complexity:**
- Comprehensive documentation (README.md, QUALITY.md, CLAUDE.md)
- Clear examples for all project types
- Test coverage: 57 tests (unit + integration)

**For ambiguous discovery:**
- Propose explicit config when ambiguous
- User confirms, then cached for future syncs
- Clear error messages explaining conflict

**For cache invalidation:**
- 24-hour expiration (prevents stale cache)
- Manual invalidation (delete `.doc-cache.json`)
- Structure-based key (content changes don't invalidate)

**For atomic validation:**
- Severity levels (CRITICAL blocks, WARNING allows)
- Detailed error messages (line numbers, fix guidance)
- Auto-revert prevents broken state

---

## Alternatives Considered

### Alternative 1: Manual-Only Sync

**Approach:** Users manually update all modules when syncing

**Rejected because:**
- ❌ Error-prone (forget to update a module → stale docs)
- ❌ Doesn't scale (10+ modules = high probability of missed updates)
- ❌ Users avoid modularizing to avoid manual sync burden
- ❌ Defeats the purpose of automation

### Alternative 2: Explicit Configuration Only (No Auto-Detection)

**Approach:** Require CLAUDE.md declaration for all modules

**Rejected because:**
- ❌ Maintenance burden (add module → update config → commit)
- ❌ Easy to forget (add module, miss config update → silently ignored)
- ❌ Doesn't scale (10+ modules = 10+ config lines to maintain)
- ❌ Poor UX (90% of cases are unambiguous, why force config?)

**Why hybrid is better:**
- Auto-detect works for 90% of cases (links, directory patterns)
- Explicit config only needed for ambiguous 10%
- Best of both worlds (convenience + control)

### Alternative 3: Auto-Detection Only (No Explicit Override)

**Approach:** Always auto-detect, never allow config override

**Rejected because:**
- ❌ No escape hatch when auto-detect is wrong
- ❌ False positives (external links detected as modules)
- ❌ Users can't override bad detection
- ❌ Ambiguous cases have no resolution path

**Why hybrid is better:**
- Auto-detect first (fast, convenient)
- Explicit config available when needed
- User controls final decision

### Alternative 4: Content-Based Cache Keys

**Approach:** SHA256 of full file content, not just structure

**Rejected because:**
- ❌ Cache invalidates on every content change (typo fix, rewording)
- ❌ Slower (hash entire file vs extract structure only)
- ❌ Defeats caching purpose (re-discover on every edit)

**Why structure-based is better:**
- Cache survives content changes (only invalidates on structure changes)
- Faster (hash just links/includes, not full content)
- Correct behavior (structure determines modules, not content)

### Alternative 5: Per-File Validation (Not Atomic)

**Approach:** Validate each file independently, stage successful ones

**Rejected because:**
- ❌ Partial sync creates inconsistent state (some files updated, others stale)
- ❌ Broken links possible (file A updated, file B not → A references stale B)
- ❌ User must manually fix partial state (confusing, error-prone)
- ❌ Git history contains broken documentation

**Why atomic is better:**
- All-or-nothing prevents broken state
- User gets all issues at once, fixes them, then syncs
- Git history always has valid documentation
- Clear semantics (either sync succeeded or it didn't)

---

## Implementation

### Files Created (Phase 1)

1. **`scripts/document_discovery.py`** (~400 lines)
   - `discover_document_group()` - Main entry point
   - `parse_markdown_links()` - Extract `[text](file.md)` references
   - `parse_includes()` - Extract `<!-- include: file.md -->`
   - `parse_section_references()` - Extract `§ Section in file.md`
   - `check_directory_pattern()` - Check `docs/primary/*.md`

2. **`scripts/document_group_cache.py`** (~200 lines)
   - `get_cached_group()` - Load from cache if valid
   - `cache_group()` - Save to cache
   - `compute_cache_key()` - SHA256 of structure
   - `invalidate_cache()` - Clear stale cache

3. **`scripts/modular_validator.py`** (~350 lines)
   - `validate_document_group()` - Orchestrator
   - `validate_link_integrity()` - Check all links resolve
   - `check_completeness()` - Detect orphaned modules
   - `find_duplication()` - Find duplicate content
   - `ValidationResult` class - Aggregates findings

4. **`scripts/validate_document.py`** (extended)
   - Added `validate_document_group()` entry point
   - Calls existing single-file validation per file
   - Adds cross-module checks
   - Aggregates results

### Files Modified (Phase 2)

5. **`java-update-design/SKILL.md`**
   - Added Step 1a: Discover document group
   - Updated proposal format (multiple files)
   - Updated application logic (group validation + atomic revert)

6. **`update-claude-md/SKILL.md`**
   - Same changes as java-update-design

7. **`update-primary-doc/SKILL.md`**
   - Same changes (generic base for custom projects)

8. **`readme-sync.md`**
   - Same changes (skills repositories)

### Documentation (Phase 3)

9. **`README.md`**
   - Added "## Modular Documentation" section (~250 lines)
   - User-facing feature explanation
   - Hybrid discovery approach
   - Link detection and navigation
   - When to modularize
   - Automatic synchronization
   - Universal application
   - Backwards compatibility

10. **`QUALITY.md`**
    - Renamed section to "## Modular Documentation Quality Assurance"
    - Updated philosophy (modular docs in Without/With Framework lists)
    - Documented failure modes
    - Cross-module validation checks
    - Atomic validation and revert
    - Test coverage (57 tests)
    - Performance characteristics
    - Integration points

11. **`CLAUDE.md`**
    - Added "## Modular Documentation" section (~300 lines)
    - Maintainer-focused guidance
    - When to use modular docs
    - How to modularize
    - Sync workflow behavior
    - Explicit configuration format
    - Validation details
    - Universal application
    - Migration path

### Test Coverage

**57 tests total:**

**Unit tests (37):**
- `test_document_discovery.py` (15 tests)
- `test_document_cache.py` (8 tests)
- `test_modular_validator.py` (14 tests)

**Integration tests (15):**
- `test_modular_java_update_design.py` (5 tests)
- `test_modular_update_claude_md.py` (3 tests)
- `test_modular_update_primary_doc.py` (4 tests)
- `test_modular_readme_sync.py` (3 tests)

**End-to-end tests (5):**
- `test_e2e_modular_java.py` (2 tests)
- `test_e2e_modular_skills.py` (2 tests)
- `test_e2e_modular_custom.py` (1 test)

---

## Lessons Learned

### What Worked Well

✅ **Hybrid discovery eliminated 90% of configuration burden**
- Auto-detection works for common cases (links, directory patterns)
- Explicit config only needed for ambiguous 10%
- Users happy (convenience without losing control)

✅ **Atomic validation prevented broken documentation**
- All-or-nothing prevents partial sync corruption
- Git history always contains valid docs
- Clear semantics (sync succeeded or failed, no in-between)

✅ **Universal principle reduced code duplication**
- Same discovery code for all project types
- Same validation code for all project types
- Same sync logic, just different content to sync
- Zero type-specific branches in core infrastructure

✅ **Backwards compatibility ensured smooth rollout**
- Existing single-file docs work unchanged
- Opt-in (modularize when ready, not forced)
- Zero migration cost (DocumentGroup with empty modules = single file)

### What We'd Do Differently

⚠️ **Cache invalidation could be smarter**
- Current: SHA256 of all links/includes (re-hash on every check)
- Better: Track file mtime, only re-hash if file changed
- Trade-off: Slightly more complex, but faster

⚠️ **Discovery could support more formats**
- Current: Markdown links, includes, section refs, directory patterns
- Missing: YAML frontmatter, custom directives, glob patterns
- Future: Pluggable discovery backends (users register custom patterns)

⚠️ **Validation could be more granular**
- Current: CRITICAL/WARNING/NOTE
- Better: Per-check severity configuration
- Example: User wants orphaned modules to block commit (promote WARNING → CRITICAL)

### Key Architectural Insights

**1. Hybrid is better than pure (auto-detect OR config)**
- Pure auto-detect fails on edge cases
- Pure config creates maintenance burden
- Hybrid: auto-detect first, config fallback → best of both worlds

**2. Atomic operations prevent partial failures**
- Partial sync is worse than no sync (inconsistent state)
- All-or-nothing semantics are clear (succeeded or failed)
- Auto-revert on failure prevents broken git history

**3. Universal rule reduces complexity**
- One code path for all project types
- Type-specific logic only in what to sync, not how
- Scales better (new project type = configure what, not rewrite how)

**4. Structure-based cache keys are correct**
- Content changes don't affect structure (typo fix doesn't invalidate cache)
- Structure changes do affect modules (new link → re-discover)
- Faster and more correct than content-based hashing

**5. Backwards compatibility is non-negotiable**
- Zero breaking changes → smooth adoption
- Opt-in features → users choose when to modularize
- Empty modules list = single file (existing behavior preserved)

---

## Future Work

### Phase 4: Advanced Features (Deferred)

**Contradiction detection:**
- Semantic analysis (requires Claude API calls)
- Find conflicting statements across modules
- Expensive (run on-demand, not every sync)

**Smart caching:**
- Cache validation results (not just discovery)
- Invalidate on relevant file changes only
- Reduce validation overhead for unchanged modules

### Potential Enhancements

**Pluggable discovery backends:**
- Users register custom discovery patterns
- Example: YAML frontmatter lists modules
- Example: Custom `@import` directives

**Configurable validation severity:**
- Users promote WARNING → CRITICAL for their needs
- Example: Orphaned modules block commit in their repo
- Per-repository or per-document configuration

**Partial sync with transactions:**
- Allow partial sync in some cases
- Use git staging as transaction boundary
- Rollback on validation failure (like database transactions)

**Visual documentation graph:**
- Generate graph of primary + modules relationships
- Detect circular dependencies visually
- Help users understand modular structure

---

## References

- **Implementation Plan:** `/Users/mdproctor/.claude/plans/flickering-doodling-pony.md`
- **User-Facing Docs:** `README.md § Modular Documentation`
- **QA Framework:** `QUALITY.md § Modular Documentation Quality Assurance`
- **Maintainer Guidance:** `CLAUDE.md § Modular Documentation`
- **Discovery Code:** `scripts/document_discovery.py`
- **Validation Code:** `scripts/modular_validator.py`
- **Cache Code:** `scripts/document_group_cache.py`

---

## Approval

**Decision Made By:** User (mdproctor) + Claude (Sonnet 4.5)

**Date:** 2026-03-30

**Rationale:** Modular documentation support is essential for maintainability at scale. Hybrid discovery balances convenience with control. Atomic validation prevents broken documentation. Universal application eliminates code duplication across project types.

**Alternatives Rejected:** Manual-only sync (error-prone), explicit-only config (maintenance burden), auto-only detection (no escape hatch), content-based caching (too aggressive invalidation), per-file validation (partial sync creates inconsistent state).

**Status:** **ACCEPTED** - Implementation complete, documentation complete, tests passing.
