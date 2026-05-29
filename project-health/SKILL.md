---
name: project-health
description: >
  Use when correctness, completeness, or consistency of a project needs
  verification — "is the project healthy?", "pre-release check", "do a health
  check", "check docs are in sync", invokes /project-health. NOT for
  improvement suggestions (use project-refine for that).
---

# Project Health

Answer the question: **is this project correct, complete, and consistent?**

Runs universal quality checks that apply to every project type, then runs
type-specific health checks inline based on the project type declared in CLAUDE.md.

---

## Step 0 — Read Project Type

Before any checks run, read the project type from CLAUDE.md:

```bash
grep -A 2 "## Project Type" CLAUDE.md 2>/dev/null
```

Extract the type: `skills` | `java` | `blog` | `custom` | `generic`

If CLAUDE.md is missing or has no Project Type, treat as `generic` and note it
as a `config` finding.

Store the type — type-aware checks (`primary-doc`, `artifacts`, `conventions`,
`framework`) use it throughout this skill.

---

## Step 1 — Determine Tier

Parse flags from the invocation:

| Flag | Tier | What runs |
|------|------|-----------|
| `--commit` | 1 | `validate_all.py --tier commit` only |
| `--standard` | 2 | Universal quality checks |
| `--prerelease` | 3 | Universal + type-specific quality checks |
| `--deep` | 4 | All of tier 3 + refinement questions |
| `--tier N` | N | Explicit tier (1–4) |

If no tier flag is given, prompt:

> **How thorough should this check be?**
>
> 1 — **Quick** — validators only (~30s)
> 2 — **Standard** — universal quality checks (~5 min)
> 3 — **Full** — universal + type-specific quality (~15 min)
> 4 — **Deep** — everything + refinement questions (~30 min)
>
> Enter 1–4 (default: 2):

Wait for response. If no response, use tier 2.

Also parse:
- `--save` → write report to `YYYY-MM-DD-health-report.md` after output
- Category names (e.g. `docs-sync consistency`) → run only those categories
- If categories specified without `--tier`, run at tier 2

---

## Step 2 — Tier 1: Run Automated Validators

**Always run first** (all tiers include this):

```bash
python scripts/validate_all.py --tier commit
```

If this script doesn't exist, note it as a `config` finding and skip.

Report output. If CRITICAL findings from validators → flag them.

For tier 1, **stop here**. Present findings and exit.

---

## Step 3 — Build Document Scan List

For tier 2+, build the scan scope before running checks.

**Always included:**
- All `.md` files (recursive) under `doc/`, `docs/`, `documentation/` (case-insensitive)
- Root-level `.md` files matching: `readme`, `overview`, `summary`, `index`, `contributing`,
  `governance`, `code_of_conduct`, `changelog`, `history`, `release`, `architecture`,
  `design`, `decisions`, `vision`, `philosophy`, `principles`, `api`, `schema`, `glossary`,
  `security`, `deployment`, `install`, `usage`, `troubleshooting`, `roadmap`, `spec`,
  `requirements`, `quality` (case-insensitive match on filename stem)
- Any root `.md` not on the list is still scanned
- Any `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md` anywhere in the tree

**Type-specific additions (use detected type from Step 0):**
- `skills` → all `SKILL.md` files in direct subdirectories
- `java` → `pom.xml`, `build.gradle`, Javadoc comments in `src/`
- `blog` → `_config.yml`, `_posts/`, `_layouts/`, `_includes/`
- `custom` → primary document path declared in CLAUDE.md

**User-configured additions:**
Read `## Health Check Configuration` from CLAUDE.md:
```
Additional doc paths: wiki/, design/
```
Add any listed paths to the scan scope.

---

## Step 4 — Read CLAUDE.md Health Configuration

```bash
grep -A 10 "## Health Check Configuration" CLAUDE.md 2>/dev/null
```

Parse:
- `Default checks:` → limit to these categories if no categories specified on invocation
- `Skip:` → exclude these categories even if requested
- `Additional doc paths:` → already applied in Step 3

If no configuration section, use built-in defaults: run all universal categories.

---

## Step 5 — Run Universal Checks

Run the applicable check categories at the requested tier. Skip categories listed
in `Skip:` from CLAUDE.md. If specific categories were requested, run only those.

For **tier 2**: quality items only (pass/fail checks).
For **tier 4**: quality items + refinement questions (judgment items).

**Read [check-categories.md](check-categories.md)** for the full quality and
refinement checklists for all 12 universal categories before running checks:
`docs-sync`, `consistency`, `logic`, `config`, `security`, `release`,
`user-journey`, `git`, `primary-doc`, `artifacts`, `conventions`, `framework`.

---

## Step 6 — Run Type-Specific Checks (Tier 3+)

At tier 3 and 4, after universal checks complete, run the relevant type-specific
section below. Type-specific findings are prefixed with `[type]` (e.g. `[java]`).

| Project type | Section to run |
|---|---|
| `skills` | [Skills Repository](#skills-repository) |
| `java` | [Java / Quarkus](#java--quarkus) |
| `blog` | [Blog (Jekyll)](#blog-jekyll) |
| `custom` | [Custom](#custom) |
| `python` | [Python](#python) |
| `ts` / TypeScript detected | [TypeScript / Node.js](#typescript--nodejs) |
| `generic` | Skip — universal checks only |

If the project type is `generic` but TypeScript or Python files are found, suggest
running the relevant section manually.

---

## Step 7 — Present Report

```
## project-health report — [categories run] — tier [N]

### CRITICAL (must fix)
- [category] finding description

### HIGH (should fix)
- [category] finding description

### MEDIUM (worth fixing)
- [category] finding description

### LOW (nice to fix)
- [category] finding description

### PASS
✅ category1, category2, ...
```

Universal findings have no extra prefix. Type-specific findings are prefixed
with `[type]` (e.g. `[java]`). If no findings in a severity level, omit that section.

---

## Step 8 — Offer Auto-Fix (Mechanical Issues Only)

For mechanical findings (wrong count in README, stale version number, missing
`commands/<name>.md`), offer:

> **Auto-fixable findings detected.**
>
> Would you like me to apply mechanical fixes now?
> - [list of specific fixes]
>
> **(YES / NO — judgment calls are never auto-applied)**

Wait for response. Apply only on YES. Never auto-apply.

---

## Step 9 — Save Report (if --save)

If `--save` was passed, write findings to a date-prefixed file:

```bash
# Format: YYYY-MM-DD-health-report.md
```

Tell user:
> Report saved to `YYYY-MM-DD-health-report.md`. This file is gitignored by default.

Verify `.gitignore` includes `*-health-report.md` or similar. If not, suggest adding it.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Running type-specific checks before reading project type | Checks have no context | Always read project type in Step 0 first |
| Reporting "plans to implement" as bugs | Intentional design language | Distinguish docs describing intent vs. describing current state |
| Auto-fixing judgment findings | Judgment calls require human decision | Only auto-fix mechanical findings, always with YES confirmation |
| Skipping type-specific section at tier 3+ | Incomplete health picture | Run the type-specific section — it's mandatory at tier 3+ unless type is generic |
| Treating all findings as equal | CRITICAL blocks release, LOW does not | Use severity consistently |
| Running `docs-sync` without reading the actual source files | Can't verify claims without reading | Read code and docs together |

---

## Success Criteria

Health check is complete when:

- ✅ Project type read from CLAUDE.md before any checks ran
- ✅ Tier confirmed (via flag or prompt)
- ✅ All applicable universal categories checked at the requested tier
- ✅ Type-specific section run at tier 3+ (or skipped for generic)
- ✅ Report presented with findings grouped by severity
- ✅ Mechanical auto-fix offered (not applied without YES)
- ✅ Report saved if `--save` was passed

**Not complete until** all applicable categories checked and report presented.

---

## Skill Chaining

**Invoked by:**
- User says "health check", "is the project healthy", "pre-release check", or invokes `/project-health`
- Other skills (e.g. `git-commit`) can suggest `/project-health --commit` after significant changes

**Companion skill:**
- [`project-refine`] — once health is green, use project-refine for improvement opportunities (bloat, structure, deduplication). They share the same CLAUDE.md Health Check Configuration section.

---

---

# Java / Quarkus

Type-specific health checks for Java/Maven/Gradle projects. Run after universal checks
complete (tier 3+). Findings use `[java]` prefix.

## Java: Type-Specific Scan Targets

In addition to the universal document scan, include:

- `pom.xml` (root and all module POMs)
- `build.gradle` / `build.gradle.kts` (if Gradle)
- `src/main/java/` — all `.java` source files
- `src/test/java/` — all test source files
- Javadoc comments in source files (relevant for `docs-sync` and `conventions`)
- `src/main/resources/application.properties` / `application.yaml`

## Java: Augmentations to Universal Checks

These extend universal categories with Java-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] `DESIGN.md` exists and reflects current architecture (java-git-commit blocks without it)
- [ ] No stale entity, service, or repository references in DESIGN.md for classes that were removed
- [ ] Module structure in DESIGN.md matches actual Maven/Gradle module layout

**Refinement (tier 4):**
- [ ] Could DESIGN.md be split into focused modules (architecture, API, data model)?
- [ ] Has DESIGN.md grown beyond what a single file can communicate clearly?

### `artifacts` augmentations

**Quality:**
- [ ] `docs/DESIGN.md` exists (required by `java-git-commit` workflow) — if missing, offer to create a stub using the java DESIGN.md template from `workspace-init` Step 6b, commit it, and note it needs content
- [ ] Root `pom.xml` or `build.gradle` is present and parseable
- [ ] All Maven modules declared in parent `pom.xml` have corresponding directories

**Refinement (tier 4):**
- [ ] Is DESIGN.md appropriately sized, or has it grown beyond a single file?

### `conventions` augmentations

**Quality:**
- [ ] BOM (Bill of Materials) strategy is documented in CLAUDE.md or DESIGN.md
- [ ] Commit scopes are consistent with declared conventions (`rest`, `service`, `repository`, `bom`, `config`)
- [ ] No version overrides in module POMs where BOM should manage the version

**Refinement (tier 4):**
- [ ] Could BOM documentation be more concise?
- [ ] Are scope conventions clear enough that a new contributor would use them correctly?

### `framework` augmentations

**Quality:**
- [ ] No blocking JDBC calls on the Vert.x event loop without `@Blocking`
- [ ] `@Blocking` annotations present on all methods that perform I/O outside reactive pipelines
- [ ] CDI injection patterns correct (`@Inject`, not manual construction of `@ApplicationScoped` beans)
- [ ] No raw JDBC access outside `@Repository` classes
- [ ] No `@Entity` classes used as API request/response types

**Refinement (tier 4):**
- [ ] Could Quarkus/Vert.x concurrency guidance in DESIGN.md be better grouped?

## Java-Specific Categories (tier 3+)

### `java-architecture` — Architecture Integrity

**Quality** — Is the Java architecture clean and consistent?
- [ ] Layer separation respected — no direct calls from controller to repository bypassing the service layer
- [ ] Domain model classes not leaking into the API layer (no `@Entity` in REST responses)
- [ ] `@Entity` classes not used as API request/response types
- [ ] No circular imports between packages
- [ ] Service classes do not hold mutable state shared across requests
- [ ] No business logic in `@Entity` or `@Repository` classes — logic belongs in services
- [ ] No cyclic package dependencies (e.g. `com.app.order → com.app.payment → com.app.order`)

**Refinement (tier 4):**
- [ ] Are there service classes doing too many things that could be split?
- [ ] Are there utility classes that have grown into mini-services?
- [ ] Could any layer boundaries be made clearer through package restructuring?

### `java-dependencies` — Maven/Gradle Dependency Health

**Quality** — Are dependencies correct and aligned?
- [ ] All dependencies managed by a BOM — no explicit `<version>` where BOM already manages it
- [ ] No version overrides without a documented reason
- [ ] No duplicate dependencies resolved via transitive dependency paths
- [ ] Test dependencies scoped correctly (`<scope>test</scope>`) — not leaking to runtime
- [ ] `annotationProcessorPaths` includes all required annotation processors
- [ ] BOM overrides don't create runtime mismatches with transitive dependencies
- [ ] No test-scoped dependency accidentally used in production source code

**Refinement (tier 4):**
- [ ] Are there dependencies used in only one place that could be removed?
- [ ] Are there large dependencies pulled in for one small feature?
- [ ] Are there test-scoped dependencies that overlap with production utilities already on the classpath?

### `java-code-quality` — Code Duplication and Extraction Opportunities

**Quality** — Is there code that should be shared but isn't?
- [ ] No logic block appears 3+ times across the codebase (silent divergence risk)
- [ ] No similar-but-not-identical methods that should be parameterised and unified
- [ ] No hardcoded values (strings, numbers, paths) repeated across multiple classes — should be named constants or config
- [ ] No repeated sequences of calls that always appear together and belong in a helper method
- [ ] No repeated string literals across classes (status codes, event names, field names) that should be constants
- [ ] No callback or listener patterns repeated 3+ times that should share a base class or interface

**Refinement (tier 4):**
- [ ] Are there methods just over the threshold for extraction where a small refactor would make them reusable?
- [ ] Are there classes that mix concerns where splitting would naturally isolate reusable logic?
- [ ] Are there utility-style methods inside domain classes that could be extracted to a shared utility?
- [ ] Are there parallel implementations across modules that evolved independently but now do the same thing?
- [ ] Are there abstract base classes or interfaces that would capture shared behaviour if added now?

## Java: Output Example

```
## project-health report — java-architecture, java-dependencies, java-code-quality [java]

### CRITICAL (must fix)
- [java][java-architecture] PaymentController calls PaymentRepository directly, bypassing service layer

### HIGH (should fix)
- [java][framework] OrderService.findAll() makes JDBC call on Vert.x event loop — add @Blocking
- [java][java-dependencies] quarkus-core version pinned in module pom.xml overrides BOM without documented reason

### MEDIUM (worth fixing)
- [java][java-code-quality] UserValidator.validate() logic duplicated in AdminValidator and GuestValidator

### LOW (nice to fix)
- [java][primary-doc] DESIGN.md still references CacheService which was removed in last sprint

### PASS
✅ docs-sync, consistency, security, git, java-architecture
```

## Java: Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Java-specific checks don't replace universal ones | Always run universal checks first |
| Flagging `@Blocking` on every service method | Only I/O-bound methods on the event loop need it | Check whether the method actually performs blocking I/O |
| Calling a utility class a "mini-service" | Utility classes without state are fine | Only flag if a utility class has grown state or lifecycle concerns |
| Reporting BOM override as a bug without context | Overrides can be intentional | Check for a documented reason (comment in pom.xml or DESIGN.md) |
| Treating every code similarity as duplication | Some patterns are intentionally repeated per layer | Flag only identical logic blocks (3+) that diverge silently on bug fixes |
| Flagging an `@Entity` in a DTO as a violation | The concern is `@Entity` used AS the API type | Separate DTO classes that happen to share field names are fine |

**Related skills:** `java-git-commit`, `java-code-review`, `java-update-design`, `maven-dependency-update`, `project-refine`

---

---

# TypeScript / Node.js

Type-specific health checks for TypeScript/Node.js projects. Run after universal checks
complete (tier 3+). Findings use `[ts]` prefix.

## TypeScript: Type-Specific Scan Targets

In addition to the universal document scan, include:

- `tsconfig.json` / `tsconfig.*.json` (all variants)
- `package.json` + lock file (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`)
- `src/**/*.ts`, `src/**/*.tsx` — all TypeScript source files
- Test files: `**/*.test.ts`, `**/*.spec.ts`, `**/__tests__/**`
- `.eslintrc.*` / `eslint.config.*` — linter configuration
- `jest.config.*` / `vitest.config.*` — test runner configuration

## TypeScript: Augmentations to Universal Checks

These extend universal categories with TypeScript-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] README states the TypeScript version and target runtime (Node.js version, browser targets, or both)
- [ ] API documentation (if present) matches exported types and function signatures
- [ ] No documented APIs that no longer exist as exported symbols

**Refinement (tier 4):**
- [ ] Could API docs be generated from JSDoc/TSDoc comments rather than maintained manually?
- [ ] Is the runtime environment (Node version, browser support matrix) clearly communicated?

### `artifacts` augmentations

**Quality:**
- [ ] `docs/DESIGN.md` exists — if missing, offer to create a stub using the typescript DESIGN.md template from `workspace-init` Step 6b, commit it, and note it needs content
- [ ] `tsconfig.json` exists at the project root
- [ ] `tsconfig.json` has `"strict": true` enabled (or individual strict flags all enabled)
- [ ] Lock file is committed and present (`package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`)
- [ ] Build output directory (`dist/`, `build/`, `out/`) is listed in `.gitignore`
- [ ] `.env.example` present if the project requires environment variables (`.env` is gitignored)

**Refinement (tier 4):**
- [ ] Is the choice of package manager (npm/yarn/pnpm) documented and enforced via `engines` or `packageManager` in package.json?

### `conventions` augmentations

**Quality:**
- [ ] Exactly one lock file present — no mix of `package-lock.json` + `yarn.lock` (multiple package managers)
- [ ] `package.json` `scripts` section includes standard commands: `build`, `test`, `lint`
- [ ] No bare `any` in public type declarations or exported interfaces — undocumented `any` indicates missing type design
- [ ] Import paths are consistent — no mixing of relative (`../`) and path-alias (`@/`) styles without documented convention

**Refinement (tier 4):**
- [ ] Are path aliases (`@/`, `~/`) configured in both `tsconfig.json` and the bundler/test runner?
- [ ] Are linting rules documented well enough that a new contributor knows what's enforced?

## TypeScript-Specific Categories (tier 3+)

### `ts-types` — Type Safety Health

**Quality** — Is the codebase typed correctly and without shortcuts?
- [ ] `"strict": true` in `tsconfig.json` (or all equivalent flags individually enabled)
- [ ] No `// @ts-ignore` without an explanatory comment on the same or preceding line
- [ ] No `// @ts-nocheck` in any source file
- [ ] `any` usage is below threshold — zero in new code; legacy `any` is documented with a comment
- [ ] No type assertions (`as SomeType`) applied to user-supplied or external data without validation
- [ ] All exported functions and methods have explicit return type annotations
- [ ] No untyped third-party packages used without a `@types/` package or local declaration file

**Refinement (tier 4):**
- [ ] Could `unknown` + type guards replace `any` at existing locations?
- [ ] Are type assertion sites (`as`) documented with a comment explaining why the assertion is safe?
- [ ] Are there opportunities to derive types from runtime values using `typeof` / `as const` / `satisfies`?

### `ts-async` — Async Pattern Health

**Quality** — Are async operations handled safely and efficiently?
- [ ] No floating promises — every `Promise` is either `await`-ed, returned, or handled with `.catch()`
- [ ] No `await` inside loops where `Promise.all()` or `Promise.allSettled()` would parallelize correctly
- [ ] All async functions have error handling — either `try/catch` or a `.catch()` at the call site
- [ ] No mixing of raw callbacks and promises without explicit promisification (`util.promisify` or equivalent)
- [ ] No `async` functions that never `await` anything (misleading signature)

**Refinement (tier 4):**
- [ ] Are there sequential `await` chains where parallel execution via `Promise.all()` would be safe and faster?
- [ ] Are there opportunities to use `for await...of` with async iterators rather than manual promise chaining?

### `ts-build` — Build Health

**Quality** — Does the project compile and lint cleanly?
- [ ] `tsc --noEmit` passes with zero errors
- [ ] ESLint (or configured linter) passes with zero errors (warnings acceptable if documented)
- [ ] `npm run build` (or equivalent) produces output without errors
- [ ] No circular imports between modules (verify with `madge --circular` or similar if available)
- [ ] Build output directory is not committed to version control

**Refinement (tier 4):**
- [ ] Is bundle size reasonable for the target environment? Are large dependencies justified?
- [ ] Is tree-shaking or dead code elimination configured and working?
- [ ] Are source maps generated for production debugging?

### `ts-dependencies` — Dependency Health

**Quality** — Are dependencies secure, correctly categorised, and minimal?
- [ ] `npm audit` (or equivalent) reports no HIGH or CRITICAL severity vulnerabilities
- [ ] No packages where a major upgrade is available that resolves known security issues
- [ ] Runtime dependencies (`dependencies`) and development tools (`devDependencies`) are correctly separated — no build-only tool in `dependencies`
- [ ] Lock file is committed and up to date with `package.json`
- [ ] `node_modules/` is listed in `.gitignore` and not committed

**Refinement (tier 4):**
- [ ] Are there unused dependencies (`depcheck` or manual review)?
- [ ] Are there large packages pulled in for a small subset of features where a lighter alternative exists?
- [ ] Are peer dependency requirements satisfied and documented?

### `ts-testing` — Test Coverage Health

**Quality** — Are tests present, passing, and meaningful?
- [ ] Test files exist for all modules containing business logic
- [ ] `npm test` (or equivalent) passes with zero failures
- [ ] Coverage meets the project-configured threshold (if `coverageThreshold` is set in jest/vitest config)
- [ ] No `it.skip()` / `test.skip()` / `xit()` / `xtest()` without an explanatory comment
- [ ] No `console.log()` statements in test files (use assertions or test reporter output)
- [ ] No tests that assert `true` unconditionally or assert `expect(true).toBe(true)` (vacuous tests)

**Refinement (tier 4):**
- [ ] Is the ratio of integration tests to unit tests appropriate for the project's risk profile?
- [ ] Are there known flaky tests? Are they quarantined or fixed?
- [ ] Are async operations tested with proper `await` — no tests that pass by never awaiting rejections?

## TypeScript: Output Example

```
## project-health report — ts-types, ts-async, ts-build, ts-dependencies, ts-testing [ts]

### CRITICAL (must fix)
- [ts][ts-build] tsc --noEmit reports 14 errors — project does not compile cleanly

### HIGH (should fix)
- [ts][ts-types] 3 exported functions missing return type annotations in src/api/routes.ts
- [ts][ts-dependencies] lodash@4.17.15 has CRITICAL vulnerability CVE-2021-23337 — upgrade to 4.17.21

### MEDIUM (worth fixing)
- [ts][ts-async] fetchUserData() in src/services/user.ts awaits in a loop — use Promise.all()
- [ts][ts-types] // @ts-ignore on line 42 of src/utils/parser.ts has no explanatory comment

### LOW (nice to fix)
- [ts][ts-testing] 2 skipped tests in src/__tests__/auth.test.ts have no comment explaining why

### PASS
✅ docs-sync, consistency, security, git, ts-dependencies, ts-testing
```

## TypeScript: Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | TypeScript-specific checks don't replace universal ones | Always run universal checks first |
| Flagging all `any` as CRITICAL equally | Legacy codebases accumulate `any` legitimately; new code is different | Flag `any` in new/changed code as HIGH; documented legacy `any` as LOW |
| Reporting a floating promise without verifying it's truly unhandled | Some patterns intentionally fire-and-forget with error logging elsewhere | Trace the call site — confirm no `.catch()` or top-level handler exists |
| Treating `// @ts-ignore` as always wrong | Sometimes external library types are incorrect and `@ts-ignore` is the only option | Flag only when there is no explanatory comment; an explained ignore is acceptable |
| Flagging `devDependencies` separation without checking actual usage | A package listed under `dependencies` may be intentionally bundled | Verify the package is unused at runtime before flagging it as miscategorised |
| Calling skipped tests a CRITICAL finding | Skipped tests slow down quality but don't break production | Severity is LOW unless the skip count is high (>10% of suite) or skips are undocumented |

**Related skills:** `ts-dev`, `ts-code-review`, `npm-dependency-update`, `project-refine`

---

---

# Python

Type-specific health checks for Python projects. Run after universal checks
complete (tier 3+). Findings use `[python]` prefix.

Note: `type: python` is not a built-in project type. Python projects typically
use `type: generic` or `type: custom`. When `project-health` detects Python files
(`.py`, `pyproject.toml`, `requirements.txt`), it runs this section automatically.

## Python: Type-Specific Scan Targets

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

## Python: Augmentations to Universal Checks

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
- [ ] `docs/DESIGN.md` exists — if missing, offer to create a stub using the python DESIGN.md template from `workspace-init` Step 6b, commit it, and note it needs content
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

## Python-Specific Categories (tier 3+)

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

## Python: Output Example

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

## Python: Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Python-specific checks don't replace universal ones | Always run universal checks first |
| Only checking if tests pass, not type correctness | A green test suite with no type hints silently accumulates `Any` debt | Run `mypy` separately; test pass is not a proxy for type correctness |
| Treating `pip audit` warnings as low priority | Dependency vulnerabilities have CVE severity ratings for a reason; HIGH/CRITICAL warrant immediate action | Flag HIGH/CRITICAL as HIGH severity; do not defer without a documented reason |
| Accepting unpinned `requirements.txt` in production | A `requirements.txt` without `==` pins installs different versions on each deploy | Require exact pins or a committed lockfile (`poetry.lock`, `Pipfile.lock`) |
| Skipping `mypy` because "it's too strict" | Incremental adoption is possible — start with `ignore_missing_imports = true` and add coverage over time | Configure `mypy` narrowly rather than not at all; no config means no coverage |
| Ignoring missing `__init__.py` files | The absence is only caught at import time, not by linting — it causes silent test collection failures | Check all intended package directories; flag missing `__init__.py` as MEDIUM |

**Related skills:** `python-dev`, `python-code-review`, `pip-dependency-update`, `project-refine`

---

---

# Skills Repository

Type-specific health checks for Claude Code skill collection repositories (type: skills).
Run after universal checks complete (tier 3+). Findings use `[skills]` prefix.

## Skills: Type-Specific Scan Targets

In addition to the universal document scan, include:

- All `SKILL.md` files in direct subdirectories of the repo root
- All `commands/<skill-name>.md` files
- All `.claude-plugin/plugin.json` files
- `.claude-plugin/marketplace.json` — skill registry and bundle definitions
- `scripts/validate_all.py` and all files under `scripts/validation/`
- `hooks/check_project_setup.sh`
- `~/.claude/settings.json` — session-start hook registration

## Skills: Augmentations to Universal Checks

These extend universal categories with skills-repository-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] README.md reflects the current skill collection (skill counts match actual skills)
- [ ] README.md § Skill Chaining Reference table includes all skills
- [ ] README.md skill descriptions don't contradict the "Use when..." trigger conditions in each SKILL.md

**Refinement (tier 4):**
- [ ] Could README sections be reorganised for better discoverability?

### `artifacts` augmentations

**Quality:**
- [ ] Every skill directory has a `SKILL.md`
- [ ] Every skill directory has a `commands/<skill-name>.md`
- [ ] Every skill directory has a `.claude-plugin/plugin.json`
- [ ] No phantom skills in `marketplace.json` without a corresponding directory and SKILL.md

**Refinement (tier 4):**
- [ ] Are any `plugin.json` files more complex than they need to be?

### `conventions` augmentations

**Quality:**
- [ ] CSO rules documented in CLAUDE.md (`description` starts with "Use when...", no workflow summaries)
- [ ] Skill naming patterns documented and followed
- [ ] Chaining conventions documented

**Refinement (tier 4):**
- [ ] Could naming convention documentation be more concise?

### `framework` augmentations

**Quality:**
- [ ] CSO description examples in CLAUDE.md are correct (good vs. bad examples valid)
- [ ] Skill chaining examples in CLAUDE.md match actual invocation behaviour

**Refinement (tier 4):**
- [ ] Could chaining documentation be better structured?

## Skills-Specific Categories (tier 3+)

### `cross-refs` — Cross-Reference Integrity

**Quality** — Are all skill cross-references complete and bidirectional?
- [ ] Every skill mentioned in the README Skill Chaining Reference table exists on disk
- [ ] Chaining is bidirectional where required (if A chains to B, B mentions being invoked by A)
- [ ] Prerequisites sections reference skills that exist
- [ ] All markdown links to other `.md` files resolve (no 404 within repo)
- [ ] Documented chaining reflects actual invocation — if A says it chains to B, the workflow actually does so
- [ ] No Prerequisites section references a skill with a different purpose than implied

**Refinement (tier 4):**
- [ ] Are any chains unnecessarily long?
- [ ] Could the chaining table be reorganised to group related skills more intuitively?
- [ ] Do the number of cross-references between two skills suggest they should merge?

### `coverage` — Integration Coverage

**Quality** — Are new skills and features fully wired into the broader system?
- [ ] Every skill has a `commands/<skill-name>.md` slash command file
- [ ] Every skill is listed in `.claude-plugin/marketplace.json` plugins list
- [ ] Every skill appears in README.md § Skills section
- [ ] New skills appear in README.md § Skill Chaining Reference table
- [ ] New skills appear in CLAUDE.md § Key Skills
- [ ] Every validator in `scripts/validation/` is wired into `scripts/validate_all.py` at the correct tier
- [ ] Every skill in `marketplace.json` has a corresponding directory and SKILL.md (no phantom skills)
- [ ] README skill descriptions match the "Use when..." trigger conditions in each SKILL.md

**Refinement (tier 4):**
- [ ] Are any manual integration steps candidates for automation?
- [ ] Are there steps consistently forgotten, suggesting a better workflow?

### `quality` — Skill Craft Quality

**Quality** — Are skills well-written and will they trigger correctly?
- [ ] All `description` fields start with "Use when..." (CSO compliance)
- [ ] No description summarises the workflow (only trigger conditions and symptoms)
- [ ] No first/second person in descriptions ("I", "you")
- [ ] All major skills have: Prerequisites (if layered), Common Pitfalls, Success Criteria sections
- [ ] Flowcharts use `flowchart TD` notation with semantic labels
- [ ] Flowcharts only used where decision points are non-obvious
- [ ] No SKILL.md exceeds ~400 lines

**Refinement (tier 4):**
- [ ] Are there skills where the workflow could be expressed in fewer steps?
- [ ] Are any flowcharts earning their complexity, or would a numbered list be clearer?
- [ ] Could any Common Pitfalls rows be removed because they're obvious or never occur?

### `naming` — Naming Consistency

**Quality** — Are skill names consistent across all the places they appear?
- [ ] Skill `name` in frontmatter matches the directory name exactly
- [ ] Skill name in `marketplace.json` matches directory name
- [ ] Command file is named `commands/<skill-name>.md`
- [ ] Skill name in `plugin.json` matches directory name
- [ ] Skill name in README matches actual directory name (no typos or variants)
- [ ] All references to a skill use identical spelling across chaining tables, README, CLAUDE.md

**Refinement (tier 4):**
- [ ] Would a new user guess the right skill name without reading the docs?
- [ ] Are any names technically accurate but unintuitive?

### `infrastructure` — Tooling Infrastructure

**Quality** — Is the supporting infrastructure correct?
- [ ] All validators in `scripts/validation/` are wired into `scripts/validate_all.py`
- [ ] Each validator is assigned to the correct tier (COMMIT: <2s, PUSH: <30s, CI: <5min)
- [ ] Session-start hook is registered in `~/.claude/settings.json`
- [ ] Hook script at `hooks/check_project_setup.sh` matches the expected template
- [ ] Generated files (reports, caches) are in `.gitignore`
- [ ] `.gitignore` entries match the files that validators or scripts actually generate

**Refinement (tier 4):**
- [ ] Are any two validators doing overlapping checks that could be merged?
- [ ] Are any validators in a higher tier than their actual speed justifies?
- [ ] Could any scripts be removed because the problem they solve no longer exists?

### `dependencies` — Skill Dependencies

**Quality** — Do skill dependency chains actually work?
- [ ] All skills listed as Prerequisites exist on disk
- [ ] No circular dependency chains exist
- [ ] `plugin.json` dependency names match actual skill directory names
- [ ] Marketplace dependency resolution would succeed for all skills
- [ ] Optional dependencies are genuinely optional — the skill functions without them

**Refinement (tier 4):**
- [ ] Are any chains deeper than necessary?
- [ ] Could any skill with only one dependent be absorbed into that dependent?

### `performance` — Token Budget

**Quality** — Are skills within their token budget?
- [ ] No SKILL.md exceeds ~400 lines
- [ ] Heavy reference material extracted to separate `.md` files
- [ ] No duplicate content across skills inflating token cost
- [ ] No skill substantially duplicates passages from its dependency skills (each owns its scope)
- [ ] SKILL.md content is about how to use the skill, not background theory

**Refinement (tier 4):**
- [ ] Are there skill sections that add length without adding guidance?
- [ ] Are there validators whose findings could fold into an existing validator?

### `effectiveness` — Skill Effectiveness

**Quality** — Are skills correctly scoped and triggered?
- [ ] No two skills overlap significantly in purpose
- [ ] No description is so generic it would trigger on everything
- [ ] No description is so specific it would never trigger
- [ ] Obvious use cases for a skill collection repository are covered
- [ ] Skill workflow outputs match the declared use case (a "validate" skill produces pass/fail, not open-ended commentary)
- [ ] No skill description references other skills by file path rather than human-readable name

**Refinement (tier 4):**
- [ ] Are any skills doing so little they'd be better absorbed into their caller?
- [ ] Are there common workflows requiring 3+ skills that could be wrapped into one?

## Skills: Output Example

```
## project-health report — cross-refs, coverage, quality [skills]

### CRITICAL (must fix)
- [skills][coverage] issue-workflow missing from README § Skill Chaining Reference

### HIGH (should fix)
- [skills][cross-refs] git-commit says it routes to blog-git-commit but blog-git-commit doesn't mention being invoked by git-commit

### LOW (nice to fix)
- [skills][performance] update-primary-doc/SKILL.md is 312 lines — approaching budget

### PASS
✅ docs-sync, consistency, security, naming, dependencies
```

## Skills: Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Skills-specific checks don't replace universal ones | Always run universal checks first |
| Checking only the README for cross-refs | CLAUDE.md § Key Skills and chaining tables are separate | Check README, CLAUDE.md, and each SKILL.md's chaining section |
| Treating long skills as automatically bad | A 380-line skill covering a complex domain may be fine | Flag only if length is from padding, not substance |
| Marking a skill "not covered" in README when it's principles-only | Principles skills are never invoked directly | Principles skills should be listed as foundations, not as primary entries |
| Flagging missing slash command for principles skills | Principles skills are Prerequisites, not direct invocations | Only flag missing `commands/<name>.md` for user-invocable skills |
| Calling a dependency circular after one hop | Circular means A→B→A, not A→B and B→A in different contexts | Trace the actual invocation chain before flagging |

**Related skills:** `git-commit`, `project-refine`

---

---

# Blog (Jekyll)

Type-specific health checks for GitHub Pages / Jekyll blog projects (type: blog).
Run after universal checks complete (tier 3+). Findings use `[blog]` prefix.

## Blog: Type-Specific Scan Targets

In addition to the universal document scan, include:

- `_config.yml` — Jekyll site configuration
- `_posts/` — all post files (recursive)
- `_drafts/` — draft post files
- `_layouts/` — layout templates
- `_includes/` — reusable includes
- `assets/` — images, CSS, JavaScript

## Blog: Augmentations to Universal Checks

These extend universal categories with blog-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] All posts in `_posts/` follow `YYYY-MM-DD-title.md` filename convention
- [ ] Jekyll front matter is valid on all posts (parseable YAML)

**Refinement (tier 4):**
- [ ] Could post metadata (categories, tags) be standardised for better navigation?

### `artifacts` augmentations

**Quality:**
- [ ] `_posts/` directory exists
- [ ] `_config.yml` is present
- [ ] `_layouts/` and `_includes/` directories exist if referenced by any post or config

**Refinement (tier 4):**
- [ ] Is `_config.yml` lean, or has it accumulated unused config?

### `conventions` augmentations

**Quality:**
- [ ] Jekyll conventions are documented in CLAUDE.md
- [ ] Blog commit types are valid (post/edit/draft/asset/config) — see `blog-git-commit`
- [ ] Commit subject line 72-char limit enforced (blog convention)

**Refinement (tier 4):**
- [ ] Could commit type guidance be expressed more briefly in CLAUDE.md?

### `framework` augmentations

**Quality:**
- [ ] Jekyll Liquid syntax is correct in `_layouts/` and `_includes/` files
- [ ] No deprecated Jekyll features used (e.g. `pygments`, removed `permalink` formats)
- [ ] Front matter schema in posts matches fields defined or expected by `_config.yml`

**Refinement (tier 4):**
- [ ] Could layout templates be simplified or better composed?

## Blog-Specific Categories (tier 3+)

### `blog-content` — Content Quality and Consistency

**Quality** — Is blog content consistent and correct?
- [ ] All posts have required front matter (title, date, layout at minimum)
- [ ] Post dates in front matter match filename dates
- [ ] No broken internal links between posts (posts referencing other posts by path)
- [ ] No images referenced in posts that don't exist in `assets/` or equivalent
- [ ] Draft posts are in `_drafts/` not `_posts/` (unless intentionally published)
- [ ] No post uses hardcoded relative links to other posts by date/title (breaks on rename)
- [ ] Archive pages (yearly/monthly) only exist for periods where posts actually exist

**Refinement (tier 4):**
- [ ] Are posts consistently categorised and tagged?
- [ ] Are there categories with only one post that could be merged with related ones?
- [ ] Could a series of related posts be better linked to each other?

### `blog-structure` — Site Structure

**Quality** — Is the Jekyll site structure correct?
- [ ] All layouts referenced in front matter exist in `_layouts/`
- [ ] All includes referenced in layouts exist in `_includes/`
- [ ] No orphaned layout or include files (defined but never referenced)
- [ ] Pagination configured correctly if enabled in `_config.yml`

**Refinement (tier 4):**
- [ ] Are there layouts that are nearly identical and could be merged with parameters?
- [ ] Could include files be better named or better organised?
- [ ] Are there images in `assets/` no longer referenced by any post or layout?
- [ ] Are there CSS or JavaScript files in `assets/` that are no longer used?

## Blog: Output Example

```
## project-health report — blog-content, blog-structure, primary-doc [augmented]

### HIGH (should fix)
- [blog][primary-doc] _posts/2026-01-15-intro.md: front matter missing 'layout' field
- [blog][blog-content] assets/images/diagram.png referenced in post but file does not exist

### MEDIUM (worth fixing)
- [blog][conventions] CLAUDE.md does not document blog commit type conventions

### LOW (nice to fix)
- [blog][blog-structure] _layouts/wide.html and _layouts/full.html are nearly identical

### PASS
✅ docs-sync, consistency, security, git
```

## Blog: Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Blog-specific checks don't replace universal ones | Always run universal checks first |
| Checking only `_posts/` root | Posts can be in subdirectories | Scan `_posts/` recursively |
| Treating draft in `_posts/` as error | May be intentionally published | Check `published: false` front matter before flagging |
| Flagging every unused asset | Images may be used by external links or layouts | Check layouts AND posts before calling an asset orphaned |
| Reporting Liquid errors without context | Template errors cascade | Report the root file first, note secondary effects separately |

**Related skills:** `blog-git-commit`, `project-refine`

---

---

# Custom

Type-specific health checks for type: custom projects — working groups, research
projects, advocacy, documentation sites. Run after universal checks complete (tier 3+).
Findings use `[custom]` prefix.

## Custom: Type-Specific Scan Targets

In addition to the universal document scan, include:

- The **Primary Document** path declared in `CLAUDE.md` (under `## Project Type`)
- All files matching patterns in the **Sync Rules** table in `CLAUDE.md`
- Any secondary documents referenced in the Sync Rules

Read `## Project Type` from CLAUDE.md first to discover these paths before
running any checks — they vary per project.

## Custom: Augmentations to Universal Checks

These extend universal categories with custom-project-specific items (tier 2+):

### `primary-doc` augmentations

**Quality:**
- [ ] Primary document (path from CLAUDE.md) reflects the current project state
- [ ] Sync Rules in CLAUDE.md still match the actual file structure

**Refinement (tier 4):**
- [ ] Is the primary document an appropriate size, or should it be modularised?

### `artifacts` augmentations

**Quality:**
- [ ] Primary Document path declared in CLAUDE.md exists on disk
- [ ] Current Milestone section is present and up to date
- [ ] Any secondary documents referenced in Sync Rules exist at their declared paths

**Refinement (tier 4):**
- [ ] Could milestone tracking be simpler or expressed more compactly?

### `conventions` augmentations

**Quality:**
- [ ] Sync Rules are configured in CLAUDE.md (`## Project Type` → Sync Rules table)
- [ ] Sync Rules match actual workflow and file patterns in the repository

**Refinement (tier 4):**
- [ ] Could Sync Rules be expressed more concisely without losing fidelity?
- [ ] Are any Sync Rules never triggered in practice?

### `framework` augmentations

**Quality:**
- [ ] Sync patterns in rules match the declared sync strategy (e.g. `bidirectional-consistency`, `research-progress`)
- [ ] No Sync Rule references a file pattern that matches zero files

**Refinement (tier 4):**
- [ ] Could any Sync Rules be merged or simplified?

## Custom-Specific Categories (tier 3+)

### `sync-rules` — Sync Rule Health

**Quality** — Are the Sync Rules in CLAUDE.md correct and complete?
- [ ] Every file pattern in Sync Rules matches at least one actual file
- [ ] Every document section referenced in Sync Rules exists in the primary document
- [ ] No Sync Rules reference files that have been renamed or removed
- [ ] The sync strategy matches actual usage (declared strategy vs observed commit patterns)
- [ ] Current Milestone reflects the actual phase of the project
- [ ] No two Sync Rules match overlapping file patterns without clear precedence

**Refinement (tier 4):**
- [ ] Are there rules that overlap or could be merged into one?
- [ ] Are any rules so broad they match files they shouldn't?
- [ ] Could the primary document be restructured to make Sync Rules simpler?
- [ ] Are there common types of changes not captured by any rule?

### `project-currency` — Is the Project Current?

**Quality** — Does the project reflect its actual current state?
- [ ] Primary document milestone matches the actual current phase
- [ ] No sections describe work that has been completed but is still marked as planned
- [ ] No participants listed who are no longer active (if participant lists exist)
- [ ] Referenced external documents, tools, or systems still exist and are accessible
- [ ] No completed work items remain marked as "planned" or "in progress"
- [ ] External tool links (Notion, Figma, Jira, etc.) are reachable and point to current content

**Refinement (tier 4):**
- [ ] Could the primary document be reorganised to surface current work more prominently?
- [ ] Are historical phases cluttering the document and making it harder to navigate?

## Custom: Output Example

```
## project-health report — sync-rules, project-currency, primary-doc [augmented]

### CRITICAL (must fix)
- [custom][artifacts] Primary Document path 'docs/vision.md' declared in CLAUDE.md does not exist

### HIGH (should fix)
- [custom][sync-rules] Sync Rule pattern 'catalog/*.md' matches no files — directory may have been renamed
- [custom][project-currency] Milestone says "Phase 1 - Discovery" but Phase 2 work is underway

### MEDIUM (worth fixing)
- [custom][sync-rules] Two rules both match 'docs/meetings/' — consolidate to one rule

### LOW (nice to fix)
- [custom][project-currency] External Figma link in primary doc returns 404

### PASS
✅ docs-sync, consistency, security, git, conventions
```

## Custom: Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Custom-specific checks don't replace universal ones | Always run universal checks first |
| Reporting stale Sync Rules without checking | Rules may be intentionally broad or future-dated | Check if the pattern ever matched before flagging as stale |
| Flagging milestone mismatch without context | Project may be mid-transition between phases | Note the discrepancy, ask user if flag is appropriate |
| Checking only CLAUDE.md, not the primary doc | Primary doc may have drifted even if CLAUDE.md is current | Always read both and compare |
| Treating absent external links as CRITICAL | External tools go offline temporarily | Flag as MEDIUM unless the linked content is referenced by active workflows |

**Related skills:** `custom-git-commit`, `update-primary-doc`, `project-refine`
