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

Different strategies produce different behaviors when analyzing changes.

### bidirectional-consistency

**Philosophy:** Primary document and files stay synchronized bidirectionally.

**Rules:**
- New file → Add corresponding entry to primary doc
- File removed → Remove or mark deprecated in primary doc
- File modified → Update description/status in primary doc
- Section modified → Note in proposal, but don't modify files

**Use cases:** Working groups (catalog ↔ vision), documentation hubs

### research-progress

**Philosophy:** Primary document tracks research progress, files are evidence.

**Rules:**
- New analysis/experiment → Add to Methodology or Results section
- Paper added → Add to Bibliography section
- Data file added → Update Data Sources section
- Conclusion changes in files → Update Conclusions section

**Use cases:** Academic research, thesis projects

### api-spec-sync

**Philosophy:** Primary document is the spec, files implement it.

**Rules:**
- openapi.yaml changes → Update API Endpoints section
- example files added → Add to Examples section
- schema changes → Update Data Models section
- Spec changes → Note but don't auto-update (spec is authoritative)

**Use cases:** API documentation, OpenAPI specs

### architectural-changes

**Philosophy:** Primary document describes architecture, files implement it.

**Rules:**
- New service/component → Add to Architecture section
- Integration added → Update Integration Patterns
- Config changes → Note in Configuration section
- Removal → Mark as deprecated or remove from architecture

**Use cases:** Architecture Decision Records, system design docs

**Adding new strategies:**
Users can define custom strategies. If strategy is not recognized, use generic logic:
- Match files against patterns
- Propose additions for new files
- Propose updates for modified files
- Note removals

---

## Section Matching

When sync rules specify a section like "Vision - Current Landscape", find it using:

1. **Exact heading match:** `## Current Landscape` or `### Current Landscape`
2. **Partial match:** `## Vision and Current Landscape`
3. **Subsection:** `## Vision` → `### Current Landscape`

**If section not found:**
Include in proposal that the section needs to be created.

**Multiple sections:**
If sync rule says "Methodology, Results", update both sections.

---

## File Pattern Examples

From Sync Rules table, column 1:

| Pattern | Matches | Doesn't Match |
|---------|---------|---------------|
| `catalog/*.md` | `catalog/project.md` | `docs/catalog/project.md`, `catalog/sub/project.md` |
| `catalog/**/*.md` | `catalog/sub/project.md` | `other/catalog/project.md` |
| `docs/*.md, *.yaml` | `docs/guide.md`, `api.yaml` | `docs/sub/guide.md` |
| `VISION.md` | `VISION.md` (exact) | `docs/VISION.md` |
| `*.java` | `Test.java` | `src/Test.java`, `Test.kt` |
| `src/**/*.java` | `src/com/example/Test.java` | `test/com/example/Test.java` |

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

## Success Criteria

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

---

## Skill Chaining

**Invoked by:** `custom-git-commit` when Sync Rules configured

**Invokes:** None (this is a leaf skill)

**Can be invoked independently:** No, expects to be called by `custom-git-commit` with specific context

---

## Examples

### Example 1: Working Group Catalog Sync

**CLAUDE.md Sync Rules:**
```markdown
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| catalog/*.md | Vision - Current Landscape | Add project summary |
| docs/working-group/meeting-notes/*.md | Governance - Working Group | Add meeting summary |
```

**Staged files:**
- `catalog/langchain4j.md` (new file)

**Proposal:**
```markdown
## Primary Document Sync Proposal

**Primary Document:** docs/quarkus-ai-vision.md
**Sync Strategy:** bidirectional-consistency

### Proposed Changes

#### Section: Vision - Current Landscape

**Reason:** catalog/langchain4j.md (new) - New project cataloged

**Proposed update:**
```markdown
**LangChain4j Integration**
- Primary repository for LLM integrations in Quarkus
- Maintained by [maintainer name]
- Status: Active, production-ready
```

**Update type:** Add new entry
```

### Example 2: Research Thesis Sync

**CLAUDE.md Sync Rules:**
```markdown
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| experiments/*.py | Methodology - Experiments | Document experiment |
| papers/*.pdf | Bibliography | Add citation |
| data/*.csv | Data Sources | Add dataset reference |
```

**Staged files:**
- `experiments/baseline-test.py` (new file)

**Proposal:**
```markdown
## Primary Document Sync Proposal

**Primary Document:** THESIS.md
**Sync Strategy:** research-progress

### Proposed Changes

#### Section: Methodology - Experiments

**Reason:** experiments/baseline-test.py (new) - New experiment added

**Proposed update:**
```markdown
##### Baseline Performance Test

Experimental validation of baseline model performance across standard benchmarks.

**Implementation:** `experiments/baseline-test.py`
**Date:** 2026-03-30
**Status:** Initial results pending
```

**Update type:** Add new entry
```

### Example 3: API Documentation Sync

**CLAUDE.md Sync Rules:**
```markdown
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| openapi.yaml | API Endpoints | Sync endpoint documentation |
| examples/*.json | Examples | Add example |
```

**Staged files:**
- `openapi.yaml` (modified - new /users endpoint)

**Proposal:**
```markdown
## Primary Document Sync Proposal

**Primary Document:** docs/api-design.md
**Sync Strategy:** api-spec-sync

### Proposed Changes

#### Section: API Endpoints

**Reason:** openapi.yaml modified - New endpoint added: POST /users

**Proposed update:**
```markdown
##### POST /users

Creates a new user account.

**Request:**
- `email` (string, required)
- `name` (string, required)
- `role` (string, optional)

**Response:** 201 Created with User object

**Spec reference:** openapi.yaml line 145
```

**Update type:** Add new entry
```

```
