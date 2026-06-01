# Form: Technical Documentation

Structured technical documents that grow alongside a system and serve as
session context for LLMs and humans. Multi-mode: different sections use
different modes, declared in the mode map below.

**Not:** CLAUDE.md files (managed by `update-claude-md`), one-off specs or
design documents (use `forms/article.md` explanation sub-type).

---

## Distinguishing test

**Does the subject evolve?**
- Yes — the document will be updated as the system changes → technical documentation
- No — written once for an audience → article

**Is the audience dual (human + LLM session context)?**
- Yes → technical documentation
- No → article or note

**When in doubt:** Technical documentation is maintained, not published.
If content will be updated as the system evolves → technical documentation.

---

## Key properties

- **Multi-mode** — each section type has its own mode; see mode map below
- **Living document** — grows alongside the system, not written once
- **Reality-dominant** — system facts drive it, not the author's voice or the reader's task
- **Dual audience** — human scanning + LLM loading context for a session
- **One section at a time** — write-content targets one section type per invocation;
  the mode map is the routing reference

---

## Dual audience writing rules

LLM precision requirements and human scannability create tension. Apply these rules
to resolve it:

**Where they align (no tension):**
- Specific nouns (class names, file paths, error messages) — serve both audiences
- Bold lead-ins and labelled entries — scannable for humans, unambiguous anchor for LLMs
- One idea per sentence — parseable for LLMs, readable for humans
- Explicit scope statements ("not closed here", "applies to all X") — both audiences benefit

**Where they conflict:**
- LLMs benefit from repeated context (same class named in every entry, not "the above class")
- Humans benefit from shorter text (assume prior context within one section)
- **Resolution:** Repeat technical names; do not repeat reasoning. A class name is cheap;
  a paragraph of context is not. "PrReviewCaseService @ApplicationScoped displaces..."
  is better than "the service displaces..." for both audiences.

- LLMs benefit from explicit "This section does NOT cover X" statements
- Humans may find these obvious
- **Resolution:** Include scope boundaries in every section. They cost one sentence
  and prevent both audiences from inferring wrong scope.

---

## The no-content-loss rule

When restructuring or rewriting a section, no content is omitted — only relocated.

**Before rewriting any section:**
1. Enumerate all atomic facts in the source — every specific claim, file path,
   class name, reference, consequence, scope boundary
2. Record the list before touching the content

**After rewriting:**
- Every atomic fact must appear in the rewritten output — in the body or in the
  entry header fields (Design refs, Navigation, Key protocols, etc.)
- A fact not present is a loss, not a simplification
- References for depth move to header fields; actionable content stays in the body

**Strip test:** remove all labels and read only those in sequence. The result
should be a complete factual skeleton with no gaps. Any fact that only exists
in a body (not visible in any label) is invisible to scanning.

---

## Mode map

Each section type has a declared mode. Before invoking write-content for a
technical documentation section, identify the target section and its mode here.
Load the corresponding mode file from `modes/`.

### Arc42stories — canonical mode map

| Section | Mode | Mode file |
|---|---|---|
| §1–3 Introduction, Constraints, Context | Reference/lookup | `modes/reference.md` |
| §4 Solution Strategy | Explanation/comparative | `modes/explanations.md` |
| §5 Building Block View | Reference/lookup + diagram | `modes/reference.md` |
| §6 Runtime View | Explanation/comparative | `modes/explanations.md` |
| §7 Deployment View | Reference/lookup | `modes/reference.md` |
| §8 Crosscutting pointer table | Reference/pointer | `modes/reference.md` |
| §8 Anti-patterns | How-to/diagnostic | `modes/how-to.md` |
| §9.1–9.2 Journey + Chapter Index | Reference/lookup | `modes/reference.md` |
| §9.3 Chapter entries "What this delivers" | Explanation/comparative | `modes/explanations.md` |
| §9.4 Key files | Reference/inventory | `modes/reference.md` |
| §9.4 Key wiring | Reference/lookup | `modes/reference.md` |
| §9.4 "What it adds" | Explanation/comparative | `modes/explanations.md` |
| §9.4 Gotchas | How-to/diagnostic | `modes/how-to.md` |
| §9.4 Pattern to replicate | Tutorial | `modes/tutorial.md` |
| §9.4 Architectural decisions | Argumentation/rationale | `modes/argumentation.md` |
| §10 ADRs | Argumentation/decision | `modes/argumentation.md` |
| §11–12 Quality/Risk tables | Reference/lookup | `modes/reference.md` |
| §13 Glossary | Reference/lookup | `modes/reference.md` |

Other technical documentation (platform guides, component design docs, onboarding
guides) declares its own mode map using this format. The section names and modes
will differ; the principle — one declared mode per section type — is the same.

---

## Content migration guide

Use when migrating existing content to the mode-aware style defined here.

### Before rewriting

1. Identify the section's mode from the mode map above
2. Read the corresponding mode file from `modes/`
3. Enumerate all atomic facts from the source section:
   - File paths, class names, method names
   - Configuration values, environment variables
   - Issue numbers, commit hashes, blog links
   - Consequences stated ("without this, X fails")
   - Scope boundaries ("not closed here", "not applicable to Y")
   - References to external documents

### Rewrite

Apply the mode's constraint set from the mode file. Where content needs to be
relocated rather than omitted:
- References for depth → header metadata fields (Design refs, Key protocols, Navigation)
- Accountability gaps → Accountability gaps table
- Historical context → not in the entry; belongs in the blog or git history

### After rewriting — loss check

Verify coverage: every atomic fact from the pre-rewrite list must appear in the
output — in the body or a header field.

Check the strip test: remove all labels and bold lead-ins and read only those
in sequence. Is the factual skeleton complete? Every gap is a content loss.
