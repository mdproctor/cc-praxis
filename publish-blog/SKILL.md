---
name: publish-blog
description: >
  Use when publishing blog entries to external platforms via blog-routing.yaml
  — user says "publish blog", "publish entries", "cross-post this entry", or
  invokes /publish-blog. NOT for writing new entries (use write-blog for that).
---

# Publish Blog

Routes blog entries from the project's `docs/_posts/` directory to external
publishing destinations based on `blog-routing.yaml` routing rules.

This is a **second-level routing** step, independent of the workspace `## Routing`
config used by `epic`. That config controls where the `blog/` directory lives.
This skill controls where individual entries are cross-posted to blog platforms.

---

## Prerequisites

- `blog-routing.yaml` exists at `~/.claude/blog-routing.yaml` (global) and optionally
  at `<workspace>/blog-routing.yaml` (project override)
- Blog entries have `entry_type`, `projects`, and optionally `tags` in frontmatter
- Each destination path in the routing config is a valid directory

---

## Workflow

### Step 1 — Load routing config

Check for configs:

```bash
ls ~/.claude/blog-routing.yaml 2>/dev/null && echo "global found"
ls blog-routing.yaml 2>/dev/null && echo "project found"
```

If global config is missing, stop and tell the user:
> "No global routing config found at `~/.claude/blog-routing.yaml`.
> Create it first — see the routing config format in the Blog Entry Types Design spec."

Use `scripts/blog_router.py` to load and merge the configs:

```python
from scripts.blog_router import BlogRouter, load_routing_config, merge_configs
from pathlib import Path

global_config = load_routing_config(Path.home() / '.claude/blog-routing.yaml')
project_config = None
if Path('blog-routing.yaml').exists():
    project_config = load_routing_config(Path('blog-routing.yaml'))

merged = merge_configs(global_config, project_config)
router = BlogRouter(merged)
```

### Step 2 — Scan blog entries

Read all entries in `docs/_posts/`:

```bash
ls docs/_posts/*.md | sort
```

For each entry, parse the YAML frontmatter to extract:
- `entry_type` — article | note
- `subtype` — diary | ... (notes only)
- `projects` — list of project identifiers
- `tags` — list of topic tags (may be absent or empty)

Use `scripts/utils/yaml_utils.py` → `extract_frontmatter()` for parsing.

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
cp "docs/_posts/<filename>" "<target_dir>/<filename>"
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

### Step 8 — Summary

```
Publishing complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ personal-blog   — 2 entries published, committed, pushed
✅ quarkus-blog    — 1 entry published, committed (no remote)
❌ project-blog    — push failed (run: git -C ~/project push)
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
- [ ] Summary shows per-destination outcome (✅ / ❌)

---

## Skill Chaining

**Invoked by:** User directly — "publish blog", "cross-post entries", `/publish-blog`

**Reads output of:** [`write-blog`] — the blog entries in `docs/_posts/`

**Uses:** `scripts/blog_router.py` — routing config loader and resolver

**Related:** `epic` — Level 1 routing (where the `blog/` directory lives).
This skill is Level 2 routing (per-entry cross-posting to platforms). The two are
independent; `epic` does not invoke `publish-blog`.
