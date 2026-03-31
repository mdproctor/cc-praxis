#!/usr/bin/env python3
"""
Document Discovery for Modular Documentation Support

Discovers modular documentation structure via:
- Automatic detection (markdown links, includes, section refs, directory patterns)
- Explicit configuration (CLAUDE.md)
- Hybrid approach (auto-detect first, propose config if ambiguous)

Universal across all project types (skills, java, blog, custom, generic).
"""

import re
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set
import sys

# Import cache module (will be created next)
try:
    from scripts.document_group_cache import get_cached_group, cache_group, compute_cache_key
except ImportError:
    # Fallback for testing
    get_cached_group = lambda x: None
    cache_group = lambda x: None
    compute_cache_key = lambda x: ""


@dataclass(frozen=True)
class ModuleFile:
    """Represents a module file that's part of a document group"""
    path: Path
    relationship: str  # "linked" | "included" | "directory-pattern" | "section-ref"

    def __str__(self):
        return f"{self.path} ({self.relationship})"


@dataclass
class DocumentGroup:
    """Represents a primary document and its optional modules"""
    primary_file: Path
    modules: List[ModuleFile]
    discovered_via: str  # "auto" | "config"
    cache_key: str

    def __str__(self):
        mods = f"{len(self.modules)} modules" if self.modules else "no modules"
        return f"DocumentGroup({self.primary_file}, {mods}, via {self.discovered_via})"

    def all_files(self) -> List[Path]:
        """Return all files in group (primary + modules)"""
        return [self.primary_file] + [m.path for m in self.modules]


def discover_document_group(primary_file: Path) -> DocumentGroup:
    """
    Main discovery entry point. Discovers modular documentation structure.

    Process:
    1. Check cache
    2. Try explicit config from CLAUDE.md
    3. Try automatic detection
    4. If ambiguous, would propose config (for now, use detected)
    5. Cache result
    6. Return DocumentGroup

    Args:
        primary_file: Primary document file (DESIGN.md, CLAUDE.md, README.md, etc.)

    Returns:
        DocumentGroup with primary file and discovered modules
    """
    primary_file = Path(primary_file).resolve()

    if not primary_file.exists():
        # Return single-file group for non-existent files (defensive)
        return DocumentGroup(
            primary_file=primary_file,
            modules=[],
            discovered_via="auto",
            cache_key=""
        )

    # Check cache first
    cached = get_cached_group(primary_file)
    if cached:
        return cached

    # Try explicit config from CLAUDE.md
    explicit_modules = read_explicit_config(primary_file)
    if explicit_modules is not None:
        group = DocumentGroup(
            primary_file=primary_file,
            modules=explicit_modules,
            discovered_via="config",
            cache_key=compute_cache_key(primary_file)
        )
        cache_group(group)
        return group

    # Auto-detect modules
    detected_modules = detect_modules_automatic(primary_file)

    # Check for ambiguity (multiple detection methods with conflicts)
    # For now, we use all detected modules
    # Future: could propose explicit config if ambiguous

    group = DocumentGroup(
        primary_file=primary_file,
        modules=detected_modules,
        discovered_via="auto",
        cache_key=compute_cache_key(primary_file)
    )

    cache_group(group)
    return group


def detect_modules_automatic(primary_file: Path) -> List[ModuleFile]:
    """
    Auto-detect modules via:
    - Markdown links: [text](file.md)
    - Include directives: <!-- include: file.md -->
    - Section references: § Section in file.md
    - Directory patterns: docs/design/*.md if primary is DESIGN.md

    Args:
        primary_file: Primary document to analyze

    Returns:
        List of discovered module files
    """
    if not primary_file.exists():
        return []

    with open(primary_file, 'r', encoding='utf-8') as f:
        content = f.read()

    base_dir = primary_file.parent
    modules: Set[ModuleFile] = set()

    # 1. Parse markdown links
    linked = parse_markdown_links(content, base_dir)
    for path in linked:
        modules.add(ModuleFile(path=path, relationship="linked"))

    # 2. Parse include directives
    included = parse_includes(content, base_dir)
    for path in included:
        modules.add(ModuleFile(path=path, relationship="included"))

    # 3. Parse section references
    section_refs = parse_section_references(content, base_dir)
    for path in section_refs:
        modules.add(ModuleFile(path=path, relationship="section-ref"))

    # 4. Check directory pattern
    pattern_files = check_directory_pattern(primary_file)
    for path in pattern_files:
        # Only add if not already in modules from explicit refs
        if not any(m.path == path for m in modules):
            modules.add(ModuleFile(path=path, relationship="directory-pattern"))

    # Convert set to list, sort by path for consistency
    modules_list = sorted(modules, key=lambda m: str(m.path))

    # Check for circular references
    cycles = detect_circular_references([primary_file] + [m.path for m in modules_list])
    if cycles:
        print(f"⚠️  Warning: Circular references detected: {' → '.join(str(p) for p in cycles)}",
              file=sys.stderr)
        # Remove modules involved in cycles
        modules_list = [m for m in modules_list if m.path not in cycles]

    return modules_list


def parse_markdown_links(content: str, base_dir: Path) -> List[Path]:
    """
    Extract [text](file.md) and [text](file.md#section) references.
    Only includes .md files, filters out external URLs and anchors.

    Args:
        content: Markdown content to parse
        base_dir: Base directory for resolving relative paths

    Returns:
        List of linked markdown file paths that exist
    """
    # Match [text](path) and [text](path#anchor)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)

    paths = []
    for text, link in matches:
        # Skip external URLs
        if link.startswith(('http://', 'https://', 'ftp://')):
            continue

        # Skip pure anchors (#section)
        if link.startswith('#'):
            continue

        # Remove anchor if present (file.md#section → file.md)
        link = link.split('#')[0]

        # Only include .md files
        if not link.endswith('.md'):
            continue

        # Resolve relative to base_dir
        path = (base_dir / link).resolve()

        # Only include if file exists
        if path.exists() and path.is_file():
            paths.append(path)

    return paths


def parse_includes(content: str, base_dir: Path) -> List[Path]:
    """
    Extract <!-- include: file.md --> directives.

    Args:
        content: Markdown content to parse
        base_dir: Base directory for resolving relative paths

    Returns:
        List of included file paths that exist
    """
    # Match <!-- include: path -->
    pattern = r'<!--\s*include:\s*([^\s]+)\s*-->'
    matches = re.findall(pattern, content, re.IGNORECASE)

    paths = []
    for link in matches:
        # Resolve relative to base_dir
        path = (base_dir / link).resolve()

        # Only include if file exists
        if path.exists() and path.is_file():
            paths.append(path)

    return paths


def parse_section_references(content: str, base_dir: Path) -> List[Path]:
    """
    Extract § Section in file.md references.

    Args:
        content: Markdown content to parse
        base_dir: Base directory for resolving relative paths

    Returns:
        List of referenced file paths that exist
    """
    # Match "§ Section in file.md" or "§ Section (file.md)"
    pattern = r'§\s+[^(]+\s+(?:in|\()\s*([^\s)]+\.md)'
    matches = re.findall(pattern, content)

    paths = []
    for link in matches:
        # Resolve relative to base_dir
        path = (base_dir / link).resolve()

        # Only include if file exists
        if path.exists() and path.is_file():
            paths.append(path)

    return paths


def check_directory_pattern(primary_file: Path) -> List[Path]:
    """
    Check directory pattern based on primary file name.

    If DESIGN.md → check docs/design/*.md
    If CLAUDE.md → check docs/workflows/*.md
    If README.md → check docs/readme/*.md

    Args:
        primary_file: Primary document file

    Returns:
        List of files matching directory pattern
    """
    name = primary_file.stem.lower()  # DESIGN.md → design
    base_dir = primary_file.parent

    # Map primary file names to directory patterns
    patterns = {
        'design': 'docs/design',
        'claude': 'docs/workflows',
        'readme': 'docs/readme',
        'vision': 'docs/vision',
        'thesis': 'docs/thesis',
        'architecture': 'docs/architecture',
    }

    if name not in patterns:
        return []

    pattern_dir = base_dir / patterns[name]

    if not pattern_dir.exists() or not pattern_dir.is_dir():
        return []

    # Find all .md files in directory (excluding primary file itself)
    md_files = []
    for path in pattern_dir.glob('*.md'):
        if path.is_file() and path.resolve() != primary_file.resolve():
            md_files.append(path.resolve())

    return md_files


def detect_circular_references(files: List[Path]) -> Optional[List[Path]]:
    """
    Find circular references (A→B→A cycles).

    Args:
        files: List of files to check for circular refs

    Returns:
        List of files in cycle if found, None otherwise
    """
    # Build graph of references
    graph = {}
    for file_path in files:
        if not file_path.exists():
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all referenced .md files from this file
        referenced = (
            parse_markdown_links(content, file_path.parent) +
            parse_includes(content, file_path.parent) +
            parse_section_references(content, file_path.parent)
        )

        graph[file_path] = set(referenced)

    # Detect cycles using DFS
    def has_cycle_dfs(node, visited, rec_stack, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    cycle = has_cycle_dfs(neighbor, visited, rec_stack, path)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:]

        path.pop()
        rec_stack.remove(node)
        return None

    visited = set()
    for node in graph:
        if node not in visited:
            cycle = has_cycle_dfs(node, visited, set(), [])
            if cycle:
                return cycle

    return None


def read_explicit_config(primary_file: Path) -> Optional[List[ModuleFile]]:
    """
    Read explicit module configuration from CLAUDE.md.

    Format:
    ## Modular Documentation

    ### DESIGN.md
    **Modules:**
    - docs/design/architecture.md
    - docs/design/components.md

    Args:
        primary_file: Primary document to find config for

    Returns:
        List of modules from config, or None if no config found
    """
    claude_md = primary_file.parent / "CLAUDE.md"

    if not claude_md.exists():
        return None

    with open(claude_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find "## Modular Documentation" section
    modular_section_match = re.search(
        r'##\s+Modular\s+Documentation\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not modular_section_match:
        return None

    modular_section = modular_section_match.group(1)

    # Find subsection for this primary file
    primary_name = primary_file.name
    subsection_pattern = rf'###\s+{re.escape(primary_name)}\s*\n\*\*Modules:\*\*\s*\n((?:- .+\n?)+)'

    subsection_match = re.search(subsection_pattern, modular_section, re.MULTILINE)

    if not subsection_match:
        return None

    modules_text = subsection_match.group(1)

    # Parse module list (lines starting with "- ")
    module_paths = []
    for line in modules_text.strip().split('\n'):
        line = line.strip()
        if line.startswith('- '):
            path_str = line[2:].strip()
            path = (primary_file.parent / path_str).resolve()

            # Only include if file exists
            if path.exists() and path.is_file():
                module_paths.append(ModuleFile(path=path, relationship="config"))

    return module_paths if module_paths else None


def propose_explicit_config(primary_file: Path, detected: List[ModuleFile]) -> str:
    """
    Generate CLAUDE.md config suggestion when auto-detection is ambiguous.

    Args:
        primary_file: Primary document
        detected: Auto-detected modules

    Returns:
        Markdown snippet for CLAUDE.md configuration
    """
    primary_name = primary_file.name
    base_dir = primary_file.parent

    # Generate relative paths from repository root
    config = f"""## Modular Documentation

### {primary_name}
**Modules:**
"""

    for module in detected:
        try:
            rel_path = module.path.relative_to(base_dir)
            config += f"- {rel_path}\n"
        except ValueError:
            # If path is not relative to base_dir, use absolute
            config += f"- {module.path}\n"

    return config.strip()
