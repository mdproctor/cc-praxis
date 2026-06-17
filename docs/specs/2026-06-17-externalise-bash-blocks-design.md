# Externalise Mechanical Code from SKILL.md Files

**Issue:** #123
**Date:** 2026-06-17
**Status:** Approved (revised after second review)

## Goal

Remove all embedded bash and Python from SKILL.md bodies into callable `.py`
scripts. Skills become pure workflow guidance — decision trees, sequencing,
user messages. Scripts handle mechanics.

Two motivations drive this:
1. **Permission prompt elimination** — every inline bash command triggers Claude
   Code's permission system. Python scripts called via `python3 /path/script.py`
   are pre-approved and never prompt.
2. **Token reduction** — bash blocks load into context when the skill is invoked.
   Mechanical code the LLM doesn't reason about wastes context window.

## Audit Summary

| Category | Count |
|----------|-------|
| Total bash/python blocks across all SKILL.md files | 294 |
| Instructional (stay in SKILL.md — templates, examples, patterns) | ~55 |
| Already externalised (11 existing scripts) | ~25 |
| DATA — cheap lookups → ctx.py | ~85 |
| DATA — expensive (gh, complex git log) → inline or per-skill | ~33 |
| OPERATION (write operations → per-skill scripts) | ~96 |

**Instructional blocks by skill:**

| Skill | Instr. blocks | What they contain |
|-------|--------------|-------------------|
| python-dev | 21 | Good/bad code pattern examples |
| workspace-init | 12 | INDEX.md, HANDOFF.md, CLAUDE.md, .gitignore templates |
| fix-ci | 5 | Example test commands (mvn, npm, pytest) the LLM adapts |
| issue-workflow | 4 | Epic/issue body templates, git restore/add-p guidance |
| retro-issues | 3 | Epic/issue body templates |
| sync-local | 3 | Example invocation commands for users |
| git-squash | 2 | Rebase todo template, AFTER block template |
| publish-blog | 2 | blog-routing.yaml format examples |
| adr | 1 | MADR template |
| handover | 1 | Mermaid decision flowchart |
| write-content | 1 | Style guide loading example |

Top skills by block count: workspace-init (44), git-squash (36), work-end (31),
python-dev (21 — all instructional), work-start (17), git-commit (16),
issue-workflow (15), handover (14), retro-issues (13), update-claude-md (13),
work-pause (12), publish-blog (11).

## Core Principle

**Separate reasoning from execution.**

Every bash block decomposes into:
- **Reasoning** (what to do, what content to generate) → stays in SKILL.md
- **Execution** (running commands, writing files, API calls) → extracted to scripts

There is no block where the execution itself requires LLM judgment. Judgment
applies to choosing inputs and interpreting outputs, never to the act of running
a command. Even blocks where the LLM generates content (commit messages, issue
bodies) split cleanly: the LLM generates the content, then passes it to a script
that delivers it.

### What stays in SKILL.md

- Decision trees and conditional paths (flowcharts, state detection)
- Content generation instructions (what commit message to write, what issue body)
- User-facing messages (prompts, confirmations, status reports)
- Reasoning guidance (how to interpret script output, when to take which path)
- Instructional code examples (python-dev patterns, fix-ci test commands)
- Common Errors tables (expected error codes and recovery actions)

### What goes to scripts

- File I/O (existence checks, reads, writes, directory creation)
- Git operations (add, commit, push, checkout, rebase, branch creation)
- GitHub API calls (issue create/close/edit, PR operations)
- Path resolution (already in ctx.py)
- Multi-step mechanical sequences (stash → checkout → pull → commit → push)

### Handling conditions

Conditions in bash blocks follow a simple rule:

- **Mechanical condition** (derivable from data: SINGLE_REPO, PROJECT_TYPE,
  HAS_META) → the condition moves INTO the script. Pass the data value as
  an argument. The script handles the branching internally.
- **Judgment condition** (requires LLM: "is this diff too large?", "does this
  follow conventions?", "should we squash these?") → the condition stays in
  SKILL.md. The LLM evaluates, then calls the script for the chosen path.

## Architecture

### Two-layer extraction: ctx.py primary, per-skill scripts secondary

**ctx.py is the primary extraction mechanism.** It absorbs all cheap data
lookups that skills currently perform via inline grep, ls, and git-read
commands. This eliminates the largest class of blocks (~85 across all skills)
with zero new scripts.

**Per-skill scripts handle write operations** that ctx.py cannot: git commits,
pushes, file creation, GitHub API calls, multi-step sequences with side effects.

**ctx.py boundary:** only CHEAP LOCAL operations. File existence checks,
CLAUDE.md/config parsing, .meta field extraction, git local state. GitHub API
calls (`gh issue view`, `gh pr list`) are slow, can fail, and aren't always
needed — they do NOT go in ctx.py. They stay as inline LLM commands or in
per-skill scripts.

### Script protocol

**Default: KEY=VALUE output** — matches existing ctx.py / scaffold.py pattern.
Used by all scripts except commit_gather.py (see below).

- Output `KEY=VALUE` lines on stdout for data
- Exit 0 on success, non-zero on error
- All paths passed as CLI arguments — no hardcoded paths
- `key=value` argument style for named parameters

**Exception: JSON output** — for scripts that return structured per-record data
(e.g., per-commit records). commit_gather.py outputs JSON because per-commit
data with nested fields (files, issue refs, patch IDs) doesn't fit KEY=VALUE.
The LLM parses JSON natively.

**Error output protocol:**

```
ERROR=<error_code>
ERROR_DETAIL=<human-readable message>
```

Where `error_code` is a machine-readable identifier (branch_exists, dirty_tree,
network_error, auth_failed, file_not_found). `ERROR_DETAIL` is what the LLM
shows to the user.

Scripts report facts. SKILL.md documents expected errors and recovery actions:

```markdown
### Common Errors
| Error code | Recovery |
|------------|----------|
| branch_exists | Ask user to choose a different name or delete existing |
| dirty_tree | Run git status, show uncommitted files, ask user to stash |
```

### Content passing protocol

When a script needs content the LLM generates (commit messages, issue bodies,
file content):

- **Single-line content:** pass as a CLI argument (`message="feat: add X"`)
- **Structured content with fixed format:** script generates from arguments.
  Example: EPIC-CLOSED.md has a fixed format — pass branch, date, issues as
  args, script assembles it. No LLM-authored prose needed.
- **Multi-line LLM-generated content:** LLM writes to `/tmp/cc-praxis-<context>.md`
  using the Write tool, passes the path as `content-file=<path>`. Script reads
  the file, uses its content, and deletes the temp file after use.

Most cases are "structured with fixed format." The content-file pattern is rare
and only needed when the LLM authors freeform prose that a script delivers.

### No shared operation scripts

Git commit+push and `gh issue close` appear across many skills. A shared
`git_ops.py` with `commit(repo, files, msg)` was considered and rejected.

The reason: **subprocess.run is already one line in Python.** A shared
function saves 1 line per call site (16 instances across 7 skills = 16 lines
total). A shared module adds import machinery, a new file, a new test file,
and cross-skill coupling — for 16 lines of savings. Error handling is already
consistent: `check=True` raises CalledProcessError everywhere.

If the atomic operations were genuinely complex (5+ lines each, error recovery
logic, retries), a shared utility would pay for itself. They're not — they're
`subprocess.run(["git", "-C", path, "commit", "-m", msg], check=True)`.

### Script naming convention

Scripts are named by WHAT THEY DO, following the established pattern:
ctx.py, routing.py, scaffold.py, blog_dest.py, section_hashes.py,
check_links.py, flyway_scan.py, create_symlinks.py.

No generic `ops.py` convention. Each script name is self-documenting:

| Instead of | Use |
|-----------|-----|
| `workspace_ops.py` | `workspace_create.py`, `artifact_migrate.py`, `hook_install.py` |
| `work_end_ops.py` | `artifact_promote.py`, `branch_cleanup.py` |
| `squash_ops.py` | `commit_gather.py`, `rebase_exec.py`, `branch_swap.py` |
| `commit_ops.py` | `staged_check.py`, `commit_exec.py` |

Some skills have 2-3 small focused scripts. Test files group by skill
(e.g., `test_workspace_init_scripts.py` covers all scripts in workspace-init/).

### Thin script threshold

**3+ operations OR any multi-step sequence → script.**
**1-2 simple operations in a rarely-used skill → LLM inlines.**

A single `git add + commit` wrapped in a Python script with argparse, error
handling, and a test file is unnecessary complexity — an abstraction with no
architectural benefit. The 4 eliminated skills (adr, update-claude-md,
implementation-doc-sync, project-refine) each have 1-2 simple operations
that run rarely. The script overhead exceeds the benefit.

3+ operations justify a script because it provides atomic execution, consistent
error handling, and the test investment scales with operation count.

### Testing protocol

From the externalised-scripts-require-tests protocol (PP-20260609-df21ed):

- Script + test committed together, never separately
- Tests cover: happy path, 2+ edge cases, bad argument handling
- Use `tmp_path` pytest fixtures — no hardcoded paths in tests
- Test files group by skill directory, not per-script

## Phase 1 — ctx.py Expansion

One commit. ctx.py is the primary extraction mechanism.

### New fields

| New KEY | Value | Skills that benefit |
|---------|-------|-------------------|
| `PROJECT_TYPE` | `java`, `skills`, `blog`, `custom`, `generic`, or empty | 10 skills |
| `ISSUES_STATUS` | `enabled`, `declined`, `absent` | 7 skills (9 uses) |
| `HAS_META` | `yes` / `no` | 5 skills |
| `DESIGN_REPO_KEY` | `workspace`, `project`, `cross-repo:<name>`, or empty | 2 skills |
| `HAS_ARC42STORIES` | `yes` / `no` | 4 skills |
| `HAS_PROJECT_ARTIFACTS` | `yes` / `no` | 2 skills |
| `WORKSPACE_DECLINED` | `yes` / `no` | 1 skill |
| `HAS_PLATFORM_DOC` | `yes` / `no` | 1 skill |
| `HAS_PROTOCOLS_DIR` | `yes` / `no` | 1 skill |
| `BLOG_DIR` | path or empty | 2 skills |
| `HAS_BLOG_ROUTING` | `yes` / `no` (checks both global and project locations) | 3 skills |
| `PROJECT_NAME` | from CLAUDE.md `**Name:**` field, or empty | 1 skill |
| `HAS_WRITING_STYLE_REF` | `yes` / `no` | 1 skill |
| `FLYWAY_NEXT_V` | from .meta, or `unknown` | 1 skill |

**Lifecycle note:** `DESIGN_REPO_KEY` and `FLYWAY_NEXT_V` are populated from
.meta fields. They are empty when no .meta exists (before work-start completes
or on main). Skills that use these fields already gate on `HAS_META=yes`.

**DESIGN_SECTION_HASHES** is NOT a new ctx.py field. ctx.py returns the stored
baseline hashes from .meta (already part of its .meta parsing, named
`META_SECTION_HASHES`). The separate `section_hashes.py` script computes current
hashes from DESIGN.md. The LLM compares stored vs current. No inlining needed.

### ISSUES_OK → ISSUES_STATUS (atomic rename)

ISSUES_OK is replaced with ISSUES_STATUS in a single commit. ctx.py and
every SKILL.md that reads it, updated atomically. No backwards compatibility
period. There are no end users — the platform owner controls all callers.

### Anti-pattern fix

`work/SKILL.md` greps CLAUDE.md for `**Workspace:**` instead of using ctx.py.
The handover SKILL.md explicitly documents why this is wrong (multiple CLAUDE.mds
are loaded, parent's workspace declaration is found first). Fixed in Phase 1.

### git-squash/ctx.py

Stays separate — it adds squash-specific fields (commit ranges, candidate
analysis) that don't belong in the shared ctx.py. Its `BASE_BRANCH` extraction
should delegate to project-init ctx.py output rather than re-implementing.

**Delegation mechanism:** The SKILL.md already calls project-init/ctx.py in
Path Resolution. git-squash/ctx.py should accept `base-branch=<value>` as an
argument and stop parsing CLAUDE.md for it. The SKILL.md passes the value
through — consistent with the architecture (SKILL.md orchestrates, scripts
receive explicit arguments).

### What does NOT go into ctx.py

- Multi-line content (Project Artifacts section, Health Check Configuration)
- Routing cascade (ADR/blog destination) — already handled by routing.py
- GitHub API calls — too slow, can fail, not always needed
- Complex git log analysis — expensive, skill-specific
- Live DESIGN.md section hashes — section_hashes.py handles this
- update-claude-md's validation checks — too specialised

### ctx.py growth strategy

ctx.py grows from 93 lines to ~150-200 lines. This is manageable as a single
file. No module split needed at this scale.

**Selective computation:** Not needed. All fields are cheap (file existence
checks, string parsing, git local state). The most expensive operation is
`subprocess.run("git", "rev-parse", ...)` at ~10ms. Adding 15 file checks
adds ~5-10ms. If a genuinely expensive field is ever proposed, the answer is
"that field doesn't belong in ctx.py" — not "add a --fields flag."

**Testing gap:** No test_ctx.py exists. Phase 1 creates one. Strategy: create
temp directories with CLAUDE.md, .meta, and git state via tmp_path fixtures.
Verify KEY=VALUE output for each field. Edge cases: missing CLAUDE.md, missing
.meta, single-repo mode, workspace-declined flag.

### Phase 1 eliminates ~85 blocks

After Phase 1, approximately 85 inline grep/ls/file-check blocks across
10+ skills are replaced by reading ctx.py output. Each SKILL.md replaces
those blocks with "use `PROJECT_TYPE` / `ISSUES_STATUS` / etc. from ctx.py."

The remaining ~33 DATA blocks involve expensive operations (GitHub API calls,
complex git log analysis) that stay as inline commands or move to per-skill
scripts where they're part of a larger operation sequence.

## Phase 2 — Per-Skill Scripts

One commit per skill. Each commit contains:
1. New script(s) in the skill directory (descriptive names)
2. Corresponding test file in `tests/`
3. Updated SKILL.md with bash blocks replaced by script call instructions

### Skills that need scripts (8 full + 3 thin = 11)

| Priority | Skill | Scripts | Key operations | Blocks elim. |
|----------|-------|---------|---------------|-------------|
| 1 | workspace-init | `workspace_create.py`, `artifact_migrate.py`, `hook_install.py` | dir creation, git init, gh repo create, hook install, artifact migration | ~18 |
| 2 | work-end | `artifact_promote.py`, `branch_cleanup.py` | promote to main/project, journal merge, issue close, scaffold removal, EPIC-CLOSED | ~16 |
| 3 | git-squash | `commit_gather.py`, `rebase_exec.py`, `branch_swap.py` | commit data collection, rebase execution, branch rename + force push | ~15 |
| 4 | work-pause | `pause_exec.py` | WIP commit (both repos), push, stack push, branch switch | ~7 |
| 5 | work-resume | `resume_exec.py` | stack pop, checkout, rebase, WIP reset | ~5 |
| 6 | issue-workflow | `issue_setup.py` | label creation, hook install, epic/issue creation, scope update | ~5 |
| 7 | retro-issues | `retro_create.py` | bulk epic/issue creation, issue close | ~4 |
| 8 | publish-blog | `blog_publish.py` | copy entries, commit destinations, remove sources | ~5 |
| 9 | git-commit (thin) | `commit_exec.py` | execute commit, optional squash | ~4 |
| 10 | handover (thin) | `handover_commit.py` | commit HANDOFF.md to workspace main | ~3 |
| 11 | work-start (thin) | `branch_create.py` | dual-repo branch creation + scaffold commit | ~2 |

**work-start note:** Phase 1 delivers most of work-start's improvement
(7 DATA blocks → ctx.py). The Phase 2 `branch_create.py` handles only 2
remaining operations. work-start is already the best-externalised skill.

### Skills that do NOT need scripts (4 eliminated)

After Phase 1 ctx.py expansion, these skills have only 0-2 trivial write
operations remaining. Per the thin script threshold (< 3 operations, rarely
used), the LLM inlines these:

- **update-claude-md** — 10 DATA blocks (→ ctx.py), 2 remaining operations
  (curl config-arch refresh, apply CLAUDE.md changes). The "apply changes"
  is LLM file editing, not a script operation.
- **adr** — 2 DATA blocks (→ ctx.py), 1 remaining operation (git add + commit).
- **implementation-doc-sync** — 3 DATA blocks (→ ctx.py), 2 remaining operations
  (gh issue create, git add + commit).
- **project-refine** — 5 DATA blocks (→ ctx.py), 1 optional operation (write
  report file).

### Skills that already have no bash blocks

After Phase 1, these skills have only instructional or pre-approved blocks:

code-review, dependency-update, security-audit, update-design (type detection
only — ctx.py), project-health (type detection + validate_all.py invocation),
project-init (fast-path checks — ctx.py), work (state detection — ctx.py),
sync-local, python-dev, ts-dev, java-dev, fix-ci, idea-log, write-content.

### git-squash: deeper treatment

git-squash is the most complex skill (1320 lines, 36 blocks). It deserves
specific attention because many of its bash blocks are embedded in decision
trees — the LLM uses git output to classify commits, which is reasoning, not
mechanical execution.

**The 36 blocks break down as:**
- Already externalised: 3 (ctx.py for ranges, compaction targets, rebase todo)
- Instructional: 2 (rebase todo template, AFTER block template)
- DATA (16): PR/branch metadata fetch, merge commit scanning, commit data
  gathering (log formats), conventional commit detection, PR body fetch,
  issue ref extraction, SHA verification, timestamp analysis, cherry-pick
  detection, before/after counts
- OPERATION (15): working branch creation, filter-repo execution, soft reset,
  rebase execution, commit amend, quality check iteration, push, branch swap
  (rename × 3, set upstream, force push), backup cleanup

**Two data-gathering phases** — separated by filter-repo (which rewrites SHAs):

1. **Pre-filter (Steps 0b, 1a, 1b):** PR/branch metadata, Project Artifacts
   resolution, file scan across range. Some of this is cheap (Project Artifacts
   → ctx.py HAS_PROJECT_ARTIFACTS, blog routing → ctx.py HAS_BLOG_ROUTING).
   The expensive parts (gh pr list, git branch -r) stay inline.

2. **Classification (Steps 3a-3i):** per-commit subject, body, author, date,
   files, stat, issue refs, patch-ids, conventional commit detection, PR body.
   This is what `commit_gather.py` collects.

**commit_gather.py scope:** collects classification data only (Steps 3a, 3b,
3c, 3d-pre, 3f, 3i). Invoked AFTER filter-repo completes (SHAs are stable).

**commit_gather.py output format:** JSON, not KEY=VALUE. Per-commit data with
nested fields doesn't fit KEY=VALUE:

```json
{
  "range": "abc..def",
  "commit_count": 15,
  "is_conventional": true,
  "pr": {"number": 47, "title": "...", "body": "...", "base": "main"},
  "commits": [
    {
      "sha": "abc1234",
      "subject": "feat: add X",
      "body": "Because Y...",
      "author": "alice@example.com",
      "date": "2026-04-18T14:30:00",
      "files": ["src/X.java", "test/XTest.java"],
      "insertions": 45,
      "deletions": 3,
      "issue_refs": [{"type": "Closes", "number": 33}],
      "patch_id": "deadbeef1234"
    }
  ]
}
```

The LLM reads this JSON and applies classification rules from squash-policy.md.
The script gathers facts; the LLM reasons over them.

**What stays outside commit_gather.py:**
- Pre-filter context (Steps 0b, 1a, 1b) — runs before filter-repo, different SHAs
- SHA verification (Step 3e) — pre-execution check, not classification
- Post-execution counts (Step 6) — two simple git log commands
- Post-squash interval verification — already in git-squash/ctx.py

**rebase_exec.py** takes the LLM's classification output (which commits to
pick/squash/merge, curated messages) and executes the rebase non-interactively.

**branch_swap.py** handles the Step 8 branch rename + force push sequence.

### SKILL.md transformation examples

**Simple case (no conditions):**

Before:
```markdown
### Step 10 — Commit scaffold

\```bash
git -C "$WORKSPACE" add design/JOURNAL.md design/.meta
git -C "$WORKSPACE" commit -m "init(<branch>): scaffold workspace branch"
git -C "$WORKSPACE" push
\```
```

After:
```markdown
### Step 10 — Commit scaffold

Run: `python3 ~/.claude/skills/work-start/branch_create.py commit-scaffold <workspace> branch=<name>`
Read COMMITTED=yes/no from output.
If ERROR=dirty_tree: run git status and report to user.
```

**Conditional case (mechanical condition):**

Before:
```markdown
### Step 9 — Mark closed

\```bash
if [ "$SINGLE_REPO_MODE" = "yes" ]; then
    git -C "$WORKSPACE" checkout "$BRANCH_NAME"
fi
mkdir -p "$WORKSPACE/design"
cat <<EOF > "$WORKSPACE/design/EPIC-CLOSED.md"
# Closed: $BRANCH_NAME
...
EOF
git -C "$WORKSPACE" add design/EPIC-CLOSED.md
git -C "$WORKSPACE" commit -m "chore: mark $BRANCH_NAME closed"
git -C "$WORKSPACE" push
if [ "$SINGLE_REPO_MODE" = "yes" ]; then
    git -C "$WORKSPACE" checkout main
fi
\```
```

After:
```markdown
### Step 9 — Mark closed

Run: `python3 ~/.claude/skills/work-end/branch_cleanup.py create-epic-closed <workspace> branch=<name> single-repo=<yes/no> date=<YYYY-MM-DD> issues=<comma-sep>`

The script handles: conditional checkout (single-repo mode), EPIC-CLOSED.md
generation from structured inputs (fixed format — no LLM-authored content
needed), git add + commit + push, and conditional checkout back to main.

Read CREATED=yes/no from output.
```

The mechanical condition (`SINGLE_REPO_MODE`) moves into the script — it's
derivable from data, not LLM judgment. The content has a fixed format and is
assembled from arguments — no temp file or content passing needed.

**Judgment condition (stays in SKILL.md):**

```markdown
### Step 3b — Squash candidate check

Read UNPUSHED_COUNT from ctx.py output.

If UNPUSHED_COUNT > 1:
  Ask: "There are N unpushed commits. Squash before committing? (y/n)"
  If yes → run: `python3 ~/.claude/skills/git-commit/commit_exec.py squash <project>`
  If no → proceed to Step 4.
```

The LLM decides whether to offer the squash. The script executes whichever
path is chosen.

## Execution Strategy

**Phase 1** is one commit: ctx.py expansion (14 new fields) + SKILL.md
updates across all affected skills + test_ctx.py creation + ISSUES_OK →
ISSUES_STATUS atomic rename.

**Phase 2** is one commit per skill, heaviest first (workspace-init → work-end
→ git-squash → ...).

**Session boundary:** Multi-session work. Target per session: Phase 1 + 2-3
Phase 2 skills. Each commit is independently useful.

**Verification between commits:**
- `python3 -m pytest tests/test_ctx.py -v` (Phase 1)
- `python3 -m pytest tests/test_<skill>_scripts.py -v` (Phase 2, per skill)
- `python3 scripts/validate_all.py --tier commit` — no SKILL.md regressions

## Risks and Mitigations

**Script fails at runtime but skill worked before.**
Inline bash was tested implicitly every invocation. New scripts could have
bugs. Mitigation: mandatory tests (happy path + edge cases + bad inputs).
Scripts output structured errors (ERROR=code, ERROR_DETAIL=message).
SKILL.md documents expected errors and recovery actions.

**SKILL.md becomes too terse.**
Mitigation: SKILL.md keeps decision logic AND documents what each script
expects/returns. Common Errors tables list recovery actions. The script
call is embedded in the workflow step with context, not isolated.

**ctx.py grows too large.**
At ~150-200 lines after expansion, it remains manageable as a single file.
All fields are cheap local operations (<10ms total). No selective computation
needed. If an expensive field is ever proposed, the answer is "it doesn't
belong in ctx.py" — not "add a --fields flag."

**Remaining bash blocks after full externalisation.**
~33 expensive DATA blocks (GitHub API, complex git log) stay as inline
commands. ~55 instructional blocks (templates, code examples) stay by design.
~25 blocks already externalised. This is intentional, not incomplete.

**Token savings by tier:**
- Heavy skills (workspace-init, work-end, git-squash): ~20-25% reduction.
  workspace-init: ~350 lines of bash → ~60 lines of script calls = ~24%.
- Medium skills (git-commit, issue-workflow, handover): ~10-15% reduction.
- Light skills (adr, project-refine): ~2-5% reduction.
- Skills with only instructional blocks (python-dev, fix-ci): 0% — and
  that's correct; those blocks are the skill's guidance.

## Out of Scope

- Rewriting decision logic or flowcharts
- Changing skill chaining
- Extracting instructional code examples (python-dev, fix-ci)
- Merging or splitting skills
- Shared operation scripts (per-skill scripts only)
- GitHub API calls in ctx.py (too slow, too fragile)
- Live DESIGN.md hash computation in ctx.py (section_hashes.py handles this)

## Deliverables

- 1 expanded ctx.py (14 new fields) + test_ctx.py (new)
- ~25 new per-skill scripts across 11 skills (descriptive names)
- ~11 new test files (grouped by skill)
- ~25 updated SKILL.md files
- ~175 bash blocks eliminated (85 via ctx.py + 84 via per-skill scripts + 6 inlined by sub-threshold skills)
- ~119 blocks intentionally remaining (55 instructional + 25 already externalised + 33 expensive DATA + 6 trivial)
- Zero permission prompts for mechanical operations
