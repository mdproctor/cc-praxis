# ADR-0005: No AI Attribution Unless Explicitly Requested

**Status:** Accepted

**Date:** 2026-03-30

**Context:** Universal across all commit workflows (git-commit, java-git-commit, custom-git-commit)

---

## Decision

Commit messages describe WHAT changed and WHY, without mentioning WHO or WHAT wrote the code, unless the user explicitly requests attribution.

**Specifically:**
- No `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`
- No `Generated-by:`, `AI-assisted:`, or tool mentions
- No meta-commentary about how the commit was created
- Commit messages focus purely on the change itself

---

## Context

### The Problem

Early commit implementations auto-added attribution:

```
feat(api): add user authentication

Implemented JWT-based authentication with refresh tokens.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**User feedback:**
> "I don't want AI attribution in my commits by default. If I want to acknowledge Claude's help, I'll add it myself."

**Philosophical question:** Who owns the commit?
- Is it the user's work (they directed, reviewed, approved)?
- Is it Claude's work (Claude wrote the code)?
- Is it collaborative (both contributed)?

**The answer affects:**
- Git blame (who to ask about this change?)
- Commit history (clean vs cluttered?)
- Professional perception (AI-assisted stigma?)
- Legal/attribution (who owns the code?)

## Decision Drivers

- **User ownership** - Most users want full ownership of commits
- **Clean history** - Attribution adds noise to git log
- **Professional standards** - Some workplaces discourage AI attribution
- **Flexibility preserved** - Users who want attribution can still add it
- **Simplicity** - Default should be what most users want
- **Honesty without burden** - Being transparent shouldn't be forced

## Considered Options

### Option 1: Always Add Attribution (REJECTED)

**Approach:** Every commit includes `Co-Authored-By: Claude`

**Pros:**
- Transparent about AI assistance
- Acknowledges tool contribution
- Consistent across all commits

**Cons:**
- ❌ Most users don't want it by default
- ❌ Clutters git history
- ❌ Some workplaces discourage AI attribution
- ❌ Can't opt out easily
- ❌ Treats tool like a person (philosophical issue)

**Real user feedback:**
> "Please don't add Co-Authored-By to my commits. I'm the author. Claude is a tool I used, not a co-author."

### Option 2: Make Attribution Opt-Out (REJECTED)

**Approach:** Add attribution by default, but let users disable via flag

```bash
git-commit --no-attribution
```

Or via CLAUDE.md:
```markdown
## Commit Preferences

**Attribution:** disabled
```

**Pros:**
- Transparent by default
- Can be disabled if needed

**Cons:**
- ❌ Still defaults to unwanted behavior
- ❌ Requires user action to get clean commits
- ❌ Most users would disable it (wrong default)
- ❌ Configuration overhead

### Option 3: Add Subtle Metadata (REJECTED)

**Approach:** Add attribution in commit trailer, not Co-Authored-By

```
feat(api): add user authentication

Implemented JWT-based authentication with refresh tokens.

Tool-Assisted: Claude Code
```

**Pros:**
- Less prominent than Co-Authored-By
- Still transparent

**Cons:**
- ❌ Still attribution (just less obvious)
- ❌ Still unwanted by most users
- ❌ Non-standard git trailer

### Option 4: No Attribution Unless Requested (ACCEPTED)

**Approach:** Commit messages describe the change, nothing more

**Default behavior:**
```
feat(api): add user authentication

Implemented JWT-based authentication with refresh tokens.
Tests added for login flow and token refresh.
```

**When user requests attribution:**
```
User: "commit with attribution"

feat(api): add user authentication

Implemented JWT-based authentication with refresh tokens.
Tests added for login flow and token refresh.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Pros:**
- ✅ Clean commits by default
- ✅ User maintains full ownership
- ✅ No professional stigma risk
- ✅ Flexibility preserved (can add if wanted)
- ✅ Matches user expectations
- ✅ Focuses on WHAT changed, not WHO wrote it

**Cons:**
- ⚠️ Less transparent about AI assistance (but user controls this)
- ⚠️ Could be seen as hiding AI use (but it's opt-in, not deceptive)

## Decision Outcome

**Chosen option:** No Attribution Unless Explicitly Requested

**Implementation:**

### 1. Core Rule in All Commit Skills

**In git-commit/SKILL.md:**
```markdown
## Core Rules

- **Never add attribution to commit messages** unless the user explicitly requests it:
  - No `Co-Authored-By: Claude` or similar AI attribution
  - No `Generated-by:`, `AI-assisted:`, or tool mentions
  - No meta-commentary about how the commit was created
  - Commit messages describe WHAT changed and WHY, not WHO/WHAT wrote it
```

**Applies to:**
- `git-commit`
- `java-git-commit`
- `custom-git-commit`

### 2. Explicit Request Pattern

**User can request attribution:**
- "commit with attribution"
- "commit and credit Claude"
- "add co-author Claude"

**Then add:**
```
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### 3. Commit Message Focus

**What commit messages should contain:**
- Type (feat, fix, refactor, etc.)
- Scope (optional, if meaningful)
- Description (what changed, imperative mood)
- Body (why changed, context, trade-offs)
- Footer (Fixes #123, BREAKING CHANGE, etc.)

**What commit messages should NOT contain:**
- Attribution (unless requested)
- Tool mentions
- Process commentary ("This was generated by...")
- Meta-information about authorship

## Consequences

### Positive

✅ **User ownership** - Commits are the user's work
✅ **Clean history** - No attribution noise in git log
✅ **Professional standards** - Meets workplace requirements
✅ **Flexibility** - Users can add attribution when they want
✅ **Focus on content** - Commit messages describe changes, not process
✅ **Reduced friction** - No need to configure "no attribution" mode
✅ **Philosophical clarity** - Tool vs author distinction clear

### Negative

⚠️ **Less transparent** - AI assistance not visible by default
⚠️ **Could mislead** - Might imply user wrote all code manually
⚠️ **Social expectations** - Some communities value attribution

### Neutral

📝 **User decides** - Transparency level is user choice
📝 **Context-dependent** - Attribution may be appropriate in some projects
📝 **Evolving norms** - Social expectations about AI attribution may change

## Validation

Success criteria for this ADR:

- ✅ No attribution in default commits
- ✅ Core rule documented in all commit skills
- ✅ Explicit request pattern works (user can opt-in)
- ✅ Common Pitfalls section warns against auto-attribution
- ✅ Examples show commits without attribution

## Real-World Examples

### Wrong (Old Behavior)

```
feat(auth): add JWT authentication

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Problem:** User didn't ask for attribution, but got it anyway.

### Right (Current Behavior)

**Default commit:**
```
feat(auth): add JWT authentication

Implemented token-based auth with refresh flow.
Tests cover login, logout, and token refresh.
```

**User explicitly requests attribution:**
```
User: "commit this with attribution to Claude"

feat(auth): add JWT authentication

Implemented token-based auth with refresh flow.
Tests cover login, logout, and token refresh.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Related Decisions

- **Conventional Commits 1.0.0** - Focus on commit content, not authorship
- **Git-commit Core Rules** - Established no-attribution principle
- **Professional standards** - Many workplaces prefer no AI attribution

## Notes

**What we learned:**

Attribution is a personal choice, not a technical requirement. Defaulting to attribution assumes users want to advertise AI assistance, but most prefer clean commits.

**Key principle:**
> "Commit messages describe WHAT changed and WHY, not WHO or WHAT wrote it."

**The philosophical stance:**
- Claude is a tool, like an IDE, linter, or code formatter
- We don't add "Co-Authored-By: IntelliJ IDEA" to commits
- We don't add "Generated-by: Copilot" to code
- Claude should be treated the same: useful tool, not co-author

**User ownership principle:**
The user directs the work, reviews the code, approves the changes, and takes responsibility for the commit. That makes them the author, regardless of which tools they used.

**Flexibility preserved:**
Users who want to acknowledge Claude's help can do so explicitly. This respects both transparency advocates and privacy advocates.

**Quote from commit guidelines:**
> "If the user didn't ask for attribution, don't add it. Their commit, their choice."
