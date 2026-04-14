---
name: project-health
description: >
  Use when correctness, completeness, or consistency of a project needs
  verification — "is the project healthy?", "pre-release check", "do a health
  check", "check docs are in sync", invokes /project-health. NOT for
  improvement suggestions (use project-refine for that).
---

# Project Health

Answer the question: **is this project correct, complete, and consistent?**

Runs universal quality checks that apply to every project type, then automatically
chains to the type-specific health skill based on the project type declared in CLAUDE.md.

---

## Step 0 — Read Project Type

Before any checks run, read the project type from CLAUDE.md:

```bash
grep -A 2 "## Project Type" CLAUDE.md 2>/dev/null
```

Extract the type: `skills` | `java` | `blog` | `custom` | `generic`

If CLAUDE.md is missing or has no Project Type, treat as `generic` and note it
as a `config` finding.

Store the type — type-aware checks (`primary-doc`, `artifacts`, `conventions`,
`framework`) use it throughout this skill.

---

## Step 1 — Determine Tier

Parse flags from the invocation:

| Flag | Tier | What runs |
|------|------|-----------|
| `--commit` | 1 | `validate_all.py --tier commit` only |
| `--standard` | 2 | Universal quality checks |
| `--prerelease` | 3 | Universal + type-specific quality checks |
| `--deep` | 4 | All of tier 3 + refinement questions |
| `--tier N` | N | Explicit tier (1–4) |

If no tier flag is given, prompt:

> **How thorough should this check be?**
>
> 1 — **Quick** — validators only (~30s)
> 2 — **Standard** — universal quality checks (~5 min)
> 3 — **Full** — universal + type-specific quality (~15 min)
> 4 — **Deep** — everything + refinement questions (~30 min)
>
> Enter 1–4 (default: 2):

Wait for response. If no response, use tier 2.

Also parse:
- `--save` → write report to `YYYY-MM-DD-health-report.md` after output
- Category names (e.g. `docs-sync consistency`) → run only those categories
- If categories specified without `--tier`, run at tier 2

---

## Step 2 — Tier 1: Run Automated Validators

**Always run first** (all tiers include this):

```bash
python scripts/validate_all.py --tier commit
```

If this script doesn't exist, note it as a `config` finding and skip.

Report output. If CRITICAL findings from validators → flag them.

For tier 1, **stop here**. Present findings and exit.

---

## Step 3 — Build Document Scan List

For tier 2+, build the scan scope before running checks.

**Always included:**
- All `.md` files (recursive) under `doc/`, `docs/`, `documentation/` (case-insensitive)
- Root-level `.md` files matching: `readme`, `overview`, `summary`, `index`, `contributing`,
  `governance`, `code_of_conduct`, `changelog`, `history`, `release`, `architecture`,
  `design`, `decisions`, `vision`, `philosophy`, `principles`, `api`, `schema`, `glossary`,
  `security`, `deployment`, `install`, `usage`, `troubleshooting`, `roadmap`, `spec`,
  `requirements`, `quality` (case-insensitive match on filename stem)
- Any root `.md` not on the list is still scanned
- Any `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md` anywhere in the tree

**Type-specific additions (use detected type from Step 0):**
- `skills` → all `SKILL.md` files in direct subdirectories
- `java` → `pom.xml`, `build.gradle`, Javadoc comments in `src/`
- `blog` → `_config.yml`, `_posts/`, `_layouts/`, `_includes/`
- `custom` → primary document path declared in CLAUDE.md

**User-configured additions:**
Read `## Health Check Configuration` from CLAUDE.md:
```
Additional doc paths: wiki/, design/
```
Add any listed paths to the scan scope.

---

## Step 4 — Read CLAUDE.md Health Configuration

```bash
grep -A 10 "## Health Check Configuration" CLAUDE.md 2>/dev/null
```

Parse:
- `Default checks:` → limit to these categories if no categories specified on invocation
- `Skip:` → exclude these categories even if requested
- `Additional doc paths:` → already applied in Step 3

If no configuration section, use built-in defaults: run all universal categories.

---

## Step 5 — Run Universal Checks

Run the applicable check categories at the requested tier. Skip categories listed
in `Skip:` from CLAUDE.md. If specific categories were requested, run only those.

For **tier 2**: quality items only (pass/fail checks).
For **tier 4**: quality items + refinement questions (judgment items).

**Read [check-categories.md](check-categories.md)** for the full quality and
refinement checklists for all 12 universal categories before running checks:
`docs-sync`, `consistency`, `logic`, `config`, `security`, `release`,
`user-journey`, `git`, `primary-doc`, `artifacts`, `conventions`, `framework`.

---

## Step 6 — Chain to Type-Specific Skill (Tier 3+)

At tier 3 and 4, after universal checks complete, automatically invoke the
type-specific health skill in the same session:

| Project type | Invoke |
|---|---|
| `skills` | `skills-project-health` |
| `java` | `java-project-health` |
| `blog` | `blog-project-health` |
| `custom` | `custom-project-health` |
| `generic` | Skip — universal checks only |

The type-specific skill's output is appended to the report. Do NOT redirect the
user to run a separate command — chain automatically.

If the type-specific skill does not exist yet, note it as a LOW finding:
> [config] Type-specific health skill `{type}-project-health` not yet available

---

## Step 7 — Present Report

```
## project-health report — [categories run] — tier [N]

### CRITICAL (must fix)
- [category] finding description

### HIGH (should fix)
- [category] finding description

### MEDIUM (worth fixing)
- [category] finding description

### LOW (nice to fix)
- [category] finding description

### PASS
✅ category1, category2, ...
```

Universal findings have no extra prefix. Type-specific findings are prefixed
with `[type]` (e.g. `[java]`). If no findings in a severity level, omit that section.

---

## Step 8 — Offer Auto-Fix (Mechanical Issues Only)

For mechanical findings (wrong count in README, stale version number, missing
`commands/<name>.md`), offer:

> **Auto-fixable findings detected.**
>
> Would you like me to apply mechanical fixes now?
> - [list of specific fixes]
>
> **(YES / NO — judgment calls are never auto-applied)**

Wait for response. Apply only on YES. Never auto-apply.

---

## Step 9 — Save Report (if --save)

If `--save` was passed, write findings to a date-prefixed file:

```bash
# Format: YYYY-MM-DD-health-report.md
```

Tell user:
> Report saved to `YYYY-MM-DD-health-report.md`. This file is gitignored by default.

Verify `.gitignore` includes `*-health-report.md` or similar. If not, suggest adding it.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Running type-specific checks before reading project type | Checks have no context | Always read project type in Step 0 first |
| Reporting "plans to implement" as bugs | Intentional design language | Distinguish docs describing intent vs. describing current state |
| Auto-fixing judgment findings | Judgment calls require human decision | Only auto-fix mechanical findings, always with YES confirmation |
| Skipping chain to type-specific skill at tier 3+ | Incomplete health picture | Chain is mandatory at tier 3+ unless type is generic |
| Treating all findings as equal | CRITICAL blocks release, LOW does not | Use severity consistently |
| Running `docs-sync` without reading the actual source files | Can't verify claims without reading | Read code and docs together |

---

## Success Criteria

Health check is complete when:

- ✅ Project type read from CLAUDE.md before any checks ran
- ✅ Tier confirmed (via flag or prompt)
- ✅ All applicable universal categories checked at the requested tier
- ✅ Type-specific skill chained at tier 3+ (or skipped for generic)
- ✅ Report presented with findings grouped by severity
- ✅ Mechanical auto-fix offered (not applied without YES)
- ✅ Report saved if `--save` was passed

**Not complete until** all applicable categories checked and report presented.

---

## Skill Chaining

**Invoked by:**
- User says "health check", "is the project healthy", "pre-release check", or invokes `/project-health`
- Type-specific health skills invoke this as their prerequisite foundation
- Other skills (e.g. `git-commit`) can suggest `/project-health --commit` after significant changes

**Chains to (at tier 3+):**
- `skills-project-health` — for type: skills
- `java-project-health` — for type: java
- `blog-project-health` — for type: blog
- `custom-project-health` — for type: custom

**Suggests (not auto-chained — these types are not built-in project types):**
- `python-project-health` — suggested when a Python project is detected (no `type: python` built-in; Python projects use `type: generic` or `type: custom`)
- `ts-project-health` — suggested when a TypeScript/Node.js project is detected (no `type: ts` built-in; TS projects use `type: generic`)

**Companion skill:**
- [`project-refine`] — once health is green, use project-refine for improvement opportunities (bloat, structure, deduplication). They share the same CLAUDE.md Health Check Configuration section.
