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

# Check for HANDOVER.md and prompt to read it (runs when CLAUDE.md exists)
if [ -f "CLAUDE.md" ] && [ -f "HANDOVER.md" ]; then
  LAST_UPDATED=$(git log -1 --format="%ar" -- HANDOVER.md 2>/dev/null || echo "unknown age")
  echo "📋 HANDOVER.md found (last updated: $LAST_UPDATED)."
  echo "Before starting: ask the user 'Read your session handover? (y/n)' — if yes, read and briefly summarise HANDOVER.md."
  # Check staleness
  COMMIT_TIME=$(git log -1 --format="%ct" -- HANDOVER.md 2>/dev/null)
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
