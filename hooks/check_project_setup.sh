#!/bin/bash
# Session-start hook. Output is read by Claude as directives to act on.

# Only run inside a git repository
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  exit 0
fi

# Project setup — delegate all checks to project-init
echo "🔧 Invoke the project-init skill to verify this project is set up before proceeding."


# Handover — session context, handled here not in project-init
if [ -f "CLAUDE.md" ] && [ -f "HANDOVER.md" ]; then
  LAST_UPDATED=$(git log -1 --format="%ar" -- HANDOVER.md 2>/dev/null || echo "unknown age")
  echo "📋 HANDOVER.md found (last updated: $LAST_UPDATED)."
  echo "Before starting: ask the user 'Read your session handover? (y/n)' — if yes, read and briefly summarise HANDOVER.md."
  COMMIT_TIME=$(git log -1 --format="%ct" -- HANDOVER.md 2>/dev/null)
  if [ -n "$COMMIT_TIME" ]; then
    NOW=$(date +%s)
    DAYS=$(( (NOW - COMMIT_TIME) / 86400 ))
    if [ "$DAYS" -gt 7 ]; then
      echo "⚠️ Handover is $DAYS days old — flag as potentially stale before summarising."
    fi
  fi
fi
