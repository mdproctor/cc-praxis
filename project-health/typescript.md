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
