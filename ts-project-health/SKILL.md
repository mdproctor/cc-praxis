---
name: ts-project-health
description: >
  Use when a TypeScript or Node.js project needs a health review. Invoked
  directly via /ts-project-health or suggested by project-health. Extends
  project-health with TypeScript-specific categories.
---

# ts-project-health

Health checks for TypeScript/Node.js projects. Runs all universal checks from
`project-health` first, then adds TypeScript-specific checks for type safety,
async patterns, build integrity, dependency health, and test coverage.

Follows the same pattern as `java-project-health` extending `project-health`.

## Prerequisites

**This skill builds on `project-health`.** Apply all universal checks first:

- All universal categories: `docs-sync`, `consistency`, `logic`, `config`,
  `security`, `release`, `user-journey`, `git`, `primary-doc`, `artifacts`,
  `conventions`, `framework`
- Same tier system (1–4) and named aliases (`--commit`, `--standard`,
  `--prerelease`, `--deep`)
- Same output format — TypeScript-specific findings are prefixed with `[ts]`

When invoked directly (`/ts-project-health`), run universal checks first,
then TypeScript-specific checks. Output is combined — identical to
`project-health` auto-chaining here.

---

## Tier System

Inherited from `project-health` — see [check-categories.md](../project-health/check-categories.md#tier-system).
TypeScript-specific categories (`ts-types`, `ts-async`, `ts-build`, `ts-dependencies`, `ts-testing`) run at tier 3+.

---

## Type-Specific Scan Targets

In addition to the universal document scan, include:

- `tsconfig.json` / `tsconfig.*.json` (all variants)
- `package.json` + lock file (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`)
- `src/**/*.ts`, `src/**/*.tsx` — all TypeScript source files
- Test files: `**/*.test.ts`, `**/*.spec.ts`, `**/__tests__/**`
- `.eslintrc.*` / `eslint.config.*` — linter configuration
- `jest.config.*` / `vitest.config.*` — test runner configuration

---

## Augmentations to Universal Checks

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

---

## TypeScript-Specific Categories

These categories are only checked for type: ts projects (tier 3+).

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

---

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

---

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

---

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

---

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

---

## Output Format

Universal findings appear without a prefix. TypeScript-specific findings use `[ts]`:

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

Severity scale: see [check-categories.md](../project-health/check-categories.md#severity-scale).

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | TypeScript-specific checks don't replace universal ones | Always run universal checks first (prerequisite) |
| Flagging all `any` as CRITICAL equally | Legacy codebases accumulate `any` legitimately; new code is different | Flag `any` in new/changed code as HIGH; documented legacy `any` as LOW |
| Reporting a floating promise without verifying it's truly unhandled | Some patterns intentionally fire-and-forget with error logging elsewhere | Trace the call site — confirm no `.catch()` or top-level handler exists |
| Treating `// @ts-ignore` as always wrong | Sometimes external library types are incorrect and `@ts-ignore` is the only option | Flag only when there is no explanatory comment; an explained ignore is acceptable |
| Flagging `devDependencies` separation without checking actual usage | A package listed under `dependencies` may be intentionally bundled | Verify the package is unused at runtime before flagging it as miscategorised |
| Calling skipped tests a CRITICAL finding | Skipped tests slow down quality but don't break production | Severity is LOW unless the skip count is high (>10% of suite) or skips are undocumented |

---

## Skill Chaining

**Invoked by:** User directly via `/ts-project-health`, or by `project-health` if `type: ts` is configured in CLAUDE.md (TypeScript is not a built-in project type; see `docs/PROJECT-TYPES.md` for supported types)

**Can be invoked directly:** Yes — `/ts-project-health` runs universal checks first,
then TypeScript-specific checks, producing identical output to the auto-chained flow

**Prerequisite for:** Nothing currently chains from this skill

**Related skills:**
- `project-health` — universal prerequisite foundation
- `ts-dev` — TypeScript development skill; `ts-project-health` catches issues that accumulate between sessions
- `ts-code-review` — per-PR code review; `ts-project-health` is for whole-project health
- `npm-dependency-update` — dependency upgrades; `ts-dependencies` findings here often indicate upgrades needed
- `project-refine` — companion for improvement opportunities after health is green
