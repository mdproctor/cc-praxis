# 0002 — OOPath runtime as pipeline on RuleDefinition

Date: 2026-04-05
Status: Accepted

## Context and Problem Statement

OOPath traversal (`pathN()` methods) produces correlated tuples: for each root
fact, traverse nested collections to produce `TupleN` results. This is
fundamentally different from existing sources which are independent of the
current fact combination. The sandbox needed a runtime execution model without
breaking the existing `TupleSource` abstraction.

## Decision Drivers

* Existing `TupleSource` interface and `matchedTuples()` pipeline must remain unchanged
* OOPath execution must be self-contained and independently testable
* Sandbox simplicity preferred over full Rete beta-memory fidelity
* `RuleDefinition` must remain the single execution entry point

## Considered Options

* **Option A** — Add a separate OOPath pipeline (`ooPathRootIndex` + `ooPathSteps` list) to `RuleDefinition`; `matchedTuples()` switches to correlated execution mode when the pipeline is set
* **Option B** — Generalise `TupleSource` to `(ctx, currentFacts[]) → List<Object[]>` so OOPath sources can depend on the current partial fact combination
* **Option C** — PathN builders pre-compute the traversal plan and register a lazy executor; `RuleDefinition` never sees OOPath internals

## Decision Outcome

Chosen option: **Option A**, because it is the most isolated change — no
modifications to `TupleSource`, existing sources, or the standard cross-product
loop. OOPath is purely additive: the new mode fires only when `ooPathRootIndex >= 0`.
The correlated execution (for each outer combination, run the pipeline from the
root fact) is self-contained, easy to test in isolation, and does not affect
any existing code path.

### Positive Consequences

* Zero changes to the existing `TupleSource`/`matchedTuples()` pipeline
* OOPath mode is additive and clearly isolated
* Easy to unit-test: set `ooPathRootIndex` and `ooPathSteps` directly
* `copyTuple()` at the leaf prevents sibling-branch mutation of collected results

### Negative Consequences / Tradeoffs

* A `RuleDefinition` can currently have either regular sources OR an OOPath pipeline, not both mixed in arbitrary positions — limitation if complex hybrid rules are needed later
* Pipeline is registered at `PathN.path()` chain completion, coupling builder chain order to execution model

## Pros and Cons of the Options

### Option A — Separate OOPath pipeline on RuleDefinition

* ✅ No changes to existing `TupleSource` interface or any consumer
* ✅ Self-contained, easy to reason about
* ❌ Can't mix OOPath mid-chain with regular sources in arbitrary positions

### Option B — Generalise TupleSource to be correlated

* ✅ Elegant unification of all source types under one abstraction
* ❌ Breaks existing sources (must accept and ignore `currentFacts` parameter)
* ❌ Increases complexity of all existing source implementations

### Option C — Lazy executor in PathN builders

* ✅ `RuleDefinition` stays completely unchanged
* ❌ Complex deferred execution model hard to reason about
* ❌ Unclear when the pipeline is actually registered and executed

## Links

* Spec: [`docs/superpowers/specs/2026-04-05-phase3b-oopath.md`](../superpowers/specs/2026-04-05-phase3b-oopath.md)
