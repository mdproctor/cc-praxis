# Implementation Plan: Universal "Diary of Work" Documentation System

### Executive Summary

This plan addresses the merge conflict problem in collaborative documentation by introducing a **temporal, append-only diary system** that operates across all 4 project types. The core insight: dated entries never conflict, and GitHub issues provide temporal ordering with discussion capabilities. This is a **universal quality framework enhancement**, not a project-specific feature.

---

## 1. Architectural Design Decisions

### 1.1 Design Philosophy: Universal First

**CRITICAL PRINCIPLE:** This is not a Java-specific feature. This is a **universal documentation quality pattern** that prevents merge conflicts across ALL project types.

**Why Universal:**
- Merge conflicts in DESIGN.md/VISION.md/THESIS.md affect all collaborative projects
- Claude-driven intelligent merge using diary context works for any document
- Temporal entry pattern (dated files/issues) is project-agnostic
- Same problem (concurrent documentation edits) exists in java, custom, skills, and generic types <!-- nocheck:project-types -->

**Reference:** CLAUDE.md § Meta-Rule: Consider Universality First

### 1.2 Skill Naming Convention

**Recommendation: Domain-agnostic naming (capture-diary, consolidate-diary, diary-merge)**

**Rationale:**
- Following existing pattern: `update-primary-doc` (not `update-vision`), `git-commit` (not `java-commit` at base layer)
- "diary" is conceptually clear: temporal work log
- Labels can be type-specific (design-diary, ideas-diary, work-diary) without changing skill names
- Aligns with universal quality framework architecture

**Alternative rejected:** Domain-specific naming (capture-design, consolidate-design) would require separate skills per type, violating DRY and universality principle.

### 1.3 Two-Tier Storage Strategy

**Preferred: GitHub Issues**
- Temporal ordering (issue #N always after #N-1)
- Built-in discussion (comments)
- Zero merge conflicts (stored remotely)
- Searchable/filterable by labels
- Integration with project workflow (link from commits, PRs)

**Fallback: Dated Files (.work/YYYY-MM-DD-topic.md)**
- Works without GitHub remote
- Dated filenames = temporal ordering
- Each day = new file = no conflicts
- Git history preserves temporal sequence
- Simple grep/find for searching

**Implementation:** Skills detect GitHub availability (check `.git/config` for remote, attempt `gh` command) and use appropriate tier.

### 1.4 Project Type Detection Strategy

**Recommendation: Read from CLAUDE.md (explicit declaration)**

**Rationale:**
- Follows existing pattern (git-commit, java-git-commit, custom-git-commit all read CLAUDE.md)
- Zero ambiguity
- User controls behavior
- Auto-detection is fragile (proven in PROJECT-TYPES.md § Why Explicit Declaration)

**Fallback:** If CLAUDE.md missing, prompt user to declare type (same as git-commit Step 0).

### 1.5 Primary Document Mapping

**Recommendation: Hybrid approach (hardcoded for built-in types, user-configured for custom)**

**Type-specific mappings:**

| Project Type | Primary Document | Diary Label | Hardcoded? |
|--------------|------------------|-------------|------------|
| **java** | `docs/DESIGN.md` | `design-diary` | ✅ Yes |
| **custom** | User's "Primary Document" from CLAUDE.md | User-configured label | ❌ No (read from CLAUDE.md) |
| **skills** | `README.md` + `CLAUDE.md` | `work-diary` | ✅ Yes (dual docs) |
| **generic** | None (opt-in) | `work-diary` | ❌ No (user provides path) |

**User configuration in CLAUDE.md (for type: custom):**
```markdown
## Project Type

**Type:** custom
**Primary Document:** docs/vision.md
**Diary Label:** ideas-diary
```

**Note:** All project types use `.work/` directory for file-based entries (no configuration needed).

### 1.6 GitHub Issues Detection

**Recommendation: Progressive enhancement with graceful fallback**

**Detection order:**
1. Check `.git/config` for `remote "origin"` with GitHub URL
2. Attempt `gh auth status` (fast check, <100ms)
3. If both succeed → use GitHub issues
4. If either fails → use file-based diary (no error, just fallback)

**User override in CLAUDE.md (optional):**
```markdown
**Diary Storage:** file  # Force file-based even if GitHub available
```

### 1.7 Consolidation Timing

**Recommendation: Manual-only with pre-commit prompt**

**Rationale:**
- User controls when ideas/decisions solidify into primary doc
- Pre-commit prompt raises awareness (like java-update-design)
- Not automatic (prevents premature consolidation)
- Not blocking (user can skip if entries not ready)

**Integration pattern:**
```
git-commit Step 1d (new):
  → Check for unconsolidated diary entries
  → If found: "You have N unconsolidated diary entries. Consolidate now? (Y/n/skip)"
  → If Y: Invoke consolidate-diary
  → If n: Show entry list, ask which to consolidate
  → If skip: Continue with commit
```

### 1.8 Integration with Existing Sync Workflows

**Recommendation: Parallel system initially, with migration path**

**Phase 1: Parallel (introduce diary without disrupting existing users)**
- `java-update-design` continues to work unchanged
- `capture-diary` + `consolidate-diary` available as opt-in
- Users can use both (diary for WIP ideas, update-design for immediate sync)
- Zero breaking changes

**Phase 2: Integration (after diary system proven stable)**
- `java-update-design` prompts: "Quick sync now, or capture to diary?"
- Superpowers (writing-plans, executing-plans) auto-capture decisions to diary
- `java-git-commit` checks for unconsolidated entries
- Still backwards compatible (existing users can ignore diary)

**Phase 3: Replacement (only if users prefer diary workflow)**
- `update-primary-doc` becomes "consolidate from diary or immediate update?"
- Users choose workflow based on project needs
- Migration guide for existing projects

**Never forced:** Existing workflows continue to work. Diary is enhancement, not replacement.

### 1.9 Diary Label Customization

**Recommendation: Hardcoded per built-in type, user-configured for custom**

**Built-in types (hardcoded in skills):**
- `type: java` → `design-diary` (architectural decisions)
- `type: skills` → `work-diary` (skill development)
- `type: generic` → `work-diary` (general notes)

**Custom types (read from CLAUDE.md):**
```markdown
**Diary Label:** ideas-diary  # Or research-diary, experiment-diary, etc.
```

**Why not single universal label:**
- Filtering: Users want to see design decisions separate from research notes
- Multi-project GitHub accounts: Same repo might have design-diary + research-diary
- Semantic clarity: Label indicates content type

**Why not arbitrary user labels for built-in types:**
- Consistency: All Java projects use design-diary (easier to share patterns)
- Simplicity: Fewer decisions for users
- Type-specific semantics: "design" has architectural meaning in Java projects

### 1.10 Archive Strategy

**Recommendation: Move to .work/archive/ (for file-based), close issue with consolidation reference (for GitHub)**

**File-based archival:**
```
.work/
  2026-03-15-cache-strategy.md         # Unconsolidated
  2026-03-20-api-versioning.md          # Unconsolidated
  archive/
    2026-03-01-module-split.md          # Consolidated in commit abc123
    2026-03-10-auth-flow.md             # Consolidated in commit def456
```

**Metadata in archived files:**
```markdown
---
consolidated: 2026-03-25
consolidated-in-commit: abc123def
consolidated-to-section: DESIGN.md § Architecture Overview
---
```

**GitHub issue archival:**
- Close issue when consolidated
- Add comment: "Consolidated in commit abc123 → DESIGN.md § Architecture"
- Issue remains searchable in closed state
- Git history links back to issue

**Why archive instead of delete:**
- Git history preservation (can see what led to decisions)
- Audit trail (when was this idea proposed? when consolidated?)
- Reverting consolidation (restore from archive if decision changes)

---

## 2. Step-by-Step Implementation Approach

### Phase 1: Foundation (capture-diary skill)

**Order of implementation:**

**1.1 Create `capture-diary/SKILL.md` (3-5 hours)**
- Universal base skill (no project-type branching)
- Detects project type from CLAUDE.md
- Detects GitHub availability
- Creates diary entry (issue or file)
- Frontmatter with CSO-compliant description
- Decision flowchart (GitHub vs file path)
- Common Pitfalls table

**1.2 Implement GitHub issue creation path (2-3 hours)**
- Use `gh issue create` with label and template
- Template includes: Date, Topic, Context, Decision (if any), Next Steps
- Label based on project type (design-diary, ideas-diary, etc.)
- Milestone support (link to Current Milestone from CLAUDE.md)

**1.3 Implement file-based creation path (2-3 hours)**
- Create `.work/` directory (universal across all project types)
- Filename: `YYYY-MM-DD-topic.md` (date + slugified topic)
- Frontmatter: `date`, `topic`, `consolidated` (false initially)
- Template same as GitHub issue (consistent UX)

**1.4 Add type-specific path resolution (1-2 hours)**
- Java: Primary doc = `docs/DESIGN.md`, diary label = `design-diary`
- Custom: Read from CLAUDE.md
- Skills: Primary doc = `README.md` + `CLAUDE.md`, label = `work-diary`
- Generic: Prompt user for path and label (or use defaults)

**1.5 Testing and validation (2-3 hours)**
- Test in Java project (design-diary creation)
- Test in custom project (ideas-diary with config)
- Test with/without GitHub
- Test with/without CLAUDE.md
- Test interactive prompts

**Deliverable:** Working `capture-diary` skill (10-15 hours)

---

### Phase 2: Consolidation (consolidate-diary skill)

**2.1 Create `consolidate-diary/SKILL.md` (4-6 hours)**
- Reads unconsolidated entries (GitHub issues or files)
- Discovers document group (uses existing `document_discovery.py`)
- Analyzes entries for common themes/sections
- Proposes primary doc updates (grouped by section)
- Marks entries as consolidated
- Frontmatter with CSO-compliant description
- Decision flowchart (discovery → analysis → proposal → consolidation)
- Common Pitfalls table

**2.2 Implement GitHub issue consolidation (3-4 hours)**
- List open issues with diary label
- Fetch issue body and comments (`gh issue view`)
- Extract themes (manually guided, Claude does semantic analysis)
- Generate primary doc updates
- Close issues with consolidation reference
- Link commits to issues

**2.3 Implement file-based consolidation (3-4 hours)**
- Scan `.work/` for files with `consolidated: false`
- Read file contents
- Extract themes
- Generate primary doc updates
- Move to `.work/archive/`
- Update frontmatter with consolidation metadata

**2.4 Integration with document_discovery.py (2-3 hours)**
- Discover primary doc modules (reuse existing code)
- Map diary entries to modules (not just primary)
- Example: Design diary entry about API → `docs/design/api.md`
- Propose updates across all files in group

**2.5 Validation integration (2-3 hours)**
- Use existing `validate_document.py` for primary doc
- Use existing `modular_validator.py` for document groups
- Atomic update/revert (all files or none)
- No new validators needed (reuse universal validation)

**2.6 Testing and validation (3-4 hours)**
- Test with multiple diary entries
- Test theme extraction
- Test modular document consolidation
- Test archival (issues + files)
- Test validation integration

**Deliverable:** Working `consolidate-diary` skill (17-24 hours)

---

### Phase 3: Intelligent Merge (diary-merge skill)

**3.1 Create `diary-merge/SKILL.md` (5-7 hours)**
- 3-way merge context reader (base, ours, theirs)
- Diary entry collector (both branches)
- Semantic conflict detector (uses diary to resolve)
- Merge proposal generator
- Frontmatter with CSO-compliant description
- Decision flowchart (conflict detection → diary analysis → resolution)
- Common Pitfalls table

**3.2 Implement conflict detection (3-4 hours)**
- Detect merge conflicts in primary docs (DESIGN.md, VISION.md, etc.)
- Read base version (merge-base)
- Read ours (current branch)
- Read theirs (branch being merged)
- Identify conflict markers

**3.3 Implement diary context collection (4-5 hours)**
- Collect diary entries from both branches (git log + grep for diary commits)
- Collect GitHub issues from both branches (if available)
- Extract temporal sequence (which decision came first?)
- Extract intent (what was each author trying to achieve?)

**3.4 Implement intelligent resolution (5-6 hours)**
- Use diary context to resolve semantic conflicts
- Example: Both added same section → Check diary, one was "exploring", one was "decided" → Keep decided
- Example: Conflicting approaches → Check diary for trade-off analysis → Propose combined approach
- Generate merge proposal with rationale from diary
- Let user review and confirm

**3.5 Testing and validation (4-5 hours)**
- Simulate merge conflict scenarios
- Test with diary entries on both branches
- Test without diary (graceful degradation)
- Test with GitHub issues vs files
- Test user confirmation flow

**Deliverable:** Working `diary-merge` skill (21-27 hours)

---

### Phase 4: Integration with Existing Workflows

**4.1 Update `git-commit` (2-3 hours)**
- Add Step 1d: Check for unconsolidated diary entries
- Prompt user: "Consolidate now? (Y/n/skip)"
- Invoke `consolidate-diary` if user confirms
- Update flowchart
- Update Common Pitfalls table

**4.2 Update `java-git-commit` (1-2 hours)**
- Inherit Step 1d from `git-commit`
- Java-specific prompt wording
- Update flowchart

**4.3 Update `custom-git-commit` (1-2 hours)**
- Inherit Step 1d from `git-commit`
- Custom-specific prompt wording
- Update flowchart

**4.4 Update Superpowers integration (3-4 hours)**
- `superpowers:writing-plans` → Auto-capture design decisions to diary
- `superpowers:executing-plans` → Auto-capture implementation notes to diary
- Optional (configurable in CLAUDE.md): `auto-capture: true/false`

**4.5 Testing and validation (2-3 hours)**
- Test pre-commit prompts
- Test with/without unconsolidated entries
- Test user skip/defer
- Test Superpowers auto-capture

**Deliverable:** Integrated workflow (9-14 hours)

---

### Phase 5: Documentation and Migration

**5.1 Update CLAUDE.md (2-3 hours)**
- Add § Diary System overview
- Document configuration options
- Update Pre-Commit Checklist
- Add to § Key Skills

**5.2 Update README.md (2-3 hours)**
- Add § Diary System explanation
- Update Skill Chaining Reference
- Update How Skills Work Together
- Add to Key Features

**5.3 Update QUALITY.md (2-3 hours)**
- Document diary validation
- Add to Quality Protection by Project Type
- Update Implementation Status

**5.4 Create ADR (1-2 hours)**
- ADR: Universal Diary System for Merge Conflict Prevention
- Context: Collaborative documentation merge conflicts
- Decision: Temporal diary with GitHub/file fallback
- Consequences: Zero token cost, opt-in, universal

**5.5 Migration guide (2-3 hours)**
- How to enable diary in existing projects
- Migrating from java-update-design only to diary workflow
- Configuration examples per project type
- Troubleshooting common issues

**Deliverable:** Complete documentation (9-14 hours)

---

## 3. Architectural Trade-offs and Recommendations

### 3.1 Chosen Architecture

**Two-tier storage (GitHub issues preferred, file-based fallback)**

**Pros:**
- ✅ Works with or without GitHub (universal)
- ✅ Issues provide discussion + temporal ordering
- ✅ Files work offline
- ✅ Zero merge conflicts (both methods)
- ✅ Progressive enhancement (better with GitHub, works without)

**Cons:**
- ❌ Two code paths to maintain
- ❌ Slightly more complex testing
- ❌ Users might be confused which to use (mitigated: automatic detection)

**Why chosen:** Universality wins. Not all projects use GitHub (some use GitLab, Gitea, etc.). File-based fallback ensures skills work everywhere.

---

### 3.2 Alternative: GitHub-only

**Pros:**
- ✅ Simpler implementation (one code path)
- ✅ Better discussion features
- ✅ Better search/filter

**Cons:**
- ❌ Requires GitHub remote (breaks universality)
- ❌ Doesn't work offline
- ❌ Excludes GitLab/Gitea users

**Why rejected:** Violates universality principle. Skills should work everywhere.

---

### 3.3 Alternative: File-based only

**Pros:**
- ✅ Simpler implementation
- ✅ Works everywhere
- ✅ No external dependencies

**Cons:**
- ❌ No discussion (just dated files)
- ❌ Harder to search/filter
- ❌ No automatic temporal ordering guarantees

**Why rejected:** GitHub issues are strictly better when available. Progressive enhancement wins.

---

### 3.4 Alternative: ADR-based (extend ADR skill)

**Pros:**
- ✅ Reuses existing skill
- ✅ Already has sequential numbering
- ✅ Familiar to users

**Cons:**
- ❌ ADRs are for **decisions**, diary is for **exploration**
- ❌ Not all diary entries become ADRs (many are abandoned ideas)
- ❌ ADRs are heavyweight (formal structure), diary is lightweight (quick notes)
- ❌ Semantic conflict: ADR = finalized decision, diary = work in progress

**Why rejected:** Different purposes. ADRs document **what we decided**, diary documents **what we explored**. Some diary entries graduate to ADRs (consolidate creates ADR when appropriate).

---

### 3.5 Recommended: Hybrid with ADR graduation path

**Pattern:**
1. Capture idea to diary (quick, informal)
2. Explore in diary comments/entries (iterate)
3. Consolidate to primary doc when ready (formal documentation)
4. If significant decision: Create ADR (reference diary for context)

**Example workflow:**
```
Day 1: /capture-diary "Cache invalidation strategy"
  → Issue #123 or .work/2026-03-15-cache-strategy.md

Day 2-5: Add comments/updates to issue or file

Day 6: /consolidate-diary
  → Updates DESIGN.md § Caching with strategy
  → Proposes ADR creation (significant decision)

Day 7: /adr "Use Write-Through Cache Pattern"
  → Links to diary issue #123 for exploration context
```

**Result:** Diary + ADR complement each other, not conflict.

---

## 4. Dependencies and Sequencing

### 4.1 Dependencies

**External:**
- GitHub CLI (`gh`) for issue creation (optional, graceful fallback)
- Existing `document_discovery.py` (already implemented)
- Existing `validate_document.py` (already implemented)
- Existing `modular_validator.py` (already implemented)

**Internal:**
- `capture-diary` must be implemented before `consolidate-diary` (creates entries to consolidate)
- `consolidate-diary` must be implemented before `diary-merge` (merge uses consolidated understanding)
- Integration (Phase 4) requires all 3 core skills complete

**No circular dependencies.** Linear progression: capture → consolidate → merge → integration.

### 4.2 Sequencing Constraints

**Must complete in order:**
1. Phase 1 (capture-diary) — Foundation, no dependencies
2. Phase 2 (consolidate-diary) — Depends on capture-diary for entry format
3. Phase 3 (diary-merge) — Depends on consolidate-diary for merge context
4. Phase 4 (integration) — Depends on all 3 core skills
5. Phase 5 (documentation) — Depends on implementation complete

**Can parallelize:**
- Within Phase 1: GitHub path (1.2) and file path (1.3) can be developed in parallel
- Within Phase 2: GitHub consolidation (2.2) and file consolidation (2.3) can be developed in parallel
- Within Phase 4: All git-commit updates (4.1, 4.2, 4.3) can be done in parallel

**Estimated timeline:**
- **Sequential:** 66-96 hours (13-19 days at 5 hours/day)
- **With parallelization:** 50-70 hours (10-14 days at 5 hours/day)

---

## 5. Testing Strategy

### 5.1 Unit Testing

**Scope:**
- Diary entry creation (issue + file)
- Project type detection
- GitHub availability detection
- Entry archival
- Consolidation logic

**Approach:**
- Use existing `scripts/testing/` infrastructure
- Git worktree isolation (like existing skill tests)
- Mock `gh` command for issue testing
- Temporary directory for file-based testing

**Coverage target:** 90% (following existing pattern in QUALITY.md)

### 5.2 Integration Testing

**Scenarios:**
1. Java project with GitHub (design-diary via issues)
2. Java project without GitHub (design-diary via files)
3. Custom project with user config (ideas-diary)
4. Skills project (work-diary)
5. Modular documents (diary → modules consolidation)
6. Merge conflict resolution (3-way merge with diary context)

**Approach:**
- Create test repositories for each scenario
- Run full workflow (capture → consolidate → commit)
- Verify primary doc updates
- Verify archival
- Verify validation

### 5.3 Regression Testing

**Key regressions to prevent:**
- Diary entries lost during consolidation
- Merge conflicts in diary files (should never happen - dated filenames)
- Primary doc corruption during consolidation
- Unconsolidated entries invisible to git-commit prompt

**Approach:**
- Add to existing `run_regression_tests.py`
- Test known failure modes
- Prevent repeat issues

### 5.4 Functional Testing

**User workflows to test:**
1. Developer captures idea → Consolidates later → Commits
2. Two developers capture conflicting ideas → Merge intelligently → Resolve
3. User without GitHub → Uses file-based diary → Works seamlessly
4. User migrates from java-update-design → Enables diary → Both work

**Approach:**
- Manual testing with real projects
- Beta testing with early adopters
- Documentation feedback loop

---

## 6. Documentation Updates Needed

### 6.1 CLAUDE.md Updates

**New sections:**
- § Diary System (overview, when to use, configuration)
- § Diary Configuration (per project type)

**Updated sections:**
- § Key Skills (add capture-diary, consolidate-diary, diary-merge)
- § Pre-Commit Checklist (add "Consolidate diary?" check)
- § Skill Chaining (add diary workflow arrows)

**Estimated effort:** 2-3 hours

### 6.2 README.md Updates

**New sections:**
- § Diary System (user-facing explanation, benefits)

**Updated sections:**
- § Skills (add 3 new skills with descriptions)
- § Skill Chaining Reference (add diary chaining rows)
- § How Skills Work Together (add diary workflow example)
- § Key Features (add diary as feature)

**Estimated effort:** 2-3 hours

### 6.3 QUALITY.md Updates

**New sections:**
- § Diary Entry Validation (structure, temporal ordering)

**Updated sections:**
- § Quality Protection by Project Type (add diary to universal protection)
- § Implementation Status (add diary validators if any)

**Estimated effort:** 1-2 hours

### 6.4 PROJECT-TYPES.md Updates

**Updated sections:**
- § Type: java (add diary configuration example)
- § Type: custom (add diary label configuration)
- § Type: skills (add work-diary explanation)

**Estimated effort:** 1 hour

### 6.5 New Documentation

**Migration Guide:**
- How to enable diary in existing projects
- Migrating from update-only to diary workflow
- Configuration examples
- Troubleshooting

**Estimated effort:** 2-3 hours

**ADR:**
- ADR-000X: Universal Diary System for Merge Conflict Prevention
- Context, decision, consequences
- References to prior art (ADR system, issue tracking)

**Estimated effort:** 1-2 hours

---

## 7. Migration Path for Existing Users

### 7.1 Backward Compatibility

**CRITICAL: Zero breaking changes.**

**Existing workflows continue unchanged:**
- `java-update-design` still syncs DESIGN.md immediately (no diary)
- `update-primary-doc` still works for custom projects
- `git-commit` doesn't require diary
- No new CLAUDE.md fields required

**Diary is opt-in enhancement:**
- Users invoke `/capture-diary` when they want it
- Pre-commit prompt is non-blocking (can skip)
- Configuration is optional (defaults work)

### 7.2 Migration Phases

**Phase 1: Awareness (immediate)**
- Documentation explains diary system
- README shows new skills
- Users can try in test projects

**Phase 2: Adoption (gradual)**
- Early adopters enable diary
- Feedback collected
- Documentation refined

**Phase 3: Integration (after proving value)**
- Superpowers auto-capture to diary (optional)
- More users migrate from immediate sync to diary workflow
- Community shares patterns

**No forced migration.** Users choose based on project needs.

### 7.3 Migration Guide

**For Java projects:**
```markdown
## Enabling Diary System

1. No configuration needed (uses defaults)
2. Try it: `/capture-diary "Your architectural idea"`
3. Continue working
4. When ready: `/consolidate-diary`
5. Commit as usual

**What changes:**
- New `.work/` directory (or GitHub issues)
- Pre-commit prompt: "Consolidate diary?" (can skip)

**What stays the same:**
- `java-update-design` still works
- DESIGN.md still syncs
- No required workflow changes
```

**For custom projects:**
```markdown
## Enabling Diary System

1. Add to CLAUDE.md:
   ```markdown
   **Diary Label:** ideas-diary
   ```

2. Try it: `/capture-diary "Your idea"`
3. Continue working
4. When ready: `/consolidate-diary`
5. Commit as usual
```

**For skills projects:**
```markdown
## Enabling Diary System

1. No configuration needed (uses work-diary)
2. Capture: `/capture-diary "Skill enhancement idea"`
3. Consolidate: `/consolidate-diary` → Updates README.md or CLAUDE.md
4. Commit as usual
```

---

## 8. Critical Files for Implementation

### 8.1 New Skills (Create)

1. **/Users/mdproctor/claude/skills/capture-diary/SKILL.md**
   - Core diary entry creation skill
   - GitHub vs file path detection
   - Universal across all project types

2. **/Users/mdproctor/claude/skills/consolidate-diary/SKILL.md**
   - Diary consolidation to primary docs
   - Uses document_discovery.py for modular docs
   - Integration with existing validation

3. **/Users/mdproctor/claude/skills/diary-merge/SKILL.md**
   - Intelligent 3-way merge using diary context
   - Conflict resolution with temporal understanding
   - Graceful degradation without diary

### 8.2 Modified Skills (Update)

4. **/Users/mdproctor/claude/skills/git-commit/SKILL.md**
   - Add Step 1d: Check unconsolidated entries
   - Add diary prompt
   - Update flowchart

5. **/Users/mdproctor/claude/skills/java-git-commit/SKILL.md**
   - Inherit diary check from git-commit
   - Update flowchart
   - Document integration

6. **/Users/mdproctor/claude/skills/custom-git-commit/SKILL.md**
   - Inherit diary check from git-commit
   - Update flowchart
   - Document integration

### 8.3 Documentation (Update)

7. **/Users/mdproctor/claude/skills/CLAUDE.md**
   - § Diary System (new)
   - § Key Skills (add 3 skills)
   - § Pre-Commit Checklist (add diary check)

8. **/Users/mdproctor/claude/skills/README.md**
   - § Diary System (new)
   - § Skills (add 3 skills)
   - § Skill Chaining Reference (add rows)

9. **/Users/mdproctor/claude/skills/QUALITY.md**
   - § Diary Entry Validation (new, if validators needed)
   - § Quality Protection by Project Type (add diary)

10. **/Users/mdproctor/claude/skills/docs/PROJECT-TYPES.md**
    - Add diary configuration examples per type

### 8.4 Supporting Files (May Create)

11. **/Users/mdproctor/claude/skills/scripts/diary_utils.py** (if shared logic needed)
    - GitHub detection
    - Entry parsing
    - Archive logic

12. **/Users/mdproctor/claude/skills/docs/DIARY-MIGRATION-GUIDE.md**
    - Step-by-step migration
    - Configuration examples
    - Troubleshooting

13. **/Users/mdproctor/claude/skills/docs/adr/000X-universal-diary-system.md**
    - ADR documenting this decision
    - Context and alternatives
    - Consequences

---

## Summary

This implementation plan delivers a **universal, zero-token-cost, opt-in diary system** that solves merge conflicts across all 4 project types without breaking existing workflows. The temporal nature of dated entries (files or issues) guarantees zero conflicts, and Claude-driven intelligent merge uses diary context to resolve semantic conflicts.

**Key innovations:**
1. Universal first (not Java-specific)
2. Two-tier storage (GitHub preferred, file fallback)
3. Backward compatible (opt-in, not required)
4. Integrates with existing validation (reuses document_discovery.py, validate_document.py)
5. Gradual adoption (try → adopt → integrate)

**Estimated effort:**
- Core implementation: 50-70 hours
- Documentation: 9-14 hours
- Testing: Integrated into implementation
- **Total: 60-85 hours (12-17 days at 5 hours/day)**

**Next steps:**
1. Review and discuss this plan
2. Create Phase 1 (capture-diary) as proof of concept
3. Test with real project
4. Iterate based on feedback
5. Complete remaining phases
