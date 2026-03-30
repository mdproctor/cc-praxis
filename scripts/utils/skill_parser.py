"""Skill file parsing utilities."""

import re
from pathlib import Path
from typing import List, Dict, Set, Optional


def extract_skill_references(content: str) -> Set[str]:
    """
    Extract all skill names referenced in backticks.

    Returns set of skill names like: {'java-dev', 'git-commit', 'update-design'}
    """
    # Find all backtick-quoted skill names (hyphenated names)
    pattern = r'`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`'
    matches = re.findall(pattern, content)

    # Filter out things that are clearly not skill names
    skill_names = set()
    for match in matches:
        # Skill names typically have 2-4 parts
        parts = match.split('-')
        if 2 <= len(parts) <= 4:
            # Avoid file paths, command flags, etc.
            if not any(part in ['md', 'json', 'yml', 'yaml', 'sh', 'py'] for part in parts):
                skill_names.add(match)

    return skill_names


def extract_sections(content: str) -> Dict[str, str]:
    """
    Extract sections from markdown content.

    Returns dict of section_name -> section_content
    """
    sections = {}
    current_section = None
    current_content = []

    for line in content.split('\n'):
        # Check for section headers (## Header)
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()

            # Start new section
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def has_section(content: str, section_name: str) -> bool:
    """Check if content has a specific section."""
    pattern = f'^## {re.escape(section_name)}$'
    return bool(re.search(pattern, content, re.MULTILINE))


def extract_flowcharts(content: str) -> List[str]:
    """
    Extract all flowcharts (```dot ... ``` blocks) from content.

    Returns list of flowchart source code strings.
    """
    flowcharts = []
    in_flowchart = False
    current_flowchart = []

    for line in content.split('\n'):
        if line.strip() == '```dot':
            in_flowchart = True
            current_flowchart = []
        elif line.strip() == '```' and in_flowchart:
            flowcharts.append('\n'.join(current_flowchart))
            in_flowchart = False
        elif in_flowchart:
            current_flowchart.append(line)

    return flowcharts


def extract_chaining_info(sections: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Extract skill chaining information.

    Returns dict with keys:
        - 'chains_to': skills this skill invokes
        - 'invoked_by': skills that invoke this skill
        - 'prerequisites': foundation skills this builds on
    """
    chaining = {
        'chains_to': [],
        'invoked_by': [],
        'prerequisites': []
    }

    # Check Skill Chaining section
    if 'Skill Chaining' in sections:
        content = sections['Skill Chaining']

        # Find "Chains to X" or "Invokes X"
        for line in content.split('\n'):
            if 'chains to' in line.lower() or 'invokes' in line.lower():
                # Extract skill names in backticks
                matches = re.findall(r'`([a-z][a-z0-9-]+)`', line)
                chaining['chains_to'].extend(matches)

            if 'invoked by' in line.lower() or 'triggered by' in line.lower():
                matches = re.findall(r'`([a-z][a-z0-9-]+)`', line)
                chaining['invoked_by'].extend(matches)

    # Check Prerequisites section
    if 'Prerequisites' in sections:
        content = sections['Prerequisites']
        matches = re.findall(r'`([a-z][a-z0-9-]+)`', content)
        chaining['prerequisites'].extend(matches)

    # Deduplicate
    for key in chaining:
        chaining[key] = list(set(chaining[key]))

    return chaining


def count_words(content: str) -> int:
    """Count words in content (excluding code blocks and frontmatter)."""
    # Remove frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

    # Count words
    words = re.findall(r'\b\w+\b', content)
    return len(words)
