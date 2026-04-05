# cc-praxis — Health, TypeScript, and Python

**Date:** 2026-04-02
**Type:** phase-update

---

Two parallel goals this phase: build a quality framework that would catch problems automatically, and expand the language coverage beyond Java.

## What we were trying to achieve: Don't let it rot

The skills existed but there was no systematic way to verify they stayed internally consistent. Cross-references could drift. Section names could diverge. Bidirectional chaining could break silently.

For languages: TypeScript/Node.js was the obvious next addition, followed by Python. Java-first was never the intention — it was just the first complete implementation.

## What we believed going in: A few validators and mechanical translation

I expected to write a small number of validators targeting the most common problems — mainly cross-references.

For TypeScript, I thought it would be largely mechanical: create the same five skills as Java, adapt the rules for TypeScript-specific concerns. Strict mode, async patterns, prototype pollution. Done in a day or two.

## The validator framework

What started as "a few validators" became 17 across three tiers.

**COMMIT tier** (under 2s): frontmatter, CSO compliance, cross-references, naming, sections, structure, project-type consistency, flowchart syntax, document structure, blog-commit format.

**PUSH tier** (under 30s): cross-document consistency, temporal references, usability, edge cases, behaviour, README sync, web app sync.

**CI tier** (under 5 minutes): mypy, flake8, bandit for the Python tooling.

The cross-reference validator initially produced 48 false positives — scanning too broadly and flagging internal terms that aren't skill names. We scoped it to the Skill Chaining sections only and added an allowlist of known non-skill terms. That got it to zero false positives.

Every validator caught real problems. That's how you know they're working.

## project-health: the hard design problem

`project-health` and `project-refine` were the most design-intensive skills I'd written. Unlike the others with clear workflows, project-health needed to work across all project types, have a tier system, auto-chain to type-specific specialists at higher tiers, and stay cleanly separated from project-refine.

There were five open questions in the design document at one point. We worked through all of them — choosing Option B for routing (universal base, auto-chain to type-specific skills), and drawing a firm line between "correctness" (project-health) and "improvement opportunities" (project-refine). Mixing them causes confusion about what action to take.

## TypeScript

Five skills: `ts-dev`, `ts-code-review`, `ts-security-audit`, `npm-dependency-update`, `ts-project-health`. The cross-referencing work on the Java skills had taught us what to do from the start — the TypeScript skills had correct bidirectional references from the first commit.

One unexpected problem: bidirectional inference initially put `git-commit` in `ts-code-review`'s `invoked_by` field, making `git-commit` appear as a child of `ts-code-review` in the chain graph. Claude flagged this as wrong — and it was. We fixed it by marking `git-commit` as BIDIRECTIONAL_EXEMPT; the chain doesn't force inference through universal entry points.

## Python

Five more: `python-dev`, `python-code-review`, `python-security-audit`, `pip-dependency-update`, `python-project-health`. Python's code review has specific concerns the Java and TypeScript ones don't: pickle deserialization, subprocess shell injection (which looks innocuous — `shell=True` — but isn't), the important distinction between passing a string and a list to `subprocess.run`.

## CI and the Puppeteer problem

We added GitHub Actions CI to run the validators and tests on every push. First attempt failed — Puppeteer, which the Mermaid validator uses, hit Chrome sandbox issues in the CI environment. The fix: only treat an explicit "Parse error" from Mermaid as a syntax failure. A Puppeteer crash is an environment problem, not a diagram problem.

## What changed and why: scope, then split

The health skill design pivoted when a single universal skill became unwieldy. The split — `project-health` for universal correctness, separate `java-project-health`, `ts-project-health`, and so on for language depth — was the right architecture.

Skills need a quality framework from the start, not as an afterthought. The validator infrastructure is what lets the collection grow without accumulating invisible drift. Every new skill I add now runs through 17 automated checks before it lands.
