---
name: dependency-management-principles
description: >
  Universal dependency management principles for projects using BOM (Bill of
  Materials) patterns. Covers alignment verification, compatibility checking,
  upgrade safety, and version drift prevention. Works with any package manager
  that supports dependency management patterns. Use as foundation for
  package-manager-specific dependency update skills.
---

# Dependency Management Principles

Universal principles for managing dependencies in projects using BOM (Bill of Materials) or similar dependency management patterns.

## Why This Matters

**Caught early vs. caught in production:**
- Version conflict found during update: 5-minute rollback
- Version conflict in production: Service crashes, emergency rollback, incident postmortem

**What dependency management prevents:**
- **Version drift** where dependencies conflict with platform BOM
- **Breaking changes** from major upgrades without migration planning
- **Security vulnerabilities** from outdated dependencies with known CVEs
- **Build failures** from incompatible dependency combinations

**What dependency management is:**
- Proactive alignment with platform/framework BOMs
- Controlled, tested upgrades with compatibility verification
- Protection against accidental version downgrades

## Workflow

### Step 1 — Understand current state

Read the dependency manifest file to identify:
- Platform/framework version
- BOM or dependency management strategy
- Current dependency versions
- Any explicit version overrides

### Step 2 — Determine the update task

| User request | Action |
|---|---|
| "Upgrade platform" | Check latest platform version, propose upgrade |
| "Add dependency X" | Check if X is BOM-managed; if yes, add without version |
| "Bump dependency X" | Check if X is BOM-managed; warn if manually overriding |
| "Check for updates" | Run update check, filter by alignment risk |

### Step 3 — Check dependency management alignment

Ask yourself: **Is this dependency managed by a platform or ecosystem BOM?**

**BOM alignment rules:**

| Situation | Action |
|---|---|
| Dependency is in platform BOM | Add with no explicit version |
| Dependency is in ecosystem BOM | Add with no explicit version |
| Extension/plugin not in BOM | Specify version; note as "unmanaged" |
| Overriding BOM-managed version | Warn: "Only do this for CVE fixes or confirmed compatibility" |

### Step 4 — Check platform compatibility

For platform version upgrades:
- Check breaking changes in release notes
- Verify ecosystem compatibility (plugins, extensions)
- Check language/runtime version requirements
- Review migration guides

### Step 5 — Propose changes

Present clear proposal:

```
## Proposed dependency changes

| Package | Current | Proposed | BOM managed? | Notes |
|---|---|---|---|---|
| platform-core | 3.2.1 | 3.4.0 | — | Platform upgrade |
| plugin-x | 0.6.0 | 0.7.1 | No | Check release notes |

## BOM alignment check
✅ All other dependencies remain BOM-managed — no version drift.

## Risks
- plugin-x 0.7.1 release notes should be reviewed
- Check for breaking changes in platform 3.4.0
```

Then ask:
> "Does this look good? Reply **YES** to apply these changes,
> or tell me what to adjust."

### Step 6 — Apply and verify

Only after explicit YES:
1. Apply version changes to manifest file
2. Run build/compile check to verify changes
3. Report success or errors

## BOM Alignment Decision Flow

```dot
digraph bom_decision {
    "Adding/updating dependency" [shape=doublecircle];
    "In platform BOM?" [shape=diamond];
    "In ecosystem BOM?" [shape=diamond];
    "CVE fix required?" [shape=diamond];
    "Add with no version" [shape=box, style=filled, fillcolor=lightgreen];
    "Add version, note unmanaged" [shape=box, style=filled, fillcolor=yellow];
    "Override with WARNING" [shape=box, style=filled, fillcolor=red];

    "Adding/updating dependency" -> "In platform BOM?";
    "In platform BOM?" -> "CVE fix required?" [label="yes"];
    "In platform BOM?" -> "In ecosystem BOM?" [label="no"];
    "CVE fix required?" -> "Override with WARNING" [label="yes"];
    "CVE fix required?" -> "Add with no version" [label="no"];
    "In ecosystem BOM?" -> "Add with no version" [label="yes"];
    "In ecosystem BOM?" -> "Add version, note unmanaged" [label="no"];
}
```

---

## Common Pitfalls

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Adding version to BOM-managed dependency | Overrides BOM, causes version drift and conflicts | Remove version, let BOM manage it |
| Upgrading one dependency without checking BOM | Breaks compatibility with platform | Check dependency tree first |
| Using platform version in individual dependencies | Duplicate/conflicting version management | Only set in dependency management section |
| Bumping platform without checking ecosystem | Platform-ecosystem version mismatch | Update both in lockstep |
| Applying changes without build check | Silent compilation failures post-commit | Always verify build after changes |
| Upgrading major version without release notes | Breaking changes surprise you | Check release notes before proposing |
| Adding unmanaged version without noting it | Future confusion about explicit version | Note "unmanaged" in proposal |

## Skill Chaining

**Not invoked directly** — this is a foundation skill referenced via Prerequisites.

Package-manager-specific skills (`maven-dependency-update` for Maven/Quarkus,
`npm-dependency-update`, `go-dependency-update`, etc.) implement these principles
with package-manager-specific commands, file formats, and tooling.

**Extended by:** [`maven-dependency-update`] for Maven/Quarkus projects (and future package-manager-specific skills)
