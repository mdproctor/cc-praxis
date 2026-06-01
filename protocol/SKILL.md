---
name: protocol
slash-command: false
description: >
  Use when working with protocol files — standing rules, architectural constraints, and
  conventions that keep a project or platform coherent. Protocols may live in the current
  project or in a shared garden repo (e.g. casehub/garden) — the skill resolves the correct
  location automatically. Session-time operations: CAPTURE (create a new protocol entry),
  SWEEP (scan session for rules worth formalising), SEARCH (find protocols by keyword),
  HEALTH (validate schema completeness and ref integrity). DEEP-SCAN is stubbed — requires
  Hortora audits 1–4 to implement. NOT for universal technical knowledge (use forage for
  that). NOT for architectural decisions (use adr).
---

# Protocol — Project-Level Rule Operations

## What Protocols Are

Standing architectural rules, design patterns, and conventions that keep a project or
platform coherent. A protocol answers "how do we do this consistently?" — not "how do
I avoid this library gotcha?" Protocols are hypotheses, not dogma: test them against
the problem at hand; update them when they don't fit.

**Not a protocol:**
- Universal technical gotcha → use `forage`
- One-off architectural decision → use `adr`
- Rule that only applies in one file → use an inline comment

---

## Protocol Entry Format

```yaml
---
id: PP-YYYYMMDD-xxxxxx
title: "Short directive title"
type: principle | rule
scope: universal | platform | repo | application
applies_to: "which modules / contexts"
severity: critical | important | guidance
refs:
  - path/to/relevant/doc.md
violation_hint: "optional — what a violation looks like"
created: YYYY-MM-DD
---

One paragraph. The directive. Minimum context to understand why.
No implementation detail — refs: covers that.
```

**type:**
- `rule` — has a concrete, specific prescription, often with an example needed to follow it
- `principle` — directional guidance; references out to detail, no example in the body

**severity:**
- `critical` — violations cause bugs, build failures, or data corruption
- `important` — violations cause problems; workarounds possible but costly
- `guidance` — best practice; violations are technical debt

---

## Locating the Protocols Directory

Before any operation, resolve the protocols path:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
```

Resolution order — use the first that applies:

1. **CLAUDE.md routing row (highest priority):** If the project's `CLAUDE.md` has a `protocols` row in its Routing table, extract the explicit path from the Notes column and use it. This handles multi-repo ecosystems where a peer module delegates protocol storage to a central parent repo.
   ```
   | protocols  | parent | /absolute/path/to/parent/docs/protocols/ — ... |
   ```
   Parse: first token starting with `/` in the Notes cell.

2. **Local `docs/protocols/`:** If `$PROJECT_ROOT/docs/protocols/` exists, use it.

3. **Sibling parent layout:** If `$PROJECT_ROOT/../parent/docs/protocols/` exists (multi-repo layout where each module repo sits beside a `parent/` repo), use that path.

4. **Child parent layout:** If `$PROJECT_ROOT/parent/docs/protocols/` exists, use it.

5. **Create at project root (last resort):** Only if none of the above exist. Do not ask the user to confirm — protocol information must never be lost.
   ```bash
   mkdir -p "$PROJECT_ROOT/docs/protocols"
   ```

---

## Workflows

### CAPTURE (create a new protocol entry)

Use when: a rule or principle should be formalised as a reusable project protocol.
The user provides the directive; CAPTURE scaffolds and writes the entry.

**Step 1 — Generate ID**

```bash
PP_ID="PP-$(date +%Y%m%d)-$(python3 -c 'import secrets; print(secrets.token_hex(3))')"
```

**Step 2 — Derive fields**

Work from what's already known in context. Ask only for what's genuinely unclear.

| Field | Derive from |
|-------|-------------|
| `title` | The directive itself — imperative, one line |
| `type` | `rule` if a concrete prescription; `principle` if directional |
| `scope` | `universal` if any Java/Quarkus project benefits; `platform` if specific to this platform's foundation; `repo` if one repo within the platform; `application` if for apps built on this platform |
| `applies_to` | Which modules, contexts, or conditions trigger this rule |
| `severity` | `critical` if violations cause bugs; `important` if costly; `guidance` otherwise |
| `refs` | Any design docs or related protocols mentioned in context |
| `violation_hint` | What a violation looks like — derive from the problem description |

**Step 3 — Choose a filename**

Derive a descriptive kebab-case slug from the title, e.g.:
`"Use OCC + explicit counters..."` → `occ-threshold-counters.md`

Check for filename conflicts in the protocols directory before writing.

**Step 4 — Draft and confirm**

Draft the full entry (frontmatter + one-paragraph body). Show it to the user:
> "Does this capture the rule accurately?"

Wait for confirmation before writing.

**Step 5 — Write the entry file**

Route to the correct subfolder based on `scope`:
- `scope: universal` → `docs/protocols/universal/<slug>.md`
- `scope: platform` or `scope: repo` → `docs/protocols/casehub/<slug>.md`
- `scope: application` → `docs/protocols/casehub/<slug>.md`

```bash
# Write to the correct subfolder
```

**Step 6 — Commit**

Commit to the protocols garden repo, not the current project repo. Resolve the git root
from the protocols directory:

```bash
PROTOCOLS_GIT_ROOT=$(git -C "$PROTOCOLS_DIR" rev-parse --show-toplevel)
git -C "$PROTOCOLS_GIT_ROOT" add docs/protocols/universal/<slug>.md  # or casehub/
git -C "$PROTOCOLS_GIT_ROOT" commit -m "protocol(PP-YYYYMMDD-xxxxxx): <slug>"
```

**Step 7 — Update the correct index**

Route by the `scope` field:

| scope value | Index to update |
|-------------|----------------|
| `universal` | `docs/protocols/universal/INDEX.md` — add row under the appropriate category section |
| `platform` or `repo` | `docs/protocols/casehub/FOUNDATION-INDEX.md` — add row to the Protocols table |
| `application` | `docs/protocols/casehub/HARNESS-INDEX.md` — add row to the Protocols table |

Row format:
```markdown
| [slug.md](slug.md) | One-line rule summary | applies_to value |
```

For `universal/INDEX.md`, place the row under the most relevant category section
(Maven / Build, Java / Architecture, Quarkus, Application Design). Add a new section
if none fits.

Commit the index update in the same commit as the protocol file.

**Step 8 — Report**

Tell the user the protocol ID, filename, and that it was committed.

---

### SWEEP (scan session for rules worth formalising)

Use at the end of a session or when triggered by handover. Reviews the conversation
for patterns and constraints that should become protocols. Unlike forage SWEEP
(which finds universal technical knowledge), protocol SWEEP finds project-specific
rules that recurred or were enforced informally.

**Step 1 — Scan for implicit rules**

Review the session for:
- "We should always..." or "never..." statements about this project
- Constraints enforced more than once (same rule applied to different files)
- Workarounds that became de facto policy
- Patterns copied across modules without a written source of truth

For each candidate, propose explicitly:
> "We established that [X] — this looks like a standing rule worth formalising as a protocol. Worth capturing?"

**Step 2 — Scan for rule violations discovered**

Review the session for cases where an existing protocol was violated:
- A file was found that broke a rule, was corrected, and the rule re-confirmed
- A new module was set up and had to be taught the same constraint as existing modules

For each: check if the violation_hint on the existing protocol is clear enough.
If not, offer to enrich it via the existing entry.

**Step 3 — Submit confirmed entries**

For each confirmed entry, run CAPTURE Steps 1–8 from context. Do NOT ask the user
to re-describe rules already established in the session.

**Step 4 — Report**

Tell the user: N candidates found, M confirmed and committed. If nothing surfaced:
"No new protocol candidates found in this session."

---

### SEARCH (find protocols by keyword)

Use when: looking for existing rules before writing new code, or when checking
whether a constraint is already formalised.

**Step 1 — Resolve path and search**

Resolve `PROTOCOLS_DIR` using the Locating section above, then search:

```bash
# Search title, applies_to, violation_hint in all protocol files
grep -rli "<keyword>" "$PROTOCOLS_DIR" --include="*.md" | grep -v INDEX | grep -v PENDING
```

**Step 2 — For each match, extract and show the frontmatter**

```bash
# Show frontmatter + first paragraph of body for context
head -20 "$PROTOCOLS_DIR/<match>.md"
```

**Step 3 — Return matches**

Present each matching protocol as:
> **PP-YYYYMMDD-xxxxxx** — `<title>`
> Applies to: `<applies_to>` | Severity: `<severity>`
> `<violation_hint>` (if present)

If no matches: "No protocol found for '<keyword>' in this project."

---

### HEALTH (validate schema completeness and ref integrity)

Use when: checking the state of the protocols directory before adding new entries,
or as a periodic sanity check.

**Step 1 — Count entries**

Resolve `PROTOCOLS_DIR` using the Locating section above, then:

```bash
ls "$PROTOCOLS_DIR"/**/*.md | grep -v INDEX | grep -v PENDING | wc -l
```

**Step 2 — Check required fields**

For each protocol file, verify YAML frontmatter contains all required fields:
`id`, `title`, `type`, `scope`, `applies_to`, `severity`, `created`.

```python
import pathlib, yaml

REQUIRED = {"id", "title", "type", "scope", "applies_to", "severity", "created"}
VALID_TYPES = {"rule", "principle"}
VALID_SCOPES = {"universal", "platform", "repo", "application"}
VALID_SEVERITIES = {"critical", "important", "guidance"}

protocols_dir = pathlib.Path(os.environ["PROTOCOLS_DIR"])  # resolved via Locating section
issues = []

for f in sorted(protocols_dir.glob("*.md")):
    if f.name in ("INDEX.md", "PENDING-MODULE-UPDATES.md"):
        continue
    text = f.read_text()
    if not text.startswith("---"):
        issues.append(f"{f.name}: no YAML frontmatter")
        continue
    parts = text.split("---", 2)
    try:
        fm = yaml.safe_load(parts[1])
    except Exception as e:
        issues.append(f"{f.name}: invalid YAML — {e}")
        continue
    missing = REQUIRED - set(fm.keys())
    if missing:
        issues.append(f"{f.name}: missing fields — {', '.join(sorted(missing))}")
    if fm.get("type") not in VALID_TYPES:
        issues.append(f"{f.name}: invalid type '{fm.get('type')}' (expected: rule, principle)")
    if fm.get("scope") not in VALID_SCOPES:
        issues.append(f"{f.name}: invalid scope '{fm.get('scope')}' (expected: platform, repo)")
    if fm.get("severity") not in VALID_SEVERITIES:
        issues.append(f"{f.name}: invalid severity '{fm.get('severity')}' (expected: critical, important, guidance)")

print(f"\nTotal: {count} protocols")
if issues:
    print(f"Issues ({len(issues)}):")
    for i in issues:
        print(f"  ⚠️  {i}")
else:
    print("✅ All protocols pass schema validation")
```

**Step 3 — Check ref integrity**

For each `refs:` entry in any protocol, verify the referenced file exists:

```bash
# For each ref path in each protocol, check existence
```

Report broken refs as:
> ⚠️ `<protocol-file>` refs `<ref-path>` — file not found

**Step 4 — Report**

```
HEALTH report — docs/protocols/
  Total entries:   N
  Schema valid:    N (or: M issues found)
  Broken refs:     N (or: none)
```

---

### DEEP-SCAN (not yet implemented)

DEEP-SCAN will perform gap analysis, relevance classification, and violation detection
across the protocol layer. It requires the four audits from the Hortora methodology
design to complete first — particularly Audit 2 (convention split: universal vs
casehub-specific) and Audit 3 (folder structure validation).

> **Not yet implemented** — DEEP-SCAN requires Audits 1–4 from
> `spec/docs/design/2026-05-05-hortora-project-knowledge-methodology.md`
> to validate the folder structure and content classification assumptions
> before gap detection can be built. Stub this operation until the audits complete.

---

## Common Pitfalls

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Capturing a universal gotcha as a protocol | Protocols are project-specific | If it applies outside this project, use forage instead |
| Capturing an ADR as a protocol | ADRs are one-off decisions; protocols are standing rules | Use `adr` skill for architectural decision records |
| Leaving refs pointing to non-existent files | HEALTH will flag these; context for future sessions is broken | Run HEALTH and fix broken refs before committing |
| Not updating the correct index after CAPTURE | Index is the fast-path for SEARCH | Route by scope: universal→universal/INDEX.md, platform/repo→casehub/FOUNDATION-INDEX.md, application→casehub/HARNESS-INDEX.md |
| Writing implementation detail in the protocol body | Protocols are directives, not tutorials | refs: out to design docs; keep body to one paragraph |
| Using type=rule for a high-level principle | Misleads readers about expected specificity | `principle` for directional; `rule` for specific + example |

---

## Success Criteria

CAPTURE is complete when:
- ✅ PP-ID generated (`PP-YYYYMMDD-xxxxxx` format)
- ✅ Entry file written to the resolved `PROTOCOLS_DIR/universal/<slug>.md` or `PROTOCOLS_DIR/casehub/<slug>.md` based on scope
- ✅ User confirmed the draft before writing
- ✅ Entry committed to the protocols garden repo (not necessarily the current project repo)
- ✅ Correct index updated and committed in the same commit (routed by scope field)

SWEEP is complete when:
- ✅ Session reviewed for implicit rules and re-enforced constraints
- ✅ Each candidate proposed explicitly before capturing
- ✅ Confirmed entries written via CAPTURE and committed
- ✅ Report given: N candidates found, M captured

SEARCH is complete when:
- ✅ All protocol files searched for the keyword
- ✅ Matching entries returned with id, title, applies_to, severity, and violation_hint

HEALTH is complete when:
- ✅ All files checked for required YAML frontmatter fields
- ✅ type, scope, severity validated against allowed values
- ✅ All refs checked for file existence
- ✅ Summary report given

---

## Skill Chaining

**Invoked by:**
- User directly ("protocol CAPTURE", "add a protocol", "protocol SEARCH", "protocol HEALTH")
- `handover` — protocol SWEEP is added to the wrap checklist alongside forage sweep

**Complements:**
- `forage` — universal technical knowledge; protocol handles project-specific rules
- `adr` — one-off architectural decisions; protocol handles recurring standing rules

**Does NOT handle:**
- Universal garden entries (use `forage`)
- Architectural decision records (use `adr`)
- Content classification or gap analysis (DEEP-SCAN — not yet implemented)

**Protocols location:** Resolved via the Locating section — may be a sibling garden repo (e.g. `casehub/garden/docs/protocols/`), not the current project root. Always commit to the garden repo's git root, not the current project.
