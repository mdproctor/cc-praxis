---
name: work
description: >
  Use when the user says "work", "work end", "work pause", or "work resume" —
  detects current branch state and routes to the correct work lifecycle skill
  automatically. "work" alone starts new work or shows the pause stack.
  "work end" closes the branch. "work pause" saves state. "work resume" shows
  the stack and returns to a paused branch. Replaces needing to know which
  lifecycle skill to invoke.
---

# work

Unified entry point for the work lifecycle. Detects state and routes to the
correct skill — developer says `work` to begin, `work end` to close,
`work pause` to save and switch, `work resume` to return to paused work.

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
WORKSPACE=$(grep "^\*\*Workspace:\*\*" CLAUDE.md 2>/dev/null | head -1 | sed "s/.*\`\(.*\)\`.*/\1/")
STACK_FILE="$WORKSPACE/design/.pause-stack"
STACK_DEPTH=$(grep -c "^- branch:" "$STACK_FILE" 2>/dev/null || echo 0)
CURRENT_BRANCH=$(git -C "$WORKSPACE" branch --show-current 2>/dev/null)
IS_MAIN=$([ "$CURRENT_BRANCH" = "main" ] && echo "yes" || echo "no")
```

| Detected state | Action |
|---------------|--------|
| On main, stack empty | → **work-start** — begin new work |
| On main, stack has 1 entry | → **work-resume** automatically |
| On main, stack has 2+ entries | → show stack picker (Step 3) |
| On a feature branch | → ask: end or pause? (Step 4) |

**Step 3 — Stack picker (on main, 2+ paused branches)**

Show all paused branches with age and note:

```
You have <N> paused branches:
  1. <branch>  #<issue>  paused <duration> ago
  2. <branch>  #<issue>  paused <duration> ago
  ...

Resume one, or start something new? (1 / 2 / ... / new)
```

- Number → **work-resume** with that branch pre-selected
- `new` → **work-start**

If stack depth > 3, prefix with: `⚠️  Stack has <N> paused branches — consider closing some before adding more.`

**Step 4 — On feature branch: ask once**

> "You're on `<branch-name>`. What do you want to do?
> 1. **end** — close this branch, merge journal, close issue, return to main
> 2. **pause** — commit WIP, push to stack, switch to main (resume later)"

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
