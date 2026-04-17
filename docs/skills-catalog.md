# cc-praxis — Skills Catalog

> For installation and getting started: [README.md](../README.md) · For skills architecture: [architecture.md](architecture.md)

All 48 skills — descriptions, chaining relationships, and usage guidance.

---

#### **python-dev**
Expert Python development — type hints, async patterns, safety, and testing:
- Strict type annotation enforcement (no bare `Any`, use `Optional`/`Union` explicitly)
- Async/await correctness (unawaited coroutines, proper error propagation)
- Safety patterns (input validation, safe file operations, injection prevention)
- pytest best practices — fixtures, parametrize, no mocks where real objects work

**Features:** Quick Reference table · Rule Priority flowchart · Common Pitfalls table · ❌/✅ code examples

**Triggers:** Writing Python, fixing bugs, refactoring, `.py` files, `pyproject.toml`, `requirements.txt`.

#### **python-code-review**
Pre-commit code review for Python projects, extending code-review-principles:
- Type safety (bare `Any`, missing annotations, unsafe casts)
- Async correctness (unawaited coroutines, missing error handling)
- Test quality (mocks vs real, behavioural testing)

**Triggers:** "review the code", "check these changes", `/python-code-review`.

#### **python-security-audit**
OWASP Top 10 security audit for Python projects, triggered by python-code-review when security-critical code is detected:
- Injection vulnerabilities (SQL, command, template)
- Auth and session handling
- Sensitive data exposure (logging, serialisation)
- Dependency vulnerabilities (`pip audit`)

**Triggers:** Explicit security review request, or when python-code-review detects auth/payment/PII handling.

#### **pip-dependency-update**
Dependency management for pip, poetry, and pipenv projects:
- `pip audit` for known vulnerabilities
- Version constraint review (pinned vs ranges)
- Compatible upgrade proposals with `pip-compile` or `poetry update`
- Major version jump assessment — ADR offered when warranted

**Triggers:** "update dependencies", "bump version", "add dependency", `requirements.txt` or `pyproject.toml` changes.

#### **python-project-health**
Python-specific health checks extending the universal project-health skill:
- Type coverage (mypy strictness, annotation gaps)
- Test infrastructure (pytest config, coverage thresholds)
- Packaging correctness (`pyproject.toml`, entry points, classifiers)
- Python version compatibility claims vs actual syntax used

**Triggers:** `/python-project-health`, or auto-chained by `project-health` when `type: python` detected.

---

## Skills

### Setup & Management

#### **cc-praxis-ui**
Visual skill manager — a local web app for browsing, installing, updating, and uninstalling skills:
- Browse all 48 skills by bundle with descriptions and chaining relationships
- Live install state: see what's installed, what's outdated, and what's available
- Install or uninstall individual skills or whole bundles with accurate counts
- Auto Execute mode runs commands directly; Manual mode shows commands to copy-paste
- Context-aware: when served publicly (GitHub Pages) the Install tab is hidden

**Launch:** `/cc-praxis-ui` inside Claude Code, or `cc-praxis` in a terminal (added to PATH on plugin install).

**Server:** `python3 scripts/web_installer.py [--port PORT] [--no-browser]`

#### **workspace-init**
One-time workspace setup per project per machine:
- Creates `~/claude/private/<project>/` (or `public/`) with full directory structure
- Writes routing CLAUDE.md with `add-dir` session-start instruction and artifact locations table
- Creates gitignored CLAUDE.md symlink in the project via `.git/info/exclude` (never touches tracked `.gitignore`)
- Initialises a git repo for the workspace; optionally pushes to a remote
- Detects and offers to migrate existing `docs/` artifacts to the workspace

**Triggers:** "init workspace", "set up workspace", "create workspace for <project>", `/workspace-init`.

#### **epic**
Single entry point for the full epic lifecycle — detects current state and routes automatically:
- No active epic → offers to create branches, scaffold `design/JOURNAL.md` with SHA baseline, link or create a GitHub issue, optionally invoke brainstorming
- Active epic → asks whether to close it or begin a new one

**Starting an epic:** creates matching branches in the project repo and workspace, scaffolds `design/.meta` with epic name and SHA baseline, links to an existing GitHub issue or creates one.

**Closing an epic:** routes artifacts per `## Routing` config in workspace CLAUDE.md, merges `design/JOURNAL.md` into the project `DESIGN.md`, posts specs to the GitHub issue, handles branch cleanup with approve-all or step-by-step confirmation.

**Artifact routing** — three-layer config controls where artifacts go at epic close:
- Layer 1 (built-in): all artifacts → project repo
- Layer 2 (global): `~/.claude/CLAUDE.md ## Routing` — default destination
- Layer 3 (workspace): `## Routing` table in workspace CLAUDE.md — per-artifact override
Valid destinations: `project`, `workspace` (workspace/main), `alternative <path>`

**Triggers:** "begin epic", "new epic", "close epic", "finish epic", `/epic`.

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

**Features:** Common Pitfalls table · starter templates for skills and code repositories · modular CLAUDE.md support (primary + linked modules)

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

#### **docs/development/readme-sync.md**
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

**Note:** SKILL.md validation for type: skills repositories is handled by the **docs/development/skill-validation.md workflow**, not a portable skill. This modular documentation file is automatically referenced by git-commit when SKILL.md files are staged.

**What it validates:**
- Frontmatter structure (name, description, CSO compliance)
- Flowchart syntax (Mermaid validation, PUSH tier)
- Naming conventions (generic `-principles`, language prefixes)
- Cross-reference integrity (bidirectional chaining)
- Documentation completeness (Success Criteria, Common Pitfalls, Prerequisites)

**Automated validators:** `scripts/validate_all.py` orchestrates 19 validators across 3 tiers (commit/push/ci). See CLAUDE.md § Quality Assurance Framework for complete validation architecture.

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
- Stored in `adr/` (workspace)

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
- Stored in `snapshots/YYYY-MM-DD-<topic>.md` (workspace)

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

**Triggers:** "log this idea", "park that thought", "add to idea log", "we should consider this someday". Code review skills *mention* `/idea-log` as a pointer when a possibility surfaces — they do not invoke it automatically.

#### **write-blog**
Living project diary — captures decisions, pivots, and discoveries written in the moment, not in hindsight:
- Preserves what was believed at the time — including aspirations that later changed and approaches that were rejected
- Captures pivot moments explicitly: what was considered, what was rejected, what constraint forced the change
- Diary voice (first person, present tense, honest about uncertainty) — not a polished article written after everything is done
- Four entry types: Day Zero (initial vision before any code), Phase Update (milestone), Pivot (direction change), Correction (earlier belief proved wrong — never edits the original)
- Two modes: single entry (invoked with context) or full retrospective sweep (invoked blank — scans git history, proposes phases, writes in sequence)

**Features:**
- Correction entries reference originals rather than revising them — the historical record is preserved
- Mandatory writing rules loaded at draft time (not upfront) — retrospective workflow demand-loaded
- Integrates with `adr` (significant decisions get formal records) and `design-snapshot` (milestones get state freezes)
- Visual elements: illustrations (web-sourced or AI-generated), code blocks for interesting implementation detail, mandatory screenshots for any UI work (clipped to relevant area)
- Stored in `docs/blog/YYYY-MM-DD-<initials>NN-<topic>.md` (author initials from `~/.claude/settings.json` + per-author sequence number, prevents merge conflicts)

**Entry metadata (added at write time):**
- `entry_type`: `article` (topic-driven, standalone) or `note` (session narrative)
- `subtype`: `diary` for note entries
- `projects`: 1..n project identifiers — drives personal blog filtering
- `tags`: topic tags — drives routing rules via `blog-routing.yaml`

**Triggers:** "write a blog entry", "update the project blog", "log what we built today", "document this pivot", "add a diary entry", or at significant architectural decisions, pivots, or phase completions. `/write-blog` alone triggers the full retrospective sweep.

#### **publish-blog**
Routes blog entries from `docs/_posts/` to configured external git destinations based on `blog-routing.yaml` routing rules:
- Reads global `~/.claude/blog-routing.yaml` and optionally a per-workspace `blog-routing.yaml` (project rules extend global via `extends:`)
- Resolves destinations per entry using AND-logic match fields (`entry_type`, `tags`, `projects`) — multiple matching rules union their destinations
- Shows a routing plan before any file operations; user confirms or selects entries individually
- Copies entries to each destination directory; commits and pushes git destinations; reports per-destination outcome (✅ / ❌)
- Powered by `scripts/blog_router.py` — independently testable routing resolver

**Routing config format:**
```yaml
# ~/.claude/blog-routing.yaml
destinations:
  personal-blog: { type: git, path: ~/blog/, subdir: _posts/ }
  quarkus-blog:  { type: git, path: ~/quarkus-community-blog/, subdir: _posts/ }
defaults:
  destinations: [personal-blog]
rules:
  - match: { tags: [quarkus] }
    destinations: [quarkus-blog, personal-blog]
```

**This is Level 2 blog routing** — independent of `epic`'s Level 1 routing (where the `blog/` directory lives). The two systems do not interact.

**Triggers:** "publish blog", "publish entries", "cross-post this entry", `/publish-blog`.

#### **forage**
Cross-project library of hard-won technical knowledge — stored at `${HORTORA_GARDEN:-~/.hortora/garden}/` (a git repo shared across all projects on this machine). Three entry types: **gotchas** (bugs that silently fail, behaviours contradicting docs), **techniques** (non-obvious approaches a skilled developer wouldn't naturally reach for), and **undocumented** (features that exist and work but aren't in any docs).

Four session-time workflows:
- **CAPTURE** — add a specific entry (score, draft, confirm, commit to garden repo)
- **SWEEP** — scan the session for all three entry types; propose scored candidates; never asks the user to re-explain
- **SEARCH** — retrieve existing entries by keyword or symptom
- **REVISE** — enrich an existing entry with a solution, alternative, variant, or status change

For deduplication across existing entries, use `harvest` (separate skill — dedicated session operation).

**Features:**
- Submission model: write first, deduplicate later — no expensive garden reads during CAPTURE
- Garden Score (1–15) gates every submission: non-obviousness, discoverability, breadth, pain/impact, longevity
- Git-only access model: all reads via `git show HEAD:path` — never direct filesystem reads
- Distinct from `idea-log` (undecided possibilities), `adr` (formal decisions), `write-blog` (project narrative)

**Triggers:** "add this to the garden", "forage sweep", "search the garden", or proactively when something genuinely non-obvious surfaces during debugging.

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

#### **handover**
End-of-session HANDOFF.md generator — gives the next Claude session enough context to resume immediately:
- Delta-first: only changed sections written in full; unchanged sections reference git history
- Wrap checklist: offers write-blog, design-snapshot, update-claude-md, forage sweep before writing
- Forage sweep built in: scans session for gotchas, techniques, and undocumented items across all three categories before context is lost
- Session rename prompt: suggests a meaningful name and prompts `/rename` at the right moment
- Token budget: HANDOFF.md stays under 500 tokens — if it grows fat, routing is failing mid-epic

**Terminology:** *handover* = the act (what you do at session end); *handoff* = the artifact (`HANDOFF.md` passed to the next session)

**Triggers:** "create a handover", "end of session", "update the handover", "write a handover".

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
    → Validates SKILL.md (follows docs/development/skill-validation.md workflow if staged)
    → update-claude-md + docs/development/readme-sync.md (automatic)
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
Code review surfaces a possibility (review mentions /idea-log as a pointer)
  → /idea-log (user invokes to park it — no commitment required)
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
  → Validates SKILL.md (follows docs/development/skill-validation.md workflow)
  → Generates conventional commit message
  → Updates README.md via docs/development/readme-sync.md
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

