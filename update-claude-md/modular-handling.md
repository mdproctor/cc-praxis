# Modular CLAUDE.md Handling

Used by `update-claude-md` when Step 1a reveals a modular CLAUDE.md structure
(primary file + linked module files). Only load this if `group.modules` is non-empty.

---

## Step 1a — Discover document group

```python
from scripts.document_discovery import discover_document_group
from pathlib import Path

group = discover_document_group(Path("CLAUDE.md"))
```

**This discovers:**
- Primary file: `CLAUDE.md`
- Optional modules via:
  - Markdown links: `[Workflows](docs/workflows/ci.md)`
  - Include directives: `<!-- include: patterns.md -->`
  - Section references: `§ Testing in docs/workflows/testing.md`
  - Directory pattern: `docs/workflows/*.md` files

**Cache behavior:**
- First sync: Discovers modules, caches in `.doc-cache.json`
- Subsequent syncs: Uses cache (fast path, <10ms)
- Cache invalidation: Automatic on structure changes (new links, new files)

**Result:**
- Single-file CLAUDE.md → `group.modules` is empty → use standard workflow
- Modular CLAUDE.md → `group.modules` contains linked files → continue below

---

## Step 2 — Read modular content

- Read CLAUDE.md (primary file)
- Read each module file listed in `group.modules`
- Understand how content is split across files

---

## Step 5 — Propose updates (modular)

Group proposals by file:

```
## Proposed CLAUDE.md updates

### Section: Development Tools
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/workflows/ci.md updates

### Section: Build Pipeline
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/workflows/testing.md updates

### Section: Test Commands
**Replace:**
> (new section)

**With:**
> ## New Test Commands
> - `npm test:integration` - Run integration tests
> - `npm test:e2e` - Run end-to-end tests

**Reason:** New testing infrastructure added
```

**Routing logic:**
- New build commands → Update `docs/workflows/build.md` (if exists), else CLAUDE.md § Development Commands
- New test patterns → Update `docs/workflows/testing.md` (if exists), else CLAUDE.md § Testing Patterns
- New tools → Update `docs/workflows/tools.md` (if exists), else CLAUDE.md § Development Tools
- Repository structure → Update CLAUDE.md (primary always has high-level structure)

---

## Step 6 — Confirm and apply (modular)

When user confirms YES:

1. Apply proposed changes to ALL affected files (primary + modules)
2. **Validate entire document group:**
   ```python
   from scripts.validate_document import validate_document_group
   from scripts.document_discovery import discover_document_group
   from pathlib import Path

   group = discover_document_group(Path("CLAUDE.md"))
   issues = validate_document_group(group)
   ```
3. **If validation fails (CRITICAL issues):**
   - Revert ALL modified files:
     ```bash
     git restore CLAUDE.md docs/workflows/ci.md docs/workflows/testing.md
     ```
   - Report CRITICAL issues to user
   - Ask user to fix manually
   - Stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print summary: "✅ Updated files: CLAUDE.md, docs/workflows/ci.md, docs/workflows/testing.md"
   - All modified files ready for staging

**Validation checks for modular groups:**
- Link integrity: All `[links](file.md)` and `[links](file.md#section)` resolve
- Completeness: No orphaned modules (unreferenced from primary)
- No duplication: Substantial paragraphs not duplicated across files
- Individual file validation: Each file passes single-file corruption checks
