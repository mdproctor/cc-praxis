---
id: PP-20260609-df21ed
title: "Externalised skill scripts must ship with pytest tests in the same commit"
type: rule
scope: repo
applies_to: "Any .py script added to a skill directory (project-init/, workspace-init/, work-start/, work-end/, etc.) as part of bash externalisation"
severity: important
violation_hint: "Script file exists without a corresponding tests/test_<script_name>.py, or test file lacks coverage of happy path, edge cases, and bad inputs"
created: 2026-06-09
---

When a bash block in a SKILL.md is replaced with a callable Python script, the script and its test file must be committed together — never separately. Tests must cover at minimum: the happy path, at least two edge cases (empty input, missing file), and bad argument handling. Using `tmp_path` pytest fixtures is required; no hardcoded paths in tests. A script without tests does not merge.
