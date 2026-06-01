# Mode: Reference

Look-up content. Three sub-types by reading behaviour — all share the same
core constraint: no prose paragraphs, no narrative, no explanation of why.

---

## Shared rules (all sub-types)

- No prose paragraphs — tables or bullet lists only
- No narrative framing or reader journey
- No explanation of why unless it is itself the referenced fact
- Dense and telegraphic — more so than a human would naturally write
  (this is what makes it feel human; experts write densely)
- One-line descriptions answer "what is this and what does it do"
  not "this file contains X" or "this is used for Y"

---

## Lookup sub-type

The reader knows what they're looking for and wants to find the definition,
value, or specification. Not browsing — retrieving a specific fact.

**Used by:** Glossary entries, API reference, configuration options, flag
definitions, protocol specifications, constant definitions.

**Rules:**
- Term or item name is the label — always bold or a heading
- Definition is one sentence — what it is, not what it's for
- Cross-references use the artifact schema format if defined
- No examples unless the example IS the definition

**Voice texture:**
Right: "`@DefaultBean` — CDI annotation marking a bean as the default;
displaced by any `@ApplicationScoped` implementation without this annotation."
Wrong: "`@DefaultBean` is an annotation that you can use when you want to..."

---

## Pointer sub-type

The reader is directed to an authoritative source that lives elsewhere.
The pointer carries minimal inline content — just enough to know whether
to follow the link.

**Used by:** Crosscutting concept tables, §8 tables in technical documentation,
dependency lists, protocol reference tables.

**Rules:**
- One line per pointer: what the reference covers AND why to go there
- Does not duplicate the referenced content
- Format: `[Reference name] — [what it covers]`
- If the reference requires additional context to use, add one clause:
  `[Reference] — [what it covers]; [key condition or constraint]`

**Voice texture:**
Right: "`flyway-migration-rules.md` — Flyway V-number allocation and H2
compatibility conventions."
Wrong: "For information about Flyway migrations, please refer to
`flyway-migration-rules.md` which contains important guidelines about..."

---

## Inventory sub-type

The reader wants to know what exists — enumerated with one-line descriptions.
Browsing, not retrieving. The list IS the content.

**Used by:** Key files lists in technical documentation layer entries,
directory listings, dependency tables, component rosters.

**Rules:**
- File path / class name / component name → em dash → one sentence
- The sentence answers: "what is this thing and what does it do in this system"
- Not: "this file contains X" (obvious) or "this is used by Y" (wrong focus)
- Sort by reading order when possible — not alphabetically
- Omit entries that add nothing; completeness is not the goal, navigability is

**Voice texture:**
Right: "`review/PrReviewApplicationService.java` — port interface; CDI
displacement boundary for Layer 2+."
Wrong: "`review/PrReviewApplicationService.java` — this file contains the
application service interface that is used as the boundary point for CDI
displacement in later layers."
