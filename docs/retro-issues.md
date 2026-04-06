# Retrospective Issue Mapping
Generated: 2026-04-06
Repo: mdproctor/cc-praxis
Scope: 2026-03-29 → 2026-04-06 | 285 commits analysed
Summary: 0 epics · 0 child issues · 27 standalones · 1 excluded | Issues: #1–#27

**Epic analysis:** v1.0.0 tag (2026-03-31) and blog entries provide candidate boundaries,
but every time window spans 4+ unrelated scopes (marketplace, validation, garden,
project-health, write-blog, etc.). Gate 3 fails for all windows → all standalones.
This is correct — the project developed many independent skill areas in parallel sprints.

---

## Standalone Issues

### Issue #1: "Add initial skill collection" [enhancement]
Scopes: (initial commit, skills, docs)
Period: 2026-03-29
Commits:
- `77a4dca` 2026-03-29 — This is my first set of skills
- `7ff998` 2026-03-29 — docs: enhance skills with quality improvements and validation
- `6ee3ed` 2026-03-29 — docs(skills): enhance skills with code examples and add security-audit

---

### Issue #2: "Refactor skill collection for consistency and CSO compliance" [enhancement]
Scopes: skills
Period: 2026-03-29
Commits:
- `230d89` 2026-03-29 — refactor(skills): improve consistency and cross-referencing
- `bbd81e` 2026-03-29 — refactor(skills): complete cross-reference and consistency fixes
- `7221ad` 2026-03-29 — refactor(skills): extract generic principles and rename for clarity
- `2cefb9` 2026-03-29 — feat(skills): add CLAUDE.md synchronization via update-claude-md skill
- `0d1c56` 2026-03-29 — feat(skills): add skill-review and update-readme for complete skills repository workflow
- `9972c3` 2026-03-29 — fix(skills): correct bidirectional cross-references and chaining descriptions
- `d1aea3` 2026-03-29 — fix(skills): complete structural consistency across all skills
- `b55fa0` 2026-03-29 — refactor(skills): improve readability and consistency across all skills
- `9e16af` 2026-03-29 — refactor(skills): improve readability and scannability
- `a0e0dc` 2026-03-29 — refactor(skills): fix logic errors and improve clarity
- `4066ac` 2026-03-29 — style(skills): add light developer humor to reinforce key points
- `273441` 2026-03-29 — refactor(skills): tighten frontmatter triggers to prevent token waste
- `1baf79` 2026-03-29 — docs: improve frontmatter CSO compliance and clarity
- `6ebb84` 2026-04-03 — docs: thorough bidirectional chaining audit and test
- `56e2c0` 2026-04-01 — docs: comprehensive documentation audit — accuracy, structure, CSO compliance

---

### Issue #3: "Improve README documentation" [documentation]
Scopes: readme
Period: 2026-03-29 → 2026-04-01
Commits:
- `1068cf` 2026-03-29 — docs(readme): expand Key Features with missing highlights
- `8dc538` 2026-03-29 — docs(readme): rename 'Key improvements' to 'Key Features'
- `b1b7db` 2026-03-29 — docs(readme): add humorous section on commit message importance
- `b61476` 2026-03-29 — docs(readme): fix gaps and update quality validation
- `12dccc` 2026-03-30 — docs(readme): add reference to PROJECT-TYPES.md
- `32167d` 2026-03-30 — docs(readme): comprehensive Quality & Validation Framework documentation
- `adba2e` 2026-03-30 — refactor(readme): remove duplicate sections and clean structure
- `0b03f2` 2026-03-30 — fix(docs): remove skill-review references from README.md
- `0a0dbb` 2026-03-31 — docs(readme): move installation to top and document both methods
- `46da70` 2026-03-31 — docs(readme): add skill authoring benefit to cloning
- `53f031` 2026-03-30 — docs: update README and QUALITY.md with completed validation infrastructure
- `6f3f76` 2026-03-30 — docs(philosophy): add reflection on what makes this collection special
- `dfc350` 2026-03-30 — docs(philosophy): make reflection timeless and universal
- `8e4f19` 2026-04-01 — feat: add cc-praxis logo to repository and README

---

### Issue #4: "Strengthen git-commit and java-git-commit skills" [enhancement]
Scopes: git-commit, java-git-commit
Period: 2026-03-29 → 2026-04-03
Commits:
- `3a6fa1` 2026-03-29 — feat(java-git-commit): add DESIGN.md existence check
- `17adba` 2026-03-29 — docs(readme): document java-git-commit DESIGN.md enforcement
- `2bbd55` 2026-03-29 — fix(git-commit): strengthen no-attribution rule and add examples
- `025fdd` 2026-03-29 — fix(git-commit): clarify repository type distinction vs java-git-commit
- `7e7c41` 2026-03-30 — docs(git-commit): add pragmatic scope guidance
- `cb0bc1` 2026-04-03 — fix: git-commit is a universal root — not invoked by ts-code-review

---

### Issue #5: "Build skill validation and testing framework" [enhancement]
Scopes: validation, qa, testing, mermaid
Period: 2026-03-30 → 2026-04-02
Commits:
- `8b36d3` 2026-03-30 — feat(qa): add comprehensive quality assurance framework
- `0010d3` 2026-03-30 — test(qa): implement functional testing infrastructure
- `ff8c32` 2026-03-30 — feat(qa): add validation tiering strategy to plan and CLAUDE.md
- `82a198` 2026-03-30 — test(testing): add git worktree isolation to skill test runner
- `bb98a5` 2026-03-30 — test(testing): add basic test runner structure
- `aa64f5` 2026-03-30 — fix(testing): improve test runner resilience
- `075b0d` 2026-03-30 — feat(testing): add regression test runner
- `1ee0a0` 2026-03-30 — fix(testing): improve regression test runner robustness
- `e86e2f` 2026-03-30 — feat(testing): add test coverage reporter
- `bc6404` 2026-03-30 — feat(validation): add README/CLAUDE.md sync validator
- `f0c341` 2026-03-30 — feat(validation): add tier support to validation orchestrator
- `12fa04` 2026-03-30 — feat(validation): add cross-document consistency validator
- `49401d` 2026-03-30 — feat(validation): add temporal consistency validator
- `902e98` 2026-03-30 — feat(validation): add usability/UX validator
- `776916` 2026-03-30 — feat(validation): add edge case coverage validator
- `7a865f` 2026-03-30 — feat(validation): add behavior consistency validator
- `8a9e9d` 2026-03-30 — feat(validation): add Python quality validator
- `bb6781` 2026-03-30 — fix(validation): fix orchestrator target passing to validators
- `eb1518` 2026-03-30 — test: add test cases for high-priority skills + fix coverage bug
- `9ddc8f` 2026-03-30 — test: achieve 100% coverage with tier-appropriate tests
- `bdd8d6` 2026-03-30 — chore: ignore Python cache directories
- `c862907` 2026-03-30 — feat: add universal document validation to prevent sync corruption
- `95cd8e` 2026-03-30 — refactor: modularize skills-specific validation to eliminate token waste
- `4bfc12` 2026-03-31 — fix(mermaid): quote parentheses in labels and add Mermaid syntax validator
- `c09459` 2026-04-01 — feat(validation): add project-type list consistency validator
- `53efc4` 2026-04-01 — feat(validation): enforce slash command files for all skills
- `2588c1` 2026-04-02 — feat: add validate_links and validate_examples to PUSH tier
- `a837e8` 2026-04-02 — fix: only treat explicit 'Parse error' as Mermaid syntax failure in CI
- `6c9de6` 2026-04-02 — fix: flowchart validator treats puppeteer CI failures as mmdc unavailable
- `e9efe9` 2026-04-02 — refactor: unify ValidationResult — remove duplicate class from modular_validator
- `e44c8e` 2026-03-30 — docs(spec): comprehensive quality review design
- `62ec73` 2026-03-30 — docs(qa): document Phase 1 findings and tiering strategy
- `ae5723` 2026-03-30 — docs(qa): mark Phase 2 validators as complete
- `c0bf72` 2026-03-30 — docs(qa): comprehensive quality review findings report
- `3010f0` 2026-03-30 — docs: comprehensive quality review completion summary
- `615c57` 2026-03-30 — docs: update comprehensive review with test coverage improvements
- `cd9e52` 2026-03-30 — docs: update review completion with 100% test coverage achievement
- `acc5c7` 2026-03-30 — docs: update quality review completion with validator validation
- `e825a6` 2026-03-30 — docs: create QUALITY.md and streamline README
- `b9547a` 2026-03-30 — docs: add comprehensive QA framework and validation guidance
- `653d6b` 2026-03-30 — docs(quality): document Quick tier and universal framework vision

---

### Issue #6: "Consolidate CLAUDE.md documentation and policies" [documentation]
Scopes: claude-md
Period: 2026-03-29 → 2026-04-01
Commits:
- `615d3d` 2026-03-29 — docs(claude-md): add project type awareness and extensibility guidance
- `665b5c` 2026-03-30 — docs(claude-md): comprehensive project type taxonomy and guidance
- `0f038a` 2026-03-30 — docs(claude-md): consolidate document sync QA
- `3418e0` 2026-03-30 — docs(claude-md): consolidate QA framework with QUALITY.md
- `b71fbb` 2026-03-30 — docs(claude-md): minimize modular documentation section
- `b26f27` 2026-03-30 — docs(claude-md): consolidate project type awareness
- `8c272e` 2026-03-30 — docs(claude-md): standardize tier naming to match implementation
- `5ea3dd` 2026-03-30 — docs(claude-md): make checklists mandatory by default
- `2a6416` 2026-03-30 — docs: add third-party exclusion policy and restructure
- `cf5f3b` 2026-04-01 — docs(claude-md): add project identity, developer workflow, and new skills for fresh sessions
- `564f07` 2026-04-01 — docs(claude-md): add no-AI-attribution rule to pre-commit checklist
- `9ee94d` 2026-04-01 — docs(claude-md): document skill loading rules — symlinks, commands, cache
- `e019a0` 2026-04-01 — docs(claude-md): consistency pass — remove duplication and stale content
- `d00e87` 2026-04-01 — docs(claude-md): document bundle management workflow
- `0631f6` 2026-04-06 — docs(CLAUDE.md): document /sync-local slash command and defaults/ skill pattern

---

### Issue #7: "Add project type taxonomy and routing" [enhancement]
Scopes: project-types, commit (routing)
Period: 2026-03-30 → 2026-04-01
Commits:
- `da1249` 2026-03-30 — feat: add project type taxonomy and routing
- `50b945` 2026-03-30 — feat(commit): add project type taxonomy and routing
- `a62584` 2026-03-30 — docs: extract project type taxonomy to reference doc
- `789753` 2026-03-30 — refactor: extract generic update-primary-doc base
- `73bbc2` 2026-03-30 — refactor(update-claude-md): remove redundant skills-specific section
- `cde4f3` 2026-04-01 — feat(project-types): add blog type for GitHub Pages / Jekyll

---

### Issue #8: "Add modular documentation support" [enhancement]
Scopes: docs (modular)
Period: 2026-03-30 → 2026-04-01
Commits:
- `258036` 2026-03-30 — feat: add modular documentation support with hybrid discovery
- `23c5ff` 2026-04-01 — feat(docs): progressive modular doc nudge with user-adjustable threshold
- `8f7e82` 2026-03-30 — refactor: modularize skills-update-readme to save tokens
- `fb5ede` 2026-03-30 — fix: implement adr invocation and update Skill Chaining Reference

---

### Issue #9: "Add ADR infrastructure and architectural decisions" [documentation]
Scopes: adr
Period: 2026-03-30
Commits:
- `e900fd` 2026-03-30 — docs(adr): add architectural decision records for key design choices

---

### Issue #10: "Build marketplace CLI and skill installation system" [enhancement]
Scopes: marketplace, install-skills, uninstall-skills
Period: 2026-03-30 → 2026-04-01
Commits:
- `a14325` 2026-03-30 — feat(marketplace): add skill scanner for metadata generation
- `6fb105` 2026-03-30 — feat(marketplace): add frontmatter parser for skill name
- `b51779` 2026-03-30 — feat(marketplace): add dependency parser from Prerequisites section
- `f6fef4` 2026-03-30 — feat(marketplace): add skill.json generator
- `01a57e` 2026-03-30 — fix(marketplace): add error handling and validation to skill.json generator
- `b3c05c` 2026-03-30 — fix(marketplace): add write error handling and complete test coverage
- `512e4b` 2026-03-31 — feat(marketplace): add main CLI for metadata generation
- `ce3fe4` 2026-03-31 — fix(marketplace): add error resilience and complete test coverage for main CLI
- `7ad797` 2026-03-31 — feat(marketplace): add registry fetcher
- `10ebd0` 2026-03-31 — feat(marketplace): add skill lookup in registry
- `66b49e` 2026-03-31 — feat(marketplace): add dependency graph builder
- `bb8131` 2026-03-31 — fix(marketplace): add circular dependency detection to graph builder
- `2379c6` 2026-03-31 — feat(marketplace): add dependency conflict detection
- `96980f` 2026-03-31 — feat(marketplace): add git sparse checkout installer
- `a3db12` 2026-03-31 — fix(marketplace): add validation and atomic installation
- `1da9b7` 2026-03-31 — feat(marketplace): add skill validation
- `0af298` 2026-03-31 — test(marketplace): add missing validator test coverage
- `3e7a65` 2026-03-31 — feat(marketplace): add CLI install command
- `9a4e29` 2026-03-31 — fix(marketplace): improve CLI input handling and test coverage
- `3f88bc` 2026-03-31 — feat(marketplace): add CLI uninstall command
- `0df183` 2026-03-31 — feat(marketplace): add CLI list command
- `7ce99b` 2026-03-31 — feat(marketplace): add main CLI entry point
- `46b4c2` 2026-03-31 — docs(marketplace): add registry usage and publishing guide
- `dc9f97` 2026-03-31 — docs(readme): add marketplace installation instructions
- `eed604` 2026-03-31 — test(marketplace): add end-to-end integration tests
- `785b38` 2026-03-31 — feat(marketplace): add registry template with all skills
- `4c7c72` 2026-03-31 — docs: add skill marketplace implementation plan and design spec
- `080e9b` 2026-03-31 — refactor(marketplace): adopt official formats and reduce custom code by 92%
- `258b12` 2026-03-31 — feat(marketplace): add install-all command
- `a21ce9` 2026-03-31 — feat(marketplace): add uninstall-all command
- `7e5790` 2026-03-31 — feat(marketplace): add install-skills bootstrap wizard
- `90fde2` 2026-03-31 — feat(marketplace): add uninstall-skills cleanup wizard
- `2fcb87` 2026-03-31 — fix(marketplace): use relative paths in plugin source fields
- `cf5e26` 2026-04-01 — feat(marketplace): make bundle lists dynamic from marketplace.json
- `40616c` 2026-04-01 — chore(marketplace): update description to reflect broader scope

---

### Issue #11: "Refactor scripts and hooks for Claude Code compatibility" [enhancement]
Scopes: scripts, hooks
Period: 2026-04-01
Commits:
- `5a3274` 2026-04-01 — feat(scripts): add sync-local command and claude-skill test suite
- `374d92` 2026-04-01 — fix(hooks): make session-start hook directive so Claude acts on it
- `1a2701` 2026-04-01 — feat(scripts): sync-local now installs and updates the session-start hook
- `73fdc4` 2026-04-01 — refactor(scripts): install skills to ~/.claude/skills/ not plugin cache
- `6c5fc0` 2026-04-01 — fix(scripts): never symlink into Claude Code plugin cache
- `55b5df` 2026-04-01 — fix(scripts): sync-local now updates Claude Code's real plugin cache
- `b2b6f6` 2026-04-01 — refactor(scripts): remove .marketplace — install directly to Claude plugin cache

---

### Issue #12: "Add Java development skill improvements" [enhancement]
Scopes: java-dev
Period: 2026-04-01
Commits:
- `3993cb` 2026-04-01 — feat(java-dev): MCP refactoring tiers, multi-line strings, attribution
- `e95da1` 2026-04-01 — feat(java-dev): extend no-string-literals rule to cover package names
- `bd0e6e` 2026-04-01 — feat(java-dev): require .class references instead of String class names
- `b334f4` 2026-04-01 — fix(java-dev): remove artifacts, fix stale refs, tighten incident narratives
- `d48371` 2026-04-01 — fix(skills): systematic review fixes across 4 skills

---

### Issue #13: "Add slash command support for all skills" [enhancement]
Scopes: validation, skills (commands)
Period: 2026-04-01
Commits:
- `2e16d9` 2026-04-01 — feat(skills): add slash commands to all 20 skills
- `53efc4` 2026-04-01 — feat(validation): enforce slash command files for all skills

---

### Issue #14: "Add blog project type and git-commit skill" [enhancement]
Scopes: blog, project-types
Period: 2026-04-01
Commits:
- `a4a7e0` 2026-04-01 — feat(blog): add blog-git-commit skill with commit message validation
- `cde4f3` 2026-04-01 — feat(project-types): add blog type for GitHub Pages / Jekyll

---

### Issue #15: "Rename project to cc-praxis" [chore]
Scopes: (rename)
Period: 2026-04-01
Commits:
- `891dcd` 2026-04-01 — rename: claude-skills → cc-praxis

---

### Issue #16: "Add GitHub issue tracking skill" [enhancement]
Scopes: issue-workflow
Period: 2026-04-01, 2026-04-06
Commits:
- `818624` 2026-04-01 — feat(issue-workflow): add GitHub issue tracking skill
- `ea2fb9` 2026-04-06 — feat(issue-workflow): add epic planning and proactive issue creation

---

### Issue #17: "Design and implement project-health skill suite" [enhancement]
Scopes: project-health, health, project-refine
Period: 2026-04-01 → 2026-04-02
Commits:
- `cfb9fb` 2026-04-01 — docs: add project-health skill design document
- `c3a3f8` 2026-04-01 — refactor: centralise health checks by referencing project-health design doc
- `48c0a8` 2026-04-01 — docs(project-health): add category overview table and invocation groups
- `74c666` 2026-04-01 — docs(project-health): split category table by universal vs project type
- `8c0f3c` 2026-04-01 — docs(project-health): define universal document scanning scope
- `55e1c3` 2026-04-01 — docs(project-health): extend scanning scope for inline docs and user-configured paths
- `b57a18` 2026-04-01 — docs(project-health): add well-known root doc filenames, case-insensitive
- `ad804e` 2026-04-01 — feat(discovery): add well-known doc names and user-configured paths to scanner
- `285233` 2026-04-01 — docs(project-health): add 'improve' category with bloat scoring
- `c10617` 2026-04-01 — docs(project-health): rename 'improve' category to 'refine'
- `ffa271` 2026-04-01 — docs(project-health): add refinement dimension to every check category
- `2fb8af` 2026-04-01 — docs(project-health): structural consistency pass — Quality and Refinement aligned
- `bccba5` 2026-04-01 — docs(project-health): extract four universal checks from per-type additions
- `df0cf2` 2026-04-01 — docs: split project-health into two companion skills
- `f4001f` 2026-04-01 — docs(project-health): adopt Option B — universal base + type-specific skills
- `76965e` 2026-04-01 — fix: pre-v1.0 system review — 13 issues resolved
- `116cca` 2026-04-02 — docs(java-project-health): add java-code-quality category for duplication and extraction
- `fb50a2` 2026-04-02 — docs(project-health): remove skills-specific categories from universal, fix narrow checks
- `1120a4` 2026-04-02 — docs(project-health): move type-specific scan targets to type-specific skills
- `f4001f` 2026-04-02 — docs(project-health): emphasise bidirectional chaining with type-specific skills
- `d44d7e` 2026-04-02 — docs(project-health): remove all remaining type-specific content
- `a06036` 2026-04-02 — docs(health): enrich all six health documents with additional checks
- `1c72e5` 2026-04-02 — chore(docs): remove stale reports, archive superseded plans
- `9464b2` 2026-04-02 — fix: address project-health tier-4 findings
- `6acd63` 2026-04-02 — refactor: project-refine tier-4 improvements across collection
- `741f95` 2026-04-02 — refactor: complete near-term cleanup items
- `11173` 2026-04-02 — feat: implement project-health and project-refine skill suite
- `c0ab36` 2026-04-02 — fix: design review corrections across all health documents
- `d59abf` 2026-04-02 — docs(project-refine): defer tracking is a TODO — always show all findings for now
- `446d1d` 2026-04-02 — docs: add tier system to project-health and project-refine
- `dea852` 2026-04-02 — docs(project-refine): merge tests into code domain — tests are code
- `fbeb55` 2026-04-02 — docs: resolve all five open questions for project-health and project-refine
- `77e3c5` 2026-04-02 — docs(project-health): resolve type-context-before-checks — type detection is step 1
- `dbb59d` 2026-04-02 — docs(project-health): resolve routing — Option B auto-chain

---

### Issue #18: "Add TypeScript/Node.js skill suite" [enhancement]
Scopes: ts-dev, ts-code-review, ts-security-audit, npm-dependency-update, ts-project-health
Period: 2026-04-02
Commits:
- `136d50` 2026-04-02 — docs: systematic TypeScript documentation coverage review
- `29fa6e` 2026-04-02 — feat: add TypeScript/Node.js skill suite (5 skills)

---

### Issue #19: "Add Python skill suite" [enhancement]
Scopes: python-dev, python-code-review, python-security-audit, pip-dependency-update, python-project-health
Period: 2026-04-03
Commits:
- `62bd5d` 2026-04-03 — feat: add Python skill suite (5 skills)
- `5d07ab` 2026-04-03 — docs: systematic Python documentation coverage

---

### Issue #20: "Set up GitHub Actions CI" [enhancement]
Scopes: ci
Period: 2026-04-02
Commits:
- `85f771` 2026-04-02 — ci: opt into Node.js 24 for GitHub Actions runners
- `5c67ed` 2026-04-02 — ci: replace stub workflow with working two-job CI

---

### Issue #21: "Build web installer UI (cc-praxis-ui)" [enhancement]
Scopes: cc-praxis-ui, web installer, marketplace (UI layer)
Period: 2026-04-03 → 2026-04-04
Commits:
- `e05ae3` 2026-04-03 — docs: web installer test specification (80 test cases)
- `d28d0e` 2026-04-04 — feat: implement web_installer.py with live state and 60 tests
- `ab2cbf` 2026-04-04 — feat: add cc-praxis-ui skill and bin/cc-praxis launcher
- `83bd53` 2026-04-04 — fix: install specific skills from web UI
- `f97796` 2026-04-04 — fix: missing bundle buttons + 30 Playwright UI tests
- `eb4924` 2026-04-04 — fix: bundle state UI never updated + add integration tests
- `e9c412` 2026-04-04 — fix: bundle modal shows actual skill count, not hardcoded total
- `b0e655` 2026-04-04 — fix: UX/design review — 11 improvements to web installer UI
- `69b48e` 2026-04-04 — test: add coverage for all UX/design review fixes (37 new tests)
- `a50c12` 2026-04-04 — feat: ergonomics, aesthetics and user flow improvements
- `cfc1c7` 2026-04-04 — docs: document cc-praxis-ui, web installer, and new test infrastructure
- `93e18f` 2026-04-04 — docs: add SKILL-MANAGER.md user guide for the web UI
- `372866` 2026-04-04 — docs: replace ASCII art in SKILL-MANAGER.md with real screenshots
- `2aefad` 2026-04-04 — docs: expand SKILL-MANAGER.md with 10 additional screenshots and sections
- `89054a` 2026-04-04 — refactor: wire methodology skills into a cohesive family

---

### Issue #22: "Add unified web app for GitHub Pages" [enhancement]
Scopes: web app, generate_web_app_data
Period: 2026-04-03
Commits:
- `4081817` 2026-04-03 — feat: unified web app — single index.html adapts to local vs web context
- `ab6354` 2026-04-03 — feat: generate_web_app_data.py + validate_web_app.py prevent drift

---

### Issue #23: "Add utility skills (idea-log, design-snapshot, sync-local)" [enhancement]
Scopes: idea-log, design-snapshot, sync-local
Period: 2026-04-03 → 2026-04-05
Commits:
- `8a74b7` 2026-04-03 — feat: add design-snapshot skill
- `829e26` 2026-04-04 — feat: add idea-log skill for parking undecided ideas
- `80dbc0` 2026-04-04 — docs: log idea — dual-repo model for epic-scoped developer work
- `1db993` 2026-04-06 — docs: add design snapshot 2026-04-06-writing-infrastructure-and-garden
- `33730` 2026-04-06 — docs: log idea — periodically evolve personal writing style guide
- `871633` 2026-04-05 — feat: add sync-local dev skill and document dev-only skill pattern

---

### Issue #24: "Build knowledge garden skill" [enhancement]
Scopes: garden, knowledge-garden
Period: 2026-04-04 → 2026-04-06
Commits:
- `acef1d` 2026-04-04 — feat: add knowledge-garden skill — cross-project gotcha library
- `3e1caf` 2026-04-04 — rename: knowledge-garden → garden
- `240bc8` 2026-04-04 — refactor: garden — submission-based contribution model
- `bc20cf` 2026-04-04 — feat: garden accepts techniques alongside gotchas
- `a227d8` 2026-04-05 — feat: garden accepts undocumented entries as third type
- `4bcc5b` 2026-04-05 — feat: garden SWEEP operation — scans session for all 3 entry types
- `67ff53` 2026-04-05 — feat(garden): add techniques to description trigger, approaches/ directory, and routing
- `1db628` 2026-04-05 — refactor(garden): technique covers approaches; labels for cross-cutting; remove approaches/ dir
- `be8d6a` 2026-04-05 — feat(garden): improve MERGE guidance, file header rules, label compliance, three-axis index
- `266c2b` 2026-04-05 — feat(garden): version policy — required for 3rd party libs, omit for own pre-1.0 projects
- `660088` 2026-04-06 — fix(garden): compute and show score at SWEEP proposal time, not after confirmation
- `1dec5a` 2026-04-05 — feat(garden): add scoring system to submission and merge workflow
- `1c0bc6` 2026-04-06 — feat(garden): add GE-IDs, DEDUPE workflow, drift algorithm, CHECKED.md
- `ad4897` 2026-04-06 — feat(garden): IDs at submission time, three-tier dedup, DISCARDED.md
- `5fafb7` 2026-04-06 — fix(garden): mandatory 'What was tried' heading in gotcha template
- `1bfb51` 2026-04-06 — feat(garden): add REVISE workflow for enriching existing entries
- `07d926` 2026-04-06 — feat(garden): bundle validate_garden.py with skill; update SKILL.md reference
- `8cd915` 2026-04-06 — feat(garden): add validator run to MERGE success criteria
- `b1c929` 2026-04-06 — docs: add project blog entry 2026-04-06-03-garden-remembers-itself

---

### Issue #25: "Build write-blog skill" [enhancement]
Scopes: write-blog, project-blog
Period: 2026-04-04 → 2026-04-06
Commits:
- `0077bc` 2026-04-04 — feat: add project-blog skill — living R&D diary
- `5a1184` 2026-04-04 — feat: project blog (4 entries) + revised project-blog skill
- `57b775` 2026-04-05 — fix: project-blog is for publication, not private — clarify pipeline with write-blog-post
- `b5ca4d` 2026-04-05 — feat: project-blog loads personal writing style guide before drafting
- `1a1842` 2026-04-05 — fix: project-blog = writing, write-blog-post = publishing
- `2582cf` 2026-04-05 — rename: project-blog → write-blog, write-blog-post → publish-blog
- `514ec1` 2026-04-05 — feat: write-blog RETROSPECTIVE mode — blog all work to date
- `fe0a2e` 2026-04-05 — fix: update write-blog command — fix stale skill name and add RETROSPECTIVE trigger
- `15f0e8` 2026-04-05 — feat: write-blog command is intent-driven — blank=retrospective, context=single entry
- `6f63234` 2026-04-05 — feat(write-blog): add RETROSPECTIVE decision flowchart
- `8e94d8` 2026-04-05 — fix(write-blog): resolve 9 consistency issues from systematic review
- `773184` 2026-04-05 — fix(write-blog): replace vague Next: pitfall with don't use Next: at all
- `3e33a6` 2026-04-05 — feat(write-blog): align heading guidance with style guide
- `c4046e` 2026-04-05 — refactor: revise all 5 blog entries to match writing style guide
- `9c2a5c` 2026-04-06 — feat(write-blog): four-layer writing architecture
- `4caced` 2026-04-06 — fix(write-blog): note series exception to no-Next: rule
- `0cee62` 2026-04-06 — fix(write-blog): address systematic review findings
- `00efa7` 2026-04-06 — feat(write-blog): always use two-digit sequence number in filenames
- `26681f` 2026-04-06 — refactor: rename blog entries to YYYY-MM-DD-NN-title.md convention
- `23900` 2026-04-06 — fix(write-blog): move CLAUDE.md style guide check to Step 0c — gate not offer
- `155f86` 2026-04-06 — docs: add project blog entry 2026-04-06-02-writing-rules-get-teeth
- `f1ba7c` 2026-04-06 — feat(write-blog): chain to update-claude-md on first blog entry
- `918ae1` 2026-04-06 — feat(write-blog): add image guidance — screenshots, generated, web search, index
- `88cc7f` 2026-04-06 — feat: propagate writing style guide requirement to all CLAUDE.md files
- `2769c7` 2026-04-06 — feat: enforce style guide as hard gate in write-blog and CLAUDE.md
- `e50dd4` 2026-04-06 — docs: add project blog entry 2026-04-06-writing-about-itself
- `e2b059` 2026-04-04 — fix: close all consistency gaps found in audit
- `b76184` 2026-04-05 — fix: garden sweep in session-handoff is done by handoff itself, not by garden

---

### Issue #26: "Add session handoff skill" [enhancement]
Scopes: session-handoff
Period: 2026-04-04 → 2026-04-06
Commits:
- `4e13db` 2026-04-04 — feat: add session-handoff skill + log holistic memory architecture idea
- `e33c93` 2026-04-04 — refactor: session-handoff — delta-first writing + git history as archive
- `42336` 2026-04-02 — docs: add session handoff document for health/refine trial
- `58463` 2026-04-02 — docs: update session handoff for health/refine trial session
- `119ea5` 2026-04-05 — feat: session-handoff always performs garden sweep before writing handover
- `268eeb` 2026-04-05 — fix(session-handoff): correct wrap checklist order — garden→claude-md→snapshot→blog
- `fcccce` 2026-04-05 — feat(session-handoff): add session wrap checklist before handover
- `9881f5` 2026-04-06 — docs: session handover 2026-04-06
- `aebc39` 2026-04-06 — docs: session handover 2026-04-06
- `84b40c` 2026-04-06 — docs: session handover 2026-04-06

---

### Issue #27: "Add retrospective issue mapping skill" [enhancement]
Scopes: retro-issues, plans
Period: 2026-04-06
Commits:
- `9fe442` 2026-04-06 — docs(plans): add retro-issues implementation plan
- `9b833c` 2026-04-06 — feat(retro-issues): add retrospective git history to epics/issues skill
- `0a512d` 2026-04-06 — fix(retro-issues): fix classifier bugs and add scope-based clustering
- `4794e1` 2026-04-06 — fix(retro-issues): add epic coherence gates — max children and scope spread
- `21345d` 2026-04-06 — feat(retro-issues): make ticket grouping primary goal; add related-scope merging
- `0e5b99` 2026-04-06 — feat(retro-issues): all commits get tickets; narrow trivial exclusions; full commit lists in report

---

## Excluded Commits (no ticket — trivial only)

This table should be short. If it's long, reconsider the classification.

| Hash | Date | Message | Reason |
|------|------|---------|--------|
| `1a6b96` | 2026-03-31 | docs: convert all Graphviz diagrams to Mermaid format | Whitespace/formatting conversion — matches "convert to Mermaid format" example |
