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
| Errors, warnings, quick-fix intentions | `ide_diagnostics` | |
| Check IDE is ready for semantic ops | `ide_index_status` | |
| Sync IDE after external file changes | `ide_sync_files` | |

---

## `mcp__intellij` — JetBrains official (for what intellij-index cannot do)

| Operation | Tool |
|-----------|------|
| Build / compile | `build_project` |
| Run a named test or app configuration | `execute_run_configuration` |
| Hover documentation / type info at position | `get_symbol_info` |
| File-level inspection results | `get_file_problems` |
| Targeted text replacement (no semantic awareness) | `replace_text_in_file` |
| Apply code formatting rules | `reformat_file` |
| Project module structure | `get_project_modules` |
| Library dependencies | `get_project_dependencies` |
| Find files by glob pattern | `find_files_by_glob` |
| Find files by name keyword | `find_files_by_name_keyword` |
| Browse directory tree | `list_directory_tree` |
| Run shell command in IDE terminal | `execute_terminal_command` |
| Open a file in the editor | `open_file_in_editor` |

---

## Lifecycle-managed projects

IntelliJ projects may be in sleep states managed by the MCP lifecycle plugin. The plugin
automatically frees memory when projects are idle. **Never ask the user to open a project —
the plugin handles this transparently.**

### Project states

| State | Memory | What to do |
|-------|--------|------------|
| `active` | full | Use normally |
| `background` | reduced | Use normally — index is live |
| `dormant` | low | Use normally — any tool call wakes it |
| `closed` | none | Provide `project_path` — auto-reopens (5–30s first time) |

### Rules

1. **Always include `project_path`** when you know which project you need. This is what
   triggers auto-open for closed projects. Never omit it and never tell the user to open
   the project themselves.

2. **Check status before a batch of operations** if you are unsure what is open:
   ```
   ide_project_status
   ```
   Response shows which projects are open and their current mode.

3. **If you get `no_project_open`** with a `managed_closed_projects` field in the error,
   retry any tool call with `project_path` set to one of those paths. The plugin will
   reopen it automatically. If all else fails, any tool call without `project_path`
   will auto-open the first managed-closed project to restore MCP access.

4. **`ide_open_project` does not enroll a project in lifecycle management.** Enrollment
   happens on the first real semantic call (find references, diagnostics, refactoring)
   after the project is open. Use `ide_open_project` only when a project has never been
   opened and is not in the lifecycle manager's registry.

5. **If a project is closed and you have its path, just use the path.** Do not call
   `ide_open_project` first — the auto-open via `project_path` is more efficient and
   works for all managed projects including ones closed by the lifecycle timer.

### Example: working on a closed managed project

```
# Wrong — tells user to open it manually
⚠️ eidos not open — please open /Users/dev/casehub/eidos

# Right — just provide project_path, plugin reopens it
ide_find_references { "project_path": "/Users/dev/casehub/eidos", "file": "...", ... }
```

---

## Decision rule

**`intellij-index`** for anything semantic: navigation, references, refactoring, diagnostics.

**`intellij`** for build/run, formatting, file browsing, database tools, and terminal.

**Native tools** (Read, Edit, Grep, Glob) for reading files, searching content, and targeted text edits where semantic awareness is not needed.

---

## Skill Chaining

**Used as prerequisite by:** `java-dev`, `python-dev`, `ts-dev`
