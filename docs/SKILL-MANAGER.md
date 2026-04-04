# cc-praxis Skill Manager — User Guide

The skill manager is a web interface for browsing, installing, and managing cc-praxis skills. It gives you a visual overview of all 43 skills, shows what's installed on your machine, and lets you install or remove skills with one click.

---

## Opening the Skill Manager

The skill manager has two modes depending on how you open it.

### Option A — Ask Claude to launch it

In any Claude Code session:

> "Open cc-praxis" or "launch the skill manager"

Claude will start the local server and open your browser automatically. You'll see all three tabs: **About**, **Browse**, and **Install**.

### Option B — Run it yourself

```bash
python3 scripts/web_installer.py
```

Or, if you installed the plugin and `cc-praxis` is on your PATH:

```bash
cc-praxis
```

This opens `http://localhost:8765` in your browser.

### Viewing on GitHub Pages (Browse only)

If you visit the skill manager on GitHub Pages rather than running it locally, the **Install** tab is hidden. You can browse all the skills and explore the chain graph, but installing requires running the local server — only the local server can read your `~/.claude/skills/` directory and run install commands on your machine.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  cc-praxis / Skills         [ About ]  [ Browse ]                       │
│                                                         (no Install tab) │
│  ℹ️  To manage skills, run: python3 scripts/web_installer.py             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Three Tabs

```
┌─────────────────────────────────────────────────────────────────────────┐
│  cc-praxis / Skills    [ About ]  [ Browse ]  [ Install ]               │
│                          ──────                           ↻ Refresh     │
│                                               ⚡ Auto-execute  📋 Show  │
└─────────────────────────────────────────────────────────────────────────┘
```

| Tab | Purpose |
|-----|---------|
| **About** | Overview of the collection — what it does, how skills work, which languages are supported |
| **Browse** | Explore all 43 skills with descriptions and the skill chain graph |
| **Install** | See what's installed on your machine and manage your installation |

---

## Browse — Exploring Skills

The Browse tab shows all skills grouped into bundles. Click a bundle header to expand it.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ▶ ● Core                                               5 of 5          │
│  ▼ ● Java / Quarkus                                     5 of 10         │
│  ──────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  java-dev        v1.0.0   [ Dev ]    ✓ Installed                        │
│  Foundation for all Java/Quarkus development — strict type safety,       │
│  Quarkus-specific patterns, no-string-literals rule for class refs.      │
│  Chains to: java-code-review  quarkus-observability                     │
│  Extended by: java-code-review  java-security-audit  quarkus-flow-dev   │
│                                                                          │
│  java-code-review  v1.0.0  [ Review ]  ✓ Installed                      │
│  Code review checklist for Java/Quarkus — resource leaks, event loop    │
│  safety, test coverage. Triggers java-security-audit for auth code.     │
│  Chains to: java-security-audit  java-git-commit                        │
│  Invoked by: java-dev  java-git-commit  quarkus-flow-dev                │
│                                                                          │
│  java-security-audit  v1.0.0  [ Security ]  Not installed      Install  │
└─────────────────────────────────────────────────────────────────────────┘
```

Each skill card shows:

- **Name and version** — the skill identifier and release version
- **Role pill** — colour-coded badge indicating the skill's function
- **Install status** — ✓ Installed (green), Not installed (gray)
- **Description** — what the skill does and when it activates
- **Chaining relationships** — which skills this one invokes and which invoke it

### Role Pills

The coloured badge tells you what category a skill belongs to:

```
[ Dev ]       Blue    — Development workflow
[ Review ]    Amber   — Code review
[ Security ]  Red     — Security audit
[ Commit ]    Purple  — Git commit workflow
[ Sync ]      Slate   — Document synchronisation
[ Deps ]      Orange  — Dependency management
[ Health ]    Green   — Project health checks
[ Setup ]     Gray    — Installation wizards
[ ADR ]       Slate   — Architecture documentation
[ Foundation ] Purple — Universal base skills (not invoked directly)
```

---

## Understanding Skill Relationships

Skills in cc-praxis aren't independent — they form a connected system. There are three kinds of relationships between skills:

### Chains To

When a skill finishes its job, it can hand off to another skill automatically. For example:

```
  java-code-review ──chains to──▶ java-security-audit
                                   (offered for auth/PII code)

  java-code-review ──chains to──▶ java-git-commit
                                   (offered after review passes)
```

"Chains to" means: this skill will offer to invoke that one when the right conditions arise. You're always in control — chains are offers, not forced sequences.

### Invoked By

The reverse of "chains to." If skill A chains to skill B, then skill B lists skill A in its "invoked by." This gives you the full picture from either direction.

```
  git-commit  ──invokes──▶  update-claude-md
  
  update-claude-md  ──invoked by──▶  git-commit
                                      java-git-commit
                                      blog-git-commit
                                      custom-git-commit
```

### Builds On / Extended By

Some skills are built on top of foundation skills. The foundation provides universal rules; the specialist adds language-specific detail.

```
  code-review-principles  ◀──extended by──  java-code-review
                          ◀──extended by──  ts-code-review
                          ◀──extended by──  python-code-review

  java-code-review  ──builds on──▶  code-review-principles
                    ──builds on──▶  java-dev
```

`code-review-principles` itself is never invoked directly — it's a foundation that specialists load as a prerequisite. When you install `java-code-review`, you should also install `code-review-principles` to get the full ruleset.

> **Important:** When you install a skill that builds on a foundation, the skill manager will automatically include the foundation in the install operation. You don't need to install them separately.

---

## The Chain Graph

Every skill card in Browse has a **Chain** button. Clicking it opens an inline panel showing that skill's position in the full dependency graph.

```
  java-git-commit  v1.0.0  [ Commit ]  ✓ Installed         [⬤→⬤ Chain]
  Smart Java commits with automatic DESIGN.md synchronisation.
  ...
```

Click **Chain**:

```
┌─ Chain: java-git-commit ──────────────────────────────────────────────── × ┐
│                                                                              │
│   ⊙  →  git-commit  →  java-git-commit  →  ▼                               │
│                                             ├─ java-code-review             │
│                                             ├─ java-update-design           │
│                                             └─ update-claude-md             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

Reading the chain left to right:

| Element | Meaning |
|---------|---------|
| `⊙` | Root of the chain — this skill has no parent |
| `→ git-commit →` | Parent skill in the execution chain |
| **`java-git-commit`** | The skill you clicked (shown in bold) |
| `▼ ├─ ...` | Children — skills this one chains to |

### Navigating the Graph

Any skill name in the chain panel is **clickable**. Clicking it scrolls to that skill's card and opens its own chain view. This lets you walk the full graph interactively:

```
  Click "git-commit" in the panel above...

┌─ Chain: git-commit ──────────────────────────────────────────────────── × ┐
│                                                                              │
│  git-commit  →  ▼                                                           │
│                 ├─ blog-git-commit                                           │
│                 ├─ java-git-commit  ▶ (has children — click ▶ to expand)   │
│                 ├─ issue-workflow                                            │
│                 ├─ ts-code-review                                            │
│                 └─ update-claude-md                                          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

The `▶` toggle expands grandchildren inline:

```
│  git-commit  →  ▼
│                 ├─ java-git-commit  ▼
│                 │    ├─ java-code-review
│                 │    ├─ java-update-design
│                 │    └─ update-claude-md
│                 └─ update-claude-md
```

Click **×** to close the chain panel, or click another skill's Chain button to switch views.

---

## Install — Managing Your Installation

The Install tab is only available when the skill manager is running locally (via `python3 scripts/web_installer.py` or the `cc-praxis` command). It shows your real install state, refreshed from `~/.claude/skills/` on every page load.

### The Sync Bar

At the top of the Install tab:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  All Skills                        [Update]  ⚠️ 2 outdated              │
│  12 of 43 installed                          [Install]  [Uninstall]     │
└─────────────────────────────────────────────────────────────────────────┘
```

- **12 of 43 installed** — how many skills are currently in `~/.claude/skills/`
- **⚠️ 2 outdated** — skills where your installed version is behind the latest release
- **Update** — updates all installed skills to their latest versions (see [Update](#update-moving-everything-to-one-version))
- **Install** — installs all skills not yet installed (all 43)
- **Uninstall** — removes all installed skills

### Bundle States

Skills are grouped into bundles. Each bundle header shows its install state at a glance:

```
  ●  ▶ Core                                    5 of 5       [Uninstall]
  ◐  ▼ Java / Quarkus                          3 of 10      [Install] [Uninstall]
  ○    Principles                              0 of 4       [Install]
  ●    TypeScript                              5 of 5       [Uninstall]
  ○    Python                                  0 of 5       [Install]
```

| Indicator | Meaning |
|-----------|---------|
| `●` Green dot | All skills in this bundle are installed |
| `◐` Blue dot | Some skills installed — partial bundle |
| `○` Gray dot | No skills installed |

The bundle count ("3 of 10") shows exactly how many are installed. Partial bundles show both **Install** (for the missing skills) and **Uninstall** (for the installed ones).

### Individual Skill Rows

Expand a bundle to see each skill individually:

```
  ▼ ◐ Java / Quarkus                           3 of 10    [Install] [Uninstall]
  ─────────────────────────────────────────────────────────────────────────────
  ●  java-dev            v1.0.0   [ Dev ]      Foundation for all Java...    [Uninstall]
  ●  java-code-review    v1.0.0   [ Review ]   Code review with CRITICAL...  [Uninstall]
  ○  java-security-audit v1.0.0   [ Security ] OWASP Top 10 for Java...      [Install]
  ●  java-git-commit     v1.0.0   [ Commit ]   Smart commits with DESIGN...  [Uninstall]
  ○  java-update-design  v1.0.0   [ Sync ]     DESIGN.md synchronisation...  [Install]
  ○  maven-dependency-update v1.0.0 [ Deps ]   Maven BOM management...       [Install]
```

Each row shows:
- `●` or `○` dot — installed or not
- Skill name and version
- Role pill
- Short description
- **Install** or **Uninstall** button depending on current state

Outdated skills are highlighted in amber:

```
  ▲  java-dev     v1.0.0 → v1.0.1  [ Dev ]    Foundation for all...  [Uninstall]
```

---

## Installing Skills

### Installing a Bundle

Click **Install** on a bundle header to install all missing skills in that bundle at once. If some are already installed, the button and modal will show only the ones that still need installing:

```
┌───────────────────────────────────────────────┐
│  Install Java / Quarkus Bundle                │
│  7 skills will be added to ~/.claude/skills/  │
│                                               │
│  python3 scripts/claude-skill install         │
│  java-security-audit java-update-design       │
│  maven-dependency-update quarkus-flow-dev ... │
│  [Copy]                                       │
│                                               │
│  ℹ️  Dependency included automatically:        │
│  code-review-principles will also be          │
│  installed — required for java-code-review.   │
│                                               │
│  ⚡ This command will run automatically.       │
│                                               │
│            [Cancel]    [Install 7 skills]     │
└───────────────────────────────────────────────┘
```

Notice the **dependency notice**: `code-review-principles` is a foundation skill that `java-code-review` builds on. The skill manager detects this automatically and includes it in the install — you don't need to add it manually.

> **Built-on parents are always installed with their children.** If you install `ts-code-review`, you'll also get `code-review-principles`. If you install `java-project-health`, you'll also get `project-health`.

### Installing an Individual Skill

Click **Install** on any individual skill row for a single-skill install:

```
┌────────────────────────────────────────────┐
│  Install java-security-audit               │
│  java-security-audit will be added to      │
│  ~/.claude/skills/                         │
│                                            │
│  python3 scripts/claude-skill install      │
│  security-audit-principles java-security-  │
│  audit                                     │
│  [Copy]                                    │
│                                            │
│  ℹ️  security-audit-principles will also    │
│     be installed (required dependency).    │
│                                            │
│  ⚡ This command will run automatically.   │
│                                            │
│        [Cancel]           [Install]        │
└────────────────────────────────────────────┘
```

---

## Update — Moving Everything to One Version

The **Update** button in the sync bar is different from **Install**. Here's what each does:

| Action | What it does |
|--------|-------------|
| **Install** | Adds skills that aren't yet installed |
| **Update** | Brings all *installed* skills to their latest version |
| **Update All** (sync bar Update) | Updates everything to the same version as a set |

Skills in cc-praxis are designed to work together as a consistent set. The `java-code-review` skill references conventions from `java-dev`; `git-commit` routes to specialists that share the same commit format. Running different versions of related skills can cause subtle inconsistencies.

When you click **Update**, you see:

```
┌───────────────────────────────────────────────────────────┐
│  Update All Skills                                        │
│  2 installed skills have updates available                │
│                                                           │
│  A new version is available. Skills work together as a    │
│  set — updating them all at once ensures compatibility.   │
│                                                           │
│  ts-dev     v1.0.0 → v1.1.0                              │
│  java-dev   v1.0.0 → v1.0.1                              │
│                                                           │
│  View release notes →                                     │
│                                                           │
│  python3 scripts/claude-skill sync-local --all            │
│  [Copy]                                                   │
│                                                           │
│  ⚡ This command will run automatically when you confirm. │
│                                                           │
│             [Cancel]                [Update All]          │
└───────────────────────────────────────────────────────────┘
```

> **Mixed version warning:** If you've manually updated some skills but not others, you may see a warning: *"Mixed versions detected — some skills are already ahead of others. We strongly recommend updating all skills together."* Click Update All to resolve this.

---

## Auto Execute vs Show Command

The mode toggle in the header controls what happens when you click Install, Uninstall, or Update:

```
  ⚡ Auto-execute  |  📋 Show command
  ───────────────────────────────────
```

### ⚡ Auto Execute (default)

The skill manager runs the command for you. When you click **Install 5 skills**, it calls the API, the command runs in the background, and you see a success notification:

```
  ✓ Skills installed — open a new Claude Code session to use them.
                                                              [×]
```

The install state updates automatically — you'll see the dots turn green and the count update.

### 📋 Show Command

The modal shows the command but doesn't run it. Copy it and run it yourself in a terminal:

```
┌────────────────────────────────────────────┐
│  Install Python Bundle                      │
│  5 Python skills will be added to           │
│  ~/.claude/skills/                          │
│                                             │
│  python3 scripts/claude-skill install       │
│  python-dev python-code-review python-      │
│  security-audit pip-dependency-update       │
│  python-project-health                      │
│  [Copy]                                     │
│                                             │
│  📋 Copy and run this command in your       │
│     terminal, then click Done to refresh.   │
│                                             │
│        [Cancel]          [Done — Refresh]   │
└────────────────────────────────────────────┘
```

After running the command in your terminal, click **Done — Refresh** to reload the install state. The dots will update to reflect what's now installed.

> Use **Show Command** if you want to review what will run before it happens, or if you're on a system where running commands via the browser feels uncomfortable.

---

## Refreshing the Install State

The install state is loaded when the page opens and after every Auto Execute action. If you install or remove skills in your terminal directly (not through the UI), the UI won't know until you refresh.

Click **↻ Refresh** in the header to reload from `~/.claude/skills/`:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  cc-praxis / Skills  [ About ]  [ Browse ]  [ Install ]  ↻ Refresh     │
└─────────────────────────────────────────────────────────────────────────┘
```

Or use the **Done — Refresh** button after running a Show Command manually.

---

## Finding Skills

The search bar in the navigation filters skills across both Browse and Install views:

```
  All  ·  Core  ·  Principles  ·  Java/Quarkus  ·  TypeScript  ·  Python  ·  Extras
  ──────────────────────────────────────────────────────────────────── [Search skills…] [⊟ Collapse All]
```

Type any part of a skill name or description. Results filter instantly:

```
  Search: "security"

  ▼ ◐ Java / Quarkus
      java-security-audit  OWASP Top 10 for Java/Quarkus...   [Install]

  ▼ ● TypeScript
      ts-security-audit    OWASP Top 10 for TypeScript...      [Uninstall]

  ▼ ○ Python
      python-security-audit  OWASP Top 10 for Python...        [Install]
```

Use **⊟ Collapse All** / **⊞ Expand All** to control bundle visibility when you're scrolling through many results.

---

## Recommended Installation Order

If you're starting fresh, here's the recommended approach:

**1. Install Core first** — these skills work in every project:

```
  Core Bundle: git-commit, update-claude-md, adr, project-health, project-refine
```

**2. Install Principles** — foundation skills that language-specific bundles build on:

```
  Principles Bundle: code-review-principles, security-audit-principles,
                     dependency-management-principles, observability-principles
```

**3. Add your language bundle:**

```
  Java/Quarkus  →  TypeScript  →  Python  (install the one(s) you use)
```

**4. Add individual extras** as needed: `issue-workflow`, `design-snapshot`, `idea-log`, `project-blog`, `knowledge-garden`.

The nudge box at the top of the Install tab reminds you of this:

```
  ┌─────────────────────────────────────────────────────────────────── × ┐
  │  💡 New here? Start simple. Install Core first, then add your         │
  │  language bundle (TypeScript or Java/Quarkus). Open a new Claude     │
  │  Code session and say "commit" to see it in action.                  │
  └───────────────────────────────────────────────────────────────────────┘
```

---

## After Installing

After installing or uninstalling, **open a new Claude Code session** for the changes to take effect. Skills are loaded at session start — existing sessions won't pick up the new skills until they're restarted.

```
  ✓ Skills installed — open a new Claude Code session to use them.  [×]
```

This banner stays visible until you dismiss it, so you won't miss it even if you're looking at something else when the install completes.

---

## Quick Reference

| What you want | Where to find it |
|--------------|-----------------|
| What a skill does | Browse tab — skill card description |
| How skills connect | Browse tab — Chain button on any skill card |
| What's installed on your machine | Install tab — dots and counts |
| Install a bundle | Install tab — Install button on bundle header |
| Install one skill | Install tab — Install button on skill row |
| Update outdated skills | Install tab — Update button in sync bar |
| Remove skills | Install tab — Uninstall button on bundle or row |
| Run command yourself | Switch to Show Command mode in header |
| Refresh after manual terminal install | ↻ Refresh button in header |
| Find a specific skill | Search bar in navigation |
| Open the skill manager | `python3 scripts/web_installer.py` or ask Claude |
