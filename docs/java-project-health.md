# java-project-health — Design Document

**Status:** Design phase — not yet implemented as a skill
**Skill name (planned):** `java-project-health`
**Slash command (planned):** `/java-project-health`
**Invoked by:** [`project-health`](project-health.md) when `type: java` declared in CLAUDE.md

This document tracks the Java-specific health checks that augment the universal checks in `project-health`.

---

## Purpose

Runs after `project-health` completes its universal checks. Adds Java/Maven/Gradle-specific correctness and refinement checks that only make sense for Java projects.

Follows the same pattern as `java-git-commit` extending `git-commit`.

---

## Prerequisite

**This skill builds on [`project-health`](project-health.md).** All universal checks run first. This skill adds Java-specific checks on top.

---

## Augmentations to Universal Checks

These extend the universal categories with Java-specific items:

| Universal check | Quality additions | Refinement additions |
|----------------|------------------|---------------------|
| `primary-doc` | DESIGN.md exists and reflects current architecture; no stale entity/service/repository references | Could DESIGN.md be split into focused modules (architecture, API, data model)? |
| `artifacts` | `docs/DESIGN.md` exists (java-git-commit blocks without it) | Is DESIGN.md appropriately sized, or has it grown beyond a single file? |
| `conventions` | BOM strategy documented; commit scopes consistent (rest/service/repository/bom/config) | Could BOM documentation be more concise? Are scope conventions clear? |
| `framework` | No blocking JDBC on Vert.x event loop; @Blocking annotations correct; CDI injection patterns correct; no raw JDBC outside repositories | Could Quarkus/Vert.x concurrency guidance be better grouped? |

---

## Java-Specific Categories

These categories only exist for Java projects and are not present in `project-health`:

### `java-architecture` — Architecture Integrity

**Quality** — Is the Java architecture clean and consistent?
- [ ] Layer separation respected (no direct calls from controller to repository)
- [ ] Domain model classes are not leaking into API layer
- [ ] @Entity classes are not used as API request/response types
- [ ] No circular imports between packages
- [ ] Service classes do not hold mutable state shared across requests

**Refinement** — Could the architecture be simpler or better expressed?
- [ ] Are there service classes doing too many things that could be split?
- [ ] Are there utility classes that have grown into mini-services?
- [ ] Could any layer boundaries be made clearer through package structure?

### `java-dependencies` — Maven/Gradle Dependency Health

**Quality** — Are dependencies correct and aligned?
- [ ] All dependencies in BOM — no explicit versions where BOM manages them
- [ ] No version overrides without documented reason
- [ ] No duplicate dependencies via transitive resolution
- [ ] Test dependencies scoped correctly (not leaking to runtime)
- [ ] `annotationProcessorPaths` includes all required processors

**Refinement** — Could the dependency structure be leaner?
- [ ] Are there dependencies used in only one place that could be removed?
- [ ] Are there large dependencies used for one small feature?
- [ ] Could test utilities be consolidated to reduce test dependency sprawl?

---

## Output Format

Same severity rating as `project-health`, prefixed with `[java]`:

```
### HIGH (should fix)
- [java][framework] OrderService.findAll() makes JDBC call on Vert.x event loop — add @Blocking
- [java][java-architecture] PaymentController calls PaymentRepository directly, bypassing service layer
```
