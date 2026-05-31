---
name: cc-praxis
description: >
  Use when cc-praxis management is needed: diagnosing setup problems ("why isn't
  cc-praxis working", "check the setup", "nothing is triggering"), or
  launching the skill manager UI ("open cc-praxis", "manage skills",
  "show installed skills", "what skills are installed").
---

# cc-praxis

Two modes — detect from context:

- **Check** — diagnose setup problems and report what's wrong with recovery steps
- **UI** — launch the local skill manager web app

---

## Mode: Check

Run when the user reports cc-praxis isn't working as expected.

Run all checks in order, collect results, present a single formatted report.

### Check 1 — CLAUDE.md

```bash
[ -f CLAUDE.md ] && echo "found" || echo "missing"
grep "^type:\|^Type:\|^\*\*Type:\*\*" CLAUDE.md 2>/dev/null | head -1
grep -i "GitHub repo:" CLAUDE.md 2>/dev/null | head -1
grep -i "Issue tracking:" CLAUDE.md 2>/dev/null | head -1
```

| State | Report |
|-------|--------|
| Missing | ❌ **CLAUDE.md missing** — Ask Claude: *"Set up a CLAUDE.md for my [language] project"* |
| Exists, no type | ⚠️ **CLAUDE.md has no project type** — Add: `type: java` (or `typescript`, `python`, `generic`) |
| Exists, type found | ✅ **CLAUDE.md present** — `type: <detected>` |

### Check 2 — Installed skills

```bash
ls ~/.claude/skills/ 2>/dev/null | sort
```

Recommended skills per type:

| Project type | Recommended |
|-------------|-------------|
| `java` | `java-dev`, `java-code-review`, `java-git-commit`, `git-commit` |
| `typescript` | `ts-dev`, `ts-code-review`, `git-commit` |
| `python` | `python-dev`, `python-code-review`, `git-commit` |
| any | `adr`, `handover`, `update-claude-md` |

For each recommended skill missing from `~/.claude/skills/`:
> ⚠️ **`skill-name` not installed** — Run `/install-skills` or: `scripts/claude-skill install skill-name`

### Check 3 — Session-start hook

```bash
grep -l "check_project_setup" ~/.claude/settings.json 2>/dev/null && echo "registered" || echo "missing"
[ -f ~/.claude/hooks/check_project_setup.sh ] && echo "script present" || echo "script missing"
```

| State | Report |
|-------|--------|
| Registered + script present | ✅ **Session hook active** |
| Not registered | ❌ **Session hook not registered** — Re-run `/install-skills` |
| Script missing | ❌ **Hook script missing** — Re-run `/install-skills` |

### Check 4 — DESIGN.md (Java only)

```bash
[ -f DESIGN.md ] && echo "found" || echo "missing"
```

| State | Report |
|-------|--------|
| Found | ✅ **DESIGN.md present** |
| Missing | ❌ **DESIGN.md missing** — java-git-commit blocks without it |

Skip for non-Java projects.

### Report format

```
cc-praxis environment check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLAUDE.md        ✅ type: java · GitHub repo: owner/repo
Skills           ✅ java-dev, java-code-review, java-git-commit (+6 more)
Session hook     ✅ active
DESIGN.md        ✅ present
Work Tracking    ✅ issue tracking enabled

All good — cc-praxis is correctly configured.
```

Always show all four checks, even passing ones.

---

## Mode: UI

Run when the user wants to browse or manage skills visually.

### Step 1 — Launch

```bash
cc-praxis --no-browser &
```

If `cc-praxis` not on PATH:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/web_installer.py" --no-browser &
```

### Step 2 — Open browser

```bash
open http://localhost:8765    # macOS
xdg-open http://localhost:8765  # Linux
```

If port in use: `cc-praxis --port 8766 --no-browser &` then open `:8766`.

### Step 3 — Confirm

> Skill manager running at **http://localhost:8765**
>
> Browse skills, manage what's installed, view chaining relationships.
>
> Close with `pkill -f web_installer.py` when done.

---

## Skill Chaining

**Check mode invokes:** [`install-skills`] — if key skills are missing; [`workspace-init`] — if workspace not configured

**UI mode invokes:** Nothing — launches a background process and returns
