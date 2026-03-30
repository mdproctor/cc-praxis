# Claude Code Skills for Java & Quarkus Development

A curated collection of specialized skills for Claude Code that streamline Java development, focusing on Quarkus applications, quarkus-flow workflows, and professional software engineering practices.

## Overview

These skills transform Claude Code into an expert Java/Quarkus development assistant that understands enterprise-grade code quality, safety requirements, and modern cloud-native patterns. Each skill encodes best practices, common pitfalls, and project-specific conventions to ensure consistent, production-ready code.

**Key Features:**
- ✅ **❌/✅ Code examples** showing wrong and right approaches
- ✅ **Quick Reference tables** for instant lookup
- ✅ **Red Flags section** in java-dev to prevent rationalizations
- ✅ **Common Pitfalls tables** documenting mistakes with fixes
- ✅ **Real-World Impact** sections with production incidents
- ✅ **Decision flowcharts** for complex workflows
- ✅ **Automatic skill chaining** (dev → review → commit → design sync)
- ✅ **Automatic DESIGN.md sync** with every commit
- ✅ **Quarkus/Vert.x specialized** (event loop, BOM, reactive patterns)
- ✅ **RED-GREEN-REFACTOR validated** (tested under pressure scenarios)

## Getting Started: Project Type Setup

**IMPORTANT:** Skills route differently based on project type. First-time commit in any repository will guide you through setup interactively, or you can set it up manually.

### The 4 Project Types

| Type | When to Use | Documentation | Commit Skill |
|------|-------------|---------------|--------------|
| **skills** | Claude Code skill repositories (has `*/SKILL.md` files) | README.md + CLAUDE.md (auto-synced) | `git-commit` |
| **java** | Java/Maven/Gradle projects | DESIGN.md (required) + CLAUDE.md (optional, auto-synced) | `java-git-commit` |
| **custom** | Working groups, research, docs, advocacy | User-configured primary document (auto-synced) | `custom-git-commit` |
| **generic** | Everything else | CLAUDE.md optional (auto-synced) | `git-commit` |

### Quick Setup

**Option 1: Automatic (Recommended)**

Just try to commit. If `CLAUDE.md` is missing or has no project type, `git-commit` will ask you 4 questions and create it for you:

```bash
git add <your files>
# Then say "commit" to Claude - it will guide you through setup
```

**Option 2: Manual**

Create `CLAUDE.md` in your repository root:

**For Skills Repositories:**
```markdown
## Project Type

**Type:** skills
```

**For Java Projects:**
```markdown
## Project Type

**Type:** java
```
Then create `docs/DESIGN.md` (java-git-commit will block without it).

**For Custom Projects** (working groups, research, docs, etc.):
```markdown
## Project Type

**Type:** custom
**Primary Document:** docs/vision.md

**Sync Strategy:** bidirectional-consistency

**Sync Rules:**
| Changed Files | Document Section | Update Type |
|---------------|------------------|-------------|
| catalog/*.md | Vision - Current Landscape | Add project summary |
| docs/meetings/*.md | Governance | Add meeting summary |

**Current Milestone:** Phase 1 - Discovery
```

**For Generic Projects:**
```markdown
## Project Type

**Type:** generic
```

### What Happens at Commit Time

**type: skills** → `git-commit`:
- Validates SKILL.md files with `skill-review`
- Auto-syncs README.md (skill catalog)
- Auto-syncs CLAUDE.md (workflow conventions)

**type: java** → `java-git-commit`:
- Requires docs/DESIGN.md (blocks if missing)
- Auto-syncs DESIGN.md (architecture)
- Auto-syncs CLAUDE.md (workflow conventions)
- Java-specific commit scopes (`rest`, `repository`, `service`, etc.)

**type: custom** → `custom-git-commit`:
- Syncs user-configured primary document (VISION.md, THESIS.md, etc.)
- Follows user's Sync Rules table
- Auto-syncs CLAUDE.md (workflow conventions)

**type: generic** → `git-commit`:
- Auto-syncs CLAUDE.md if it exists
- Basic conventional commits

### Why Explicit Type Declaration?

**We tried auto-detection.** It was fragile:
- Research repos with pom.xml files got treated as Java projects
- Java projects without pom.xml yet got treated as generic
- Renaming files broke detection mid-project

**Explicit declaration is better:**
- You know exactly what workflow you're getting
- Type won't change unexpectedly
- Easy to override if project evolves
- Clear error messages when using wrong skill

### Changing Project Types

Just edit CLAUDE.md and change the type. Example: research project graduates to production Java service:

```diff
## Project Type

-**Type:** custom
-**Primary Document:** THESIS.md
+**Type:** java
```

Remove custom-specific fields, create `docs/DESIGN.md`, and you're done.

## Why Commit Messages and Design Docs Actually Matter (Yes, Really)

Let's be honest: writing good commit messages and keeping design documentation in sync with code is about as exciting as watching paint dry. It ranks somewhere between "updating Jira tickets" and "mandatory corporate training videos" on the Developer Fun Scale™.

**The usual developer experience:**
- **3:00 PM:** Write brilliant code solving a complex problem
- **3:45 PM:** `git commit -m "fix stuff"` (you'll remember what it does, right?)
- **3:46 PM:** Move on to next task (design doc? what design doc?)
- **Next Tuesday:** Teammate asks "Why did we change the cache invalidation strategy?"
- **You:** *frantically scrolls through git log* "Uhh... 'fix stuff', 'more fixes', 'actually fix it this time'..."
- **3 months later:** You're debugging and find your own code. No idea why it works that way. Commit message: "refactor". Thanks, past you. Really helpful.

**The actual cost of bad commit messages:**
- **Debugging time:** 30 minutes trying to understand why code exists → discover commit message is "wip" → give up, rewrite it
- **Code review delays:** Reviewer has no context → asks 10 clarifying questions → you forgot what you did → meeting scheduled
- **Incident post-mortems:** "When did this bug get introduced?" → `git bisect` → 20 commits all say "updates" → cry
- **Onboarding new developers:** "Just read the git history to understand the architecture" → they quit

**The actual cost of stale design docs:**
- **Architecture drift:** DESIGN.md says system uses Redis → code actually uses Hazelcast (changed 8 months ago, doc never updated)
- **Wrong decisions:** New developer reads outdated doc → implements feature the wrong way → has to redo it
- **Meeting overhead:** Every design question becomes "let me check the code to see what we actually did"
- **Institutional knowledge loss:** Senior dev leaves → their mental model of the system dies with them

**The automation win:**

These skills make documentation *painless* by doing it *as you code*:
- `java-git-commit` generates proper conventional commit messages automatically by analyzing your actual changes
- `java-update-design` keeps DESIGN.md in sync with code *before* you commit, not as a quarterly exercise
- Both work together so documentation is *part of* the commit, not a separate chore you skip

**Result:** Six months from now, you'll thank yourself. Your teammates will thank you. The new hire will thank you. And that 2 AM production incident? The git history will actually help instead of making you want to rage-quit.

You're not writing documentation. You're leaving breadcrumbs for Future You, who has the memory of a goldfish and the patience of a caffeinated squirrel.

## Why Skills Even Exist

**The problem:** Without skills, every conversation with Claude starts from scratch:
- Claude: "Let me write this workflow with a `for` loop!"
- You: "No, use the FuncDSL. We talked about this yesterday."
- Claude: "Right! Let me mock the database."
- You: "No! Real database! We *just* discussed this!"
- Claude: "Got it! Should I use `HashMap`?"
- You: *flips desk*

**The solution:** Skills = "things we've already figured out, written down once, so we never have to explain them again." Think of them as the difference between training a golden retriever and training a goldfish.

## Skills Architecture

This collection follows a **layered architecture** where foundation skills provide universal principles, and specialized skills extend them for specific languages, frameworks, and workflows.

### Layer 1: Commit Workflow (3 skills)

**Pattern:** Router → Specialized Handlers

| Skill | Purpose | Project Types |
|-------|---------|---------------|
| **git-commit** | Entry point, routes based on project type | skills, generic |
| **java-git-commit** | Java-specific commits with DESIGN.md sync | java |
| **custom-git-commit** | User-configured commits with primary doc sync | custom |

### Layer 2: Documentation Sync (4 skills)

**Pattern:** Document Type Specialists

| Skill | Document | Project Types | Auto-Invoked By |
|-------|----------|---------------|-----------------|
| **update-claude-md** | CLAUDE.md (workflows) | all | git-commit, java-git-commit, custom-git-commit |
| **java-update-design** | DESIGN.md (architecture) | java | java-git-commit |
| **readme-sync.md** | README.md (skill catalog) | skills | git-commit |
| **update-primary-doc** | User-configured doc | custom | custom-git-commit |

### Layer 3: Review (3 skills)

**Pattern:** Domain-Specific Review Specialists

| Skill | Reviews | Auto-Invoked By | Blocks On |
|-------|---------|-----------------|-----------|
| **skill-review** | SKILL.md structure | git-commit | CRITICAL findings |
| **java-code-review** | Java code quality | java-git-commit | CRITICAL findings |
| **java-security-audit** | OWASP Top 10 | java-code-review | Security vulnerabilities |

### Layer 4: Principles (4 skills)

**Pattern:** Universal Foundations (Referenced, Not Invoked)

| Skill | Domain | Extended By |
|-------|--------|-------------|
| **code-review-principles** | Universal code review | java-code-review |
| **security-audit-principles** | Universal OWASP Top 10 | java-security-audit |
| **dependency-management-principles** | Universal BOM patterns | maven-dependency-update |
| **observability-principles** | Universal logging/tracing/metrics | quarkus-observability |

### Layer 5: Java/Quarkus Development (4 skills)

**Pattern:** Layered Specialization

| Skill | Purpose | Builds On |
|-------|---------|-----------|
| **java-dev** | Java development foundation | (base layer) |
| **quarkus-flow-dev** | Quarkus Flow workflows | java-dev |
| **quarkus-flow-testing** | Workflow testing | java-dev, quarkus-flow-dev |
| **quarkus-observability** | Quarkus observability config | observability-principles |

### Layer 6: Utilities (2 skills)

| Skill | Purpose | Builds On |
|-------|---------|-----------|
| **maven-dependency-update** | Maven BOM management | dependency-management-principles |
| **adr** | Architecture Decision Records | (standalone) |

---

## Skills

### Layer 1: Commit Workflow

#### **git-commit**
Generic conventional commit workflow for any repository:
- Generates conventional commit messages (Conventional Commits 1.0.0)
- **Routes to specialized skills** based on project type (java-git-commit for type: java, custom-git-commit for type: custom)
- **Interactive setup** if CLAUDE.md missing (prompts for project type)
- Works with any codebase or file types
- Proposes commit message for user review before committing
- Base workflow extended by java-git-commit and custom-git-commit

**Features:**
- Decision Flow flowchart (stage → generate → propose → commit)
- Conventional commit type and scope reference
- Common Pitfalls table
- Language-agnostic examples

**Triggers:** "commit", "make a commit", `/git-commit` in non-Java repositories.

#### **java-git-commit**
Intelligent commit workflow that extends git-commit with:
- **Enforces DESIGN.md existence** — blocks commits if `docs/DESIGN.md` is missing
- Java/Quarkus-specific scope suggestions (controller, service, repository, BOM)
- Automatic DESIGN.md synchronization via `java-update-design` skill
- Maven/Gradle awareness

**Features:**
- Decision flowchart showing complete commit + design sync process
- Common Pitfalls table (11 commit mistakes including Java-specific)
- Java-specific scope and type examples
- Simplified workflow (references git-commit, adds DESIGN.md sync)

**Triggers:** "commit" in repositories with `type: java` declared in CLAUDE.md, or explicitly via "smart commit", "update design and commit", `/java-git-commit`.

#### **custom-git-commit**
Intelligent commit workflow for custom project types (working groups, research, documentation, advocacy):
- **User-configured primary document sync** — reads sync strategy from CLAUDE.md
- Flexible sync via Sync Rules table (file patterns → document sections)
- Support for multiple sync strategies (bidirectional-consistency, research-progress, api-spec-sync, architectural-changes)
- Milestone alignment tracking

Extends git-commit with user-configured synchronization for projects that don't fit skills/java patterns.

**Features:**
- Decision flowchart showing complete commit + primary doc sync process
- Common Pitfalls table (custom project mistakes)
- Examples for 4 custom project archetypes (working groups, research, API docs, standards)
- Flexible table-driven sync (no hardcoded project knowledge)

**Triggers:** "commit" in repositories with `type: custom` declared in CLAUDE.md.

### Layer 2: Documentation Sync

#### **update-claude-md**
Maintains CLAUDE.md documentation in sync with workflow and convention changes:
- Build commands and development workflows
- Testing patterns and commands
- Naming conventions and code organization
- Repository-specific tools and processes
- Skill lists (for skills repositories)

**Features:**
- Common Pitfalls table (documentation mistakes)
- Skills repository awareness (skill naming, cross-references)
- Code repository support (build tools, testing frameworks)

Invoked automatically by `git-commit` and `java-git-commit` (if CLAUDE.md exists), or independently. Handles workflow documentation; for architectural documentation, see `java-update-design`.

#### **java-update-design**
Maintains DESIGN.md documentation in sync with code changes, capturing:
- Component structure and responsibilities
- Architectural patterns
- Integration points
- Technical decisions

**Features:**
- Common Pitfalls table (9 documentation mistakes)
- Java-specific signal detection (annotations → architectural meaning)

Invoked automatically by `java-git-commit` or independently. Handles architectural documentation; for workflow/convention documentation, see `update-claude-md`.

#### **readme-sync.md**
Maintains README.md documentation in sync with skill collection changes in skills repositories:
- Skill descriptions (Skills section)
- Chaining relationships (Skill Chaining Reference table)
- Feature additions (Key Features section)
- Repository structure changes

**Features:**
- Common Pitfalls table (8 documentation mistakes)
- Skills repository awareness (skill naming, chaining patterns)

Invoked automatically by `git-commit` (if README.md exists and skill changes detected), or independently. Specific to skills repositories; for code repositories, use project-specific documentation tools.

#### **update-primary-doc**
Generic table-driven primary document synchronization for custom projects:
- Syncs VISION.md, THESIS.md, or user-configured primary documents
- Reads Sync Rules from CLAUDE.md (file patterns → document sections)
- Supports 4 built-in sync strategies + custom strategies
- Section-aware updates (headings, subsections)
- Glob pattern matching (*, **, exact paths)

**Features:**
- Common Pitfalls table (sync configuration mistakes)
- 4 sync strategies documented (bidirectional-consistency, research-progress, api-spec-sync, architectural-changes)
- Pattern matching examples
- Proposal-only (returns changes to calling skill for user confirmation)

Invoked automatically by `custom-git-commit` when Sync Rules configured in CLAUDE.md. Generic processor with no hardcoded project knowledge—all behavior driven by user's Sync Rules table.

### Layer 3: Review

#### **skill-review**
Pre-commit review for Claude Code skills ensuring structural integrity, CSO compliance,
and documentation completeness:
- Frontmatter validation (name, description, CSO rules)
- Flowchart syntax testing (Graphviz validation)
- Naming convention compliance (generic `-principles`, language prefixes)
- Cross-reference verification (bidirectional chaining)
- Documentation completeness (Success Criteria, Common Pitfalls, Prerequisites)
- Severity assignment (CRITICAL/WARNING/NOTE)
- **Deep Analysis Mode:** Comprehensive validation beyond basic structural checks

Builds quality assurance discipline specifically for skills repositories. Blocks commits
on CRITICAL findings (invalid frontmatter, broken flowcharts, CSO violations).

**Features:**
- Review checklist by category (frontmatter, naming, cross-references, flowcharts)
- Severity decision flowchart
- Deep analysis procedures (reference accuracy, logical soundness, completeness)
- Automated validation scripts (`scripts/validate_all.py` orchestrates 7 validators)
- Integration with QA framework (see CLAUDE.md § Quality Assurance Framework)
- Common Pitfalls table (8 skill authoring mistakes)
- Cross-reference bidirectional verification

**Triggers:** "review my skill", "check this skill", `/skill-review`, or automatically when SKILL.md files are staged for commit.

#### **java-code-review**
Pre-commit code review for Java/Quarkus applications enforcing:
- Critical safety checks (resource leaks, classloader issues, deadlock risks)
- Concurrency correctness for Quarkus/Vert.x event loop
- Performance best practices for cloud deployments
- Testing coverage validation
- Code clarity standards

Builds on code-review-principles with Java-specific checks. Assigns severity levels (CRITICAL/WARNING/NOTE) and blocks commits on critical findings.

**Features:**
- Prerequisites section (extends code-review-principles)
- Java/Quarkus-specific violation patterns
- ❌/✅ code examples for Safety, Concurrency, Performance, Testing sections
- Integration with java-git-commit workflow

**Triggers:** "review my code", "check my changes", `/java-code-review`, or automatically via `java-git-commit`.

#### **java-security-audit**
Security vulnerability review for Java/Quarkus applications:
- OWASP Top 10 checks adapted for Quarkus server-side apps
- Injection prevention (SQL, Log, Command)
- Broken authentication and access control detection
- Cryptographic failures and security misconfiguration
- SSRF and unvalidated redirect checks
- Quarkus security feature recommendations

Builds on security-audit-principles with Java/Quarkus-specific patterns.

**Features:**
- Prerequisites section (extends security-audit-principles)
- ❌/✅ code examples for each OWASP category
- Quarkus-specific security patterns and configurations
- Integration with Vault, OIDC, and security extensions

**Triggers:** "security review", "audit security", "OWASP", or when reviewing auth/authorization/PII handling code.

### Layer 4: Principles (Foundation Layer)

> **Note:** These skills are referenced via Prerequisites, not invoked directly.

#### **code-review-principles**
Universal code review principles covering safety, concurrency, performance, testing philosophy, and review workflow. Language-agnostic checklist with severity assignment guidance.

**Features:**
- Safety violation patterns (resource leaks, deadlocks, silent corruption)
- Concurrency checklist (blocking on async threads, thread-safe collections)
- Performance principles for hot paths
- Testing philosophy (real implementations over mocks)
- Severity assignment flow
- Common pitfalls table

**Extended by:** java-code-review (and future language-specific reviews)

#### **security-audit-principles**
Universal OWASP Top 10 security audit principles for server-side applications. Language-agnostic vulnerability identification.

**Features:**
- OWASP Top 10 checklist (injection, auth, access control, crypto, config, etc.)
- Severity decision flow
- Defense in depth principles
- Common security pitfalls table

**Extended by:** java-security-audit (and future language-specific audits)

#### **dependency-management-principles**
Universal dependency management principles for BOM (Bill of Materials) patterns. Works with any package manager.

**Features:**
- BOM alignment decision flow
- Compatibility checking workflow
- Version drift prevention
- When to create ADRs for dependencies
- Common pitfalls table

**Extended by:** maven-dependency-update (and future package managers)

#### **observability-principles**
Universal observability principles: structured logging, distributed tracing, and metrics. Technology-agnostic guidance.

**Features:**
- Three pillars of observability (logs, traces, metrics)
- MDC/correlation ID patterns
- HTTP header propagation
- OpenTelemetry concepts
- Metrics types (counters, histograms, gauges)
- Production configuration checklist

**Extended by:** quarkus-observability (and future frameworks)

### Layer 5: Java/Quarkus Development

#### **java-dev**
Expert Java development for Quarkus server-side applications with focus on:
- Safety-first approach (resource leaks, deadlocks, silent corruption)
- Performance optimization for cloud deployments
- Concurrency patterns aligned with Quarkus/Vert.x event loop
- Testing with JUnit 5, AssertJ, and Quarkus test annotations

**Features:**
- Quick Reference table (safety, concurrency, performance, testing, code quality)
- Rule Priority Flow flowchart (Safety > Concurrency > Performance > Code Quality)
- "Red Flags — These Thoughts Mean STOP" 4-column rationalization table (Problem-Impact-Fix)
- "Why These Rules Matter" section with 6 real production incidents
- ❌/✅ code examples for Safety, Concurrency, Performance sections
- Enhanced Skill Chaining (6 comprehensive skill references)
- RED-GREEN-REFACTOR validated (prevents resource leaks under pressure)

**Triggers:** Writing Java classes, fixing bugs, refactoring, working with `.java`, `pom.xml`, or build files.

#### **quarkus-flow-dev**
Specialized development for quarkus-flow (CNCF Serverless Workflow) including:
- Workflow DSL patterns with FuncDSL
- Task composition (function/agent/http/emit/listen)
- Human-in-the-loop (HITL) patterns
- LangChain4j AI service integration

**Features:**
- Prerequisites section (builds on java-dev rules)
- Task DSL Quick Reference table (12 common patterns)
- Complete API reference extracted to `funcDSL-reference.md`
- Common Pitfalls table (7 mistakes and fixes)
- HITL pattern example with full workflow
- Enhanced Skill Chaining (includes quarkus-observability)
- Token-optimized: 31.5% reduction from original size

**Triggers:** Flow subclasses, workflow YAML, mentions of "workflow", "agent", "agentic", or "LangChain4j".

#### **quarkus-flow-testing**
Comprehensive testing patterns for quarkus-flow workflows:
- Unit tests with `@QuarkusTest` and injected workflows
- YAML workflow testing with `@Identifier`
- REST integration tests with REST Assured
- RFC 7807 error mapping validation
- AI service mocking strategies (`@InjectMock`, `@QuarkusTestProfile`)

**Features:**
- Prerequisites section (builds on java-dev and quarkus-flow-dev)
- Quick Reference table for test types
- Common Pitfalls table (7 mistakes)
- Two mocking strategies with complete examples

**Triggers:** "test workflow", "mock agent", `@QuarkusTest` for Flow classes, debugging workflow test failures.

#### **quarkus-observability**
Configures production-grade observability for Quarkus/quarkus-flow:
- Structured JSON logging with MDC
- quarkus-flow workflow tracing (instance tracking)
- OpenTelemetry distributed tracing
- Micrometer/Prometheus metrics
- Log aggregator integration (Kibana, Loki, Datadog)

Builds on observability-principles with Quarkus-specific configuration.

**Features:**
- Prerequisites section (extends observability-principles)
- Quarkus extension configuration (quarkus-logging-json, quarkus-opentelemetry)
- quarkus-flow-specific workflow tracing patterns
- application.properties configuration examples

**Triggers:** Mentions of "logging", "tracing", "observability", "MDC", "OpenTelemetry", "metrics", workflow debugging.

### Layer 6: Utilities

#### **maven-dependency-update**
Maven dependency management with BOM-first approach:
- Quarkus platform alignment verification
- BOM-managed vs explicit version detection
- Compatibility checking before version bumps
- Safe upgrade proposals with risk assessment

Builds on dependency-management-principles with Maven/Quarkus-specific workflow.

**Features:**
- Prerequisites section (extends dependency-management-principles)
- Maven-specific BOM alignment rules
- Quarkus platform version compatibility checking
- pom.xml manipulation workflow

**Triggers:** "update dependencies", "bump version", "upgrade Quarkus", "add dependency", `pom.xml` changes.

#### **adr**
Creates and manages Architecture Decision Records (ADRs) in MADR format:
- Sequential numbering and lifecycle management
- Captures context, alternatives, and tradeoffs
- Append-only with supersession tracking
- Stored in `docs/adr/`

**Features:**
- Common Pitfalls table (8 ADR anti-patterns)
- MADR template with all sections
- Lifecycle management guide

**Triggers:** "create an ADR", significant technical decisions, major version upgrades, new extension adoption.

---

## How Skills Work Together

Skills are designed to chain together for complete workflows:

### Development → Review → Commit (Java repositories)
```
java-dev or quarkus-flow-dev
  → quarkus-flow-testing (if writing tests)
  → java-code-review (automatic or manual)
    → java-git-commit
      → java-update-design + update-claude-md (automatic)
```

### Skill Development → Review → Commit (Skills repositories)
```
superpowers:writing-skills
  → skill-review (automatic when SKILL.md staged)
  → git-commit
    → update-claude-md + readme-sync.md (automatic)
```

### Architecture Decision → Documentation
```
Major decision made
  → adr (document decision)
  → git-commit
    → update-claude-md (automatic, adds ADR to "Key Decisions" section)
```

### Dependency Update → Review → Documentation
```
maven-dependency-update
  → java-code-review (if code compatibility changes)
  → adr (if significant version jump or new extension)
  → java-git-commit
    → java-update-design (documents new dependency architecture)
```

### Observability Setup → Dependencies → Commit
```
quarkus-observability
  → maven-dependency-update (adds OpenTelemetry/Micrometer extensions)
  → adr (documents observability strategy)
  → java-git-commit
    → java-update-design (documents monitoring architecture)
```

---

## Key Features (What Makes These Skills Different)

- ✅ **❌/✅ Code examples** - Wrong vs right approaches for safety, concurrency, performance
- ✅ **Quick Reference tables** - Instant lookup without reading full skill
- ✅ **Red Flags section** in java-dev - Stops rationalization dead in its tracks
- ✅ **Common Pitfalls tables** - Real mistakes with fixes (Mistake | Why It's Wrong | Fix)
- ✅ **Real-World Impact sections** - Production incidents showing why rules exist
- ✅ **Decision flowcharts** - Complex decisions as visual diagrams
- ✅ **Automatic skill chaining** - dev → review → commit → design sync
- ✅ **Automatic DESIGN.md sync** - Architecture docs stay current with every commit
- ✅ **Automatic CLAUDE.md sync** - Workflow docs stay current with convention changes
- ✅ **Automatic README.md sync** - Skill catalog stays current (skills repos only)
- ✅ **Universal document validation** - Automatic corruption detection prevents sync regressions across all project types
- ✅ **Quarkus/Vert.x specialized** - Event loop awareness, BOM patterns, reactive patterns
- ✅ **RED-GREEN-REFACTOR validated** - Tested under pressure, prevents resource leaks

---

## Usage

### For Java Development

**When writing code:**
```
You: "I need to add pagination to the REST endpoint"
Claude: [Uses java-dev] Creates paginated endpoint with proper resource handling
```

**When committing:**
```
You: "commit"
Claude: [Uses java-git-commit]
  → Runs java-code-review (if not done)
  → Generates conventional commit message
  → Updates DESIGN.md via java-update-design
  → Updates CLAUDE.md via update-claude-md
  → Commits all changes together
```

### For Skills Development

**When creating a skill:**
```
You: "I want to create a Python development skill"
Claude: [Uses superpowers:writing-skills] Drafts skill with proper structure
```

**When committing:**
```
You: "commit"
Claude: [Uses git-commit]
  → Validates SKILL.md via skill-review
  → Generates conventional commit message
  → Updates README.md via readme-sync.md
  → Updates CLAUDE.md via update-claude-md
  → Commits all changes together
```

---

## Requirements

- **Claude Code** (CLI, Desktop, Web, or IDE extension)
- **For Java skills:** JDK 17+, Maven or Gradle
- **For commit skills:** Git configured with user name/email
- **For DESIGN.md sync:** docs/DESIGN.md must exist (java-git-commit will block without it)

---

## Skill Chaining Reference

Each skill explicitly declares when to chain to other skills:

| From Skill | To Skill | When |
|------------|----------|------|
| `git-commit` | skill-validation.md workflow | SKILL.md files staged (type: skills) |
| `git-commit` | readme-sync.md workflow | README.md exists + skill changes (type: skills) |
| `git-commit` | `update-claude-md` | CLAUDE.md exists |
| `git-commit` | `java-git-commit` | Routes if type: java declared |
| `git-commit` | `custom-git-commit` | Routes if type: custom declared |
| `java-git-commit` | `java-code-review` | Automatic (if not done this session) |
| `java-git-commit` | `java-update-design` | Always (automatic) |
| `java-git-commit` | `update-claude-md` | CLAUDE.md exists (automatic) |
| `custom-git-commit` | `update-primary-doc` | Sync Rules configured (automatic) |
| `custom-git-commit` | `update-claude-md` | CLAUDE.md exists (automatic) |
| `java-code-review` | `java-security-audit` | Security-critical code detected |
| `java-dev` | `java-code-review` | User triggers review |
| `quarkus-flow-dev` | `quarkus-flow-testing` | Writing tests for workflows |
| `quarkus-flow-dev` | `java-code-review` | User triggers review |
| `quarkus-flow-testing` | `java-code-review` | User triggers review |
| `maven-dependency-update` | `java-code-review` | Code compatibility changes needed |
| `maven-dependency-update` | `adr` | Major version jump or new extension |
| `quarkus-observability` | `maven-dependency-update` | Adding OTEL/Micrometer deps |
| `adr` | `java-git-commit` | Stage ADR with related changes |
| `java-update-design` | (companion: `update-claude-md`) | Architecture changes often need workflow doc updates |
| `readme-sync.md` | (companion: `update-claude-md`) | Skill changes often need workflow doc updates |

---
## License

Copyright 2026 Mark Proctor

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Contributing

These skills are tailored for specific project conventions. When adapting for your own use:

1. Review safety and concurrency rules in `java-dev`
2. Adjust conventional commit types in `java-git-commit`
3. Customize BOM versions in `maven-dependency-update`
4. Update observability endpoints in `quarkus-observability`
5. Extend generic principles skills for other languages/frameworks (e.g., `go-code-review`, `gradle-dependency-update`)

## Skill Quality & Validation

All skills have been systematically improved following the [superpowers:writing-skills](https://github.com/anthropics/superpowers) methodology:

- ✅ **CSO-optimized descriptions** (Claude Search Optimization) - trigger-focused, no workflow summaries
- ✅ **Token efficiency** - heavy reference material extracted to separate files
- ✅ **Quick Reference tables** - scannable summaries for fast lookup
- ✅ **Common Pitfalls tables** - documented mistakes with fixes (standardized 3-column format)
- ✅ **Real-World Impact** - production incidents demonstrating why rules matter
- ✅ **Decision flowcharts** - visual guides for non-obvious decisions (Graphviz-validated)
- ✅ **RED-GREEN-REFACTOR validation** - java-dev tested under pressure scenarios

**Testing methodology:** Skills are validated by running baseline scenarios WITHOUT the skill (documenting agent behavior), then WITH the skill (verifying compliance). The java-dev skill successfully prevented resource leaks under combined time pressure, authority pressure, and sunk cost.

**Recent quality improvements (2026-03):**
- ✅ **Logic correctness audit:** Fixed 15 logic errors (4 CRITICAL, 7 MAJOR, 4 MINOR) including invalid Maven commands, missing flowchart paths, broken cross-references, and command correctness issues
- ✅ **Security audit:** Comprehensive OWASP Top 10 review completed — 9.2/10 security posture, zero vulnerabilities detected, excellent safety controls throughout
- ✅ **Readability enhancements:** Applied 4 systematic patterns across 14 skills — standardized table formatting, added section transitions, made decision points explicit, added visual separators for improved scannability
- ✅ **Cross-reference integrity:** All skill chaining verified bidirectionally, Prerequisites sections accurate, flowcharts validated with `dot`
- ✅ **Consistency enforcement:** All skills follow conventions (naming patterns, section ordering, Common Pitfalls format, Success Criteria for artifact-producing skills)

### Document Sync Quality Assurance

**Universal validation framework prevents documentation corruption across all project types.**

**What gets validated:**
- ✅ All .md files before commit (git-commit Step 1c)
- ✅ CLAUDE.md after sync (update-claude-md)
- ✅ DESIGN.md after sync (java-update-design)
- ✅ README.md after sync (readme-sync.md)
- ✅ Primary documents after sync (update-primary-doc for VISION.md, THESIS.md, etc.)

**Validation checks:**
| Check | Severity | Action |
|-------|----------|--------|
| **Duplicate headers** | CRITICAL | Block commit, revert changes |
| **Corrupted tables** | CRITICAL | Block commit, revert changes |
| **Orphaned sections** | WARNING | Ask user to confirm |
| **Large line changes** | WARNING | Ask user to confirm |

**Implementation:**
- `scripts/validate_document.py` - Portable Python 3 validator (no dependencies)
- Exit code 0 = clean, 1 = CRITICAL (blocks), 2 = WARNING (asks user)
- Automatic revert on corruption: `git restore <file>`
- Works in all project types (skills/java/custom/generic)

**Regression prevention:**
- Issue #002: README.md corruption (341 lines of duplicates) - RESOLVED
- Automatic pre-commit validation prevents recurrence
- All sync workflows validate before staging

See **CLAUDE.md § Document Sync Quality Assurance** for complete framework documentation.

## Repository Structure

```
.
├── LICENSE                              # Apache License 2.0
├── README.md                            # This file
├── CLAUDE.md                            # Guidance for Claude Code
├── scripts/                             # Validation and automation
│   └── validate_document.py            # Universal .md corruption detector
├── skill-validation.md                  # Skills-specific SKILL.md validation workflow
├── readme-sync.md                       # Skills-specific README.md sync workflow
├── code-review-principles/              # Generic code review principles
│   └── SKILL.md
├── security-audit-principles/           # Generic security audit principles
│   └── SKILL.md
├── dependency-management-principles/    # Generic dependency management principles
│   └── SKILL.md
├── observability-principles/            # Generic observability principles
│   └── SKILL.md
├── java-dev/                            # Core Java/Quarkus development
│   └── SKILL.md
├── quarkus-flow-dev/                    # Serverless Workflow patterns
│   ├── SKILL.md
│   └── funcDSL-reference.md            # Complete FuncDSL API reference
├── quarkus-flow-testing/                # Workflow testing patterns
│   └── SKILL.md
├── skill-review/                        # SKILL.md validation and review
│   └── SKILL.md
├── java-code-review/                    # Java-specific code review
│   └── SKILL.md
├── java-security-audit/                 # Java-specific security audit
│   └── SKILL.md
├── git-commit/                          # Generic conventional commits
│   └── SKILL.md
├── java-git-commit/                     # Java-specific smart commits
│   └── SKILL.md
├── java-update-design/                       # DESIGN.md maintenance
│   └── SKILL.md
├── update-claude-md/                    # CLAUDE.md maintenance
│   └── SKILL.md
├── adr/                                 # Architecture Decision Records
│   └── SKILL.md
├── maven-dependency-update/             # Maven dependency management
│   └── SKILL.md
└── quarkus-observability/               # Quarkus observability setup
    └── SKILL.md
```
