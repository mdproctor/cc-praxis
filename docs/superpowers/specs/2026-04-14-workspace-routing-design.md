# Workspace Routing Design

**Date:** 2026-04-14
**Status:** Approved
**Extends:** `docs/superpowers/specs/2026-04-13-artifact-routing-design.md`

---

## Problem

The artifact routing spec (2026-04-13) introduced declarative routing for epic-close artifacts.
However, all valid destinations were either the project repo or external repos. For projects
that want zero methodology artifacts in their project repo, there was no permanent home for
ADRs, DESIGN.md, snapshots, and other artifacts between epics.

The workspace is already a git repo with a `main` branch. Epic branches already fork from it.
Nothing routes artifacts *back* to workspace/main at epic close.

---

## Solution

Add `workspace` as a first-class routing destination. Introduce a three-layer config that
preserves the built-in default (all artifacts → project repo) while allowing a global user
preference and per-workspace per-artifact overrides.

---

## Three Routing Targets

| Target | Meaning |
|--------|---------|
| `project` | Artifact goes to the project repo — existing behaviour |
| `workspace` | Artifact is committed to workspace/main — new |
| `alternative <path>` | Artifact goes to a different git repo — existing capability |

### `alternative <path>` Syntax

```
alternative ~/personal-blog/
alternative /absolute/path/to/repo/
```

Rules:
- Keyword `alternative` followed by exactly one space, then the path
- Path must start with `/` (absolute) or `~` (tilde-expanded to `$HOME`)
- Path must not contain unquoted spaces. If path has spaces: `alternative ~/my\ docs/`
- Invalid: `alternative` (no path), `alternative~` (no space), `/path` (no keyword)
- Path is validated to exist before epic-close begins routing

### Artifact Names in Routing Config

| Config key | What it routes |
|------------|---------------|
| `adr` | All ADR files in `adr/` |
| `blog` | All blog entries in `blog/` |
| `design` | The journal-to-DESIGN.md merge operation (not JOURNAL.md itself) |
| `snapshots` | All design snapshots in `snapshots/` |

The `design` key controls **where DESIGN.md lives** — the merge destination. JOURNAL.md
is always posted to the GitHub issue then discarded, regardless of routing. If routing
`design: workspace`, the merged DESIGN.md is written to workspace/main; if `design: project`,
it is written to the project repo (current behaviour).

---

## Three-Layer Config

```
Layer 1 (built-in):   project            ← nothing configured = nothing changes
Layer 2 (global):     ~/.claude/CLAUDE.md  ## Routing
Layer 3 (workspace):  <workspace>/CLAUDE.md  ## Routing  (per-artifact)
```

### Resolution Algorithm (formal)

For each artifact type at epic-close:

```
1. If artifact row present in Layer 3 table → use Layer 3 value
2. Else if Layer 2 section present AND has a valid **Default destination:** line → use Layer 2 value
3. Else → use Layer 1 default: project
```

**Edge cases — explicit rules:**

| Situation | Behaviour |
|-----------|-----------|
| Layer 3 `## Routing` section absent | Treat as absent; fall to Layer 2 |
| Layer 3 table present but artifact not listed | Fall to Layer 2 |
| Layer 3 table empty | Treat as absent; fall to Layer 2 |
| Layer 2 section absent | Treat as absent; fall to Layer 1 |
| Layer 2 present but no `**Default destination:**` line | Treat as absent; fall to Layer 1 |
| Any layer has invalid value | Warn user; fall to next layer |
| `alternative` keyword with no path | Invalid; warn and fall to next layer |

### Layer 2 — Global (`~/.claude/CLAUDE.md`)

```markdown
## Routing
**Default destination:** workspace
```

Valid values: `workspace` or `project` only. No alternative path at global level —
a global alternative would require all workspaces to share the same external repo path,
which is not meaningful.

### Layer 3 — Per-Workspace (`<workspace>/CLAUDE.md`)

```markdown
## Routing

| Artifact   | Destination                  |
|------------|------------------------------|
| adr        | workspace                    |
| design     | workspace                    |
| blog       | alternative ~/personal-blog/ |
| snapshots  | workspace                    |
```

All three targets are valid at this layer. Unspecified artifact types fall through to
Layer 2.

---

## workspace/main as Artifact Accumulator

The workspace is a git repo initialised by `workspace-init` with a `main` branch.
Epic branches already fork from workspace/main. This means artifacts committed to
workspace/main at one epic close are naturally visible at the next epic start — no
additional mechanism needed.

**Flow:**
```
workspace/main (ADRs, DESIGN.md, snapshots from previous epics)
    └── epic/feature-x (new artifacts written during the epic)
            └── epic-close → commits artifacts back to workspace/main
workspace/main (updated — all artifacts accumulated)
    └── epic/feature-y (next epic, sees everything)
```

**Journal merge with `design: workspace` — baseline shift:**

When `design → workspace`, the three-way merge must operate against workspace/main's
`DESIGN.md`, not the project's. This requires a different SHA baseline:

| Routing | Baseline source | Merge target | Baseline recorded by |
|---------|----------------|--------------|---------------------|
| `design: project` | project HEAD at epic-start | project DESIGN.md | epic-start (current behaviour) |
| `design: workspace` | workspace/main HEAD at epic-start | workspace/main DESIGN.md | epic-start (reads routing config) |

**epic-start** reads the routing config at branch creation time. If `design → workspace`,
it records the **workspace/main HEAD SHA** in `design/.meta` instead of the project HEAD SHA.

**epic-close** three-way merge when `design → workspace`:
```
baseline = git -C <workspace> show <workspace-sha>:DESIGN.md
current  = workspace/main HEAD DESIGN.md
journal  = design/JOURNAL.md §Section entries
result   → write merged DESIGN.md to workspace/main
```

This ensures each epic's journal merge builds on accumulated workspace design knowledge,
regardless of what the project repo does independently. There is no ratcheting problem
because the baseline advances with workspace/main, not the stale project SHA.

---

## epic-close Changes

`epic-close` reads the layered routing config and resolves the effective target for
each artifact before routing:

```
1. Read ~/.claude/CLAUDE.md ## Routing → global default (workspace | project)
2. Read <workspace>/CLAUDE.md ## Routing → per-artifact overrides
3. For each artifact: apply Layer 3 override if present, else Layer 2, else Layer 1
4. Route per resolved target:
   - project    → existing project repo routing (unchanged)
   - workspace  → git commit to workspace/main
   - alternative → existing external repo routing (unchanged)
```

**Committing to workspace/main:**
```bash
git -C <workspace-path> checkout main
git -C <workspace-path> add <artifact-files>
git -C <workspace-path> commit -m "feat: promote <artifact-type> from epic <epic-name>"
# push if workspace has a remote
git -C <workspace-path> push 2>/dev/null || true
```

---

## workspace-init Changes

Update the workspace CLAUDE.md template to document the `## Routing` section and its
three valid targets. The section is optional — absence means all artifacts go to the
project repo (Layer 1 default).

Add an example routing section to the template showing all three targets.

---

## Two-Level Routing for Blog Entries

Blog entries are the only artifact type with a second level of routing beyond the
workspace `## Routing` config:

| Level | Config | Governs | When |
|-------|--------|---------|------|
| 1 | `<workspace>/CLAUDE.md ## Routing` | Where `blog/` directory lives (project/workspace/alternative) | epic-close |
| 2 | `~/.claude/blog-routing.yaml` | Which blog platforms each entry is cross-posted to, based on entry_type/tags/projects | publish-blog |

Level 1 is handled by `epic-close` (batch, same as ADRs and snapshots). Level 2 is
handled by the `publish-blog` skill (per-entry, platform publishing). The two levels
are independent — `epic-close` does not read `blog-routing.yaml`.

Other artifact types (ADRs, snapshots) only need Level 1. Per-entry routing for ADRs
is out of scope until explicitly requested.

---

## Scope

**In scope:**
- Three-layer routing config (Layer 1 built-in, Layer 2 global, Layer 3 workspace)
- `workspace` as a valid routing target
- `epic-close` routing resolution and workspace/main commit
- `workspace-init` CLAUDE.md template update
- Updated artifact routing design spec

**Out of scope:**
- `workspace` as a global alternative path (not meaningful)
- Changes to workspace git structure (already correct)
- Changes to epic-start branching model (already forks from workspace/main)
- UI or tooling for inspecting accumulated workspace artifacts

---

## Vocabulary Reconciliation

The 2026-04-13 artifact routing spec used different target names. This spec supersedes that vocabulary:

| Old term (2026-04-13) | New term (2026-04-14) | Notes |
|-----------------------|-----------------------|-------|
| `project repo` | `project` | Same meaning; shorter |
| `base` | _(removed)_ | Was shorthand for base destination path; replaced by `workspace` or explicit `alternative <path>` |
| `design-journal` (config key) | `design` | The config key; `design-journal` was the old artifact name |

The old terms must not be used in new workspace CLAUDE.md routing configs. epic-close
should warn and fall through to the next layer if it encounters `project repo` or `base`.

---

## Backward Compatibility

- No `## Routing` anywhere → all artifacts go to project repo (unchanged)
- Existing workspaces with `## Routing` pointing to `project repo` → unchanged
- New `workspace` target only activates when explicitly configured
