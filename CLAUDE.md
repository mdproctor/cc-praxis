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
java-dev → java-code-review → java-git-commit → java-update-design + update-claude-md (automatic)

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

### Skills-Repository-Specific Documentation

**This repository has modularized documentation for skills-specific workflows to avoid token waste in other projects.**

Skills-repository-specific logic (SKILL.md validation, README synchronization) is NOT implemented as portable skills. Instead, it lives in standalone documentation files at the repository root:

| File | Purpose | Used By |
|------|---------|---------|
| **skill-validation.md** | SKILL.md validation workflow (frontmatter, CSO, flowcharts, cross-references) | `git-commit` when type: skills AND SKILL.md files staged |
| **readme-sync.md** | README.md synchronization workflow (skill collection changes) | `git-commit` when type: skills AND skill changes detected |

**Why modularized (not skills):**
- These workflows only apply to THIS repository
- Loading them as skills wastes tokens in all other projects (java, custom, generic)
- They contain heavy reference material (checklists, tables, patterns)
- CLAUDE.md loads automatically in every conversation
- git-commit can reference these files when operating in type: skills mode

**When git-commit operates in type: skills mode:**
1. Check for staged SKILL.md files → Follow skill-validation.md workflow
2. Check for skill collection changes → Follow readme-sync.md workflow
3. Both workflows maintain the same confirmation pattern (propose → user YES → apply)

**These files are NOT:**
- Loaded in java/custom/generic projects (zero token cost)
- Duplicated in skills collection (single source of truth)
- Skills themselves (not in skills/ directory, not user-invocable via Skill tool)

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

### Third-Party Skill Exclusion

**CRITICAL: Only document skills authored by the repository owner.**

**Rules:**
- ✅ **Document only user-authored skills** in README.md and CLAUDE.md
- ❌ **Never document third-party skills** (skills from superpowers:*, external repos, etc.)
- ✅ **Add third-party skills to .gitignore** immediately upon discovery
- ❌ **Never reference third-party skills** in documentation (chaining tables, workflows, repository structure)

**Rationale:**
- Third-party skills are maintained elsewhere and can change without notice
- Documenting them creates maintenance burden and stale references
- Users already see third-party skills in their skill list
- README/CLAUDE.md should reflect only what this repository provides

**Implementation:**
1. Add skill directory to .gitignore with comment: `# Third-party skill from [source]`
2. Remove all references from README.md (Skills section, Chaining table, Repository Structure)
3. Remove all references from CLAUDE.md (Key Skills section)
4. Verify removal with: `grep -r "skill-name" README.md CLAUDE.md`

**Examples of third-party skills to exclude:**
- `superpowers:*` (all superpowers skills)
- `skill-creator` (external skill authoring tool)
- `frontend-design:*` (third-party frontend skills)
- Any skill not in version control for this repository

**Quality check:** During deep analysis, verify no third-party skills are documented anywhere.

## Editing Skills

When modifying existing skills:

1. **Check README first** — the Skill Chaining Reference table shows the complete dependency graph
2. **Update cross-references** — if you add chaining, update both skills (source and target)
3. **Preserve CSO descriptions** — don't add workflow summaries to frontmatter
4. **Test flowcharts** — invalid dot syntax breaks skill loading
5. **Maintain Prerequisites** — layered skills (quarkus-flow-*) must reference their foundations

## Pre-Commit Checklist for Skills

**MANDATORY checks when committing changes to this repository:**

- [ ] **SKILL.md files modified?** → Follow readme-sync.md workflow (do NOT skip, let it decide if README needs updates)
- [ ] **CLAUDE.md modified?** → Follow relevant update workflow if applicable
- [ ] **New validation/testing added?** → Update README.md § Skill Quality & Validation
- [ ] **New scripts/ files added?** → Update README.md § Repository Structure
- [ ] **New chaining relationships?** → Update README.md § Skill Chaining Reference
- [ ] **New features added to skills?** → Update README.md § Key Features
- [ ] **Framework changes** (same pattern across multiple skills)? → Document in README.md

**Do NOT rationalize skipping these checks:**
- ❌ "Just internal changes" → Wrong, internal changes can warrant documentation
- ❌ "Not significant enough" → Wrong, let the workflow decide significance
- ❌ "I know what needs updating" → Wrong, you'll miss things (like the validation framework gap)
- ✅ **Always run the workflows** — they exist to catch what you miss

**Recent regression:** Validation framework added to 4 sync workflows but README.md not updated. Root cause: Skipped readme-sync.md workflow, rationalized "just internal changes". Fix: Never skip workflows when SKILL.md files change.

## Meta-Rule: Consider Universality First

**CRITICAL: Before applying any fix, ask "Should this be universal?"**

**The principle:**
When you identify a problem and prepare a solution, STOP and consider:
1. **Is this problem specific to one context** (skills repo only, Java only, this file only)?
2. **Or is this a universal problem** (could happen in any project type, any AI assistant, any workflow)?

**If uncertain whether to make it universal → ASK THE USER.**

**Examples:**

| Situation | Narrow Fix | Universal Fix | Correct Choice |
|-----------|------------|---------------|----------------|
| README.md sync missing | Add check to readme-sync.md only | Add framework change detection to ALL sync workflows | Universal (ADR-0001) |
| Java-specific BOM issue | Fix in maven-dependency-update | Make dependency management universal | Narrow (Java-specific) |
| Rationalization bypass | Strengthen git-commit Step 2b | Add mandatory checks to all workflows | Universal |
| Quarkus event loop bug | Fix in quarkus-flow-dev | Make concurrency universal | Already universal (code-review-principles) |

**Why this matters:**
- **Prevents repeated regressions** - fix once, applies everywhere
- **Scales to future project types** - type: python, type: rust get the fix automatically
- **Reduces user burden** - don't re-discover same problem per project
- **Forces better design** - universal solutions are often cleaner

**When to stay narrow:**
- Domain-specific knowledge (Java annotations, Quarkus configuration)
- Language syntax (Java vs Python vs Go)
- Tool-specific features (Maven BOM vs npm package.json)
- Framework patterns (Quarkus vs Spring)

**When to go universal:**
- Process failures (rationalization, skipping workflows)
- Quality gates (validation, testing, documentation)
- Human behavior patterns (cognitive biases, shortcuts)
- Infrastructure (scripts, automation, validation)

**The test:** If the problem could plausibly occur in a different project type with different technologies, it's probably universal.

**See:** ADR-0001: Documentation Completeness Must Be Universal, Not Project-Specific

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
- `git-commit` — automatically invokes `skill-review` (if SKILL.md staged), `update-claude-md` (if CLAUDE.md exists), and `readme-sync.md` (if README.md exists and skill changes). Routes to java-git-commit or custom-git-commit based on project type
- `java-git-commit` — automatically invokes `java-update-design` and `update-claude-md` (if docs exist). For type: java projects only
- `custom-git-commit` — automatically invokes `update-primary-doc` (if Sync Rules configured) and `update-claude-md` (if exists). For type: custom projects (working groups, research, docs)
- `java-code-review` — triggers `java-security-audit` for security-critical code
- `skill-review` — blocks `git-commit` if CRITICAL findings exist

**Specialized skills** (domain-specific):
- `quarkus-flow-dev` — builds on `java-dev`, extended by `quarkus-flow-testing`
- `java-security-audit` — OWASP Top 10 for Java/Quarkus, triggered by `java-code-review`
- `maven-dependency-update` — Maven BOM management, builds on `dependency-management-principles`
- `quarkus-observability` — Quarkus observability config, builds on `observability-principles`
- `skill-review` — SKILL.md validation (frontmatter, CSO, cross-references, flowcharts), invoked by `git-commit`
- `update-primary-doc` — Generic table-driven primary document sync (VISION.md, THESIS.md, etc.), invoked by `custom-git-commit`. Reads Sync Rules from CLAUDE.md
- `java-update-design` — DESIGN.md synchronization (architecture documentation), invoked by `java-git-commit`. For type: java projects only
- `update-claude-md` — CLAUDE.md synchronization (workflow documentation), invoked by `git-commit`, `java-git-commit`, and `custom-git-commit`
- `readme-sync.md` — README.md synchronization (skills repository documentation), invoked by `git-commit`. For type: skills projects only

## README Synchronization

When adding/modifying skills, update README sections:

- **Skills** section: Add/update skill description with trigger conditions
- **How Skills Work Together**: Update chaining workflows if changed
- **Skill Chaining Reference** table: Add new chaining relationships
- **Key Features**: Note new flowcharts, Prerequisites sections, etc.

The README is the single source of truth for the skill collection's architecture.

## Quality Assurance Framework

**CRITICAL: This section prevents regressions by documenting all types of validation that skills must pass.**

Skills are infrastructure code that guides AI behavior across millions of invocations. Quality issues compound exponentially. This framework ensures skills maintain structural integrity, logical soundness, and documentation accuracy over time.

### The Testing Philosophy

**Skills need both automated and manual validation:**

| Validation Type | What It Catches | Tools |
|----------------|-----------------|-------|
| **Automated** | Structural errors, syntax, format violations, broken references | Scripts, linters, parsers |
| **Manual** | Logic errors, unclear writing, missing edge cases, contradictions | Deep analysis reviews |
| **Functional** | Workflow execution, command correctness, actual usability | Test cases with real Claude instances |

**All three are required.** Automated tests catch mechanical errors fast. Manual reviews catch semantic errors. Functional tests catch real-world failures.

---

### Automated Validation (Level 1)

**These checks can and should be scripted.**

#### 1.1 Frontmatter Validation

**Script location:** `scripts/validate_frontmatter.py` (to be created)

**Checks:**
- ✅ YAML frontmatter exists and is valid YAML
- ✅ Required fields present: `name`, `description`
- ✅ `name` matches directory name (skill-name/SKILL.md → name: skill-name)
- ✅ `name` uses hyphens, not underscores or spaces
- ✅ `description` starts with "Use when"
- ✅ `description` is under 500 characters
- ✅ `description` contains no first/second person ("I", "you")
- ✅ No extra fields (only `name`, `description`, optional `compatibility`)

**Exit code:** Non-zero if any check fails

**Example validation:**
```python
def validate_frontmatter(skill_path):
    # Read SKILL.md
    # Parse YAML frontmatter
    # Check all rules above
    # Return violations list
```

#### 1.2 CSO (Claude Search Optimization) Compliance

**Script location:** `scripts/validate_cso.py` (to be created)

**Checks:**
- ✅ Description does NOT contain workflow keywords: "step", "then", "invoke", "run", "execute", "dispatch"
- ✅ Description focuses on WHEN (symptoms, triggers, conditions)
- ✅ Description does NOT describe HOW (workflow, process, steps)
- ✅ Description does NOT list tool names (Bash, Read, Edit, Agent)
- ✅ Description length appropriate (100-500 chars preferred)

**Why this matters:** Workflow summaries in descriptions cause "expensive wallpaper" - Claude follows the summary instead of reading the skill body, making the skill useless.

**Red flags:**
- "dispatches subagent per task"
- "runs tests then commits"
- "step 1... step 2..."
- "uses Read tool to..."

#### 1.3 Graphviz Flowchart Validation

**Script location:** `scripts/validate_flowcharts.py` (to be created)

**Checks:**
- ✅ All flowcharts use valid Graphviz dot syntax
- ✅ No generic labels (step1, step2, helper1, pattern2)
- ✅ All node labels are semantic and descriptive
- ✅ Flowcharts appear only for decisions/loops (not for reference material)

**Implementation:**
```bash
# Extract flowcharts from SKILL.md
sed -n '/```dot/,/```/p' SKILL.md | sed '1d;$d' > /tmp/flowchart.dot

# Validate with graphviz
dot -Tsvg /tmp/flowchart.dot > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "CRITICAL: Invalid flowchart syntax"
  exit 1
fi

# Check for generic labels
if grep -E '"(step|helper|pattern|node)[0-9]+"' /tmp/flowchart.dot; then
  echo "WARNING: Generic flowchart labels detected"
  exit 1
fi
```

#### 1.4 Cross-Reference Integrity

**Script location:** `scripts/validate_references.py` (to be created)

**Checks:**
- ✅ All skill names referenced in backticks exist as directories
- ✅ All `Chains to X` references have corresponding SKILL.md files
- ✅ All `Prerequisites` references exist
- ✅ All `Invoked by` references exist
- ✅ No references to deleted/renamed skills

**Data structure:**
```python
# Build reference graph
skill_references = {
    'java-git-commit': {
        'chains_to': ['java-update-design', 'update-claude-md'],
        'invoked_by': ['git-commit'],
        'prerequisites': ['git-commit'],
        'mentioned_in': ['java-update-design', 'README.md']
    }
}

# Validate all references resolve
for skill, refs in skill_references.items():
    for ref in refs['chains_to']:
        assert skill_exists(ref), f"{skill} references non-existent {ref}"
```

#### 1.5 Naming Convention Compliance

**Script location:** `scripts/validate_naming.py` (to be created)

**Checks:**
- ✅ Generic principles: `*-principles` suffix
- ✅ Language-specific: language prefix (`java-*`, `python-*`)
- ✅ Tool-specific: tool prefix (`maven-*`, `gradle-*`)
- ✅ Framework-specific: framework prefix (`quarkus-*`, `spring-*`)
- ✅ No mixed patterns (e.g., `java-maven-principles` is ambiguous)

**Pattern matching:**
```python
PATTERNS = {
    'principles': r'^[a-z]+-principles$',
    'language': r'^(java|python|go|rust)-[a-z-]+$',
    'tool': r'^(maven|gradle|npm|pip)-[a-z-]+$',
    'framework': r'^(quarkus|spring|react|vue)-[a-z-]+$',
}

def categorize_skill(name):
    for category, pattern in PATTERNS.items():
        if re.match(pattern, name):
            return category
    return 'uncategorized'
```

#### 1.6 File Organization Validation

**Script location:** `scripts/validate_structure.py` (to be created)

**Checks:**
- ✅ Every skill directory has SKILL.md
- ✅ Supporting files in expected locations (scripts/, references/, assets/)
- ✅ No orphaned files (files not referenced in SKILL.md)
- ✅ Referenced files exist (skill mentions `references/api.md` → file exists)
- ✅ No duplicate content (same reference file in multiple skills)

#### 1.7 Required Sections

**Script location:** `scripts/validate_sections.py` (to be created)

**Checks based on skill type:**

| Skill Type | Required Sections |
|------------|------------------|
| **All skills** | "Skill Chaining" OR "Prerequisites" |
| **Artifact-producing** | "Success Criteria" with checkboxes |
| **Major skills** | "Common Pitfalls" table (3 columns) |
| **Layered skills** | "Prerequisites" referencing foundation |
| **Complex workflows** | Decision flowchart OR clear numbered steps |

**Detection logic:**
```python
def is_artifact_producing(skill_name):
    """Skills that create commits, files, ADRs, updates."""
    return any(keyword in skill_name for keyword in
               ['commit', 'update', 'create', 'sync'])

def requires_success_criteria(skill_path):
    skill_name = os.path.basename(skill_path)
    content = read_skill(skill_path)
    return is_artifact_producing(skill_name) and \
           '## Success Criteria' not in content
```

---

### Deep Analysis Validation (Level 2)

**These checks require human judgment but follow systematic procedures.**

When the user requests "deep analysis" or before major releases, perform ALL of these checks:

#### 2.1 Reference Accuracy

**Manual procedure:**

1. **Read every skill mentioned in cross-references**
2. **Verify bidirectional links:**
   - If A says "chains to B" → check B says "invoked by A"
   - If A says "builds on B" → check B mentions A in "Used by" or "Extended by"
3. **Check reference timestamps:**
   - Skills reference current tool names (not deprecated tools)
   - Examples use current syntax (not outdated API)
   - Links point to current locations (not moved/deleted files)
4. **Verify claim accuracy:**
   - If skill says "automatically invoked by X" → read X and confirm
   - If skill says "only for type: java" → check no other types use it
   - If skill says "blocks commit on CRITICAL" → verify this behavior exists

**Common stale references found:**
- ❌ "invoked by old-skill-name" (skill was renamed)
- ❌ "uses TodoWrite tool" (deprecated tool name)
- ❌ "see docs/ARCHITECTURE.md" (file moved to DESIGN.md)
- ❌ "runs with --flag" (flag removed in newer version)

#### 2.2 Logical Soundness

**Manual procedure:**

1. **Walk through the workflow as if executing it:**
   - Can each step actually be performed?
   - Do commands have correct syntax?
   - Are file paths correct?
   - Do variables exist when referenced?

2. **Check decision logic:**
   - If-then branches cover all cases?
   - No contradictory conditions?
   - Loops have clear exit conditions?
   - Edge cases handled?

3. **Verify prerequisites:**
   - If skill requires X to exist, does it check for X?
   - If skill assumes Y is true, does it validate Y?
   - Dependencies in correct order?

**Example logical errors found:**
- ❌ "Read DESIGN.md" but never checked it exists → fails on first use
- ❌ "If Java project... else if Skills project" → missing else for other types
- ❌ "grep for X, then read $MATCH" → $MATCH variable never set
- ❌ "Run tests, then commit" → no handling for test failures

#### 2.3 Contradiction Detection

**Manual procedure:**

1. **Within-skill contradictions:**
   - Section A says "always do X"
   - Section B says "never do X"
   - Root cause: copy-paste or incremental edits

2. **Cross-skill contradictions:**
   - Skill A: "java-git-commit always syncs DESIGN.md"
   - Skill B: "DESIGN.md sync is optional"
   - Resolution: Determine which is authoritative

3. **Documentation vs. behavior contradictions:**
   - CLAUDE.md: "skill-review blocks on CRITICAL"
   - skill-review: "WARNING level blocks commits"
   - Fix: Make behavior match documentation (or update docs)

**Systematic check:**
- List all imperative statements (MUST, ALWAYS, NEVER)
- Search for opposing statements about same topic
- Resolve by determining correct behavior
- Update all references to be consistent

#### 2.4 Completeness Analysis

**Manual procedure:**

1. **Edge case coverage:**
   - What if file doesn't exist?
   - What if command fails?
   - What if user says "no"?
   - What if input is empty/malformed?

2. **Error handling:**
   - Every command that can fail has failure handling?
   - User is informed of problems with actionable advice?
   - Graceful degradation where possible?

3. **Documentation gaps:**
   - Every mentioned concept is defined?
   - Acronyms spelled out on first use?
   - Examples provided for complex instructions?
   - "Why" explained, not just "what"?

**Gap detection pattern:**
```
Read skill start to finish.
For each instruction:
  - Could a new Claude follow this without prior context?
  - Are there assumptions not stated?
  - Are there terms not defined?
  - Are there examples missing?
```

#### 2.5 Readability & Clarity

**Manual procedure:**

1. **Language clarity:**
   - No ambiguous pronouns (it, this, that without clear antecedent)
   - No double negatives
   - Active voice preferred over passive
   - Consistent terminology (not "sync" in one place, "update" in another)

2. **Structure coherence:**
   - Sections in logical order
   - Related content grouped together
   - Clear transitions between sections
   - Headings accurately describe content

3. **Cognitive load:**
   - Not too many concepts introduced at once
   - Complex ideas broken into steps
   - Tables used for dense reference material
   - Flowcharts for complex decisions

**Red flags:**
- Sentences over 40 words (usually can be split)
- Paragraphs over 8 lines (usually can be broken up)
- More than 3 levels of nesting (restructure)
- Jargon without definition (explain or link)

#### 2.6 Duplication & Overlap

**Manual procedure:**

1. **Unnecessary duplication:**
   - Same instructions in multiple skills → extract to shared foundation
   - Same example repeated → reference once, link from others
   - Same validation logic → create common validation skill

2. **Troublesome overlap:**
   - Two skills that trigger on similar conditions → clarify boundaries
   - Two skills that do similar things → merge or differentiate
   - Two sources of truth for same information → choose canonical location

3. **Gaps between skills:**
   - Workflow ends at skill A, should start at skill B, but no chaining
   - Concept mentioned in skill A, detailed in skill B, but no reference
   - Related skills don't mention each other

**Resolution pattern:**
- Duplication → DRY (extract common, reference from specific)
- Overlap → Differentiate (clear triggering conditions, different purposes)
- Gaps → Connect (add cross-references, chaining)

#### 2.7 Skill Chaining Correctness

**Manual procedure:**

1. **Build the complete chain graph:**
   ```
   git-commit (skills mode)
     ├─ skill-review (if SKILL.md staged)
     ├─ readme-sync.md (if skill changes)
     └─ update-claude-md (if CLAUDE.md exists)

   git-commit (java mode)
     └─ "Use java-git-commit instead"

   java-git-commit
     ├─ java-code-review (if not done)
     │   └─ java-security-audit (if security-critical)
     ├─ java-update-design (if DESIGN.md exists)
     └─ update-claude-md (if CLAUDE.md exists)
   ```

2. **Verify each link:**
   - Parent skill actually invokes child
   - Child skill acknowledges parent
   - Conditions for invocation are clear
   - No circular dependencies

3. **Check chain completeness:**
   - User request → terminal skill (produces artifact)
   - No dead-end skills (invoked but invoke nothing)
   - No orphan skills (never invoked, not user-invocable)

#### 2.8 Third-Party Skill Documentation

**Manual procedure:**

**CRITICAL: Verify no third-party skills are documented in README.md or CLAUDE.md.**

1. **Identify third-party skills:**
   ```bash
   # Check .gitignore for excluded skill directories
   grep '/$' .gitignore | grep -v '^#' | grep -v '^\.'

   # Check for superpowers:* references
   grep -E 'superpowers:|skill-creator|frontend-design:' README.md CLAUDE.md
   ```

2. **Verify exclusions:**
   - ✅ All third-party skill directories in .gitignore
   - ✅ No third-party skills in README.md "Skills" section
   - ✅ No third-party skills in README.md "Skill Chaining Reference" table
   - ✅ No third-party skills in README.md "Repository Structure" section
   - ✅ No third-party skills in CLAUDE.md "Key Skills" section
   - ✅ No third-party skills in workflow diagrams

3. **Check for stale references:**
   - Search for skill names that appear in .gitignore
   - Verify removal from all documentation
   - Check for indirect references (e.g., "use skill-creator to...")

**Common violations found:**
- ❌ skill-creator documented in Development Tools section
- ❌ superpowers:* skills listed in chaining table
- ❌ Third-party skills in repository structure diagram
- ❌ Workflow examples showing third-party skill invocation

**Fix procedure:**
1. Remove all documentation references
2. Verify .gitignore entry exists
3. Run consistency check: `grep -r "<skill-name>" README.md CLAUDE.md` should return no results

---

### Functional Testing (Level 3)

**These checks execute skills against real scenarios.**

#### 3.1 Test Case Structure

**Location:** Each skill directory can have `tests/` subdirectory

**Structure:**
```
skill-name/
  SKILL.md
  tests/
    test_cases.json       # Test definitions
    fixtures/             # Input files for tests
    expected/             # Expected outputs
    results/              # Actual outputs (gitignored)
```

**Test case format:**
```json
{
  "skill_name": "java-git-commit",
  "tests": [
    {
      "id": "basic-commit",
      "description": "Commit single Java file change",
      "setup": "scripts/setup_basic_commit.sh",
      "prompt": "commit these changes",
      "expected_behavior": {
        "invokes_skills": ["java-update-design", "update-claude-md"],
        "creates_commit": true,
        "commit_message_matches": "^(feat|fix|refactor)\\(.*\\):.*",
        "files_modified": ["docs/DESIGN.md", "CLAUDE.md"]
      },
      "assertions": [
        {"type": "file_exists", "path": "docs/DESIGN.md"},
        {"type": "git_commit_exists", "message_contains": "Co-Authored-By: Claude"},
        {"type": "skill_invoked", "skill": "java-update-design"}
      ]
    }
  ]
}
```

#### 3.2 Test Execution Framework

**Script location:** `scripts/testing/run_skill_tests.py`

**Process:**
1. Create isolated git worktree for each test
2. Run setup script to prepare state
3. Invoke Claude with skill loaded and test prompt
4. Capture outputs (files created, commits made, skills invoked)
5. Compare against expected behavior
6. Report pass/fail with details

**Execution:**
```bash
# Run all tests for a skill
python scripts/testing/run_skill_tests.py java-git-commit

# Run specific test
python scripts/testing/run_skill_tests.py java-git-commit --test basic-commit

# Run all skill tests in repository
python scripts/testing/run_skill_tests.py --all
```

#### 3.3 Regression Test Suite

**Location:** `tests/regression/`

**Purpose:** Prevent known issues from reoccurring

**Structure:**
```
tests/regression/
  issue-001-cso-violation.json          # CSO description had workflow
  issue-002-circular-dependency.json    # Skill A → B → A loop
  issue-003-missing-bidirectional.json  # A references B, B doesn't reference A
  issue-004-stale-tool-name.json        # Referenced deprecated TodoWrite
```

**Each regression test:**
- Documents the original issue
- Provides failing example
- Validates the fix
- Runs on every commit

**Example regression test:**
```json
{
  "issue_id": "001",
  "title": "CSO Violation - Workflow in Description",
  "description": "Skill had workflow summary in description, causing expensive wallpaper",
  "original_violation": {
    "skill": "superpowers:execute-plan",
    "description": "Use when executing plans - dispatches subagent per task with code review between tasks"
  },
  "why_it_failed": "Claude followed description instead of reading full skill",
  "fix_applied": "Removed workflow details from description",
  "validation": {
    "type": "cso_check",
    "description_must_not_contain": ["dispatches", "per task", "code review"]
  }
}
```

**Regression test execution:**
```bash
# Run all regression tests
python scripts/testing/run_regression_tests.py

# Verify specific issue is fixed
python scripts/testing/run_regression_tests.py --issue 001
```

---

### Standards & Best Practices

**Follow these established standards for skill validation:**

#### Documentation Standards

| Standard | Reference | Application |
|----------|-----------|-------------|
| **Markdown CommonMark** | https://commonmark.org/ | All SKILL.md files |
| **YAML 1.2** | https://yaml.org/spec/1.2/ | Frontmatter only |
| **Graphviz DOT** | https://graphviz.org/doc/info/lang.html | Flowcharts |
| **Conventional Commits** | https://www.conventionalcommits.org/ | Commit message format (not skill content) |

#### Code Quality Standards (for scripts/)

| Standard | Tool | Application |
|----------|------|-------------|
| **Python PEP 8** | `flake8`, `black` | All .py scripts |
| **Shell POSIX** | `shellcheck` | All .sh scripts |
| **Type hints** | `mypy` | Python validation scripts |

#### Test Coverage Standards

**Minimum test coverage for production skills:**
- ✅ 100% of user-invocable skills have at least 1 functional test
- ✅ 100% of auto-invoked skills have regression tests
- ✅ All flowchart decision branches covered by tests
- ✅ All error conditions have failure tests

**Coverage tracking:**
```bash
# Generate coverage report
python scripts/testing/test_coverage.py --report

# Output:
# java-git-commit: 5/5 branches tested (100%)
# git-commit: 3/4 branches tested (75%) - missing: type: custom test
# skill-review: 8/8 validations tested (100%)
```

---

### Integration with Skill Workflows

**How validation integrates into development workflows:**

#### Pre-Commit Validation

**Triggered by:** `git-commit` when SKILL.md files are staged

**Workflow:**
```
git-commit (for type: skills)
  ├─ Run automated validation (Level 1)
  │   ├─ validate_frontmatter.py
  │   ├─ validate_cso.py
  │   ├─ validate_flowcharts.py
  │   ├─ validate_references.py
  │   ├─ validate_naming.py
  │   └─ validate_sections.py
  │
  ├─ skill-review (Level 2 checks)
  │   ├─ Reference accuracy
  │   ├─ Logical soundness
  │   ├─ Completeness
  │   └─ Block on CRITICAL findings
  │
  ├─ readme-sync.md (if skills changed)
  └─ update-claude-md (if exists)
```

**Exit behavior:**
- ❌ **CRITICAL findings → Block commit** (frontmatter invalid, flowchart broken, references missing)
- ⚠️ **WARNING findings → Show but allow** (naming convention violation, missing Common Pitfalls)
- ℹ️ **NOTE findings → Log only** (could add examples, could improve clarity)

#### Deep Analysis Review

**Triggered by:** User request ("do a deep analysis") or before release

**Workflow:**
```
deep-analysis
  ├─ Run ALL Level 1 automated checks
  ├─ Run ALL Level 2 manual procedures
  ├─ Run Level 3 functional tests
  ├─ Generate comprehensive report
  └─ Create action items for findings
```

**Report format:**
```markdown
# Deep Analysis Report - 2026-03-30

## Summary
- Skills analyzed: 45
- Automated checks: 312 passed, 3 failed
- Manual reviews: 45 completed
- Functional tests: 89 passed, 2 failed
- Total issues: 14 (4 critical, 6 warning, 4 note)

## Critical Issues (Must Fix)
1. java-security-audit: Flowchart has invalid dot syntax
2. quarkus-flow-dev: References non-existent `quarkus-reactive-dev`
3. maven-dependency-update: CSO violation in description
4. java-update-design: Missing Success Criteria section

## Warning Issues (Should Fix)
...

## Functional Test Failures
1. java-git-commit/basic-commit: DESIGN.md not updated
2. skill-review/cso-check: False negative on workflow keywords

## Recommendations
...
```

#### Continuous Integration

**Triggered by:** Push to repository, Pull Request

**GitHub Actions workflow:**
```yaml
name: Skill Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Automated Validation
        run: |
          python scripts/validate_all.py --strict

      - name: Run Regression Tests
        run: |
          python scripts/testing/run_regression_tests.py

      - name: Check Documentation Sync
        run: |
          python scripts/check_readme_sync.py
          python scripts/check_claude_md_sync.py

      - name: Report Results
        run: |
          python scripts/generate_report.py --output report.md
          cat report.md >> $GITHUB_STEP_SUMMARY
```

---

### Validation Script Roadmap

**Scripts to create (in priority order):**

#### Phase 1: Critical Automated Checks
1. ✅ **`validate_frontmatter.py`** - YAML structure, required fields
2. ✅ **`validate_cso.py`** - Description compliance
3. ✅ **`validate_flowcharts.py`** - Graphviz syntax, semantic labels
4. ✅ **`validate_references.py`** - Cross-reference integrity

#### Phase 2: Structural Validation
5. ✅ **`validate_naming.py`** - Naming conventions
6. ✅ **`validate_sections.py`** - Required sections
7. ✅ **`validate_structure.py`** - File organization

#### Phase 3: Test Execution
8. ✅ **`run_skill_tests.py`** - Functional test runner
9. ✅ **`run_regression_tests.py`** - Regression test runner
10. ✅ **`test_coverage.py`** - Coverage reporting

#### Phase 4: Deep Analysis Tools
11. ✅ **`analyze_references.py`** - Reference staleness detection
12. ✅ **`detect_contradictions.py`** - Cross-skill consistency
13. ✅ **`check_completeness.py`** - Gap analysis

#### Phase 5: Integration & Reporting
14. ✅ **`validate_all.py`** - Master validation orchestrator
15. ✅ **`generate_report.py`** - Comprehensive reporting
16. ✅ **`check_readme_sync.py`** - README accuracy validation
17. ✅ **`check_claude_md_sync.py`** - CLAUDE.md accuracy validation

**Each script should:**
- Exit with code 0 (pass) or non-zero (fail)
- Output JSON results for parsing
- Support `--verbose` flag for detailed output
- Support `--fix` flag for auto-fixable issues (where safe)
- Include unit tests for the validator itself

---

### Deep Analysis Checklist

**When user requests deep analysis, systematically perform ALL checks:**

#### Automated Checks (Run Scripts)
- [ ] Frontmatter validation (all skills)
- [ ] CSO compliance (all skills)
- [ ] Flowchart validation (skills with flowcharts)
- [ ] Cross-reference integrity (all references)
- [ ] Naming convention compliance (all skills)
- [ ] Required sections (by skill type)
- [ ] File organization (all skills)

#### Manual Analysis (Systematic Review)
- [ ] Reference accuracy (bidirectional verification)
- [ ] Logical soundness (workflow walkthrough)
- [ ] Contradiction detection (within & across skills)
- [ ] Completeness analysis (edge cases, error handling)
- [ ] Readability & clarity (language, structure)
- [ ] Duplication & overlap (DRY, differentiation)
- [ ] Skill chaining correctness (graph validation)

#### Functional Testing
- [ ] Run all skill functional tests
- [ ] Run all regression tests
- [ ] Test coverage report
- [ ] New test case identification

#### Documentation Sync
- [ ] README.md accuracy (chaining table, skill list)
- [ ] CLAUDE.md accuracy (architecture, conventions)
- [ ] Cross-references up to date
- [ ] Examples still valid

#### Report Generation
- [ ] Findings categorized (CRITICAL/WARNING/NOTE)
- [ ] Action items prioritized
- [ ] Regression test coverage verified
- [ ] Recommendations documented

**Time estimate:** 2-4 hours for full deep analysis of 40+ skills

---

### Preventing Regressions

**Known issues that MUST NOT recur:**

#### Issue Registry

**Location:** `docs/known-issues.md`

**Format:**
```markdown
## Issue #001: CSO Violation - Workflow in Description

**Symptom:** Skill has workflow summary in description field

**Impact:** Claude follows description instead of reading skill body (expensive wallpaper)

**Root Cause:** Description field is visible in skill list, tempting to summarize workflow

**Detection:** Automated - `validate_cso.py` checks for workflow keywords

**Prevention:**
- CSO validation in pre-commit hook
- Regression test issue-001-cso-violation.json
- Documentation in CLAUDE.md "Frontmatter Requirements"

**Last Occurrence:** 2026-01-15 (fixed in commit abc123)

**Test Coverage:** ✅ Automated + Regression test
```

#### Common Regression Patterns

| Pattern | How It Happens | Prevention |
|---------|----------------|------------|
| **CSO violations** | New skill copies old bad description | Pre-commit CSO validation |
| **Broken references** | Skill renamed, references not updated | Automated reference integrity check |
| **Missing bidirectional links** | Skill A added, forgot to update Skill B | Manual checklist + reference validation |
| **Stale tool names** | Tool renamed, old examples not updated | Grep for deprecated names in validation |
| **Flowchart syntax errors** | Copy-paste from different syntax variant | Graphviz validation pre-commit |
| **Contradictory statements** | Incremental edits without full context | Deep analysis before releases |
| **Missing Success Criteria** | New artifact-producing skill added | Section validation script |

#### Regression Prevention Workflow

**For every bug fix:**

1. **Document the issue** in `docs/known-issues.md`
2. **Create regression test** in `tests/regression/issue-XXX.json`
3. **Add validation** (automated if possible)
4. **Update checklists** (if new category of issue)
5. **Run full test suite** to verify fix doesn't break other things

**For every new skill:**

1. **Run all automated checks** before first commit
2. **Create functional tests** (at least 1 happy path)
3. **Verify in skill-review** checklist
4. **Update README.md** and potentially CLAUDE.md
5. **Deep analysis review** before marking complete

---

### Success Criteria for QA Framework

**The QA framework is working when:**

- ✅ Zero CRITICAL findings pass pre-commit validation
- ✅ All skills have at least 1 functional test
- ✅ All known issues have regression tests
- ✅ Deep analysis finds ≤5 WARNING issues per 40 skills
- ✅ No duplicate issues across releases (regressions blocked)
- ✅ New contributors can run validation locally
- ✅ CI blocks PRs with validation failures

**Not complete until:**
- Validation scripts created (Phase 1-3 minimum)
- Regression test suite established
- CI integration configured
- Documentation reviewed and approved

---

## Document Sync Quality Assurance

**CRITICAL: Universal validation for all .md files being synced across all project types.**

Document corruption can occur during any sync operation (README.md, CLAUDE.md, DESIGN.md, custom primary docs). This framework prevents corruption before it reaches git commits.

### When This Applies

**All project types:**
- **type: skills** → README.md, CLAUDE.md (via readme-sync.md, update-claude-md)
- **type: java** → DESIGN.md, CLAUDE.md (via java-update-design, update-claude-md)
- **type: custom** → Primary doc (VISION.md, THESIS.md, API.md, etc.), CLAUDE.md (via update-primary-doc, update-claude-md)
- **type: generic** → CLAUDE.md (via update-claude-md)

**Any document being automatically synchronized is at risk.**

### Validation Script

**Location:** `scripts/validate_document.py`

**Universal validation that works on any .md file:**

```bash
python scripts/validate_document.py <filepath>
```

**Exit codes:**
- `0` - No issues (clean document)
- `1` - CRITICAL issues (blocks commit)
- `2` - WARNING issues (should review)

**What it detects:**

1. **Duplicate section headers** (CRITICAL)
   - Same `## Header` appears multiple times
   - Usually caused by copy-paste errors during sync

2. **Corrupted table structures** (CRITICAL)
   - Table header followed by prose instead of separator/data rows
   - Example: `| Col1 | Col2 |` followed by "This is a description" instead of `|---|---|`

3. **Orphaned sections** (WARNING)
   - Section header with no content before next header
   - May indicate incomplete sync or missing content

4. **Large structural changes** (WARNING)
   - More than 100 lines modified
   - Requires manual structural review

### Integration Points

**All sync workflows MUST validate after applying changes:**

#### update-claude-md Step 6 (after user confirms YES)

```bash
# Apply proposed changes
# Then validate:
python scripts/validate_document.py CLAUDE.md
if [ $? -eq 1 ]; then
  echo "❌ CRITICAL: Validation failed, reverting changes"
  git restore CLAUDE.md
  exit 1
fi
```

#### java-update-design Step 6 (after user confirms YES)

```bash
# Apply proposed changes
# Then validate:
python scripts/validate_document.py docs/DESIGN.md
if [ $? -eq 1 ]; then
  echo "❌ CRITICAL: Validation failed, reverting changes"
  git restore docs/DESIGN.md
  exit 1
fi
```

#### update-primary-doc Step 6 (after user confirms YES)

```bash
# Apply proposed changes to primary doc
# Then validate:
python scripts/validate_document.py <primary-doc-path>
if [ $? -eq 1 ]; then
  echo "❌ CRITICAL: Validation failed, reverting changes"
  git restore <primary-doc-path>
  exit 1
fi
```

#### readme-sync.md Step 6 (after user confirms YES)

```bash
# Apply proposed changes
# Then validate:
python scripts/validate_document.py README.md
if [ $? -eq 1 ]; then
  echo "❌ CRITICAL: Validation failed, reverting changes"
  git restore README.md
  exit 1
fi
```

### Pre-Commit Gate (git-commit)

**Before committing, validate ALL staged .md files:**

```markdown
### Step 1c — Validate documentation files

Check for staged .md files (excluding SKILL.md):
```bash
git diff --staged --name-only | grep '\.md$' | grep -v 'SKILL\.md$'
```

**For each .md file found:**
```bash
python scripts/validate_document.py <file>
```

**If validation fails:**
- **CRITICAL (exit code 1):** BLOCK commit, show issues, ask user to fix
- **WARNING (exit code 2):** Show warnings, ask user to confirm before proceeding
```

**This runs in ALL project types** (skills, java, custom, generic).

### Portable Implementation

**The validation script is portable:**

1. **Copy to any project using these skills:**
   ```bash
   cp scripts/validate_document.py <target-project>/scripts/
   ```

2. **Works standalone (no dependencies):**
   - Pure Python 3
   - No external libraries required
   - Uses only stdlib (sys, re, pathlib, collections, subprocess)

3. **Integrates with any sync workflow:**
   - Language-agnostic (checks .md syntax, not content semantics)
   - Works on any document type (README, DESIGN, VISION, THESIS, etc.)
   - Project-type independent

### Common Document Corruption Patterns

**These patterns are detected automatically:**

| Pattern | Example | Detection | Prevention |
|---------|---------|-----------|------------|
| **Duplicate headers during restructure** | Two "## Skills" sections | Duplicate header check | Validate before commit |
| **Table header + prose** | `\| Col1 \| Col2 \|` followed by description text | Corrupted table check | Validate table format |
| **Copy-paste from wrong section** | Section content pasted under wrong header | Orphaned section check | Review large diffs |
| **Incomplete sync** | Section header added but content not synced | Orphaned section check | Validate completeness |
| **Merge conflict corruption** | `<<<<<<< HEAD` markers in document | Git diff check | Pre-commit validation |

### Regression Prevention

**Add to Issue Registry:**

```markdown
## Issue #002: Document Corruption During Sync

**Symptom:** Duplicate sections, corrupted tables, orphaned headers

**Impact:** Unreadable documentation, broken links, user confusion

**Root Cause:** Sync operations (update-claude-md, java-update-design, etc.) can introduce corruption when proposing large changes

**Detection:** Automated - `validate_document.py` checks all .md files

**Prevention:**
- Universal validation in all sync workflows
- Pre-commit gate in git-commit for all project types
- Automated revert if validation fails
- Documentation in CLAUDE.md "Document Sync Quality Assurance"

**Test Coverage:** ✅ Automated validation on all sync operations
```

### Success Criteria

Document sync quality assurance is working when:

- ✅ All sync workflows validate before staging
- ✅ git-commit validates all staged .md files (all project types)
- ✅ CRITICAL corruption is automatically caught and reverted
- ✅ Zero document corruption reaches commits
- ✅ Validation script is portable to all projects using these skills
- ✅ Users never need to manually check for corruption

**Not complete until:**
- validate_document.py created and tested
- All 4 sync workflows updated (update-claude-md, java-update-design, update-primary-doc, readme-sync.md)
- git-commit updated to validate all .md files
- CLAUDE.md documentation complete
