---
name: pip-dependency-update
description: >
  Use when updating Python packages, bumping versions, adding dependencies,
  or running pip audit in a Python project. Applies to pip, poetry, and
  pipenv projects.
---

# pip / Poetry / pipenv Dependency Update Helper

You are an expert in Python ecosystem dependency management. Your primary
concern is keeping dependencies current, secure, and version-consistent —
never applying changes without user confirmation, and always checking for
breaking changes before major bumps.

## Prerequisites

**Load `~/.hortora/garden/approaches/dependency-management.md`** before proceeding.
Apply all principles from that file, then the Python/pip-specific patterns below.

## Core Rules

- **Never `pip install --upgrade` everything at once** — update one package
  at a time, verify the application, then continue.
- **Never apply changes** without explicit user confirmation.
- **Check breaking changes** before any major version bump — read the
  CHANGELOG or GitHub releases page first.
- **Run `pip audit` after every update** — address HIGH/CRITICAL findings
  immediately; don't defer them.
- **Always use a virtual environment** — never install to system Python.
- **Pin exact versions in production apps** (`==`); use compatible-release
  specifiers (`~=`) or ranges in published libraries.
- **Separate runtime from dev dependencies** — use `requirements-dev.txt`,
  `[dev]` extras in `pyproject.toml`, or `poetry add --group dev`.
- **Commit the lockfile** (`poetry.lock`, `Pipfile.lock`, or a pinned
  `requirements.txt`) — it is not optional.

---

## Workflow

### Step 1 — Understand the current state

```bash
# Identify which package manager is in use
ls pyproject.toml poetry.lock Pipfile Pipfile.lock requirements.txt 2>/dev/null

# pip / requirements.txt
pip list --outdated
pip audit

# poetry
poetry show --outdated
poetry run pip audit   # or: pip audit inside the poetry venv

# pipenv
pipenv update --outdated
pipenv run pip audit
```

Identify:
- The package manager in use (pip / poetry / pipenv / conda)
- Current versions and available updates
- Any security advisories from the audit output
- Whether dependencies are pinned exactly or use ranges

### Step 2 — Classify the update task

| User request | Action |
|---|---|
| "Fix security vulnerabilities" | Run audit, address HIGH/CRITICAL first |
| "Add package X" | Classify runtime vs dev; check version specifier policy |
| "Bump package X" | Check latest version, semver delta (patch/minor/major), read changelog if major |
| "Update everything" | Warn: update one package at a time; propose a prioritized list |
| "Upgrade Python" | Check all current packages for Python version support first |

### Step 3 — Check compatibility

Before proposing any change:

```bash
# pip — check what Python versions a package supports
pip index versions <package>
pip show <package>

# poetry — preview what would change
poetry add <package>@latest --dry-run

# Check package metadata for Python version requirement
pip install <package>==<version> --dry-run 2>&1 | grep Requires-Python
```

**Compatibility rules:**

| Situation | Action |
|---|---|
| Patch version update (`1.2.3 → 1.2.4`) | Safe to apply; run tests |
| Minor version update (`1.2.3 → 1.3.0`) | Check changelog; usually safe |
| Major version update (`1.x → 2.x`) | Read migration guide; test thoroughly; offer ADR |
| Security patch requiring major bump | Apply immediately; document in proposal |
| Python version constraint conflict | Resolve before applying; show conflict clearly |
| Yanked version on PyPI | Treat as WARNING; skip to next available version |

### Step 4 — Propose changes

Present a clear proposal before touching anything:

```
## Proposed dependency changes

| Package | Current | Target | Breaking? | Reason |
|---------|---------|--------|-----------|--------|
| requests | 2.28.2 | 2.32.3 | No | Security patch (CVE-2024-35195) |
| pydantic | 1.10.13 | 2.7.0 | Yes | v2 is new major — migration required |
| pytest | 7.4.0 | 8.2.0 | No | Latest stable |

## Security findings (pip audit)
⚠️  1 HIGH vulnerability in requests <2.32.3 (CVE-2024-35195)

## Risks
- pydantic 2 is a major version — v1 models must be migrated. Read the
  migration guide before confirming: https://docs.pydantic.dev/latest/migration/
- All other updates are patch/minor — low risk.
```

Then ask:
> "Does this look good? Reply **YES** to apply these changes, or tell me
> what to adjust."

### Step 4a — Detect major version changes and offer ADR

**After user confirms YES**, but before applying changes:

**Check for major version upgrades:**
- Any dependency with a major semver change (e.g., `1.x → 2.x`)
- Framework upgrades (Django, Flask, FastAPI, SQLAlchemy)
- Python interpreter version changes
- Addition of significant new packages (auth, ORM, message queue, async runtime)

**If major change detected:**
> I notice this is a major version upgrade:
> - [Package] [old version] → [new version]
>
> Major version changes are architectural decisions — they may introduce
> breaking changes, new patterns, or different API contracts.
>
> Would you like to create an ADR documenting why we're making this upgrade? (YES/no)

**If user says YES:**
- Invoke `adr` skill with context about the upgrade
- Let user draft the ADR
- After ADR is created, continue to Step 5

**If user says NO or it's not a major change:**
- Continue to Step 5

### Step 5 — Apply and verify

Only after explicit YES:

**pip / requirements.txt:**
```bash
# Activate the virtual environment first
source .venv/bin/activate   # or: .venv\Scripts\activate on Windows

# Install specific version (use == for production apps)
pip install requests==2.32.3
pip install --upgrade pytest

# Regenerate pinned requirements
pip freeze > requirements.txt

# Run tests to catch regressions
pytest

# Re-check for new audit issues
pip audit
```

**poetry:**
```bash
poetry add requests@2.32.3
poetry add --group dev pytest@latest

poetry run pytest
poetry run pip audit   # or pip audit inside venv
```

**pipenv:**
```bash
pipenv install requests==2.32.3
pipenv install --dev pytest

pipenv run pytest
pipenv run pip audit
```

Report success or any errors introduced by the update.

### Step 6 — Offer review for new packages

After adding a significant new package (especially auth, ORM, HTTP client,
or payments):

> "This adds [package] as a new dependency. Would you like me to do a quick
> `python-code-review` of the integration to check for misuse or security issues?"

---

## Version Strategy Decision Flow

```mermaid
flowchart TD
    Update_requested((Update requested))
    Security_vulnerability_{Security vulnerability?}
    Semver_delta_{Semver delta?}
    Read_changelog{Read changelog}
    Has_breaking_changes_{Has breaking changes?}
    Apply_immediately[Apply immediately\npip audit fix]
    Propose_and_apply[Propose and apply\nlow risk]
    Propose_with_note[Propose with\nchangelog review note]
    Read_migration_guide[Read migration guide\ntest thoroughly]
    Offer_ADR[Offer ADR]
    User_confirms_{User confirms?}
    Apply[Apply changes]
    Abort[Abort update]
    Update_requested --> Security_vulnerability_
    Security_vulnerability_ -->|"HIGH / CRITICAL"| Apply_immediately
    Security_vulnerability_ -->|"none / LOW"| Semver_delta_
    Semver_delta_ -->|patch| Propose_and_apply
    Semver_delta_ -->|minor| Read_changelog
    Semver_delta_ -->|major| Read_migration_guide
    Read_changelog --> Has_breaking_changes_
    Has_breaking_changes_ -->|no| Propose_and_apply
    Has_breaking_changes_ -->|yes| Propose_with_note
    Read_migration_guide --> Offer_ADR
    Offer_ADR --> User_confirms_
    Propose_and_apply --> User_confirms_
    Propose_with_note --> User_confirms_
    User_confirms_ -->|yes| Apply
    User_confirms_ -->|no| Abort
```

---

## Version Strategy Reference

**Version specifier comparison:**

| Specifier | Meaning | Example installs |
|-----------|---------|-----------------|
| `==1.2.3` | Exact pin | Only `1.2.3` |
| `~=1.2.3` | Compatible release (patch) | `1.2.3` up to `<1.3.0` |
| `~=1.2` | Compatible release (minor) | `1.2` up to `<2.0` |
| `>=1.2,<2.0` | Explicit range | `1.2` to `<2.0` |
| `^1.2.3` | Semver caret (poetry only) | `1.2.3` up to `<2.0.0` |

**When to pin exactly (`==`):**
- Production applications (reproducible, auditable builds)
- Security-sensitive packages (auth, crypto)
- After a major version migration (freeze while stabilizing)
- Any package in `requirements.txt` committed as a lockfile

**When to use ranges:**
- Published libraries (`install_requires` in `pyproject.toml`) — don't restrict consumers
- `[dev]` / test dependencies where floating is acceptable

---

## Package Manager Quick Reference

| Task | pip | poetry | pipenv |
|------|-----|--------|--------|
| Add runtime dep | `pip install X==1.2` | `poetry add X@1.2` | `pipenv install X==1.2` |
| Add dev dep | `pip install --extra-index … X` (in requirements-dev.txt) | `poetry add --group dev X` | `pipenv install --dev X` |
| Show outdated | `pip list --outdated` | `poetry show --outdated` | `pipenv update --outdated` |
| Security audit | `pip audit` | `poetry run pip audit` | `pipenv run pip audit` |
| Regenerate lockfile | `pip freeze > requirements.txt` | `poetry lock` | auto-updated by pipenv |

---

## Success Criteria

Dependency update is complete when:

- ✅ User has confirmed changes with **YES**
- ✅ All proposed versions installed with no dependency conflicts
- ✅ `pip audit` shows no new HIGH/CRITICAL findings
- ✅ Tests pass (`pytest`)
- ✅ Application starts without import errors
- ✅ Lockfile updated and staged for commit (`poetry.lock`, `Pipfile.lock`, or pinned `requirements.txt`)
- ✅ For major upgrades: ADR created documenting the decision

**Not complete until** all criteria met and changes committed.

---

## Common Pitfalls

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Installing to system Python | Pollutes global environment; version conflicts across projects | Always activate a virtual environment first |
| `requirements.txt` without exact pins in production | Non-reproducible builds; silent regressions on redeploy | Use `pip freeze > requirements.txt` for pinned lockfile |
| `pip audit fix --force` blindly | Jumps to major versions with breaking changes | Review the diff; prefer targeted `pip install X==<version>` |
| Mixing pip and conda in the same environment | Inconsistent dependency resolution; corrupted environment | Pick one: use conda envs for conda packages, venvs for pip |
| Not testing after update | Regressions discovered in production | Always run full test suite (`pytest`) after any dependency change |
| Ignoring deprecation warnings | Deprecated APIs become errors in the next major version | Fix `DeprecationWarning` during minor bumps, not after a major breaks you |
| `pip install -r requirements.txt` without activating venv | Installs to wrong Python; may require sudo | Activate venv first, or use `python -m pip install -r requirements.txt` |

---

## Skill Chaining

**Invoked by:** User explicitly — "update dependencies", "bump package X", "run pip audit", "add package Y"

**Invokes:**
- [`adr`] when major version upgrades or significant new packages detected (offered to user)
- [`python-code-review`] after adding new packages with security implications (offered to user)

**Can be invoked independently:** User says "update dependencies", "add a package", "pip audit", or whenever `requirements.txt`, `pyproject.toml`, or `Pipfile` changes are needed
