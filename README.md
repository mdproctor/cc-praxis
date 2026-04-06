<p align="center">
  <img src="logo.svg" width="140" alt="cc-praxis logo"/>
</p>

# cc-praxis

A curated collection of Claude Code skills for professional software development — with deep Java/Quarkus support and universal principles that apply to any project.

## Installation

### Quick Start — Claude Code Marketplace

```bash
# Add this marketplace to Claude Code
/plugin marketplace add github.com/mdproctor/cc-praxis

# Run the one-time bootstrap wizard
/plugin install install-skills
/install-skills
```

The `/install-skills` wizard:
- Configures a session-start hook for automatic CLAUDE.md detection
- Lets you choose what to install (all skills, Java/Quarkus bundle, foundation principles, or individual)
- Automatically resolves and installs dependencies
- Verifies the setup

After the wizard completes, **close that conversation** — skills are then available in all future sessions.

> **Dependency resolution note:** The official Claude Code marketplace doesn't yet support automatic dependency resolution ([Issue #9444](https://github.com/anthropics/claude-code/issues/9444)). The `/install-skills` wizard handles this for you. If you prefer installing manually, use the `scripts/claude-skill` installer below.

**To uninstall:**
```bash
/uninstall-skills
```

The wizard checks for reverse dependencies and confirms before removing anything.

---

### Web UI — `scripts/web_installer.py`

If you have the repository cloned locally, the web installer gives you a visual browser for managing skills:

```bash
python3 scripts/web_installer.py          # opens http://localhost:8765 automatically
python3 scripts/web_installer.py --port 8766 --no-browser
```

Or after the plugin is installed: just run `cc-praxis` in your terminal.

---

### Manual Installer — `scripts/claude-skill`

Clone the repository and use the bundled installer directly. This gives you automatic dependency resolution without the wizard, plus the full local development workflow described in [Contributing & Local Development](#contributing--local-development).

```bash
git clone https://github.com/mdproctor/cc-praxis.git ~/cc-praxis
cd ~/cc-praxis
```

```bash
# Install individual skills (auto-resolves dependencies)
scripts/claude-skill install java-dev
scripts/claude-skill install quarkus-flow-testing   # installs java-dev + quarkus-flow-dev automatically

# Install all skills
scripts/claude-skill install-all -y

# List what's installed
scripts/claude-skill list

# Uninstall
scripts/claude-skill uninstall java-dev
scripts/claude-skill uninstall-all -y
```

**Installed skills location:** `~/.claude/skills/`

---

## Overview

Each skill encodes battle-tested best practices, common pitfalls, and project-specific conventions so Claude Code gives consistent, production-ready guidance without re-explaining the same things every session. See [Key Features](#key-features-what-makes-these-skills-different) for a full breakdown.

## Getting Started: Project Type Setup

**IMPORTANT:** Skills route differently based on project type. First-time commit in any repository will guide you through setup interactively, or you can set it up manually.

### Project Types

| Type | When to Use | Documentation | Commit Skill |
|------|-------------|---------------|--------------|
| **skills** | Claude Code skill repositories (has `*/SKILL.md` files) | README.md + CLAUDE.md (auto-synced) | `git-commit` |
| **java** | Java/Maven/Gradle projects | DESIGN.md (required) + CLAUDE.md (optional, auto-synced) | `java-git-commit` |
| **blog** | GitHub Pages / Jekyll blogs (date-prefixed posts) | CLAUDE.md optional (auto-synced) | `git-commit` |
| **custom** | Working groups, research, docs, advocacy | User-configured primary document (auto-synced) | `custom-git-commit` |
| **generic** | Everything else | CLAUDE.md optional (auto-synced) | `git-commit` |

📖 **[Complete Project Type Documentation: docs/PROJECT-TYPES.md](docs/PROJECT-TYPES.md)** — Detailed taxonomy, routing logic, decision matrix, and examples for all project types. See [docs/PROJECT-TYPES.md](docs/PROJECT-TYPES.md) for why explicit declaration is used over auto-detection.

### Quick Setup

**Option 1: Automatic (Recommended)**

Just try to commit. If `CLAUDE.md` is missing or has no project type, `git-commit` will prompt you to choose one and create it for you:

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

**For Blog Projects** (GitHub Pages / Jekyll):
```markdown
## Project Type

**Type:** blog
```

**For Generic Projects:**
```markdown
## Project Type

**Type:** generic
```

### What Happens at Commit Time

**type: skills** → `git-commit`:
- Validates SKILL.md files (follows skill-validation.md workflow)
- Auto-syncs README.md (skill catalog)
- Auto-syncs CLAUDE.md (workflow conventions)

**type: java** → `java-git-commit`:
- Requires docs/DESIGN.md (blocks if missing)
- Auto-syncs DESIGN.md (architecture)
- Auto-syncs CLAUDE.md (workflow conventions)
- Java-specific commit scopes (`rest`, `repository`, `service`, etc.)

**type: blog** → `git-commit`:
- Blog-aware commit scopes (`post`, `layout`, `config`, `asset`)
- Auto-syncs CLAUDE.md if it exists
- Post filename validation (`YYYY-MM-DD-title.md` format enforced)
- Commit type validation (`post`, `edit`, `draft`, `asset`, `config` only)
- 72-char subject limit (not 50 — blog titles are longer than code commit subjects)

**type: custom** → `custom-git-commit`:
- Syncs user-configured primary document (VISION.md, THESIS.md, etc.)
- Follows user's Sync Rules table
- Auto-syncs CLAUDE.md (workflow conventions)

**type: generic** → `git-commit`:
- Auto-syncs CLAUDE.md if it exists
- Basic conventional commits

## Why This Collection Exists

Three problems that compound silently:

**Commits without context:** "fix stuff" at 3pm is obvious. By Tuesday it's archaeology. Structured commit messages (`fix(auth): prevent token refresh race condition`) make git history searchable and release notes automatic.

**Design docs that drift:** Code evolves; DESIGN.md doesn't get updated. Three months later, the doc describes a system that no longer exists. Automated sync keeps docs honest.

**Repeated explanations:** Every new session, every new collaborator needs the same context. Skills encode that context once. The right workflow runs automatically.

## Skills Architecture

This collection follows a **layered architecture** where foundation skills provide universal principles, and specialized skills extend them for specific languages, frameworks, and workflows.

### Layer 1: Commit Workflow (4 skills)

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

### Layer 3: Review (2 skills)

**Pattern:** Domain-Specific Review Specialists

| Skill | Reviews | Auto-Invoked By | Blocks On |
|-------|---------|-----------------|-----------|
| **java-code-review** | Java code quality | java-git-commit | CRITICAL findings |
| **java-security-audit** | OWASP Top 10 | java-code-review | Security vulnerabilities |

**Note:** SKILL.md validation for type: skills repositories is handled by the skill-validation.md workflow (not a portable skill), automatically invoked by git-commit when SKILL.md files are staged.

### Layer 4: Principles (4 skills)

**Pattern:** Universal Foundations (Referenced, Not Invoked)

| Skill | Domain | Extended By |
|-------|--------|-------------|
| **code-review-principles** | Universal code review | java-code-review, ts-code-review, python-code-review |
| **security-audit-principles** | Universal OWASP Top 10 | java-security-audit, ts-security-audit, python-security-audit |
| **dependency-management-principles** | Universal BOM patterns | maven-dependency-update, npm-dependency-update, pip-dependency-update |
| **observability-principles** | Universal logging/tracing/metrics | quarkus-observability |

### Layer 5: Java/Quarkus Development (4 skills)

**Pattern:** Layered Specialization

| Skill | Purpose | Builds On |
|-------|---------|-----------|
| **java-dev** | Java development foundation | (base layer) |
| **quarkus-flow-dev** | Quarkus Flow workflows | java-dev |
| **quarkus-flow-testing** | Workflow testing | java-dev, quarkus-flow-dev |
| **quarkus-observability** | Quarkus observability config | observability-principles |

### Layer 6: Utilities (6 skills)

| Skill | Purpose | Builds On |
|-------|---------|-----------|
| **maven-dependency-update** | Maven BOM management | dependency-management-principles |
| **adr** | Architecture Decision Records | (standalone) |
| **design-snapshot** | Immutable dated design state record | (standalone) |
| **idea-log** | Living log for undecided possibilities | (standalone) |
| **write-blog** | Living project diary — decisions, pivots, and discoveries in the moment | (standalone) |
| **knowledge-garden** | Cross-project library of hard-won bugs, gotchas, and unexpected behaviours | (standalone, writes to ~/claude/knowledge-garden/) |

### Layer 7: Health & Quality (8 skills)

| Skill | Purpose | Builds On |
|-------|---------|-----------|
| **project-health** | Universal correctness and consistency checks | (standalone) |
| **project-refine** | Improvement opportunities and bloat reduction | (standalone) |
| **skills-project-health** | Skills repo health checks | project-health |
| **java-project-health** | Java project health checks | project-health |
| **blog-project-health** | Blog project health checks | project-health |
| **custom-project-health** | Custom project health checks | project-health |
| **ts-project-health** | TypeScript/Node.js health checks | project-health |
| **python-project-health** | Python health checks | project-health |

### Layer 8: TypeScript/Node.js Development (4 skills)

| Skill | Purpose | Builds On |
|-------|---------|-----------|
| **ts-dev** | TypeScript development guidance | (standalone) |
| **ts-code-review** | TypeScript code review | code-review-principles |
| **ts-security-audit** | TypeScript/Node.js OWASP security audit | security-audit-principles |
| **npm-dependency-update** | npm/yarn/pnpm dependency management | dependency-management-principles |

### Layer 9: Python Development (4 skills)

| Skill | Purpose | Builds On |
|-------|---------|-----------|
| **python-dev** | Python development guidance | (standalone) |
| **python-code-review** | Python code review | code-review-principles |
| **python-security-audit** | Python OWASP security audit | security-audit-principles |
| **pip-dependency-update** | pip/poetry/pipenv dependency management | dependency-management-principles |

---

## Skills

### Setup & Management

#### **cc-praxis-ui**
Visual skill manager — a local web app for browsing, installing, updating, and uninstalling skills:
- Browse all 40+ skills by bundle with descriptions and chaining relationships
- Live install state: see what's installed, what's outdated, and what's available
- Install or uninstall individual skills or whole bundles with accurate counts
- Auto Execute mode runs commands directly; Manual mode shows commands to copy-paste
- Context-aware: when served publicly (GitHub Pages) the Install tab is hidden

**Launch:** `/cc-praxis-ui` inside Claude Code, or `cc-praxis` in a terminal (added to PATH on plugin install).

**Server:** `python3 scripts/web_installer.py [--port PORT] [--no-browser]`

#### **install-skills**
One-time bootstrap wizard for new environments:
- Configures session-start hook (automatic CLAUDE.md detection on new repos)
- Interactive skill selection: all, Java/Quarkus bundle, foundation principles, or individual
- Automatic dependency resolution
- Verifies setup on completion

**Triggers:** `/install-skills` (run once per environment after adding marketplace).

#### **uninstall-skills**
Guided removal wizard:
- Choose what to remove: all, Java/Quarkus bundle, or individual skills
- Checks reverse dependencies before removing (warns if other skills depend on it)
- Optionally removes session-start hook
- Requires explicit confirmation before anything is deleted

**Triggers:** `/uninstall-skills`.

---

### Layer 1: Commit Workflow

#### **git-commit**
Generic conventional commit workflow for any repository:
- Generates conventional commit messages (Conventional Commits 1.0.0)
- **Routes to specialized skills** based on project type declared in CLAUDE.md
- **Interactive setup** if CLAUDE.md missing (prompts for project type, creates it)
- Proposes commit message for user review before committing

**Features:** Decision Flow flowchart · Common Pitfalls table · commit format and scope reference in separate reference files

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

#### **blog-git-commit**
Conventional commit workflow for GitHub Pages / Jekyll blogs:
- **Blog-specific content types** — `post` (new post), `edit` (update), `draft` (WIP), `asset` (images/CSS), `config` (site config)
- **Post filename validation** — enforces `YYYY-MM-DD-title.md` format before committing
- **72-char subject limit** — blog titles are longer than code commit subjects
- **Commit message validation** via `scripts/validation/validate_blog_commit.py`

**Triggers:** "commit" in repositories with `type: blog` declared in CLAUDE.md, or explicitly via `/blog-git-commit`.

#### **custom-git-commit**
Intelligent commit workflow for custom project types (working groups, research, documentation, advocacy):
- **User-configured primary document sync** — reads sync strategy from CLAUDE.md
- Flexible sync via Sync Rules table (file patterns → document sections)
- Supports bidirectional-consistency, research-progress, api-spec-sync, architectural-changes strategies

**Features:** Decision flowchart · Common Pitfalls table · examples for 4 project archetypes

**Triggers:** "commit" in repositories with `type: custom` declared in CLAUDE.md.

### Layer 2: Documentation Sync

#### **update-claude-md**
Maintains CLAUDE.md in sync with workflow and convention changes: build commands, testing patterns, naming conventions, repository-specific tools, and skill lists.

**Features:** Common Pitfalls table · starter templates for skills and code repositories

Invoked automatically by all commit skills (if CLAUDE.md exists), or independently. For architectural documentation see `java-update-design`.

**Triggers:** CLAUDE.md needs updating, or automatically via `git-commit`.

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
Generic table-driven primary document synchronization for custom projects. Syncs VISION.md, THESIS.md, or any user-configured primary document based on Sync Rules declared in CLAUDE.md.
- Supports 4 built-in sync strategies + custom strategies
- Proposal-only — returns changes to calling skill for user confirmation

**Features:** Common Pitfalls table · sync strategy and pattern matching reference in separate files

Invoked automatically by `custom-git-commit` when Sync Rules configured.

**Triggers:** Primary document needs sync, or automatically via `custom-git-commit`.

### Layer 3: Review

#### **SKILL.md Validation (Modular Workflow)**

**Note:** SKILL.md validation for type: skills repositories is handled by the **skill-validation.md workflow**, not a portable skill. This modular documentation file is automatically referenced by git-commit when SKILL.md files are staged.

**What it validates:**
- Frontmatter structure (name, description, CSO compliance)
- Flowchart syntax (Mermaid validation, PUSH tier)
- Naming conventions (generic `-principles`, language prefixes)
- Cross-reference integrity (bidirectional chaining)
- Documentation completeness (Success Criteria, Common Pitfalls, Prerequisites)

**Automated validators:** `scripts/validate_all.py` orchestrates 14 validators across 3 tiers (commit/push/ci). See CLAUDE.md § Quality Assurance Framework for complete validation architecture.

**Why modular, not a skill:** Skills-specific validation only applies to THIS repository (type: skills). Loading as a portable skill would waste ~800 lines of tokens in all other projects (java, custom, generic). See CLAUDE.md § Skills-Repository-Specific Documentation. <!-- nocheck:project-types -->

---

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
Expert Java development for Quarkus server-side applications:
- Safety-first (resource leaks, deadlocks, silent corruption)
- Concurrency patterns aligned with Quarkus/Vert.x event loop
- Testing with JUnit 5, AssertJ, and Quarkus test annotations

**Features:** Rule Priority flowchart · "These Thoughts Mean STOP" rationalization table · ❌/✅ code examples · Quick Reference table

**Triggers:** Writing Java classes, fixing bugs, refactoring, `.java`, `pom.xml`, or build files.

#### **quarkus-flow-dev**
Specialized development for quarkus-flow (CNCF Serverless Workflow):
- Workflow DSL patterns with FuncDSL
- Task composition (function/agent/http/emit/listen)
- Human-in-the-loop (HITL) patterns and LangChain4j AI service integration

**Features:** Prerequisites section (builds on java-dev) · Task DSL Quick Reference table · Common Pitfalls table · API reference in `funcDSL-reference.md`

**Triggers:** Flow subclasses, workflow YAML, "workflow", "agent", "agentic", or "LangChain4j".

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

#### **design-snapshot**
Creates immutable, dated records of design state:
- Captures where the project is, how it got here, and where it's going
- Prompts for missing ADRs after writing — surfaces decisions without ADR coverage
- Links to existing ADRs rather than duplicating them
- Snapshots never change after commit — create a new dated snapshot to supersede

**Features:**
- Supersession tracking (older snapshot gets "Superseded by" link)
- Draft + confirm workflow — user approval required before writing
- Stored in `docs/design-snapshots/YYYY-MM-DD-<topic>.md`

**Triggers:** "create a design snapshot", "snapshot where we are", "document our progress", "in case we need to go back", significant pivot points.

#### **idea-log**
Lightweight living log for undecided possibilities — a parking lot for "we should consider this someday" thoughts:
- Captures ideas before they evaporate, without committing to them
- Reviews active ideas with staleness detection (flags entries older than 90 days)
- Promotes ideas to ADR (architectural decision) or task when ready to act on
- Discards — never deletes — keeping a record of "what we considered and rejected"

**Features:**
- Duplicate detection before appending new ideas
- Priority tagging (high/medium/low) with guidance
- Status tracking (active/promoted/discarded)
- Invoked by code review skills when reviews surface patterns worth parking

**Triggers:** "log this idea", "park that thought", "add to idea log", "we should consider this someday", or when code review surfaces a possibility worth remembering.

#### **write-blog**
Living project diary — captures decisions, pivots, and discoveries written in the moment, not in hindsight:
- Preserves what was believed at the time — including aspirations that later changed and approaches that were rejected
- Captures pivot moments explicitly: what was considered, what was rejected, what constraint forced the change
- Diary voice (first person, present tense, honest about uncertainty) — not a polished article written after everything is done
- Four entry types: Day Zero (initial vision before any code), Phase Update (milestone), Pivot (direction change), Correction (earlier belief proved wrong — never edits the original)
- Each entry ends with a "Next:" teaser setting up the following entry

**Features:**
- Correction entries reference originals rather than revising them — the historical record is preserved
- Integrates with `adr` (significant decisions get formal records) and `design-snapshot` (milestones get state freezes)
- Stored in `docs/blog/YYYY-MM-DD-<topic>.md`

**Triggers:** "write a blog entry", "update the project blog", "log what we built today", "document this pivot", "add a diary entry", or at significant architectural decisions, pivots, or phase completions.

#### **knowledge-garden**
Cross-project library of hard-won technical gotchas — stored in `~/claude/knowledge-garden/` (a git repo shared across all projects on this machine):
- Captures bugs whose symptoms mislead about root cause, tools that contradict documentation, silent failures, and workarounds found after multiple failed approaches
- Dual-indexed by technology AND by symptom type — find entries by what you're working on OR by what you're experiencing
- Three operations: **CAPTURE** (add a new gotcha), **SEARCH** (retrieve relevant entries), **IMPORT** (batch import from project BUGS-AND-ODDITIES.md files)
- Proactive trigger fires without user asking, at end of debugging sessions where something genuinely non-obvious was discovered
- Strict quality filter: "would a skilled developer familiar with this technology still have spent significant time on this?"

**Features:**
- Never deletes entries — adds "Resolved in: vX.Y" notes for fixed bugs
- Commits every entry with `feat(<dir>): add '<title>'` to the knowledge-garden git repo
- GARDEN.md index covers both technology and symptom-type dimensions with tag index
- Distinct from `idea-log` (undecided possibilities), `adr` (formal decisions), `write-blog` (project narrative)

**Triggers:** "add this to the knowledge garden", "log this bug", "future Claude should know this", "this took way too long", or proactively at end of non-obvious debugging sessions.

#### **issue-workflow**
Full-lifecycle GitHub issue tracking across four phases:
- **Phase 0: Setup** — configures `## Work Tracking` in CLAUDE.md, creates standard GitHub labels (including `epic`), optionally reconstructs issues from git history
- **Phase 1: Pre-Implementation** — when a plan is ready, creates an epic with child issues (Context / What / Acceptance Criteria / Notes), establishes active epic and active issue for the session
- **Phase 2: Task Intake** — before writing any code, checks for an active issue; if none, drafts and proposes one with epic placement assessed; detects cross-cutting concerns
- **Phase 3: Pre-Commit** — fallback safety net; confirms issue linkage on staged changes; catches anything Phase 2 missed; guides commit splits

Ad-hoc issues discovered during implementation are always assessed for epic fit (active epic → other open epics → standalone) with Claude suggesting placement and the user confirming. Planned issues from Phase 1 go into the active epic automatically.

**Triggers:** `/issue-workflow`, or invoked automatically throughout the session when Work Tracking is enabled in CLAUDE.md.

#### **retro-issues**
One-off retrospective mapping of git history to GitHub epics and issues:
- Analyses git log, ADRs, blog entries, and design docs to detect phase boundaries (ADR dates, blog milestones, git tags, commit gaps >7 days)
- Groups functional commits into issues by directory; trivial commits (typos, formatting, merges) excluded with reasons listed separately
- Enforces 2-child minimum for epics — single-child candidates demoted to standalone
- Writes full proposed structure to `docs/retro-issues.md` for direct review and editing before any GitHub calls
- Creates all issues as closed, in order: epics → children (with epic refs) → standalones
- Optional: amends historical commit messages with `Refs #N` / `Closes #N` via branch-swap pattern — work on `retro-amended`, verify with `git diff`, swap labels, keep original as backup

**Triggers:** `/retro-issues` only. Never auto-triggered.

---

### Layer 8: TypeScript/Node.js Development

#### **ts-dev**
Expert TypeScript development for Node.js and browser applications:
- Strict mode enforcement (no `any`, prefer `unknown` + type guards)
- Async/await correctness (unhandled rejections, parallel vs sequential)
- Error handling with discriminated unions and Result types

**Features:** Quick Reference table · Rule Priority flowchart · Common Pitfalls table · ❌/✅ code examples

**Triggers:** Writing TypeScript, fixing bugs, refactoring, `.ts`/`.tsx` files, `tsconfig.json`, `package.json`.

#### **ts-code-review**
Pre-commit code review for TypeScript projects, extending code-review-principles:
- Type safety (no `any`, unsafe assertions, non-null assertions)
- Async correctness (unawaited promises, missing error handling)
- Test quality (mocks vs real, behavioral testing)

**Features:** Prerequisites section (extends code-review-principles) · Severity Decision Flow · Common Pitfalls table

**Triggers:** "review the code", "check these changes", `/ts-code-review`.

#### **ts-security-audit**
OWASP Top 10 security audit for TypeScript/Node.js applications:
- Injection (SQL, command, NoSQL, template)
- Broken auth (JWT, bcrypt, session management, rate limiting)
- Prototype pollution (Node.js-specific) · SSRF · Cryptographic failures

**Features:** Prerequisites section (extends security-audit-principles) · Node.js Security Features table · ❌/✅ code examples · Severity flowchart

**Triggers:** "security review", "audit security", "check for vulnerabilities", or offered by `ts-code-review`.

#### **npm-dependency-update**
npm/yarn/pnpm dependency management, extending dependency-management-principles:
- Version strategy (exact vs ranges, when to pin)
- `npm audit` triage and remediation
- Breaking change detection with ADR integration

**Features:** Prerequisites section (extends dependency-management-principles) · Semver guidance table · Version Strategy flowchart · Success Criteria

**Triggers:** "update dependencies", "npm audit", "upgrade package", `package.json` changes.

---

### Layer 7: Health & Quality

#### **project-health**
Universal project correctness and consistency checker:
- Answers: is the project correct, complete, and consistent?
- 12 universal check categories: docs-sync, consistency, logic, config, security, release, user-journey, git, primary-doc, artifacts, conventions, framework
- 4-tier depth: `--commit` (validators only) → `--standard` → `--prerelease` → `--deep` (+ refinement questions)
- Auto-chains to type-specific health skill at tier 3+

**Features:**
- Mechanical auto-fix offered for fixable findings (requires YES confirmation)
- `--save` flag writes a date-stamped report file
- Companion to project-refine

**Triggers:** "health check", "is the project healthy", "pre-release check", `/project-health`.

#### **project-refine**
Improvement-focused companion to project-health:
- Answers: could this be smaller, clearer, or better structured?
- Looks at bloat, duplication, consolidation, and structural opportunities
- Covers docs, code/tests, and universal domains
- Never blocks work — findings are always opportunities, never failures

**Features:**
- Same 4-tier depth system as project-health
- Separate from health checks — refine only after health is green
- Domain-scoped: can run just `docs` or `code` categories

**Triggers:** "find duplication", "bloat check", "look for ways to improve docs", "do a refine session", `/project-refine`.

#### **skills-project-health**
Type-specific health checks for skill collection repositories, extending project-health:
- Adds 8 skills-specific categories: cross-refs, coverage, quality, naming, infrastructure, dependencies, performance, effectiveness
- Validates SKILL.md craft (CSO compliance, flowcharts, Success Criteria)
- Checks marketplace.json integrity, slash command coverage, validator wiring
- Auto-chained by project-health when `type: skills` is detected

**Triggers:** `/skills-project-health`, or automatically chained by `project-health` at tier 3+.

#### **java-project-health**
Type-specific health checks for Java/Maven/Gradle projects, extending project-health:
- Adds Java-specific checks: architecture consistency, dependency health, test coverage, build integrity
- Validates DESIGN.md accuracy against codebase
- Checks BOM alignment and Quarkus-specific patterns

**Triggers:** `/java-project-health`, or automatically chained by `project-health` at tier 3+.

#### **blog-project-health**
Type-specific health checks for GitHub Pages / Jekyll blogs, extending project-health:
- Adds blog-specific checks: post format, front matter validity, Jekyll configuration
- Validates content freshness and navigation integrity

**Triggers:** `/blog-project-health`, or automatically chained by `project-health` at tier 3+.

#### **custom-project-health**
Type-specific health checks for type: custom projects, extending project-health:
- Adds custom checks: primary document sync, work tracking configuration, custom conventions
- Reads Sync Rules from CLAUDE.md to validate project-specific requirements

**Triggers:** `/custom-project-health`, or automatically chained by `project-health` at tier 3+.

#### **ts-project-health**
Type-specific health checks for TypeScript/Node.js projects, extending project-health:
- Adds 5 TypeScript-specific categories: ts-types, ts-async, ts-build, ts-dependencies, ts-testing
- Checks `strict: true` in tsconfig, floating promises, `npm audit` findings, lock file committed
- Verifies `tsc --noEmit` passes and ESLint is clean

**Triggers:** `/ts-project-health`, or automatically chained by `project-health` at tier 3+.

---

## How Skills Work Together

Skills are designed to chain together for complete workflows:

### Development → Review → Commit (TypeScript repositories)
```
ts-dev
  → ts-code-review (manual or before committing)
    → ts-security-audit (if auth/payment/PII code)
      → git-commit
        → update-claude-md (automatic)
```

### Dependency Update → Security Review (TypeScript)
```
npm-dependency-update
  → ts-code-review (when adding new packages)
    → git-commit
```

### Development → Review → Commit (Python repositories)
```
python-dev
  → python-code-review (manual or before committing)
    → python-security-audit (if auth/payment/PII code)
      → git-commit
        → update-claude-md (automatic)
```

### Dependency Update → Security Review (Python)
```
pip-dependency-update
  → python-code-review (when adding new packages)
    → git-commit
```

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
  → git-commit
    → Validates SKILL.md (follows skill-validation.md workflow if staged)
    → update-claude-md + readme-sync.md (automatic)
```

### Blog Post → Commit (Blog repositories)
```
Write or edit a post
  → git-commit (or /blog-git-commit)
    → blog-git-commit (validates filename, type, message format)
    → update-claude-md (if CLAUDE.md exists)
```

### Idea → Decision → Documentation
```
Code review or brainstorm surfaces a possibility
  → idea-log (park it before it's forgotten, no commitment required)
    → adr (promote when ready to decide — idea becomes a formal decision)
      → git-commit
        → update-claude-md (automatic)
```

### Design State → Snapshot → ADRs
```
Significant pivot or brainstorm completed
  → design-snapshot (freeze where the project is — immutable record)
    → adr (for any decisions in the snapshot without an ADR yet — offered, not automatic)
      → git-commit
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

### R&D Diary → Formal Records → State Freeze
```
write-blog (diary entry at a pivot or milestone)
  → adr (significant decisions get a formal record alongside the narrative)
  → design-snapshot (milestone entries freeze the full design state)
    → git-commit
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
- ✅ **Modular documentation support** - Split large docs into focused modules, sync all files together, validate cross-file integrity
- ✅ **Quarkus/Vert.x specialized** - Event loop awareness, BOM patterns, reactive patterns
- ✅ **RED-GREEN-REFACTOR validated** - Tested under pressure, prevents resource leaks

---

## Modular Documentation

**Split large documentation into focused modules while keeping everything automatically synchronized.**

### What Is Modular Documentation?

Instead of maintaining a single 2000-line document, split it into focused files:

**Before:**
```
docs/DESIGN.md (2000 lines)
  - Overview, Architecture, Components, API, Data Model, Deployment...
```

**After:**
```
docs/DESIGN.md (200 lines - navigation)
docs/design/architecture.md
docs/design/components.md
docs/design/api.md
docs/design/data-model.md
docs/design/deployment.md
```

**The sync workflows automatically discover all modules, update them together, and validate cross-file integrity.**

### Why Use Modular Documentation?

**Large single-file documents become unmaintainable:**
- Hard to navigate (find specific section in 2000 lines)
- Different concerns mixed together (architecture + API + deployment)
- Merge conflicts when multiple people edit
- Cognitive overload when updating one part

**Modular structure solves this:**
- Each file focused on one concern (easier to understand, edit, review)
- Parallel editing (no merge conflicts between architecture and API changes)
- Better navigation (jump directly to `api.md` instead of scrolling)
- **Automatic synchronization** - sync workflows keep all files in sync

### Hybrid Discovery Approach

**Automatic discovery (preferred):**

Sync workflows discover modules through multiple methods:

**1. Markdown links:**
```markdown
See [Architecture](docs/design/architecture.md) for component structure.
```

**2. Include directives:**
```markdown
<!-- include: components.md -->
```

**3. Section references:**
```markdown
§ API Details in docs/design/api.md
```

**4. Directory patterns:**
If your primary file is `DESIGN.md`, sync automatically checks `docs/design/*.md`

**Caching for performance:**
- First sync: Discovers structure, caches in `.doc-cache.json` (gitignored)
- Subsequent syncs: Uses cache (<10ms, no re-parsing)
- Automatic cache invalidation when you add/remove links

### How Link Detection Works

**When you create a link in your primary document, sync workflows automatically:**

1. **Parse the link:** Extract file path from `[text](path.md)` or `§ Section in path.md`
2. **Resolve path:** Make it absolute relative to primary document
3. **Verify existence:** Check if the file actually exists
4. **Add to group:** Include in the document group for synchronized updates
5. **Cache structure:** Save for fast subsequent syncs

**This happens automatically. You just add links, sync workflows handle the rest.**

### Navigating Modular Documents

**Primary file becomes navigation hub:**

```markdown
# Project Design

## Overview
High-level project summary...

## Architecture
See [Architecture](docs/design/architecture.md) for detailed component
structure, data flow, and design decisions.

## API
See [API Endpoints](docs/design/api.md) for REST endpoint documentation,
request/response schemas, and authentication.

## Data Model
See [Data Model](docs/design/data-model.md) for entity relationships,
database schema, and migration strategy.
```

**Module files contain focused content:**

```markdown
# Architecture

## Component Overview
[Detailed architecture content here...]

## Data Flow
[Sequence diagrams, data flow descriptions...]

## Design Decisions
[Rationale for architectural choices...]
```

**Cross-references between modules:**

```markdown
# API Endpoints

## Authentication
See [Security Model](security.md) for authentication flows.

## User API
Interacts with [User Service](../design/components.md#user-service).
```

### When to Modularize

**Use modular when:**
- Document exceeds ~500 lines
- Multiple distinct topics (architecture, API, data model, deployment)
- Multiple contributors editing different sections
- Frequent updates to specific sections

**Keep single-file when:**
- Document under ~300 lines
- Single cohesive topic
- Infrequent updates
- Solo maintainer

### Automatic Synchronization

**When you commit changes, sync workflows:**

1. **Discover modules** from your primary document (via links/includes/refs)
2. **Analyze code changes** and map to sections across all files
3. **Propose updates** grouped by file:
   ```
   ## Proposed DESIGN.md updates
   [changes to primary]

   ## Proposed docs/design/api.md updates
   [changes to API module]
   ```
4. **Wait for your YES** before applying anything
5. **Update all files together** (atomic operation)
6. **Validate entire group** (link integrity, completeness, no corruption)
7. **Revert ALL files** if validation fails (not just primary)

**You see all proposed changes before they're applied. You approve once, all files update together.**

### Universal Application

**Works across all project types:**

| Project Type | Documents | Example Modules |
|--------------|-----------|-----------------|
| **Java projects** | DESIGN.md, CLAUDE.md | `docs/design/architecture.md`, `docs/workflows/build.md` |
| **Skills repositories** | README.md, CLAUDE.md | `docs/readme/skills.md`, `docs/workflows/ci.md` |
| **Research projects** | THESIS.md | `docs/thesis/methodology.md`, `docs/thesis/results.md` |
| **Working groups** | VISION.md | `docs/vision/projects.md`, `docs/vision/roadmap.md` |
| **API documentation** | API.md | `docs/api/endpoints.md`, `docs/api/schemas.md` |

Same discovery mechanism, same validation, same sync behavior - universal.

### Backwards Compatible

**No migration required.** Single-file documents work unchanged:

- Sync workflows discover zero modules → work as before
- No performance penalty (empty modules list is fast)
- Opt-in by adding links when you're ready

**Gradual migration:**

```
Week 1: Extract API section → docs/design/api.md, add link
Week 2: Extract data model → docs/design/data-model.md, add link
Week 3: Extract architecture → docs/design/architecture.md, add link
```

Each step is independently useful. No "all or nothing" migration.

### Example: Modularizing DESIGN.md

**Step 1: Create module file**
```bash
mkdir -p docs/design
# Move API section content to docs/design/api.md
```

**Step 2: Add link in DESIGN.md**
```markdown
## API
See [API Endpoints](docs/design/api.md) for REST endpoint documentation.
```

**Step 3: Commit**
```bash
git add DESIGN.md docs/design/api.md
git commit -m "docs(design): modularize API section"
```

**That's it.** Next time sync runs:
- Discovers `docs/design/api.md` via link
- Caches structure
- Updates both files when API-related code changes
- Validates links between them

### Quality Assurance

**Automatic validation prevents corruption:**

- ✅ **Link integrity:** Broken links block commit
- ✅ **Completeness:** Warns about orphaned modules
- ✅ **No duplication:** Detects duplicate content across files
- ✅ **Document structure:** Validates each file individually

**See QUALITY.md for complete validation framework.**

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
  → Validates SKILL.md (follows skill-validation.md workflow)
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

**Invocation types:** `auto` = always happens without user input · `conditional` = happens when a condition is met · `manual` = user explicitly requests it

| From Skill | To Skill | Type | Condition / When |
|------------|----------|------|-----------------|
| `git-commit` | skill-validation.md workflow | conditional | SKILL.md files staged (type: skills) |
| `git-commit` | readme-sync.md workflow | conditional | README.md exists + skill changes (type: skills) |
| `git-commit` | `update-claude-md` | conditional | CLAUDE.md exists |
| `git-commit` | `java-git-commit` | auto | type: java declared in CLAUDE.md |
| `git-commit` | `blog-git-commit` | auto | type: blog declared in CLAUDE.md |
| `git-commit` | `custom-git-commit` | auto | type: custom declared in CLAUDE.md |
| `git-commit` | `issue-workflow` | conditional | New CLAUDE.md created (setup offer) |
| `git-commit` | `issue-workflow` | conditional | Work Tracking enabled (pre-commit analysis) |
| `blog-git-commit` | `update-claude-md` | conditional | CLAUDE.md exists |
| `issue-workflow` | (terminal) | — | No outgoing chains |
| `java-git-commit` | `java-update-design` | auto | Always |
| `java-git-commit` | `update-claude-md` | conditional | CLAUDE.md exists |
| `custom-git-commit` | `update-primary-doc` | conditional | Sync Rules configured in CLAUDE.md |
| `custom-git-commit` | `update-claude-md` | conditional | CLAUDE.md exists |
| `java-code-review` | `java-security-audit` | conditional | Security-critical code detected |
| `java-code-review` | `java-git-commit` | manual | User wants to commit after review |
| `java-dev` | `java-code-review` | manual | User triggers review |
| `quarkus-flow-dev` | `quarkus-flow-testing` | manual | User is writing tests for workflows |
| `quarkus-flow-dev` | `quarkus-observability` | manual | Workflow tracing/MDC setup needed |
| `quarkus-flow-dev` | `java-code-review` | manual | User triggers review |
| `quarkus-flow-dev` | `java-git-commit` | manual | User is ready to commit |
| `quarkus-flow-testing` | `java-code-review` | manual | User triggers review |
| `quarkus-flow-testing` | `java-git-commit` | manual | User is ready to commit |
| `maven-dependency-update` | `adr` | manual | Major version jump or new extension |
| `maven-dependency-update` | `java-git-commit` | manual | After successful dependency updates |
| `quarkus-observability` | `maven-dependency-update` | manual | Adding OTEL/Micrometer deps |
| `quarkus-observability` | `java-git-commit` | manual | Observability config changes |
| `adr` | `java-git-commit` | manual | Stage ADR with related changes |
| `java-update-design` | `update-claude-md` | manual | Architecture changes often need workflow doc updates too |
| `readme-sync.md` | `update-claude-md` | manual | Skill changes often need workflow doc updates too |
| `ts-dev` | `ts-code-review` | manual | User triggers review |
| `ts-code-review` | `ts-security-audit` | conditional | Security-critical code detected (auth/payment/PII) |
| `ts-code-review` | `git-commit` | manual | User wants to commit after review |
| `ts-security-audit` | `git-commit` | manual | After security review complete |
| `npm-dependency-update` | `adr` | manual | Major version jump or significant new package |
| `npm-dependency-update` | `git-commit` | manual | After successful dependency updates |
| `python-dev` | `python-code-review` | manual | User triggers review |
| `python-code-review` | `python-security-audit` | conditional | Security-critical code detected (auth/payment/PII) |
| `python-code-review` | `git-commit` | manual | User wants to commit after review |
| `python-security-audit` | `git-commit` | manual | After security review complete |
| `pip-dependency-update` | `adr` | manual | Major version jump or significant new package |
| `pip-dependency-update` | `git-commit` | manual | After successful dependency updates |

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

## Contributing & Local Development

### Releasing Skills

Skills use trunk-based development with git tags. See [RELEASE.md](RELEASE.md) for the full release workflow, versioning conventions, and how marketplace.json versioning relates to per-skill plugin.json versions.

---

### Session-Start Hook

`hooks/check_project_setup.sh` runs at every Claude Code session start. It checks whether the current directory has a `CLAUDE.md` with a project type declared, and if not, outputs an `⚠️ ACTION REQUIRED` directive prompting Claude to ask you to set one up.

`scripts/claude-skill sync-local` automatically keeps your local copy of this hook in sync with the repo version and ensures it's registered in `~/.claude/settings.json`.

---

### Skill Authoring Environment

When you clone this repository, `CLAUDE.md` is loaded automatically by Claude Code, giving you expert in-context guidance on:
- Skill architecture and frontmatter requirements
- Claude Search Optimization (CSO) — how descriptions determine when skills trigger
- Naming conventions (`java-*`, `*-principles`, framework prefixes)
- Skill chaining patterns and bidirectional cross-references
- Quality assurance workflows and pre-commit checklists
- Document sync and validation

This makes the cloned repository a **complete skill development environment**. See [CLAUDE.md § Skill Architecture](CLAUDE.md#skill-architecture) for the full authoring guide and [QUALITY.md](QUALITY.md) for the validation framework.

---

### Local Development Workflow

The recommended workflow copies your local edits directly into Claude Code's plugin cache, so changes are live in the next session you open.

**One-time setup:**
```bash
git clone https://github.com/mdproctor/cc-praxis.git ~/cc-praxis
cd ~/cc-praxis

# Install all skills from local source into Claude Code's cache
scripts/claude-skill sync-local --all -y
```

**After editing a skill:**
```bash
vim java-dev/SKILL.md

# Push the change into Claude Code's cache
scripts/claude-skill sync-local -y
```

**After a `git pull`:**
```bash
git pull
scripts/claude-skill sync-local -y   # update cache with latest
```

### `sync-local` Reference

```bash
# Update already-installed skills from local source
scripts/claude-skill sync-local

# Also install skills not yet in the cache (default: update only)
scripts/claude-skill sync-local --all

# Skip confirmation prompt
scripts/claude-skill sync-local --all -y
```

`sync-local` writes to Claude Code's plugin cache (`~/.claude/skills/`) and updates the registry files. It never modifies the source files or git history.

---

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run just the installer tests
python3 -m pytest tests/test_claude_skill.py -v
```

Tests use temporary directories throughout and never touch your real install location.

---

### Running Validators

```bash
# Full validation suite (commit tier — fast, <2s)
python3 scripts/validate_all.py

# Specific validators
python3 scripts/validation/validate_frontmatter.py   # YAML structure
python3 scripts/validation/validate_cso.py           # Skill descriptions
python3 scripts/validation/validate_project_types.py # Project type list consistency

# Validate a specific document
python3 scripts/validate_document.py README.md
```

See [QUALITY.md § Validation Script Roadmap](QUALITY.md#validation-script-roadmap) for the full list of validators and their tier assignments.

---

### Adapting Skills for Your Own Use

These skills encode conventions from specific projects. When customising:

1. Review safety and concurrency rules in `java-dev` — inspired by Sanne Grinovero's Java guidelines
2. Adjust conventional commit types in `java-git-commit`
3. Customise BOM versions in `maven-dependency-update`
4. Update observability endpoints in `quarkus-observability`
5. Extend the generic principles skills for other languages/frameworks (e.g., `go-code-review`, `gradle-dependency-update`) — see [CLAUDE.md § Extending to New Languages](CLAUDE.md#extending-to-new-languages-pattern-examples)

## Quality & Validation Framework

📖 **[Full Documentation: QUALITY.md](QUALITY.md)** — Comprehensive guide to validation tiers, division of labor between scripts and Claude, and implementation details.

**Every project using these skills gets comprehensive quality protection.** This multi-layered framework ensures reliability, consistency, and correctness across all project types — not just for the skills repository itself, but for **your Java projects, blogs, custom documentation, and generic repositories**.

### Quick Reference: Running Validation

**Validate specific documents:**
```bash
python scripts/validate_document.py README.md
python scripts/validate_document.py docs/DESIGN.md
python scripts/validate_document.py docs/vision.md
```

**For skills repository:**
```bash
python scripts/validate_all.py                    # All skills
python scripts/validation/validate_cso.py         # CSO compliance
python scripts/validation/validate_flowcharts.py  # Mermaid syntax (PUSH tier)
```

**Automatic validation:** Pre-commit gates block CRITICAL issues. Post-sync validation auto-reverts corruption. See [QUALITY.md § When Validation Runs](QUALITY.md#when-validation-runs).

### Quality Protection by Project Type

| Project Type | Universal Protection | Type-Specific Protection |
|--------------|---------------------|-------------------------|
| **java** | Document corruption, CLAUDE.md sync | Code review, security audit, DESIGN.md sync, BOM alignment |
| **blog** | Document corruption, CLAUDE.md sync | Blog-aware commit scopes (post/layout/config/asset) |
| **custom** | Document corruption, CLAUDE.md sync | Primary doc sync, user-configured validation, sync rules |
| **skills** | Document corruption, CLAUDE.md sync | SKILL.md validation, CSO compliance, README sync |
| **generic** | Document corruption, CLAUDE.md sync | (universal only) |

See [QUALITY.md § Quality Protection by Project Type](QUALITY.md#quality-protection-by-project-type) for detailed before/after comparisons.

### Validation Tiers

| Level | When | Time Budget | Key Checks |
|-------|------|-------------|-----------|
| **Quick** | File save | <100ms | Syntax, heading hierarchy |
| **Commit** | Pre-commit | <2s | Structure, corruption (blocks CRITICAL) |
| **Review** | User-invoked | User-driven | Scripts + Claude deep analysis |
| **Push** | Pre-push | <30s | Cross-document consistency |
| **Full** | CI/Scheduled | <5min | Everything + external URLs |

See [QUALITY.md § Tiered Validation](QUALITY.md#tiered-validation) for complete details.

### Why This Framework Matters

Quality issues in AI-guided development compound exponentially. This framework prevents:
- **Code issues:** Resource leaks, concurrency bugs, security vulnerabilities
- **Documentation drift:** DESIGN.md, VISION.md, THESIS.md become lies
- **Corruption:** Duplicate headers, broken tables slip into git history
- **Expensive wallpaper:** Skills with bad descriptions get ignored by Claude

**Result:** Production-grade quality by default. The java-dev skill was pressure-tested and successfully prevented resource leaks that baseline Claude introduced. This framework ensures that reliability across all project types.

See [QUALITY.md § Why Quality Matters](QUALITY.md#why-quality-matters) for complete before/after comparisons and real incident examples.

## Repository Structure

```
.
├── LICENSE                              # Apache License 2.0
├── README.md                            # This file
├── CLAUDE.md                            # Claude Code guidance + skill authoring environment
├── QUALITY.md                           # Validation framework documentation
├── PHILOSOPHY.md                        # Design principles
├── RELEASE.md                           # Release workflow (trunk-based, git tags)
├── hooks/
│   └── check_project_setup.sh          # Session-start hook (synced by scripts/claude-skill)
├── bin/
│   └── cc-praxis                        # Shell launcher (added to PATH on plugin install)
├── .claude-plugin/
│   └── marketplace.json                 # Marketplace catalog (all 41 skills)
├── scripts/                             # Automation and validation
│   ├── claude-skill                     # Skill installer/manager CLI (install, sync-local, etc.)
│   ├── web_installer.py                 # Web skill manager server (serves docs/index.html)
│   ├── generate_web_app_data.py         # Regenerates CHAIN JS + bundle meta in docs/index.html
│   ├── validate_all.py                  # Master orchestrator (3-tier validation)
│   ├── validate_document.py             # Universal .md corruption detector
│   ├── generate_skill_metadata.py       # Regenerates skill.json for all skills
│   └── validation/                      # SKILL.md validators (17 total, 3 tiers)
│       ├── validate_frontmatter.py     # YAML structure, required fields [COMMIT]
│       ├── validate_cso.py             # Description CSO compliance [COMMIT]
│       ├── validate_references.py      # Cross-reference integrity [COMMIT]
│       ├── validate_naming.py          # Naming conventions [COMMIT]
│       ├── validate_sections.py        # Required sections by type [COMMIT]
│       ├── validate_structure.py       # File organization [COMMIT]
│       ├── validate_project_types.py   # Project type list consistency [COMMIT]
│       ├── validate_flowcharts.py      # Mermaid syntax validation [PUSH]
│       ├── validate_web_app.py         # Web app sync with SKILL.md data [PUSH]
│       ├── validate_cross_document.py  # Cross-document consistency [PUSH]
│       ├── validate_temporal.py        # Stale references [PUSH]
│       ├── validate_usability.py       # Readability, UX [PUSH]
│       ├── validate_edge_cases.py      # Edge case coverage [PUSH]
│       ├── validate_behavior.py        # Behavioral consistency [PUSH]
│       ├── validate_readme_sync.py     # README/CLAUDE sync [PUSH]
│       └── validate_python_quality.py  # mypy, flake8, bandit [CI]
├── tests/                               # Test suite (295 tests)
│   ├── test_claude_skill.py            # Tests for scripts/claude-skill
│   ├── test_mockup_chaining.py         # Skill chaining ground truth (CHAINING_TRUTH)
│   ├── test_chain_data_drift.py        # CHAIN JS in index.html vs CHAINING_TRUTH
│   ├── test_web_installer_server.py    # Web installer API unit tests (55 tests)
│   ├── test_web_installer_integration.py # Real install/uninstall permutation tests (40 tests)
│   ├── test_web_installer_ui.py        # Playwright browser UI tests (38 tests)
│   ├── test_document_discovery.py      # Tests for document discovery
│   ├── test_document_cache.py          # Tests for document caching
│   └── test_modular_validator.py       # Tests for modular validator
├── docs/                                # Web skill manager + documentation
│   ├── index.html                       # Web skill manager UI (About/Browse/Install tabs)
│   ├── ideas/
│   │   └── IDEAS.md                     # Project idea log (undecided possibilities)
│   ├── PROJECT-TYPES.md                # Complete project type taxonomy and routing
│   └── adr/                            # Architecture Decision Records
├── skill-validation.md                  # Skills-specific SKILL.md validation workflow
├── readme-sync.md                       # Skills-specific README.md sync workflow
├── install-skills/                      # Marketplace bootstrap wizard
│   └── SKILL.md
├── uninstall-skills/                    # Guided uninstall wizard
│   └── SKILL.md
├── git-commit/                          # Generic conventional commits + project type routing
│   └── SKILL.md
├── java-git-commit/                     # Java-specific smart commits with DESIGN.md sync
│   └── SKILL.md
├── custom-git-commit/                   # User-configured commits with primary doc sync
│   └── SKILL.md
├── update-claude-md/                    # CLAUDE.md workflow documentation sync
│   └── SKILL.md
├── java-update-design/                  # DESIGN.md architecture sync (Java projects)
│   └── SKILL.md
├── update-primary-doc/                  # Generic primary document sync (custom projects)
│   └── SKILL.md
├── code-review-principles/              # Universal code review principles
│   └── SKILL.md
├── security-audit-principles/           # Universal OWASP Top 10 principles
│   └── SKILL.md
├── dependency-management-principles/    # Universal BOM/dependency principles
│   └── SKILL.md
├── observability-principles/            # Universal logging/tracing/metrics principles
│   └── SKILL.md
├── java-dev/                            # Core Java/Quarkus development rules
│   └── SKILL.md
├── java-code-review/                    # Java-specific code review
│   └── SKILL.md
├── java-security-audit/                 # Java/Quarkus OWASP security audit
│   └── SKILL.md
├── maven-dependency-update/             # Maven BOM dependency management
│   └── SKILL.md
├── quarkus-flow-dev/                    # Quarkus Serverless Workflow patterns
│   ├── SKILL.md
│   └── funcDSL-reference.md            # Complete FuncDSL API reference
├── quarkus-flow-testing/                # Quarkus workflow testing patterns
│   └── SKILL.md
├── quarkus-observability/               # Quarkus observability configuration
│   └── SKILL.md
└── adr/                                 # Architecture Decision Records skill
    └── SKILL.md
```
