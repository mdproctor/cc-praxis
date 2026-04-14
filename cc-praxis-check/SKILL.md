---
name: cc-praxis-check
description: >
  Use when something seems wrong with cc-praxis — user says "why isn't
  cc-praxis working", "check the setup", "diagnose cc-praxis", "nothing is
  triggering", or invokes /cc-praxis-check. NOT for day-to-day development
  — only for troubleshooting setup and configuration issues.
---

# cc-praxis Environment Check

Diagnoses common setup problems and reports the current cc-praxis configuration
with specific recovery steps for anything missing or misconfigured.

---

## Workflow

Run each check in order, collect results, then present a single formatted report.

### Check 1 — CLAUDE.md

```bash
# Does CLAUDE.md exist?
[ -f CLAUDE.md ] && echo "found" || echo "missing"

# What project type is declared?
grep "^type:\|^Type:\|^\*\*Type:\*\*" CLAUDE.md 2>/dev/null | head -1

# Is GitHub repo configured?
grep -i "GitHub repo:" CLAUDE.md 2>/dev/null | head -1

# Is Work Tracking enabled?
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

From the detected project type, identify the recommended skills:

| Project type | Recommended skills |
|-------------|-------------------|
| `java` | `java-dev`, `java-code-review`, `java-git-commit`, `git-commit` |
| `typescript` / `generic` (TS) | `ts-dev`, `ts-code-review`, `git-commit` |
| `python` / `generic` (Python) | `python-dev`, `python-code-review`, `git-commit` |
| any | `adr`, `handover`, `update-claude-md` |

For each recommended skill that is **not** in `~/.claude/skills/`:

> ⚠️ **`skill-name` not installed** — Run `/install-skills` and select it, or:
> `scripts/claude-skill install skill-name`

For installed skills, list them concisely:

> ✅ **Skills installed:** java-dev, java-code-review, java-git-commit (+N more)

### Check 3 — Session-start hook

```bash
# Check if hook is registered
grep -l "check_project_setup" ~/.claude/settings.json 2>/dev/null && echo "registered" || echo "missing"

# Check hook script exists
[ -f ~/.claude/hooks/check_project_setup.sh ] && echo "script present" || echo "script missing"
```

| State | Report |
|-------|--------|
| Registered + script present | ✅ **Session hook active** — CLAUDE.md detection runs at session start |
| Not registered | ❌ **Session hook not registered** — Re-run `/install-skills` to register it |
| Registered but script missing | ❌ **Hook script missing** — Re-run `/install-skills` to restore it |

### Check 4 — DESIGN.md (Java only)

Only run if project type is `java`:

```bash
[ -f DESIGN.md ] && echo "found" || echo "missing"
```

| State | Report |
|-------|--------|
| Found | ✅ **DESIGN.md present** — java-git-commit can sync it |
| Missing | ❌ **DESIGN.md missing** — java-git-commit blocks without it. Ask Claude: *"Create a DESIGN.md for my project"* |

Skip this check (mark N/A) for non-Java projects.

---

## Report Format

Present all results together after running all checks:

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

Or with issues:

```
cc-praxis environment check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLAUDE.md        ❌ not found
Skills           ⚠️  java-code-review not installed
Session hook     ✅ active
DESIGN.md        ❌ not found (required for java-git-commit)
Work Tracking    ⚠️  not configured

Recovery steps:
1. CLAUDE.md: "Set up a CLAUDE.md for my Quarkus REST API"
2. java-code-review: scripts/claude-skill install java-code-review
3. DESIGN.md: "Create a DESIGN.md for my project"
```

Always show all four checks, even if they pass. Users need to see the full picture.

---

## Success Criteria

- [ ] All four checks run in order
- [ ] Report shows ✅ / ❌ / ⚠️ for every check
- [ ] Failed checks include specific recovery steps (exact commands or prompts)
- [ ] Report is shown in a single block, not streamed line by line
- [ ] Runs in under 10 seconds

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Only checking CLAUDE.md | Users often have CLAUDE.md but missing DESIGN.md or hook | Run all four checks every time |
| Vague recovery step: "install the skill" | User doesn't know how | Give the exact command: `scripts/claude-skill install java-code-review` |
| Skipping DESIGN.md check for Java | java-git-commit blocks silently without it | Always check if type is java |
| Reporting checks one by one | Creates confusing output stream | Collect all results, present as a single report |

---

## Skill Chaining

**Invoked by:** User directly when cc-praxis isn't working as expected — `/cc-praxis-check`

**Chains to:** [`install-skills`] — if key skills are missing; [`workspace-init`] — if workspace not configured
