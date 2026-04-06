# 0002 — User-level storage architecture

Date: 2026-04-05
Status: Accepted

## Context and Problem Statement

Sparge's project data (config, state, enriched HTML) was originally stored
inside the blog-migrator repo directory. This coupled user data to application
code — moving or updating the codebase risked losing project data, and the
data would appear in git status as untracked files.

## Decision Drivers

* Project data must survive code moves, updates, and re-clones
* Application code (repo) and user data should be cleanly separated
* Location should be configurable for users with non-standard setups
* Pattern should follow established conventions (~/.toolname/)

## Considered Options

* **Option A** — Keep data in `blog-migrator/projects/` (current)
* **Option B** — Store data in `~/.sparge/` (app config and project data together)
* **Option C** — App config at `~/.sparge/config.json`; project data at `~/sparge-projects/` (configurable)

## Decision Outcome

Chosen option: **Option C**, because it cleanly separates the app's own
settings (where to find projects) from the project data itself, and makes
the project data location user-configurable without touching app config.

### Positive Consequences

* Project data survives code updates and re-clones
* `~/sparge-projects/` location is user-configurable via `~/.sparge/config.json`
* Clean separation: `~/.sparge/` is tiny (just a pointer); project data is elsewhere
* No untracked files polluting the git repo

### Negative Consequences / Tradeoffs

* First-run requires migration or fresh setup
* Two locations to know about instead of one

## Pros and Cons of the Options

### Option A — Data in repo dir

* ✅ Simple — everything in one place
* ❌ Data lost or detached on code move/update
* ❌ Untracked files in git repo
* ❌ Not portable

### Option B — All in `~/.sparge/`

* ✅ Single user-level location
* ❌ `~/.sparge/` becomes large (all posts, enriched HTML, state)
* ❌ Config and data mixed — harder to back up separately

### Option C — Config + separate data dir (chosen)

* ✅ Config location fixed (`~/.sparge/`); data location flexible
* ✅ Easy to back up project data independently
* ✅ Follows unix convention for user config vs data separation
* ❌ Two locations to explain to users

## Links

* Design snapshot: `docs/design-snapshots/2026-04-05-sparge-pipeline-and-storage.md`
* Spec: `docs/superpowers/specs/2026-04-05-author-filter-design.md`
