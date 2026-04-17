<p align="center">
  <img src="logo.svg" width="140" alt="cc-praxis logo"/>
</p>

# cc-praxis

**Claude Code skills that make professional software development feel automatic.**

You commit code — it reviews for safety issues first, syncs your design document, links the GitHub issue, and writes the conventional commit message. You ask Claude to implement a feature — it designs a spec, gets your approval, then writes a TDD implementation plan. You end a session — it captures a handover so the next session picks up in one message.

48 skills for Java/Quarkus, TypeScript/Node.js, and Python. Install the ones relevant to your stack, in any order.

---

## Quick Start

```bash
/plugin marketplace add github.com/mdproctor/cc-praxis
/plugin install install-skills
/install-skills
```

Pick a language bundle (or start with just 3 skills — see [Getting Started Guide](https://mdproctor.github.io/cc-praxis/guide/)). Close the session. Skills are active in every session after.

> **New to cc-praxis?** The [Getting Started Guide](https://mdproctor.github.io/cc-praxis/guide/) walks you through the full workflow in 12 steps — pick Java, TypeScript, or Python.

> **Dependency resolution note:** The official Claude Code marketplace doesn't yet support automatic dependency resolution ([Issue #9444](https://github.com/anthropics/claude-code/issues/9444)). The `/install-skills` wizard handles this for you. If you prefer installing manually, use the `scripts/claude-skill` installer below.

**To uninstall:**
```bash
/uninstall-skills
```

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

Add to your `CLAUDE.md`:

```markdown
## Project Type

**Type:** java   # java | skills | blog | custom | generic
```

For the `custom` type's full sync configuration and all type definitions: [docs/PROJECT-TYPES.md](docs/PROJECT-TYPES.md).

### What Happens at Commit Time

**type: skills** → `git-commit`:
- Validates SKILL.md files (follows docs/development/skill-validation.md workflow)
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


## Skill Chaining Reference

**Invocation types:** `auto` = always happens without user input · `conditional` = happens when a condition is met · `manual` = user explicitly requests it · `prereq` = loaded as foundation before the skill runs

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
| `handover` | `forage` | conditional | Forage sweep checked in wrap checklist (Step 2b) |
| `handover` | `write-blog` | conditional | Blog entry checked in wrap checklist |
| `handover` | `design-snapshot` | conditional | Design snapshot checked in wrap checklist |
| `handover` | `update-claude-md` | conditional | Convention sync checked in wrap checklist |
| `write-blog` | `publish-blog` | manual | User wants to push entries to external platforms |
| `idea-log` | `adr` | manual | Promoting an idea to a formal architectural decision |
| `idea-log` | `issue-workflow` | manual | Promoting an idea to tracked implementation work |
| `idea-log` | `git-commit` | manual | Committing IDEAS.md additions and status updates |
| `design-snapshot` | `idea-log` | conditional | Reviewing a snapshot surfaces undecided ideas |
| `epic` | `superpowers:brainstorming` | conditional | User accepts brainstorm offer when starting an epic |
| `project-health` | `skills-project-health` | auto | type: skills detected in CLAUDE.md (tier 3+) |
| `project-health` | `java-project-health` | auto | type: java detected in CLAUDE.md (tier 3+) |
| `project-health` | `blog-project-health` | auto | type: blog detected in CLAUDE.md (tier 3+) |
| `project-health` | `custom-project-health` | auto | type: custom detected in CLAUDE.md (tier 3+) |
| `project-health` | `ts-project-health` | conditional | TypeScript project detected (tier 3+) |
| `project-health` | `python-project-health` | conditional | Python project detected (tier 3+) |
| `java-code-review` | `code-review-principles` | prereq | Universal review checklist loaded as foundation |
| `ts-code-review` | `code-review-principles` | prereq | Universal review checklist loaded as foundation |
| `python-code-review` | `code-review-principles` | prereq | Universal review checklist loaded as foundation |
| `java-security-audit` | `security-audit-principles` | prereq | Universal OWASP Top 10 loaded as foundation |
| `ts-security-audit` | `security-audit-principles` | prereq | Universal OWASP Top 10 loaded as foundation |
| `python-security-audit` | `security-audit-principles` | prereq | Universal OWASP Top 10 loaded as foundation |
| `maven-dependency-update` | `dependency-management-principles` | prereq | Universal BOM patterns loaded as foundation |
| `npm-dependency-update` | `dependency-management-principles` | prereq | Universal BOM patterns loaded as foundation |
| `pip-dependency-update` | `dependency-management-principles` | prereq | Universal BOM patterns loaded as foundation |
| `quarkus-observability` | `observability-principles` | prereq | Universal logging/tracing/metrics loaded as foundation |
| `quarkus-flow-dev` | `java-dev` | prereq | Java safety and concurrency rules loaded as foundation |
| `quarkus-flow-testing` | `java-dev` | prereq | Java testing patterns loaded as foundation |
| `quarkus-flow-testing` | `quarkus-flow-dev` | prereq | Quarkus Flow workflow patterns loaded as foundation |

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

For contributors and skill authors: [QUALITY.md](QUALITY.md) covers the full validation framework — 19 validators across commit/push/CI tiers, the division of labour between scripts and Claude, and the skill authoring quality bar.

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
│   └── marketplace.json                 # Marketplace catalog (48 skills; excludes sync-local dev-only)
├── scripts/                             # Automation and validation
│   ├── claude-skill                     # Skill installer/manager CLI (install, sync-local, etc.)
│   ├── web_installer.py                 # Web skill manager server (serves docs/index.html)
│   ├── generate_web_app_data.py         # Regenerates CHAIN JS + bundle meta in docs/index.html
│   ├── validate_all.py                  # Master orchestrator (3-tier validation)
│   ├── validate_document.py             # Universal .md corruption detector
│   ├── generate_skill_metadata.py       # Regenerates skill.json for all skills
│   ├── blog_router.py                   # Blog routing config resolver (load, merge, resolve destinations)
│   ├── workspace_routing.py             # Three-layer workspace routing resolver (CLAUDE.md ## Routing)
│   └── validation/                      # SKILL.md validators (21 total, 3 tiers)
│       ├── validate_frontmatter.py     # YAML structure, required fields [COMMIT]
│       ├── validate_cso.py             # Description CSO compliance [COMMIT]
│       ├── validate_references.py      # Cross-reference integrity [COMMIT]
│       ├── validate_naming.py          # Naming conventions [COMMIT]
│       ├── validate_sections.py        # Required sections by type [COMMIT]
│       ├── validate_structure.py       # File organization [COMMIT]
│       ├── validate_project_types.py   # Project type list consistency [COMMIT]
│       ├── validate_blog_frontmatter.py # Blog post frontmatter validation [COMMIT]
│       ├── validate_blog_commit.py     # Blog commit message conventions [COMMIT]
│       ├── validate_doc_structure.py   # Modularisation nudge threshold check [COMMIT]
│       ├── validate_flowcharts.py      # Mermaid syntax validation [PUSH]
│       ├── validate_web_app.py         # Web app sync with SKILL.md data [PUSH]
│       ├── validate_cross_document.py  # Cross-document consistency [PUSH]
│       ├── validate_temporal.py        # Stale references [PUSH]
│       ├── validate_usability.py       # Readability, UX [PUSH]
│       ├── validate_edge_cases.py      # Edge case coverage [PUSH]
│       ├── validate_behavior.py        # Behavioral consistency [PUSH]
│       ├── validate_readme_sync.py     # README/CLAUDE sync [PUSH]
│       ├── validate_links.py           # External link reachability [PUSH]
│       ├── validate_examples.py        # Code example correctness [PUSH]
│       └── validate_python_quality.py  # mypy, flake8, bandit [CI]
├── tests/                               # Test suite (1152 tests)
│   ├── test_claude_skill.py            # Tests for scripts/claude-skill
│   ├── test_mockup_chaining.py         # Skill chaining ground truth (CHAINING_TRUTH)
│   ├── test_chain_data_drift.py        # CHAIN JS in index.html vs CHAINING_TRUTH
│   ├── test_web_installer_server.py    # Web installer API unit tests (55 tests)
│   ├── test_web_installer_integration.py # Real install/uninstall permutation tests (40 tests)
│   ├── test_web_installer_ui.py        # Playwright browser UI tests (38 tests)
│   ├── test_document_discovery.py      # Tests for document discovery
│   ├── test_document_cache.py          # Tests for document caching
│   ├── test_modular_validator.py       # Tests for modular validator
│   ├── test_blog_router.py             # Blog routing resolver (37 tests — unit, integration, e2e)
│   ├── test_jekyll_pages.py            # Jekyll articles/diary page templates (21 tests)
│   ├── test_workspace_routing.py       # Three-layer workspace routing resolver (36 tests)
│   ├── test_guide_page.py              # Getting started guide structural tests (24 tests)
│   └── test_guide_ui.py               # Getting started guide Playwright e2e tests (18 tests)
├── docs/                                # Web skill manager + documentation
│   ├── index.html                       # Web skill manager UI (About/Browse/Install tabs)
│   ├── guide.html                       # 12-section interactive getting started guide (/guide/)
│   ├── architecture.md                  # Skills layered architecture — 9-layer diagram and tables
│   ├── skills-catalog.md               # Full 48-skill reference catalog with descriptions and usage
│   ├── articles/
│   │   └── index.html                   # Articles listing page — filters entry_type: article
│   ├── blog/
│   │   └── index.html                   # Diary listing page — filters subtype: diary
│   ├── ideas/
│   │   └── IDEAS.md                     # Project idea log (undecided possibilities)
│   ├── PROJECT-TYPES.md                # Complete project type taxonomy and routing
│   ├── adr/                            # Architecture Decision Records
│   └── development/
│       ├── skill-validation.md         # Skills-specific SKILL.md validation workflow
│       ├── readme-sync.md              # Skills-specific README.md sync workflow
│       └── registry-template.json     # Template for external registry repositories
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
│   ├── SKILL.md
│   ├── starter-templates.md             # CLAUDE.md starter templates (skills + code repos)
│   └── modular-handling.md              # Modular CLAUDE.md discovery, propose, and validate
├── java-update-design/                  # DESIGN.md architecture sync (Java projects)
│   ├── SKILL.md
│   ├── mapping-reference.md             # Code change → DESIGN.md section mapping table
│   ├── starter-template.md              # DESIGN.md starter template for new Java projects
│   └── modular-handling.md              # Modular DESIGN.md discovery, propose, and validate
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
├── write-blog/                          # Living project diary skill
│   └── SKILL.md
├── publish-blog/                        # Blog entry publishing to external git destinations
│   └── SKILL.md
└── adr/                                 # Architecture Decision Records skill
    └── SKILL.md
```
