# Comprehensive Quality Review - Design Specification

**Date:** 2026-03-30
**Type:** Quality Assurance Enhancement
**Approach:** Layer-by-Layer Incremental

---

## Overview

Conduct the deepest evaluation and review of the skills repository, applying all quality assurance rules and discovering new validation types. Build on existing comprehensive QA framework by completing TODOs, implementing new validators, and performing deep manual analysis.

**Goals:**
1. Complete all TODO items from previous deep analysis
2. Discover and implement new validation categories
3. Go deeper than any previous analysis with triple-checking
4. Document all new problem types for future prevention

**Context:**
- Existing: 7 automated validators, comprehensive QA framework, zero CRITICAL issues
- TODO: Functional test execution, test cases, new validation types, deep analysis areas
- User requirement: No shortcuts, triple-check everything, find new validation types

---

## Architecture

### Three-Phase Structure

```
Phase 1: Complete Existing TODOs
├─ Functional test execution scripts
├─ Test cases for critical skills
├─ Test coverage reporting
└─ README/CLAUDE.md sync checkers
    ↓ (Discovers gaps during implementation)

Phase 2: New Validation Categories
├─ Document new problem types found in Phase 1
├─ Add validators for new categories
├─ Cross-document consistency checks
├─ Temporal consistency (stale references)
├─ Usability/UX analysis
└─ Python code quality (validators themselves)
    ↓ (Validates everything built so far)

Phase 3: Deep Dive Uncovered Areas
├─ Security implications review
├─ Skill interaction analysis
├─ Documentation gap analysis
├─ Behavioral consistency across skills
├─ Edge case scenario testing
├─ Performance/scalability review
└─ Final triple-check validation
```

### Quality Gates Between Phases

**After Phase 1:**
- All existing validators pass
- New test execution scripts work correctly
- Test cases execute without errors
- Coverage reporting is accurate

**After Phase 2:**
- All new validators pass on existing skills
- No false positives detected
- New issue types documented
- Regression tests added

**After Phase 3:**
- All findings reviewed and categorized
- Security issues addressed or documented
- Consistency improvements documented
- Final triple-check complete

### Triple-Check Mechanism

**For every component:**
1. **First pass:** Implement feature/validator
2. **Second pass:** Run against all skills, document findings
3. **Third pass:** Review findings, re-check edge cases, verify no false positives/negatives

**Applied to:**
- Test execution scripts
- New validators
- Manual analysis findings
- Security review
- Final validation

---

## Phase 1: Complete Existing TODOs

### 1.1 Functional Test Execution Scripts

**Objective:** Enable automated execution of skill tests with isolation and verification.

**Components to Build:**

**1. `scripts/testing/run_skill_tests.py`**

**Functionality:**
- Execute functional tests for skills
- Use git worktrees for isolation
- Capture outputs (files, commits, invocations)
- Compare against expected behavior
- Support parallel execution
- JSON output for CI integration

**Input:** Test case JSON files in `tests/skills/<skill-name>/`

**Output:** Test results with pass/fail status

**Test case format:**
```json
{
  "skill_name": "git-commit",
  "tests": [
    {
      "id": "basic-commit",
      "description": "Commit single file change",
      "setup": "scripts/setup_basic_commit.sh",
      "prompt": "commit these changes",
      "expected_behavior": {
        "invokes_skills": ["update-claude-md"],
        "creates_commit": true,
        "commit_message_matches": "^(feat|fix|docs)\\(.*\\):.*",
        "files_modified": ["CLAUDE.md"]
      }
    }
  ]
}
```

**2. `scripts/testing/run_regression_tests.py`**

**Functionality:**
- Execute regression tests from `tests/regression/`
- Verify known issues don't recur
- Support running specific issues
- JSON output for CI

**Input:** Regression test JSON files (issue-XXX-*.json)

**Output:** Pass/fail status per issue

**3. `scripts/testing/test_coverage.py`**

**Functionality:**
- Calculate test coverage metrics
- Report gaps in coverage
- Track trends over time

**Metrics:**
- Branch coverage (all decision paths tested)
- Skill coverage (which skills have tests)
- Validator coverage (all validators tested)
- Regression coverage (all issues tested)

**Output format:**
```
Test Coverage Report
====================
Overall: 75% (15/20 skills)

By Category:
  User-invocable skills: 80% (4/5)
  Foundation skills: 60% (3/5)
  Update skills: 100% (3/3)

Gaps:
  - quarkus-flow-dev: No tests
  - dependency-management-principles: No tests

Recommendations:
  - Add tests for foundation skills
  - Test quarkus-specific workflows
```

**Triple-check plan:**
1. First: Implement basic execution, test on one skill
2. Second: Test on all skills, verify isolation works
3. Third: Check for flaky tests, edge cases, false results

### 1.2 Test Cases for Top 5 User-Invocable Skills

**Priority skills:**

**1. git-commit**
- Test scenarios:
  - Basic commit (single file)
  - Skill changes (triggers skill-review)
  - README sync (triggers readme-sync)
  - CLAUDE.md sync (triggers update-claude-md)
  - Project type routing (skills/java/custom/generic) <!-- nocheck:project-types -->
  - Validation failure handling
  - User says NO scenario

**2. java-git-commit**
- Test scenarios:
  - DESIGN.md missing (blocks commit)
  - Basic Java commit
  - DESIGN.md sync
  - java-code-review invocation
  - Security-critical code (chains to java-security-audit)
  - Validation failure rollback

**3. custom-git-commit**
- Test scenarios:
  - Missing sync rules
  - Primary doc sync
  - Table-driven sync logic
  - Milestone tracking
  - Validation failure handling

**4. java-code-review**
- Test scenarios:
  - Safety violations detection
  - Security-critical code detection
  - Chains to java-security-audit
  - Blocking on CRITICAL findings
  - WARNING confirmation flow

**5. skill-review**
- Test scenarios:
  - Frontmatter validation
  - CSO compliance checking
  - Cross-reference verification
  - Flowchart validation
  - Blocking on CRITICAL findings

**Expected outcome:** 25+ test scenarios total (5+ per skill)

**Discovery opportunity:** Writing tests will reveal:
- Missing validators
- Unchecked edge cases
- Documentation gaps
- Behavioral inconsistencies

### 1.3 README/CLAUDE.md Sync Checkers

**Objective:** Automate detection of documentation drift.

**Component:** `scripts/validation/validate_readme_sync.py`

**Checks:**
1. **Skills in README match actual skills**
   - Parse README.md § Skills section
   - List actual skill directories
   - Compare and report discrepancies

2. **Chaining table matches actual chaining**
   - Parse README.md § Skill Chaining Reference
   - Read SKILL.md cross-references
   - Verify bidirectional consistency

3. **CLAUDE.md references match reality**
   - Parse CLAUDE.md § Key Skills
   - Verify skill names exist
   - Check workflow descriptions match actual behavior

4. **No stale skill names**
   - Search for references to non-existent skills
   - Check for renamed skills in documentation

5. **ADR references are correct**
   - Parse ADR references in CLAUDE.md
   - Verify ADR files exist

**Output:**
```
README/CLAUDE.md Sync Check
============================

✅ Skills section: All 19 skills documented
❌ Chaining table: Missing entry for update-primary-doc
⚠️  CLAUDE.md: References skill-creator (third-party, should be in .gitignore)
✅ ADR references: All 10 ADRs exist

Issues found: 2
  CRITICAL: 0
  WARNING: 2
```

**Triple-check:**
1. First: Parse documents, build structure
2. Second: Verify all checks work correctly
3. Third: Test on intentionally broken docs to verify detection

---

## Phase 2: New Validation Categories

### 2.1 Cross-Document Consistency Validator

**New validator:** `scripts/validation/validate_cross_document.py`

**What it checks:**

**1. README ↔ Skills consistency**
- Skills listed in README exist as directories
- SKILL.md files exist for all listed skills
- Descriptions roughly match (manual review flag if very different)

**2. Chaining relationship consistency**
- README chaining table matches SKILL.md § Skill Chaining
- Bidirectional references are symmetric
- Invocation claims are accurate

**3. CLAUDE.md ↔ Reality consistency**
- Key Skills section lists actual skills
- Workflow descriptions match actual behavior
- Tool/command references are current

**4. ADR ↔ Documentation consistency**
- ADRs referenced in CLAUDE.md exist
- Decisions documented in ADRs are reflected in workflows
- No contradictions between ADRs and current practice

**5. Terminology consistency**
- Consistent use of "sync" vs "update"
- Consistent use of "propose" vs "suggest"
- Consistent severity levels (CRITICAL/WARNING/NOTE)

**Why it's new:** Current validators check single files; this checks relationships between documents.

**Implementation approach:**
- Build knowledge graph from all documents
- Traverse graph checking consistency
- Report inconsistencies with context

**Triple-check:**
1. First: Parse all documents, build graph
2. Second: Check all edges resolve
3. Third: Manually verify semantic consistency (not just syntactic)

### 2.2 Temporal Consistency Validator

**New validator:** `scripts/validation/validate_temporal.py`

**What it checks:**

**1. Deprecated tool names**
- Scan for: TodoWrite, TodoRead (deprecated)
- Check for: Old tool names that changed

**2. Outdated command syntax**
- Git command flags that no longer exist
- Python syntax from old versions
- Bash patterns that are deprecated

**3. Moved/renamed files**
- References to docs/ARCHITECTURE.md (moved to DESIGN.md)
- References to old skill names
- Stale path references

**4. Version-specific patterns**
- Python 2 syntax (should be Python 3)
- Old git workflows (git flow vs current patterns)
- Deprecated npm/maven commands

**Why it's new:** Code evolves; this catches references that become stale over time.

**Implementation approach:**
- Maintain deprecation database (deprecated_patterns.json)
- Scan all files for patterns
- Report matches with suggested updates

**Deprecation database example:**
```json
{
  "deprecated_tools": [
    {"old": "TodoWrite", "new": "TaskCreate", "since": "2026-01-01"},
    {"old": "TodoRead", "new": "TaskGet", "since": "2026-01-01"}
  ],
  "deprecated_paths": [
    {"old": "docs/ARCHITECTURE.md", "new": "docs/DESIGN.md", "since": "2025-12-01"}
  ]
}
```

**Triple-check:**
1. First: Scan for known deprecated patterns
2. Second: Review findings in context (some might be examples of old patterns)
3. Third: Verify suggestions are correct

### 2.3 Usability/UX Validator

**New validator:** `scripts/validation/validate_usability.py`

**What it checks:**

**1. Clear triggering conditions**
- Description starts with "Use when"
- Triggering conditions are specific, not vague
- Examples of when to use provided

**2. Examples for complex instructions**
- Complex operations have examples
- Code blocks for commands
- Before/after examples for edits

**3. Actionable error messages**
- Not just "failed"
- Includes what went wrong
- Suggests how to fix

**4. Measurable success criteria**
- Success Criteria section exists for artifact-producing skills
- Criteria are checkboxes
- Criteria are verifiable

**5. Common Pitfalls table**
- Exists for major skills
- Three columns: Mistake | Why It's Wrong | Fix
- Covers real issues users encounter

**6. Jargon defined**
- Acronyms spelled out on first use
- Technical terms explained
- Links to definitions provided

**7. Sequential workflow steps**
- Steps are numbered
- Steps are in logical order
- No skipped steps

**Why it's new:** Current validators check correctness; this checks clarity and user experience.

**Implementation approach:**
- Rule-based checks for common patterns
- Heuristics for example density
- Flag potential usability issues for manual review

**Triple-check:**
1. First: Apply rules, flag potential issues
2. Second: Manually review flagged items
3. Third: Verify improvements enhance usability

### 2.4 Edge Case Coverage Validator

**New validator:** `scripts/validation/validate_edge_cases.py`

**What it checks:**

**1. File-not-found handling**
- Checks for file existence before reading
- Graceful error messages when files missing
- Guidance on creating missing files

**2. Empty input handling**
- Handles empty strings
- Handles empty files
- Handles empty git diffs

**3. Permission errors**
- File permissions considered
- Directory permissions checked
- Git permissions mentioned

**4. Network/external failures** (for tools that fetch)
- Timeout handling
- Retry logic documented
- Fallback behavior specified

**5. Concurrent operations**
- Git lock files mentioned
- Race conditions discussed
- Atomicity guarantees documented

**6. Idempotency**
- Safe to run twice
- No duplicate operations
- State consistency maintained

**Why it's new:** Current validators check happy path; this checks error paths.

**Implementation approach:**
- Scan for file operations without existence checks
- Scan for network operations without error handling
- Flag operations that should be idempotent but don't document it

**Triple-check:**
1. First: Identify all file/network/git operations
2. Second: Check each for edge case handling
3. Third: Verify documentation is accurate

### 2.5 Behavioral Consistency Validator

**New validator:** `scripts/validation/validate_behavior.py`

**What it checks:**

**1. Commit message format consistency**
- All commit skills follow Conventional Commits
- Same format across git-commit, java-git-commit, custom-git-commit
- Consistent scope patterns

**2. Severity level consistency**
- All review skills use CRITICAL/WARNING/NOTE
- Same meaning across skills
- Consistent blocking behavior (CRITICAL blocks)

**3. Update workflow consistency**
- All update skills: propose → confirm → apply → validate
- Consistent revert-on-failure pattern
- Same user confirmation pattern ("YES")

**4. Error handling consistency**
- Similar errors reported similarly
- Consistent error message format
- Similar recovery suggestions

**5. User confirmation consistency**
- All use "YES" (not "yes", "y", "ok")
- Confirmation prompts are similar
- Rejection handling is consistent

**Why it's new:** Ensures consistent user experience across the skill collection.

**Implementation approach:**
- Define behavioral patterns per skill category
- Check each skill against its category pattern
- Report deviations

**Pattern definitions:**
```python
PATTERNS = {
    "commit_skills": {
        "message_format": "Conventional Commits 1.0.0",
        "confirmation": "Reply YES to commit",
        "routing": "Check CLAUDE.md for project type"
    },
    "review_skills": {
        "severity_levels": ["CRITICAL", "WARNING", "NOTE"],
        "blocking": "CRITICAL blocks commit",
        "output_format": "## Skill: <name>\n### CRITICAL Issues"
    }
}
```

**Triple-check:**
1. First: Define patterns for each skill category
2. Second: Check all skills in category
3. Third: Manually verify deviations are intentional

### 2.6 Python Code Quality Validator

**New validator:** `scripts/validation/validate_python_quality.py`

**What it checks (for the validators themselves):**

**1. Type hints**
- Function signatures have type hints
- Return types specified
- Complex types properly annotated

**2. Docstrings**
- All functions have docstrings
- Docstrings follow standard format (Google or NumPy style)
- Parameters and returns documented

**3. Error handling**
- No bare except clauses
- Specific exceptions caught
- Error messages are informative

**4. Code quality**
- PEP 8 compliance (via flake8)
- No unused imports
- No dead code
- Proper logging instead of print

**5. Security**
- No os.system or eval
- Path operations use Path objects
- Input sanitization where needed
- No command injection vulnerabilities

**6. Testing**
- Unit tests exist for validators
- Tests cover edge cases
- Tests are isolated

**Why it's new:** We validate skills but haven't validated the validators themselves.

**Implementation approach:**
- Use mypy for type checking
- Use flake8 for style
- Use bandit for security
- Custom checks for docstrings
- Parse AST for complex checks

**Triple-check:**
1. First: Run automated tools (mypy, flake8, bandit)
2. Second: Manual code review of validators
3. Third: Verify tests cover critical paths

---

## Phase 3: Deep Dive Uncovered Areas

### 3.1 Security Implications Review

**Objective:** Manual security audit of workflows and validators.

**Areas to review:**

**1. Command injection risks**
- Scan for: os.system, subprocess with shell=True, eval, exec
- Review: bash command construction in skills
- Verify: User input is sanitized

**Example to check:**
```python
# Risky:
os.system(f"git commit -m '{user_message}'")

# Safe:
subprocess.run(["git", "commit", "-m", user_message])
```

**2. Path traversal vulnerabilities**
- Check: File operations use validated paths
- Verify: No arbitrary file access
- Review: Directory traversal prevention

**Example to check:**
```python
# Risky:
file_path = user_input
open(file_path)

# Safe:
file_path = Path(user_input).resolve()
if not file_path.is_relative_to(BASE_DIR):
    raise SecurityError("Path traversal detected")
```

**3. Git command safety**
- Review: force push usage (should warn user)
- Check: hard reset usage (should confirm with user)
- Verify: destructive operations documented

**4. Secret exposure risks**
- Check: .env files not staged accidentally
- Verify: Credentials not in commit messages
- Review: Sensitive file patterns excluded

**5. Destructive operations**
- List: All operations that delete/overwrite data
- Verify: User confirmation required
- Check: Revert mechanisms exist

**Deliverable:** Security audit report with:
- Risk categorization (CRITICAL/HIGH/MEDIUM/LOW)
- Specific line numbers and files
- Recommended mitigations
- Regression tests for security issues

**Triple-check:**
1. First: Automated scan for common patterns
2. Second: Manual review of each finding
3. Third: Verify mitigations don't break functionality

### 3.2 Skill Interaction Analysis

**Objective:** Analyze how skills interact under all conditions.

**Scenarios to trace:**

**1. Chaining failure scenarios**
- git-commit → skill-review fails → what state?
- java-git-commit → DESIGN.md validation fails → proper revert?
- update-claude-md applies → validation fails → rollback?

**2. Atomicity guarantees**
- Multiple files updated → one validation fails → all reverted?
- Partial commits possible? Should they be?
- Transaction boundaries clear?

**3. State consistency**
- Skill invoked twice → same result (idempotent)?
- Concurrent invocations safe?
- Git repository state consistent?

**4. Resource cleanup**
- Git worktrees cleaned up?
- Temp files removed?
- File handles closed?

**5. Error propagation**
- Errors from chained skills reported correctly?
- Error context preserved?
- Recovery guidance provided?

**Method:**
- Trace through chaining workflows manually
- Identify all state transitions
- Verify cleanup at all exit points
- Test failure scenarios

**Deliverable:** Skill interaction report with:
- Interaction diagrams
- Failure mode analysis
- Recommendations for improvements

**Triple-check:**
1. First: Trace nominal paths
2. Second: Trace error paths
3. Third: Test actual failure scenarios

### 3.3 Documentation Gap Analysis

**Objective:** Find undocumented assumptions and missing explanations.

**Method:** Read each skill as if I've never seen it before.

**What to look for:**

**1. Undocumented assumptions**
- Prerequisites not stated
- Environment assumptions
- Tool version requirements

**2. Missing "why" explanations**
- Non-obvious design choices
- Workflow ordering rationale
- Tool selection reasons

**3. Insufficient examples**
- Complex operations without examples
- Edge cases without illustrations
- Before/after comparisons missing

**4. Unclear success criteria**
- Vague completion conditions
- No verification steps
- Ambiguous "done" definition

**5. Missing troubleshooting**
- Common errors not documented
- No debugging guidance
- Recovery steps missing

**6. Gaps between docs and behavior**
- Documentation says one thing, code does another
- Outdated workflow descriptions
- Missing workflow steps

**Deliverable:** Documentation gap report with:
- Specific gaps identified
- Recommended additions
- Priority ranking (HIGH/MEDIUM/LOW)

**Triple-check:**
1. First: Read all skills fresh
2. Second: Compare docs to code
3. Third: Verify fixes are clear and accurate

### 3.4 Consistency Across Skill Types

**Objective:** Find inconsistencies in user experience.

**Comparisons to make:**

**1. Commit skills comparison**
- git-commit vs java-git-commit vs custom-git-commit
- User confirmation patterns
- Error handling
- Routing logic
- Documentation sync behavior

**2. Review skills comparison**
- skill-review vs java-code-review
- Severity reporting
- Finding format
- Blocking behavior

**3. Update skills comparison**
- update-claude-md vs java-update-design vs update-primary-doc
- Proposal format
- Validation handling
- Revert mechanisms

**4. Terminology audit**
- Sync vs update (when each is used)
- Propose vs suggest
- Apply vs commit
- Consistent throughout?

**Method:**
- Create comparison matrices
- Identify divergences
- Determine if intentional or inconsistent

**Deliverable:** Consistency audit with:
- Comparison tables
- Identified inconsistencies
- Recommendations for harmonization

**Triple-check:**
1. First: Create comparison matrices
2. Second: Review divergences
3. Third: Verify intentionality

### 3.5 Edge Case Scenario Testing

**Objective:** Manually trace through extreme scenarios.

**Scenarios to test:**

**1. Large scale scenarios**
- User stages 100 files → readability issues?
- SKILL.md has 50 cross-references → performance?
- Git repo with 10,000 commits → git log slow?
- README.md is 10,000 lines → validation time?

**2. Wrong environment scenarios**
- Skill run in wrong directory → error message clear?
- Missing Python dependencies → graceful failure?
- Git repository not initialized → detected?

**3. Concurrent scenarios**
- Multiple skills run simultaneously → conflicts?
- Git operations concurrent → lock handling?

**4. Unusual input scenarios**
- Empty commit message → handled?
- Files with spaces in names → quoted correctly?
- Unicode in commit messages → preserved?

**5. Failure cascade scenarios**
- Validation fails → revert fails → recovery?
- Network timeout during fetch → retry logic?

**Method:**
- Set up test environments for each scenario
- Manually execute workflows
- Document behavior
- Compare to expected behavior

**Deliverable:** Edge case test report with:
- Scenario descriptions
- Actual behavior observed
- Expected behavior
- Gaps or issues identified

**Triple-check:**
1. First: Test each scenario
2. Second: Review behavior against expectations
3. Third: Verify edge cases are documented or handled

### 3.6 Performance & Scalability Review

**Objective:** Identify performance watchpoints (not optimization, just awareness).

**Areas to check:**

**1. Validation script performance**
- Time to validate 1 skill
- Time to validate all skills
- Time for pre-commit validation
- Target: <2s for pre-commit

**2. Git operation performance**
- git diff on large files
- git log on large repos
- git status with many files
- Target: <5s for typical operations

**3. Document parsing performance**
- Parsing large README.md (10,000 lines)
- Building cross-reference graph
- Target: <1s for parsing

**4. Skill discovery performance**
- Loading 100+ skills
- Parsing all frontmatter
- Target: <5s for full discovery

**5. Concurrent execution**
- Multiple validators running
- Parallel test execution
- Resource contention

**Method:**
- Time critical operations
- Test with large inputs
- Identify any operations >5s
- Document watchpoints

**Deliverable:** Performance review with:
- Timing measurements
- Identified watchpoints (if any)
- Recommendations (if needed)

**Note:** This is awareness, not optimization. Only flag if something is unusually slow.

**Triple-check:**
1. First: Measure typical operations
2. Second: Test with large inputs
3. Third: Verify measurements are representative

### 3.7 Regression Test Coverage Audit

**Objective:** Verify all risks are covered by tests.

**Checks:**

**1. Known issues coverage**
- Each issue in known-issues.md has regression test
- Tests actually catch the issue
- Tests are automated

**2. Validator coverage**
- Each CRITICAL validator has regression test
- Validators can detect their target issues
- No false positives

**3. Workflow coverage**
- Each major workflow has functional test
- Happy path tested
- Error paths tested

**4. Edge case coverage**
- Edge cases from 3.5 have tests
- Unusual inputs tested
- Failure scenarios tested

**5. Security coverage**
- Security issues from 3.1 have tests
- Attack scenarios tested
- Mitigations verified

**Method:**
- Cross-reference known issues with tests
- Check validator list against test list
- Verify coverage gaps

**Deliverable:** Coverage audit with:
- Coverage matrix
- Gaps identified
- Test recommendations

**Triple-check:**
1. First: List all testable items
2. Second: Check each has tests
3. Third: Verify tests actually work

### 3.8 Final Triple-Check Validation

**Objective:** Systematic re-validation of everything.

**Process:**

**1. First pass - Run ALL validators**
- Execute all 7 original validators
- Execute all 6 new validators
- Execute Python quality checks
- Collect all findings

**2. Second pass - Review all findings**
- Categorize by severity
- Eliminate false positives
- Add context to each finding
- Verify fixes are correct

**3. Third pass - Random spot-check**
- Pick 5 random skills
- Read them completely without validators
- Compare manual findings to validator output
- If discrepancy found, improve validator

**Random sampling strategy:**
```python
import random
skills = list_all_skills()
sample = random.sample(skills, 5)
for skill in sample:
    manual_review(skill)
    validator_output = run_validators(skill)
    compare(manual_review, validator_output)
```

**Deliverable:** Final validation report with:
- All findings from all validators
- Manual spot-check results
- Validator accuracy assessment
- Final recommendations

**Triple-check:**
1. First: Automated validation
2. Second: Manual verification
3. Third: Spot-check validation accuracy

---

## Implementation Plan Summary

### Phase 1 Tasks (Complete TODOs)
1. Implement run_skill_tests.py
2. Implement run_regression_tests.py
3. Implement test_coverage.py
4. Implement validate_readme_sync.py
5. Write test cases for git-commit
6. Write test cases for java-git-commit
7. Write test cases for custom-git-commit
8. Write test cases for java-code-review
9. Write test cases for skill-review
10. Document Phase 1 findings

### Phase 2 Tasks (New Validators)
1. Implement validate_cross_document.py
2. Implement validate_temporal.py
3. Implement validate_usability.py
4. Implement validate_edge_cases.py
5. Implement validate_behavior.py
6. Implement validate_python_quality.py
7. Run all new validators
8. Document new issues found
9. Add regression tests for new issues
10. Update CLAUDE.md § QA Framework

### Phase 3 Tasks (Deep Dive)
1. Security audit review
2. Skill interaction analysis
3. Documentation gap analysis
4. Consistency audit
5. Edge case scenario testing
6. Performance review
7. Regression test coverage audit
8. Final triple-check validation
9. Compile comprehensive findings report
10. Update deep-analysis-report

---

## Success Criteria

**Must achieve:**
- [ ] Zero CRITICAL issues remain unaddressed
- [ ] All existing TODOs completed and tested
- [ ] At least 6 new validation categories implemented
- [ ] All 5 priority skills have functional tests (25+ scenarios)
- [ ] Test coverage ≥80% for user-invocable skills
- [ ] All new issues added to known-issues.md with regression tests
- [ ] Triple-check validation performed on all findings
- [ ] Complete documentation of all new validators

**Quality gates:**
- [ ] Each new validator passes self-validation
- [ ] Each phase validated before moving to next
- [ ] All findings reviewed and categorized
- [ ] No regressions introduced

**Output quality:**
- Clear categorization of all findings
- Actionable recommendations with line numbers
- Reproducible test cases for all issues
- Documentation updates for all new validators
- Regression tests for all new issue types

---

## Deliverables

**Phase 1:**
- run_skill_tests.py, run_regression_tests.py, test_coverage.py
- validate_readme_sync.py
- 25+ test cases for 5 skills
- Phase 1 findings report

**Phase 2:**
- 6 new validators
- Validation findings reports
- Updated known-issues.md
- New regression tests
- Updated CLAUDE.md

**Phase 3:**
- Security audit report
- Skill interaction analysis
- Documentation gap analysis
- Consistency audit findings
- Edge case test results
- Performance review (if watchpoints needed)
- Final comprehensive report
- Updated deep-analysis-report-YYYY-MM-DD.md

---

## Timeline Estimate

**Phase 1:** ~3-4 hours
**Phase 2:** ~3-4 hours
**Phase 3:** ~2-3 hours
**Total:** ~8-11 hours of thorough, triple-checked work

---

## Notes

**Triple-check philosophy:**
Every component goes through three passes to catch issues that single-pass reviews miss. This catches the problems that emerge when you "think you're done but aren't."

**Discovery mindset:**
Phase 1 implementation will naturally reveal gaps. We document these as we find them, feeding into Phase 2 validator design.

**No shortcuts:**
Each validator, test, and analysis follows the triple-check pattern. No assumptions, no skipping steps.

**Performance awareness:**
We're not optimizing, but we track timing to identify if any watchpoints are needed for future work.
