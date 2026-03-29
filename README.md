# Claude Code Skills for Java & Quarkus Development

A curated collection of specialized skills for Claude Code that streamline Java development, focusing on Quarkus applications, quarkus-flow workflows, and professional software engineering practices.

## Overview

These skills transform Claude Code into an expert Java/Quarkus development assistant that understands enterprise-grade code quality, safety requirements, and modern cloud-native patterns. Each skill encodes best practices, common pitfalls, and project-specific conventions to ensure consistent, production-ready code.

**Key Features:**
- ✅ **❌/✅ Code examples** showing wrong and right approaches
- ✅ **Quick Reference tables** for instant lookup
- ✅ **Red Flags sections** to prevent rationalizations
- ✅ **Common Mistakes tables** documenting pitfalls
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
- Enhanced Skill Chaining (includes logging-observability)
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
- Common Testing Pitfalls table (7 mistakes)
- Two mocking strategies with complete examples

**Triggers:** "test workflow", "mock agent", `@QuarkusTest` for Flow classes, debugging workflow test failures.

### Quality Assurance

#### **code-review**
Pre-commit code review enforcing:
- Critical safety checks (resource leaks, classloader issues, deadlock risks)
- Concurrency correctness
- Performance best practices
- Testing coverage validation
- Code clarity standards

Assigns severity levels (CRITICAL/WARNING/NOTE) and blocks commits on critical findings.

**Features:**
- "Why Code Review Matters" section with real incident examples
- Severity assignment flowchart (CRITICAL/WARNING/NOTE decision tree)
- Comprehensive checklist organized by category
- ❌/✅ code examples for Safety, Concurrency, Performance, Testing sections

**Triggers:** "review my code", "check my changes", `/code-review`, or automatically via `java-git-commit`.

#### **security-audit**
Security vulnerability review for Quarkus applications:
- OWASP Top 10 checks adapted for Quarkus server-side apps
- Injection prevention (SQL, Log, Command)
- Broken authentication and access control detection
- Cryptographic failures and security misconfiguration
- SSRF and unvalidated redirect checks
- Quarkus security feature recommendations

**Features:**
- "Why Security Audits Matter" with real breach examples
- Severity assignment flowchart (CRITICAL/WARNING/NOTE for security)
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

Invoked automatically by `java-git-commit` or independently.

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

#### **dependency-update**
Maven dependency management with BOM-first approach:
- Quarkus platform alignment verification
- BOM-managed vs explicit version detection
- Compatibility checking before version bumps
- Safe upgrade proposals with risk assessment

**Features:**
- Common Pitfalls table (7 BOM/version mistakes)
- BOM alignment rules with clear decision criteria
- Version compatibility checking workflow

**Triggers:** "update dependencies", "bump version", "upgrade Quarkus", "add dependency", `pom.xml` changes.

#### **logging-observability**
Configures production-grade observability for Quarkus/quarkus-flow:
- Structured JSON logging with MDC
- quarkus-flow workflow tracing (instance tracking)
- OpenTelemetry distributed tracing
- Micrometer/Prometheus metrics
- Log aggregator integration (Kibana, Loki, Datadog)

**Triggers:** Mentions of "logging", "tracing", "observability", "MDC", "OpenTelemetry", "metrics", workflow debugging.

## How Skills Work Together

Skills are designed to chain together for complete workflows:

### Development → Review → Commit
```
java-dev or quarkus-flow-dev
  → quarkus-flow-testing (if writing tests)
  → code-review (automatic or manual)
    → java-git-commit
      → update-design (automatic)
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
dependency-update
  → code-review (if code changes)
    → java-git-commit
      → Optional: adr (for major upgrades)
```

### Observability Setup
```
logging-observability
  → dependency-update (for new deps)
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
- **Common Mistakes** documented with fixes
- **Real-World Impact** sections with production incident examples
- **Decision flowcharts** for complex workflows
- **Red Flags** sections to catch rationalizations early

## Usage

These skills are invoked automatically by Claude Code based on context, or explicitly via skill names:

```
/java-git-commit
/code-review
/update-design
/adr
```

Skills trigger automatically when relevant keywords appear in conversation or when working with specific file types.

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
| `quarkus-flow-dev` | `code-review` → `java-git-commit` | After workflow implementation |
| `quarkus-flow-testing` | `code-review` → `java-git-commit` | After writing tests |
| `code-review` | Blocks `java-git-commit` | If CRITICAL findings exist |
| `java-git-commit` | `update-design` | Always (automatic) |
| `dependency-update` | `adr` | Major version upgrades |
| `dependency-update` | `java-git-commit` | After successful update |
| `logging-observability` | `dependency-update` | Adding OTel/Micrometer deps |
| `logging-observability` | `adr` | First-time observability setup |
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
3. Customize BOM versions in `dependency-update`
4. Update observability endpoints in `logging-observability`

## Skill Quality & Validation

All skills have been systematically improved following the [superpowers:writing-skills](https://github.com/anthropics/superpowers) methodology:

- ✅ **CSO-optimized descriptions** (Claude Search Optimization) - trigger-focused, no workflow summaries
- ✅ **Token efficiency** - heavy reference material extracted to separate files
- ✅ **Quick Reference tables** - scannable summaries for fast lookup
- ✅ **Common Mistakes tables** - documented pitfalls with fixes
- ✅ **Real-World Impact** - production incidents demonstrating why rules matter
- ✅ **Decision flowcharts** - visual guides for non-obvious decisions
- ✅ **RED-GREEN-REFACTOR validation** - java-dev tested under pressure scenarios

**Testing methodology:** Skills are validated by running baseline scenarios WITHOUT the skill (documenting agent behavior), then WITH the skill (verifying compliance). The java-dev skill successfully prevented resource leaks under combined time pressure, authority pressure, and sunk cost.

## Repository Structure

```
.
├── LICENSE                          # Apache License 2.0
├── README.md                        # This file
├── java-dev/                        # Core Java/Quarkus development
│   └── SKILL.md
├── quarkus-flow-dev/               # Serverless Workflow patterns
│   ├── SKILL.md
│   └── funcDSL-reference.md        # Complete FuncDSL API reference
├── quarkus-flow-testing/           # Workflow testing patterns
│   └── SKILL.md
├── code-review/                    # Pre-commit quality checks
│   └── SKILL.md
├── security-audit/                 # Security vulnerability review
│   └── SKILL.md
├── java-git-commit/                # Smart commit with design sync
│   └── SKILL.md
├── update-design/                  # DESIGN.md maintenance
│   └── SKILL.md
├── adr/                            # Architecture Decision Records
│   └── SKILL.md
├── dependency-update/              # Maven dependency management
│   └── SKILL.md
└── logging-observability/          # Production observability setup
    └── SKILL.md
```
