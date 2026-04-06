# Handover — 2026-04-06

**Head commit:** `b1c929a` — docs: add project blog entry 2026-04-06-03-garden-remembers-itself
**Previous handover:** (none — first handover)

## What Changed This Session

- **write-blog**: four-layer writing architecture (mandatory-rules.md, common-voice.md, personal guide, invocation overrides); pre-draft gate enforced; Step 0c gates on CLAUDE.md style guide pointer before drafting; same-day YYYY-MM-DD-NN filename convention; systematic review fixed 9 issues
- **garden**: GE-IDs at submission time; three-tier duplicate detection (light/medium/DEDUPE); CHECKED.md sparse pair log; DISCARDED.md for reconciliation; drift-based DEDUPE trigger (threshold 10); validate_garden.py integrity checker; TEST-SCENARIOS.md; 33 existing submissions retroactively assigned GE-0001–GE-0033; 2 new submissions GE-0034–GE-0035
- **session-handoff**: wrap checklist (garden→claude-md→snapshot→blog) with all/toggle support
- **sync-local**: new dev-only skill with `/sync-local` slash command; developer-only pattern documented in CLAUDE.md
- **CLAUDE.md**: Writing Style Guide mandatory requirement added; developer-only skills pattern; defaults/ directory pattern; /sync-local noted
- **All 6 blog entries** renamed to YYYY-MM-DD-NN-title.md convention
- **First design snapshot**: `docs/design-snapshots/2026-04-06-writing-infrastructure-and-garden.md`
- **3 blog entries today**: 01-writing-about-itself, 02-writing-rules-get-teeth, 03-garden-remembers-itself

## State Right Now

- **Garden**: 35 submissions ready to merge (GE-0001–GE-0035); validator passes clean; CHECKED.md empty; drift counter at 0; merge session needed (full context budget)
- **Stale install**: `~/.claude/skills/knowledge-garden/` — old pre-rename directory, safe to delete
- **cc-praxis**: 45 skills; all synced; working tree clean

## Immediate Next Step

Run a dedicated garden MERGE session: `cd ~/claude/knowledge-garden && garden merge` — assigns GE-IDs to existing entries, runs light duplicate checks, populates CHECKED.md, integrates all 35 submissions.

## Open Questions / Blockers

- Image index (`docs/images/IMAGE-INDEX.md`) — currently project-level by decision; revisit if images turn out to be reusable across projects
- `publish-blog` skill — series navigation deferred to it; not yet built
- v1.0.1 tag — significant additions since v1.0.0; consider after garden merge

## References

| Context | Where | Retrieve with |
|---------|-------|---------------|
| Design state | `docs/design-snapshots/2026-04-06-writing-infrastructure-and-garden.md` | `cat` that file |
| Project narrative | `docs/blog/2026-04-06-03-garden-remembers-itself.md` | `cat` that file |
| Technical gotchas | `~/claude/knowledge-garden/GARDEN.md` | index only; detail on demand |
| Garden validator | `~/claude/knowledge-garden/scripts/validate_garden.py` | `python3 ... --verbose` |
| Garden submissions | `~/claude/knowledge-garden/submissions/` | `ls` to list |
| Open ideas | `docs/ideas/IDEAS.md` | `cat` that file |
