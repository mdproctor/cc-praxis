---
description: Write a project blog entry, or sweep all work to date as a series. With no argument, triggers a retrospective sweep of git history — proposes phases for selection, then writes confirmed entries in sequence. With an argument, uses that as context for a single entry — proposes what it thinks you want, refines with your input, then writes.
---

Invoke the `write-blog` skill.

**No argument** — triggers RETROSPECTIVE mode: scans git history, proposes phases as a numbered selection list (all ticked by default), writes confirmed entries one at a time.

**With context** — single entry mode: uses the provided text as the starting point, proposes the entry type and focus, refines with your input, then writes.

Examples:
- `/write-blog` → retrospective sweep of all work to date
- `/write-blog the web installer phase` → draft an entry about the web installer work
- `/write-blog we just fixed the bundle state bug` → capture today's pivot
