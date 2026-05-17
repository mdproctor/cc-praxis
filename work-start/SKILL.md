---
name: work-start
description: >
  MUST be invoked at the start of every piece of work — user says "work-start",
  or it appears as the first instruction in a work-item prompt. Runs four
  mandatory checks before any design or implementation begins: reads the
  platform doc and runs the coherence protocol against the described work,
  checks relevant protocols, confirms an issue exists, and verifies IntelliJ
  MCPs with a hard stop if unavailable. These checks are NOT optional and must
  NOT be skipped even for small changes. Failure to run this skill before
  starting work risks violating platform conventions, missing relevant rules,
  working without an issue, or silently degrading to bash when IntelliJ is
  unavailable.
---

# Work Start

Four mandatory checks before any design or implementation begins.
**All four must complete before proceeding.**

---

## 0 — Check Epic State

Before anything else, check whether a workspace epic is in progress:

```bash
cat design/.meta 2>/dev/null
git branch --show-current
```

Also read the project repo branch:
```bash
grep "add-dir" CLAUDE.md | head -1 | sed 's/.*add-dir //'
# then:
git -C <project-path> branch --show-current
```

| State | Action |
|-------|--------|
| `.meta` exists, both repos on same epic branch | Surface epic name and issue number — you are mid-epic |
| `.meta` exists, branches differ | **Stop** — branch mismatch. Switch both repos to the same branch before proceeding |
| `.meta` on main branch | **Stop** — orphaned `.meta`. Run `/epic` to clean up before starting work |
| No `.meta`, both on main | **Stop** — no active epic. See below before continuing |

**If no active epic (no `.meta`, both on main):**

```
⚠️  No active epic detected. Before proceeding, choose one:

  1. Issue-scoped work      → invoke /epic begin to create the epic branch
  2. Exploratory/isolated   → invoke superpowers:using-git-worktrees
  3. Intentional main work  → confirm explicitly before continuing

Do not proceed to steps 1–4 below until one of these is resolved.
```

Wait for the user to respond before continuing.

**Do NOT output the work-start summary. Do NOT say "proceeding to brainstorming". Do NOT continue to steps 1–4.** This is a hard gate — the session stops here until the user picks one of the three options above.

**After the user responds:**
- Option 1 (epic begin): wait for `/epic begin` to complete, then resume work-start from Step 1.
- Option 2 (worktrees): wait for `superpowers:using-git-worktrees` to complete, then resume work-start from Step 1.
- Option 3 (confirmed main): accept the confirmation and proceed to Steps 1–4 normally. Include `⚠️ Working on main (explicitly confirmed)` in the final work-start report.

**If mid-epic, include in the work-start report:**
```
⚡ Active epic: <epic-name>  Issue: #<N>
   Project branch: <branch>  Workspace branch: <branch>
```

---

## 1 — Read the Platform Doc and Run the Coherence Protocol

Locate the platform doc:

```bash
# casehubio
ls ~/claude/casehub/parent/docs/PLATFORM.md 2>/dev/null
# Other projects: check CLAUDE.md for platform-doc: key, or docs/PLATFORM.md
```

Read it, then run the Platform Coherence Protocol against the work described
in this prompt. The protocol asks — answer each one for the specific work:

1. **Does this already exist?** Is this capability implemented somewhere in the platform already?
2. **Is this the right repo?** Would this work more naturally live in a different repo?
3. **Does this create a consolidation opportunity?** Should existing similar code be unified?
4. **Is it consistent with platform patterns?** Does it follow the module tier structure, naming conventions, and architectural rules?
5. **Does it need a platform-level doc update?** Will PLATFORM.md, APPLICATIONS.md, or docs/repos/ need updating after this?

If any answer raises a concern, surface it to the user before proceeding.

---

## 2 — Check Relevant Protocols

```bash
ls ~/claude/casehub/parent/docs/protocols/
```

Scan the protocol list for any rules relevant to the described work. Common ones to check:

- Maven coordinate changes → `maven-coordinate-standard.md`, `artifact-rename-propagation.md`
- Flyway migrations → `flyway-migration-rules.md`, `flyway-version-range-allocation.md`
- SPI changes → `ledger-spi-propagation.md`, `spi-blocking-reactive-parity.md`
- Cross-repo deps → `artifact-rename-propagation.md`
- Module structure → `module-tier-structure.md`, `maven-submodule-folder-naming.md`

Read any that apply. Surface violations or constraints to the user before proceeding.

---

## 3 — Confirm an Issue Exists

```bash
gh issue list --state open --limit 10
```

- If an issue covers this work: note the issue number — every commit must reference it
- If no issue exists: create one now before proceeding

```bash
gh issue create --title "..." --body "..."
```

Do not proceed without an issue number.

---

## 4 — Verify IntelliJ MCPs

Call `mcp__intellij-index__ide_index_status` and `mcp__intellij__get_project_modules`.
Do NOT use the `LSP` tool — that is Claude Code's built-in LSP, not IntelliJ.

**If either MCP is unavailable:**
- Stop immediately
- Tell the user which MCP is missing
- Do not proceed with any semantic operation
- Do not fall back to bash, grep, or sed as substitutes
- Wait for the user to reconnect via `/mcp`

**If both are available:** confirm and continue.

IntelliJ can also drop mid-task. If at any point during the work a semantic
operation fails because an MCP is unavailable, stop again and tell the user
rather than silently falling back.

---

## Done — Report and Hand Off

Output a brief summary:

```
work-start complete.
Platform doc: [read / not found]
Coherence Protocol: [any concerns raised, or "clear"]
Protocols checked: [list any relevant ones read]
Issue: #N — [title]
IntelliJ: ✅ both connected / ⚠️ [missing — stopped]

Proceeding to brainstorming.
```

Then hand off to `superpowers:brainstorming` on the described work.
