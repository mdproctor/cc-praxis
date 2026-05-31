---
name: ide-tooling
description: >
  INVOKE IMMEDIATELY when two IntelliJ MCPs are visible: mcp__intellij-index__*
  and mcp__intellij__*. These are NOT interchangeable — mcp__intellij-index__
  supports auto-opening projects via project_path; mcp__intellij__ cannot.
  Always use mcp__intellij-index__ for code navigation. Never try mcp__intellij__
  first and fall back. Also invoke for any IDE operation: rename, move file,
  find references, navigate to definition, type hierarchy, diagnostics.
slash-command: false
---

# IDE Tooling — IntelliJ MCP Guide

## ⚠️ Critical: Two MCPs, one right choice

**Use `mcp__intellij-index__*` for everything code-related. Never use `mcp__intellij__*` to navigate or open projects.**

| Need | Use |
|------|-----|
| Find references, navigate, search, diagnostics, rename, move | `mcp__intellij-index__*` |
| Check if project is open | `mcp__intellij-index__ide_project_status` |
| Project not open → open it | Pass `project_path` to any `mcp__intellij-index__` tool — auto-opens |
| Build, run tests, terminal, formatting | `mcp__intellij__*` only |

**Never ask the user to open a project. Never fall back to bash because a project isn't open. Never launch IntelliJ from the command line.** Pass `project_path` and let the plugin handle it.

---

Always prefer IntelliJ MCPs over bash, grep, or text tools for semantic code
operations. IntelliJ understands the code structure; text tools do not.

Check `ide_index_status` before batch operations — indexing may still be in
progress. If neither MCP server is available for a semantic operation, stop
and inform the user rather than silently falling back to text tools.

---

## `mcp__intellij-index` — Semantic index (always prefer for code intelligence)

Multi-project aware: supports `project_path` to target any open or managed project.

| Operation | Tool | Notes |
|-----------|------|-------|
| Find all usages of a symbol | `ide_find_references` | **Run before any rename or delete** — understand full impact first |
| Navigate to symbol declaration | `ide_find_definition` | |
| All implementations of an interface/abstract | `ide_find_implementations` | |
| What does this method override | `ide_find_super_methods` | |
| Full class/interface inheritance tree | `ide_type_hierarchy` | |
| Who calls this / what this calls | `ide_call_hierarchy` | |
| Find a class by name | `ide_find_class` | Faster than grep for known names |
| Find a file by name | `ide_find_file` | |
| **Safe rename** — updates all references | `ide_refactor_rename` | Never use Edit/sed for renames |
| **Safe move** — updates package/imports | `ide_move_file` | Never use bash mv for source files |
| Safe delete — checks usages first | `ide_refactor_safe_delete` | Lists usages if deletion would break things |
| Fast identifier/word search | `ide_search_text` | Faster than grep for exact names |
| Errors, warnings, quick-fix intentions | `ide_diagnostics` | Supersedes `get_file_problems` |
| All open/managed projects + their states | `ide_project_status` | **Use this, not `get_project_modules`** |
| Check IDE is ready for semantic ops | `ide_index_status` | |
| Sync IDE after external file changes | `ide_sync_files` | |

---

## `mcp__intellij` — JetBrains built-in (window-scoped — only sees already-open projects)

**Cannot auto-open projects.** If a project isn't open in the IDE, `mcp__intellij__*` tools
will fail or return wrong results. Never use these tools to check whether a project is open
or to trigger opening one — use `mcp__intellij-index__ide_project_status` instead, which
auto-opens via `project_path`.

Use `mcp__intellij__*` only for operations `intellij-index` cannot do. Tools marked ⚠️ have an
`intellij-index` equivalent that is multi-project aware — prefer those.

| Operation | Tool | Note |
|-----------|------|------|
| Build / compile | `build_project` | |
| Run a named test or app configuration | `execute_run_configuration` | |
| Hover documentation / type info at position | `get_symbol_info` | |
| File-level inspection results | `get_file_problems` | ⚠️ Use `ide_diagnostics` instead |
| Targeted text replacement (no semantic awareness) | `replace_text_in_file` | |
| Apply code formatting rules | `reformat_file` | |
| Project module structure | `get_project_modules` | ⚠️ Use `ide_project_status` instead — multi-project aware |
| Library dependencies | `get_project_dependencies` | |
| Find files by glob pattern | `find_files_by_glob` | |
| Find files by name keyword | `find_files_by_name_keyword` | ⚠️ Use `ide_find_file` instead |
| Browse directory tree | `list_directory_tree` | |
| Run shell command in IDE terminal | `execute_terminal_command` | |
| Open a file in the editor | `open_file_in_editor` | |

---

## Lifecycle-managed projects

Projects may be sleeping to free memory. **Never ask the user to open a project.**

1. **Always include `project_path` and proceed silently** — it auto-opens any project
   that has a `.idea` directory, whether managed, in limbo, or never enrolled. Do not
   warn the user that a project is closed. Do not ask the user to open it. Just pass
   `project_path` to whichever semantic tool you need (`ide_find_references`,
   `ide_search_text`, etc.) — the plugin opens the project first, then runs the tool.
2. **Use `ide_project_status` to see all open projects** — not `get_project_modules`,
   which only sees the currently focused window. If `ide_project_status` is unavailable,
   skip this step and go straight to rule 1 with the path you need.
3. **If you get `no_project_open`** — retry any tool call with a `project_path` from the
   error's `managed_closed_projects` list.

```
# Wrong — warned the user instead of proceeding
⚠️ IntelliJ — casehub-connectors is not open. Currently open: engine, life, aml...

# Right — pass project_path silently, plugin opens it automatically
ide_find_references { "project_path": "/Users/dev/casehub/connectors", ... }
```

---

## Decision rule

**`intellij-index`** for anything semantic: navigation, references, refactoring, diagnostics.

**`intellij`** for build/run, formatting, file browsing, database tools, and terminal.

**Native tools** (Read, Edit, Grep, Glob) for reading files, searching content, and targeted text edits where semantic awareness is not needed.

---

## Skill Chaining

**Used as prerequisite by:** `java-dev`, `python-dev`, `ts-dev`
