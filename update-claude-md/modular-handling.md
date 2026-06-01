# Modular CLAUDE.md Handling

Used by `update-claude-md` when Step 1a reveals a modular CLAUDE.md structure
(primary file + linked module files). Only load this if `group.modules` is non-empty.

---

## Step 1a — Identify module files

The modular structure is detected in SKILL.md Step 1a via bash file-presence checks. By the time this file is loaded, you already know which module files exist.

**Treat the detected files as writable targets.** Understand what content each one owns:
- `docs/GOTCHAS.md` — pitfalls, workarounds, non-obvious behaviours
- `docs/FLYWAY.md` — migration versions, V-number rules, prerequisites
- `scripts/README.md` — build script reference, expected test times

Read CLAUDE.md and each present module file before proposing any changes.

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
2. **Validate links:** Check that any markdown links to module files resolve:
   ```bash
   grep -oE '\[([^\]]+)\]\(docs/[^)]+\)' CLAUDE.md | grep -oE 'docs/[^)]+' | while read -r p; do [ -f "$p" ] || echo "BROKEN LINK: $p"; done
   ```
3. **If broken links found:**
   - Revert affected files: `git restore CLAUDE.md` (and module files if changed)
   - Report to user; stop (do not stage)
4. **If no broken links:**
   - Print summary: "✅ Updated files: CLAUDE.md, docs/workflows/ci.md, docs/workflows/testing.md"
   - All modified files ready for staging

**Validation checks for modular groups:**
- Link integrity: All `[links](file.md)` and `[links](file.md#section)` resolve
- Completeness: No orphaned modules (unreferenced from primary)
- No duplication: Substantial paragraphs not duplicated across files
- Individual file validation: Each file passes single-file corruption checks
