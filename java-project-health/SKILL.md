---
name: java-project-health
description: >
  Use when health-checking a type: java (Java/Maven/Gradle) project, or when
  invoked automatically by project-health on java project type detection.
---

# java-project-health

Health checks for Java/Maven/Gradle projects. Runs all universal checks from
`project-health` first, then adds Java-specific checks for architecture
integrity, dependency alignment, and code quality.

Follows the same pattern as `java-git-commit` extending `git-commit`.

## Prerequisites

**This skill builds on `project-health`.** Apply all universal checks first:

- All universal categories: `docs-sync`, `consistency`, `logic`, `config`,
  `security`, `release`, `user-journey`, `git`, `primary-doc`, `artifacts`,
  `conventions`, `framework`
- Same tier system (1–4) and named aliases (`--commit`, `--standard`,
  `--prerelease`, `--deep`)
- Same output format — Java-specific findings are prefixed with `[java]`

When invoked directly (`/java-project-health`), run universal checks first,
then Java-specific checks. Output is combined — identical to `project-health`
auto-chaining here.

---

## Tier System

Inherited from `project-health` — see [check-categories.md](../project-health/check-categories.md#tier-system).
Java-specific categories (`java-architecture`, `java-dependencies`, `java-code-quality`) run at tier 3+.

---

## Type-Specific Scan Targets

In addition to the universal document scan, include:

- `pom.xml` (root and all module POMs)
- `build.gradle` / `build.gradle.kts` (if Gradle)
- `src/main/java/` — all `.java` source files
- `src/test/java/` — all test source files
- Javadoc comments in source files (relevant for `docs-sync` and `conventions`)
- `src/main/resources/application.properties` / `application.yaml`

---

## Augmentations to Universal Checks

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
- [ ] `docs/DESIGN.md` exists (required by `java-git-commit` workflow)
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

---

## Java-Specific Categories

These categories are only checked for type: java projects (tier 3+).

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

---

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

---

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

---

## Output Format

Universal findings appear without a prefix. Java-specific findings use `[java]`:

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

Severity scale: see [check-categories.md](../project-health/check-categories.md#severity-scale).

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Skipping universal checks | Java-specific checks don't replace universal ones | Always run universal checks first (prerequisite) |
| Flagging `@Blocking` on every service method | Only I/O-bound methods on the event loop need it | Check whether the method actually performs blocking I/O |
| Calling a utility class a "mini-service" | Utility classes without state are fine | Only flag if a utility class has grown state or lifecycle concerns |
| Reporting BOM override as a bug without context | Overrides can be intentional | Check for a documented reason (comment in pom.xml or DESIGN.md) |
| Treating every code similarity as duplication | Some patterns are intentionally repeated per layer | Flag only identical logic blocks (3+) that diverge silently on bug fixes |
| Flagging an `@Entity` in a DTO as a violation | The concern is `@Entity` used AS the API type | Separate DTO classes that happen to share field names are fine |

---

## Skill Chaining

**Invoked by:** `project-health` automatically when `type: java` detected in CLAUDE.md

**Can be invoked directly:** Yes — `/java-project-health` runs universal checks first,
then Java-specific checks, producing identical output to the auto-chained flow

**Prerequisite for:** Nothing currently chains from this skill

**Related skills:**
- `project-health` — universal prerequisite foundation
- `java-git-commit` — Java commit skill; requires `docs/DESIGN.md` (validates here under `artifacts`)
- `java-code-review` — per-PR code review; `java-project-health` is for whole-project health
- `java-update-design` — DESIGN.md sync; `primary-doc` findings here often indicate a sync is overdue
- `maven-dependency-update` — dependency upgrades; `java-dependencies` findings here often indicate upgrades needed
- `project-refine` — companion for improvement opportunities after health is green
