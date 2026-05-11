# git-squash

Compacts noisy git history into clean, meaningful commits. Eliminates workspace artifacts, CI churn, methodology noise, and redundant fixups while preserving every line of project content.

## What it does

1. **Phase 0 — filter-repo**: strips workspace artifact files (HANDOFF.md, blog entries) from history entirely. Commits that become empty are pruned automatically.
2. **Phase 1 — squash/merge**: collapses noise commits (style, CI, docs follow-ons, WIP) into their parent feature commits. Generates a plan document for author approval before touching anything.
3. **Branch isolation**: all destructive work happens on a working branch. Original history is preserved on a backup branch until explicitly swapped.

## Design decisions

**Why filter-repo before squash, not after**
Commits that only contain workspace artifact files become empty after filtering and are pruned automatically. If squash ran first, those commits would be absorbed into feature commits, mixing project history with workspace noise. Filtering first keeps the two concerns separate.

**Why branch isolation**
Force-pushing rewritten history to a shared branch without review is high-risk. The working branch lets multiple people review the plan document before the swap. The backup branch means the original history is recoverable for weeks.

**Why DROP is wrong for commits with file changes**
A commit message saying "session handover" doesn't mean the commit is empty — it may also touch CLAUDE.md or docs. Dropping it destroys those changes silently. The correct approach: filter the workspace artifact files first (which may make the commit empty), then squash/drop the now-empty commits.

**Why the curated message column must be assessed, not copied**
The plan document's "Curated result" column is the author's record of what they reviewed and decided. Echoing the original message verbatim signals nothing was evaluated. Either an enhanced message or an explicit adequacy note proves the decision happened.

**Why proximity-grouped commits need a forward scan**
A chore commit with zero semantic overlap with its nearest KEEP doesn't belong in that group. Before forcing a wrong attachment, scan forward up to 5 commits for a KEEP with any word overlap. A small standalone chore is cleaner history than a misattributed one.

**Why CI arcs are handled differently from single CI commits**
A single `ci: retrigger` commit is noise. A sequence of 10 CI commits building from scratch to working state is a development arc with a final meaningful outcome. The final commit represents the arc's conclusion and is worth keeping; the intermediates are implementation noise.

**Why stale-ref fixups must anchor to the rename, not the nearest KEEP**
Stale reference commits (`docs: fix stale repo name references post-rename`) are inseparable from the rename that caused them. Anchoring them to whatever KEEP happens to precede them creates semantically wrong groups. They always belong with the rename commit regardless of what intervenes.

**Why the backup naming convention matters**
`backup/pre-squash-<branch>-<YYYYMMDD>` makes backups discoverable and sortable. When multiple squash passes happen over weeks, you need to tell them apart. The cleanup step at the start of each `/git-squash` run surfaces old backups and offers to delete them.

**Why the pre-push hook never runs filter-repo**
Filter-repo is a one-time destructive rewrite that requires author review and explicit approval. The pre-push hook is automatic. Combining the two would mean filter-repo runs silently on every push — completely wrong. The hook only checks for SQUASH/MERGE candidates (message patterns), never touches history.

**Why `printf '%s' "$diff" | wc -l` not `echo "$diff" | wc -l`**
`echo ""` outputs a newline, so `echo "" | wc -l` returns 1 even for empty input. This caused every interval verification sample to show `diff=1` when the actual diff was empty (zero content). `printf '%s'` outputs nothing for empty input, giving the correct count of 0.

## The Project Artifacts section

Skills like git-squash need to know which paths are project content (never filter) vs workspace noise (candidate for filter-repo). The `## Project Artifacts` section in CLAUDE.md is the single source of truth. If absent, git-squash asks the user and offers to write it. `workspace-init` writes it automatically during workspace creation.

## Two modes

**On-demand (`/git-squash`)**: full workflow — branch isolation, filter-repo, plan generation, review gate, swap. Can touch pushed commits.

**Pre-push hook**: fast path — pattern check on unpushed commits only, in-place squash, no filter-repo, no branch creation. Never touches shared history.

## Reconstruction vs compaction

**Compaction** (ledger, work, qhorus, claudony, parent): all original commits are present. Squash reduces noise within the existing linear history.

**Reconstruction** (engine): PRs were squash-merged — each PR became one commit. The pre-pass recovers original branch commits using PR metadata and groups them under their PR heading for the plan document.

## Plan document format

The plan document is the approval artifact. Execution never happens without it. For ranges >10 commits, the plan is always written to a file on the working branch before asking for YES. The file travels with the branch for external review.

## Spec files

- `squash-policy.md` — classification rules (KEEP / SQUASH / MERGE / DROP)
- `hooks/pre-push` — pre-push hook source
- `~/claude/cc-praxis/docs/superpowers/specs/git-squash-improvements-v2.md` — pending improvements and known limitations
