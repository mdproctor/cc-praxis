# ADR-0006: Generic Principles Foundation Skills

**Status:** Accepted

**Date:** 2026-03-30

**Context:** Universal extensibility model for multi-language support

---

## Decision

Establish two-tier skill architecture: generic foundation skills (language-agnostic principles) extended by language/tool/framework-specific implementations.

**Foundation skills (generic, suffix `-principles`):**
- `code-review-principles`
- `security-audit-principles`
- `dependency-management-principles`
- `observability-principles`

**Extension skills (specific, prefixed `language-*`, `tool-*`, `framework-*`):**
- `java-code-review` (extends code-review-principles)
- `java-security-audit` (extends security-audit-principles)
- `maven-dependency-update` (extends dependency-management-principles)
- `quarkus-observability` (extends observability-principles)

---

## Context

### The Problem

Early skill implementations were language-specific only:

```
java-code-review/
  - Safety checks
  - Concurrency patterns
  - Review workflow
  - Java-specific: NullPointerException, Stream API, Optional

java-security-audit/
  - OWASP Top 10
  - SQL injection
  - XSS prevention
  - Java-specific: PreparedStatement, CSRF tokens
```

**What this meant for extensibility:**
- Adding Python support → duplicate all code review logic
- Adding Go support → duplicate all security audit logic
- Adding Rust support → duplicate all dependency management logic
- Result: N languages × M skill types = massive duplication

**Concrete example:**
```
OWASP Top 10 is language-agnostic:
- Injection (applies to all languages)
- Broken authentication (applies to all languages)
- XSS (applies to web applications in any language)

But we had it ONLY in java-security-audit.

To add Python: copy all OWASP principles, just change the examples.
```

**The insight:** Principles are universal, examples are language-specific.

## Decision Drivers

- **Avoid duplication** - OWASP Top 10 is the same for Python/Java/Go/Rust
- **Enable multi-language** - Want to support Python, Go, Rust, JavaScript
- **Maintainability** - Fix OWASP principle once, all languages benefit
- **Discoverability** - Foundation skills can be referenced standalone
- **Consistency** - Same review principles across all languages
- **Extensibility** - New languages = reference foundations + add examples

## Considered Options

### Option 1: Keep Everything Language-Specific (REJECTED)

**Approach:** java-code-review, python-code-review, go-code-review, etc., each standalone

**Pros:**
- Self-contained (everything in one place)
- No cross-references needed

**Cons:**
- ❌ Massive duplication (same principles repeated N times)
- ❌ Maintenance nightmare (fix bug in one, must fix in all)
- ❌ Inconsistency (principles drift across languages)
- ❌ Doesn't scale (10 languages × 5 skill types = 50 duplicated skills)
- ❌ Can't reference principles standalone

### Option 2: Make Everything Generic (REJECTED)

**Approach:** One code-review skill for all languages

**Pros:**
- Zero duplication
- Easy to maintain

**Cons:**
- ❌ Loses language-specific examples
- ❌ Can't provide concrete patterns (NullPointerException vs panic!() vs None)
- ❌ Too abstract (users need specific guidance)
- ❌ Token waste (loads irrelevant language examples)

### Option 3: Two-Tier Architecture - Generic Foundations + Specific Extensions (ACCEPTED)

**Approach:**

**Tier 1: Generic Principles** (language-agnostic)
```markdown
# code-review-principles/SKILL.md

## Safety
- Check for null/nil/None dereferencing
- Validate array bounds
- Handle errors explicitly

## Concurrency
- Check for data races
- Verify synchronization
- Look for deadlocks
```

**Tier 2: Language-Specific Extensions** (concrete examples)
```markdown
# java-code-review/SKILL.md

## Prerequisites

**This skill builds on `code-review-principles`**. Apply all rules from:
- **code-review-principles**: Safety, concurrency, performance, testing

## Java-Specific Additions

### Safety
- NullPointerException (use Optional, @NonNull, Objects.requireNonNull)
- ArrayIndexOutOfBoundsException (use enhanced for-loop, .length checks)
- Stream terminal operations (check .orElse(), .orElseThrow())

### Concurrency
- synchronized blocks (prefer j.u.c locks for flexibility)
- volatile vs AtomicReference (visibility guarantees)
- CompletableFuture error handling (always .exceptionally() or .handle())
```

**Pros:**
- ✅ Zero duplication (principles once, examples in specific skills)
- ✅ Maintainable (fix principle once, all languages benefit)
- ✅ Extensible (new language = reference foundation + add examples)
- ✅ Discoverable (can reference foundation skills standalone)
- ✅ Consistent (same principles across languages)
- ✅ Concrete (language skills provide specific patterns)

**Cons:**
- ⚠️ More files (2 files instead of 1 per language)
- ⚠️ Cross-references (must maintain Prerequisites sections)
- ⚠️ Loading overhead (2 skills loaded instead of 1)

## Decision Outcome

**Chosen option:** Two-Tier Architecture - Generic Foundations + Specific Extensions

**Implementation:**

### 1. Foundation Skills Created

**Generic principles (never invoked directly, only referenced):**

| Skill | Coverage |
|-------|----------|
| `code-review-principles` | Safety, concurrency, performance, testing, review workflow |
| `security-audit-principles` | OWASP Top 10, input validation, authentication, authorization |
| `dependency-management-principles` | BOM patterns, version alignment, compatibility |
| `observability-principles` | Logging, tracing, metrics, MDC patterns |

**Naming convention:** `-principles` suffix

### 2. Extension Skills Created

**Language/tool/framework-specific (invoked by users):**

| Skill | Extends | Adds |
|-------|---------|------|
| `java-code-review` | `code-review-principles` | Java-specific: NullPointerException, Stream API, Optional |
| `java-security-audit` | `security-audit-principles` | Java-specific: PreparedStatement, CSRF tokens, @Validated |
| `maven-dependency-update` | `dependency-management-principles` | Maven-specific: pom.xml, BOM alignment, quarkus-bom |
| `quarkus-observability` | `observability-principles` | Quarkus-specific: application.properties, Micrometer, Panache |

**Naming convention:** `language-*`, `tool-*`, `framework-*` prefix

### 3. Cross-Reference Pattern

**Via Prerequisites sections:**
```markdown
## Prerequisites

**This skill builds on `code-review-principles`**. Apply all rules from:
- **code-review-principles**: Safety, concurrency, performance, testing

**Java-specific additions below.**
```

### 4. Extensibility Pattern for New Languages

**Adding Python support:**

1. **Reference existing foundations** (already done):
   - `code-review-principles` ✓
   - `security-audit-principles` ✓
   - `dependency-management-principles` ✓
   - `observability-principles` ✓

2. **Create Python-specific extensions:**
   ```
   python-code-review/
     Prerequisites: code-review-principles
     Adds: AttributeError, IndexError, None checks, type hints

   python-security-audit/
     Prerequisites: security-audit-principles
     Adds: SQL injection with SQLAlchemy, XSS with Jinja2

   pip-dependency-update/
     Prerequisites: dependency-management-principles
     Adds: requirements.txt, setup.py, Poetry, Pipenv

   python-observability/
     Prerequisites: observability-principles
     Adds: logging module, structlog, OpenTelemetry Python
   ```

3. **Zero duplication** - OWASP Top 10, BOM patterns, review workflow already covered

**Same pattern for Go, Rust, JavaScript, etc.**

## Consequences

### Positive

✅ **Zero duplication** - Principles written once, used by all languages
✅ **Easy to extend** - New language = reference + add examples (~200 lines vs ~1000 lines)
✅ **Maintainable** - Fix OWASP principle once, Python/Java/Go all benefit
✅ **Consistent** - Same review standards across all languages
✅ **Discoverable** - Foundation skills stand alone (can read principles without language context)
✅ **Scalable** - 10 languages × 4 foundation skills = 40 references, not 40 duplicates

### Negative

⚠️ **More files** - 2 skills per language (foundation + extension) vs 1
⚠️ **Cross-references** - Must maintain Prerequisites sections (bidirectional)
⚠️ **Loading overhead** - 2 skills loaded (foundation + extension) vs 1
⚠️ **Complexity** - Need to understand two-tier architecture

### Neutral

📝 **Foundation skills never invoked directly** - Only referenced via Prerequisites
📝 **Naming makes tier explicit** - `-principles` suffix = foundation, `language-*` prefix = extension
📝 **Can evolve foundations** - Add new principle, all languages inherit automatically

## Validation

Success criteria for this ADR:

- ✅ All foundation skills created (4 total)
- ✅ All Java extensions reference foundations via Prerequisites
- ✅ Zero duplication of principles across languages
- ✅ Naming convention consistent (`-principles` suffix, `language-*` prefix)
- ✅ Pattern documented for future languages
- ✅ Foundation skills never invoked directly (checked via skill-review)

## Extensibility Examples

### Python (Future)

```markdown
# python-code-review/SKILL.md

## Prerequisites

**This skill builds on `code-review-principles`**. Apply all rules from:
- **code-review-principles**: Safety, concurrency, performance, testing

## Python-Specific Additions

### Safety
- AttributeError (check hasattr(), getattr() with default)
- IndexError (use slicing [:], len() checks)
- None checks (use `if x is not None`, avoid `if x`)
- Type hints (use mypy, check Optional[T])

### Concurrency
- GIL awareness (CPU-bound vs IO-bound)
- asyncio patterns (await, gather, ensure_future)
- Threading vs multiprocessing (when to use each)
```

### Go (Future)

```markdown
# go-code-review/SKILL.md

## Prerequisites

**This skill builds on `code-review-principles`**. Apply all rules from:
- **code-review-principles**: Safety, concurrency, performance, testing

## Go-Specific Additions

### Safety
- panic() usage (only for programmer errors, not user errors)
- nil pointer dereferencing (check != nil)
- slice bounds (use len(), cap())
- error handling (never ignore err return values)

### Concurrency
- goroutine leaks (always provide exit path)
- channel deadlocks (buffered vs unbuffered)
- race detector (run with -race flag)
- sync.WaitGroup (call Done() in defer)
```

## Related Decisions

- **ADR-0002:** Project-Type-Specific Skills Must Use Type Prefix (same extensibility principle)
- **Naming Conventions (CLAUDE.md)** - Established `-principles` suffix, `language-*` prefix pattern
- **Skill Chaining** - Foundation skills referenced via Prerequisites, not invoked

## Notes

**What we learned:**

Principles are language-agnostic, implementations are language-specific. Separating these concerns enables:
- Code reuse (principles once)
- Language specificity (examples in context)
- Easy extension (new language = reference + examples)

**Key insight:**
> "OWASP Top 10 is the same for Python and Java. Only the examples differ."

**Analogy:**
- Foundation skill = Design pattern (Observer, Strategy, Factory)
- Extension skill = Implementation in a specific language (Java Observer, Python Observer)

**Refactoring that established this:**

Commit `7221ad0` - refactor(skills): extract generic principles and rename for clarity

Before:
```
java-code-review/ (everything)
```

After:
```
code-review-principles/ (universal)
java-code-review/ (Java-specific, references code-review-principles)
```

**Result:** Can now add python-code-review, go-code-review, etc. with ~200 lines each instead of ~1000 lines duplicating principles.

**Future-proofing:**
This pattern scales to any number of languages. Adding language #10 is as easy as adding language #2 - just reference the foundations and add language-specific examples.
