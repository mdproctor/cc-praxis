# README Extraction — Architecture + Skills Catalog

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split README.md (1,779 lines) into three focused documents: README (~600 lines, entry point), docs/architecture.md (~150 lines, developer reference), docs/skills-catalog.md (~1,050 lines, full skill reference).

**Architecture:** Pure extraction — no content changes, only reorganisation. README replaces the extracted sections with a bridge section (bundle table + links). The `validate_readme_sync.py` validator is updated to check `docs/skills-catalog.md` instead of README for skill coverage.

**Tech Stack:** Markdown, Python (validator update), pytest.

---

## What Moves Where

| Content | Lines (approx) | Destination |
|---------|----------------|-------------|
| `## Skills Architecture` (layer diagram + 9-layer tables) | 199–348 | `docs/architecture.md` |
| `## Skills` (48-skill descriptions) | 349–1074 | `docs/skills-catalog.md` |
| `## Key Features` (bullet list pitch) | 1075–1092 | **STAYS in README** |
| `## Modular Documentation` (feature docs) | 1094–1381 | `docs/skills-catalog.md` |
| Everything else | 1–198, 1382–end | **STAYS in README** |

README gains a **bridge section** replacing lines 199–1381 (minus Key Features):
```markdown
## Skills

48 skills across three language stacks. [**Browse the full skill catalog →**](docs/skills-catalog.md)

Quick-start bundles — each gives immediate value with 3 skills:

| Bundle | Skills |
|--------|--------|
| **Quick Start: Java / Quarkus** | java-dev + java-code-review + java-git-commit |
| **Quick Start: TypeScript** | ts-dev + ts-code-review + git-commit |
| **Quick Start: Python** | python-dev + python-code-review + git-commit |

Install with `/install-skills` and pick a quick-start bundle. Full language bundles (Java: 10 skills, TypeScript: 5, Python: 5) are also available.

For the layered architecture showing how skills relate to each other: [**Skills Architecture →**](docs/architecture.md)

---
```

---

## File Map

| File | Action | Result |
|------|--------|--------|
| `README.md` | MODIFY | ~600 lines (from 1,779) |
| `docs/architecture.md` | CREATE | ~150 lines |
| `docs/skills-catalog.md` | CREATE | ~1,050 lines |
| `scripts/validation/validate_readme_sync.py` | MODIFY | Check skills-catalog.md instead of README |
| `tests/test_validate_readme_sync.py` | MODIFY | Update expectations |
| `tests/test_guide_page.py` | MODIFY | Add structural tests for new files |

---

## Task 1: Tests for new document structure (RED)

**Files:**
- Modify: `tests/test_guide_page.py`

- [ ] **Step 1: Add structural tests**

Add this class to `tests/test_guide_page.py` (after the existing classes):

```python
ARCHITECTURE_PATH = REPO_ROOT / 'docs' / 'architecture.md'
SKILLS_CATALOG_PATH = REPO_ROOT / 'docs' / 'skills-catalog.md'


class TestReadmeExtraction(unittest.TestCase):
    """Integration: README extraction produced correct documents."""

    def test_architecture_doc_exists(self):
        self.assertTrue(ARCHITECTURE_PATH.exists(),
                        'docs/architecture.md must exist')

    def test_skills_catalog_exists(self):
        self.assertTrue(SKILLS_CATALOG_PATH.exists(),
                        'docs/skills-catalog.md must exist')

    def test_readme_links_to_architecture(self):
        content = GUIDE_PATH.parent.parent / 'README.md'
        readme = content.read_text()
        self.assertIn('docs/architecture.md', readme,
                      'README must link to docs/architecture.md')

    def test_readme_links_to_skills_catalog(self):
        readme = (REPO_ROOT / 'README.md').read_text()
        self.assertIn('docs/skills-catalog.md', readme,
                      'README must link to docs/skills-catalog.md')

    def test_readme_under_800_lines(self):
        lines = (REPO_ROOT / 'README.md').read_text().splitlines()
        self.assertLess(len(lines), 800,
                        f'README should be under 800 lines after extraction, got {len(lines)}')

    def test_architecture_doc_has_layer_sections(self):
        content = ARCHITECTURE_PATH.read_text()
        self.assertIn('Layer 1', content)
        self.assertIn('Layer 9', content)

    def test_skills_catalog_has_skill_descriptions(self):
        content = SKILLS_CATALOG_PATH.read_text()
        # Should contain the skill description format
        self.assertIn('#### **git-commit**', content)
        self.assertIn('#### **java-dev**', content)
        self.assertIn('#### **python-dev**', content)

    def test_readme_still_has_key_features(self):
        readme = (REPO_ROOT / 'README.md').read_text()
        self.assertIn('Key Features', readme,
                      'Key Features section must remain in README')

    def test_readme_still_has_chaining_reference(self):
        readme = (REPO_ROOT / 'README.md').read_text()
        self.assertIn('Skill Chaining Reference', readme)

    def test_readme_has_bundle_table(self):
        readme = (REPO_ROOT / 'README.md').read_text()
        self.assertIn('Quick Start: Java', readme)
        self.assertIn('Quick Start: TypeScript', readme)
        self.assertIn('Quick Start: Python', readme)
```

- [ ] **Step 2: Run to confirm RED**

```bash
cd /Users/mdproctor/claude/cc-praxis
python3 -m pytest tests/test_guide_page.py::TestReadmeExtraction -v 2>&1 | tail -15
```

Expected: All 10 tests FAIL (files don't exist yet).

- [ ] **Step 3: Commit failing tests**

```bash
git add tests/test_guide_page.py
git commit -m "test(readme): structural tests for architecture.md and skills-catalog.md extraction — RED"
```

---

## Task 2: Create docs/architecture.md

**Files:**
- Create: `docs/architecture.md`

- [ ] **Step 1: Read the README to extract the Skills Architecture section**

The content to extract is the `## Skills Architecture` section from README.md, approximately lines 199–348 (from `## Skills Architecture` up to but not including `## Skills`).

- [ ] **Step 2: Create docs/architecture.md**

Create `/Users/mdproctor/claude/cc-praxis/docs/architecture.md` with this header + the extracted content:

```markdown
# cc-praxis — Skills Architecture

> **This document is extracted from the main README.** For installation and getting started: [README.md](../README.md) · For the full skill catalog: [skills-catalog.md](skills-catalog.md)

---

[paste the full ## Skills Architecture section content here, starting from "This collection follows a layered architecture..."]
```

The extracted content runs from the paragraph "This collection follows a layered architecture where foundation skills..." through the end of the last Layer table (Layer 9: Python Development), ending just before `## Skills`.

- [ ] **Step 3: Verify architecture.md is correct**

```bash
wc -l docs/architecture.md
head -5 docs/architecture.md
grep "Layer 1\|Layer 9" docs/architecture.md
```

Expected: file exists, contains both Layer 1 and Layer 9.

- [ ] **Step 4: Commit**

```bash
git add docs/architecture.md
git commit -m "docs: extract Skills Architecture to docs/architecture.md"
```

---

## Task 3: Create docs/skills-catalog.md

**Files:**
- Create: `docs/skills-catalog.md`

- [ ] **Step 1: Read README to identify exact extraction boundaries**

```bash
grep -n "^## Skills$\|^## Key Features\|^## Modular Documentation\|^## Skill Chaining" /Users/mdproctor/claude/cc-praxis/README.md | head -10
```

This gives the exact line numbers for:
- `## Skills` → start of skills descriptions
- `## Key Features` → STOP here for first block (keep Key Features in README)
- `## Modular Documentation` → start of second block to extract
- `## Skill Chaining Reference` → STOP here (keep everything from here onward in README)

- [ ] **Step 2: Create docs/skills-catalog.md**

Create `/Users/mdproctor/claude/cc-praxis/docs/skills-catalog.md` with:

```markdown
# cc-praxis — Skills Catalog

> **This document is extracted from the main README.** For installation and getting started: [README.md](../README.md) · For skills architecture: [architecture.md](architecture.md)

All 48 skills — descriptions, chaining relationships, and usage guidance. Install with `/install-skills` and pick the skills relevant to your stack.

---

[paste the full ## Skills section content, starting from "### Setup & Management" through to just before ## Key Features]

---

[paste the ## Modular Documentation section content through to just before ## Skill Chaining Reference]
```

The two extracted blocks are:
1. `## Skills` section: from line `### Setup & Management` through to (not including) `## Key Features`
2. `## Modular Documentation` section: from `## Modular Documentation` through to (not including) `## Skill Chaining Reference`

- [ ] **Step 3: Verify skills-catalog.md**

```bash
wc -l docs/skills-catalog.md
grep -c "#### \*\*" docs/skills-catalog.md
```

Expected: ~1,050 lines, 48+ skill heading matches.

- [ ] **Step 4: Commit**

```bash
git add docs/skills-catalog.md
git commit -m "docs: extract 48-skill catalog and modular docs to docs/skills-catalog.md"
```

---

## Task 4: Update README — add bridge section, remove extracted content

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Identify the exact lines to replace**

```bash
grep -n "^## Skills Architecture$\|^## Skill Chaining Reference$" /Users/mdproctor/claude/cc-praxis/README.md
```

This gives the exact start/end of the block to replace (lines 199 through ~1381).

- [ ] **Step 2: Replace extracted content with bridge section**

Remove all content between `## Skills Architecture` (inclusive) and `## Skill Chaining Reference` (exclusive), EXCEPT keep `## Key Features` and its content.

The replacement block to insert between `## Why This Collection Exists` and `## Key Features` is:

```markdown
## Skills

48 skills across three language stacks. [**Browse the full skill catalog →**](docs/skills-catalog.md)

Quick-start bundles — each gives immediate value with 3 skills:

| Bundle | Skills |
|--------|--------|
| **Quick Start: Java / Quarkus** | `java-dev` + `java-code-review` + `java-git-commit` |
| **Quick Start: TypeScript** | `ts-dev` + `ts-code-review` + `git-commit` |
| **Quick Start: Python** | `python-dev` + `python-code-review` + `git-commit` |

Install with `/install-skills` and pick a quick-start bundle. Full language bundles (Java: 10 skills, TypeScript: 5, Python: 5) are also available.

For the layered architecture showing how skills relate to each other: [**Skills Architecture →**](docs/architecture.md)

---
```

The resulting README structure should be:
1. Logo + tagline + value pitch (lines 1–13)
2. Quick Start (installation)
3. Overview + Project Type Setup
4. Why This Collection Exists
5. **[NEW] Skills** — bridge section with bundle table + links
6. Key Features (kept from original)
7. Skill Chaining Reference
8. Requirements
9. Contributing & Local Development
10. Quality & Validation Framework
11. Repository Structure
12. License

- [ ] **Step 3: Verify README length and content**

```bash
wc -l README.md
grep -c "#### \*\*" README.md  # Should be 0 — all skill blocks moved
grep "docs/skills-catalog.md\|docs/architecture.md" README.md
grep "Quick Start: Java\|Quick Start: TypeScript\|Quick Start: Python" README.md
```

Expected:
- README < 800 lines
- 0 `#### **` patterns (skill blocks moved out)
- Links to both new docs present
- Bundle table present

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(readme): replace 1,100-line skill catalog with bridge section linking to docs/"
```

---

## Task 5: Update validate_readme_sync.py — check skills-catalog.md

**Files:**
- Modify: `scripts/validation/validate_readme_sync.py`

The `get_skills_from_readme()` function currently scans README for `#### **skill-name**` patterns. With the catalog moved to `docs/skills-catalog.md`, this must check both files.

- [ ] **Step 1: Write a failing test**

Add to `tests/test_validate_readme_sync.py` (read the file first to understand existing tests, then add):

```python
def test_skills_catalog_checked_for_skill_coverage(self):
    """validate_readme_sync should find skills in docs/skills-catalog.md."""
    import subprocess
    result = subprocess.run(
        ['python3', 'scripts/validation/validate_readme_sync.py'],
        capture_output=True, text=True, cwd='/Users/mdproctor/claude/cc-praxis'
    )
    # Should not warn about skills missing from docs
    self.assertNotIn('Skills exist but not documented', result.stdout + result.stderr,
                     'validate_readme_sync should find all skills in skills-catalog.md')
```

Run to confirm it fails (validator will report skills missing from README):

```bash
python3 scripts/validation/validate_readme_sync.py 2>&1 | head -20
```

- [ ] **Step 2: Update get_skills_from_readme() to check skills-catalog.md**

In `scripts/validation/validate_readme_sync.py`, replace the `get_skills_from_readme()` function:

```python
def get_skills_from_readme() -> Set[str]:
    """Parse skills from README.md and docs/skills-catalog.md.

    After the README extraction, skill descriptions live in docs/skills-catalog.md.
    Check both files so validation works whether skills are in README or catalog.
    """
    skills = set()
    pattern = re.compile(r'####\s+\*\*([a-z][a-z0-9-]+)\*\*')

    for path in [Path('README.md'), Path('docs/skills-catalog.md')]:
        if not path.exists():
            continue
        content = path.read_text()
        for match in pattern.finditer(content):
            skills.add(match.group(1))

    return skills
```

- [ ] **Step 3: Run validator**

```bash
python3 scripts/validation/validate_readme_sync.py 2>&1
```

Expected: `✅ All documentation in sync` (or only expected warnings, no skill coverage issues).

- [ ] **Step 4: Run full commit-tier validators**

```bash
python3 scripts/validate_all.py --tier commit 2>&1 | tail -5
```

Expected: `8/8 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/validation/validate_readme_sync.py tests/test_validate_readme_sync.py
git commit -m "fix(validator): check docs/skills-catalog.md for skill coverage after README extraction"
```

---

## Task 6: Update Repository Structure + run full suite

**Files:**
- Modify: `README.md` (Repository Structure section)

- [ ] **Step 1: Add new docs to Repository Structure**

Find the `docs/` section in the Repository Structure block (search for `├── docs/`) and add the two new files:

```
│   ├── architecture.md              # Skills layered architecture — 9-layer diagram and tables
│   ├── skills-catalog.md            # Full 48-skill reference catalog with descriptions and usage
```

- [ ] **Step 2: Run all structural tests**

```bash
python3 -m pytest tests/test_guide_page.py::TestReadmeExtraction -v 2>&1 | tail -15
```

Expected: All 10 tests PASS.

- [ ] **Step 3: Run full test suite (non-Playwright)**

```bash
python3 -m pytest tests/ --ignore=tests/test_guide_ui.py -q --tb=line 2>&1 | tail -5
```

Expected: 1162+ tests pass.

- [ ] **Step 4: Commit and push**

```bash
git add README.md
git commit -m "docs(readme): add architecture.md and skills-catalog.md to Repository Structure"
git push
```

---

## Self-Review

**Spec coverage:**

| Requirement | Task |
|-------------|------|
| docs/architecture.md created with layer content | Task 2 |
| docs/skills-catalog.md created with 48-skill descriptions | Task 3 |
| README < 800 lines | Task 4 |
| README links to both new docs | Task 4 |
| Bridge section with bundle table | Task 4 |
| Key Features stays in README | Task 4 |
| Skill Chaining Reference stays in README | Task 4 |
| validate_readme_sync updated for skills-catalog.md | Task 5 |
| 8/8 validators pass | Task 5 |
| Repository Structure updated | Task 6 |

**Placeholder scan:** No TBD or TODO in any task.

**Content integrity:** The extraction is pure copy — no content is changed, only reorganised. The bridge section adds new content (bundle table, links) but removes nothing of value.

**Risk:** validate_readme_sync is the main breakage risk — addressed in Task 5 before the push.
