# git-squash Skill — 10 Systematic Improvements Spec

**Status:** In progress — Refs #62  
**Verification repo:** `~/claude/casehub/ledger` backup branch `backup/pre-squash-main-20260507`  
**After all 10:** Re-run compaction on ledger, work, qhorus, claudony, parent and replace main.

---

## Implementation Order

### Phase 1 — Quick wins (minimal code, easy to verify)

#### Improvement #10 — Row 17 path-based exceptions

**Current:** Any commit with <5 lines changed and no issue ref is squashed. Pure size heuristic, semantically blind.

**Fix:** Exempt from size-based squash:
- Security-relevant paths: `*auth*`, `*security*`, `*permission*`, `*secret*`, `*credential*`, `*encryption*`
- Configuration files: `application.properties`, `application.yml`, `pom.xml` (dependency/version changes)

Also require: the preceding commit must share at least one file before size-based auto-squash fires. Zero file overlap + small size = keep standalone.

---

#### Improvement #9 — Curated column collapse

**Current:** 40+ rows of "message adequate — unchanged" trains users to ignore the curated column.

**Fix:** In the plan document, suppress rows where curated result is "message adequate — unchanged" and replace with a count line:
```
> N commits absorbed with messages adequate — no changes to subject lines.
```
Only show the curated column rows where the result meaningfully differs (enhanced message, MERGE synthesis, quality flag). The table becomes signal-only.

---

#### Improvement #7 — Proximity-grouped resolution path

**Current:** Proximity-grouped annotation (zero word overlap with KEEP) labels the problem but offers no resolution. The wrong grouping still happens.

**Fix:** When a commit is proximity-grouped:
1. Scan forward up to 20 commits for a better semantic match (word overlap > 0)
2. If found: re-group there instead (with a note in the plan: "relocated from proximity group to semantic home")
3. If not found: classify as standalone KEEP micro-commit rather than forcing a wrong attachment — a small standalone chore is better history than a misattributed one

---

### Phase 2 — Medium effort

#### Improvement #3 — Same-issue clustering (full)

**Current:** Row 10 detects same-issue docs+feat pairs. General #N clustering does not happen.

**Fix:** Add a pre-classification pass that groups all commits sharing the same issue ref:
- If group = one feat + one or more fix/test/docs: MERGE all into the feat
- If group = multiple feat commits: KEEP each but annotate as parts of same issue
- If group = fix/test only (no feat): MERGE into most substantive, flag "no primary feat identified"
- Run this pass BEFORE pattern classification (between Step 3c and 3d)
- Issue refs extracted from both subject and body

---

#### Improvement #5 — Planning doc body carry-forward

**Current:** Design spec and implementation plan commits are absorbed into implementing feat. The planning commit body (rationale, approach, rejected alternatives) is discarded.

**Fix:** When absorbing a planning commit, extract its body content and add to the curated body of the implementing feat:
- Format: `[Plan: <planning commit subject>]` as a body line
- Followed by any extracted rationale (sentences containing "because", "to avoid", "per", "decided", constraint descriptions)
- Appears in the plan as an addition to the curated message body section
- Specific case of the general body synthesis (improvement #1)

---

#### Improvement #6 — Already-clean narrative structure

**Current:** Already-clean section is a flat representative scope list ("feat(supplement), feat(merkle)..."). No structure, no narrative.

**Fix:** Group already-clean commits by scope cluster with commit counts:
```
## Already Clean — 186 commits

| Capability | Commits | Representative |
|------------|---------|----------------|
| supplement | 14 | LedgerSupplement base, serialiser, supplements V1002 migration... |
| merkle | 12 | MMR algorithm, verification service, Ed25519 checkpoint... |
| causality | 8 | findCausedBy, correlationId core, e2e tests... |
| art12 | 7 | retention enforcement, archive record, audit queries... |
...
```
Makes the clean history read as a project narrative rather than a commit dump.

---

### Phase 3 — Significant effort

#### Improvement #1 — Commit body synthesis

**Current:** Commit bodies are gathered (Step 3a) but their substantive content is ignored when generating curated messages. Bodies disappear after squash.

**Fix:** Add synthesis pass (Step 3a-ii) that:
1. Extracts from all commits in a group: ADR references, rationale phrases ("because", "to avoid", "so that", "decided to"), constraint statements, rejected alternatives
2. Deduplicates and composes a synthesised body for the group's curated final commit
3. The curated result column shows the synthesised body alongside the (possibly enhanced) subject
4. Priority: ADR refs > explicit rationale > constraint statements > approach descriptions

---

#### Improvement #8 — Mixed-content handover resolution path

**Current:** ⚠️ flag for mixed-content handover surviving filter-repo, but no guided resolution.

**Fix:** When a mixed-content handover is detected (subject matches "session handover" but commit has project file changes), offer an interactive resolution:
```
This commit mixes a session handover with project file changes:
  Project files: CLAUDE.md (17 lines), docs/integration-guide.md (3 lines)
  
Options:
  a — Extract project changes to a separate commit, squash the handover message
  b — Keep as-is (handover message stays in history)
  c — Drop the handover text, rename commit to describe the project changes
```
Option a: uses `git show <sha> -- <project-files>` to create a patch, applies it as a new commit before the original, marks original as SQUASH.

---

#### Improvement #2 — Post-compaction quality gate

**Current:** Step 7 is a review gate for plan correctness. No assessment of surviving commit quality.

**Fix:** Add Step 7a quality assessment on the working branch after squash executes, before review gate:

For each KEEP commit, evaluate:
- Subject length < 50 chars AND diff > 50 lines → ⚠️ subject too brief for change size
- No body AND diff > 30 lines AND no issue ref → 📝 consider adding rationale
- Scope missing on conventional commit for significant change → 📝 add scope
- Non-conventional subject on significant commit → ⚠️ flag

Output a brief quality report grouped by severity:
```
Post-compaction quality check:
  ⚠️  2 commits with brief subjects on large changes
  📝  5 commits without rationale bodies on significant changes
  
Show details? (YES / n)
```
Flag severity: ⚠️ = should fix before publishing, 📝 = consider adding detail. Never blocks the squash.

---

#### Improvement #4 — PR/branch pre-pass (implement Strategy B)

**Current:** Five-strategy degradation is specced. Strategy E (flat) is always used in practice. Strategy B (merge commit boundaries) is the most impactful and most achievable without GitHub API.

**Fix:** Implement Strategy B for repos that use merge-commit PRs:
1. In Step 0b, scan for `Merge pull request #N` commits in the range (row 2a: KEEP)
2. These become natural group boundaries
3. Commits between two PR merges are pre-merge work for the PR that follows
4. Group heading: `### PR #N — <PR title or merge commit message> (date) [AUTHOR]`
5. Fall through to Strategy D/E if no merge commits found

Also: remove Strategies A and C from the documented hierarchy if they remain unimplemented after this session — specced-but-not-run creates false confidence.

---

## Verification Protocol (per improvement)

1. Implement changes in squash-policy.md and/or SKILL.md
2. Update plan generator Python code to match
3. Run on ledger backup branch: `backup/pre-squash-main-20260507`
4. Compare specific outputs to original ledger plan at `~/claude/casehub/ledger/docs/squash-plan-2026-05-06.md`
5. Confirm: improvement is visible in output, no groups regressed
6. Spot-check on qhorus backup (`backup/pre-squash-main-20260507`) for cross-repo confirmation
7. Sync skill to `~/.claude/skills/`, commit, push

## Post-completion

After all 10 verified:
1. Re-run full compaction workflow on each casehub repo backup branch
2. Compare new plans to original plans — confirm aggregate improvement
3. Swap new compacted branch onto main for each repo
4. Push to mdproctor forks
