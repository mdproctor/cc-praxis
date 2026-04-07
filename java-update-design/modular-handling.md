# Modular DESIGN.md Handling

Used by `java-update-design` when Step 1a reveals a modular DESIGN.md structure
(primary file + linked module files). Only load this if `group.modules` is non-empty.

---

## Step 1a — Discover document group

```python
from scripts.document_discovery import discover_document_group
from pathlib import Path

group = discover_document_group(Path("docs/DESIGN.md"))
```

**This discovers:**
- Primary file: `docs/DESIGN.md`
- Optional modules via:
  - Markdown links: `[Architecture](docs/design/architecture.md)`
  - Include directives: `<!-- include: components.md -->`
  - Section references: `§ API Details in docs/design/api.md`
  - Directory pattern: `docs/design/*.md` files

**Cache behavior:**
- First sync: Discovers modules, caches in `.doc-cache.json`
- Subsequent syncs: Uses cache (fast path, <10ms)
- Cache invalidation: Automatic on structure changes (new links, new files)

**Result:**
- Single-file DESIGN.md → `group.modules` is empty → use standard workflow
- Modular DESIGN.md → `group.modules` contains linked files → continue below

---

## Step 2 — Read modular content

- Read DESIGN.md (primary file)
- Read each module file listed in `group.modules`
- Understand how content is split across files

---

## Step 5 — Propose updates (modular)

Group proposals by file:

```
## Proposed docs/DESIGN.md updates

### Section: Architecture
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/design/architecture.md updates

### Section: Component Overview
**Replace:**
> <existing text>

**With:**
> <new text>

**Reason:** <rationale>

---

## Proposed docs/design/api.md updates

### Section: REST Endpoints
**Replace:**
> (new section)

**With:**
> ## New UserAPI Endpoints
> - `POST /api/users` - Create user
> - `GET /api/users/{id}` - Get user by ID

**Reason:** New UserController added
```

**Routing logic:**
- New @RestController → Update `docs/design/api.md` (if exists), else DESIGN.md § API
- New @Entity → Update `docs/design/data-model.md` (if exists), else DESIGN.md § Data Model
- New module → Update `docs/design/components.md` (if exists), else DESIGN.md § Components
- Cross-cutting change → Update DESIGN.md (primary always has high-level architecture)

---

## Step 6 — Confirm and apply (modular)

When user confirms YES:

1. Apply proposed changes to ALL affected files (primary + modules)
2. **Validate entire document group:**
   ```python
   from scripts.validate_document import validate_document_group
   from scripts.document_discovery import discover_document_group
   from pathlib import Path

   group = discover_document_group(Path("docs/DESIGN.md"))
   issues = validate_document_group(group)
   ```
3. **If validation fails (CRITICAL issues):**
   - Revert ALL modified files:
     ```bash
     git restore docs/DESIGN.md docs/design/architecture.md docs/design/api.md
     ```
   - Report CRITICAL issues to user; ask user to fix manually; stop (do not stage)
4. **If validation succeeds or has only warnings:**
   - Print summary: "✅ Updated files: DESIGN.md, docs/design/architecture.md, docs/design/api.md"
   - All modified files ready for staging

**Validation checks for modular groups:**
- Link integrity: All `[links](file.md)` and `[links](file.md#section)` resolve
- Completeness: No orphaned modules (unreferenced from primary)
- No duplication: Substantial paragraphs not duplicated across files
- Individual file validation: Each file passes single-file corruption checks
