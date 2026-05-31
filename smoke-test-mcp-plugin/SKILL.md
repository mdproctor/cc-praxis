---
name: smoke-test-mcp-plugin
description: >
  Use when the jetbrains-index-mcp-plugin needs to be built, installed, and verified —
  after any code change, before raising a PR, or when something feels wrong after a
  restart. Handles both the install path and the smoke test.
slash-command: false
---

## Step 1 — Build

```bash
cd /Users/mdproctor/claude/jetbrains-index-mcp-plugin
./gradlew buildPlugin --no-build-cache
```

Confirm `BUILD SUCCESSFUL` and note the zip path: `build/distributions/*.zip`.

## Step 2 — Install

Two paths depending on whether the plugin is already running:

**Path A — plugin is running** (use `ide_install_plugin`):
```
ide_install_plugin   # auto-detects build/distributions/*.zip
```
Then call `ide_restart`. Wait 30s, reconnect with `/mcp`.

**Path B — bootstrap / plugin not running** (manual install):

```bash
# Remove old extracted directory if present
rm -rf "/Users/mdproctor/Library/Application Support/JetBrains/IntelliJIdea2026.1/plugins/jetbrains-index-mcp-plugin"
```

```python
python3 -c "
import zipfile, glob, os
plugins_dir = os.path.expanduser('~/Library/Application Support/JetBrains/IntelliJIdea2026.1/plugins')
zips = sorted(glob.glob('build/distributions/*.zip'), key=os.path.getmtime)
if not zips: raise SystemExit('No zip found — run ./gradlew buildPlugin first')
zipfile.ZipFile(zips[-1]).extractall(plugins_dir)
print('Extracted', os.path.basename(zips[-1]))
"
```

**Critical:** copying the zip is NOT enough — IntelliJ requires an extracted directory.
After extraction, restart IntelliJ manually, then reconnect with `/mcp`.

## Step 3 — Verify plugin loaded

```bash
grep "Registered.*built-in MCP tools" ~/Library/Logs/JetBrains/IntelliJIdea*/idea.log | tail -3
```

If no match: plugin did not load. Check `idea.log` for `ERROR` or `WARN` near startup.

## Step 4 — Smoke test

Read `smoke-tests/mcp-protocol.md` from the plugin project, then execute every test
case in order. Report PASS/FAIL per test. If any test fails, diagnose before continuing.

## Setup

Locate the plugin project path. The protocol file is at:
```
<plugin-project>/smoke-tests/mcp-protocol.md
```

Read it fully before starting. The meta-protocol section explains:
- How to call the MCP server via HTTP directly (not via Claude's MCP schema)
- How to confirm IntelliJ actually restarted (restarter.log check)
- How to detect "old code still running" vs a new bug
- Fallback when `ide_restart` doesn't fire

## Execution

Work through every test case in order. For each test:

1. Make the HTTP call as described
2. Check the response against the PASS/FAIL criteria in the protocol
3. Report the result: **PASS** or **FAIL — [reason]**
4. On FAIL: follow the diagnostic hints in the protocol before moving on

Run fork-only tests (section "Fork-only tests") when working in the fork.
Skip them when verifying an upstream build.

## After all tests

Write a summary table: tool | result | notes.

Flag any FAIL that indicates a regression (test was passing before this build).
Flag any FAIL that indicates a new protocol gap (the protocol didn't anticipate this failure mode).

## Common pitfalls

| Pitfall | What happens | Fix |
|---------|-------------|-----|
| Copying the zip without extracting | Plugin directory missing, nothing loads | Use the Python extract command — copy alone is never enough |
| Using Claude's MCP schema | Stale tool list from session start, missing new tools | Call via curl directly |
| Not checking `idea.log` for "Registered N built-in" | Assume plugin loaded when it didn't | Always verify Step 3 before testing |
| Not checking restarter.log | `ide_restart` appears to work but old code still runs | Always verify log entry |
| Testing before indexing completes | `ide_index_status` returns `isDumbMode: true`, tool calls fail | Wait for `isDumbMode: false` |
| Wrong project_path | Multi-project error fires before tool validation | Pass the plugin project path on every call |
