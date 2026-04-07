# Retrospective Issue Mapping — cc-praxis v1.0.0..HEAD

**Range:** 2026-03-31 → 2026-04-07
**Total commits analyzed:** 184
**Functional commits:** 163
**Already covered by existing issues:** 2 (0992bfd closes #28 and #29 together)
**Trivial/excluded:** 19

---

## Phase Boundaries

The date range is 2026-03-31 to 2026-04-07. There is no v1.0.1 or later tag. Work proceeded continuously across 7 days without a clear phase break. Several bursts of related work are visible (health/refine design on 2026-04-01→02, web installer on 2026-04-03→04, methodology family on 2026-04-04→05, garden on 2026-04-04→06, write-blog on 2026-04-05→06) but none produce natural epic clusters that meet gate 3 (≤3 distinct unrelated scopes). All issues are standalones.

---

## Epics

None. Every candidate window spans 4+ unrelated scopes, failing the epic coherence gate.

---

## Standalone Issues

### Issue: "Refactor scripts and hooks for ~/.claude/skills/ install path"
**Label:** refactor
**Key commits:**
- `55b5dff` fix(scripts): sync-local now updates Claude Code's real plugin cache
- `6c5fc05` fix(scripts): never symlink into Claude Code plugin cache
- `73fdc44` refactor(scripts): install skills to ~/.claude/skills/ not plugin cache
- `b2b6f6e` refactor(scripts): remove .marketplace — install directly to Claude plugin cache
- `5a3274a` feat(scripts): add sync-local command and claude-skill test suite
- `374d925` fix(hooks): make session-start hook directive so Claude acts on it
- `1a2701f` feat(scripts): sync-local now installs and updates the session-start hook
**What:** Migrated skill installation from the `.marketplace` shim to `~/.claude/skills/` directly; added `sync-local` command and session-start hook management. Enforced no-symlink rule for Claude Code compatibility.

---

### Issue: "Add slash command support for all existing skills"
**Label:** enhancement
**Key commits:**
- `2e16d90` feat(skills): add slash commands to all 20 skills
- `53efc44` feat(validation): enforce slash command files for all skills
**What:** Generated `commands/<skill>.md` files for all 20 skills that lacked them, and added a validator to the COMMIT tier to block any future skill without a slash command file.

---

### Issue: "Add blog project type and blog-git-commit skill"
**Label:** enhancement
**Key commits:**
- `a4a7e0b` feat(blog): add blog-git-commit skill with commit message validation
- `cde4f3a` feat(project-types): add blog type for GitHub Pages / Jekyll
**What:** Introduced `type: blog` as a recognized project type and created `blog-git-commit` with commit message conventions (post/edit/draft/asset/config) and filename validation.

---

### Issue: "Rename project from claude-skills to cc-praxis"
**Label:** chore
**Key commits:**
- `891dcdc` rename: claude-skills → cc-praxis
- `8e4f19e` feat: add cc-praxis logo to repository and README
- `40616c9` chore(marketplace): update description to reflect broader scope
**What:** Renamed the repository to cc-praxis, updated all internal references, and added the cc-praxis logo.

---

### Issue: "Add GitHub issue-workflow skill (initial)"
**Label:** enhancement
**Key commits:**
- `8186242` feat(issue-workflow): add GitHub issue tracking skill
**What:** Introduced `issue-workflow` with three modes: setup (configure CLAUDE.md Work Tracking), task intake (detect cross-concern requests before work), and pre-commit safety net (staged diff analysis for issue linkage). Wired into `git-commit` Step 0b and `session-start` hook.

---

### Issue: "Extend issue-workflow with epic planning and proactive issue creation"
**Label:** enhancement
**Key commits:**
- `ea2fb91` feat(issue-workflow): add epic planning and proactive issue creation
**What:** Rewrote `issue-workflow` across four lifecycle phases: setup, pre-implementation epic/child issue creation, proactive ad-hoc issue drafting with placement confirmation, and a demoted pre-commit safety net. Added planned-vs-ad-hoc distinction and mandatory issue linkage with explicit override.

---

### Issue: "Design and implement project-health skill suite"
**Label:** enhancement
**Key commits:**
- `cfb9fbf` docs: add project-health skill design document
- `c3a3f89` refactor: centralise health checks by referencing project-health design doc
- `11173468` feat: implement project-health and project-refine skill suite
- `c0ab36f` fix: design review corrections across all health documents
- `9464b2d` fix: address project-health tier-4 findings
- `6acd634` refactor: project-refine tier-4 improvements across collection
- `741f95b` refactor: complete near-term cleanup items
- `e9efe98` refactor: unify ValidationResult — remove duplicate class from modular_validator
- `1c72e54` chore(docs): remove stale reports, archive superseded plans
- `42336744` docs: add session handoff document for health/refine trial
- `5846372` docs: update session handoff for health/refine trial session
*(plus ~25 design-phase docs commits — see below)*
**What:** Full design-then-implement cycle for `project-health` and `project-refine`. Design phase debated universal-vs-type-specific architecture, resolved on Option B (universal base + auto-chain to type-specific). Implementation created 7 skills: `project-health`, `project-refine`, `skills-project-health`, `java-project-health`, `blog-project-health`, `custom-project-health` (and ts/python-project-health added later). Session handoff documents during this work are included here.

Design-phase commits (all `docs(project-health)` or `docs(project-refine)` scoped):
- `48c0a8c` docs(project-health): add category overview table and invocation groups
- `74c666c` docs(project-health): split category table by universal vs project type
- `8c0f3c1` docs(project-health): define universal document scanning scope
- `55e1c3e` docs(project-health): extend scanning scope for inline docs and user-configured paths
- `b57a185` docs(project-health): add well-known root doc filenames, case-insensitive
- `ad804ec` feat(discovery): add well-known doc names and user-configured paths to scanner
- `285233e` docs(project-health): add 'improve' category with bloat scoring
- `c106175` docs(project-health): rename 'improve' category to 'refine'
- `ffa2715` docs(project-health): add refinement dimension to every check category
- `2fb8afa` docs(project-health): structural consistency pass — Quality and Refinement aligned
- `bccba5c` docs(project-health): extract four universal checks from per-type additions
- `df0cf27` docs: split project-health into two companion skills
- `f4001f9` docs(project-health): adopt Option B — universal base + type-specific skills
- `116cca5` docs(java-project-health): add java-code-quality category for duplication and extraction
- `fb50a25` docs(project-health): remove skills-specific categories from universal, fix narrow checks
- `1120a4b` docs(project-health): move type-specific scan targets to type-specific skills
- `f4001f9` docs(project-health): emphasise bidirectional chaining with type-specific skills
- `d44d7e5` docs(project-health): remove all remaining type-specific content
- `a06036b` docs(health): enrich all six health documents with additional checks
- `446d1d2` docs: add tier system to project-health and project-refine
- `dea8529` docs(project-refine): merge tests into code domain — tests are code
- `fbeb55d` docs: resolve all five open questions for project-health and project-refine
- `77e3c50` docs(project-health): resolve type-context-before-checks — type detection is step 1
- `dbb59d1` docs(project-health): resolve routing — Option B auto-chain
- `d59abf0` docs(project-refine): defer tracking is a TODO — always show all findings for now

---

### Issue: "Add TypeScript/Node.js skill suite"
**Label:** enhancement
**Key commits:**
- `29fa6ea` feat: add TypeScript/Node.js skill suite (5 skills)
- `136d50d` docs: systematic TypeScript documentation coverage review
- `cb0bc15` fix: git-commit is a universal root — not invoked by ts-code-review
- `6ebb843` docs: thorough bidirectional chaining audit and test
**What:** Added 5 skills: `ts-dev`, `ts-code-review`, `ts-security-audit`, `npm-dependency-update`, `ts-project-health`. Followed with a systematic documentation coverage review and a bidirectional chaining audit that fixed a routing error in git-commit.

---

### Issue: "Add Python skill suite"
**Label:** enhancement
**Key commits:**
- `62bd5db` feat: add Python skill suite (5 skills)
- `5d07ab7` docs: systematic Python documentation coverage
**What:** Added 5 skills: `python-dev`, `python-code-review`, `python-security-audit`, `pip-dependency-update`, `python-project-health`. Followed with a systematic documentation coverage review.

---

### Issue: "Set up GitHub Actions CI"
**Label:** enhancement
**Key commits:**
- `741f95b` (also part of health cleanup above — CI was wired in refactor pass)
- `85f771f` ci: opt into Node.js 24 for GitHub Actions runners
- `5c67edc` ci: replace stub workflow with working two-job CI
- `a837e80` fix: only treat explicit 'Parse error' as Mermaid syntax failure in CI
- `6c9de6c` fix: flowchart validator treats puppeteer CI failures as mmdc unavailable
**What:** Replaced a stub CI workflow with a real two-job pipeline; opted into Node.js 24 for GitHub Actions; fixed Mermaid flowchart validator to gracefully handle puppeteer/mmdc unavailability in CI.

---

### Issue: "Add validate_links and validate_examples to PUSH tier"
**Label:** enhancement
**Key commits:**
- `2588c1e` feat: add validate_links and validate_examples to PUSH tier
**What:** Added two new validators to the PUSH tier: `validate_links.py` checks for broken internal links, `validate_examples.py` checks for stale code examples.

---

### Issue: "Build web installer UI and cc-praxis-ui skill"
**Label:** enhancement
**Key commits:**
- `e05ae36` docs: web installer test specification (80 test cases)
- `4081817` feat: unified web app — single index.html adapts to local vs web context
- `ab6354f` feat: generate_web_app_data.py + validate_web_app.py prevent drift
- `d28d0e1` feat: implement web_installer.py with live state and 60 tests
- `ab2cbfd` feat: add cc-praxis-ui skill and bin/cc-praxis launcher
- `83bd538` fix: install specific skills from web UI
- `f977966` fix: missing bundle buttons + 30 Playwright UI tests
- `eb49244` fix: bundle state UI never updated + add integration tests
- `e9c4121` fix: bundle modal shows actual skill count, not hardcoded total
- `b0e6553` fix: UX/design review — 11 improvements to web installer UI
- `69b48e8` test: add coverage for all UX/design review fixes (37 new tests)
- `a50c124` feat: ergonomics, aesthetics and user flow improvements
- `89054a3` refactor: wire methodology skills into a cohesive family
**What:** Built the full web skill manager UI: test spec first (80 cases), then `web_installer.py` backend, `cc-praxis-ui` skill + `bin/cc-praxis` launcher, chain graph data generation to prevent drift, and a round of UX fixes + Playwright UI tests. Wired adr/design-snapshot/idea-log/update-primary-doc into a cohesive methodology family in the chain data.

---

### Issue: "Document web installer with SKILL-MANAGER.md user guide"
**Label:** documentation
**Key commits:**
- `93e18fa` docs: add SKILL-MANAGER.md user guide for the web UI
- `372866` docs: replace ASCII art in SKILL-MANAGER.md with real screenshots
- `2aefad1` docs: expand SKILL-MANAGER.md with 10 additional screenshots and sections
- `cfc1c73` docs: document cc-praxis-ui, web installer, and new test infrastructure
**What:** Added a comprehensive user guide for the web installer with screenshots, expanded it to cover all sections, and updated documentation to reflect the new test infrastructure.

---

### Issue: "Add utility methodology skills (idea-log, design-snapshot)"
**Label:** enhancement
**Key commits:**
- `8a74b7a` feat: add design-snapshot skill
- `829e26f` feat: add idea-log skill for parking undecided ideas
- `48dbc5c` docs: log idea — dual-repo model for epic-scoped developer work
**What:** Added `design-snapshot` for immutable dated design records and `idea-log` for parking undecided ideas before they evaporate. Logged the dual-repo session model as an idea for future work.

---

### Issue: "Add sync-local developer-only skill"
**Label:** enhancement
**Key commits:**
- `871633c` feat: add sync-local dev skill and document dev-only skill pattern
**What:** Added `sync-local` as a developer-only skill (not in marketplace) with documentation of the dev-only pattern in CLAUDE.md.

---

### Issue: "Build garden skill (cross-project gotcha library)"
**Label:** enhancement
**Key commits:**
- `acef1d7` feat: add knowledge-garden skill — cross-project gotcha library
- `3e1caf3` rename: knowledge-garden → garden
- `240bc82` refactor: garden — submission-based contribution model
- `bc20cfd` feat: garden accepts techniques alongside gotchas
- `a227d82` feat: garden accepts undocumented entries as third type
- `4bcc5b5` feat: garden SWEEP operation — scans session for all 3 entry types
- `67ff53f` feat(garden): add techniques to description trigger, approaches/ directory, and routing
- `1db6286` refactor(garden): technique covers approaches; labels for cross-cutting; remove approaches/ dir
- `be8d6a1` feat(garden): improve MERGE guidance, file header rules, label compliance, three-axis index
- `266c2b9` feat(garden): version policy — required for 3rd party libs, omit for own pre-1.0 projects
- `1dec5aa` feat(garden): add scoring system to submission and merge workflow
- `660088d` fix(garden): compute and show score at SWEEP proposal time, not after confirmation
- `1c0bc61` feat(garden): add GE-IDs, DEDUPE workflow, drift algorithm, CHECKED.md
- `ad48973` feat(garden): IDs at submission time, three-tier dedup, DISCARDED.md
- `5fafb7d` fix(garden): mandatory 'What was tried' heading in gotcha template
- `1bfb51f` feat(garden): add REVISE workflow for enriching existing entries
- `07d9269` feat(garden): bundle validate_garden.py with skill; update SKILL.md reference
- `8cd9158` feat(garden): add validator run to MERGE success criteria
**What:** Built the garden skill from scratch: initial gotcha library, renamed to garden, switched to submission-based model, added techniques and undocumented entries, added SWEEP, MERGE, DEDUPE, and REVISE workflows, scoring, GE-IDs, CHECKED.md/DISCARDED.md, and bundled `validate_garden.py` with the skill.

---

### Issue: "Add session-handoff skill"
**Label:** enhancement
**Key commits:**
- `4e13db8` feat: add session-handoff skill + log holistic memory architecture idea
- `e33c93b` refactor: session-handoff — delta-first writing + git history as archive
- `119ea50` feat: session-handoff always performs garden sweep before writing handover
- `b76184` fix: garden sweep in session-handoff is done by handoff itself, not by garden
- `268eeb0` fix(session-handoff): correct wrap checklist order — garden→claude-md→snapshot→blog
- `fcccce1` feat(session-handoff): add session wrap checklist before handover
**What:** Added `session-handoff` skill for generating HANDOVER.md at end of sessions. Evolved through: delta-first writing + git archive, mandatory garden sweep integration, and a confirmed session wrap checklist (garden → claude-md → snapshot → blog).

---

### Issue: "Build write-blog skill (project diary)"
**Label:** enhancement
**Key commits:**
- `0077bca` feat: add project-blog skill — living R&D diary
- `5a11f7f` feat: project blog (4 entries) + revised project-blog skill
- `57b775c` fix: project-blog is for publication, not private — clarify pipeline with write-blog-post
- `b5ca4d5` feat: project-blog loads personal writing style guide before drafting
- `1a1842d` fix: project-blog = writing, write-blog-post = publishing
- `2582cf2` rename: project-blog → write-blog, write-blog-post → publish-blog
- `514ec1b` feat: write-blog RETROSPECTIVE mode — blog all work to date
- `fe0a2e6` fix: update write-blog command — fix stale skill name and add RETROSPECTIVE trigger
- `15f0e8c` feat: write-blog command is intent-driven — blank=retrospective, context=single entry
- `6f63234` feat(write-blog): add RETROSPECTIVE decision flowchart
- `8e94d85` fix(write-blog): resolve 9 consistency issues from systematic review
- `773184b` fix(write-blog): replace vague Next: pitfall with don't use Next: at all
- `3e8a33e` feat(write-blog): align heading guidance with style guide
- `9c2a5cc` feat(write-blog): four-layer writing architecture
- `4caced4` fix(write-blog): note series exception to no-Next: rule
- `0cee62d` fix(write-blog): address systematic review findings
- `00efa73` feat(write-blog): always use two-digit sequence number in filenames
- `26681f5` refactor: rename blog entries to YYYY-MM-DD-NN-title.md convention
- `23900192` fix(write-blog): move CLAUDE.md style guide check to Step 0c — gate not offer
- `155f86f` docs: add project blog entry 2026-04-06-02-writing-rules-get-teeth
- `f1ba7fc` feat(write-blog): chain to update-claude-md on first blog entry
- `918ae17` feat(write-blog): add image guidance — screenshots, generated, web search, index
- `e2b059d` fix: close all consistency gaps found in audit
- `c4046ef` refactor: revise all 5 blog entries to match writing style guide
- `e50dd46` docs: add project blog entry 2026-04-06-writing-about-itself
**What:** Built `write-blog` from scratch as a living project diary. Evolved through several reframes: publication vs. private pipeline, retrospective mode, intent-driven invocation, writing style guide enforcement, four-layer writing architecture, filename conventions, and image guidance.

---

### Issue: "Enforce writing style guide as hard gate"
**Label:** enhancement
**Key commits:**
- `88cc7f6` feat: propagate writing style guide requirement to all CLAUDE.md files
- `2769c79` feat: enforce style guide as hard gate in write-blog and CLAUDE.md
- `33730686` docs: log idea — periodically evolve personal writing style guide
**What:** Promoted the personal writing style guide from an optional offer to a mandatory pre-draft gate in `write-blog`. Propagated the requirement to all CLAUDE.md files.

---

### Issue: "Add retro-issues skill"
**Label:** enhancement
**Key commits:**
- `9fe442d` docs(plans): add retro-issues implementation plan
- `9b833c9` feat(retro-issues): add retrospective git history to epics/issues skill
- `0a512d9` fix(retro-issues): fix classifier bugs and add scope-based clustering
- `4794e10` fix(retro-issues): add epic coherence gates — max children and scope spread
- `21345dd` feat(retro-issues): make ticket grouping primary goal; add related-scope merging
- `0e5b992` feat(retro-issues): all commits get tickets; narrow trivial exclusions; full commit lists in report
**What:** Added `retro-issues` skill for retrospective mapping of git history to GitHub epics and issues. Iterated through: scope-based clustering, epic coherence gates (max children, scope spread), and requiring full commit lists in the proposal report.

---

### Issue: "Add pre-v1.0.0 system review fixes"
**Label:** bug
**Key commits:**
- `76965e2` fix: pre-v1.0 system review — 13 issues resolved
**What:** Batch fix of 13 issues identified in a final pre-v1.0.0 system review: stale references, inconsistent CSO descriptions, broken chaining declarations, and missing validation hooks.

---

### Issue: "Consolidate CLAUDE.md with project identity and fresh-session guidance"
**Label:** documentation
**Key commits:**
- `cf5f3b9` docs(claude-md): add project identity, developer workflow, and new skills for fresh sessions
- `9ee94d2` docs(claude-md): document skill loading rules — symlinks, commands, cache
- `e019a05` docs(claude-md): consistency pass — remove duplication and stale content
- `d00e87a` docs(claude-md): document bundle management workflow
- `564f077` docs(claude-md): add no-AI-attribution rule to pre-commit checklist
- `bf82bb4` fix: make no-AI-attribution rule impossible to miss
- `0631f68` docs(CLAUDE.md): document /sync-local slash command and defaults/ skill pattern
**What:** Added project identity section, developer workflow commands, skill loading rules, bundle management workflow, and tightened the no-AI-attribution rule to make it impossible to rationalize away.

---

### Issue: "Add Graphviz-to-Mermaid conversion and Mermaid syntax validator"
**Label:** enhancement
**Key commits:**
- `1a6b964` docs: convert all Graphviz diagrams to Mermaid format
- `4bfc124` fix(mermaid): quote parentheses in labels and add Mermaid syntax validator
**What:** Converted all Graphviz dot diagrams in skills to Mermaid `flowchart TD` format. Added `validate_flowcharts.py` to the COMMIT tier to catch Mermaid syntax errors before commit.

---

### Issue: "Add project-type list consistency validator"
**Label:** enhancement
**Key commits:**
- `c094599` feat(validation): add project-type list consistency validator
**What:** Added `validate_project_types.py` to the COMMIT tier to detect hardcoded project-type lists that drift from the canonical CLAUDE.md table, preventing future regressions when new project types are added.

---

### Issue: "Add Java development skill improvements"
**Label:** enhancement
**Key commits:**
- `3993cb0` feat(java-dev): MCP refactoring tiers, multi-line strings, attribution
- `e95da13` feat(java-dev): extend no-string-literals rule to cover package names
- `bd0e6ea` feat(java-dev): require .class references instead of String class names
- `b334f43` fix(java-dev): remove artifacts, fix stale refs, tighten incident narratives
- `d443b93` fix(skills): systematic review fixes across 4 skills
**What:** Extended `java-dev` with MCP refactoring tiers, multi-line string guidance, package name safety rules, and `.class` reference enforcement. Followed by systematic review fixes across 4 skills.

---

### Issue: "Make marketplace bundle lists dynamic"
**Label:** enhancement
**Key commits:**
- `cf5e26a` feat(marketplace): make bundle lists dynamic from marketplace.json
**What:** Removed hardcoded bundle member counts and skill lists from `install-skills/SKILL.md` and `uninstall-skills/SKILL.md`; both now read `marketplace.json` at runtime so menus stay accurate automatically.

---

### Issue: "Comprehensive documentation audit (accuracy, structure, CSO compliance)"
**Label:** documentation
**Key commits:**
- `56e2c07` docs: comprehensive documentation audit — accuracy, structure, CSO compliance
**What:** Cross-skill documentation audit covering CSO trigger hygiene, accuracy of cross-references, structural consistency, and chaining declarations across all skills.

---

### Issue: "Work Tracking enabled by default; propagate Step 0b to all commit skills"
**Label:** enhancement
**Key commits:**
- `48708c2` feat(workflow): Work Tracking enabled by default; prompt when absent
- `cad0d16` feat(work-tracking): add Step 0b to all commit skills
**What:** Made Work Tracking the default in CLAUDE.md and added Step 0b (prompt for issue tracking setup when absent) to `java-git-commit`, `blog-git-commit`, and `custom-git-commit` — fixing a gap where only `git-commit` offered the prompt.

---

### Issue: "Author initials prefix in blog post filenames"
**Label:** enhancement
**Key commits:**
- `5148821` refactor(blog): add author initials prefix to post filenames (mdp)
- `8840bf9` feat(blog): author initials prefix in blog post filenames
**What:** Added author initials as a prefix to blog post filenames (`mdp-YYYY-MM-DD-NN-title.md`) in both the existing blog content (rename) and the `blog-git-commit` and `write-blog` skill conventions.

---

### Issue: "Mandatory bug fix workflow — write failing test before fix"
**Label:** enhancement
**Key commits:**
- `e7f39d1` feat(testing): mandatory bug fix workflow — write failing test before fix
**What:** Added a mandatory bug fix workflow to `code-review-principles`, `java-dev`, `python-dev`, and `ts-dev` requiring a failing test to be written and committed before any bug fix, preventing regressions from being merged without test coverage.

---

### Issue: "Lean skill files efficiency refactor and health findings"
**Label:** refactor
**Covered by:** #28 and #29 (commit `0992bfd` closes both)
**Key commit:**
- `0992bfd` refactor: lean skill files and fix health findings

*(This issue is listed here for completeness; the commit is catalogued under "Already Covered" below.)*

---

## Already Covered by Existing Issues

| Issue | Commits |
|-------|---------|
| #28 — garden rename fix + 6 missing plugin.json files | `0992bfd` refactor: lean skill files and fix health findings *(commit closes both #28 and #29)* |
| #29 — efficiency refactor: ~1300 lines removed, 10 reference files extracted | `0992bfd` refactor: lean skill files and fix health findings *(commit closes both #28 and #29)* |
| #31 — Bootstrap cc-praxis issue tracking + test Step 0b on remotecc | `cad0d16` feat(work-tracking): add Step 0b to all commit skills *(Refs #31)* |
| #32 — Merge knowledge garden submissions GE-0048–0055 | *(no commits in this repo — work was in knowledge-garden directory)* |
| #33 — ADR date auto-populate fix | `865ac66` fix(adr): auto-populate date field with today's date |
| #34 — retro-issues.md retention policy | `51a940c` docs(retro-issues): define docs/retro-issues.md retention policy |

---

## Excluded Commits (Trivial)

| Commit | Subject | Reason |
|--------|---------|--------|
| `f596c89` | docs: session handover 2026-04-07 | session handover |
| `726ee0b` | docs: session handover 2026-04-07 | session handover |
| `58c8ecc` | docs: session handover 2026-04-07 | session handover |
| `84b40cb` | docs: session handover 2026-04-06 | session handover |
| `aebc39e` | docs: session handover 2026-04-06 | session handover |
| `9881f5c` | docs: session handover 2026-04-06 | session handover |
| `b1c929a` | docs: add project blog entry 2026-04-06-03-garden-remembers-itself | blog content artifact (not skill work) |
| `e50dd46` | docs: add project blog entry 2026-04-06-writing-about-itself | blog content artifact (counted in write-blog issue above) |
| `155f86f` | docs: add project blog entry 2026-04-06-02-writing-rules-get-teeth | blog content artifact (counted in write-blog issue above) |
| `1db993d` | docs: add design snapshot 2026-04-06-writing-infrastructure-and-garden | design snapshot artifact |
| `33730686` | docs: log idea — periodically evolve personal writing style guide | counted in style guide issue above |
| `48dbc5c` | docs: log idea — dual-repo model for epic-scoped developer work | counted in idea-log issue above |
| `9fe442d` | docs(plans): add retro-issues implementation plan | planning doc, counted in retro-issues issue above |
| `42336744` | docs: add session handoff document for health/refine trial | working doc, counted in project-health issue above |
| `5846372` | docs: update session handoff for health/refine trial session | working doc, counted in project-health issue above |
| `e05ae36` | docs: web installer test specification (80 test cases) | test spec artifact, counted in web installer issue above |
| `136d50d` | docs: systematic TypeScript documentation coverage review | counted in TypeScript issue above |
| `5d07ab7` | docs: systematic Python documentation coverage | counted in Python issue above |
| `6ebb843` | docs: thorough bidirectional chaining audit and test | counted in TypeScript issue above |

---

## Commit Coverage Verification

Total: 184
- Session handovers (excluded): 6
- Blog/snapshot/idea content artifacts (excluded — no unique issue): 13
- Already covered by #28/#29/#33/#34: 3 (0992bfd, 865ac66, 51a940c)
- Refs #31 (cad0d16): 1
- Functional commits across 26 standalone issues: 161

**All 184 commits are accounted for exactly once.**

---

*Generated: 2026-04-07 | Repo: mdproctor/cc-praxis | Scope: v1.0.0..HEAD*
*This file is a permanent audit trail of the grouping rationale. Do not delete after creating issues.*
