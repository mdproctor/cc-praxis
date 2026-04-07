# project-health — Universal Check Categories

Full quality and refinement checklists for all 12 universal check categories.
Referenced by `project-health/SKILL.md` Step 5 and all type-specific sub-skills.

---

## Tier System

| Tier | What runs |
|------|-----------|
| 1 (`--commit`) | `validate_all.py --tier commit` only |
| 2 (`--standard`) | Universal quality checks only |
| 3 (`--prerelease`) | Universal + type-specific quality checks |
| 4 (`--deep`) | All of tier 3 + refinement questions |

Type-specific categories run at tier 3+. Augmentations to universal categories
apply at the same tier as the universal check.

---

## Severity Scale

| Severity | Meaning |
|----------|---------|
| **CRITICAL** | Correctness failure — should block release |
| **HIGH** | Should fix before shipping |
| **MEDIUM** | Worth fixing in next session |
| **LOW** | Nice to fix, low urgency |

---

### `docs-sync` — Documentation Accuracy

**Quality**
- [ ] Code behaviour matches what docs describe
- [ ] No "planned" / "not yet implemented" language for things that already exist
- [ ] Component and artifact counts are correct everywhere stated
- [ ] Version numbers consistent across all places they appear
- [ ] URLs and external references are correct and reachable
- [ ] No stale "TODO" or "coming soon" references for completed work
- [ ] Release status language matches actual state
- [ ] Temporal claims still accurate ("as of Q1 2026", "in the last 6 months")
- [ ] Code examples and output samples match what the code actually produces
- [ ] Environment variable names, config keys, and file paths match actual source

**Refinement (tier 4 only)**
- [ ] Over-explained sections where the code is self-evident?
- [ ] Detail level appropriate for intended audience?
- [ ] Could prose be replaced with a table or example easier to scan?
- [ ] Sections whose purpose overlaps enough to merge?

---

### `consistency` — Internal Consistency

**Quality**
- [ ] No contradictions between any two documents on the same topic
- [ ] No duplicate information that could drift (same content in 2+ places)
- [ ] Section naming conventions followed consistently
- [ ] Recurring structural elements use consistent formatting
- [ ] Severity levels (CRITICAL/WARNING/NOTE) used consistently
- [ ] Terminology consistent throughout (e.g. "invoke" not mixed with "call")
- [ ] Same concept named the same way across all audience levels

**Refinement (tier 4 only)**
- [ ] Scattered terminology that could be unified in a glossary?
- [ ] Sections saying the same thing in different words that should merge?
- [ ] Inconsistent formatting that adds cognitive load?

---

### `logic` — Workflow Logic & UX

**Quality**
- [ ] No workflow step references a script or file that doesn't exist
- [ ] No workflow step requires an external tool without verifying it's installed
- [ ] Hook outputs are directive (ACTION REQUIRED) not just informational
- [ ] Hook doesn't fire on non-git directories
- [ ] No workflow blocks progress without giving the user a way forward
- [ ] Error messages include recovery steps
- [ ] No redundant checks (same thing checked twice in same flow)
- [ ] Chained workflows don't create infinite loops
- [ ] Exit codes consistent and documented
- [ ] Workflow steps requiring user judgment specify clear decision criteria
- [ ] Ordered workflows document what happens if steps are skipped or reordered

**Refinement (tier 4 only)**
- [ ] Steps that could be combined without losing clarity?
- [ ] Prompts or confirmations asked more times than necessary?
- [ ] Multi-step flows reducible by inferring answers from context?
- [ ] Technical error messages where plain language would serve better?

---

### `config` — Project Configuration Health

**Quality**
- [ ] CLAUDE.md exists and has `## Project Type`
- [ ] Project type is one of: skills, java, blog, custom, generic
- [ ] Required primary artifacts for the project type exist
- [ ] `## Commit Messages` section present (no-AI-attribution rule)
- [ ] `## Work Tracking` present if team collaboration is needed (advisory)

**Refinement (tier 4 only)**
- [ ] CLAUDE.md overloaded with sections that could be removed or consolidated?
- [ ] Sections so rarely changed they could be simplified?
- [ ] Sync Rules table (type: custom) expressible more concisely?

---

### `security` — Security & Safety

**Quality**
- [ ] No hardcoded tokens, passwords, or API keys in any file
- [ ] Shell scripts quote variables to prevent word splitting
- [ ] No `rm -rf` without explicit path validation
- [ ] No `eval` of untrusted input
- [ ] All executable scripts have correct permissions
- [ ] No secrets in git history (check recent commits)
- [ ] Scripts validate inputs before acting on them
- [ ] External tool dependencies documented or checked before use
- [ ] Scripts that write files check the target directory exists first
- [ ] Relative paths in scripts work regardless of calling directory

**Refinement (tier 4 only)**
- [ ] Scripts doing more than necessary (smaller attack surface)?
- [ ] Complex shell logic replaceable with easier-to-audit Python?

---

### `release` — Release Readiness

*Run at tier 3+ or when explicitly requested.*

**Quality**
- [ ] No SNAPSHOT, dev, or alpha markers in release artifacts
- [ ] All component versions consistent and intentional
- [ ] GitHub labels set up for release note generation
- [ ] `gh release create --generate-notes` would produce meaningful output
- [ ] No obviously incomplete components (stubs, placeholders, empty sections)
- [ ] All tests passing
- [ ] Release notes reference the issues or PRs being released
- [ ] Release notes don't claim fixes/features not in this release

**Refinement (tier 4 only)**
- [ ] Would generated release notes tell a coherent story?
- [ ] GitHub issue titles good enough to serve as changelog entries?
- [ ] Could versioning strategy be simplified?

---

### `user-journey` — End User Experience

*Run at tier 3+ or when explicitly requested.*

**Quality**
- [ ] Getting started path documented and works end-to-end
- [ ] First meaningful action is guided
- [ ] Setup prompts are clear and skippable where optional
- [ ] Error messages explain what went wrong and how to recover
- [ ] No dead ends — every failure state has a next step
- [ ] Entry points (commands, slash commands, scripts) work as documented
- [ ] Getting started validated from a fresh environment
- [ ] Documented error recovery steps actually resolve the stated error

**Refinement (tier 4 only)**
- [ ] Required setup steps that could be inferred or automated?
- [ ] Onboarding sequence longer than necessary?
- [ ] Optional prompts surfaced too early in the flow?

---

### `git` — Repository State

*Run when explicitly requested or `--deep`.*

**Quality**
- [ ] No uncommitted changes that should be committed
- [ ] No stale git worktrees
- [ ] Tags consistent with marketplace/package versions (for release)
- [ ] No merge conflict markers in tracked files
- [ ] Branch is up to date with remote

**Refinement (tier 4 only)**
- [ ] Branching strategy more complex than team size justifies?
- [ ] Branches or worktrees that outlived their purpose?

---

### `primary-doc` — Primary Document Accuracy

**Quality** (apply to the correct artifact for the detected project type)
- [ ] Primary document exists
- [ ] Content accurately describes what the project currently does
- [ ] No sections describe features or workflows that no longer exist
- [ ] Referenced files, paths, and modules within the document still exist
- [ ] Terminology matches what is actually used in the codebase

**Refinement (tier 4 only)**
- [ ] Appropriate size, or should it be split into focused modules?
- [ ] Sections so rarely updated they've become stale noise?
- [ ] Structure could be reorganised to match how readers navigate it?

---

### `artifacts` — Required Artifacts Exist

**Quality** (apply to the correct artifact list for the detected project type)
- [ ] All required files and directories exist
- [ ] Required configuration files are present and parseable
- [ ] Any artifact referenced in CLAUDE.md actually exists at the declared path
- [ ] No required artifact is empty, stubbed, or placeholder only
- [ ] No required artifact appears abandoned

**Refinement (tier 4 only)**
- [ ] Any required artifact significantly larger than it needs to be?
- [ ] Required artifacts that have become redundant and could be retired?

---

### `conventions` — Conventions Declared and Followed

**Quality**
- [ ] Project-specific conventions documented in CLAUDE.md or referenced doc
- [ ] Commit messages follow the declared conventions for this project type
- [ ] File naming follows declared conventions
- [ ] No convention documented but never followed, or followed but never documented
- [ ] Declared conventions that can be enforced automatically are enforced by tooling

**Refinement (tier 4 only)**
- [ ] Conventions so obvious they don't need documentation?
- [ ] Conventions so complex they suggest the underlying approach should simplify?
- [ ] Conventions that conflict with each other subtly?

---

### `framework` — Framework Pattern Correctness

*Run at tier 3+ or when explicitly requested.*

**Quality**
- [ ] Code examples use patterns correct for the declared framework
- [ ] Documented workflows account for framework-specific constraints
- [ ] No guidance recommends an approach the framework explicitly discourages
- [ ] Framework-specific annotations, decorators, or conventions used correctly in examples
- [ ] Patterns are current for the version of the framework in use

**Refinement (tier 4 only)**
- [ ] Framework-specific guidance scattered or consolidated?
- [ ] Framework patterns documented that are never actually used?
- [ ] Could framework guidance link to authoritative external docs?
