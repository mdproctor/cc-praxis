---
name: ide-tooling
description: >
  Use when any IDE operation is needed — renaming a symbol, moving a file,
  finding all references, navigating to a definition, exploring a type hierarchy,
  diagnosing dependency chains, or any other operation where IntelliJ provides
  semantic correctness that bash/grep cannot. Also use when the user asks
  which tool to use for a code navigation or refactoring task.
---

# IDE Tooling — IntelliJ MCP Guide

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

## `mcp__intellij` — JetBrains official (window-scoped — only sees the focused project)

Use only for operations `intellij-index` cannot do. Tools marked ⚠️ have an
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

1. **Always include `project_path`** — it auto-opens closed projects (5–30s). Never tell
   the user to open a project manually.
2. **Use `ide_project_status` to see all open projects** — not `get_project_modules`,
   which only sees the currently focused window and will mislead you when multiple
   projects are managed.
3. **If you get `no_project_open`** — retry any tool call with a `project_path` from the
   error's `managed_closed_projects` list.

```
# Wrong — Claude asked user instead of using project_path
⚠️ eidos not open — please open /Users/dev/casehub/eidos

# Right — project_path triggers auto-open
ide_find_references { "project_path": "/Users/dev/casehub/eidos", ... }
```

---

## Decision rule

**`intellij-index`** for anything semantic: navigation, references, refactoring, diagnostics.

**`intellij`** for build/run, formatting, file browsing, database tools, and terminal.

**Native tools** (Read, Edit, Grep, Glob) for reading files, searching content, and targeted text edits where semantic awareness is not needed.

---

## Skill Chaining

**Used as prerequisite by:** `java-dev`, `python-dev`, `ts-dev`
