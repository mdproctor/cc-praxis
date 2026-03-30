# Project Type Taxonomy

**Purpose:** Complete reference for all Claude Code project types, routing logic, and configuration patterns.

**For type: skills repositories:** See CLAUDE.md for skills-specific guidance. This document provides details on ALL project types for reference.

---

## Why Explicit Declaration Over Auto-Detection

**We tried auto-detection. It failed.**

**Problems we encountered:**
- Java project with extensive markdown docs → Detected as "docs project"
- Skills repo with example Java code → Detected as "Java project"
- Research project with code samples → Ambiguous
- Edge cases everywhere

**Solution: User declares explicitly in CLAUDE.md.**

**Benefits:**
- Zero ambiguity
- User controls behavior
- Clear intent
- Self-documenting

**Implementation:**
- `git-commit` reads CLAUDE.md first thing
- Routes to appropriate skill based on declared type
- If missing, interactively prompts user to declare it

---

### Type 1: Skills Repository (Built-in)

**Why this type exists:**
- Skills have specific structure (YAML frontmatter, CSO requirements)
- SKILL.md files need validation (frontmatter, cross-references, flowcharts)
- README.md must stay in sync with skill changes
- We understand skills deeply (we built this system)

**Declaration:**
```markdown
## Project Type

**Type:** skills
```

**What we know about skills:**
- `*/SKILL.md` files define skills
- Frontmatter must have `name` and `description`
- CSO rules: descriptions = WHEN to use, not HOW it works
- Cross-references must be bidirectional
- Flowcharts use Graphviz dot notation
- README.md documents the skill collection

**Built-in Behavior:**
```
git-commit (for type: skills)
  ├─ skill-review (validates SKILL.md if staged)
  │   └─ Blocks on CRITICAL findings
  ├─ readme-sync.md (syncs README.md if skill changes)
  ├─ update-claude-md (syncs CLAUDE.md if exists)
  └─ Conventional commit
```

**Sync Logic (Hardcoded):**
- `readme-sync.md` knows: SKILL.md changes → update Skills section, chaining table
- `skill-review` knows: Check frontmatter format, CSO compliance, cross-refs

**This type is ONLY for skills repositories.** Don't use for other documentation projects.

---

### Type 2: Java/Maven/Gradle (Built-in)

**Why this type exists:**
- Java architecture has known patterns (layers, components, modules)
- DESIGN.md serves specific purpose (architecture documentation)
- We understand Java domain models (@Entity, @Service, @Repository, etc.)
- We can map code changes to architectural concepts

**Declaration:**
```markdown
## Project Type

**Type:** java
```

**What we know about Java projects:**
- `pom.xml` or `build.gradle` define build
- `docs/DESIGN.md` documents architecture (REQUIRED)
- Code organized in packages/modules
- Annotations indicate architectural roles (@Entity, @Service, etc.)
- Dependencies managed via BOM patterns

**Built-in Behavior:**
```
java-git-commit (for type: java)
  ├─ Check DESIGN.md exists (BLOCKS if missing)
  ├─ java-code-review (if not done this session)
  │   └─ java-security-audit (for security-critical code)
  ├─ java-update-design (syncs DESIGN.md with code changes)
  │   └─ Maps .java changes to architecture sections
  ├─ update-claude-md (syncs CLAUDE.md if exists)
  └─ Conventional commit with Java-specific scopes
```

**Sync Logic (Hardcoded):**
- `java-update-design` knows: New @Entity → Update "Domain Model" section
- `java-update-design` knows: New module in pom.xml → Update "Component Structure"
- `java-code-review` knows: Check for safety violations, concurrency bugs

**This type is ONLY for Java/Maven/Gradle projects.** Don't use for other code projects.

---

### Type 3: Custom (User-Configured)

**Why this type exists:**
- Catch-all for projects with special documentation needs
- Every project is different (working groups ≠ research ≠ API docs)
- We CAN'T hardcode sync logic for all possible project types
- User knows their domain, we provide the mechanism

**Declaration (Full Configuration Required):**
```markdown
## Project Type

**Type:** custom
**Primary Document:** docs/vision.md  # Path to main document

**Sync Strategy:** bidirectional-consistency  # Built-in or custom

**Sync Rules:**
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| `docs/catalog/*.md` | Section 2 "Projects" | Add/update entries |
| `examples/*/` | Section 3 "Examples" | Mark completed |

**Consistency Checks:**
- All catalog entries referenced in vision exist
- Metadata headers present on major docs

**Current Milestone:** Phase 1 - Discovery
```

**User-Configured Behavior:**
```
custom-git-commit (for type: custom)
  ├─ Verify Primary Document exists (path from CLAUDE.md)
  ├─ Read Sync Rules table from CLAUDE.md
  ├─ update-primary-doc (generic, table-driven)
  │   ├─ Match staged files against patterns
  │   └─ Propose updates to specified sections
  ├─ Optional validators (if configured)
  │   ├─ validate-milestone-alignment
  │   └─ validate-metadata
  ├─ update-claude-md (syncs CLAUDE.md)
  └─ Conventional commit
```

**Sync Logic (User-Defined):**
- We read the Sync Rules table
- Match files using patterns in column 1
- Propose updates to sections in column 2
- Follow guidance in column 3
- NO hardcoded knowledge of the project

**Examples of Custom Projects:**

**Working Group (e.g., Quarkus AI Initiative):**
- Primary Document: `docs/quarkus-ai-vision.md`
- Sync: catalog entries → Vision Section 2, examples → Section 3
- Milestone: Phase-based (Phase 1, Phase 2, etc.)

**Research Project:**
- Primary Document: `THESIS.md`
- Sync: experiments → Methodology, papers → Bibliography
- Milestone: Chapter-based (Chapter 3, Chapter 4, etc.)

**API Documentation:**
- Primary Document: `docs/api-design.md`
- Sync: openapi.yaml → API Endpoints, examples → Examples section
- Milestone: Version-based (v2.1.0, v3.0.0, etc.)

**Standards/Specification:**
- Primary Document: `SPECIFICATION.md`
- Sync: implementations → Adoption, issues → Decisions
- Milestone: Draft status (WD, CR, PR, REC)

**This type is for ANYTHING with a primary document and sync needs that aren't skills or Java.**

#### Growing Your Sync Rules: Evolution Example

**Scenario:** Your custom project starts small, then grows.

**Initial Sync Rules (Phase 1 - Discovery):**

```markdown
**Sync Rules:**
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| `docs/catalog/*.md` | Section 2 "Projects" | Add/update catalog entries |
| `examples/*/README.md` | Section 3 "Examples" | Mark completed examples |
```

**Project grows. Phase 2 adds decision tracking:**

```markdown
**Sync Rules:**
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| `docs/catalog/*.md` | Section 2 "Projects" | Add/update catalog entries |
| `examples/*/README.md` | Section 3 "Examples" | Mark completed examples |
| `decisions/*.md` | Section 4 "Decisions" | Document architectural choices |
```

**Phase 3 adds integration demos:**

```markdown
**Sync Rules:**
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| `docs/catalog/*.md` | Section 2 "Projects" | Add/update catalog entries |
| `examples/*/README.md` | Section 3 "Examples" | Mark completed examples |
| `decisions/*.md` | Section 4 "Decisions" | Document architectural choices |
| `integrations/*/config.yaml` | Section 5 "Integrations" | Add integration patterns |
| `docs/roadmap.md` | Section 6 "Future Work" | Sync upcoming milestones |
```

**How to expand safely:**

1. **Add new rows, don't replace the table**
   - Existing rules continue working
   - New patterns are additive
   - No disruption to current sync behavior

2. **Test with one new row first**
   - Make a change matching the new pattern
   - Run custom-git-commit
   - Verify primary doc updates correctly
   - Then add more rules

3. **Update milestone when appropriate**
   - Phase 1 → Phase 2: Update milestone
   - Helps track progress in commit messages
   - Documents evolution of the project

4. **Keep Consistency Checks current**
   - Add checks for new sections: "All integrations reference valid catalog entries"
   - Remove checks for deprecated sections
   - Ensures primary doc stays coherent

**Common mistakes to avoid:**

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Replacing entire table | Loses existing sync patterns | Add new rows at bottom |
| Overlapping patterns | Two rules match same file → conflict | Make patterns mutually exclusive |
| Vague "Update Type" | `update-primary-doc` doesn't know what to do | Be specific: "Add entry", "Update status", "Document pattern" |
| Not testing incrementally | All 5 new rules at once → hard to debug | Add 1 rule, test, then add next |

**Result:** Your Sync Rules evolve with your project. Start simple, grow as needed, no skill changes required.

---

### Type 4: Generic (Fallback)

**Why this type exists:**
- Simple projects without special documentation requirements
- Default fallback when no type declared
- Minimal overhead, maximum simplicity

**Declaration (Optional):**
```markdown
## Project Type

**Type:** generic
```

Or simply omit the Project Type section entirely (defaults to generic).

**Behavior:**
```
git-commit (for type: generic)
  ├─ update-claude-md (if CLAUDE.md exists)
  └─ Conventional commit (basic)
```

**No sync logic, no validation, just commits.**

**Use for:**
- Simple scripts or utilities
- Personal projects
- Experiments
- Anything without special documentation needs

---

### Decision Matrix: When to Create a New Built-in Type

**Question: Should I create a new `<type>-git-commit` skill?**

**Ask these questions:**

1. **Do we understand this domain universally?**
   - ✅ Java: Yes (architecture patterns are well-known)
   - ✅ Skills: Yes (we built the skill system)
   - ❌ Working groups: No (every group is different)
   - ❌ Research: No (every thesis is different)

2. **Can we hardcode the sync logic?**
   - ✅ Java: Yes (DESIGN.md sections map to code concepts)
   - ✅ Skills: Yes (README sections map to skill structure)
   - ❌ Vision docs: No (sections vary by project)
   - ❌ Thesis: No (chapter organization varies)

3. **Is this a well-established, widely-used pattern?**
   - ✅ Java/Maven: Yes (industry standard)
   - ✅ Skills: Yes (our standard)
   - ❌ Working groups: No (varies widely)
   - ❌ Your specific use case: Probably not universal

**Decision Tree:**

```
Can we hardcode sync logic universally?
├─ YES → Create built-in type (<type>-git-commit)
│        Examples: java, skills
│
└─ NO → Use type: custom
         Examples: working groups, research, API docs, standards
```

**If you answered NO to any question: Use `type: custom`, not a new built-in type.**

---

### Lessons Learned: What NOT to Do

**❌ Don't create `working-group-git-commit`:**
- Not all working groups have vision documents
- Section names vary (some have "Projects", others "Members", others "Deliverables")
- Milestones vary (phases vs chapters vs versions vs sprints)
- **Solution:** One `custom-git-commit` with user config

**❌ Don't create `research-git-commit`:**
- Not all theses have the same structure
- Some have Methodology → Results, others have Theory → Application
- Citation styles vary (APA, MLA, Chicago, IEEE)
- **Solution:** One `custom-git-commit` with user config

**❌ Don't create `api-docs-git-commit`:**
- Some use OpenAPI, others use GraphQL schemas, others use custom formats
- Some sync with code, others don't
- Section organization varies
- **Solution:** One `custom-git-commit` with user config

**❌ Don't try to auto-detect project types:**
- Too many edge cases
- Fails when projects mix concerns
- User knows best what their project is
- **Solution:** Explicit declaration in CLAUDE.md

**The Pattern: Two built-in types (skills, java) + one configurable type (custom) + one fallback (generic) = handles everything.**

---

### How Routing Works

**git-commit reads CLAUDE.md first:**

```
Step 1: Read CLAUDE.md
  └─ Extract: Type: [skills | java | custom | generic]

Step 2: Route based on type
  ├─ skills → Continue with git-commit (skills mode)
  │           ├─ skill-review
  │           ├─ readme-sync.md
  │           └─ update-claude-md
  │
  ├─ java → STOP: "Use java-git-commit instead"
  │
  ├─ custom → STOP: "Use custom-git-commit instead"
  │
  └─ generic → Continue with git-commit (basic mode)
              └─ update-claude-md (if exists)

Step 3: If CLAUDE.md missing or no type
  └─ Interactive setup:
     "What kind of project is this? [1-4]"
     Create/update CLAUDE.md based on answer
```

**Each specialized skill verifies its type:**

```
java-git-commit:
  Step 0: Verify CLAUDE.md declares type: java
          If wrong/missing → Offer to fix or redirect

custom-git-commit:
  Step 0: Verify CLAUDE.md declares type: custom
          If missing config → Interactive setup
```

---

### Adding Support for a New Domain (Future Claudes)

**Scenario: You want to add support for Python projects.**

**Ask: Is this a built-in or custom type?**

**Decision criteria:**
1. Do we understand Python architecture universally?
2. Can we hardcode how to sync architecture docs?
3. Is there a standard Python architecture documentation pattern?

**If YES to all three:**

**Option A: Create `python-git-commit` (new built-in type)**

```markdown
## Project Type

**Type:** python
```

**You must create:**
- `python-git-commit` skill (like java-git-commit)
- `update-architecture-doc` skill for Python (like java-update-design)
- Define what "architecture doc" means for Python
- Hardcode sync logic (what code changes map to what doc sections)

**Add to CLAUDE.md:**
- New section under "Current Supported Project Types"
- Document sync logic
- Update routing in git-commit

**If NO to any question:**

**Option B: Use `type: custom` (recommended)**

User configures in their CLAUDE.md:

```markdown
## Project Type

**Type:** custom
**Primary Document:** docs/architecture.md

**Sync Strategy:** bidirectional-consistency

**Sync Rules:**
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| `src/**/*.py` | "Modules" | Document new modules |
| `requirements.txt` | "Dependencies" | Update dependency list |
```

**No new skills needed. Just use existing `custom-git-commit`.**

#### Real-World Example: Adding Python Support

**Scenario:** User wants commit workflow for Python project with architecture docs.

**Question:** Should we create `python-git-commit` (new built-in type)?

**Analysis:**
1. **Do we understand Python architecture universally?**
   - ❌ No — Python projects vary wildly (Django apps, FastAPI services, data pipelines, ML projects, CLI tools)
   - Some use Clean Architecture, others use package-based, others use monolithic
   - No single "Python architecture pattern" like Java's layered approach

2. **Can we hardcode sync logic?**
   - ❌ No — we don't know if architecture doc should track modules, packages, classes, or something else
   - Django projects might document apps vs services vs models
   - FastAPI might document routers vs dependencies vs schemas
   - Data science might document pipelines vs transformers vs models

3. **Is there a standard Python architecture documentation pattern?**
   - ❌ No — unlike Java (where DESIGN.md typically has Layers/Components/Domain Model), Python has no standard

**Decision: Use `type: custom`, NOT a new built-in type.**

**Why this is correct:**
- Python is too diverse to hardcode sync logic
- Every Python project structures docs differently
- User knows their architecture better than we do
- One `custom-git-commit` with user's Sync Rules handles ALL Python variants

**How user would configure:**

```markdown
## Project Type

**Type:** custom
**Primary Document:** docs/architecture.md

**Sync Strategy:** bidirectional-consistency

**Sync Rules:**
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| `src/api/*.py` | "API Routers" | Document new endpoints |
| `src/models/*.py` | "Domain Models" | Update model descriptions |
| `src/services/*.py` | "Business Logic" | Document service changes |
| `requirements.txt` | "Dependencies" | Update dependency list |

**Current Milestone:** Version 2.1.0
```

**Result:** Works perfectly without creating `python-git-commit`, `python-update-design`, etc.

**Key insight:** If you can't answer "what does architecture doc mean for ALL X projects", it's not a built-in type.

---

### Interactive Setup: Helping Users Declare Type

**When CLAUDE.md missing or no type declared:**

```
I notice this repository doesn't have a Project Type declared in CLAUDE.md.
Let me help you set this up - it only takes a moment.

**What kind of project is this?**

1. **Skills repository** - Claude Code skills (has */SKILL.md files)
2. **Java project** - Maven/Gradle (has pom.xml or build.gradle)
3. **Custom project** - Working groups, research, docs, etc.
4. **Generic project** - No special handling needed

Reply with the number (1-4) or type the name.
```

**Based on response, create CLAUDE.md:**

**For 1 (skills):**
```markdown
## Project Type

**Type:** skills
```

**For 2 (java):**
```markdown
## Project Type

**Type:** java
```
Plus check for DESIGN.md, offer to create if missing.

**For 3 (custom):**
Prompt for:
- Primary document path
- Current milestone
Create CLAUDE.md with template sync rules.

**For 4 (generic):**
```markdown
## Project Type

**Type:** generic
```

**Then stage CLAUDE.md and continue with commit.**

**This ensures every project gets properly configured, not just blocked.**

---

### Summary for Future Claudes

**The Four Types (Memorize This):**

| Type | Hardcoded Logic? | User Config? | Use When |
|------|------------------|--------------|----------|
| `skills` | ✅ Yes | ❌ No | This skills repo |
| `java` | ✅ Yes | ❌ No | Java/Maven/Gradle |
| `custom` | ❌ No | ✅ Yes | Everything else with special needs |
| `generic` | ❌ No | ❌ No | Simple projects |

**Key Insights:**
1. **Explicit > Auto-detection** - User declares type in CLAUDE.md
2. **Built-in types are rare** - Only create if logic is universal and hardcodable
3. **Custom type handles variations** - One skill, infinite configurations
4. **Interactive setup helps users** - Don't just block, guide them
5. **Routing happens in git-commit** - Read type, route to specialized skill

**When in doubt: Use `type: custom` with user configuration, not a new built-in type.**
