---
name: fix-ci
description: >
  Use when CI is red and the user asks to fix it, or when a push fails CI
  and the user asks "is CI green?" after a fix. Ensures all failures are
  reproduced locally, root-caused, and verified green before any push.
  Never use CI as a test runner.
---

# Fix CI

Local-first, root-cause-first workflow for fixing CI failures. Every failure
is reproduced, diagnosed, and verified locally before pushing. One push, one
CI run, done.

**Anti-pattern this replaces:** fix one symptom → push → wait 5 min → check CI
→ find next failure → repeat. This uses CI as a test runner, creates long wait
cycles, and fixes symptoms instead of root causes.

---

## Step 1 — Gather failures

Get the list of failing tests from CI.

```bash
gh run list --repo <OWNER_REPO> --limit 1 --json databaseId --jq '.[0].databaseId'
gh run view <ID> --repo <OWNER_REPO> --log-failed 2>/dev/null | grep "<<< FAILURE\|<<< ERROR"
```

Record every failing test class and its error message. This is the full scope —
don't stop at the first one.

---

## Step 2 — Reproduce locally (isolated)

For each failing test, reproduce the failure locally by running **only that test**.
Not the full suite — isolated, fast.

```bash
# Example for Maven/Quarkus
scripts/mvn-test <module> -Dtest=FailingTestClass

# Example for npm
npm test -- --testPathPattern=failing-test
```

**If the test passes locally in isolation:** the failure is test-ordering
contamination. Run the full module suite to reproduce:
```bash
scripts/mvn-test <module>
```

**If the test needs infrastructure** (Docker, database, external service):
check if the CI environment provides it and the local environment doesn't.
The test should skip gracefully when infrastructure is absent — if it doesn't,
that's part of the fix.

### Remote machine option

If the user has configured a remote test machine (SSH access, same repo checked out),
run the isolated test there instead:

```bash
ssh <remote> "cd <project-path> && <test-command> -Dtest=FailingTestClass"
```

Only use the remote machine for isolated test runs (Steps 2 and 4), not the
full build (Step 5). The remote option is for cases where the local machine
lacks infrastructure (Docker, specific JDK, native image toolchain) that CI has.

---

## Step 3 — Root cause analysis

For each failure, diagnose the **root cause**, not the symptom.

**The question:** what changed, and what else does it affect?

- If a new column was added: which modules have entities with that column?
  Check ALL of them, not just the one that failed.
- If a config property changed: which modules have their own copy of that config?
  Check ALL of them.
- If a CDI bean changed: which modules depend on it? Trace the dependency tree.
- If a test infrastructure change was made: which modules share the same test
  infrastructure pattern? Fix them all.

**Root cause checklist:**
1. What is the immediate error? (symptom)
2. What code change caused it? (trigger)
3. What is the architectural pattern that was violated? (root cause)
4. Where else in the project does the same pattern exist? (blast radius)
5. Fix all instances, not just the one that failed.

**Exhaustive means exhaustive.** Use `grep`, `find`, or IDE search to locate
every instance of the pattern. A tenancyId fix that catches runtime but misses
examples, queues-examples, queues-dashboard, ai, and flow-examples is a symptom
fix. The root cause is "every module that persists entities needs tenancyId" —
find them all.

---

## Step 4 — Fix and verify (isolated loop)

For each failing test:

1. Apply the fix
2. Run **only that test** locally (or on the remote machine)
3. Confirm it passes
4. Move to the next failing test

Do not run the full suite yet. Isolated runs are fast — seconds, not minutes.

```
Loop:
  pick next failing test
  → apply fix
  → run isolated test
  → green? → next test
  → red?  → back to Step 3, dig deeper
```

---

## Step 5 — Full local build

Only after ALL isolated tests pass.

Run the complete test suite for all modules. This catches:
- Cross-module contamination
- Test ordering issues
- Transitive dependency breaks

```bash
# Maven multi-module
mvn test -pl module1,module2,module3,...

# Or the project's full build script
scripts/check-build
```

**If new failures appear:** go back to Step 2 for those failures.
Do not push until the full local build is green.

---

## Step 6 — Push

One push. One CI run.

```bash
git push
```

---

## Step 7 — Verify CI

Schedule a wakeup to poll CI status. Default wait: 5 minutes (300s).
Override by setting `ci-build-time-minutes` in CLAUDE.md `## Build and Test`.

```
ScheduleWakeup:
  delaySeconds: 300   # or ci-build-time-minutes × 60 from CLAUDE.md
  reason: "waiting for CI run to complete after push"
  prompt: "/fix-ci"
```

On wakeup, check CI:

```bash
gh run list --repo <OWNER_REPO> --limit 1 \
  --json status,conclusion,headSha \
  --jq '.[0] | "\(.status) | \(.conclusion // "—") | \(.headSha[:7])"'
```

- **completed + success** → done. Report green.
- **completed + failure** → go back to Step 1 with the new failures. The failure
  is environment-specific (Docker, OS, test ordering on a different JVM).
  Reproduce locally or on the remote machine and repeat the full cycle.
- **in_progress / queued** → schedule another wakeup (270s).

---

## Pre-existing failures

If a test was already failing before your changes (verify by checking it against
the pre-change commit), it is not your responsibility to fix in this cycle.
File an issue, note it, and exclude it from the green gate.

```bash
# Verify a test was pre-existing
git stash
<run test>  # still fails? pre-existing
git stash pop
```

---

## Skill Chaining

**Invoked by:** User saying "fix CI", "CI is red", "is CI green?" after a push,
or when a pre-push hook or CI check fails.

**Invokes:** Nothing — standalone diagnostic and fix workflow.

**Complements:** `java-dev`, `ts-dev`, `python-dev` for the actual code fixes;
`git-commit` for committing the fixes; `superpowers:verification-before-completion`
for the final green check.
