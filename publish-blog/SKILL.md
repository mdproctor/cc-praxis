---
name: publish-blog
description: >
  Use when publishing blog entries to external platforms via blog-routing.yaml
  — user says "publish blog", "publish entries", "cross-post this entry", or
  invokes /publish-blog. NOT for writing new entries (use write-content with diary type for that).
---

# Publish Blog

Routes blog entries from the workspace blog directory to external publishing
destinations based on `blog-routing.yaml` routing rules.

This is a **second-level routing** step, independent of the workspace `## Routing`
config. That config controls where the `blog/` directory lives.
This skill controls where individual entries are cross-posted to blog platforms.

---

## Prerequisites

- `blog-routing.yaml` exists at `~/.claude/blog-routing.yaml` (global) and optionally
  at `<workspace>/blog-routing.yaml` (project override)
- Blog entries have `entry_type`, `projects`, and optionally `tags` in frontmatter
- Each destination path in the routing config is a valid directory

---

## Workflow

### Step 0 — Resolve blog directory

Use the same three-layer resolution as write-content (diary form):

1. `Blog directory:` field in CLAUDE.md — explicit path, highest priority
2. `## Routing` table in CLAUDE.md — `blog → workspace` means `<Workspace>/blog/`; `blog → project` means `<Project repo>/blog/`
3. Default: `blog/` relative to CWD

```bash
# Check for explicit Blog directory field
grep -i "blog directory:" CLAUDE.md 2>/dev/null

# Otherwise check routing table
grep -A 20 "^## Routing$" CLAUDE.md 2>/dev/null | grep "^| blog"
```

Resolve `BLOG_DIR` to an **absolute path** before proceeding.

### Step 1 — Load routing config

```bash
ls ~/.claude/blog-routing.yaml 2>/dev/null && echo "global found"
ls <WORKSPACE>/blog-routing.yaml 2>/dev/null && echo "project found"
```

If global config is missing, stop:
> "No global routing config found at `~/.claude/blog-routing.yaml`."

Read the global config with PyYAML. If a project-level `blog-routing.yaml`
exists in the workspace, read it too and merge: project `destinations` and
`rules` extend (not replace) the global ones.

**No external script.** Apply the routing logic directly:

**Matching rules** — for each entry, evaluate every rule in order:
- `entry_type: X` — exact match against frontmatter `entry_type`
- `tags: [a, b]` — entry must have at least one of these tags
- `projects: [x, y]` — entry must belong to at least one of these projects
- Multiple fields in one rule → AND logic
- Multiple matching rules → union their `destinations` lists
- No rule matches → use `defaults.destinations`

Collect `(entry_filename, [destination_names])` pairs. Proceed to Step 4.

### Step 2 — Scan blog entries

Read all entries in `$BLOG_DIR`:

```bash
ls "$BLOG_DIR"/*.md | grep -v INDEX | sort
```

For each entry, parse the YAML frontmatter to extract:
- `entry_type` — article | note
- `subtype` — diary | ... (notes only)
- `projects` — list of project identifiers
- `tags` — list of topic tags (may be absent or empty)

Parse YAML frontmatter directly with PyYAML (split on `---` delimiters) — no utility script dependency needed.

Skip entries where `entry_type` is missing (warn the user).

### Step 3 — Resolve destinations per entry

For each entry, call:

```python
destinations = router.resolve_destinations(frontmatter)
```

### Step 4 — Show routing plan

Present a table before doing anything:

```
Blog publishing plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Entry                               Destinations
2026-04-14-mdp01-day-zero.md       personal-blog
2026-04-14-mdp02-closing-gaps.md   personal-blog
2026-04-14-quarkus-article.md      quarkus-blog, personal-blog

  Destination paths:
  personal-blog  →  ~/blog/_posts/   (git)
  quarkus-blog   →  ~/quarkus-community-blog/_posts/   (git)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Publish all? (y/n) or enter entry numbers to publish selectively:
```

If user enters numbers (e.g. "1 3"), publish only those entries.
If user says `y`, publish all.
If user says `n`, stop.

### Step 5 — Validate destinations

For each destination referenced in the plan:

```python
dest_config = router.get_destination_config(dest_name)
dest_path = Path(dest_config['path']).expanduser()
subdir = dest_config.get('subdir', '')
target_dir = dest_path / subdir if subdir else dest_path
```

Check the target directory exists:
```bash
ls "<target_dir>" 2>/dev/null || echo "missing"
```

If any target directory is missing, warn before proceeding:
```
⚠️ Destination 'quarkus-blog' → ~/quarkus-community-blog/_posts/ does not exist.
   Create it, or skip this destination? (create / skip / abort)
```

### Step 6 — Copy entries to destinations

For each (entry, destination) pair approved by the user:

```bash
cp "$BLOG_DIR/<filename>" "<target_dir>/<filename>"
```

If the destination is a git repo:
```bash
git -C "<dest_path>" add "<subdir>/<filename>"
```

### Step 7 — Commit destinations with a remote

After copying all entries for a destination, if the destination is a `git` type
and has a remote:

```bash
# Verify remote exists
git -C "<dest_path>" remote get-url origin 2>/dev/null && echo "has-remote"

# Commit
git -C "<dest_path>" commit -m "chore: publish blog entries from cc-praxis"

# Push
git -C "<dest_path>" push
```

If push fails, report with resolution command:
```
❌ Push failed for 'personal-blog'. Run manually:
   git -C ~/blog push
```

### Step 8 — Clean up source entries

Published entries are now versioned in the destination repo — the workspace copy
is redundant. Delete it:

```bash
git -C "$BLOG_DIR/.." rm "$BLOG_DIR/<filename>"
```

If all entries in `$BLOG_DIR` have been published and removed, also remove
`INDEX.md` if present.

Commit the removals in the source workspace repo:

```bash
git -C "$BLOG_DIR/.." commit -m "chore: remove published blog entries"
```

Only remove entries whose destinations all succeeded (✅). If any destination
failed for an entry, keep the source copy until the failure is resolved.

### Step 9 — Summary

```
Publishing complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ personal-blog   — 2 entries published, committed, pushed
✅ quarkus-blog    — 1 entry published, committed (no remote)
❌ project-blog    — push failed (run: git -C ~/project push)

Source cleanup: 2 entries removed from workspace (1 retained — destination failed)
```

---

## blog-routing.yaml Format

### Global (`~/.claude/blog-routing.yaml`)

```yaml
version: 1

destinations:
  personal-blog:
    type: git
    path: ~/blog/
    subdir: _posts/
  quarkus-blog:
    type: git
    path: ~/quarkus-community-blog/
    subdir: _posts/

defaults:
  destinations: [personal-blog]

rules:
  - match:
      tags: [quarkus]
    destinations: [quarkus-blog, personal-blog]
```

### Project override (`<workspace>/blog-routing.yaml`)

```yaml
extends: ~/.claude/blog-routing.yaml

destinations:
  project-blog:
    type: git
    path: ~/cc-praxis-blog/
    subdir: _posts/

rules:
  - match:
      entry_type: article
      projects: [cc-praxis]
    destinations: [personal-blog, project-blog]
```

### Rule semantics

| Field in `match:` | Match logic |
|-------------------|-------------|
| `entry_type: article` | Exact string match |
| `tags: [quarkus]` | Entry must have at least one of these tags |
| `projects: [cc-praxis]` | Entry must belong to at least one of these projects |
| Multiple fields | AND logic — all must match |
| Multiple matching rules | Destinations are unioned |
| No matching rules | Entry goes to `defaults.destinations` |

---

## Edge Cases

| Situation | Behaviour |
|-----------|-----------|
| Entry missing `entry_type` | Skip with warning |
| Entry with no matching rules | Routes to `defaults.destinations` |
| `defaults.destinations` not configured | Entry gets no destinations (warn user) |
| Destination path missing | Prompt: create / skip / abort |
| Git push fails | Continue with remaining destinations, report at end |
| Entry already exists at destination | Overwrite silently (idempotent) |

---

## Success Criteria

- [ ] Global `blog-routing.yaml` loaded; project override merged if present
- [ ] All entries scanned, `entry_type` parsed
- [ ] Routing plan shown and user confirmed before any file operations
- [ ] All destination directories validated before copying
- [ ] Entries copied to each resolved destination
- [ ] Git destinations committed; remote destinations pushed (or failure reported)
- [ ] Successfully published entries removed from source workspace
- [ ] Summary shows per-destination outcome (✅ / ❌)

---

## Skill Chaining

**Invoked by:** User directly — "publish blog", "cross-post entries", `/publish-blog`

**Reads output of:** [`write-content`] — the blog entries in the resolved `$BLOG_DIR`

**No external scripts required** — routing logic is applied inline from the config YAML.

**Related:** workspace `## Routing` config — Level 1 routing (where the `blog/` directory lives).
This skill is Level 2 routing (per-entry cross-posting to platforms). The two are
independent.
