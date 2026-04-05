# cc-praxis — Building the Infrastructure

**Date:** 2026-03-31
**Type:** phase-update

---

Skills are only useful if they're actually installed. After the first nine, I needed a way to distribute them — ideally without requiring anyone to clone a repo and manually copy files around.

## What we were trying to achieve: Skills on any machine in minutes

The goal was a marketplace-style system: add a single registry entry, install individual skills or curated bundles, done. Claude Code has a plugin marketplace mechanism. I wanted cc-praxis to live there.

## What we believed going in: The plugin cache was the right home

Claude Code has a `~/.claude/plugins/cache/` directory managed by the marketplace. We'd put the skills there and everything would work.

We also assumed bundles would be straightforward — groups of skills that belong together. That turned out to be correct, but required more infrastructure than expected.

## Three attempts at installation

**Symlinks.** We wrote a sync script that symlinked skill directories into `~/.claude/plugins/cache/`. Claude Code doesn't follow symlinks in the skills directory. Skills are silently ignored. We discovered this after thinking everything was working.

**Plugin cache directly.** This worked, but the cache has a specific versioned structure (`cache/<marketplace>/<plugin>/<version>/`) and requires registration in `installed_plugins.json`. More complex than it needed to be.

**`~/.claude/skills/` directly.** Claude Code auto-discovers skills in this directory — no registration needed. We wrote a `claude-skill` installer script that copies there. The installer became a real tool: `install`, `install-all`, `sync-local`, `list`, `uninstall`.

## The scaffolding we hadn't planned

**Session-start hook.** When you open Claude Code in a directory without a `CLAUDE.md`, it would be useful to have Claude prompt you to set up the project type. We added a hook script that fires at session start. The `install-skills` wizard installs it. Not something I'd planned — it emerged from thinking about what a first-time user actually experiences.

**Project type taxonomy.** Skills behave differently by project type: `java` projects get `java-git-commit` with DESIGN.md sync, `blog` projects get `blog-git-commit` with content-type conventions. We formalised this as a routing table so `git-commit` reads the project type and delegates correctly. I'd started thinking of cc-praxis as "Java skills." By the time this was done, it was clearly a general-purpose framework. Java is just the most complete implementation.

**Mermaid migration.** Nine skills, each with at least one diagram, all in GraphViz dot format. Claude Code renders Mermaid natively. Not a small job, but necessary.

**The rename.** `claude-skills` was too generic. `cc-praxis` — Claude Code praxis, the practice of Claude Code — felt more distinctive.

## The no-AI attribution rule

One rule I added explicitly and conspicuously: commit messages must never mention AI attribution. No "Co-Authored-By: Claude", no "AI-assisted:". This rule kept getting violated — not maliciously, just because some tooling adds it by default. I put it in the pre-commit checklist, made it prominent in the git-commit skill, flagged it as a critical violation.

It still got violated a few times after that.

## What changed and why: Two pivots and a broader scope

The install mechanism pivoted twice — first away from symlinks, then away from the plugin cache. Landing on `~/.claude/skills/` was right because it's what Claude Code was designed for.

The project type taxonomy changed the scope of the whole project. Routing to specialists based on CLAUDE.md declaration keeps each skill focused. One `git-commit` skill handling all project types directly would have been a mess.

Without the infrastructure — reliable install, session-start hook, taxonomy — cc-praxis would only ever work for me. With it, anyone can add the marketplace entry and have a working installation within minutes.
