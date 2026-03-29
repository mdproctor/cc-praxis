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
- `update-design` keeps DESIGN.md in sync with code *before* you commit, not as a quarterly exercise
- Both work together so documentation is *part of* the commit, not a separate chore you skip

**Result:** Six months from now, you'll thank yourself. Your teammates will thank you. The new hire will thank you. And that 2 AM production incident? The git history will actually help instead of making you want to rage-quit.

You're not writing documentation. You're leaving breadcrumbs for Future You, who has the memory of a goldfish and the patience of a caffeinated squirrel.

## Skills

### Generic Foundation Skills

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

### Core Development

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

### Development Tools

#### **skill-creator**
Comprehensive skill authoring and optimization tool for creating, testing, and improving Claude Code skills:
- Skill drafting and iterative improvement
- Test prompt generation and execution
- Qualitative and quantitative evaluation (via eval scripts)
- Skill description optimization for better triggering accuracy
- Variance analysis and performance benchmarking

**Features:**
- Complete eval framework (scripts in `eval-viewer/`, `scripts/`)
- Automated test running with background execution
- Interactive review workflow with quantitative metrics
- Description optimizer for Claude Search Optimization (CSO)

**Triggers:** "create a skill", "edit this skill", "optimize skill", "test this skill", "run evals", skill performance measurement.

### Quality Assurance

#### **skill-review**
Pre-commit review for Claude Code skills ensuring structural integrity, CSO compliance,
and documentation completeness:
- Frontmatter validation (name, description, CSO rules)
- Flowchart syntax testing (Graphviz validation)
- Naming convention compliance (generic `-principles`, language prefixes)
- Cross-reference verification (bidirectional chaining)
- Documentation completeness (Success Criteria, Common Pitfalls, Prerequisites)
- Severity assignment (CRITICAL/WARNING/NOTE)

Builds quality assurance discipline specifically for skills repositories. Blocks commits
on CRITICAL findings (invalid frontmatter, broken flowcharts, CSO violations).

**Features:**
- Review checklist by category (frontmatter, naming, cross-references, flowcharts)
- Severity decision flowchart
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

### Version Control & Documentation

#### **git-commit**
Generic conventional commit workflow for any repository:
- Generates conventional commit messages (Conventional Commits 1.0.0)
- Works with any codebase or file types
- Proposes commit message for user review before committing
- Base workflow extended by java-git-commit

**Features:**
- Decision Flow flowchart (stage → generate → propose → commit)
- Conventional commit type and scope reference
- Common Pitfalls table
- Language-agnostic examples

**Triggers:** "commit", "make a commit", `/git-commit` in non-Java repositories.

#### **java-git-commit**
Intelligent commit workflow that extends git-commit with:
- Java/Quarkus-specific scope suggestions (controller, service, repository, BOM)
- Automatic DESIGN.md synchronization via `update-design` skill
- Maven/Gradle awareness
- Proposes everything for review before committing

**Features:**
- Decision flowchart showing complete commit + design sync process
- Common Pitfalls table (11 commit mistakes including Java-specific)
- Java-specific scope and type examples
- Simplified workflow (references git-commit, adds DESIGN.md sync)

**Triggers:** "commit", "smart commit", "update design and commit", `/java-git-commit` in Java/Maven/Gradle repositories.

#### **update-design**
Maintains DESIGN.md documentation in sync with code changes, capturing:
- Component structure and responsibilities
- Architectural patterns
- Integration points
- Technical decisions

**Features:**
- Common Pitfalls table (9 documentation mistakes)
- Java-specific signal detection (annotations → architectural meaning)
- Surgical update strategy (preserves user's voice)

Invoked automatically by `java-git-commit` or independently. Handles architectural documentation; for workflow/convention documentation, see `update-claude-md`.

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
- Surgical update strategy (preserves user's voice)

Invoked automatically by `git-commit` and `java-git-commit` (if CLAUDE.md exists), or independently. Handles workflow documentation; for architectural documentation, see `update-design`.

#### **update-readme**
Maintains README.md documentation in sync with skill collection changes in skills repositories:
- Skill descriptions (Skills section)
- Chaining relationships (Skill Chaining Reference table)
- Feature additions (Key Features section)
- Repository structure changes

**Features:**
- Common Pitfalls table (8 documentation mistakes)
- Skills repository awareness (skill naming, chaining patterns)
- Surgical update strategy (preserves user's voice)

Invoked automatically by `git-commit` (if README.md exists and skill changes detected), or independently. Specific to skills repositories; for code repositories, use project-specific documentation tools.

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

### Project Management

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

## How Skills Work Together

Skills are designed to chain together for complete workflows:

### Development → Review → Commit (Java repositories)
```
java-dev or quarkus-flow-dev
  → quarkus-flow-testing (if writing tests)
  → java-code-review (automatic or manual)
    → java-git-commit
      → update-design + update-claude-md (automatic)
```

### Skill Development → Review → Commit (Skills repositories)
```
skill-creator or superpowers:writing-skills
  → skill-review (automatic when SKILL.md staged)
  → git-commit
    → update-claude-md + update-readme (automatic)
```

### Architecture Decision → Documentation
```
Major decision made
  → adr (capture decision)
    → update-design (sync with DESIGN.md)
      → java-git-commit
```

### Dependency Management → Commit
```
maven-dependency-update
  → java-code-review (if code changes)
    → java-git-commit
      → Optional: adr (for major upgrades)
```

### Observability Setup
```
quarkus-observability
  → maven-dependency-update (for new deps)
    → Optional: adr (document strategy)
      → java-git-commit
```

## Key Features

### Safety First
- Resource leak detection with rationalization prevention
- Deadlock prevention with lock ordering rules
- Thread safety validation for Vert.x event loop
- Silent corruption prevention
- **Validated:** RED-GREEN-REFACTOR tested under pressure scenarios

### Cloud-Native Optimization
- Quarkus/Vert.x event loop awareness
- Performance patterns for cloud deployment
- Minimal allocation strategies
- Reactive programming support

### Professional Workflows
- Conventional commit standards with automatic DESIGN.md sync
- Architecture decision records in MADR format
- Living design documentation
- BOM-aligned dependency management

### Test-Driven Quality
- JUnit 5 + AssertJ
- `@QuarkusTest`, `@QuarkusComponentTest`, `@QuarkusIntegrationTest`
- Real CDI wiring over mocking
- MockServer for HTTP integration tests
- AI service mocking patterns for quarkus-flow

### Quality Assurance
- **Quick Reference tables** in every major skill
- **Common Pitfalls** documented with fixes
- **Real-World Impact** sections with production incident examples
- **Decision flowcharts** for complex workflows
- **Red Flags** section (java-dev) to catch rationalizations early

## Usage

These skills are invoked automatically by Claude Code based on context, or explicitly via skill names:

```
/java-git-commit
/java-code-review
/java-security-audit
/maven-dependency-update
/quarkus-observability
/update-design
/adr
```

Skills trigger automatically when relevant keywords appear in conversation or when working with specific file types.

**Generic foundation skills** are not invoked directly - they are referenced as prerequisites by language-specific skills.

## Requirements

- Claude Code CLI, desktop, web, or IDE extension
- Java 17+
- Maven-based Quarkus projects
- Git repository

## Skill Chaining Reference

Each skill explicitly declares when to chain to other skills:

| From Skill | Chains To | When |
|---|---|---|
| `java-dev` | `java-git-commit` | After implementation/refactoring |
| `quarkus-flow-dev` | `quarkus-flow-testing` | When writing tests |
| `quarkus-flow-dev` | `java-code-review` → `java-git-commit` | After workflow implementation |
| `quarkus-flow-testing` | `java-code-review` → `java-git-commit` | After writing tests |
| `code-review-principles` | (referenced by language-specific reviews) | Foundation for all code reviews |
| `java-code-review` | Blocks `java-git-commit` | If CRITICAL findings exist |
| `java-code-review` | `java-security-audit` | Security-critical code detected |
| `security-audit-principles` | (referenced by language-specific audits) | Foundation for all security audits |
| `java-security-audit` | Blocks `java-git-commit` | If CRITICAL vulnerabilities exist |
| `dependency-management-principles` | (referenced by package managers) | Foundation for all dependency updates |
| `maven-dependency-update` | `adr` | Major version upgrades |
| `maven-dependency-update` | `java-git-commit` | After successful update |
| `observability-principles` | (referenced by framework implementations) | Foundation for all observability |
| `quarkus-observability` | `maven-dependency-update` | Adding OTel/Micrometer deps |
| `quarkus-observability` | `adr` | First-time observability setup |
| `skill-creator` | `skill-review` | When skill authoring complete |
| `superpowers:writing-skills` | `skill-review` | When skill authoring complete |
| `skill-review` | Blocks `git-commit` | If CRITICAL findings exist (skills repos) |
| `git-commit` | `skill-review` | Always (automatic if SKILL.md files staged) |
| `git-commit` | `update-claude-md` | Always (automatic if CLAUDE.md exists) |
| `git-commit` | `update-readme` | Always (automatic if README.md exists and skill changes) |
| `java-git-commit` | `update-design` | Always (automatic if docs/DESIGN.md exists) |
| `java-git-commit` | `update-claude-md` | Always (automatic if CLAUDE.md exists) |
| `update-design` | (companion: `update-claude-md`) | Architecture changes often need workflow doc updates |
| `update-readme` | (companion: `update-claude-md`) | Skill changes often need workflow doc updates |
| `adr` | `update-design` | New components documented |
| `adr` | `java-git-commit` | Stage with related changes |

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

## Repository Structure

```
.
├── LICENSE                              # Apache License 2.0
├── README.md                            # This file
├── CLAUDE.md                            # Guidance for Claude Code
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
├── skill-creator/                       # Skill authoring and optimization
│   ├── SKILL.md
│   ├── agents/                          # Test agents
│   ├── assets/                          # Skill creation assets
│   ├── eval-viewer/                     # Quantitative eval tools
│   ├── references/                      # Skill authoring references
│   └── scripts/                         # Eval automation scripts
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
├── update-design/                       # DESIGN.md maintenance
│   └── SKILL.md
├── update-claude-md/                    # CLAUDE.md maintenance
│   └── SKILL.md
├── update-readme/                       # README.md maintenance
│   └── SKILL.md
├── adr/                                 # Architecture Decision Records
│   └── SKILL.md
├── maven-dependency-update/             # Maven dependency management
│   └── SKILL.md
└── quarkus-observability/               # Quarkus observability setup
    └── SKILL.md
```
