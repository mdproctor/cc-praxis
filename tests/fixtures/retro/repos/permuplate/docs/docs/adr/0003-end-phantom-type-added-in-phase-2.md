# 0003 — END phantom type added alongside First/Second split, not with not()/exists()

Date: 2026-04-05
Status: Accepted

## Context and Problem Statement

The `END` phantom type parameter (enabling typed `end()` returns from nested
scopes like `not()`, `exists()`) is required in Phase 3 for not()/exists()
scopes. The question was whether to add it proactively in Phase 2 alongside
the First/Second split, or defer it to Phase 3 when actually needed.

## Decision Drivers

* Adding `END` later requires changing every generated class signature — a breaking API change
* Every test call site with explicit type references would need retroactive updating
* `not()` and `exists()` are planned Phase 3 features; the infrastructure should be ready without a breaking change
* The real Drools `RuleBuilder` has `END` on every generated class

## Considered Options

* **Option A** — Add `END` in Phase 2 alongside the First/Second split (proactive)
* **Option B** — Add `END` in Phase 3 when `not()`/`exists()` actually require it (just-in-time)

## Decision Outcome

Chosen option: **Option A**, because adding `END` later forces a retroactive
breaking change across all generated class signatures and every explicit type
reference in tests. The upfront cost is moderate (one extra `Void` in type
signatures, `null` in constructors for top-level rules) while the deferred
cost is proportionally much higher — and the real Drools has had `END` from
the start.

### Positive Consequences

* Phase 3 `not()`/`exists()` can use `END` without any API breakage
* Generated classes match real Drools signatures from the start
* Tests using `var` are entirely unaffected (most existing tests)

### Negative Consequences / Tradeoffs

* Adds `Void` to explicit type references (`JoinBuilder.Join1First<Void, DS, A>`)
* Constructor calls become `new Join1First<>(null, rd)` instead of `new Join1First<>(rd)`
* Slightly increases complexity of the Phase 2 First/Second split implementation

## Pros and Cons of the Options

### Option A — Add END in Phase 2 (proactive)

* ✅ Zero breaking change when Phase 3 arrives
* ✅ Matches real Drools signatures from the start
* ❌ Minor upfront verbosity cost

### Option B — Add END in Phase 3 (just-in-time)

* ✅ Simpler Phase 2 implementation
* ❌ Phase 3 requires changing every generated class signature — a breaking API change
* ❌ Every explicit type reference in tests needs retroactive updating
* ❌ Diverges from real Drools longer than necessary

## Links

* Spec: [`docs/superpowers/specs/2026-04-05-phase2-first-second-split.md`](../superpowers/specs/2026-04-05-phase2-first-second-split.md)
