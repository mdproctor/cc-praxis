# HANDOVER.md Reference

Used by `session-handoff` Step 5 (write HANDOVER.md) and by the next session
when resuming work. Contains the template, routing table, and git read patterns.

---

## HANDOVER.md Template

```markdown
# Handover — YYYY-MM-DD

**Head commit:** `<hash>` — <subject line>
**Previous handover:** `git show HEAD~1:HANDOVER.md` | diff: `git diff HEAD~1 HEAD -- HANDOVER.md`

## What Changed This Session

- <only things that changed — not a general summary>
- <if nothing changed in a section, say so and skip it>

## State Right Now

<Write only if changed from previous handover.>
<If unchanged: *Unchanged — `git show HEAD~1:HANDOVER.md`*>

## Immediate Next Step

<Always write this explicitly — it changes every session.>
<Be specific: not "continue work" but "run X and update section Y".>

## Open Questions / Blockers

<Write only if changed. If unchanged: *Unchanged — see previous handover.*>

## References

Read only what the task requires. Use git show / grep for surgical reads.

| Context | Where | Retrieve with |
|---------|-------|---------------|
| Design state | `docs/design-snapshots/<latest>.md` | `cat` that file |
| Project narrative | `docs/write-blog/<latest>.md` | `cat` that file |
| Technical gotchas | `~/claude/knowledge-garden/GARDEN.md` | index only; detail on demand |
| Open ideas | `docs/ideas/IDEAS.md` | `cat` that file |
| Previous handover | git history | `git show HEAD~1:HANDOVER.md` |
| Specific section of prev | git history | `git show HEAD~1:HANDOVER.md \| grep -A 10 "## Section"` |

## Environment

<Only if non-obvious and changed since CLAUDE.md. Omit if nothing unusual.>
```

---

## What Goes in HANDOVER.md vs Other Files

| Information | Where it belongs |
|-------------|-----------------|
| What changed this session | HANDOVER.md — write in full |
| What didn't change this session | HANDOVER.md — reference previous via git |
| Why a design decision was made | write-blog or adr |
| Current architecture | design-snapshot (reference from handover) |
| Cross-project technical gotcha | garden (reference from handover) |
| Undecided possibilities | idea-log (reference from handover) |
| Permanent conventions | CLAUDE.md (auto-loaded, don't repeat) |

---

## Surgical git Reads for the Next Session

When the next session needs context from a previous handover, use targeted
git commands rather than loading the whole file:

```bash
# Just the "Open Questions" section from two sessions ago
git show HEAD~2:HANDOVER.md | grep -A 15 "## Open Questions"

# What the "State Right Now" section said last week
git log --before="7 days ago" -1 --format="%H" -- HANDOVER.md \
  | xargs -I{} git show {}:HANDOVER.md | grep -A 10 "## State"

# Did anything change in the References table between sessions?
git diff HEAD~1 HEAD -- HANDOVER.md | grep "^[+-]" | grep "References" -A 20
```

The principle: prefer `grep -A N` over reading entire files. Git diffs show
only changed lines. Section reads are cheaper than full-file reads.

---

## When to Load a Previous Handover

Load `git show HEAD~1:HANDOVER.md` when:
- The current handover marks several sections as "Unchanged" and the task
  requires that context — retrieve only the relevant section
- The current handover is stale (>7 days) and an intermediate one might
  have more recent state

Do NOT preemptively load previous handovers at session start. Check freshness
first; load only when a specific task demands the missing context.
