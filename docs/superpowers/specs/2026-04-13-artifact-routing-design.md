# Artifact Routing — Design Spec

**Date:** 2026-04-13
**Status:** Superseded by `docs/superpowers/specs/2026-04-14-workspace-routing-design.md`

> ⚠️ **Vocabulary in this spec is deprecated.** The destination values `base`, `project repo`,
> and config key `design-journal` have been replaced. See the 2026-04-14 spec for current
> vocabulary: `project`, `workspace`, `alternative <path>`, `design`.

---

## Problem

The current workspace model routes all artifacts to the project repo at epic
close. In practice, colleagues and authors have preferred alternative
destinations — a separate docs repo, a personal blog repo, a team wiki. There
is no way to declare these preferences; everything lands in the project repo
by default.

---

## Solution

A declarative `## Routing` section in workspace `CLAUDE.md`. If absent,
existing behaviour is unchanged. If present, `epic-close` reads it and routes
each artifact to its declared destination.

---

## Core Principle

> The absence of routing config means nothing changes. Routing is opt-in,
> additive, and declared in the workspace — not in the project repo.

---

## Routing Config

A new section in workspace `CLAUDE.md`, separate from `## Artifact Locations`
(which records where skills write *during* the epic — a different concern).

```markdown
## Routing

**Base destination:** `~/docs/team-wiki/`

| Artifact | Destination |
|----------|-------------|
| `adr` | base |
| `blog` | base |
| `design-journal` | project repo |
| `docs` | `~/personal-blog/docs/` |
```

**Destination values:**

| Value | Meaning |
|-------|---------|
| `base` | Use the base destination with the artifact's standard subdirectory appended (e.g. `~/docs/team-wiki/adr/`) |
| An explicit path | Use this path as-is; overrides base entirely |
| `project repo` | Promote to the project repo — existing behaviour |

**Defaults:**
- If `## Routing` section is absent — all artifacts go to project repo (current
  behaviour, unchanged)
- If `## Routing` section exists but an artifact has no row — project repo
- Base destination is optional; if omitted, explicit paths are used per-artifact

**Configuration:** Added manually to workspace `CLAUDE.md` when non-default
routing is wanted. `workspace-init` does not prompt for it — routing is an
ongoing concern, not a setup concern.

---

## Destination Capability Detection

`epic-close` inspects each destination path and adapts its behaviour:

```
destination path
  ├── doesn't exist yet → create it, then copy
  ├── exists, no .git  → plain filesystem copy
  ├── exists, has .git, no remote → copy + commit
  └── exists, has .git, has remote → copy + commit + push
```

**Detection logic:**
```bash
if [ -d "<dest>/.git" ]; then
  if git -C "<dest>" remote get-url origin &>/dev/null; then
    # remote git — copy + commit + push
  else
    # local git — copy + commit
  fi
else
  # plain filesystem — copy only
fi
```

**Commit message for git destinations:**
```
feat: promote <artifact-type> from <project> epic <epic-name>
```

**On failure:** `epic-close` reports what succeeded and what failed — it does
not roll back successful promotions. The user resolves failures manually
(e.g. no network for push) and can re-run the promotion for that artifact.

**Subdirectory convention:** when routing to a base destination, the
artifact's standard subdirectory is appended automatically:
`~/docs/team-wiki/` + `adr/` → `~/docs/team-wiki/adr/`

---

## Artifact Coverage

| Artifact | Default (no routing config) | Routable |
|----------|-----------------------------|---------|
| `adr` | Promoted to project repo | Yes |
| `blog` | Promoted to project repo | Yes |
| `design-journal` | Posted to GitHub issue, then discarded | Yes — routing overrides discard |
| `snapshots` | Left in workspace git history | Yes |
| `specs` | Posted to GitHub issue, then discarded | No — ephemeral by design |
| `plans` | Posted to GitHub issue, then discarded | No — ephemeral by design |
| `handover` | Discarded | No — session-scoped, no value after epic |

**Key decisions:**
- `specs` and `plans` are never routable — their value is captured in the
  GitHub issue post; the documents themselves are working artifacts
- `handover` is never routable — session-scoped noise after the epic closes
- `design-journal` routing overrides the default discard — if a destination
  is declared, it is promoted there instead of being discarded after posting

---

## Relation to Existing Workspace Model Spec

This extends the `Epic Lifecycle — epic-close` section of
`2026-04-09-workspace-model-design.md`. Step 3 (Promote ADRs) and Step 4
(Promote blog entries) now route via the routing config rather than always
going to the project repo. All other steps unchanged.

---

## Out of Scope

- Blog entry type differentiation (article vs. note) and complex blog routing
  — see IDEAS.md; separate epic
- `epic-start` and `epic-close` full skill specs — see mdproctor/cc-praxis#49
