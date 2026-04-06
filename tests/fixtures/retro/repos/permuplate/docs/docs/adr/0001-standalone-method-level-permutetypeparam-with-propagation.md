# 0001 — Standalone method-level @PermuteTypeParam with rename propagation

Date: 2026-04-05
Status: Accepted

## Context and Problem Statement

Permuplate's `@PermuteTypeParam` annotation could only expand type parameters
inside `@PermuteMethod`. Making `join()` fully typed required renaming a method
type parameter (`<B>`) to the next alpha letter per arity AND propagating that
rename into parameter types (e.g. `DataSource<B>` → `DataSource<C>`). Without
this, `join()` returned a raw type and callers required pre-typed constants,
`@SuppressWarnings`, and explicit casts.

## Decision Drivers

* Drools DSL `join()` must be fully typed at every arity — matching the real Drools pattern
* Template must remain valid compilable Java with no annotation noise on parameters
* Propagation into parameter types should be automatic (no `@PermuteDeclr` required)
* `@PermuteMethod` methods must be guarded against double-processing with the wrong inner context

## Considered Options

* **Option A** — Extend `PermuteTypeParamTransformer.transform()` with Step 5 for non-`@PermuteMethod` methods + word-boundary-safe propagation inside `transformMethod()`
* **Option B** — Use `@PermuteMethod` with a degenerate range (`from="${i}" to="${i}"`) as a hack to trigger method-level processing
* **Option C** — Keep `Object` parameter type with explicit casts at every call site

## Decision Outcome

Chosen option: **Option A**, because it is the clean, correct extension of the
existing transformer. Step 5 scans non-`@PermuteMethod` methods for the
annotation and processes them with the outer context. Propagation inside
`transformMethod()` uses word-boundary-safe string replacement so `DataSource<B>`
becomes `DataSource<C>` automatically. `@PermuteDeclr` on a parameter always
overrides propagation. `@PermuteMethod` methods are explicitly guarded to prevent
double-processing with the wrong (outer-only) context.

### Positive Consequences

* `join()` is fully typed — no casts, no `@SuppressWarnings`, no pre-typed constants
* Template remains valid Java with no annotation noise on parameters
* Multi-value expansions (`from < to`) correctly skip propagation (no single rename target)
* Works in both APT and Maven plugin modes (shared transformer)

### Negative Consequences / Tradeoffs

* Required fixing a pre-existing `String.replace()` bug in `buildTypeParam()` bounds substitution (now uses word-boundary-safe `replaceTypeIdentifier()`)
* Multi-value expansions leave parameter types stale — callers must use `@PermuteDeclr` explicitly for those parameters
* Adds complexity to `PermuteTypeParamTransformer` (Step 5 guard logic)

## Pros and Cons of the Options

### Option A — Extend transformer with Step 5 + propagation

* ✅ Clean, correct implementation — no hacks
* ✅ Propagation eliminates annotation noise at every call site
* ✅ Works in both APT and Maven plugin modes
* ❌ Required fixing a pre-existing bounds-substitution bug

### Option B — @PermuteMethod degenerate range hack

* ✅ No transformer changes needed
* ❌ Misuses `@PermuteMethod` semantically (single-iteration "loop" just to trigger processing)
* ❌ Requires inner variable even though it's unused

### Option C — Object parameter with casts

* ✅ No Permuplate changes
* ❌ Every call site needs ugly double-cast: `(Object)(Function<DS,DataSource<Account>>) ctx -> ctx.accounts()`
* ❌ Defeats the type-safety goal entirely

## Links

* Spec: [`docs/superpowers/specs/2026-04-04-method-type-param-propagation.md`](../superpowers/specs/2026-04-04-method-type-param-propagation.md)
