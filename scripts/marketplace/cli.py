"""
CLI commands for skill marketplace.

Orchestrates installation workflow:
1. Fetch registry
2. Resolve dependencies
3. Show installation plan
4. Confirm with user
5. Install skills in dependency order
6. Validate each installation
"""

import sys
from pathlib import Path

from scripts.marketplace.registry import fetch_registry, find_skill
from scripts.marketplace.dependency_resolver import build_dependency_graph, detect_conflicts
from scripts.marketplace.installer import install_skill
from scripts.marketplace.validator import validate_skill


def install_command(
    skill_name: str,
    marketplace_dir: Path,
    snapshot: bool = False
) -> int:
    """
    Install skill and dependencies.

    Args:
        skill_name: Name of skill to install
        marketplace_dir: Path to .marketplace directory
        snapshot: If True, use snapshotRef instead of defaultRef

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        print(f"Fetching registry...")
        registry = fetch_registry()
        print("✓ Registry loaded\n")

        print(f"Resolving dependencies for {skill_name}...")
        skill_entry = find_skill(registry, skill_name)

        ref = skill_entry["snapshotRef"] if snapshot else skill_entry["defaultRef"]
        repository = skill_entry["repository"]
        path = skill_entry["path"]

        graph = build_dependency_graph(
            skill_name=path,
            registry=registry,
            repository=repository,
            ref=ref
        )

        # Show dependency tree
        if len(graph) > 1:
            print(f"  {skill_name} requires:")
            for skill in graph[:-1]:  # All except the requested skill
                version = skill.get('version', ref)
                print(f"    - {skill['name']} ({version})")

        print(f"\nInstallation plan:")
        for i, skill in enumerate(graph, 1):
            version = skill.get('version', ref)
            print(f"  {i}. {skill['name']} {version}")

        # Detect conflicts
        detect_conflicts(graph)

        # Confirm
        response = input("\nProceed? (Y/n): ").strip().lower()
        if response == 'n' or response == 'no':
            print("Cancelled.")
            return 1

        # Install each skill
        print()
        for skill in graph:
            skill_name_install = skill["name"]
            skill_version = skill.get("version", ref)

            print(f"Installing {skill_name_install} {skill_version}...")

            install_skill(
                skill_metadata=skill,
                marketplace_dir=marketplace_dir,
                ref=ref
            )

            # Validate
            validate_skill(marketplace_dir / skill_name_install)

            print(f"✓ Validated")
            print(f"✓ Installed to {marketplace_dir}/{skill_name_install}/\n")

        print(f"Successfully installed {len(graph)} skill(s).")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
