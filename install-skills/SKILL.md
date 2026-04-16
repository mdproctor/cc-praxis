---
name: install-skills
description: >
  Use when setting up Claude Code skills in a new environment, or when invoked
  via /install-skills. One-time bootstrap — configures hooks and installs
  selected skills with automatic dependency resolution.
---

# Install Skills - Marketplace Bootstrap

**One-time setup skill.** Run this after adding the marketplace to configure your environment and install skills.

## What This Does

1. **Configure session-start hook** - Automatic CLAUDE.md detection when opening repositories
2. **Install marketplace skills** - Interactive selection with automatic dependency resolution
3. **Verify setup** - Confirm everything is working

## Workflow

### Step 1: Check Hook Configuration

Check if session-start hook is already configured:

```bash
Read ~/.claude/settings.json
```

If `hooks.session-start` exists and points to a CLAUDE.md checker:
> ✅ Session-start hook already configured

If not configured, offer to set it up:

> **Configure session-start hook?**
>
> This will automatically check for CLAUDE.md when you open a repository,
> prompting you to set up project type if missing.
>
> Would you like to set this up? (Y/n)

Wait for user response.

**If YES:**

1. Create hook script at `~/.claude/hooks/check_project_setup.sh`:

```bash
#!/bin/bash
# Check CLAUDE.md exists and declares a project type in current repository.
# Output is read by Claude at session start — messages are directives to act on.

# Only run inside a git repository
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  exit 0
fi

if [ ! -f "CLAUDE.md" ]; then
  echo "⚠️  ACTION REQUIRED: No CLAUDE.md found in this repository."
  echo "Prompt the user to choose a project type and create CLAUDE.md for them."
  echo "Choices: skills | java | blog | custom | generic"
  echo "(See docs/PROJECT-TYPES.md for what each type means)"
elif ! grep -q "## Project Type" CLAUDE.md; then
  echo "⚠️  ACTION REQUIRED: CLAUDE.md exists but declares no Project Type."
  echo "Prompt the user to choose a project type and insert it into CLAUDE.md."
  echo "Choices: skills | java | blog | custom | generic"
  echo "(See CLAUDE.md § Project Type for what each type means)"
fi

# Check for HANDOFF.md and prompt to read it (runs when CLAUDE.md exists)
if [ -f "CLAUDE.md" ] && [ -f "HANDOFF.md" ]; then
  LAST_UPDATED=$(git log -1 --format="%ar" -- HANDOFF.md 2>/dev/null || echo "unknown age")
  echo "📋 HANDOFF.md found (last updated: $LAST_UPDATED)."
  echo "Before starting: ask the user 'Read your session handover? (y/n)' — if yes, read and briefly summarise HANDOFF.md."
  # Check staleness
  COMMIT_TIME=$(git log -1 --format="%ct" -- HANDOFF.md 2>/dev/null)
  if [ -n "$COMMIT_TIME" ]; then
    NOW=$(date +%s)
    DAYS=$(( (NOW - COMMIT_TIME) / 86400 ))
    if [ "$DAYS" -gt 7 ]; then
      echo "⚠️ Handover is $DAYS days old — flag as potentially stale before summarising."
    fi
  fi
fi

# Check for workspace CLAUDE.md session-start instruction
if [ -f "CLAUDE.md" ]; then
  if grep -q "## Session Start" CLAUDE.md 2>/dev/null; then
    : # Workspace configured — session-start add-dir will handle project access
  elif grep -q "## Project Type" CLAUDE.md 2>/dev/null; then
    echo "ℹ️  No workspace configured for this project."
    echo "Run /workspace-init to create ~/claude/private/<project>/ and set up the companion workspace."
    echo "(Keeps methodology artifacts out of the project repo)"
  fi
fi

# Check for Work Tracking configuration
if [ -f "CLAUDE.md" ] && grep -q "## Project Type" CLAUDE.md && ! grep -q "## Work Tracking" CLAUDE.md; then
  echo "ℹ️  OPTIONAL: No issue tracking configured for this project."
  echo "Run /issue-workflow to set up GitHub issue tracking and release-based changelog."
  echo "(Enables cross-cutting task detection and commit split suggestions)"
fi
```

2. Make it executable:
```bash
chmod +x ~/.claude/hooks/check_project_setup.sh
```

3. Use `/update-config` skill to add hook to settings.json:
```json
{
  "hooks": {
    "session-start": "~/.claude/hooks/check_project_setup.sh"
  }
}
```

4. Confirm:
> ✅ Session-start hook configured
> ✅ ~/.claude/hooks/check_project_setup.sh created
>
> From now on, opening a repository without CLAUDE.md will show a setup reminder.

**If NO:**
> Skipping hook setup. You can run /install-skills again later to set it up.

Continue to Step 2.

### Step 2: Skill Selection

Fetch marketplace catalog:

```bash
curl -fsSL https://raw.githubusercontent.com/mdproctor/cc-praxis/main/.claude-plugin/marketplace.json
```

From the fetched JSON, derive options dynamically:

```python
all_skills = [p["name"] for p in marketplace["plugins"]]
total = len(all_skills)
bundles = marketplace.get("bundles", [])
```

Present options — counts and bundle contents come from the fetched data, never hardcoded:

```
📦 Claude Code Skills Marketplace

What would you like to install?

1. Install ALL skills ({total} total)
   - Complete collection

{for i, bundle in enumerate(bundles, 2):}
{i}. Install {bundle["displayName"]} ({len(bundle["skills"])} skills)
   - {bundle["description"]}

{len(bundles)+2}. Pick individual skills
   - Custom selection

{len(bundles)+3}. Skip installation (just hook setup)

Enter choice:
```

Wait for user input.

### Step 3: Dependency Resolution

Based on user selection, resolve dependencies using this algorithm:

**Dependency Resolution (DFS with Cycle Detection):**

```python
def resolve_dependencies(skill_name, marketplace, resolved, visiting):
    if skill_name in resolved:
        return
    if skill_name in visiting:
        print(f"❌ Circular dependency detected: {skill_name}")
        return
    skill = find_skill_in_marketplace(marketplace, skill_name)
    if not skill:
        print(f"⚠️  Skill '{skill_name}' not found in marketplace")
        return
    visiting.add(skill_name)
    plugin_json_url = f"https://raw.githubusercontent.com/{extract_repo(skill['source'])}/main/{skill['path']}/.claude-plugin/plugin.json"
    try:
        plugin_metadata = fetch_json(plugin_json_url)
        for dep in plugin_metadata.get("dependencies", []):
            dep_name = dep["name"] if isinstance(dep, dict) else dep
            resolve_dependencies(dep_name, marketplace, resolved, visiting)
    except:
        pass
    visiting.remove(skill_name)
    resolved.append(skill_name)
```

**Selecting skills to install** — read from fetched marketplace, never hardcode:

```python
if choice == "all":
    skills_to_install = all_skills                    # all plugins from marketplace
elif 1 <= bundle_index < len(bundles):
    skills_to_install = bundles[bundle_index]["skills"]  # from marketplace bundles
elif choice == "individual":
    skills_to_install = user_selected_skills          # user picks from all_skills list
else:
    return  # skip

resolved = []
for skill in skills_to_install:
    resolve_dependencies(skill, marketplace, resolved, set())
```

### Step 4: Show Installation Plan

Display resolved skills in dependency order:

```
📋 Installation Plan

The following skills will be installed (in dependency order):

  1. code-review-principles
  2. security-audit-principles
  3. git-commit
  4. java-dev
  5. java-code-review
  6. java-security-audit
  7. java-git-commit
  8. maven-dependency-update
  9. quarkus-flow-dev
 10. quarkus-flow-testing
 11. quarkus-observability

Total: 11 skills

Dependencies will be installed automatically.

Proceed with installation? (Y/n):
```

Wait for user confirmation.

**If NO:**
> Installation cancelled. You can run /install-skills again anytime.

**If YES:** Continue to Step 5.

### Step 5: Install Skills

For each skill in resolved order, run:

```bash
/plugin install <skill-name>
```

Show progress:

```
Installing skills...

  ✅ code-review-principles
  ✅ security-audit-principles
  ✅ git-commit
  ✅ java-dev
  ✅ java-code-review
  ✅ java-security-audit
  ✅ java-git-commit
  ✅ maven-dependency-update
  ✅ quarkus-flow-dev
  ✅ quarkus-flow-testing
  ✅ quarkus-observability
```

### Step 6: Completion Message

After all skills installed successfully:

```
<!-- EPHEMERAL TASK: install-skills -->
<!-- RETENTION: Not required after user acknowledgment -->

═══════════════════════════════════════════════════════════
🎉 Claude Code Skills - Installation Complete!
═══════════════════════════════════════════════════════════

✅ Session-start hook configured
   Location: ~/.claude/hooks/check_project_setup.sh
   Effect: Prompts for CLAUDE.md setup when opening new repositories

✅ Skills installed: 11
   Location: ~/.claude/skills/
   Status: Available in ALL conversations (current and future)

✅ Dependencies resolved
   All required dependencies installed automatically

═══════════════════════════════════════════════════════════

**What happens next:**

Your environment is fully configured. The installed skills are now
available in ALL Claude Code conversations, not just this one.

**Recommended:** Close this conversation now.

The installation details above can be safely discarded. Skills will
remain available when you start your next conversation.

**To verify installation works:**
1. Close this conversation
2. Open a new conversation
3. Try: /java-dev or /git-commit

═══════════════════════════════════════════════════════════

<!-- This installation log can be safely compressed/forgotten -->
<!-- EPHEMERAL TASK END -->
```

## Error Handling

**Hook script creation fails:**
```
⚠️  Failed to create hook script
Error: [error message]

You can manually create ~/.claude/hooks/check_project_setup.sh later.
Continuing with skill installation...
```

**Skills installation fails:**
```
❌ Failed to install: <skill-name>
Error: [error message]

Installed so far: X skills
Failed: Y skills

You can retry individual skills with:
  /plugin install <skill-name>
```

**Marketplace fetch fails:**
```
❌ Failed to fetch marketplace catalog
Error: [error message]

Check your internet connection and try again:
  /install-skills
```

## Success Criteria

Installation is complete when:

- ✅ Session-start hook created (if user confirmed)
- ✅ Hook added to settings.json (if user confirmed)
- ✅ All selected skills installed successfully
- ✅ All dependencies resolved and installed
- ✅ User shown completion message with next steps

**Not complete until** all criteria met and user shown final message with "close conversation" recommendation.

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Installing without resolving dependencies | Skills fail due to missing deps | Always run dependency resolution first |
| Not checking if hook exists | Overwrites existing setup | Check settings.json before modifying |
| Silent failures | User doesn't know what failed | Show clear error messages with retry instructions |
| Keeping conversation open | Wastes 200+ tokens rest of session | Recommend closing after completion |

## Notes

- This is a **one-time setup skill** - run once per environment
- Hook script is bash (works on macOS/Linux, may need adaptation for Windows)
- Skills are installed via official `/plugin install` command
- All installation output is ephemeral (safe to forget after reading)
- Skill body is ~250 lines but only loaded when explicitly invoked
