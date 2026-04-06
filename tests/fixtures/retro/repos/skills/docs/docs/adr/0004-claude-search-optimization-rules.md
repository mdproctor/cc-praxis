# ADR-0004: Claude Search Optimization (CSO) Rules for Skill Frontmatter

**Status:** Accepted

**Date:** 2026-03-30

**Context:** Universal across all skill repositories using Claude Code skills

---

## Decision

Skill frontmatter descriptions must focus on **WHEN to use** (trigger conditions/symptoms), not **HOW it works** (workflow steps/implementation).

---

## Context

### The Problem

Early skill implementations included workflow summaries in the description field:

```yaml
---
name: execute-plan
description: Use when executing plans - dispatches subagent per task with code review between tasks
---
```

**What happened:**
- Claude read the description in the skill list
- Saw "dispatches subagent per task with code review"
- Followed that summary instead of reading the full skill body
- Result: Expensive wallpaper (~400 lines of skill content ignored)

**Token waste measured:**
- 8 skills with workflow summaries
- ~5KB per skill body not read
- ~40KB wasted per conversation
- Plus duplication: same info in description AND body = ~81KB total waste

### Root Cause

**The description field serves two purposes:**
1. **Discovery:** Help Claude find the right skill (WHEN to use it)
2. **Visibility:** Shown in skill list (always loaded in context)

**The failure mode:**
When descriptions contain workflow steps, they become **micro-skills** - Claude thinks "I know how to do this from the description, no need to read the full skill."

This creates a paradox:
- **Too vague:** Claude doesn't know when to invoke
- **Too detailed:** Claude bypasses the skill body
- **Sweet spot:** Trigger conditions without revealing workflow

## Decision Drivers

- **Token efficiency** - Skill bodies are expensive; don't load them if unused
- **Skill effectiveness** - Skills only work if Claude reads the full content
- **Discoverability** - Descriptions must still help Claude find the right skill
- **Consistency** - All skills should follow the same pattern
- **Validation** - Need automated way to detect violations

## Considered Options

### Option 1: Allow Workflow Summaries (REJECTED)

**Approach:** Let descriptions include step-by-step workflow

**Pros:**
- Easy to write
- Self-contained (description tells whole story)

**Cons:**
- ❌ Claude bypasses skill body (~40KB waste per conversation)
- ❌ Skill becomes "expensive wallpaper"
- ❌ Duplication (same info in description and body)
- ❌ Maintenance burden (update in two places)

### Option 2: Separate Trigger/Description Fields (REJECTED)

**Approach:** Two fields - one for triggers, one for workflow

```yaml
---
name: execute-plan
triggers: Use when you have implementation plans with independent tasks
description: Dispatches subagent per task with code review between tasks
---
```

**Pros:**
- Explicit separation of concerns

**Cons:**
- ❌ Adds complexity to frontmatter schema
- ❌ Still loads workflow description in context
- ❌ Doesn't solve the "Claude reads summary instead of body" problem
- ❌ Requires updating all existing skills

### Option 3: Auto-Generate Descriptions from Skill Body (REJECTED)

**Approach:** Script parses skill body, generates description automatically

**Pros:**
- Zero manual description writing
- Always in sync

**Cons:**
- ❌ Can't capture triggering conditions (requires understanding user intent)
- ❌ Summary generation is hard (what to include/exclude?)
- ❌ Loses human judgment about WHEN to use skill
- ❌ Still risk of workflow leakage into description

### Option 4: CSO Rules - Focus on WHEN (ACCEPTED)

**Approach:** Descriptions describe triggering conditions/symptoms, never workflow

**Good examples:**
```yaml
# ✅ Triggering conditions
description: Use when executing implementation plans with independent tasks in the current session

# ✅ Symptoms
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes

# ✅ User request patterns
description: Use when user asks "Can Claude...", "Does Claude...", "How do I..." about Claude Code features
```

**Bad examples:**
```yaml
# ❌ Workflow summary
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ❌ Implementation details
description: Use when creating skills - validates frontmatter, runs evals, benchmarks with variance analysis

# ❌ Tool listings
description: Use when debugging - uses Bash, Read, Grep, and Agent tools to investigate
```

**Pros:**
- ✅ Claude knows WHEN to invoke without knowing HOW
- ✅ Skill body must be read to learn workflow
- ✅ No duplication (description = triggers, body = workflow)
- ✅ Automated validation possible (detect workflow keywords)
- ✅ Saved ~81KB token waste per conversation

**Cons:**
- ⚠️ Harder to write (requires thinking about triggering conditions)
- ⚠️ May need iteration to get right

## Decision Outcome

**Chosen option:** CSO Rules - Focus on WHEN, not HOW

**Implementation:**

### 1. CSO Validation Rules

**Descriptions MUST:**
- Start with "Use when..."
- Describe triggering conditions or symptoms
- Be under 500 characters
- Use third person (no "I" or "you")

**Descriptions MUST NOT:**
- Contain workflow keywords: "step", "then", "invoke", "run", "execute", "dispatch"
- List tool names: "Bash", "Read", "Edit", "Agent"
- Describe HOW it works
- Summarize the workflow

### 2. Automated Validation

**Script:** `scripts/validate_cso.py`

```python
WORKFLOW_KEYWORDS = ["step", "then", "invoke", "run", "execute", "dispatch"]
TOOL_NAMES = ["Bash", "Read", "Edit", "Write", "Grep", "Agent"]

def validate_cso(description):
    # Check for workflow keywords
    for keyword in WORKFLOW_KEYWORDS:
        if keyword in description.lower():
            return f"CRITICAL: Description contains workflow keyword: {keyword}"

    # Check for tool names
    for tool in TOOL_NAMES:
        if tool in description:
            return f"WARNING: Description lists tool name: {tool}"

    return "OK"
```

**Exit code 1 on CRITICAL violations.**

### 3. Pre-Commit Integration

**Via skill-validation.md workflow:**
```markdown
### Frontmatter Structure (CRITICAL)

**CSO violations are CRITICAL** — descriptions that summarize workflow
cause Claude to skip reading the skill body.

❌ Bad: `description: Use when executing plans - dispatches subagent per task`
✅ Good: `description: Use when executing implementation plans with independent tasks`
```

### 4. Mass Fix Applied

**Fixed 8 skills:**
- superpowers:executing-plans
- superpowers:subagent-driven-development
- superpowers:systematic-debugging
- skill-creator
- java-code-review
- quarkus-flow-dev
- And others

**Token savings:** ~81KB per conversation

## Consequences

### Positive

✅ **Massive token savings** - ~81KB per conversation (8 skills fixed)
✅ **Skills actually work** - Claude reads full body, not just description
✅ **No duplication** - Description and body serve different purposes
✅ **Better discoverability** - Focus on WHEN makes it easier to find right skill
✅ **Automated enforcement** - CSO validation catches violations pre-commit
✅ **Pattern established** - All future skills follow same rule

### Negative

⚠️ **Harder to write** - Requires thinking about triggering conditions
⚠️ **Less self-contained** - Can't understand skill from description alone
⚠️ **Required rework** - All existing skills needed description updates

### Neutral

📝 **Validation needs refinement** - Some false positives on edge cases
📝 **Examples help** - Good/bad examples in CLAUDE.md guide authors

## Validation

Success criteria for this ADR:

- ✅ CSO rules documented in CLAUDE.md § Frontmatter Requirements
- ✅ Automated validation (scripts/validate_cso.py)
- ✅ Pre-commit checks (skill-validation.md workflow)
- ✅ All existing skills updated to comply
- ✅ Examples provided (good vs bad descriptions)
- ✅ Measured token savings (~81KB)

## Real-World Examples

### Before CSO Rules (WRONG)

```yaml
---
name: executing-plans
description: >
  Use when executing plans - dispatches subagent per task with code review
  between tasks
---
```

**Problem:** Claude saw "dispatches subagent per task" and followed that summary without reading the 400-line skill body.

### After CSO Rules (CORRECT)

```yaml
---
name: executing-plans
description: >
  Use when you have a written implementation plan to execute in a separate
  session with review checkpoints
---
```

**Result:** Claude knows WHEN to use it (has written plan, needs separate session, wants review checkpoints) but must read the skill to learn HOW to execute.

## Related Decisions

- **Issue #001:** CSO violation in superpowers:execute-plan (original discovery)
- **ADR-0001:** Documentation Completeness Must Be Universal (same root cause: missing validation)
- **Skill-validation.md:** Frontmatter validation workflow

## Notes

**What we learned:**

The description field is a **discovery aid**, not a **mini-skill**. Its job is to help Claude find the right skill, not to replace the skill body.

**Key principle:**
> "Descriptions are for WHEN to use (trigger conditions). Skill bodies are for HOW to use (workflow steps)."

**Token economics matter:**
- Loading unused skill bodies is expensive (~5KB each)
- Bypassing loaded skill bodies wastes that investment
- CSO rules ensure: load it → use it, or don't load it at all

**Quote that established this pattern:**
> "If the description tells Claude HOW to do it, Claude won't read the skill to learn HOW. Then the skill becomes expensive wallpaper - 400 lines loaded but ignored."
