# Commit Squash Policy

**Tie-breaking:** First matching row wins. Squash target = preceding KEEP. No preceding KEEP → squash forward into next KEEP. No KEEP at all → treat most substantive commit as KEEP, squash rest into it.

---

## Phase 0 — Filter-repo (on-demand only)

**Never run automatically. Never run from the pre-push hook.**

Filter-repo strips workspace artifact files from history before any compaction
runs. `--prune-empty` then removes commits that become empty. The KEEP/SQUASH/MERGE
pass runs only on commits with remaining project file changes.

**When to run:** On-demand `/git-squash` only, when workspace artifact commits are found in the range. Present Q&A (see SKILL.md Step 1) before running.

**What counts as a workspace artifact path** (default candidates for filtering):
- `HANDOFF.md` — session handover files
- `docs/_posts/*.md` in non-blog repos — personal diary entries

**Important:** filter-repo operates on whole file paths only — it cannot strip
sections within a file. Never offer to filter "personal methodology sections of
CLAUDE.md". Instead, `docs(claude):` commits with personal methodology content
are handled by the squash pass (row 11) or flagged as candidates there.

**What is NOT a workspace artifact** (never filter by default):
- Any path declared in `## Project Artifacts` in CLAUDE.md
- `docs/_posts/` in a `type: blog` project — the blog IS the project
- `docs/adr/` — architecture decisions are project history
- `CLAUDE.md` project-useful content (build commands, naming conventions, test patterns)

**Exception — truly empty commits:** A commit with zero file changes
(e.g. a bare `ci: retrigger` that touched nothing) can be dropped directly
in the squash pass. No filter step needed — there are no files to strip.

---

## Keep as standalone commits

| Pattern | Reason to keep |
|---------|---------------|
| `feat(scope): ...` | Introduces a new capability — the what and why matter |
| `fix(scope): ...` with ≥ 10 lines changed | Real bug fix with context |
| `fix(scope): ...` correcting user-visible output | Error messages, labels, UI strings — standalone regardless of size |
| `test(scope): <scenario name> ...` describing a specific scenario | Documents intended behaviour |
| `refactor(scope): ...` with ≥ 20 lines changed | Structural change worth understanding |
| `perf(scope): ...` with ≥ 10 lines changed | Performance change — the tradeoff matters |
| `adr: ...` | Architecture decision record — always standalone |
| `docs: <filename>.md` introducing a new document | New reference material — standalone if substantive |
| Any commit with code changes referencing an issue number (`Closes #N`, `Refs #N`) | Traceability — standalone regardless of size. **Exception:** a pure docs commit sharing the same issue ref as the immediately preceding feat commit is a MERGE candidate (row 10 below) — that case is a documentation follow-on, not a standalone contribution. |

---

## Squash into the preceding meaningful commit

Process rows in order — first match wins.

| Priority | Pattern | Action |
|----------|---------|--------|
| 1 | `wip:` / `WIP` / `checkpoint:` / `savepoint:` / `temp:` | Always squash — save-state artifacts |
| 2a | `Merge pull request #N from ...` merging into a protected branch (`main`, `master`, `release/*`) | KEEP — records when a capability landed; PR number is traceability |
| 2b | `Merge pull request #N from ...` merging into a feature branch | SQUASH — intermediate integration, not a landing event |
| 2c | `Merge branch 'main' into feature/...` / `Merge branch 'origin/main' into ...` | SQUASH — trivial upstream sync, no information value |
| 2d | `Merge branch '...' of https://github.com/...` | SQUASH — remote tracking sync noise |
| 2e | Any other `Merge branch '...'` — if merging a named feature/fix branch → KEEP; if merging main/master/develop into current branch → SQUASH | Inspect branch names before classifying |
| 3 | `Revert "..."` followed within 3 commits by a replacement | Squash all three into the final working commit |
| 4 | `build: wire ...` with a `Revert "build: wire ..."` following it | Both noise — squash into the eventual working state |
| 5 | `style: ...` / `style(<scope>): ...` / `chore: apply spotless` / `chore: fix formatting` | Always squash — cosmetic only. **Scoped variants (`style(enricher):`, etc.) match the same rule.** |
| 6 | `chore: ...` / `chore(<scope>): ...` — any chore regardless of scope | Squash into preceding commit. **Scope does not change the classification: `chore(docs):`, `chore(build):`, `chore(examples):` are all SQUASH.** |
| 8 | `docs(scope): align Javadoc ...` / `docs(scope): fix wording` / `docs(scope): add missing ...` | Squash into the feature commit it follows |
| 9 | `docs: fix stale ...` / `docs: replace stale ...` / `docs: update stale ...` / `chore(docs): replace stale ...` — stale reference fixups after a rename | MERGE all into the rename commit — they are part of the same sweep. Match any variant: `fix stale`, `replace stale`, `update stale`, `replace stale artifact names`, `fix stale repo name references post-rename`. **The anchor must be the rename commit itself, not whatever KEEP happens to be nearest.** |
| 10 | `docs: ...` with issue reference immediately following `feat: ...` with the same issue reference | MERGE into the feat — same issue, same sitting |
| 11 | `docs(claude): ...` updating project-useful content (build commands, test patterns, naming conventions, architecture) | SQUASH into the related feature or chore commit it follows |
| 12 | `fix(test): ...` where the same test class was fixed in the previous commit | Squash — same test being hardened |
| 13 | `fix(test): ...` adjusting timing, bounds, or parameters with no scenario change | Squash — test mechanical adjustment, not new scenario |
| 14 | `ci: use GH_PAT for ...` / `ci: standardise publish workflow` / `ci: add workflow_dispatch` / `ci: fix ...` | Squash into preceding commit, or DROP if truly empty (zero file changes) |
| 15 | `fix(ci): ...` / `build: bump` when a feature commit follows | Squash into the feature it unblocked |
| 16 | `fix(ci): ...` / `ci: retrigger` / `build: bump` when no feature follows, **and zero file changes** | ❌ DROP — truly empty, no files to preserve |
| 17 | Any commit with `< 5 lines changed` (excluding blank lines and imports) and no issue reference — **with exceptions below** | Squash into preceding commit |

**Row 17 guard — file overlap prerequisite before size-based auto-squash:**
Before applying the size heuristic, check whether the small commit shares at least one file with the preceding KEEP commit. Zero file overlap = no semantic relationship = do not auto-squash by size. Prefer standalone KEEP micro-commit over proximity-forced wrong attachment.

The specific path exemptions (security, config) are project-specific and cannot be applied generically. The file overlap requirement catches most false positives without requiring per-project configuration. |
| 18 | Multiple commits with near-identical messages on the same class/file | Identify the most complete, integrate unique content, squash the rest |

---

## Merge similar commits into a unified message

When two or more commits address the same concern, merge into one if a single
message tells the story more cleanly.

**Signals that two commits should merge:**
- Same scope and file set (both touching the same class/module)
- Sequential commits forming one logical change ("add field" + "wire field into handler")
- Two `test:` commits for the same scenario (setup + assertion split across commits)
- Two `feat:` commits that are clearly part one and part two of the same capability
- A rename commit followed immediately by import/reference fixup commits
- **File-overlap:** Jaccard similarity ≥ 0.7 between file sets (`|A∩B| / |A∪B|`) — both commits touching the same files are likely the same capability regardless of message wording
- **Temporal proximity:** commits within 30 minutes of each other from the same author warrant closer scrutiny — surface them together in the plan and ask whether they are genuinely distinct. Do not assume they should merge; require the author to confirm the distinction is intentional

**How to write the unified message:**
- Use the broader of the two scopes
- Combine key points from both messages into one description — richer than either alone, no longer than necessary
- Keep all issue references from both commits

**Do not merge** commits from different features or scopes just because they are small. Merge only when the result is richer than either message alone.

**Good — rename sweep merged into one:**
```
MERGE ← refactor: rename to casehub-work — groupId io.casehub, package io.casehub.work
MERGE ← docs: fix stale repo name references post-rename
MERGE ← docs: fix stale repo name references post-rename
MERGE ← fix: update imports in quarkus-work-notifications to io.casehub.connectors
INTO  → refactor: rename to casehub-work — groupId, package, import references updated
```

**Good — two halves of one capability:**
```
MERGE ← feat(blackboard): add PlanItem strict lifecycle — markRunning/markCompleted
MERGE ← feat(blackboard): PlanItem lifecycle validation — IllegalStateTransition guard
INTO  → feat(blackboard): PlanItem strict lifecycle with IllegalStateTransition guard —
        markRunning/markCompleted enforce valid transitions; concurrent CAS prevents races
```

**Bad — different modules, different concerns:**
```
DO NOT MERGE:
  feat(api): add UserRepository SPI
  feat(engine): wire WorkerStatusListener
```

---

## Special cases

**Revert chains:** `Revert X` + `X (attempt 2)` + eventual fix → collapse to one commit
with the final message. Never preserve failed attempts.

**Test hardening runs:** When 3+ commits repeatedly touch the same test class,
identify the one with the most complete message, integrate unique context, squash the rest.

**Long squash chains:** When squashing 4+ commits into one, summarise rather than
concatenate — one tight message beats four messages stapled together.

**Rename sweeps:** A major rename (groupId, package, artifact names) is always followed
by trailing fixup commits. MERGE all trailing fixups into the rename commit — they are
inseparable parts of the same change.

**Stale-ref classification takes priority over broad type patterns:** A commit matching
the stale-ref pattern (`docs: fix stale ...`, `fix: update all stale repo name references`,
`docs: replace stale artifact names`, etc.) is always SQUASH regardless of type prefix.
The `is_stale_ref` check must run before the broad `docs:` KEEP and `fix:` KEEP patterns.
`docs: fix stale repo name references post-rename` is SQUASH. `fix: update all stale repo
name references` is SQUASH. The rename sweep should pick them all up.

**CI development arc — final commit is KEEP, intermediates SQUASH:** When 3 or more
consecutive `ci:` / `fix(ci):` commits appear in the range, they represent a development
arc (scratch → working state). Classify the **last** commit in the arc as KEEP; all
preceding CI commits in the arc are SQUASH absorbed into it. Never absorb a CI arc into
an unrelated preceding KEEP — the arc is a self-contained unit.

**No preceding KEEP target:** Squash forward into the next KEEP commit instead.

**Temporal scrutiny:** When two or more commits from the same author fall within a
30-minute window, surface them together in the plan and ask whether they are
genuinely distinct. Do not classify them as MERGE automatically — proximity is a
signal to look harder, not a merge recommendation. The author must confirm the
distinction is intentional before they remain as separate KEEP commits.

**docs(claude): personal methodology:** If a `docs(claude):` commit updates personal
working-style content (collaboration preferences, session methodology) rather than
project conventions, it is a Phase 0 filter-repo candidate — not a squash target.
The skill's Q&A UI will surface it.

**Double issue-close detection:** After grouping, scan all surviving KEEP commits
for duplicate `Closes #N` references. If two KEEPs both claim `Closes #N` for the
same issue, flag it — only one should be authoritative. Convention: the PR merge
commit closes the issue; the individual branch commit that preceded it should use
`Refs #N` instead.

**Consistent proximity-grouped flagging:** Apply ⚠️ proximity-grouped to ANY commit absorbed into a semantically unrelated KEEP — CI commits (`ci:`, `fix(ci):`), formatting commits (`style:`), and any commit with zero meaningful word overlap with its KEEP target. Flag all cases consistently, not selectively.

**Multi-issue reference preservation:** When a group absorbs commits that carry
issue references different from the KEEP commit's references, all unique refs must
survive into the curated message. Collect every `Closes #N`, `Refs #N` from every
commit in the group (KEEP + absorbed). Deduplicate: `Closes` takes precedence over
`Refs` for the same issue number. Append any refs not already in the KEEP message.

Example: `feat: add TrustGateService (Closes #33)` absorbs `docs(trust): note capabilityTag (Refs #34)` →
curated message: `feat: add TrustGateService — Closes #33, Refs #34`

**Cross-author squash:** Only squash a commit from a different author when it is
already classified SQUASH — formatting, CI, spelling, mechanical noise with no design
insight. Noise has no meaningful attribution regardless of whose name is on it.

If a commit would otherwise be KEEP or MERGE, never squash it across an author
boundary. Flag it in the plan and leave it standalone. The other author made a real
contribution; it stays attributed to them.

---

## Examples

### Keep all — each commit tells a distinct story
```
feat(engine): wire WorkerStatusListener and CaseChannelProvider — Closes #152
test(blackboard): R1 — two sequential stages activate in order
fix(blackboard): nested stage activation gated on parent ACTIVE state
feat(blackboard): CaseEvictionHandler — evict plan models on terminal case state
```

### Merge — rename sweep (trailing fixups absorbed into rename)
```
MERGE ← refactor: rename to casehub-work — groupId io.casehub, package io.casehub.work
MERGE ← docs: fix stale repo name references post-rename
MERGE ← docs: fix stale repo name references post-rename
MERGE ← fix: update imports in quarkus-work-notifications to io.casehub.connectors
INTO  → refactor: rename to casehub-work — groupId, package, import references updated
```

### Squash — WIP and checkpoint artifacts
```
SQUASH ← wip: halfway through blackboard refactor
SQUASH ← checkpoint: tests passing locally
KEEP   → refactor(blackboard): extract PlanItemFactory — simplifies activation flow
```

### Squash — revert chain collapses to one
```
SQUASH ← build: wire casehub-parent BOM for quarkus-ledger
SQUASH ← Revert "build: wire casehub-parent BOM for quarkus-ledger"
KEEP   → build: remove embedded builds; use GitHub Packages; add distributionManagement
```

### Squash — small docs follow-on
```
KEEP   → feat(engine): add CaseMetaModelRepository and EventLogRepository SPI interfaces
SQUASH ← docs(engine): align findByKey Javadoc null-return wording
```

### Squash — cross-repo infrastructure chore
```
KEEP   → feat: add PostgreSQL LISTEN/NOTIFY broadcaster for distributed SSE (#93)
SQUASH ← chore: pin jandex-maven-plugin 3.1.2 in root pluginManagement
SQUASH ← chore: add jandex-maven-plugin for CDI bean discovery
```

### Squash — docs(claude) project-useful content
```
KEEP   → feat(engine): add CaseMetaModelRepository
SQUASH ← docs(claude): update testing patterns — add @QuarkusIntegrationTest convention
```

### Merge — feat and its docs commit share same issue
```
MERGE ← feat: add PostgreSQL LISTEN/NOTIFY broadcaster for distributed SSE (#93)
MERGE ← docs: systematic documentation update for PostgreSQL broadcaster (#93)
INTO  → feat: add PostgreSQL LISTEN/NOTIFY broadcaster for distributed SSE —
        with documented configuration and usage (#93)
```

### Drop — truly empty commit (zero file changes)
```
❌ DROP  ci: retrigger  ← git show confirms zero files changed
```

### Filter-repo (Phase 0, on-demand only) — workspace artifact files stripped from history
```
FILTER → HANDOFF.md removed from 3 commits (session handovers — no project content)
         3 commits became empty after strip → pruned automatically by --prune-empty
```
