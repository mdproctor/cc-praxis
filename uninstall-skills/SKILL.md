---
name: uninstall-skills
description: >
  Use when removing installed skills from the environment. Invoked via
  /uninstall-skills. Guides removal of individual skills, bundles, or all
  skills, with reverse-dependency checking and optional hook removal.
---

# Uninstall Skills - Marketplace Cleanup

**One-time cleanup skill.** Run this to remove installed skills and optionally remove the session-start hook.

## What This Does

1. **Remove marketplace skills** - Interactive selection with reverse dependency checking
2. **Remove session-start hook** - Optional cleanup of CLAUDE.md detection hook
3. **Verify cleanup** - Confirm skills are removed

## Workflow

### Step 1: Skill Selection

Show uninstall options:

```
🗑️  Claude Code Skills Marketplace - Uninstall

What would you like to uninstall?

1. Uninstall ALL skills (20 total)
   - Complete removal of all marketplace skills

2. Uninstall Java/Quarkus bundle (11 skills)
   - Backend development skills only

3. Uninstall generic foundation (4 skills)
   - Universal principles only

4. Pick individual skills
   - Custom selection

5. Remove session-start hook only
   - Keep skills, remove automatic CLAUDE.md check

6. Cancel
   - Don't uninstall anything

Enter choice (1-6):
```

Wait for user input.

### Step 2: Reverse Dependency Check

For each skill being uninstalled, check if other installed skills depend on it.

**Algorithm:**

```python
def check_reverse_dependencies(skill_to_remove, all_installed_skills, marketplace):
    """
    Check if any installed skills depend on the skill being removed.
    
    Args:
        skill_to_remove: Skill to uninstall
        all_installed_skills: List of currently installed skills
        marketplace: Marketplace catalog
    
    Returns:
        List of skills that depend on skill_to_remove
    """
    dependents = []
    
    for installed_skill in all_installed_skills:
        if installed_skill == skill_to_remove:
            continue
            
        # Fetch plugin.json for installed skill
        plugin_metadata = fetch_plugin_json(installed_skill)
        
        # Check if it depends on skill_to_remove
        for dep in plugin_metadata.get("dependencies", []):
            dep_name = dep["name"] if isinstance(dep, dict) else dep
            if dep_name == skill_to_remove:
                dependents.append(installed_skill)
                break
    
    return dependents
```

**For each bundle:**

**Bundle 1 (All skills):**
All 20 skills will be removed. No dependency check needed (removing everything).

**Bundle 2 (Java/Quarkus):**
```python
java_quarkus = [
    "java-dev", "java-code-review", "java-security-audit", "java-git-commit",
    "java-update-design", "maven-dependency-update", "quarkus-flow-dev",
    "quarkus-flow-testing", "quarkus-observability", "update-claude-md", "adr"
]

# Check each skill for dependents OUTSIDE this bundle
for skill in java_quarkus:
    dependents = check_reverse_dependencies(skill, all_installed, marketplace)
    # Filter to only dependents NOT in java_quarkus bundle
    external_dependents = [d for d in dependents if d not in java_quarkus]
    if external_dependents:
        warn_about_dependents(skill, external_dependents)
```

**Bundle 3 (Generic foundation):**
```python
foundation = [
    "code-review-principles", "security-audit-principles",
    "dependency-management-principles", "observability-principles"
]

# These are often dependencies of other skills
for skill in foundation:
    dependents = check_reverse_dependencies(skill, all_installed, marketplace)
    if dependents:
        warn_about_dependents(skill, dependents)
```

**Bundle 4 (Individual):**
Check dependencies for each selected skill individually.

### Step 3: Show Removal Plan with Warnings

Display skills to be removed with dependency warnings:

```
📋 Removal Plan

⚠️  Warning: The following skills have dependencies

java-dev is required by:
  • java-code-review
  • java-security-audit
  • java-git-commit
  • maven-dependency-update
  • quarkus-flow-dev
  • quarkus-flow-testing

code-review-principles is required by:
  • java-code-review

Skills to remove:
  1. java-dev
  2. java-code-review
  3. java-security-audit
  4. java-git-commit
  5. java-update-design
  6. maven-dependency-update
  7. quarkus-flow-dev
  8. quarkus-flow-testing
  9. quarkus-observability
 10. update-claude-md
 11. adr

Total: 11 skills

⚠️  Some skills depend on others being removed. This may cause issues.

Options:
1. Proceed anyway (may break dependent skills)
2. Add dependent skills to removal list
3. Cancel

Choose (1-3):
```

**If user chooses 2 (Add dependents):**
Recursively add all reverse dependencies to removal list:

```python
def add_all_dependents(skills_to_remove, all_installed, marketplace):
    """
    Recursively add all dependent skills to removal list.
    """
    added = True
    while added:
        added = False
        for skill in list(skills_to_remove):
            dependents = check_reverse_dependencies(skill, all_installed, marketplace)
            for dep in dependents:
                if dep not in skills_to_remove:
                    skills_to_remove.append(dep)
                    added = True
    return skills_to_remove
```

Show updated plan with all dependents included.

**If user chooses 3 (Cancel):**
```
Uninstallation cancelled. No skills removed.
```
Exit skill.

**If user chooses 1 (Proceed anyway):**
Continue to Step 4.

### Step 4: Confirm Removal

Final confirmation before removal:

```
⚠️  FINAL CONFIRMATION

You are about to uninstall 11 skills:

This action will:
- Remove skills from ~/.claude/plugins/cache/mdproctor-skills/
- Skills will no longer be available in Claude Code
- This cannot be undone (you can reinstall later)

Are you absolutely sure? Type 'YES' to confirm:
```

Wait for exact text "YES" (case-sensitive).

**If not "YES":**
```
Uninstallation cancelled.
```

**If "YES":**
Continue to Step 5.

### Step 5: Uninstall Skills

For each skill in removal list, run:

```bash
/plugin uninstall <skill-name>
```

Show progress:

```
Uninstalling skills...

  ✅ java-dev
  ✅ java-code-review
  ✅ java-security-audit
  ✅ java-git-commit
  ✅ java-update-design
  ✅ maven-dependency-update
  ✅ quarkus-flow-dev
  ✅ quarkus-flow-testing
  ✅ quarkus-observability
  ✅ update-claude-md
  ✅ adr
```

### Step 6: Hook Removal (Optional)

After skills uninstalled, ask about hook:

```
Remove session-start hook?

This will remove:
- ~/.claude/hooks/check_project_setup.sh
- Hook configuration from settings.json

The hook checks for CLAUDE.md when opening repositories.

Remove hook? (Y/n):
```

**If YES:**

1. Check if hook exists:
```bash
ls ~/.claude/hooks/check_project_setup.sh
```

2. Remove hook script:
```bash
rm ~/.claude/hooks/check_project_setup.sh
```

3. Use `/update-config` skill to remove hook from settings.json:
```json
{
  "hooks": {
    "session-start": null  // Remove the hook
  }
}
```

Or remove the entire hooks section if it only contained session-start.

4. Confirm:
```
✅ Session-start hook removed
✅ ~/.claude/hooks/check_project_setup.sh deleted
```

**If NO:**
```
Hook kept. CLAUDE.md checks will continue on repository open.
```

### Step 7: Completion Message

After all skills uninstalled:

```
<!-- EPHEMERAL TASK: uninstall-skills -->
<!-- RETENTION: Not required after user acknowledgment -->

═══════════════════════════════════════════════════════════
🗑️  Claude Code Skills - Uninstall Complete
═══════════════════════════════════════════════════════════

✅ Skills removed: 11
   Location: ~/.claude/plugins/cache/mdproctor-skills/
   Status: No longer available in Claude Code

✅ Session-start hook removed (if selected)
   CLAUDE.md checks disabled

═══════════════════════════════════════════════════════════

**What happens next:**

The uninstalled skills are no longer available in any Claude Code
conversations.

**To reinstall:**
  /install-skills

**Recommended:** Close this conversation now.

The uninstallation details above can be safely discarded.

═══════════════════════════════════════════════════════════

<!-- This uninstallation log can be safely compressed/forgotten -->
<!-- EPHEMERAL TASK END -->
```

## Error Handling

**Skill uninstall fails:**
```
❌ Failed to uninstall: <skill-name>
Error: [error message]

Uninstalled so far: X skills
Failed: Y skills

Continuing with remaining skills...
```

**Hook removal fails:**
```
⚠️  Failed to remove hook
Error: [error message]

You can manually remove:
  ~/.claude/hooks/check_project_setup.sh
  
And edit ~/.claude/settings.json to remove hooks.session-start
```

**Skill not installed:**
```
⚠️  <skill-name> not installed, skipping
```

## Success Criteria

Uninstallation is complete when:

- ✅ All selected skills uninstalled successfully
- ✅ Reverse dependencies checked and handled
- ✅ Hook removed (if user confirmed)
- ✅ User shown completion message

**Not complete until** all criteria met and user shown final message.

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Not checking reverse dependencies | Leaves broken skills installed | Always check what depends on skills being removed |
| Silent uninstall | User doesn't know what was removed | Show clear progress and confirmation |
| No confirmation | Accidental removal | Require explicit "YES" for destructive action |
| Keeping conversation open | Wastes tokens | Recommend closing after completion |

## Notes

- This is a **cleanup skill** - run when removing marketplace skills
- Checks reverse dependencies to avoid breaking installed skills
- Requires explicit "YES" confirmation for safety
- Uses official `/plugin uninstall` command
- All output is ephemeral (safe to forget after reading)
- Skill body only loaded when explicitly invoked
