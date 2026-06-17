---
name: project-refine
description: >
  Use when seeking improvement opportunities in a project — "find duplication",
  "bloat check", "look for ways to improve docs", "do a refine session".
  NOT for correctness or compliance — use project-health for that.
slash-command: false
---

# Project Refine

Answer the question: **could this project be smaller, clearer, or better structured?**

A dedicated improvement session across documentation and code (including tests).
Looks at things that already work and asks whether they could be better. Never
blocks work — findings are always opportunities, never failures.

---

## Step 0 — Read Project Type and Configuration

Read project type (for context, not routing — project-refine is always the
right skill regardless of type):

```bash
python3 ~/.claude/skills/project-init/ctx.py
```

Read `PROJECT_TYPE` from the output.

Also read Health Check Configuration from CLAUDE.md:

```bash
grep -A 10 "## Health Check Configuration" CLAUDE.md 2>/dev/null
```

Parse from `## Health Check Configuration`:
- `Default refine domains:` → domains to run (default: `docs, code, universal`)
- `Default refine tier:` → tier if not specified (default: 2)
- `Refine min score:` → minimum bloat score to report (`all` | `medium` | `high`) (default: `all`)
- `Additional doc paths:` → extra paths to scan

---

## Step 1 — Determine Tier

Parse flags from the invocation:

| Flag | Tier |
|------|------|
| `--tier 1` | Structural checks only, no file reading (~2 min) |
| `--tier 2` | Read top candidates by churn and size (~10 min) |
| `--tier 3` | Deeper scan, IntelliJ MCP if available (~20 min) |
| `--tier 4` | Full scope, prompted for focus area (~30–45 min) |

Also parse:
- `--save` → write report to `YYYY-MM-DD-refine-report.md` after output
- `--compare <file>` → show only findings not present in a previous report
- Domain names (`docs`, `code`, `universal`) → run only those domains

If no tier flag is given (and no `Default refine tier` configured), prompt:

> **How thorough should this refinement session be?**
>
> 1 — **Quick** — structural checks only, no file reading (~2 min)
> 2 — **Standard** — read top candidates by churn and size (~10 min)
> 3 — **Full** — deeper scan, IntelliJ MCP if available (~20 min)
> 4 — **Deep** — full scope, prompted for focus area (~30–45 min)
>
> Enter 1–4 (default: 2):

Wait for response. If no response, use tier 2.

---

## Step 2 — Focus Prompt (Tier 2+)

Before scanning code at tier 2 or above, ask:

> **Would you like to focus on a specific directory or package?**
>
> Enter a path (e.g. `src/main/java/com/example/payment`), or type "auto"
> to use git history and file size to find candidates automatically.

Wait for response. If a path is provided, limit code scanning to that path.
If Enter, proceed with automatic candidate selection.

---

## Step 3 — Build Scan Candidates

### Docs candidates

Build the document scan list using the same scope as `project-health`:

**Always included:**
- All `.md` files under `doc/`, `docs/`, `documentation/` (recursive, case-insensitive)
- Root-level `.md` files (all of them)
- Any `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md` anywhere in tree
- Additional paths from CLAUDE.md Health Check Configuration

**Tier 1 (structural only — no file reading):**
```bash
find . -name "*.md" -not -path "./.git/*" | xargs wc -l 2>/dev/null | sort -rn | head -20
```
Identify docs by line count. Flag files over ~400 lines as candidates.

**Tier 2:** Read the top 5 docs by line count.
**Tier 3+:** Read all docs over 200 lines. Read everything if under 30 files total.

### Code candidates

If a focus path was given, start there. Otherwise:

**Tier 1 (no file reading):**
```bash
# Files by size
find . -name "*.py" -o -name "*.java" -o -name "*.ts" -o -name "*.go" | grep -v ".git" | xargs wc -l 2>/dev/null | sort -rn | head -20

# Files by churn (most frequently changed)
git log --format=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -20

# Repeated literals
grep -r --include="*.py" --include="*.java" --include="*.ts" -h "\"[^\"]\{8,\}\"" . 2>/dev/null | sort | uniq -c | sort -rn | head -10
```

**Tier 2:** Read top 10 files by churn+size combined ranking.
**Tier 3:** Read top 20 files. Use IntelliJ MCP semantic search if available:
  - `ide_find_references` to check for unused code
  - `ide_search_text` for repeated patterns
**Tier 4:** Read all files above size threshold plus user-specified focus area.

---

## Step 4 — Run Refinement Domains

Run the configured domains (`docs`, `code`, `universal`). Skip domains excluded
by the invocation or CLAUDE.md configuration.

### `docs` — Documentation Structure & Readability

> Could documentation be better structured, smaller, or easier to read?

**Structure & organisation**
- [ ] Would a different grouping or ordering of sections improve navigation?
- [ ] Are there docs over ~400 lines with multiple distinct topics that would be clearer as separate linked files?
- [ ] Are there multiple small files covering closely related topics that would read better merged?
- [ ] Are related topics scattered across documents that should be consolidated?

**Readability**
- [ ] Passive voice, unexplained jargon, walls of text, or sentences over 25 words?
- [ ] Could any prose be replaced with a table or example easier to scan?
- [ ] Is the detail level appropriate for the intended audience?

**Dead weight**
- [ ] Sections that restate what was just said, or introductory paragraphs that add no information?
- [ ] Sections describing plans, history, or context that are no longer relevant?
- [ ] Documents or sections never read because they're hard to find or navigate to?

**Consistency of structure**
- [ ] Do tables of the same type use consistent column order and headers throughout?
- [ ] Do documents introduce concepts and define them paragraphs later (forward references)?

---

### `code` — Deduplication, Abstraction & Organisation

> Could code (including tests) be deduplicated, abstracted, or better organised?

**Duplication**
- [ ] Same blocks of logic appearing 3+ times? (high risk: fix one, miss others)
- [ ] Similar but not identical blocks that should be parameterised and shared?
- [ ] Literal values (strings, numbers, paths) repeated in multiple places?
- [ ] Same fixture or arrangement code copy-pasted across multiple test methods?
- [ ] Test patterns repeated enough to extract into shared helpers or base classes?

**Abstraction opportunities**
- [ ] Repeated sequences of calls that always appear together, belonging in a helper?
- [ ] Functions over ~30 lines combining multiple distinct concerns?
- [ ] Missing abstractions that would make the code more expressive?

**Organisation**
- [ ] Tests for one feature spread across multiple files without clear ownership?
- [ ] Tests that would benefit from being grouped to reflect the structure of what they test?
- [ ] Test names follow a consistent pattern making it easy to see what's covered?
- [ ] Files (source or test) over size guideline that test multiple unrelated concerns?
- [ ] Shared test fixtures hiding critical preconditions?

**Dead code**
- [ ] Commented-out code? (remove it — git history preserves it)
- [ ] Functions, classes, or modules never called?
- [ ] Feature flags or compatibility shims for things that no longer exist?

**Scattered configuration**
- [ ] Configuration values or defaults defined in multiple files that should be consolidated?
- [ ] Error handling inconsistent across similar operations?

---

### `universal` — Bloat Across All Areas

> What is oversized, over-engineered, or unnecessarily complex anywhere in the project?

- [ ] Files >50% larger than the guideline for their type? (SKILL.md: ~400 lines, test files: ~300 lines)
- [ ] Logic or document sections nested >3 levels deep that could be flattened?
- [ ] Functions with >4 parameters that could be grouped into a config object?
- [ ] Complex solutions for problems that have a simpler answer?
- [ ] More comment lines than code lines explaining obvious things?
- [ ] Dependencies larger than the value they provide?

---

## Step 5 — Score and Present Findings

Rate every finding on two axes:

**Size reduction potential:**
- 🔴 HIGH — >30% reduction possible
- 🟡 MEDIUM — 10–30% reduction possible
- 🟢 LOW — <10%, still worth noting

**Impact of fixing:**
- **A** — significantly improves navigation, readability, or maintenance
- **B** — noticeable improvement
- **C** — cosmetic or marginal

**The axes are independent.** A small change can have large impact. 🟢A (small fix, high impact) is common and important — wrong documentation that misleads users, a missing comment on a confusing invariant, or a one-line fix that makes a hot-path method scannable all qualify. Do not let a finding's small size push it toward B or C impact.

Filter findings by `Refine min score` from configuration:
- `all` → show 🔴🟡🟢
- `medium` → show 🔴🟡 only
- `high` → show 🔴 only

**Domain summary (always shown):**
```
docs: 🟡 moderate    code: 🔴 high    universal: 🟢 low
```

**Before presenting, run this self-check on every finding rated B or C:**
> "If someone fixes this, does it significantly change how quickly a reader understands the code or doc — or prevent them from acting on wrong information?"
> If yes → upgrade to A, regardless of how small the change is.

Common 🟢A patterns (small change, large impact):
- A capability doc says a feature is "Research phase" but it shipped — one paragraph fix, but every reader who evaluates the project is misled until it's corrected
- A hot-path method (called on every write) is 60 lines mixing 6 concerns — extracting one private method halves visual complexity permanently
- A missing class-level comment on a class with non-obvious invariants — two sentences, but saves every future contributor 10 minutes of archaeology

**Detailed findings:**
```
## project-refine — Opportunities Found

### 🔴A — High impact, significant size reduction
- scripts/validate_all.py (lines 45–89): run_validator() logic repeated
  for each tier; extract to a shared helper. Est. -40 lines. [code]

### 🟡A — High impact, medium size reduction
- OrderService.processOrder() (85 lines): mixes validation, business logic,
  and persistence; split into three methods. Est. -25 lines from save(). [code]

### 🟢A — High impact, small size reduction
- CAPABILITIES.md:313: "Current state: Research phase" — feature shipped six
  months ago; every evaluator reads this and thinks it doesn't exist. Fix: 2
  sentences. [docs]

### 🟡B — Medium impact
- update-primary-doc/SKILL.md (312 lines): Steps 4–7 cover two unrelated
  concerns; splitting would improve navigation. Est. -20 lines. [docs]

### 🟢C — Low impact, cosmetic
- java-dev/SKILL.md: "Code duplication" and "Code clarity" sections are
  adjacent and both cover style; could merge. Est. -5 lines. [docs]

### Nothing found
✅ universal
```

Findings are **opportunities**, never failures. Do NOT use CRITICAL, HIGH, MEDIUM,
LOW severity language (that belongs to `project-health`). Use bloat scores only.

**Never auto-apply changes.** All findings are judgment calls. Present
opportunities; the user decides what to act on.

---

## Step 6 — Save Report (if --save)

If `--save` was passed, write findings to a date-prefixed file:

```bash
# Format: YYYY-MM-DD-refine-report.md
```

Tell user:
> Report saved to `YYYY-MM-DD-refine-report.md`. This file is gitignored by default.

Verify `.gitignore` includes `*-refine-report.md` or similar. If not, suggest adding it.

If `--compare <file>` was passed, show only findings not present in the comparison
report. Findings are matched by file path and description prefix.

---

## Invocation Examples

```bash
# Prompted for tier
/project-refine

# Explicit tier
/project-refine --tier 2

# Specific domains
/project-refine docs --tier 1
/project-refine code --tier 3

# Save report
/project-refine --tier 3 --save

# Compare with previous report
/project-refine --compare 2026-03-15-refine-report.md
```

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Using severity language (CRITICAL/HIGH) | project-refine never blocks — that's project-health | Use bloat scores (🔴🟡🟢) only |
| Rating small-change findings as B or C because the change is small | Size and impact are independent — a two-sentence fix that corrects wrong documentation is 🟢A | Run the self-check: "does fixing this significantly change how quickly someone understands this, or prevent them acting on wrong info?" If yes → A |
| Auto-applying refine findings | All are judgment calls requiring human decision | Present opportunities only; never apply without explicit user request |
| Running `code` domain at tier 1 without reading files | Can miss duplication that isn't obvious from structure | Acknowledge tier 1 limitations; recommend tier 2+ for code findings |
| Checking tests in a separate domain from code | Tests are code — duplication patterns apply equally | Apply all code checks to test files as well |
| Flagging small files as bloated | Size alone is not bloat | Only flag when content is also redundant or over-explained |
| Running refinement before health check | Improving something broken is wasted effort | Recommend `/project-health` first if health status unknown |

---

## Success Criteria

Refinement session is complete when:

- ✅ Tier confirmed (via flag, configuration, or prompt)
- ✅ Focus path established (user input or automatic selection)
- ✅ Scan candidates identified at the appropriate tier
- ✅ All applicable domains checked
- ✅ Findings rated with bloat scores (🔴🟡🟢 × A/B/C)
- ✅ Domain summary presented
- ✅ Findings presented as opportunities (no auto-apply)
- ✅ Report saved if `--save` was passed

**Not complete until** all configured domains checked and findings presented.

---

## Skill Chaining

**Invoked by:**
- User says "bloat check", "find duplication", "improve docs structure", "refine session", or invokes `/project-refine`
- Typically run after `/project-health` when health is green

**Does not chain to other skills** — refinement findings are advisory and the user
decides what to act on independently.

**Companion skill:**
- [`project-health`] — run first to verify correctness before improving things.
  Shares the same CLAUDE.md `## Health Check Configuration` section.

**Suggested workflow:**
```bash
# 1. Verify correctness first
/project-health --prerelease

# 2. Once health is green, look for improvement opportunities
/project-refine

# Or for a full pre-release review
/project-health --deep
/project-refine --tier 3
```
