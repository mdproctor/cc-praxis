# Handover — 2026-04-14

**Branch:** main
**Head:** a39139c

---

## What Changed This Session

**Design journal model** — replaced the full-copy `design/DESIGN.md` workspace model
with `design/JOURNAL.md`: a cohesive narrative of design changes during an epic, with
structured `§Section` anchors for three-way merge at close. SHA baseline recorded at
`epic-start` enables true three-way merge (base + journal + current project).

**Three new specs:**
- `docs/superpowers/specs/2026-04-13-design-journal-design.md`
- `docs/superpowers/specs/2026-04-13-artifact-routing-design.md`
- `docs/superpowers/specs/2026-04-14-epic-lifecycle-design.md`

**Implemented and merged:**
- `epic-start` and `epic-close` skills (new) — full workspace branch lifecycle
- `java-update-design` + `update-primary-doc` — workspace mode detection, JOURNAL.md entry format
- `handover` — `journal-entry` item added to wrap checklist (OFF by default)
- All skill paths updated: `adr/`, `blog/`, `snapshots/`, `IDEAS.md` (workspace-relative)
- Session-start hook: HANDOVER.md read prompt + workspace check
- `workspace-init` Step 3b removed (no longer copies project DESIGN.md)
- INDEX.md maintenance in `adr`, `design-snapshot`, `write-blog`
- Issue #49 closed

**446 tests passing. 48 skills synced.**

---

## Immediate Next Step

**Smoke tests in a real workspace session:**
1. `/epic-start` → verify `design/JOURNAL.md` and `design/.meta` created with SHA
2. `java-update-design` → verify journal entry written (not project DESIGN.md)
3. `/epic-close` (dry run, no artifacts) → verify close plan presented with "all / step" prompt

---

## References

| Context | Where |
|---------|-------|
| Design journal spec | `docs/superpowers/specs/2026-04-13-design-journal-design.md` |
| Artifact routing spec | `docs/superpowers/specs/2026-04-13-artifact-routing-design.md` |
| Epic lifecycle spec | `docs/superpowers/specs/2026-04-14-epic-lifecycle-design.md` |
| Implementation plan | `docs/superpowers/plans/2026-04-14-epic-lifecycle.md` |
| epic-start skill | `epic-start/SKILL.md` |
| epic-close skill | `epic-close/SKILL.md` |
| Blog entry | `docs/_posts/2026-04-14-mdp01-the-model-comes-together.md` |
| Parked ideas | `IDEAS.md` (blog article/note types, complex routing) |
| Previous handover | `git show HEAD~1:HANDOFF.md` |
