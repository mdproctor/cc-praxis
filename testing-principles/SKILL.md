---
name: testing-principles
description: >
  Use when a language-specific dev or testing skill (e.g. java-dev, ts-dev,
  python-dev) references this as a Prerequisites foundation for test strategy.
  NOT invoked directly by users — only loaded via Prerequisites by
  language/framework-specific skills.
---

# Testing Principles

Universal test strategy foundation. Language-specific skills extend these rules
with framework and tooling specifics.

**Scope:** These principles govern *what kinds* of tests to write and *whether
coverage is adequate*. TDD discipline (red-green-refactor) governs *when* and
*how* to write them — follow both.

---

## Test Taxonomy

Write tests at every layer that provides distinct value. Bias toward tests that
catch real regressions, not tests that inflate a coverage number.

| Layer | What it tests | When to write |
|-------|---------------|---------------|
| **Unit** | Single function/method in isolation | Business logic, algorithms, transformations, validation rules |
| **Integration** | Components working together with real I/O | Repository layers, API handlers, service calls, DB queries |
| **End-to-End** | Complete user journey through real stack | Core user flows — login, checkout, primary feature |
| **UI / Browser** | Real browser against running server | Any web UI change — see UI Testing Mandate below |

### Choosing the right layer

**Write a unit test when:** the code is pure logic with no I/O — algorithms,
transformations, validation, business rules with complex branching. If you can
call the function with plain values and get a plain value back, it's a unit test.

**Write an integration test when:** the code touches real I/O — a database query,
an HTTP call, a file read/write, a message queue. Test with the real thing, not a
mock. If you're tempted to mock the database to write a "unit" test, write an
integration test instead.

**Write an E2E test when:** the feature has a user-visible flow that crosses
multiple layers — HTTP request → service → database → response. Limit to core
flows; not every endpoint needs one.

**Write a browser test (Playwright) when:** the code runs in a browser or renders
HTML — components, pages, forms, interactions. If the output is DOM, test it in a
browser. A TypeScript function with no DOM output does not need Playwright.

One integration test covering a real I/O path is worth more than ten unit tests
mocking the same path. Don't let unit test counts substitute for integration coverage.

---

## What to Write for Every Feature

For each new feature or significant change, cover all four categories. Missing
any of them is incomplete test coverage.

### 1 — Happy Path

The primary success case — the thing users do most often.

- Mandatory for every feature, no exceptions
- Tests what the feature is *for*, not just that it doesn't crash
- Must verify the correct output or state, not just absence of error

### 2 — Correctness

Verify the right answer is produced, not just *an* answer.

- Assert specific return values, state changes, side effects
- `result != null` is not a correctness test — `result == expectedValue` is
- Test each distinct output the function can produce

### 3 — Robustness

Verify the system handles adversarial conditions gracefully.

| Category | Examples |
|----------|----------|
| **Boundary values** | Empty input, max length, zero, negative, off-by-one |
| **Invalid input** | Wrong types, malformed data, missing required fields |
| **Error paths** | Network failure, DB unavailable, timeout, permission denied |
| **Concurrent access** | Duplicate requests, race conditions, stale reads |
| **State edge cases** | Uninitialized, already-deleted entity, partially-complete transaction |

Robustness tests catch most production bugs. Don't skip them because the happy
path passes.

### 4 — Property-Based Testing

**When it applies:** the function has an invariant that should hold for a wide
range of inputs — not just the specific examples you thought of.

Good candidates:
- Algorithms (sort, search, encode/decode, compress/decompress)
- Parsers and serialisers — `deserialise(serialise(x)) == x`
- Mathematical operations — commutativity, associativity, identity
- Data transformations where output properties are knowable from input properties
- Validation functions with large input spaces

**Not applicable for:** UI interactions, simple CRUD, fixed-enum validation,
integration tests, anything where the "correct answer" is defined case-by-case.

Use the appropriate library for the stack (Hypothesis for Python, fast-check for
TypeScript/JavaScript, jqwik for Java). Write properties as invariants, not as
specific input/output pairs:

```python
# ❌ Example-based — only tests what you thought of
assert sorted([3, 1, 2]) == [1, 2, 3]

# ✅ Property-based — holds for any list
@given(st.lists(st.integers()))
def test_sort_is_idempotent(xs):
    assert sorted(sorted(xs)) == sorted(xs)
```

### 5 — Regression Anchors

### ⛔ Bug Fix Workflow — Mandatory

When investigating a bug:

1. **Write a failing test first.** Before touching the fix, write a test that reproduces the problem. Run it and confirm it fails for the right reason.
2. **Apply the fix.** Only after seeing the test fail.
3. **Verify the test passes.** Run the test again. It must go green.
4. **Verify no regressions.** Run the full test suite.
5. **Report back only after step 4 passes.** Never claim a fix is complete until the tests confirm it.

A test written after the fix can pass for the wrong reasons. The failing test is the evidence that the fix addresses the actual bug, not a coincidental symptom. A bug fixed without a test will recur.

---

## Coverage Analysis

**Line coverage is a floor, not a ceiling.** 80% line coverage with no
robustness tests is worse than 60% with comprehensive edge-case coverage.

After writing tests for a feature, explicitly ask:

> "What would have to go wrong in production that my tests would NOT catch?"

Every answer is a missing test. Keep asking until the answer is "nothing credible."

### Coverage is inadequate when:

- All tests still pass after deleting the function body
- No test triggers any catch block or error handler
- No test asserts a specific return value (only that no exception was thrown)
- Mocks outnumber real I/O calls
- Every test is a unit test with no integration or E2E coverage

### Coverage analysis checklist

Run this after writing tests for any feature:

- [ ] Happy path verified with specific output assertion?
- [ ] Every error branch triggered by at least one test?
- [ ] Boundary values (empty, null, max, min) explicitly tested?
- [ ] Real I/O paths exercised (not only mocked)?
- [ ] Regression test exists if this is a bug fix?
- [ ] Mutation check: if I flip a `>` to `>=`, delete a return statement, or remove a condition — would a test catch it? If not, an assertion is missing.

---

## Test Flakiness Prevention

A flaky test — one that sometimes passes and sometimes fails without code
changes — is worse than no test. It erodes trust in the suite and causes real
failures to be ignored as "probably flaky."

**Apply this section when any of these are present:**

| Trigger | Risk |
|---------|------|
| Async / concurrent code | Race between assertion and completion |
| External services (HTTP, DB, queue) | Timing, network, or ordering variability |
| Date/time dependencies | Results differ by time of day or timezone |
| Shared mutable state between tests | Test-order dependency; passes in isolation, fails in suite |
| Random number generation | Non-deterministic output |
| File system with non-isolated paths | Leftover state from previous run |

**Rules:**
- Never use `sleep()` to wait for async completion — use explicit awaits, callbacks, or polling with a timeout
- Never share mutable state between tests — reset or isolate per test
- Never depend on test execution order — each test must be independent
- Seed or mock random number generators in tests that consume them
- Use injected/fixed clocks for date/time-sensitive logic, never `Date.now()` or `datetime.now()` directly
- Use isolated temp directories per test, never hardcoded paths

**If a test is already flaky:** fix the root cause (race condition, shared state) rather than adding retries. Retries hide the problem; they don't solve it.

---

## High-Value Test Prioritization

Not all tests have equal value. When time is limited:

| Priority | Test type | Reason |
|----------|-----------|--------|
| **1** | E2E for core user flows | High blast radius; catches integration failures invisible to lower layers |
| **2** | Integration tests for I/O paths | Catches wiring bugs; mocks cannot |
| **3** | Robustness / error path tests | Most production bugs are edge cases |
| **4** | Happy path unit tests | Fast feedback for logic-heavy code |
| **5** | Trivial delegation, getters/setters | Skip — near-zero bug-catching value |

Skip Priority 5 entirely. Testing trivial delegation adds maintenance burden
with no meaningful protection.

---

## UI Testing Mandate — Browser Automation Required

**A UI component or page is not tested until a browser has exercised it.**

Visual showcases, static HTML previews, and component demos are documentation,
not tests. They do not verify the feature works. Use Playwright (TypeScript
projects) or the appropriate browser automation tool for the stack.

### Required for any web UI change

At minimum, one browser test covering the happy path:

```typescript
test('user can submit the form', async ({ page }) => {
  await page.goto('/the-page');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByText('Success')).toBeVisible();
});
```

### Browser tests must cover

| Scenario | What to assert |
|----------|----------------|
| Happy path | Primary action succeeds; correct UI state appears |
| Validation | Invalid input shows specific error message |
| Async/loading | Loading state visible, then resolved state appears |
| Error state | Server error shows user-facing message, not a crash or blank screen |

### What is NOT acceptable as a UI test

- "Component rendered without throwing" — no behavioral assertion
- A static HTML file opened manually — not a running server, not repeatable
- Screenshots without assertions — documents output, doesn't verify it
- Prose description of manual testing — not automated, not repeatable

If browser automation is not set up in the project, set it up before claiming
any UI work is complete.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Mocking all dependencies | Tests verify mock behavior, not real behavior; wiring bugs invisible | Use real implementations for integration tests |
| Testing implementation, not behavior | Tests break on refactor even when behavior unchanged | Assert outcomes, not internal method calls |
| Only happy path tests | Edge cases cause most production bugs | Explicitly write robustness tests per the table above |
| Skipping browser tests for "simple" UI | Browser environment is unpredictable; "simple" still breaks | One Playwright happy path test is mandatory |
| High line coverage = done | Lines ≠ behaviors; error paths often not covered | Run the coverage analysis checklist above |
| Asserting no exception, not correct output | Tests pass even when function returns wrong value | Always assert the specific expected value |

---

## Skill Chaining

**Prerequisites for:** `java-dev`, `ts-dev`, `python-dev`

**Does not invoke anything directly** — foundation skill only.
