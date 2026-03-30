# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a skill collection for Claude Code, providing specialized guidance for Java/Quarkus development workflows. Skills are markdown files with YAML frontmatter that Claude Code loads to execute specific development tasks.

## Project Type

**Type:** skills

## Project Type Awareness

**CRITICAL: Skills must handle different project types with appropriate workflows.**

### The Four Project Types

All repositories using these skills declare their type in CLAUDE.md. This enables appropriate commit workflows, documentation sync, and validation.

**Type Declaration (Required in CLAUDE.md):**
```markdown
## Project Type

**Type:** [skills | java | custom | generic]
```

**The Four Types:**

| Type | Description | Sync Behavior | When to Use |
|------|-------------|---------------|-------------|
| **`skills`** | Skills repository | Built-in (we know how skills work) | This repository |
| **`java`** | Java/Maven/Gradle | Built-in (we know Java architecture patterns) | Java projects |
| **`custom`** | User-configured | User defines sync strategy | Everything else with special needs |
| **`generic`** | No special handling | Basic conventional commits | Simple projects, no sync needed |

---

### Why These Four Types Exist

#### The Architectural Insight: Built-in vs User-Configured

**We learned through iteration that there are only TWO patterns:**

1. **Built-in Types** (skills, java)
   - We understand the domain deeply
   - We know what DESIGN.md means for Java architecture
   - We know what SKILL.md validation requires
   - We can hardcode the sync logic because it's universal for that domain

2. **User-Configured Types** (custom)
   - Every project is different (working groups, research, API docs, standards)
   - We CAN'T know what "vision document" means across all projects
   - User declares their sync strategy in CLAUDE.md
   - One `custom` type handles infinite variations

3. **No-Op Type** (generic)
   - Fallback for simple projects
   - No special requirements

**Key Lesson: Don't create `working-group-git-commit`, `research-git-commit`, `api-docs-git-commit`.**

Instead: One `custom-git-commit` reads user's config. Infinite flexibility, zero skill explosion.

---

### Why Explicit Declaration Over Auto-Detection

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
- Easy to understand
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
  ├─ update-readme (syncs README.md if skill changes)
  ├─ update-claude-md (syncs CLAUDE.md if exists)
  └─ Conventional commit
```

**Sync Logic (Hardcoded):**
- `update-readme` knows: SKILL.md changes → update Skills section, chaining table
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
  ├─ update-design (syncs DESIGN.md with code changes)
  │   └─ Maps .java changes to architecture sections
  ├─ update-claude-md (syncs CLAUDE.md if exists)
  └─ Conventional commit with Java-specific scopes
```

**Sync Logic (Hardcoded):**
- `update-design` knows: New @Entity → Update "Domain Model" section
- `update-design` knows: New module in pom.xml → Update "Component Structure"
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
  ├─ sync-primary-doc (generic, table-driven)
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
  │           ├─ update-readme
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
- `update-architecture-doc` skill for Python (like update-design)
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

## Skill Architecture

### Frontmatter Requirements

Every `SKILL.md` requires YAML frontmatter with exactly two fields:

```yaml
---
name: skill-name-with-hyphens
description: >
  Use when [specific triggering conditions and symptoms]
---
```

**Critical: Claude Search Optimization (CSO)**

The `description` field determines when Claude loads the skill. Follow these rules:

- **Start with "Use when..."** to focus on triggering conditions
- **NEVER summarize the skill's workflow** in the description
- Describe the *problem* or *symptoms*, not the solution
- Keep under 500 characters if possible
- Third person only (no "I" or "you")

**Why this matters:** If the description summarizes the workflow, Claude may follow the description instead of reading the full skill content. Descriptions are for *when to use*, skill body is for *how to use*.

❌ Bad: `description: Use when executing plans - dispatches subagent per task with code review between tasks`

✅ Good: `description: Use when executing implementation plans with independent tasks in the current session`

### Naming Conventions

Skills follow a hierarchical naming pattern:

**Generic principles skills** (suffix: `-principles`):
- `code-review-principles` — language-agnostic review checklist
- `security-audit-principles` — universal OWASP Top 10
- `dependency-management-principles` — universal BOM patterns
- `observability-principles` — universal logging/tracing/metrics

**Language-specific skills** (prefix: language name):
- `java-dev` — Java development
- `java-code-review` — extends `code-review-principles` for Java/Quarkus
- `java-security-audit` — extends `security-audit-principles` for Java/Quarkus
- `java-git-commit` — extends `git-commit` for Java repositories

**Tool-specific skills** (prefix: tool name):
- `maven-dependency-update` — extends `dependency-management-principles` for Maven

**Framework-specific skills** (prefix: framework name):
- `quarkus-flow-dev` — Quarkus + quarkus-flow development
- `quarkus-flow-testing` — Quarkus + quarkus-flow testing
- `quarkus-observability` — extends `observability-principles` for Quarkus

**Why this matters:** The naming pattern makes it clear which skills are generic foundations vs. language/tool-specific implementations. When adding support for new languages, create skills like `go-code-review` (extends `code-review-principles`), `gradle-dependency-update` (extends `dependency-management-principles`), etc.

### Skill Chaining

Skills explicitly reference each other to create workflows. The README documents the complete chaining matrix, but when editing skills:

1. **Add cross-references in "Skill Chaining" sections** (capitalized, not "Skill chaining")
2. **Make references bidirectional** when appropriate (e.g., java-security-audit ↔ java-code-review)
3. **Use Prerequisites sections** for layered skills (e.g., quarkus-flow-testing builds on java-dev and quarkus-flow-dev)
4. **Generic principles skills are never invoked directly** — they're referenced via Prerequisites by language/framework-specific skills

Example chaining patterns:
```
# Java repositories with both DESIGN.md and CLAUDE.md:
java-dev → java-code-review → java-git-commit → update-design + update-claude-md (automatic)

# Any repository with CLAUDE.md:
git-commit → update-claude-md (automatic)
```

### Supporting Files

When skill content exceeds ~200 words or includes heavy reference material:

- Extract to separate `.md` files (e.g., `funcDSL-reference.md`)
- Reference from main `SKILL.md`
- Keep skill body focused on workflow and principles

Pattern:
```
skill-name/
  SKILL.md              # Main workflow (required)
  reference-name.md     # Heavy API/reference docs
```

### Flowcharts

Skills use Graphviz dot notation for decision flows. Add flowcharts when:

- Decision points are non-obvious
- Process has loops where you might stop too early
- "When to use A vs B" decisions exist

Never use flowcharts for:
- Reference material (use tables)
- Code examples (use markdown blocks)
- Linear instructions (use numbered lists)

Flowcharts must have semantic labels, not generic ones like `step1`, `helper2`.

### Success Criteria

Skills that produce artifacts (commits, ADRs, dependency updates) include explicit "Success Criteria" sections with checkboxes. This prevents premature completion claims.

Example pattern:
```markdown
## Success Criteria

Dependency update is complete when:

- ✅ User has confirmed changes with **YES**
- ✅ BOM alignment verified (no version drift)
- ✅ Compilation succeeds (`mvn compile` passes)
- ✅ pom.xml changes committed

**Not complete until** all criteria met and changes committed.
```

## Consistency Patterns

When editing skills, maintain these conventions:

### Section Naming

- "Skill Chaining" (capitalized C)
- "Prerequisites" (for layered skills)
- "Success Criteria" (for artifact-producing skills)
- "Common Pitfalls" (table format: Mistake | Why It's Wrong | Fix)

### Cross-Reference Format

```markdown
## Prerequisites

**This skill builds on `skill-name`**. Apply all rules from:
- **skill-name**: [specific rules that apply]
```

or

```markdown
## Skill Chaining

**Triggered by skill-name:**
When [condition], it should invoke this skill for [reason].

**Chains to skill-name:**
After [milestone], invoke skill-name for [purpose].
```

### Common Mistakes Tables

All major skills include "Common Pitfalls" tables documenting real mistakes:

```markdown
| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| [Anti-pattern] | [Consequence] | [Correct approach] |
```

## Editing Skills

When modifying existing skills:

1. **Check README first** — the Skill Chaining Reference table shows the complete dependency graph
2. **Update cross-references** — if you add chaining, update both skills (source and target)
3. **Preserve CSO descriptions** — don't add workflow summaries to frontmatter
4. **Test flowcharts** — invalid dot syntax breaks skill loading
5. **Maintain Prerequisites** — layered skills (quarkus-flow-*) must reference their foundations

## Key Skills

**Generic foundation skills** (not invoked directly, referenced via Prerequisites):
- `code-review-principles` — universal code review checklist (extended by `java-code-review`)
- `security-audit-principles` — universal OWASP Top 10 (extended by `java-security-audit`)
- `dependency-management-principles` — universal BOM patterns (extended by `maven-dependency-update`)
- `observability-principles` — universal logging/tracing/metrics (extended by `quarkus-observability`)

**Language/framework foundation skills** (others build on these):
- `java-dev` — all Java development extends this
- `git-commit` — generic conventional commits (extended by `java-git-commit`)

**Workflow integrators** (chain multiple skills):
- `git-commit` — automatically invokes `skill-review` (if SKILL.md staged), `update-claude-md` (if CLAUDE.md exists), and `update-readme` (if README.md exists and skill changes). Routes to java-git-commit or custom-git-commit based on project type
- `java-git-commit` — automatically invokes `update-design` and `update-claude-md` (if docs exist). For type: java projects only
- `custom-git-commit` — automatically invokes `sync-primary-doc` (if Sync Rules configured) and `update-claude-md` (if exists). For type: custom projects (working groups, research, docs)
- `java-code-review` — triggers `java-security-audit` for security-critical code
- `skill-review` — blocks `git-commit` if CRITICAL findings exist

**Specialized skills** (domain-specific):
- `quarkus-flow-dev` — builds on `java-dev`, extended by `quarkus-flow-testing`
- `java-security-audit` — OWASP Top 10 for Java/Quarkus, triggered by `java-code-review`
- `maven-dependency-update` — Maven BOM management, builds on `dependency-management-principles`
- `quarkus-observability` — Quarkus observability config, builds on `observability-principles`
- `skill-review` — SKILL.md validation (frontmatter, CSO, cross-references, flowcharts), invoked by `git-commit`
- `sync-primary-doc` — Generic table-driven primary document sync (VISION.md, THESIS.md, etc.), invoked by `custom-git-commit`. Reads Sync Rules from CLAUDE.md
- `update-design` — DESIGN.md synchronization (architecture documentation), invoked by `java-git-commit`. For type: java projects only
- `update-claude-md` — CLAUDE.md synchronization (workflow documentation), invoked by `git-commit`, `java-git-commit`, and `custom-git-commit`
- `update-readme` — README.md synchronization (skills repository documentation), invoked by `git-commit`. For type: skills projects only

## README Synchronization

When adding/modifying skills, update README sections:

- **Skills** section: Add/update skill description with trigger conditions
- **How Skills Work Together**: Update chaining workflows if changed
- **Skill Chaining Reference** table: Add new chaining relationships
- **Key Features**: Note new flowcharts, Prerequisites sections, etc.

The README is the single source of truth for the skill collection's architecture.
