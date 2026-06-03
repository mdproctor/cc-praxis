---
name: git-squash
description: >
  Use when the commit history contains noise — fixup commits, revert
  chains, docs wording chores, tiny cleanups — that obscures meaningful
  history. Also triggered when the pre-push hook flags squash candidates,
  or invoked on demand via /git-squash on any commit range.
---

# Git Squash

Applies the commit squash policy to a range of commits. Eliminates noise
(tiny fixups, revert chains, formatting commits) while preserving meaningful
history. Author approves every change — nothing is applied automatically.

The full policy is in `squash-policy.md` alongside this skill.

**Two modes:**
- **On-demand** (`/git-squash`): full workflow with branch isolation, filter-repo,
  intelligent classification, review gate, and branch swap. Can handle pushed commits safely.
- **Pre-push hook**: in-place squash on unpushed commits only. Fast, no branch
  creation, no force-push. Never runs filter-repo.

---

## When to Use

- **Before pushing:** run on unpushed commits to clean history before it's shared.
  The pre-push hook operates on unpushed commits only — in-place, no force-push needed.
- **On demand:** clean up any commit range at any point (`/git-squash`).
  All work happens on an isolated working branch — pushed commits can be included safely.
- **After the hook fires:** the pre-push hook detected squash candidates; run this to resolve them.
- **Pre-PR review:** branch is pushed but no PR exists yet. On-demand mode handles
  this with branch isolation and a review gate before the swap.
- **Full branch compaction / reconstruction:** compact an entire feature branch before
  merging, or reconstruct a squash-merged branch for review.
  Range syntax: `upstream/main..feat/some-feature` or `origin/main..HEAD`.
  This is the primary use case for reconstruction work — `/git-squash` handles the
  full range; do not use ad-hoc git commands outside the skill.

**git-squash is the single entrypoint for all compaction.** Do not reach for
`git reset --soft HEAD~1 && git commit --amend` or `git rebase -i` directly —
these are internal implementation details of the skill. All compaction, from a
single-commit cleanup to a full reconstruction, goes through `/git-squash`.

---

## On-Demand Workflow

### Step 0 — Create working branch

Before any destructive operation, create an isolated working branch:

```bash
ORIG_BRANCH=$(git branch --show-current)
WORK_BRANCH="squash/wip-${ORIG_BRANCH}-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$WORK_BRANCH"
```

Record both names — needed for the swap in Step 8. All filter-repo and rebase
operations run on `$WORK_BRANCH`. The original branch is untouched until the
author explicitly approves the swap.

---

### Step 0b — PR/branch pre-pass (optional enrichment)

Runs after Step 0 (working branch created), before Step 1 (filter-repo). Results
enrich grouping and headings in the plan. **Fail silently** — if `gh` is unavailable
or the pre-pass times out, skip it entirely and proceed to Strategy E (flat compaction).
Never surface the failure to the user.

```bash
# Hard timeout: 10 seconds total across all commands
PR_DATA=$(timeout 8 gh pr list --state merged --json number,title,mergeCommit,headRefName,author,mergedAt \
  --limit 500 2>/dev/null)

REMOTE_BRANCHES=$(git branch -r 2>/dev/null | grep -E "origin/(feat|fix|refactor|docs|chore)/")

RANGE_SHAS=$(git log --format="%H" <range>)
```

Apply strategies in order — stop at the first one that produces groups:

**Strategy B — Merge commit in range (PRIMARY — implement this):**  
Scan commits whose subject matches `Merge pull request #N from ...` targeting a
protected branch (row 2a: KEEP). These are natural group boundaries:
- All commits between two consecutive PR merge commits belong to the earlier PR's group (pre-merge work)
- Group heading: `### PR #N — <merge commit message truncated> (date) [AUTHOR]`
- Use **compaction format**

```bash
git log --format="%H %s" <range> | grep "Merge pull request #"
```

**Strategy D — Scope clustering (fallback when no merge commits found):**  
Group contiguous commits sharing the same conventional commit scope tag
(`feat(causality)`, `feat(merkle)`). Do NOT group non-contiguous same-scope
commits — separate clusters of the same scope are separate capabilities.
Use **compaction format** with scope as the heading.

**Strategy E — Flat (no context):**  
No merge commits, no scope clusters. Use KEEP commit message as heading (existing behaviour).

**Mode detection — reconstruction vs flat compaction:**

Before attempting any strategy, detect which mode applies:

```bash
# Count merge-commit PRs in the range (row 2a: KEEP)
git log --oneline <range> | grep -c "^[a-f0-9]* Merge pull request #"
```

- **≥ 1 PR merge commit found → Reconstruction mode**: run Strategy B. These boundaries are the primary signal; they override commit-message-based grouping.
- **0 PR merge commits → Flat compaction mode**: skip Strategies A, B, C entirely. Go directly to Strategy D (scope clustering) or E (flat). The `gh pr list` call is skipped — it adds latency and the context it returns doesn't improve grouping for flat histories.

**Strategy A — Squash-merge SHA match (reconstruction):**

When `PR_DATA` is available and reconstruction mode is confirmed, match each PR's
`mergeCommit.oid` against `RANGE_SHAS`. A match means that single commit on the
current branch represents the entire squash-merged PR. Recover the original branch
commits for grouping:

```bash
# For each PR where mergeCommit.oid is in RANGE_SHAS:
BRANCH_COMMITS=$(git log --format="%H %s" origin/<headRefName> ^<merge-base-with-main> 2>/dev/null)
```

If the source branch is still available remotely, use its commits as the group
members. If unavailable, the squash commit stands alone as its own group.
Use **reconstruction format** — the squash already happened; we are recovering
the original commits to classify them. Seed the curated message from the PR title.

*Strategy C (branch tip) is not implemented — lower priority than A and B.*

**False grouping guard:** Only form a group if the commits are **contiguous**
in the range. An intervening commit from a different scope or branch breaks
the cluster — the commits before and after the break stay in separate groups.

**Store the result** for use in Steps 3 and 5a:
```
PR_GROUPS = [
  { number: 47, title: "feat(causality): findCausedBy", author: "MDPROCTOR",
    date: "2026-04-18", branch: "feat/causality", commits: [sha1, sha2, sha3],
    strategy: "A" | "B" | "C" | "D" },
  ...
]
GROUPING_STRATEGY = "A" | "B" | "C" | "D" | "E"
```

---

### Step 1 — Filter-repo Q&A (on-demand only)

**Never run filter-repo from the pre-push hook or any automatic trigger.**
**Always runs on the working branch, never on the original.**

#### 1a — Resolve project artifacts

Check CLAUDE.md for a `## Project Artifacts` section:
```bash
grep -A 50 "^## Project Artifacts" CLAUDE.md 2>/dev/null
```

**If `## Project Artifacts` exists:** paths listed there are project content — never
filter them by default.

**Blog routing detection:** Before presenting any Q&A, check for `blog-routing.yaml`
in all three locations (most-specific wins):
```bash
# 1. Project-level override
cat blog-routing.yaml 2>/dev/null
# 2. Workspace-level override (if workspace path is known)
cat <workspace>/blog-routing.yaml 2>/dev/null
# 3. Global default
cat ~/.claude/blog-routing.yaml 2>/dev/null
```

Also detect blog-style paths actually present in the commit range:
```bash
git log --name-only --format="" <range> | grep -E "(^blog/|^docs/_posts/|^diary/)" | sort -u
```

If any routing config has external `destinations` (type: git or type: github pointing
outside this repo), blog paths are external for this project.

Cross-reference routing config, Project Artifacts, and detected paths:

| Routing found | Project Artifacts | Action |
|--------------|-------------------|--------|
| External routing (any level) | Path listed as artifact | **Contradiction** — ask user to reconcile |
| External routing (any level) | Path absent | Consistent — blog path is a filter-repo candidate |
| No routing found | Path listed as artifact | Consistent — blogs are project content, skip filtering |
| No routing found | Path absent | **Ask user**: external or project content? |

If the user says **external** but no routing exists at any level, offer to create one:
```
Blog entries detected in blog/ but no blog-routing.yaml found (checked project,
workspace, and ~/.claude/blog-routing.yaml).
Without routing config, blog entries may keep accumulating in this repo.

Set up blog routing now? (YES / n)
  Add to global ~/.claude/blog-routing.yaml, or create a project-level override? (global / project)
  Destination path/repo:
```

If YES, write the routing config and note it for committing separately after the
squash is complete.

**If `## Project Artifacts` is absent:** ask the user about common workspace artifact
paths found in the commit range, then offer to write the section:

```
CLAUDE.md has no ## Project Artifacts section.

Which of these paths in the commit range are project content (not workspace noise)?

  [x] docs/adr/       — architecture decision records
  [x] CLAUDE.md       — project conventions (build, test, naming)
  [ ] HANDOFF.md      — session handovers (workspace noise by default)
  [ ] blog/           — blog entries (detected as external per blog-routing.yaml)

Type numbers to toggle, "go" to proceed:
```

After the user responds, offer:
```
Add a ## Project Artifacts section to CLAUDE.md with these selections? (YES / n)
```

If YES, write the section to the original branch's CLAUDE.md (not the working branch).

#### 1b — Scan and filter

Scan the commit range for files that could be filtered:
```bash
git log --name-only --format="" <range> | sort -u
```

**Important limitation:** `git filter-repo` operates on whole file paths only — it
cannot strip sections within a file. Only offer filtering for whole files. For
CLAUDE.md commits, the squash pass (Step 3) handles them as SQUASH candidates instead.

Filter only paths that are NOT in Project Artifacts and match known whole-file
workspace patterns (HANDOFF.md, docs/_posts/ entries in non-blog repos, etc.).

If filterable paths are found, present a checkbox Q&A:

```
Filter workspace artifact files from history before compacting?

Detected in commit range:
[x] HANDOFF.md (session handovers — 3 commits)
[ ] docs/_posts/*.md — deselected: declared as Project Artifact in CLAUDE.md

Type numbers to toggle, "go" to proceed, or "skip" to skip filtering:
```

On **"go":** run filter-repo on the working branch only:
```bash
git filter-repo --path <path> --invert-paths --prune-empty always --refs "refs/heads/$WORK_BRANCH"
```

Show the Phase 0 report:
```
Phase 0 — filter-repo
  Stripped paths: HANDOFF.md (3 commits)
  Commits pruned after strip (became empty): 3
  Commits remaining for compaction: 11
```

On **"skip":** proceed directly to Step 2.

---

### Step 2 — Resolve commit range

**Resolve AFTER filter-repo completes** — filter-repo rewrites all SHAs.

```bash
git log --oneline @{u}..HEAD 2>/dev/null || git log --oneline origin/HEAD..HEAD 2>/dev/null
```

If no upstream is configured, ask for the base point. Record the resolved range.

**Check for pushed commits in range:**
```bash
git log --oneline <range> | while read sha rest; do
  git branch -r --contains "$sha" 2>/dev/null | grep -v HEAD | head -1
done
```

If pushed commits are in range, warn and require YES before continuing.

---

### Step 3 — Classify commits

Read `squash-policy.md`. Run all analysis passes in order, then synthesise into a
final classification for each commit.

#### 3a — Gather raw data

For every commit in the range, collect subject **and body**:
```bash
# Subject + body — %b captures the full commit body after the subject line
git log --format="%H%n%ae%n%ai%n%s%n%b%n---END---" <range>
git show --name-only --format="" <sha>   # file set per commit
git show --stat <sha>                    # line counts for small-commit detection
```

Parse each commit's body separately from its subject. The body often contains
the rationale, the constraint, the approach tried first — information that must
survive into the curated message if not already captured in the subject.

**Non-trivial body content:** a body is non-trivial if it contains more than
`Co-authored-by:`, `Signed-off-by:`, or blank lines.

**Body synthesis for groups (Step 3a-ii):** After gathering all commit bodies in a group,
extract and synthesise substantive content for the curated final commit body:

1. **ADR references:** any mention of "ADR", "ADR-NNN", "Architecture Decision" → always preserve
2. **Rationale phrases:** sentences containing "because", "to avoid", "so that", "decided to", "per decision", "constraint" → preserve the sentence
3. **Rejected alternatives:** "instead of", "not X because", "considered X but" → preserve
4. **Planning doc subjects:** when absorbing a design spec or implementation plan commit, prepend `[Plan: <planning commit subject>]` to the synthesised body
5. **Deduplication:** remove repeated content across multiple commit bodies

The synthesised body appears in the plan's curated result column alongside the subject.
If no substantive body content is found, the curated body is empty (no "message adequate" noise).

This preserves architectural rationale through the squash — the *why* survives, not just the *what*.

#### 3b — Detect conventional commits

Scan recent history (last 20 commits outside the range) to determine if the repo
uses conventional commits:
```bash
git log --oneline -20 @{u} | grep -cE "^[a-f0-9]+ (feat|fix|chore|docs|test|refactor|perf|style)[:(]"
```
If ≥ 80% match, record `CONVENTIONAL=true` — used in Step 6 to enforce format
on MERGE messages.

#### 3c — PR/issue body integration

If `gh` is available, fetch the PR for the current branch:
```bash
gh pr view --json body,title,number,baseRefName 2>/dev/null
```

If a PR exists:
- **Protected-branch merge target** (`main`, `master`, `release/*`): note this for
  merge commit classification (Step 3d)
- **Commits mentioned by SHA** in the PR description → KEEP regardless of size
- **PR task list** where each task maps 1:1 to a commit → treat all as KEEP
  (they document the work breakdown; squashing loses the traceability)
- **PR description says "fix typo in X"** → corresponding commit is SQUASH regardless
  of message pattern

#### 3d-pre — Same-issue clustering (runs before pattern classification)

Before pattern classification, group commits by shared issue reference. Extract
issue refs from both subject and body (`#N`, `Closes #N`, `Refs #N`).

For each issue number that appears in 2+ commits in the range:

```bash
git log --format="%H %s%n%b" <range> | grep -oE '(Closes|Refs|Fixes)?\s*#[0-9]+' 
```

**Clustering rules:**
- **One feat + one or more fix/test/docs sharing the same #N**: MERGE all into the feat. The combined work for that issue belongs together.
- **Multiple feat commits sharing the same #N**: KEEP each but annotate as parts of the same issue — they document distinct steps of a larger capability.
- **Only fix/test/docs for #N, no feat**: MERGE into the most substantive (largest diff), flag "no primary feat identified for #N"
- **Contiguity not required**: commits for the same issue may be scattered across the range — same-issue clustering reaches across non-adjacent commits.

Store the resulting issue-based groups as `ISSUE_GROUPS` for use in Step 3d (PR context).

#### 3d — Apply PR grouping context (if Step 0b produced groups)

If `PR_GROUPS` is populated from Step 0b, use it to pre-organise commits before
pattern classification:

- Commits within a PR group are classified together. The group's PR title (or scope
  label for Strategy D) becomes the heading for that section of the plan.
- Pattern classification (KEEP / SQUASH / MERGE / DROP) still applies within each
  group — the pre-pass determines *which* commits belong together, not how to handle
  individual commits.
- Commits not covered by any PR group fall back to the nearest-KEEP grouping (Strategy E).
- For **Strategy A (reconstruction)**: the single squash commit on main is the KEEP;
  the recovered original branch commits are classified against it. Seed the curated
  message from the PR title (subject to conventional commit enforcement).

#### 3e — Pattern classification

For each commit, apply the KEEP / SQUASH / MERGE / DROP rules from `squash-policy.md`
in priority order. Pay particular attention to the refined merge commit rules (rows
2a–2e): inspect branch names in the merge message before classifying.

Only classify a commit as DROP if `git show --stat` confirms **zero files changed**.

**Scoped patterns — scope does not exempt from SQUASH:**
`chore(docs):`, `chore(build):`, `chore(examples):`, `style(enricher):`, `style(trust):`
etc. all match their base type (`chore:`, `style:`) for classification purposes.
A scope in parentheses does not make a chore or style commit a KEEP.

**Stale-ref classification takes priority over broad type patterns:**
Check `is_stale_ref` BEFORE the broad `docs:` KEEP and `fix:` KEEP patterns.
`docs: fix stale repo name references post-rename` is SQUASH, not KEEP.
`fix: update all stale repo name references` is SQUASH, not KEEP.
The stale-ref pattern overrides the type prefix.

**CI development arc detection:**
When 3 or more consecutive `ci:` / `fix(ci):` commits appear in the range, they
represent a development arc (scratch → working state). Do not absorb them all into
whatever KEEP precedes them. Instead:
1. Identify the arc: all contiguous `ci:` / `fix(ci):` commits (none of which has
   a non-CI commit between them)
2. Promote the **last** commit in the arc to KEEP — it represents the working outcome
3. Classify all preceding commits in the arc as SQUASH, absorbed into that final KEEP
4. The arc is self-contained — it does not absorb unrelated preceding commits

**Double issue-close detection (run after grouping, before showing plan):**

After all groups are formed, scan all surviving KEEP commits for duplicate `Closes #N`
references. If two or more KEEPs both claim `Closes #N` for the same issue number,
flag it in the plan:

```bash
# Extract all Closes refs from surviving KEEP commit subjects + bodies
git log --format="%H %s%n%b" <work-branch> | grep -oE 'Closes\s+#[0-9]+'
```

For each issue number that appears more than once with `Closes`:
```
⚠️  Duplicate Closes #N: both <sha1> and <sha2> claim to close this issue.
    Only one should be authoritative. Suggest changing one to `Refs #N`.
    Typically: the PR merge commit closes; the individual branch commit refs.
```

Surface this flag in the plan before the approval prompt. Present both options:
amend one to `Refs #N`, or accept both as-is. Wait for the user's decision before
building the rebase todo.

**Consistent proximity-grouped flagging:**

The ⚠️ proximity-grouped annotation must apply to ALL cases where a commit is
absorbed into a semantically unrelated KEEP — not only chore commits. Apply it when:
- A `ci:` or `fix(ci):` commit is absorbed into a non-CI KEEP
- A `style:` or formatting commit is absorbed into an unrelated KEEP
- Any commit with zero meaningful word overlap (after PROXIMITY_STOP filter) with its KEEP

CI commits absorbed into blackboard feats, test commits, or unrelated fixes are
proximity-grouped by the same definition as chore commits near unrelated feats. Flag
them identically.

**Absorption target SHA verification (pre-execution, before building rebase todo):**

Before building the rebase todo, verify every non-group KEEP target SHA exists on
the working branch:

```bash
# Verify each referenced SHA exists — one command per SHA, no loop
git cat-file -e <sha1> 2>/dev/null || echo "MISSING: <sha1>"
git cat-file -e <sha2> 2>/dev/null || echo "MISSING: <sha2>"
# substitute actual SHA values
```

If any SHA is missing: halt and report. A missing SHA means the plan was generated
against a different branch state than the current working branch (the branch was
amended, rebased, or additional commits were added since plan generation). Do not
proceed until the plan is regenerated.

**Chronological ordering check for cross-group absorptions:**

When a SQUASH commit targets a KEEP from a *different* group (i.e., the target is
not the immediately preceding KEEP), verify the chronological relationship:

```bash
# Does SQUASH commit appear before or after its target in the range?
git log --format="%H" <range> | grep -n "<squash_sha>\|<target_sha>"
```

If the SQUASH commit appears *before* its target in the range (i.e., older), the
standard rebase todo cannot use a simple `squash` line — it would need to be listed
after the target's `pick` line, which requires manual reordering of the todo. Flag
this explicitly in the plan:

```
⚠️  Ordering: <squash_sha> is chronologically before <target_sha>.
    The rebase todo must list this commit as `squash` after the target's `pick` line.
    Verify the todo ordering before executing.
```

**Proximity-grouped resolution — scan forward before accepting a wrong attachment:**
When a SQUASH commit has zero meaningful word overlap with its nearest preceding KEEP
(PROXIMITY_STOP-filtered), do not immediately absorb it there. Instead:
1. Scan forward up to 5 commits for a KEEP with overlap > 0 (bounded to prevent spurious distant matches)
2. If a better semantic home is found: re-group there; note in plan "relocated to semantic home"
3. If no better home exists: promote the commit to KEEP micro-commit — a small standalone
   chore is better history than a wrong attachment

Only fall back to proximity grouping (with annotation) when no semantic home can be found.

**Rename sweep grouping — stale-ref fixups anchor to the rename, not nearest KEEP:**
When the range contains a rename commit (`refactor: rename to X — groupId, package...`),
scan forward from it for all stale-reference fixup commits:
- `docs: fix stale ... references`
- `docs: replace stale ... artifact names`
- `docs: update stale ...`
- `chore(docs): replace stale ...`
- `chore: update repo references to ...`

These all belong grouped under the rename commit regardless of what other KEEPs
appear between the rename and the fixups. A stale-ref fixup that is "already clean"
in isolation is wrong if a rename commit exists in the range — it is part of that
rename sweep.

#### 3f — Temporal scrutiny

Extract timestamps and identify commits from the same author within 30-minute windows:
```bash
git log --format="%H %ae %ai" <range>
```

Temporal proximity is not a merge signal — two commits 10 minutes apart may address
completely different concerns. It is a scrutiny signal: surface them together in the
plan and ask the author to confirm they are genuinely distinct before leaving them as
separate KEEP commits.

Do not reclassify or merge automatically. Show the cluster as a question:
```
⏱ Close together — 3 commits from alice@example.com within 18 minutes:
   abc1234  feat(api): add UserRepository SPI
   def5678  docs: update CLAUDE.md for new conventions
   ghi9012  fix(test): correct assertion timing
   Are these genuinely distinct? (YES to keep separate / n to review for merge)
```

#### 3g — File-overlap MERGE detection

For each pair of KEEP commits in the range, compute Jaccard similarity of their
file sets:
```
similarity = |files(A) ∩ files(B)| / |files(A) ∪ files(B)|
```

If similarity ≥ 0.7, flag as a MERGE candidate — both commits are likely addressing
the same capability regardless of message wording. Surface as:
```
📁 File-overlap MERGE candidate — these commits share 4/5 files:
   abc1234  feat(api): add UserRepository SPI
   def5678  feat(api): wire UserRepository into ServiceLocator
   Overlap: UserRepository.java, UserRepositoryImpl.java, UserRepositoryTest.java, ...
```

Do not merge commits from different features/scopes just because files overlap.
Confirm that the overlap makes semantic sense (same module, same capability).

#### 3h — Cross-author check

For any KEEP or MERGE candidate that would be absorbed into a commit from a different
author — reclassify as KEEP and flag it. Cross-author squash is only permitted when
the absorbed commit is already classified SQUASH (formatting, CI, spelling).

#### 3i — Cherry-pick detection

For commits classified SQUASH or MERGE, check if any appear on other branches:
```bash
# Get patch-id for the commit
git show <sha> | git patch-id --stable

# Compare against all other branches
git log --all --format="%H" -- | grep -v $(git rev-list <range>) | \
  xargs -I{} sh -c 'git show {} | git patch-id --stable' 2>/dev/null
```

If a commit being squashed has a matching patch-id on another branch, warn:
```
⚠️  Cherry-pick detected: abc1234 appears on branch release/2.1
    Squashing this commit rewrites its identity — the cherry-pick will conflict on
    future merges. Confirm? (YES to proceed, n to keep standalone)
```

---

### Step 4 — Show summary

```
Commit squash analysis — <N> commits in range

  Already clean (KEEP, no action): <n>
  SQUASH candidates: <n>
    Docs follow-on (Javadoc/wording):  <n>
    Formatting/cleanup (chore):        <n>
    Revert chains:                     <n>
    Small fixups (< 5 lines):          <n>
    Test hardening:                    <n>
  MERGE candidates: <n>
    Same scope/feature pairs:          <n>
    File-overlap detected:             <n>
    Temporal clusters:                 <n>
  DROP (truly empty, zero files): <n>

  Result: <N> commits → <M> commits — <absorbed> absorbed (no content lost), <dropped> dropped
```

**The plan is mandatory. Execution never happens without explicit user YES.**

For any range > 10 commits, always write the full plan to a file on the working
branch AND present it to the user before asking for approval. Never skip this step.
Never execute Step 6 without having shown the plan and received YES.

```bash
# Determine plan path — check ## Artifact Locations in CLAUDE.md first
PLAN_FILE="docs/superpowers/specs/squash-plan-$(date +%Y-%m-%d).md"
```

Write the complete plan (all groups, three-column tables, curated results, AFTER block)
to the working branch. Then say: "Plan written to `<path>`. Review it, then reply YES
to execute, or tell me which groups to change." Wait for explicit YES.

The file travels with the working branch for external review. Never offer a "skip"
path that bypasses the plan — there is none for ranges > 10 commits.

**Large-range handling (> 50 commits):** skip straight to a group view:

```
<N> commits is a large range. How would you like to review?

  group   — show one capability group at a time (recommended)
  bulk    — show summary only; accept/refuse by pattern category
  full    — show the complete plan (may be very long)
```

For **"group"**: present one squash group at a time, get YES/n per group, then move
to the next. Show progress: "Group 3 of 12."

For **"bulk"**: list pattern categories with counts and let the user accept/refuse
each category en masse before reviewing individual exceptions.

For **"full"** or for ranges ≤ 50 commits, continue to Step 5a.

---

### Step 5a — Full plan (if user says YES or range ≤ 50)

#### Already-clean section

**Default (≤ 100 clean commits):** compact format. Reviewers care about what's changing, not the clean history in detail.

```
## Already Clean — <n> commits (no action needed)
*To see all: `git log --oneline <base>..<work-branch>` excluding action groups.*

Representative: feat(supplement), feat(merkle), feat(causality), feat(art12)...
```

**For > 100 clean commits** (reconstruction scale only): use the capability narrative table so the clean history reads as a project arc, not a dump:

```markdown
## Already Clean — <n> commits

| Capability | Commits | What was built |
|------------|---------|----------------|
| supplement | 14 | LedgerSupplement base, serialiser, V1002 migration, Art.22 example |
| merkle | 12 | MMR algorithm, verification service, Ed25519 signed checkpoint |
| causality | 8 | findCausedBy SPI + JPA, correlationId core, e2e tests |
```

Group by scope from `feat(scope):` prefix; one summary line per scope from the most descriptive subjects.

#### Already-clean callout

```
## Already Clean — <n> commits (no action needed)
*To see all: `git log --oneline <base>..<HEAD>` excluding the action groups below.*

Representative: feat(supplement), feat(merkle), feat(causality), feat(prov), ...
```

#### Grouping intelligence — before building groups

**Semantic grouping for spec/plan commits:** Before assigning any commit to a group,
identify design spec and implementation plan commits (`docs: design spec — X`,
`docs: implementation plan for X`). Scan **forward** chronologically for the
`feat:`/`refactor:` commit that implements topic X. Absorb the spec/plan into
that implementing commit's group, not the nearest preceding KEEP.

If no implementing commit is found within the range: flag the spec/plan with ⚠️
rather than silently absorbing it into an unrelated KEEP.

**Session handover detection:** A commit whose subject contains "session handover"
or "session wrap" must never be used as a group KEEP. When filter-repo leaves one
behind (mixed-content commit with other files), flag it explicitly — see format below.

**Title fitness assessment:** After grouping, assess whether the KEEP commit's message
adequately represents the group:
- All absorbed commits in same scope/feature → KEEP title is fine, use as-is
- Absorbed commits from different concerns, OR KEEP is a minor doc/chore carrying significant absorbed work → flag ⚠️ and propose synthesized title
- Synthesized title: a genuine summary of the group — not concatenation, a real subject line

#### Action groups

Use the output format that matches the available context.

**When PR/branch context is available (Strategies A–D from Step 0b):**

Use PR or scope headings. Group number is secondary metadata for refusal commands.

*Compaction format (Strategies B, C, D — all original commits present):*
```markdown
### PR #47 — feat(causality): findCausedBy — causal chain traversal (2026-04-18) [MDPROCTOR]
*Compaction group 8 — 3 commits → 1*

| Commit | Action | Curated result |
|--------|--------|----------------|
| `3717757` feat(causality): findCausedBy — SPI + JPA + 6 @QuarkusTest IT tests | ✅ KEEP | *(message adequate — unchanged)* |
| `26fe313` docs: design spec — causality query API | 🔽 SQUASH ↑ | *(absorbed — pre-implementation planning doc; message adequate)* |

> **Result:** 1 commit.
```

*Reconstruction format (Strategy A — squash-merged PRs, recovering original commits):*
```markdown
### PR #38 — refactor(api): rename DispatchRule → Binding (2026-04-14) [MDPROCTOR]
**Branch:** `feat/rename-binding-casedefinition`
**Final message:** `refactor(api): rename DispatchRule → Binding — unified with schema rename`

| Original commit | Action | Curated result |
|----------------|--------|----------------|
| `2ca7bfb` refactor(api): rename DispatchRule → Binding | ✅ KEEP | *(see Final message above)* |
| `5ac72ea` refactor(schema): rename CaseHubDefinition.yaml | 🔀 MERGE ↑ | *(unified — same rename scope)* |
| `441213d` chore: remove .claude/ from tracking | 🔽 SQUASH ↑ | *(absorbed — < 5 lines, no issue ref)* |

> **Result:** 1 commit.
```

**When no PR/branch context is available (Strategy E — flat compaction):**

Use three-column table per group matching the engine reconstruction plan style.
The heading is the semantic group title (KEEP message or synthesized), group number
is secondary metadata for refusal commands only.

**Curated result for KEEP rows — active assessment required:**

Read all commit messages in the group (subjects **and** bodies). Ask: does the
KEEP subject line fully describe what this group represents after absorption?

Assessment logic:
1. If absorbed commits add meaningful structural context not in the KEEP subject
   (rename sweep absorbing source moves + CI fixes, MERGE of two capability halves)
   → synthesize an enhanced subject. **The result must be richer than either message
   alone — not concatenation.** One coherent thought, not two stapled with a semicolon.
2. If the KEEP subject genuinely covers the whole group → write
   `*(message adequate — unchanged)*` to confirm the assessment happened.
3. **Never silently echo the original KEEP message** in the Curated result column.

**When the curated message differs from the original — Final message line:**
Surface the enhanced subject as a `**Final message:**` line above the table so it
isn't truncated by the table cell. The KEEP row then says `*(see Final message above)*`.

**Body snippets from absorbed commits:**
Non-trivial body content (rationale, constraints, approach notes) belongs as a
`📝` annotation line immediately after its table row — NOT inside the Curated result
cell. This keeps the cell clean and the body visible for review.

**Curated column visibility — show only when the result actually differs:**

The Curated result column is only shown when it adds signal. For KEEP rows:
- **Result differs from original** (enhanced subject, MERGE synthesis): show full three-column table with Curated result
- **Result = message adequate** (unchanged): show the KEEP row with only two visible columns — drop the Curated cell entirely. Do not collapse to a count (that loses the "assessed" signal); instead render: `| ✅ KEEP | ` with no third column.

For a group where all absorbed commits are pure noise (style, chore, stale refs, CI one-liners) AND the KEEP message is unchanged, use the compact layout:

```markdown
## <semantic group title>
*Compaction group — <N> commits → 1*

✅ KEEP `<sha>` <subject>
> Absorbed: <absorbed subjects on one line>

> **Result:** 1 commit.
```

Only expand to the full three-column table when:
- The curated message is enhanced (Final message line is present)
- An absorbed commit has a non-trivial body worth noting (📝)
- A ⚠️ flag applies (handover, proximity-grouped, no-op pair)

This preserves the "was assessed" signal while eliminating visual noise from unchanged rows.

**SQUASH group with enhanced subject (Final message above table):**
```markdown
## <semantic group title>
*Compaction group — <N> commits → 1*
**Final message:** `<synthesized subject — one coherent thought, richer than any individual message>`

| Commit | Action | Curated result |
|--------|--------|----------------|
| `<sha>` <KEEP message> | ✅ KEEP | *(see Final message above)* |
| `<sha>` <absorbed message> | 🔽 SQUASH ↑ | *(absorbed — <reason>; context reflected in Final message)* |

> **Result:** 1 commit.
```

**MERGE group:**
```markdown
## <semantic group title>
*Compaction group — <N> commits → 1*
**Final message:** `<unified subject — combines both messages, richer than either alone>`

| Commit | Action | Curated result |
|--------|--------|----------------|
| `<sha>` <KEEP message> | ✅ KEEP | *(see Final message above)* |
| `<sha>` <merged message> | 🔀 MERGE ↑ | *(unified — <what combining adds that neither message alone captured>)* |

> **Result:** 1 commit.
```

**Title fitness flag (when KEEP message doesn't represent the group):**
```markdown
## <KEEP message>
*Compaction group — <N> commits → 1*
⚠️ **Proposed title:** `<synthesized title>`
*(<reason the KEEP title is inadequate>)*

| Commit | Action | Curated result |
|--------|--------|----------------|
...
```

**Session handover survived filter-repo:**
```markdown
## ⚠️ <session handover message>
*Compaction group — <N> commits → 1*
⚠️ **KEEP commit is a session handover** — filter-repo left this because the commit
contains mixed content. Consider splitting manually before compacting, or accept as-is.

| Commit | Action | Curated result |
|--------|--------|----------------|
| `<sha>` <handover message> | ⚠️ KEEP (handover survived filter) | `<message>` — *flag for manual review* |
| `<sha>` <absorbed message> | 🔽 SQUASH ↑ | *(absorbed — <reason>)* |

> **Result:** 1 commit (handover message preserved — review recommended).
```

**File-overlap MERGE hint (question, not auto-classified):**
```
📁 *Group <N> shares significant file overlap with group <M> — possible MERGE?*
```

**Temporal scrutiny (inline annotation):**
```
| `<sha>` <message> | ✅ KEEP ⏱ | *[<N> min after <sha2> — confirm genuinely distinct]* |
```

**Drop (truly empty):**
```
| `<sha>` <message> | ❌ DROP | *(zero file changes confirmed)* |
```

**Cross-author retention (inline flag):**
```
| `<sha>` <message> | ✅ KEEP ⚠️ | *(kept standalone — cross-author; contains design content)* |
```

#### AFTER block

**Critical:** The AFTER sample must be generated from the working branch **after squash executes** (Step 6), not before. SHAs and commit count in the plan's AFTER block are estimates based on the KEEP commits identified in classification — the real values only exist post-execution.

In the plan (pre-execution), show the simulation using KEEP commit SHAs sorted most-recent-first:
```python
# Simulate post-squash order: KEEP commits in reverse chronological order
all_keeps_sorted = sorted([g['keep'] for g in groups], key=lambda c: c['idx'], reverse=True)
sample = all_keeps_sorted[:10]
```

After squash executes (Step 6), regenerate the AFTER block from the actual working branch state:
```bash
git log --oneline <base>..<work-branch> | head -10
```

Never use `git log` on main, the backup branch, or any pre-squash state for the AFTER sample — those SHAs are stale and will include commits that were absorbed.

```
## AFTER — what `git log --oneline` will show

  <N>  commits (original)
  -<n>  pruned by filter-repo
  -<n>  absorbed by squash
  ──────────────────────────────────────────────
  <M>  commits — no content lost

Sample (most recent 10 — from working branch after squash):
  <sha>  <message>
  ...
  (run `git log --oneline <work-branch>` to verify)
```

#### Refusal prompt

```
Refuse any group? Enter group numbers (e.g. "12 35"), "all" to accept all,
or "none" to refuse all:
```

Show confirmation and wait for final YES.

---

### Step 5b — User requests changes to plan

The plan is always written and shown. If the user wants changes rather than
outright YES:

```
Which groups to change? Enter group numbers to refuse, or describe what to adjust.
Reply YES when the plan reflects what you want.
```

Never proceed to Step 6 without YES. Never offer "apply all without reviewing."

---

### Step 6 — Execute

**If nothing to do:** confirm and exit. Offer to delete the working branch.

**Single-commit squash** (fast path — only when squashing HEAD~1 into HEAD):
```bash
git reset --soft HEAD~1 && git commit --amend --no-edit
```

**Multi-commit squashes:** write the todo and execute non-interactively:
```bash
PLAN=$(mktemp)
cat > "$PLAN" <<'PLAN_EOF'
pick abc1234 feat(api): add UserRepository SPI
squash ghi9012 docs(api): align findByKey Javadoc wording
pick jkl0123 feat(engine): add CaseRepository
PLAN_EOF

GIT_SEQUENCE_EDITOR="cp $PLAN" git rebase -i <base-sha>
rm -f "$PLAN"
```

**Multi-issue reference preservation:**

Before finalising any curated message (SQUASH or MERGE groups), collect all issue
references from every commit in the group — KEEP and all absorbed:

```bash
# Extract all issue refs from a commit message
git log -1 --format="%s%n%b" <sha> | grep -oE '(Closes|Refs|Fixes) #[0-9]+'
```

Deduplicate across the group: `Closes #N` takes precedence over `Refs #N` for the
same issue number. Append any refs not already in the KEEP commit's message:

```
feat: add TrustGateService (Closes #33)   ← KEEP
docs(trust): note capabilityTag (Refs #34) ← absorbed

Curated: feat: add TrustGateService — Closes #33, Refs #34
```

Both issues get a link in GitHub and both get the commit in their timeline.

**MERGE messages — conventional commit enforcement:**

For each MERGE operation, before finalising the unified message:

1. **Format check** (if `CONVENTIONAL=true`): the proposed message must follow
   `type(scope): description`. If it doesn't, suggest a corrected form before
   showing it to the user.

2. **Scope drift check**: if the two commits being merged have different scopes
   (`feat(auth)` and `feat(payment)`), flag it:
   ```
   ⚠️  Scope drift: merging (auth) and (payment) — different concerns.
       Merging may violate single-responsibility.
       Recommend KEEP instead? (YES / n to merge anyway)
   ```

3. Apply the message via:
   ```bash
   git commit --amend -m "<unified message>"
   ```

**AFTER block — correct arithmetic:**

Compute absorbed count as a simple subtraction, not by comparing commit subjects:

```bash
BEFORE_SQUASH=$(git log --oneline <base>..<work-branch-pre-squash> | wc -l)
AFTER_SQUASH=$(git log --oneline <base>..<work-branch-post-squash> | wc -l)
ABSORBED=$(( BEFORE_SQUASH - AFTER_SQUASH ))
```

Do NOT compute absorbed by counting `original_subjects - compacted_subjects` —
subject matching double-counts commits that appear under different wording and
misses commits whose subjects changed. Arithmetic is authoritative.

**Filter-repo stripped commits in the plan:**

Commits eliminated by Phase 0 filter-repo (became empty after blog/HANDOFF.md
removal, pruned by `--prune-empty`) disappear from the compacted branch just like
squashed commits. When building the plan by comparing original vs compacted, they
will appear in the "absorbed" set — but they were handled by Phase 0, not squash.

Distinguish them: before building groups, identify which original commits were
purely workspace artifact commits (only touched `blog/`, `HANDOFF.md`, or other
filtered paths). Label those in the plan as:
```
| `sha` <subject> | 🚫 FILTER-REPO | *(stripped by Phase 0 — commit only touched workspace artifact files, became empty and was pruned)* |
```

Do not attribute filter-repo eliminations to squash groups. They are not squash
candidates — they were eliminated before squash ran.

**Net no-op pair detection:**

When a squash group absorbs both an operation and its reversal — `chore: migrate X`
+ `chore: restore X`, or `feat: add Y` + `revert "feat: add Y"` — flag it:

```
⚠️ Net no-op pair: this group absorbs both [commit A] and its reversal [commit B].
   Combined effect on the tree is zero for the affected files. Only other files
   in those commits contribute any lasting change.
```

Detect by looking for: migrate/restore pairs on the same path, add/revert pairs
on the same subject, or any two absorbed commits that together produce a zero diff
on their shared files.

**Post-squash interval tree verification (automatic — mandatory, not a placeholder):**

After rebase completes, automatically sample and verify. Run before showing the
result to the user. Run it. Do not skip.

```bash
TOTAL=$(git log --oneline <base>..<work-branch> | wc -l)
STEP=$(( TOTAL / 5 ))  # 5 evenly-spaced samples

git log --format="%H" <base>..<work-branch> | awk -v step=$STEP 'NR % step == 0 {print}' | while read compacted_sha; do
  subject=$(git log -1 --format="%s" "$compacted_sha")
  original_sha=$(git log --format="%H %s" <backup-branch> 2>/dev/null | grep -F "$subject" | head -1 | awk '{print $1}')
  if [ -n "$original_sha" ]; then
    # Use printf not echo: echo "" | wc -l returns 1 (false positive for empty diff)
    diff_out=$(git diff "$original_sha" "$compacted_sha" -- ':!HANDOFF.md' ':!blog/' 2>/dev/null)
    diff_lines=$(printf '%s' "$diff_out" | wc -l | tr -d ' ')
    status=$([ "$diff_lines" -eq 0 ] && echo "✅ diff=0" || echo "⚠️  diff=$diff_lines")
    echo "  $status  [$subject]"
  else
    echo "  ⚠️  not found in backup  [$subject]"
  fi
done
```

**Interpreting results — show all 5 to the user:**
- `diff=0` — content intact ✓
- `diff=N (small, N<30)` — expected timeline shift from squashing; verify HEAD diff is clean
- `diff=N (large, N≥30)` — investigate before proceeding; may indicate content loss or conflict resolution changed content
- `not found` — sample commit's subject changed during squash; check nearby commit

Do not proceed to the review gate if any large diffs or unexplained "not found" entries appear.

Show the result in group format with real post-rebase SHAs.

---

### Step 6b — Mixed-content handover resolution (when ⚠️ groups exist)

When the plan contains ⚠️ groups where the KEEP commit is a session handover that
survived filter-repo as mixed content, offer an interactive resolution before executing:

```
Group N has a session handover as KEEP (mixed content survived filter-repo):
  Project files changed: CLAUDE.md (17 lines), docs/integration-guide.md (3 lines)
  
Options:
  a — Extract project file changes to a separate commit, squash the handover
  b — Keep as-is (handover message stays in history)
  c — Rename commit to describe the project changes only (drop handover message)
```

**If option a:** use `git show <sha> -- <project-files>` to create a patch, apply it
as a new commit with a descriptive message, mark the original as SQUASH into it.

Offer this resolution after showing the plan but before applying squash operations.

### Step 6c — Post-squash quality check (opt-in)

The quality check is a **companion tool, not an inline gate**. git-squash is about noise reduction; message quality is a separate concern with different triggers. Offer it at the review gate, not automatically:

```
Squash complete. Run quality check on surviving commits? (YES / n)
  Checks: subject length vs diff size, missing rationale bodies, non-conventional subjects.
```

Only run if the user says YES. If they decline, proceed directly to the review gate.

When run, assess surviving commit quality:

```bash
# For each KEEP commit in the compacted range
git log --format="%H %s" <base>..<work-branch> | while read sha subject; do
  diff_lines=$(git show --stat --format="" $sha | awk '/changed/{sum+=$1} END{print sum}')
  body=$(git log -1 --format="%b" $sha | grep -v '^$' | wc -l)
  echo "$sha $diff_lines $body $subject"
done
```

Flag these patterns:

| Pattern | Severity | Message |
|---------|----------|---------|
| Subject < 50 chars AND diff > 50 lines | ⚠️ | Subject too brief for change size — consider expanding |
| No body AND diff > 30 lines AND no issue ref | 📝 | Large change without rationale — consider adding context |
| Non-conventional subject on significant commit | 📝 | Consider adding type/scope prefix |

Output a quality summary before the review gate:
```
Quality check: 2 ⚠️  5 📝  (show details? YES / n)
```

Never blocks execution — this is signal, not a gate.

### Step 7 — Review gate

```
Working branch: squash/wip-<branch>-<timestamp>

Compare against original:
  git diff <orig-branch>...squash/wip-<branch>-<timestamp>
  git log --oneline <orig-branch>..squash/wip-<branch>-<timestamp>

Push working branch for review by others? (YES / n)
  YES — git push -u origin squash/wip-<branch>-<timestamp>

Ready to swap? (YES / n / push-first)
```

Wait for explicit YES before proceeding to Step 8.

---

### Step 8 — Swap branches

```bash
BACKUP="backup/pre-squash-${ORIG_BRANCH}-$(date +%Y%m%d)"
git branch -m "$ORIG_BRANCH" "$BACKUP"
git branch -m "$WORK_BRANCH" "$ORIG_BRANCH"
git branch --set-upstream-to="origin/$ORIG_BRANCH" "$ORIG_BRANCH" 2>/dev/null || true
git push --force-with-lease origin "$ORIG_BRANCH"
```

**Post-swap working tree check (mandatory):**

After the swap and push, verify the working tree is clean:

```bash
git status --short
git log origin/"$ORIG_BRANCH".."$ORIG_BRANCH" --oneline
```

If `git status --short` produces any output (staged or unstaged changes), hard stop:
> "⚠️  Swap complete but working tree is dirty — staged/unstaged changes remain.
>  These will be invisible to the next session if not committed.
>  Commit or discard before ending the session."

If `git log origin/...` shows unpushed commits, warn:
> "⚠️  Swap complete but $ORIG_BRANCH has N unpushed commits — push or note in handover."

Do not consider the squash complete until the working tree is clean and the branch is pushed.

Confirm:
```
✅ Swap complete.
  Active branch:  <orig-branch> (squashed history)
  Backup branch:  backup/pre-squash-<orig-branch>-<YYYYMMDD> (original history)

To push backup for off-machine safety:
  git push origin backup/pre-squash-<orig-branch>-<YYYYMMDD>

To undo entirely:
  git checkout backup/pre-squash-<orig-branch>-<YYYYMMDD>
  git branch -m <orig-branch> squash/wip-<orig-branch>-<timestamp>
  git branch -m backup/pre-squash-<orig-branch>-<YYYYMMDD> <orig-branch>
  git push --force-with-lease origin <orig-branch>
```

---

### Step 9 — Backup cleanup (offered on future runs)

On any subsequent `/git-squash` invocation, check for old backup branches:
```bash
git branch | grep "backup/pre-squash-"
```

If any exist, surface them before starting new work:
```
Old squash backups found:
  backup/pre-squash-main-20260415    (21 days ago)
  backup/pre-squash-feat-auth-20260502    (4 days ago)

Delete any? Enter branch names, "all", or "none" to skip:
```

Only delete on explicit user confirmation.

---

## Pre-Push Workflow (fast — unpushed commits only)

When invoked in response to the pre-push hook, skip Steps 0, 1, 7, 8, and 9.
In-place squash is safe — history hasn't been shared yet.

1. **Step 2:** Resolve unpushed range (`@{u}..HEAD`)
2. **Step 3:** Classify per policy (run all analysis passes, including temporal
   grouping, file-overlap, and conventional commit detection — skip cherry-pick
   detection and PR integration as they add friction to the fast path)
3. **Step 4:** Show summary
4. **Step 5:** Show plan and get approval
5. **Step 6:** Execute in-place
6. **Push:** `git push` (no force needed)

---

## Installing the pre-push hook

The pre-push hook checks unpushed commits for obvious squash candidates and exits 1
if found, prompting the user to run `/git-squash` first. It never runs filter-repo.

```bash
HOOK_SRC="$HOME/.claude/skills/git-squash/hooks/pre-push"
HOOK_DEST="$(git rev-parse --git-dir)/hooks/pre-push"

if [ -f "$HOOK_DEST" ]; then
  echo "⚠️  pre-push hook already exists at $HOOK_DEST — skipping."
else
  cp "$HOOK_SRC" "$HOOK_DEST"
  chmod +x "$HOOK_DEST"
  echo "✅ pre-push hook installed."
fi
```

Bypass with `git push --no-verify` after manually confirming history is clean.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Resolving commit range before filter-repo | filter-repo rewrites all SHAs; range is stale | Always resolve range after Phase 0 completes |
| Running filter-repo without `--refs` | Rewrites entire repo history, not just working branch | Always pass `--refs refs/heads/$WORK_BRANCH` |
| Claiming to filter CLAUDE.md sections | filter-repo operates on whole file paths only | Offer whole-file filtering only; handle CLAUDE.md commits via squash pass |
| Swapping branches without review gate | No chance for second opinion on pushed history | Always show review gate before swap |
| Dropping commits with file changes | Silent data loss | Use Phase 1 filter-repo to strip files first; only drop truly empty commits |
| Squashing a KEEP/MERGE commit from a different author | Rewrites attribution | Cross-author squash only for SQUASH-classified noise |
| Using fast-path reset for non-HEAD squash pairs | Amends the wrong commit | Fast path only when squash pair is HEAD←HEAD~1 |
| Running filter-repo from pre-push hook | Destructive rewrite must be deliberate | filter-repo on-demand only, never automatic |
| Skipping Project Artifacts check | May filter project history | Always resolve Project Artifacts before scanning |
| Using `git rebase -i` without GIT_SEQUENCE_EDITOR | Opens interactive editor; blocks | Always use `GIT_SEQUENCE_EDITOR="cp $PLAN"` |
| Merging commits with different scopes without warning | Violates single-responsibility | Scope drift check on all MERGE operations |
| Squashing commits cherry-picked to other branches | Future merges will conflict | Cherry-pick detection before squashing |
| Using `--force` instead of `--force-with-lease` | Overwrites concurrent pushes | Always use `--force-with-lease` |
| Squashing commits with issue references | Loses traceability | Issue references are always KEEP — see policy |

---

## Skill Chaining

**Invoked by:** User directly via `/git-squash`; pre-push hook when squash
candidates detected

**Reads:** `~/.claude/skills/git-squash/squash-policy.md` — the classification rules

**Does not invoke anything** — standalone analysis and rebase skill
