---
name: implementation-doc-sync
description: >
  Use when documentation needs syncing — user says "sync docs", "update docs",
  "doc sweep", or invoked from a prompt snippet at session end. Scoped to what
  changed this session only, not a full project sweep. NOT a design journal
  update (java-git-commit handles that).
slash-command: false
---

# Implementation Doc Sync

Answer the question: **given what changed this session, which docs need to catch up?**

Scope is intentionally narrow — only docs that cover the components, capabilities,
or conventions that were modified. Sweeping unrelated docs wastes time and creates
noise.

---

## Step 1 — Establish Session Scope

Identify what changed. Use git and conversation context — do not guess.

```bash
# What repos have uncommitted or recently committed changes?
git log --oneline --since="8 hours ago"
git diff --name-only HEAD~5..HEAD 2>/dev/null | head -30
```

From this, extract:
- **Which repos** were touched (ledger, work, engine, etc.)
- **Which components** changed (specific modules, SPIs, APIs, protocols)
- **What kind of change** — new capability, rename, SPI change, protocol addition,
  dependency change, architecture decision

Store this as the **session scope**. Everything below is filtered through it.

---

## Step 1b — Establish Home Repo Boundary

**Run before checking any docs.** Every doc identified in Step 2 must be
checked against this boundary — peer-repo docs are never edited directly.

Run the bundled context script to resolve the home repo path:
```bash
python3 ~/.claude/skills/project-init/ctx.py
```

A doc is **in the home repo** if its absolute path starts with `<WORKSPACE>/`.

A doc is **in a peer repo** if its path starts with a sibling directory
(e.g. `../parent/`, `../engine/`, `../ledger/`) or any other git root
outside `$HOME_REPO`.

**Rule:**
- Home-repo docs → check and fix directly (Steps 3–5)
- Peer-repo docs → read for reference only; flag needed changes as a
  GitHub issue on the peer repo; **never edit or commit to them**

The CLAUDE.md of the current session may explicitly list peer repos
(look for "Never commit or push to peer repo directories" or a similar
rule). If listed, treat every repo on that list as peer-repo regardless
of path analysis.

---

## Step 2 — Map Changes to Docs

Use this mapping to identify which docs are in scope. Only include docs that
directly cover something in the session scope.

The **Location** column tells you where each doc lives. Home-repo docs are
fixed directly. Peer-repo docs are read for reference and any needed changes
are filed as GitHub issues — **never committed from this session**.

| Change type | Docs to check | Location |
|-------------|--------------|----------|
| New capability or feature | `docs/PLATFORM.md` → Capability Ownership table | **peer repo** (parent) |
| New or changed cross-repo dependency | `docs/PLATFORM.md` → Cross-Repo Dependency Map | **peer repo** (parent) |
| Repo renamed / restructured | `docs/PLATFORM.md` → Repository Map | **peer repo** (parent) |
| Per-repo deep dive affected | `docs/repos/casehub-{repo}.md` | **peer repo** (parent) |
| Application tier change | `docs/APPLICATIONS.md` | **peer repo** (parent) |
| New platform protocol | `docs/protocols/INDEX.md` + the protocol file itself | home repo |
| Existing protocol updated | The protocol file + any files that reference it | home repo |
| Convention or workflow change | `CLAUDE.md` (invoke `update-claude-md`) | home repo |
| Architecture decision | `adr/` (invoke `adr` if not yet recorded) | home repo |
| Design journal (epic branch) | `design/JOURNAL.md` (invoke `java-update-design`) | home repo |
| Maven coordinate change | `docs/protocols/maven-coordinate-standard.md` if convention changed | home repo |
| Cross-repo artifact rename | `docs/PLATFORM.md` → Cross-Repo Dependency Map | **peer repo** (parent) |

**Note on the Location column:** The entries marked "peer repo (parent)" apply
to the casehubio platform layout where `docs/PLATFORM.md` lives in the parent
repo. For other project layouts, apply the Step 1b boundary check to confirm
whether a given doc path is inside `$HOME_REPO` or not.

If a doc type is not in this table and not obviously related to the session
scope, skip it.

---

## Step 3 — Check Each In-Scope Doc

For each doc identified in Step 2, run this checklist:

### Drift
- Does the doc still accurately describe the current code/structure?
- Are any statements now false because of this session's changes?
- Are examples or code snippets still valid?

### Cross-references
- Do all links to other docs, files, or sections resolve?
- Do referenced file paths still exist (e.g. after folder renames)?
- Do referenced artifactIds match the current coordinates?

### Staleness
- Is there content that was accurate before this session but no longer is?
- Are version numbers, module names, or artifact names outdated?

### Gaps
- Is there something that changed this session that the doc should cover but doesn't?
- Was a new capability added that belongs in the Capability Ownership table?
- Was a new protocol created that isn't in INDEX.md?
- Was a new cross-repo dependency introduced that isn't in the Dependency Map?

---

## Step 4 — Fix and Report

Route each issue by location before acting:

### Home-repo docs — fix directly

1. Fix it directly — do not just flag it
2. Use IntelliJ `replace_text_in_file` for targeted edits; Edit tool for structured
   doc sections

### Peer-repo docs — file an issue, never commit

For any gap found in a peer-repo doc (e.g. `docs/PLATFORM.md` in the parent repo):

1. **Do not edit or commit to the peer repo**
2. File a GitHub issue on the peer repo describing exactly what needs updating:
   ```bash
   gh issue create --repo <owner/peer-repo> --title "docs: sync <doc-name> for <feature>" \
     --body "## What to update\n\n<exact change needed>\n\n## Context\n<why this change is needed>"
   ```
3. Report the issue number in the summary

After all actions, report a brief summary:

```
Doc sync complete — {n} docs checked, {n} updated, {n} issues filed:
- docs/protocols/INDEX.md: added artifact-rename-propagation.md entry        [home repo — fixed]
- CLAUDE.md: updated connector exclusion pattern                              [home repo — fixed]
- docs/PLATFORM.md: cross-repo dependency row needed                         [peer repo — issue #N filed on casehubio/parent]
- docs/repos/casehub-clinical.md: deep-dive needs sponsor notification note  [peer repo — issue #N filed on casehubio/parent]
- (no changes needed): docs/APPLICATIONS.md
```

If a gap requires more than a doc update (e.g. a missing ADR for a significant
decision), flag it: *"ADR not yet recorded for X — invoke `adr` to capture it."*
Do not silently skip it.

---

## Step 5 — Commit Doc Changes

**Before staging anything, verify you are in the home repo:**

```bash
CURRENT=$(git rev-parse --show-toplevel)
echo "Committing to: $CURRENT"
# Confirm this matches $HOME_REPO from Step 1b
```

If the current directory is not the home repo, `cd` to it explicitly before
staging. Never run `git add` from inside a peer repo directory.

If any home-repo docs were updated, commit them separately from code changes:

```bash
git -C "$HOME_REPO" add docs/
git -C "$HOME_REPO" commit -m "docs: sync documentation to session changes

[brief description of what was updated and why]

Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>"
```

Docs and code in separate commits keeps the history readable.

**Peer-repo changes are never committed here** — they were filed as GitHub
issues in Step 4 and are the responsibility of the peer repo's session.

---

## What This Skill Does NOT Do

- **Does not** check docs unrelated to the session scope — that is `project-health`
- **Does not** update the design journal — that is `java-update-design` (via `java-git-commit`)
- **Does not** update CLAUDE.md for convention changes — that is `update-claude-md`
  (but it will invoke those skills if the session scope triggers them)
- **Does not** write ADRs — it will flag the gap and suggest invoking `adr`
- **Does not** run tests or check code correctness — that is `superpowers:requesting-code-review`

---

## Skill Chaining

**Invoked by:** prompt snippet at end of implementation session; user says
"sync docs", "update docs", "doc sweep"

**Invokes when triggered by session scope:**
- `update-claude-md` — if conventions or workflows changed
- `java-update-design` — if on an epic branch and design decisions were made
- suggests `adr` — if a significant architectural decision lacks a record

**Complements:**
- `project-health` — full project correctness check (not session-scoped)
- `java-git-commit` — chains to `java-update-design` for design journal
- `work-end` — runs this as part of Step 3b pre-close sweep; writes HANDOFF.md after
- `handover` — runs this as part of the wrap checklist (mid-work sessions only)
