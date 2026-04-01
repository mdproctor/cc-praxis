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
elif ! grep -q "## Work Tracking" CLAUDE.md; then
  echo "ℹ️  OPTIONAL: No issue tracking configured for this project."
  echo "Run /issue-workflow to set up GitHub issue tracking and release-based changelog."
  echo "(Enables cross-cutting task detection and commit split suggestions)"
fi
