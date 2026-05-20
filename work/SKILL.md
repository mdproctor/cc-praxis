---
name: work
description: >
  Use when the user says "work", "work end", or "work pause" — detects current
  branch state and routes to the correct work lifecycle skill automatically.
  "work" alone starts or resumes. "work end" closes the branch. "work pause"
  saves state and returns to main. Replaces needing to know which lifecycle
  skill to invoke.
---

# work

Unified entry point for the work lifecycle. Detects state and routes to the
correct skill — developer says `work` to begin, `work end` to close,
`work pause` to save and switch.

---

## Routing

**Step 1 — Parse the invocation**

| Invocation | Route to |
|------------|---------|
| `work` or `work start` | → detect state (Step 2) |
| `work end` | → **work-end** immediately |
| `work pause` | → **work-pause** immediately |
| `work resume` | → **work-resume** immediately |

**Step 2 — Detect state (for `work` alone)**

```bash
# Check for paused branch marker
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md 2>/dev/null | head -1 | sed "s/.*\`\(.*\)\`.*/\1/")
PAUSED_EXISTS=$([ -f "${WORKSPACE}/main/.paused" ] || [ -f ".paused" ] && echo "yes" || echo "no")

# Check current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
IS_MAIN=$([ "$CURRENT_BRANCH" = "main" ] && echo "yes" || echo "no")
```

| Detected state | Action |
|---------------|--------|
| On main, no `.paused` marker | → **work-start** — begin new work |
| On main, `.paused` marker exists | → **work-resume** — return to paused branch |
| On a feature branch | → ask: "End this branch or pause and switch?" |

**Step 3 — On feature branch: ask once**

> "You're on `<branch-name>`. What do you want to do?
> 1. **end** — close this branch, merge journal, close issue, return to main
> 2. **pause** — save state, switch to main (resume later)"

Route to work-end or work-pause based on answer.

---

## Skill Chaining

**Routes to:**
- `work-start` — when beginning new work from main
- `work-resume` — when returning to a paused branch from main
- `work-end` — when closing a completed branch
- `work-pause` — when saving state to switch to something else

**This skill does not implement the lifecycle itself** — it detects state and
delegates. All logic lives in the individual lifecycle skills.
