# ADR-0009: Automatic Workflow Orchestration by Project Type

**Status:** Accepted

**Date:** 2026-03-30

**Context:** Universal across all commit workflows

---

## Decision

Commit skills automatically orchestrate validation, documentation sync, and commit workflows based on project type declared in CLAUDE.md. User says "commit", system determines what needs to happen.

**Orchestration patterns:**
- **type: skills** → skill-review → git-commit → readme-sync + update-claude-md
- **type: java** → java-code-review → java-git-commit → java-update-design + update-claude-md
- **type: custom** → custom-git-commit → update-primary-doc + update-claude-md
- **type: generic** → git-commit → update-claude-md (if exists)

---

## Context

### The Problem

Early commit workflows required explicit steps:

**Manual workflow (error-prone):**
```
User: "review my code"
Claude: [runs java-code-review]

User: "update the design doc"
Claude: [runs java-update-design]

User: "update CLAUDE.md"
Claude: [runs update-claude-md]

User: "now commit"
Claude: [creates commit]
```

**What went wrong:**
1. Users forget steps (skip review → buggy code committed)
2. Users skip documentation (DESIGN.md becomes stale)
3. Documentation drift (README.md not updated when skills change)
4. Inconsistent quality (some commits reviewed, others not)
5. Cognitive load (remember all steps in correct order)

**Real scenario:**
```
User modifies 3 skills, commits without updating README.
README.md now has stale skill descriptions.
Next user reads README, gets confused by missing skills.
Discovery: README was last updated 2 months ago, 10 skills added since.
```

**The question:** How to ensure quality gates without burdening users?

## Decision Drivers

- **Prevent documentation drift** - README, CLAUDE, DESIGN must stay in sync
- **Enforce quality gates** - Code review before commit, not after
- **Reduce cognitive load** - User shouldn't remember all steps
- **Consistency** - Same quality regardless of who commits
- **Flexibility** - User can override when needed (but defaults are good)
- **Type-awareness** - Different projects need different workflows

## Considered Options

### Option 1: Make All Steps Explicit (REJECTED)

**Approach:** User must invoke each step

```
/java-code-review
/java-update-design
/update-claude-md
/git-commit
```

**Pros:**
- Explicit control
- User knows what's happening

**Cons:**
- ❌ Users forget steps (documentation drift)
- ❌ Cognitive load (remember correct order)
- ❌ Inconsistent (some commits skip steps)
- ❌ Error-prone (easy to forget DESIGN.md sync)
- ❌ Manual validation (user must invoke review)

### Option 2: Single Monolithic Commit Skill (REJECTED)

**Approach:** One mega-skill with all logic

```markdown
# mega-commit/SKILL.md

If Java project:
  - Run code review
  - Update DESIGN.md
  - Update CLAUDE.md
  - Commit

If Skills project:
  - Review skills
  - Update README.md
  - Update CLAUDE.md
  - Commit

If Custom project:
  - Update primary doc
  - Update CLAUDE.md
  - Commit
```

**Pros:**
- One skill does everything

**Cons:**
- ❌ Unmaintainable (all logic in one file)
- ❌ Token waste (loads all logic for all project types)
- ❌ Can't reuse components (java-code-review used elsewhere)
- ❌ Hard to test (too many branches)
- ❌ Doesn't scale (adding Python = rewrite entire skill)

### Option 3: No Automation (REJECTED)

**Approach:** Users manually sync when they remember

**Pros:**
- Maximum flexibility

**Cons:**
- ❌ Manual sync gets skipped
- ❌ Documentation drift inevitable
- ❌ Quality inconsistent
- ❌ Defeats purpose of having skills

### Option 4: Automatic Orchestration by Project Type (ACCEPTED)

**Approach:** Commit skills read CLAUDE.md, automatically orchestrate appropriate workflows

**Architecture:**

```
git-commit (router)
  ↓
Read CLAUDE.md → Type: skills
  ↓
Orchestrate:
  1. skill-review (if SKILL.md staged) → BLOCK if CRITICAL
  2. readme-sync.md (if skill changes) → Propose README updates
  3. update-claude-md (if exists) → Propose CLAUDE.md updates
  4. Get user confirmation
  5. Apply updates
  6. Commit with validated message
```

**Workflow patterns:**

| Project Type | Entry Point | Orchestration |
|--------------|-------------|---------------|
| **type: skills** | `git-commit` | skill-review → readme-sync → update-claude-md → commit |
| **type: java** | `java-git-commit` | java-code-review → java-update-design → update-claude-md → commit |
| **type: custom** | `custom-git-commit` | update-primary-doc → update-claude-md → commit |
| **type: generic** | `git-commit` | update-claude-md (if exists) → commit |

**Pros:**
- ✅ Documentation stays in sync automatically
- ✅ Validation happens before commits (can't bypass)
- ✅ User workflow simplified (just say "commit")
- ✅ Consistent quality (all commits follow same process)
- ✅ Type-aware (right workflow for right project)
- ✅ Reusable components (java-code-review used independently)
- ✅ Maintainable (each skill focused on one thing)

**Cons:**
- ⚠️ More complex orchestration
- ⚠️ Requires maintaining coordination between skills
- ⚠️ User loses explicit control (but gains quality)

## Decision Outcome

**Chosen option:** Automatic Orchestration by Project Type

**Implementation:**

### 1. git-commit as Router

**Step 0 — Project Type Detection:**
```markdown
Read CLAUDE.md → Extract type: [skills | java | custom | generic] <!-- nocheck:project-types -->

**Route based on type:**
- type: skills → Continue (handle here)
- type: java → Redirect to java-git-commit
- type: custom → Redirect to custom-git-commit
- type: generic → Continue (basic mode)
```

### 2. Type-Specific Orchestration

**git-commit (type: skills mode):**
```markdown
Step 1: Inspect staged changes
Step 1a: Review skills (if SKILL.md staged)
  → Follow skill-validation.md
  → BLOCK if CRITICAL findings
Step 1c: Validate documentation (all .md files)
  → python scripts/validate_document.py
  → BLOCK if CRITICAL corruption
Step 2: Generate commit message
Step 2a: Sync CLAUDE.md (if exists)
  → Invoke update-claude-md
  → Propose updates
Step 2b: Sync README.md (if skill changes)
  → Follow readme-sync.md
  → Propose updates (MANDATORY, don't skip)
Step 3: Present consolidated proposal
  → Show: staged files, commit message, doc updates
Step 4: User confirms YES
Step 5: Apply updates, commit
```

**java-git-commit (type: java mode):**
```markdown
Step 0a: Verify DESIGN.md exists → BLOCK if missing
Step 1: Check code review status
  → If not done this session: invoke java-code-review
  → If security-critical: chain to java-security-audit
Step 2: Inspect staged changes
Step 3: Generate commit message (Java-specific scopes)
Step 4: Sync DESIGN.md
  → Invoke java-update-design
  → Propose architecture doc updates
Step 5: Sync CLAUDE.md (if exists)
  → Invoke update-claude-md
Step 6: Present consolidated proposal
Step 7: User confirms YES
Step 8: Apply updates, commit
```

**custom-git-commit (type: custom mode):**
```markdown
Step 0: Read Sync Rules from CLAUDE.md
Step 1: Inspect staged changes
Step 2: Generate commit message
Step 3: Sync primary document
  → Invoke update-primary-doc
  → Match files against Sync Rules
  → Propose primary doc updates
Step 4: Sync CLAUDE.md (if exists)
  → Invoke update-claude-md
Step 5: Present consolidated proposal
Step 6: User confirms YES
Step 7: Apply updates, commit
```

### 3. Consolidated Proposal Pattern

**All orchestrators present unified proposal:**
```markdown
## Staged files
[git diff --staged --stat]

## Validation results (if any)
[CRITICAL/WARNING/NOTE findings]

## Proposed commit message
[type(scope): description]

## Proposed documentation updates
[DESIGN.md, CLAUDE.md, README.md, or primary doc updates]

**Does this look good? Reply YES to commit, or tell me what to adjust.**
```

**User sees everything at once, confirms once.**

### 4. Atomic Application

**After user confirms YES:**
1. Apply all documentation updates
2. Validate all updated docs
3. If validation fails → REVERT ALL, report issues
4. Stage updated docs
5. Create commit
6. Confirm success

**All-or-nothing:** Either entire workflow succeeds, or nothing commits.

## Consequences

### Positive

✅ **Documentation stays in sync** - README, CLAUDE, DESIGN updated automatically
✅ **Validation can't be bypassed** - Runs before commit, not optional
✅ **User workflow simplified** - Just say "commit", system handles orchestration
✅ **Consistent quality** - All commits follow same process
✅ **Type-aware** - Right validation for right project type
✅ **Early error detection** - CRITICAL issues block commit (not discovered later)
✅ **Atomic operations** - Either everything succeeds or nothing commits
✅ **Single confirmation** - User reviews entire proposal once

### Negative

⚠️ **Orchestration complexity** - Must coordinate multiple skills
⚠️ **Less explicit** - User may not understand what's happening
⚠️ **Coordination burden** - Changes to one skill may affect others
⚠️ **Testing complexity** - Must test entire orchestration, not just individual skills

### Neutral

📝 **Can be overridden** - User can invoke skills individually if needed
📝 **Requires CLAUDE.md** - Project type must be declared (handled by interactive setup)
📝 **Failure handling** - Clear error messages explain what went wrong

## Validation

Success criteria for this ADR:

- ✅ git-commit routes based on project type
- ✅ Each project type has appropriate orchestration
- ✅ Documentation sync is automatic (not manual)
- ✅ Validation blocks commits on CRITICAL issues
- ✅ User sees consolidated proposal
- ✅ Atomic application (all or nothing)
- ✅ Success confirmed (git log shows commit)

## Real-World Impact

### Before Orchestration

**User adds new skill:**
```
1. Create skill-name/SKILL.md
2. git add skill-name/SKILL.md
3. git commit -m "feat(skills): add skill-name"
4. [Forget to update README.md]
5. README.md now missing new skill
6. Discovery: 3 weeks later when user notices gap
```

### After Orchestration

**Same scenario with orchestration:**
```
1. Create skill-name/SKILL.md
2. User: "commit"
3. git-commit orchestrates:
   → skill-review validates SKILL.md
   → readme-sync detects new skill
   → Proposes README.md update: "Add skill-name to Skills section"
   → Shows consolidated proposal
4. User: "yes"
5. Both SKILL.md and README.md updated atomically
6. README never becomes stale
```

## Design Patterns Used

**Chain of Responsibility:**
- git-commit → type detection → appropriate orchestrator
- Each orchestrator chains to appropriate validation/sync skills

**Template Method:**
- Common structure: validate → sync → propose → confirm → apply
- Type-specific variations fill in the steps

**Strategy:**
- Different orchestration strategies per project type
- Selected at runtime based on CLAUDE.md declaration

## Related Decisions

- **ADR-0001:** Documentation Completeness Must Be Universal (orchestration enforces universal checks)
- **Project Type Taxonomy** (CLAUDE.md § Project Type Awareness)
- **Skill Chaining** (Documented in README § Skill Chaining Reference)

## Notes

**What we learned:**

Automation doesn't mean removing user control - it means removing the burden of remembering all the steps. User still confirms, but system does the orchestration.

**Key principle:**
> "The system should do what the user meant, not just what they said."

User says "commit" → System knows:
- Validate first (catch errors before commit)
- Sync documentation (keep it current)
- Present proposal (user reviews entire change)
- Apply atomically (no partial states)

**Analogy:**
- Manual workflow = Driving stick shift (user controls every gear)
- Orchestrated workflow = Driving automatic (system shifts gears, user steers)

**Quote from user who experienced documentation drift:**
> "I added 10 skills over 2 months. README was never updated. If git-commit had told me 'README needs updating' each time, this wouldn't have happened."

That feedback led to **mandatory** readme-sync invocation.

**The forcing function:**
Orchestration ensures quality gates can't be bypassed through forgetfulness. It's not that users don't care - they're just focused on the code change. Orchestration handles the surrounding concerns.

**Future consideration:**
Could add user preferences:
```markdown
## Commit Preferences

**Auto-sync:** enabled (default)
**Validation:** strict (block on CRITICAL)
**Review:** session (once per session)
```

For now, sensible defaults are correct.
