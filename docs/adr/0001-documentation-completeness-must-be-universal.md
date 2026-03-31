# ADR-0001: Documentation Completeness Must Be Universal, Not Project-Specific

**Status:** Accepted
**Date:** 2026-03-30
**Deciders:** Mark Proctor, Claude (Sonnet 4.5)
**Context:** Regression where validation framework was added to 4 sync workflows but README.md documentation was not updated

---

## Context and Problem Statement

When implementing the universal document validation framework (scripts/validate_document.py), the framework was integrated into all 4 sync workflows (update-claude-md, update-design, custom-update-primary-doc, readme-sync.md) but the README.md was not updated to document this new capability.

**Root cause analysis revealed:**
1. SKILL.md files were modified (4 sync workflows)
2. readme-sync.md workflow should have been invoked (MANDATORY when SKILL.md files staged)
3. Workflow was skipped with rationalization "just internal changes, not significant enough"
4. This bypassed the process that would have caught the missing documentation

**The deeper problem:** This failure pattern is not specific to skills repositories. The same rationalization ("just internal, not worth documenting") can occur in:
- **type: java** - Infrastructure changes to update-design, missing documentation in DESIGN.md
- **type: custom** - Infrastructure changes to custom-update-primary-doc, missing documentation in primary doc
- **type: generic** - Infrastructure changes to update-claude-md, missing documentation anywhere

**Key insight from user:** "you have fixed it for this scripts project, but surely these are universal too and you are likely to make the same quality review mistakes in any project type?"

## Decision Drivers

- **Regression prevention across ALL project types** - not just skills repositories
- **Process failures are universal** - rationalization happens regardless of project type
- **Infrastructure changes need documentation** - new scripts, validation, automation, capabilities
- **AI assistants need explicit checks** - won't naturally think "should I document this?" without prompting
- **User shouldn't need to catch these** - automation should prevent, not detect after the fact

## Considered Options

### Option 1: Fix only for skills repositories (REJECTED)
Add framework change detection to readme-sync.md only.

**Pros:**
- Solves the immediate regression
- Minimal changes required

**Cons:**
- Same failure will occur in java/custom/generic projects <!-- nocheck:project-types -->
- Doesn't address root cause (rationalization)
- Leaves user vulnerable in other project types

### Option 2: Document the pattern that needs fixing (REJECTED)
Add issue to known-issues.md, add to manual checklist.

**Pros:**
- Raises awareness of the problem

**Cons:**
- Doesn't prevent the failure
- Relies on manual checking (which was already bypassed)
- Doesn't scale to all project types

### Option 3: Make documentation completeness checks universal (ACCEPTED)
Add framework change detection to ALL sync workflows, create universal pre-commit checks, establish meta-rule about considering universality.

**Pros:**
- Prevents regression across all project types
- Addresses root cause (makes checks automatic, not optional)
- Scales to any future project type
- Establishes principle for future improvements

**Cons:**
- More changes required initially
- Needs coordination across 4 sync workflows

## Decision Outcome

**Chosen option:** Option 3 - Make documentation completeness checks universal

**Implementation:**

1. **Add framework change detection to ALL sync workflows:**
   - update-claude-md (all project types)
   - update-design (type: java)
   - custom-update-primary-doc (type: custom)
   - readme-sync.md (type: skills) - already enhanced

2. **Make workflow invocation truly mandatory:**
   - git-commit Step 2b: Strengthen language for readme-sync.md (done)
   - Similar strengthening for other sync invocations

3. **Create universal pre-commit documentation checklist:**
   - Applies to ALL project types
   - Checks for new scripts, validation, framework changes
   - Cannot be rationalized away

4. **Establish meta-rule: "Consider universality first"**
   - Before applying any fix, ask: "Should this be universal?"
   - If uncertain, ask the user
   - Prevents project-type-specific fixes when universal fix is better

## Consequences

### Positive

- ✅ **Prevents regressions across all project types** - not just skills repos
- ✅ **Reduces user burden** - don't need to catch missing documentation
- ✅ **Scales to future project types** - any new type gets same protections
- ✅ **Establishes good precedent** - future improvements consider universality
- ✅ **Self-documenting** - each sync workflow documents what changes warrant updates

### Negative

- ⚠️ **More verbose workflows** - each sync workflow has additional step
- ⚠️ **Could have false positives** - framework change detection may over-trigger
- ⚠️ **Requires discipline** - meta-rule only works if followed

### Neutral

- 📝 **Validation script needs refinement** - currently has false positives on code examples
- 📝 **May discover more gaps** - universal checks may reveal other missing documentation

## Validation

Success criteria for this ADR:

- ✅ All 4 sync workflows have framework change detection
- ✅ Universal documentation completeness checks exist
- ✅ Meta-rule documented in CLAUDE.md
- ✅ Pre-commit checklist updated with universal checks
- ✅ Test: Modify infrastructure, verify documentation is caught

## Related Decisions

- Issue #002: README.md corruption (341 lines of duplicates) - RESOLVED
- Document Sync Quality Assurance framework (CLAUDE.md § Document Sync Quality Assurance)
- Quality Assurance Framework (CLAUDE.md § Quality Assurance Framework)

## Notes

**What we learned:**
- Project-type-specific fixes are often band-aids for universal problems
- Rationalization ("just internal changes") is a universal failure mode
- Process bypasses happen regardless of project type
- User's question "surely these are universal too?" was the key insight

**Quote from user that triggered this ADR:**
> "you have fixed it for this scripts project, but surely these are universal too and you are likely to make the same quality review mistakes in any project type?"

**Meta-principle established:**
> "Before applying any fix, ask: should this be universal? If unsure, ask the user."
