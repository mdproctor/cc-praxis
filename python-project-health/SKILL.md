---
name: python-project-health
description: >
  Use when a Python project needs a health review. Invoked directly via
  /python-project-health or suggested by project-health. Extends
  project-health with Python-specific categories.
---

# python-project-health

Health checks for Python projects. Runs all universal checks from
`project-health` first, then adds Python-specific checks for type safety,
dependency health, code quality, test coverage, and build integrity.

Follows the same pattern as `java-project-health` and `ts-project-health`
extending `project-health`.

## Prerequisites

**This skill builds on `project-health`.** Apply all universal checks first:

- All universal categories: `docs-sync`, `consistency`, `logic`, `config`,
  `security`, `release`, `user-journey`, `git`, `primary-doc`, `artifacts`,
  `conventions`, `framework`
- Same tier system (1–4) and named aliases (`--commit`, `--standard`,
  `--prerelease`, `--deep`)
- Same output format — Python-specific findings are prefixed with `[python]`

When invoked directly (`/python-project-health`), run universal checks first,
then Python-specific checks. Output is combined — identical to `project-health`
auto-chaining here.

---

## Tier System

Inherited from `project-health` — see [check-categories.md](../project-health/check-categories.md#tier-system).
Python-specific categories (`python-types`, `python-deps`, `python-quality`, `python-testing`, `python-build`) run at tier 3+.

---

## Type-Specific Scan Targets

In addition to the universal document scan, include:

- `pyproject.toml` / `setup.py` / `setup.cfg` — project metadata and build config
- `requirements.txt`, `requirements-dev.txt` — pip dependency files
- `poetry.lock` / `Pipfile.lock` — lockfiles (whichever applies)
- `src/**/*.py` — all Python source files under `src/` layout
- `tests/**/*.py` — all test files
- `.python-version` / `runtime.txt` — Python version pinning
- `mypy.ini` / `[mypy]` section in `pyproject.toml` — type checker config
- `pytest.ini` / `[tool.pytest.ini_options]` in `pyproject.toml` — test runner config
- `.flake8` / `ruff.toml` / `[tool.ruff]` in `pyproject.toml` — linter config

---

## Augmentations to Universal Checks

These extend universal categories with Python-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] README states the supported Python version(s) and setup steps (virtualenv, pip install, etc.)
- [ ] README installation instructions match the actual package manager in use (pip/poetry/pipenv)
- [ ] No documented CLI commands or API functions that no longer exist in source

**Refinement (tier 4):**
- [ ] Could API docs be generated from docstrings (`sphinx`, `pdoc`) rather than maintained manually?
- [ ] Is the Python version requirement clearly communicated to contributors?

### `artifacts` augmentations

**Quality:**
- [ ] `pyproject.toml` or `setup.py` exists at the project root
- [ ] A lockfile is committed (`poetry.lock`, `Pipfile.lock`, or equivalent) — bare `requirements.txt` without pins is insufficient for reproducible installs
- [ ] Source layout is internally consistent — either `src/` layout throughout, or flat layout throughout; not mixed
- [ ] Python version declared — `.python-version`, `runtime.txt`, or `python_requires` in `pyproject.toml`
- [ ] `__pycache__/`, `*.pyc`, `.venv/` / `venv/` are listed in `.gitignore`

**Refinement (tier 4):**
- [ ] Is the `src/` layout used? It prevents accidental imports of the un-installed package during testing.

### `conventions` augmentations

**Quality:**
- [ ] Exactly one package manager in use — no mix of `poetry.lock` + `Pipfile.lock` + bare `requirements.txt`
- [ ] Test configuration lives in one place — `[tool.pytest.ini_options]` in `pyproject.toml`, not spread across `setup.cfg` and `pytest.ini`
- [ ] Python version is declared in exactly one place — not hardcoded in multiple files (Dockerfile, CI YAML, `setup.py`, and `.python-version` all saying different things)
- [ ] No `PYTHONPATH` hacks in test runner config to work around missing `src/` install

**Refinement (tier 4):**
- [ ] Are linting rules consolidated under `[tool.ruff]` or `[tool.flake8]` in `pyproject.toml`?
- [ ] Is the package manager choice documented and enforced (e.g. a `Makefile` target or CI step)?

---

## Python-Specific Categories

These categories are only checked for type: python projects (tier 3+).

### `python-types` — Type Safety Health

**Quality** — Is the codebase typed correctly and without shortcuts?
- [ ] `mypy` is configured (at minimum `ignore_missing_imports = true` to avoid false positives on untyped third-party packages)
- [ ] `mypy` passes with zero errors when run against the source tree
- [ ] No `# type: ignore` without an explanatory comment on the same or preceding line
- [ ] Public functions and methods have type hints on all parameters and return values
- [ ] No bare `Any` in type hints without a justifying comment
- [ ] `Optional[X]` (or `X | None`) used consistently for nullable values — no implicit `None` returns from typed functions

**Refinement (tier 4):**
- [ ] Are there `Any` annotations that could be tightened to concrete types or `TypeVar`?
- [ ] Are there opportunities to use `TypedDict` or `dataclass` instead of untyped `dict` parameters?
- [ ] Could `Protocol` replace concrete base classes where structural subtyping is sufficient?

---

### `python-deps` — Dependency Health

**Quality** — Are dependencies secure, correctly separated, and reproducible?
- [ ] `pip audit` or `safety check` reports no HIGH or CRITICAL severity vulnerabilities
- [ ] Production dependencies are pinned exactly (`==`) in `requirements.txt` or locked via `poetry.lock` / `Pipfile.lock`
- [ ] Dev/test dependencies are separated from production — `[dev-dependencies]` in poetry, `requirements-dev.txt`, or `[project.optional-dependencies]` extras
- [ ] Lockfile is committed and up to date with the declared dependencies
- [ ] No packages installed to the system Python — a virtual environment is in use (`.venv/`, `venv/`, or poetry-managed)

**Refinement (tier 4):**
- [ ] Are there unused dependencies (`pip-autoremove` or manual review)?
- [ ] Are there large packages pulled in for a small subset of features where a lighter alternative exists?
- [ ] Is there a clear process for updating dependencies (Dependabot, `poetry update`, etc.)?

---

### `python-quality` — Code Quality Health

**Quality** — Is the code free of common Python anti-patterns?
- [ ] `flake8` or `ruff` passes with zero errors
- [ ] No mutable default arguments in function signatures (`def f(items=[])` — classic Python gotcha)
- [ ] No bare `except:` clauses — all `except` blocks name a specific exception type
- [ ] No `eval()` or `exec()` on non-constant, user-supplied, or externally sourced input
- [ ] No `import *` from non-`__init__` modules — star imports hide what's actually available
- [ ] No shadowing of built-in names (`list`, `dict`, `id`, `type`, `input`)

**Refinement (tier 4):**
- [ ] Are there plain `dict`s used as records where `dataclass` or `TypedDict` would add clarity and type safety?
- [ ] Are there repeated patterns of `if/elif` chains that could be replaced with a dispatch table?
- [ ] Are there functions doing too many things that could be split at natural boundaries?

---

### `python-testing` — Test Health

**Quality** — Are tests present, passing, and meaningful?
- [ ] `pytest` runs with zero failures
- [ ] Coverage meets the project-configured threshold (if `--cov-fail-under` is set in pytest config)
- [ ] No `pytest.skip()` or `unittest.skip()` without an explanatory comment
- [ ] No `print()` statements in test files — use `capfd` fixture or structured assertions
- [ ] Tests use `tmp_path` pytest fixture for temporary files, not hardcoded paths like `/tmp/test_output`
- [ ] No test that always passes vacuously (`assert True`, `assert 1 == 1`)

**Refinement (tier 4):**
- [ ] Are there repeated test patterns that could be collapsed with `@pytest.mark.parametrize`?
- [ ] Is the ratio of integration tests to unit tests appropriate for the project's risk profile?
- [ ] Are there known flaky tests? Are they quarantined with `@pytest.mark.flaky` or fixed?

---

### `python-build` — Build Health

**Quality** — Does the package install, import, and distribute cleanly?
- [ ] Package installs cleanly in a fresh virtual environment (`pip install -e .` or `poetry install`)
- [ ] Python version requirement is declared (`python_requires` in `pyproject.toml` or `setup.py`)
- [ ] No circular imports between modules — verify by importing the top-level package in a clean environment
- [ ] `__init__.py` files are present in all intended package directories (absent `__init__.py` silently breaks imports in non-namespace packages)
- [ ] No import-time side effects in library code (no logging config, no network calls, no file writes at module import)

**Refinement (tier 4):**
- [ ] Is the `src/` layout in use? It prevents stale, un-installed code from being picked up during test runs.
- [ ] Is there a `Makefile` or `tox.ini` documenting the full local dev workflow (install, lint, test, build)?
- [ ] Are wheel and sdist both buildable (`python -m build`) without errors?

---

## Output Format

Universal findings appear without a prefix. Python-specific findings use `[python]`:

```
## project-health report — python-types, python-deps, python-quality, python-testing, python-build [python]

### CRITICAL (must fix)
- [python][python-build] Circular import between src/app/models.py and src/app/services.py — ImportError at runtime

### HIGH (should fix)
- [python][python-deps] requests==2.27.1 has CRITICAL vulnerability CVE-2023-32681 — upgrade to 2.31.0
- [python][python-types] 5 public functions in src/app/api.py have no type hints

### MEDIUM (worth fixing)
- [python][python-quality] mutable default argument `def process(items=[])` in src/app/utils.py line 42
- [python][python-testing] 3 skipped tests in tests/test_auth.py have no comment explaining why

### LOW (nice to fix)
- [python][python-build] Missing __init__.py in src/app/helpers/ — directory not importable as a package

### PASS
✅ docs-sync, consistency, security, git, python-deps, python-testing
```

Severity scale: see [check-categories.md](../project-health/check-categories.md#severity-scale).

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Python-specific checks don't replace universal ones | Always run universal checks first (prerequisite) |
| Only checking if tests pass, not type correctness | A green test suite with no type hints silently accumulates `Any` debt | Run `mypy` separately; test pass is not a proxy for type correctness |
| Treating `pip audit` warnings as low priority | Dependency vulnerabilities have CVE severity ratings for a reason; HIGH/CRITICAL warrant immediate action | Flag HIGH/CRITICAL as HIGH severity; do not defer without a documented reason |
| Accepting unpinned `requirements.txt` in production | A `requirements.txt` without `==` pins installs different versions on each deploy | Require exact pins or a committed lockfile (`poetry.lock`, `Pipfile.lock`) |
| Skipping `mypy` because "it's too strict" | Incremental adoption is possible — start with `ignore_missing_imports = true` and add coverage over time | Configure `mypy` narrowly rather than not at all; no config means no coverage |
| Ignoring missing `__init__.py` files | The absence is only caught at import time, not by linting — it causes silent test collection failures | Check all intended package directories; flag missing `__init__.py` as MEDIUM |

---

## Skill Chaining

**Invoked by:** User directly via `/python-project-health`. Also suggested by `project-health` when a Python project is detected — `type: python` is not a built-in project type (Python projects use `type: generic` or `type: custom`), so `project-health` cannot auto-chain here; it suggests this skill instead

**Can be invoked directly:** Yes — `/python-project-health` runs universal checks first,
then Python-specific checks, producing identical output to the auto-chained flow

**Prerequisite for:** Nothing currently chains from this skill

**Related skills:**
- `project-health` — universal prerequisite foundation
- `python-dev` — Python development skill; `python-project-health` catches issues that accumulate between sessions
- `python-code-review` — per-PR code review; `python-project-health` is for whole-project health
- `pip-dependency-update` — dependency upgrades; `python-deps` findings here often indicate upgrades needed
- `project-refine` — companion for improvement opportunities after health is green
