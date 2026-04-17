---
name: update-primary-doc
description: >
  Use when a primary document (VISION.md, THESIS.md, etc.) needs syncing with
  repository changes, or when invoked automatically by custom-git-commit.
  Only applies to type: custom projects with Sync Rules configured in CLAUDE.md.
---

# Primary Document Synchronization (Generic Base)

You are an expert in keeping primary documents synchronized with repository changes using user-configured sync strategies.

**This skill is generic and table-driven.** It has no knowledge of specific project types. All sync logic comes from the Sync Rules table in CLAUDE.md or from child skills that extend it.

## When to Use This Skill

**This is a foundation skill.** It's extended by project-specific skills:
- `java-update-design` - Extends with Java-specific mappings (DESIGN.md)
- `skills-update-readme` - Extends with skills-specific mappings (README.md)

**Direct invocation by:** `custom-git-commit` when Sync Rules are configured in CLAUDE.md (type: custom projects)

**Do NOT use this skill directly if:**
- Project type is `java` (use `java-update-design` instead)
- Project type is `skills` (use `skills-update-readme` instead)
- No Sync Rules table in CLAUDE.md (for type: custom)
- Sync Rules table is empty or template-only

## Core Principles

**Universal document sync patterns:**
- Read Primary Document path from CLAUDE.md or child skill
- Read Sync Rules from CLAUDE.md or child skill
- Match changed files against patterns
- Propose updates to appropriate document sections
- Validate before staging

## Core Rules

- **Read sync rules from CLAUDE.md** — never hardcode project knowledge
- **Match files against patterns** — use glob-style matching (*, **, exact paths)
- **Propose changes, don't apply** — return proposals to calling skill
- **Be section-aware** — understand document structure (headings, subsections)
- **Respect sync strategy** — different strategies have different behaviors

## Workflow

### Step 0 — Workspace mode detection

Before doing anything else, check whether this session is running inside a workspace:

```bash
ls design/JOURNAL.md 2>/dev/null && echo "workspace-mode" || echo "direct-mode"
```

- **Workspace mode** (file found): Do not sync to the primary doc directly. Instead, write a journal entry to `design/JOURNAL.md` using the entry format below. The primary doc is updated at epic close via `epic`. Skip Steps 1–7.
- **Direct mode** (file not found): Proceed with the existing Sync Rules workflow unchanged (Steps 1–7 below). No file is created; detection is silent.

**In workspace mode — journal entry format:**

```markdown
### YYYY-MM-DD · §SectionName · ADR-N (optional)

[Prose narrative: what changed in this section of the primary doc, why,
what decision was made. Focus on reasoning and context. 2-6 sentences.]
```

Use the exact section name from the project's primary document in the `§` anchor.
If an entry for this `§Section` already exists in `JOURNAL.md` → update it in place.
If this is a new section → append a new entry.

---

### Step 1 — Extract configuration from CLAUDE.md

Read CLAUDE.md to extract:
```bash
cat CLAUDE.md
```

Parse these fields from the Project Type section:
- **Primary Document:** path to the document to sync
- **Sync Strategy:** which sync pattern to follow
- **Sync Rules:** the table mapping files to document sections
- **Current Milestone:** (optional) for progress tracking

**If any required field is missing:**
Stop and tell calling skill:
> ⚠️  Configuration incomplete in CLAUDE.md. Missing: [field names]
>
> This skill requires Primary Document, Sync Strategy, and Sync Rules table.

### Step 1a: Discover document group

**After extracting primary document path, discover modular structure:**

```python
from scripts.document_discovery import discover_document_group
from pathlib import Path

group = discover_document_group(Path(primary_doc_path))
```

**This discovers:**
- Primary file: e.g., `docs/vision.md`
- Optional modules via:
  - Markdown links: `[Projects](docs/vision/projects.md)`
  - Include directives: `<!-- include: governance.md -->`
  - Section references: `§ Roadmap in docs/vision/roadmap.md`
  - Directory pattern: `docs/vision/*.md` files (if primary is `docs/vision.md`)

**Cache behavior:**
- First sync: Discovers modules, caches in `.doc-cache.json`
- Subsequent syncs: Uses cache (fast path, <10ms)
- Cache invalidation: Automatic on structure changes (new links, new files)

**Result:**
- Single-file document → `group.modules` is empty (backwards compatible)
- Modular document → `group.modules` contains linked files

**Continue with all files in the group (primary + modules).**

---

### Step 2 — Read staged changes

Accept staged diff from calling skill or read it:
```bash
git diff --staged --name-only
```

Get the list of changed file paths.

---

### Step 3 — Match files against sync rules

For each staged file, check if it matches any pattern in the Sync Rules table (column 1: "Changed Files").

**Pattern matching rules:**
- `catalog/*.md` matches any .md file in catalog/ directory
- `docs/**/*.md` matches any .md file in docs/ or subdirectories
- `VISION.md` matches exact file
- `*.yaml` matches any .yaml file in root
- Multiple patterns can be comma-separated: `src/*.java, test/*.java`

**For each match found:**
- Record the file path
- Record the target document section (column 2)
- Record the update type/guidance (column 3)

---

### Step 4 — Read current content

Read the full document(s) to understand existing structure before proposing changes.

**If modular (group.modules not empty):**
- Read primary document
- Read each module file
- Understand how content is split across files

**Parse document structure:**
- Identify all headings (## Section, ### Subsection, etc.)
- Find the sections mentioned in matched sync rules
- Note current content in those sections

**If primary document doesn't exist:**
Stop and tell calling skill:
> ❌ Primary document not found: {primary_doc_path}
>
> CLAUDE.md declares this path, but file doesn't exist.
> Create it first before syncing.

**If target sections don't exist:**
Note that they need to be created (include in proposal).

---

### Step 5 — Analyze changes and generate proposals

For each matched file → section mapping:

1. **Read the changed file** to understand what changed:
```bash
git diff --staged {file_path}
```

2. **Analyze the semantic meaning** of the change:
   - New content added? → May need new entry in primary doc
   - Content removed? → May need removal from primary doc
   - Content modified? → May need update in primary doc
   - Metadata changed? → May need status update in primary doc

3. **Apply sync strategy logic** (see Sync Strategies section below)

4. **Generate specific proposal** with:
   - Which section to update
   - What content to add/modify/remove
   - Why this change is needed (reference to changed file)

---

### Step 5a — Check for framework changes (UNIVERSAL)

**Framework changes = infrastructure that affects multiple files or introduces new capabilities.**

**Red flags that warrant primary document updates:**

| Pattern | Primary Doc Impact |
|---------|-------------------|
| **New scripts/ or tools/ files** | Document in Tools/Infrastructure section |
| **New validation/testing infrastructure** | Document in Quality Assurance or Methodology |
| **Same pattern across multiple files** | Framework change, document the pattern |
| **New automation or workflow capabilities** | Document in Process or Workflow sections |
| **New milestones or phases introduced** | Update milestone tracking |
| **New collaboration patterns** | Document in Governance or Team sections |

**Example:**
- **What happened:** A new automated linter added to the development workflow
- **Framework change:** All contributors now run lint checks before committing
- **Custom project impact:** If VISION.md/THESIS.md documents the workflow, update the relevant section

**If you detect framework changes, include them in proposals even if Sync Rules don't explicitly match.**

**This check applies to ALL type: custom projects.**

---

### Step 6 — Present proposals to calling skill

**For single-file primary document:**

Return a structured proposal in this format:

```markdown
## Primary Document Sync Proposal

**Primary Document:** {primary_doc_path}
**Sync Strategy:** {strategy_name}
**Files Analyzed:** {count} files matched sync rules

### Proposed Changes

#### Section: {section_name}

**Reason:** {file_path} changed - {brief description}

**Proposed update:**
```
[Specific markdown to add/modify in this section]
```

**Update type:** {Add new entry | Modify existing | Remove | Status update}

---

[Repeat for each section that needs updates]

### No Changes Needed

Files that matched sync rules but don't require primary doc updates:
- {file_path} - {reason why no update needed}
```

**For modular primary document (primary + modules):**

Group proposals by file:

```markdown
## Primary Document Sync Proposal

**Primary Document:** {primary_doc_path}
**Sync Strategy:** {strategy_name}
**Files Analyzed:** {count} files matched sync rules

### Proposed {primary_doc_path} updates

#### Section: {section_name}

**Reason:** {file_path} changed - {brief description}

**Proposed update:**
```
[Specific markdown to add/modify]
```

**Update type:** {Add new entry | Modify existing | Remove | Status update}

---

### Proposed docs/vision/projects.md updates

#### Section: {section_name}

**Reason:** {file_path} changed - {brief description}

**Proposed update:**
```
[Specific markdown to add/modify]
```

**Update type:** {Add new entry | Modify existing | Remove | Status update}
```

**Routing logic:**
- Match file path to sync rules
- Determine target section
- If section is in a module file → route there
- If section is in primary → route there
- If section location unclear → propose in primary

**If no updates needed:**
Return:
```markdown
## Primary Document Sync Proposal

**Primary Document:** {primary_doc_path}

No updates needed. Analyzed {count} files, none require primary document changes.
```

---

### Step 7 — Apply changes (only when called back)

**This skill does NOT apply changes automatically.**

The calling skill (`custom-git-commit`) will:
1. Show proposal to user
2. Get user confirmation
3. Call this skill back with approval to apply

**When called to apply (single-file):**
1. Use Edit tool to make each proposed change
2. Preserve existing document structure
3. Maintain consistent formatting
4. Update "Last Updated" metadata if document has it
5. **Validate the document:**
   ```bash
   python scripts/validate_document.py <primary-doc-path>
   ```
6. **If validation fails (exit code 1):**
   - Revert changes: `git restore <primary-doc-path>`
   - Report CRITICAL issues to calling skill
   - Calling skill should stop and ask user to fix manually
7. **If validation succeeds or has only warnings:**
   - Return success to calling skill
   - Document is ready for staging

**When called to apply (modular - primary + modules):**
1. Apply proposed changes to ALL affected files (primary + modules)
2. Preserve existing document structure in each file
3. Maintain consistent formatting across files
4. Update "Last Updated" metadata if files have it
5. **Validate entire document group:**
   ```python
   from scripts.validate_document import validate_document_group
   from scripts.document_discovery import discover_document_group
   from pathlib import Path

   group = discover_document_group(Path(primary_doc_path))
   issues = validate_document_group(group)
   ```
6. **If validation fails (CRITICAL issues):**
   - Revert ALL modified files:
     ```bash
     git restore docs/vision.md docs/vision/projects.md docs/vision/roadmap.md
     ```
   - Report CRITICAL issues to calling skill
   - Calling skill should stop and ask user to fix manually
7. **If validation succeeds or has only warnings:**
   - Return success to calling skill
   - All modified files ready for staging

**Validation checks for modular groups:**
- Link integrity: All `[links](file.md)` and `[links](file.md#section)` resolve
- Completeness: No orphaned modules (unreferenced from primary)
- No duplication: Substantial paragraphs not duplicated across files
- Individual file validation: Each file passes single-file corruption checks

---

## Sync Strategies

**Read [sync-strategies.md](sync-strategies.md)** for the full strategy definitions:
`bidirectional-consistency`, `research-progress`, `api-spec-sync`, `architectural-changes`,
and how to handle custom strategies.

---

## Section and Pattern Matching

**Read [pattern-matching.md](pattern-matching.md)** for section heading matching rules
and file glob pattern examples.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Hardcoding project knowledge | Not generic | Read everything from CLAUDE.md |
| Auto-applying changes | User didn't confirm | Only propose, let calling skill apply |
| Ignoring sync strategy | Wrong behavior | Each strategy has different rules |
| Pattern match too broad | Matches unrelated files | Tighten glob patterns in Sync Rules |
| Pattern match too narrow | Misses relevant files | Use ** for recursive matching |
| Not finding sections | Broken proposals | Use fuzzy heading matching |
| Creating duplicate entries | Primary doc gets messy | Check if entry already exists |

---

## Document Structure Check

*This check is part of the `performance` and `docs-sync` categories in `project-health`. For a full analysis: `/project-health performance docs-sync`. See [docs/project-health.md](../docs/project-health.md).*

After applying updates, run:

```bash
python scripts/validation/validate_doc_structure.py {primary_doc_path}
```

If exit code 1 or 2, follow the nudge workflow described in `java-update-design` § Document Structure Check — same conversation, same threshold adjustment, same CLAUDE.md persistence pattern. The `{primary_doc_path}` is whatever is declared in CLAUDE.md § Primary Document.

## Success Criteria

**In direct mode** (no `design/JOURNAL.md` present):

Primary document sync proposal is complete when:

- ✅ CLAUDE.md configuration read and validated
- ✅ Staged files matched against sync rules
- ✅ Primary document structure analyzed
- ✅ Changes analyzed per sync strategy
- ✅ Structured proposal generated
- ✅ Proposal returned to calling skill

**Application is complete when** (only if called back to apply):

- ✅ Each proposed change applied via Edit tool
- ✅ Document structure preserved
- ✅ Formatting consistent
- ✅ "Last Updated" metadata updated (if exists)
- ✅ **Document validation passed** (no CRITICAL corruption)
- ✅ Success returned to calling skill, document ready for staging

**Workspace mode is complete when** (`design/JOURNAL.md` exists):

- ✅ Architectural or content changes identified from staged diff
- ✅ Journal entry drafted with `§Section` anchor matching the changed primary doc section
- ✅ Entry written to (or updated in) `design/JOURNAL.md`
- ✅ User confirmed (or confirmed no design changes this session)

**Not complete until** all criteria for the active mode are met.

---

## Skill Chaining

**Invoked by:** `custom-git-commit` when Sync Rules configured

**Invokes:** None (this is a leaf skill)

**Complements:** `design-snapshot` — this skill keeps the primary doc *current* (mutable, always up to date); `design-snapshot` *freezes* a moment in time (immutable). Both coexist: update the living doc with one, record the milestone with the other.

**Can be invoked independently:** No, expects to be called by `custom-git-commit` with specific context

---

## Examples

See **[examples.md](examples.md)** for three worked examples:
working group catalog sync, research thesis sync, and API documentation sync.
