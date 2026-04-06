# 0004 — NegationScope as separate builder class, not JoinNSecond subtype

Date: 2026-04-05
Status: Accepted

## Context and Problem Statement

Implementing `not()`/`exists()` scopes required a builder that: (a) accumulates
sources and filters into a private sub-network `RuleDefinition`, and (b) returns
the typed outer builder via `end()`. The real Drools uses `Not2 extends Group2 extends Join2Second`.
The sandbox needed to decide whether to match this inheritance or use a simpler
separate class.

## Decision Drivers

* The not-scope `rd` must be separate from the outer chain's `rd` — scope sources must not pollute the outer chain
* `end()` must return the correctly typed outer builder
* Inside the scope, `join()` must add to the scope `rd`, not the outer `rd`
* Sandbox simplicity favoured over structural fidelity to Drools

## Considered Options

* **Option A** — `NegationScope<OUTER, DS>` as a standalone class with its own `notRd`; `join()` and `filter()` are intentionally untyped; `end()` returns `OUTER`
* **Option B** — `Not2<END, DS, B, C>` extending `Join2Second<END, DS, B, C>` matching real Drools structure exactly
* **Option C** — Inline not-scope as a lambda or anonymous builder without a named class

## Decision Outcome

Chosen option: **Option A**, because the inheritance approach (Option B) creates
an irresolvable `rd` conflict: `Join2Second` has one `rd` field, and `Not2`
inheriting it means `join()` inside the not-scope would add to the outer `rd`
instead of the scope's private `rd`. Separating into a standalone class
eliminates this conflict cleanly. The cost is reduced type-safety inside the
scope (untyped `join()`), which is acceptable for a constraint builder whose
purpose is negation, not typed fact accumulation.

### Positive Consequences

* Clear separation between scope `rd` and outer `rd` — no conflict
* `end()` returns the correctly typed outer builder; outer chain resumes fully typed
* Simple to implement and reason about
* `NegationScope.join(Function<DS, DataSource<?>> source)` is clean (typed enough for the lambda case)

### Negative Consequences / Tradeoffs

* Inside the not-scope, `join()` is less typed than the main chain — doesn't enforce the child element type
* Structural divergence from real Drools (`Not2 extends Join2Second`)
* Cross-referencing outer facts inside scope filters requires `Variable<T>` (not yet implemented)

## Pros and Cons of the Options

### Option A — Standalone NegationScope class

* ✅ No `rd` conflict — scope `rd` and outer `rd` are completely separate
* ✅ Simple, easy to understand and test
* ❌ Untyped `join()` inside the scope
* ❌ Structural divergence from real Drools

### Option B — Not2 extending Join2Second (Drools pattern)

* ✅ Exact structural match with real Drools
* ❌ Inherits outer `rd` via `Join2Second`; `join()` inside scope adds to wrong `rd`
* ❌ Requires overriding `join()` and all other `rd`-writing methods to redirect — complex and fragile

### Option C — Inline lambda/anonymous builder

* ✅ No new named class
* ❌ Cannot carry a typed `end()` return
* ❌ Non-discoverable API; no place to attach documentation

## Links

* Spec: [`docs/superpowers/specs/2026-04-05-phase3a-not-exists.md`](../superpowers/specs/2026-04-05-phase3a-not-exists.md)
