# git-squash Skill — Remaining Improvements Spec

**Status:** Pending implementation  
**Derived from:** Engine Claude three-way brief + gap analysis session 2026-05-06  
**Context:** After completing the two-phase filter-repo rework, branch isolation, cross-author guard, and intelligence improvements, four gaps remain before the skill is ready for the casehubio ecosystem compaction and engine reconstruction.

---

## Gap 1 — Plan document format

### Reference

The engine reconstruction plan at `https://raw.githubusercontent.com/mdproctor/casehub/main/docs/superpowers/specs/engine-reconstruction-plan.md` is the quality baseline. The compaction-format plan must be at least as good, with the additional improvements listed below.

### Problems identified in v2 ledger report

The v2 report (`/tmp/ledger-squash-plan-v2.md`, 2026-05-06) had six deficiencies:

1. **Blind KEEP title as group heading** — the KEEP commit's message is used as-is, even when it doesn't describe what the group collectively represents after absorption
2. **Proximity grouping creates semantic mismatches** — spec/plan docs are absorbed into the nearest preceding KEEP even when they belong with the implementing feat: commit further ahead in the history
3. **Session handovers survive as KEEP commits** — when a mixed-content commit (session handover + other files) isn't fully stripped by filter-repo, the session handover message becomes a group heading
4. **No curated result column** — absorbed commits don't show their final disposition explicitly; the reader must infer
5. **Already Clean lists every commit** — 186 individual SHAs drown the signal
6. **No offer to write the plan to a file** — lost to context compaction

### Required grouping logic

#### Semantic grouping — spec/plan docs find their implementing commit

Design spec and implementation plan commits must be absorbed into their implementing `feat:/refactor:` commit, not the nearest preceding KEEP. The skill scans **forward** from the spec/plan to find the implementing commit.

**Matching rules (strict — applied in order):**

1. **Target type**: only `feat:` and `refactor:` commits are valid targets. Never match to `adr:`, `docs:`, `chore:`, `test:`, or any other type — even if word overlap is high.

2. **Extract topic words**: strip the prefix (`docs: design spec — `, `docs: implementation plan for `, etc.) and tokenise the remainder into words of 4+ characters.

3. **Word overlap scoring**: for each candidate feat:/refactor: commit in the forward window (up to 80 commits ahead), compute intersection size between topic words and commit subject words. A score of 1 (single word match) is sufficient to register — **threshold is 0, any match wins**. Best score wins; ties go to the earliest (first) matching commit.

4. **Match found**: add the spec/plan to `spec_pending[implementing_commit_sha]` — it will join that commit's group as a `spec_pre` entry when the implementing commit is processed.

5. **No match found**: flag the spec/plan with ⚠️ in the output; do NOT silently absorb it into the nearest preceding KEEP (which is always semantically wrong for planning docs).

**Why threshold = 0, not 1:** with `best_score = 1` as the initial value, a single-word match (score = 1) is not strictly greater than the initial, so it fails to register and the spec falls through to unmatched. Topic words like "forgiveness" or "supplement" uniquely identify the implementing commit — a single-word match is sufficient and correct.

**Tie-breaking — earliest match wins:** when two feat: commits have equal overlap, prefer the earlier one. Specs belong to the first implementation, not a later enhancement.

**Examples of correct semantic grouping:**
- `docs: design spec — LedgerSupplement architecture` → `feat(supplement): add LedgerSupplement base + three concrete supplements` (word: "ledgersupplement")
- `docs: implementation plan — trust score forgiveness mechanism` → `feat(forgiveness): ForgivenessParams record` (word: "forgiveness")
- `docs: design spec — EU AI Act Art.12 compliance surface` → `feat(art12):` commits (word: "art12")
- `docs: design spec — causality query API` → `feat(causality): findCausedBy` (words: "causality", "query")
- `docs: implementation plan for DESIGN.md split` → `docs: split DESIGN.md into core and capabilities` — NOTE: this is a `docs:` target, which is an exception; only flag if no feat:/refactor: match exists and the implementing commit is clearly identifiable

#### Session handover as KEEP — detect and flag

A session handover commit (subject contains "session handover" or "session wrap") should never be used as a group KEEP. When filter-repo leaves one behind (because the commit also touched other files), flag it explicitly:

```markdown
### ⚠️ docs: session handover 2026-04-17
*Group N — absorbs 1 commit*
⚠️ **KEEP commit is a session handover** — filter-repo left this behind because it contains mixed content (other files alongside the handover text). Consider splitting this commit manually before compacting, or accept it as-is knowing the handover message will persist in history.

| Commit | Action | Curated result |
|--------|--------|----------------|
| `40d0d0b` docs: session handover 2026-04-17 | ⚠️ KEEP (handover survived filter) | `docs: session handover 2026-04-17` — *flag for manual review* |
| `bdbc822` chore: add .worktrees/ to .gitignore | 🔽 SQUASH ↑ | *(absorbed — chore cleanup)* |
```

#### Title fitness assessment

After grouping, assess whether the KEEP commit's message adequately represents the group:

- **Fit**: all absorbed commits are in the same scope/feature as the KEEP → use KEEP message as heading unchanged
- **Questionable**: absorbed commits span different concerns, or the KEEP is a minor doc/chore carrying significant absorbed work → flag with ⚠️ and propose a synthesized title
- **Wrong**: the KEEP message describes something completely unrelated to what's being absorbed → ⚠️ required, synthesized title required

Synthesized title generation: summarise what the group collectively represents — not concatenation of messages, but a genuine subject line. Show as a proposed alternative:

```markdown
### feat: examples/order-processing — runnable Quarkus app with 8 integration tests
*Group 1 — absorbs 1 commit*
⚠️ **Proposed title:** `feat: examples/order-processing + LedgerConfig @ConfigRoot fix`
*(absorbed commit registers LedgerConfig — worth reflecting as it fixes a config bug, not just a test)*
```

When the absorbed commits are clearly noise (Javadoc fixes, CI one-liners, style) and don't change the semantic meaning of the KEEP — no flag needed, KEEP title stands.

### Required table format (compaction format)

Use a three-column table per group, matching the engine reconstruction plan style. The heading is the semantic group title (KEEP message or synthesized title), group number is secondary metadata.

```markdown
## feat(supplement): add LedgerSupplement base + three concrete supplements
*Compaction group — 4 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `1f330be` feat(supplement): add LedgerSupplement base + three concrete supplements | ✅ KEEP | `feat(supplement): add LedgerSupplement base + three concrete supplements` |
| `a240831` docs: design spec — LedgerSupplement architecture + ComplianceSupplement | 🔽 SQUASH ↑ | *(absorbed — pre-implementation spec; no standalone value once implemented)* |
| `7d4c5dc` docs: implementation plan — LedgerSupplement architecture | 🔽 SQUASH ↑ | *(absorbed — pre-implementation plan; no standalone value once implemented)* |
| `90c349a` fix(supplement): assert rationale field round-trips in LedgerSupplementIT | 🔽 SQUASH ↑ | *(absorbed — 1L test assertion, same test class)* |

> **Result:** 1 commit.
```

**MERGE groups** — show Final message explicitly:

```markdown
## refactor: rename to casehub-ledger — groupId io.casehub, package io.casehub.ledger
*Compaction group — 11 commits → 1*
**Final message:** `refactor: rename to casehub-ledger — groupId, package, imports, CI updated`

| Commit | Action | Curated result |
|--------|--------|----------------|
| `1e48709` refactor: rename to casehub-ledger ... | ✅ KEEP | *(see Final message above)* |
| `9613135` refactor: move source directories io/quarkiverse → io/casehub | 🔀 MERGE ↑ | *(unified — same rename scope)* |
| `5e1d54e` docs: fix stale repo name references post-rename | 🔽 SQUASH ↑ | *(absorbed — stale ref sweep)* |
...

> **Result:** 1 commit.
```

### Curated result logic for KEEP rows

**The curated result column must be assessed, not copied.** Copying the original message verbatim is wrong — it tells the reader nothing was evaluated.

For every KEEP row, assess the absorbed commits:

| Absorbed content | Curated result |
|-----------------|----------------|
| Pure noise only (Javadoc, style, chore, stale refs, CLAUDE.md, CI no-ops) | `*(message adequate — no change)*` |
| Spec/plan commits on the same topic as the KEEP | `*(message adequate — planning docs absorbed)*` |
| Significant follow-ons that add context (CI behavior change, source move, meaningful docs) | Proposed enhanced message incorporating the context |
| MERGE partner (another feat: at same level) | Always show unified message — never "message adequate" |

For absorbed rows: always show what they contribute (or why they don't), not just "absorbed":
- `*(absorbed — Javadoc follow-on; message adequate)*`
- `*(absorbed — same rename scope; reflected in curated message)*`
- `*(absorbed — pre-implementation planning doc; message adequate)*`

### Already Clean section

```
## Already Clean — 186 commits (no action needed)
*To see all: `git log --oneline <base>..<HEAD>` excluding the action groups below.*

Representative: feat(supplement), feat(merkle), feat(causality), feat(prov),
feat(reactive), feat(trust), feat(privacy), feat(enricher), feat(art12), feat(#62)...
```

### AFTER block — post-squash simulation (not pre-squash)

**Critical:** The AFTER sample must show the simulated post-squash history, not the working branch state before squash is applied. The working branch still has all pre-squash commits — reading from it directly shows noise commits that will be absorbed.

**Correct approach:** collect the KEEP commit from every group (clean and action), sort by original chronological position descending (most recent first — matching git log order), show the top 10:

```python
all_keeps = sorted([g['keep'] for g in groups], key=lambda c: c['idx'], reverse=True)
sample = all_keeps[:10]
```

Display with curated message (not original) where enhanced:

```
## AFTER — what `git log --oneline` will show

  325  commits on main (original)
   -25  pruned by filter-repo
   -72  absorbed by squash
  ──────────────────────────────────
   227  commits — no content lost

Sample (most recent 10 of 227 — post-squash simulation):
  <sha>  <curated message or original if adequate>
  ...
  (run `git log --oneline <work-branch>` after squash executes to verify)
```

### Offer to write markdown file

For any range > 10 commits, offer after the summary:

```
Write this plan to a file for sign-off? (YES / n)
  Default: docs/superpowers/specs/squash-plan-YYYY-MM-DD.md
  (Check ## Artifact Locations in CLAUDE.md for correct specs path)
```

Write to the working branch. File travels with the branch for review.

---

## Gap 2 — PR/branch pre-pass for semantic grouping

### Problem

Classification currently works bottom-up from individual commit messages. For flat-history repos (ledger, work, qhorus, claudony), PR and branch metadata provides a higher-level semantic grouping — "these 12 commits all belong to feat/causality" — which makes reports more readable and groups more meaningful. For squash-merged repos (engine reconstruction), it is essential: without it, you cannot tell which original commits belonged to which PR.

### Two use cases

**Compaction (ledger/work/qhorus/claudony):** All original commits are present. PR/branch metadata provides grouping information. The output is still compaction-format (single KEEP per group), but group headings come from PR titles or branch names rather than the KEEP commit message.

**Reconstruction (engine):** Source branches were squash-merged — each PR became one commit on main. The pre-pass recovers the original branch commits and groups them under their PR heading. Output uses reconstruction-format (three-column table per PR).

### Pre-pass implementation (Step 0b in SKILL.md)

Run before classification, after creating the working branch:

```bash
# 1. Check for merged PRs whose merge commit SHA appears in the range
gh pr list --state merged --json number,title,mergeCommit,headRefName,author,mergedAt \
  --limit 500 2>/dev/null

# 2. Check for surviving remote branch tips that match commits in the range
git branch -r | grep -E "origin/(feat|fix|refactor|docs|chore)/" 2>/dev/null

# 3. Get commit SHAs in range for matching
git log --format="%H" <range>
```

Hard timeout: 10 seconds total. If gh is unavailable or times out, skip the pre-pass silently and proceed with compaction format. Never surface the failure to the user.

### Matching strategies (in priority order)

**Strategy A — Direct SHA match (squash-merge)**  
`gh pr list` returns `mergeCommit.oid`. If that SHA appears in the range, all commits on `headRefName` that were squashed into it are members of that PR group.

**Strategy B — Merge commit in range (merge-commit PR)**  
A `Merge pull request #N` commit in the range is matched to its PR by number. All commits between it and the previous merge commit belong to that PR group.

**Strategy C — Remote branch tip match**  
`git branch -r | grep origin/feat/...` — if the tip SHA of a remote branch appears in the range, all commits on that branch (back to where it diverged from main) belong to that group.

**Strategy D — Conventional commit scope clustering**  
When A/B/C all fail, group contiguous commits sharing the same scope tag (`feat(causality)`, `feat(merkle)`) into a named capability group. Do NOT group non-contiguous same-scope commits — separate instances of the same scope are separate capabilities.

**Strategy E — Flat compaction (no context)**  
No grouping information available. Use KEEP commit message as heading (existing behaviour).

### False grouping guard

Only group commits if they are **contiguous** in the range (no intervening commits from a different scope or branch breaking the cluster). Non-contiguous commits with the same scope stay as separate groups even if they conceptually belong to the same feature — the history tells a different story.

### Output formats

**Compaction format** (all commits present, PR/branch context provides grouping):

```markdown
### PR #47 — feat(causality): findCausedBy — causal chain traversal (2026-04-18) [MDPROCTOR]

- ✅ `3717757` feat(causality): findCausedBy — SPI + JPA + 6 @QuarkusTest IT tests
- 🔽 `26fe313` docs: design spec — causality query API *(methodology — pre-implementation)*
- ✅ `4bc27ae` docs: update causality spec — correlationId + causedByEntryId to core
- 🔽 `a9a5754` docs: revise causality plan — no migration ceremony, 3 tasks *(methodology)*

> Result: 2 commits (2 absorbed)
```

**Reconstruction format** (squash-merged, recovering original branch commits):

```markdown
### PR #38 — refactor(api): rename DispatchRule → Binding (2026-04-14) [MDPROCTOR]

**Branch:** `feat/rename-binding-casedefinition`

| Original commit | Action | Curated result |
|----------------|--------|----------------|
| `2ca7bfb` refactor(api): rename DispatchRule → Binding | ✅ KEEP | `refactor(api): rename DispatchRule → Binding — unified with schema rename` |
| `5ac72ea` refactor(schema): rename CaseHubDefinition.yaml | 🔀 MERGE ↑ | *(unified — same rename scope)* |
| `441213d` chore: remove .claude/ from tracking | 🔽 SQUASH ↑ | *(absorbed — < 5 lines, no issue ref)* |

> **Result:** 1 commit.
```

**Curated result message seeding**  
For reconstruction format, seed the curated message from the PR title (subject to conventional commit enforcement and scope drift check). The user confirms or edits before it is applied.

### Graceful degradation chain

```
Strategy A (SHA match) 
  → Strategy B (merge commit)
    → Strategy C (branch tip)
      → Strategy D (scope clustering)
        → Strategy E (flat — KEEP message as heading)
```

Each level falls through automatically if no match is found. The user sees the best available output; the degradation is invisible.

---

## Gap 3 — Branch-scoped operation as first-class use case

### Problem

The "When to Use" section mentions explicit ranges but does not call out branch-scoped operation as the primary reconstruction workflow. For the engine reconstruction — the most complex planned use — this is the critical path.

### Required changes to SKILL.md "When to Use"

Add an explicit entry:

```
- **Full branch compaction / reconstruction:** compact an entire feature branch before
  merging, or reconstruct a squash-merged branch for review.
  Range syntax: `upstream/main..feat/some-feature` or `origin/main..HEAD`.
  This is the primary use case for reconstruction work — /git-squash handles the
  full range; do not use ad-hoc git commands outside the skill.
```

Also add a note at the end of the section:

```
**git-squash is the single entrypoint for all compaction.** Do not reach for
`git reset --soft HEAD~1 && git commit --amend` or `git rebase -i` directly —
these are internal implementation details. All compaction, from a single-commit
cleanup to a full reconstruction, goes through /git-squash.
```

---

## Gap 4 — workspace-init and init skills do not write Project Artifacts

### Problem

The `## Project Artifacts` section was added to `update-claude-md/starter-templates.md` (done), but `workspace-init` and `init` skills still do not populate it when creating CLAUDE.md. Skills like git-squash read this section at runtime — if it's absent, the git-squash Q&A has to ask the user instead, adding friction on every first run.

### Required changes

**`workspace-init/SKILL.md`**  
During CLAUDE.md generation (the step that writes the project CLAUDE.md), add a question to the Q&A that asks which paths are project artifacts. Use the routing table the skill already builds (what stays in the project repo vs what goes to the workspace) as the source of truth for the answer.

The workspace routing table already knows:
- Blog entries → workspace (or external via blog-routing.yaml)  
- HANDOFF.md → workspace  
- ADRs → workspace or project (user-configured)  
- DESIGN.md / docs/ → project  
- CLAUDE.md → project  

Write the inverse of "goes to workspace" into `## Project Artifacts` in the project CLAUDE.md.

**`init/SKILL.md`** (if it exists and generates CLAUDE.md)  
Same: during CLAUDE.md generation, populate `## Project Artifacts` with sensible defaults (`docs/adr/`, `CLAUDE.md`, any declared design docs). Ask if unsure.

### Priority

Lower than Gaps 1–3. The git-squash Q&A fallback covers the missing-section case adequately for now. Implement after the compaction workflow is proven on the casehubio repos.

---

## Implementation order

1. **Gap 1** (plan format) — implement now; needed for improved ledger report
2. **Gap 3** (When to Use, single entrypoint note) — small; do alongside Gap 1
3. **Gap 2** (PR/branch pre-pass) — implement before engine reconstruction; requires testing against ledger and work first
4. **Gap 4** (workspace-init/init) — separate session; lower urgency

---

## Known limitation — proximity grouping for loose commits

Some commits have no natural semantic home: a build chore (jandex pin, version bump) committed between two unrelated feature commits, or an ADR/config chore that happened to land between a test and a fix. The skill's nearest-preceding-KEEP rule absorbs these into whatever KEEP precedes them, regardless of semantic relationship.

This is an inherent limit of automated grouping. The skill cannot resolve it without human judgment.

**What the skill should do:** distinguish proximity-grouped absorptions from semantically related ones. When a SQUASH commit has **zero word overlap** (4+ character words) with its KEEP commit's subject, label it differently in the Curated result column:

- Semantically related: `*(absorbed — chore cleanup; message adequate)*`
- Proximity grouped: `*(absorbed — proximity grouped; no semantic match to KEEP — relocatable if desired)*`

**Detection:** compute word overlap between absorbed commit subject and KEEP commit subject. Zero overlap → proximity group annotation. Non-zero → normal absorption note.

This makes it easy for reviewers to spot cases that warrant manual relocation without marking them as errors.

**Known examples from ledger:**
- `chore: pin jandex-maven-plugin` in group 44 (`docs: spec for DESIGN.md split`) — zero overlap
- `chore: commit ADR 0002, plan, spec, and session config changes` in group 12 (`fix(merkle): address code review`) — zero overlap

Both are inherent proximity groups with no better automated home.

---

## Open questions

- **Gap 2, reconstruction format:** Should the three-column table include line counts per commit? The brief doesn't mention it but it was useful context in classification. Decision: omit from reconstruction table (too wide); available on request.
- **Gap 1, markdown file path:** `docs/superpowers/specs/` is the default but some repos (engine) may route specs to the workspace. Should the skill check `## Artifact Locations` in CLAUDE.md for the specs path? Likely yes — add this to the Gap 1 implementation.
- **Gap 2, scope clustering threshold:** How many commits in a contiguous same-scope cluster before it becomes a named group? Suggested: 2+ commits. A single isolated `feat(causality)` commit doesn't need a group heading.
