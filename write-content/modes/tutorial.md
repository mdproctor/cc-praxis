# Mode: Tutorial

Numbered, domain-agnostic steps for acquiring a capability. The reader does
something and leaves able to do it again independently.

**Distinguished from how-to/procedural:** Tutorial is for learning (reader is
studying, building a capability). Procedural is for working (reader is applying
existing knowledge to complete a task). A tutorial with no learning curve reads
as AI-generated. A procedural that over-explains reads as a tutorial.

**Naming note:** "Tutorial mode" is the constraint set. "Article/tutorial" is the
form sub-type (an Article written for capability acquisition). Technical
documentation "Pattern to replicate" sections also use tutorial mode — they are
not Articles, but they follow the same mode constraints.

---

## Rules

- **Numbered steps** — each step is one action, stated as an imperative sentence
- **One action per step** — if a step has two actions, split it
- **Domain-agnostic language** where the goal is replication — the reader
  should be able to follow these steps in a different domain without translation
- **Zero assumed context** — state every prerequisite; name every dependency
- **Optional "because X" clause** — add when the reason for a step is non-obvious
  and would otherwise cause confusion or wrong substitutions
- **Friction points** — for Article/tutorial, include real stumbling blocks
  ("I got stuck here because..."). For technical documentation, omit personal
  voice but retain the warning ("Ensure X before Y — otherwise Z fails with...")
- **Ends when the reader can do the thing** — no coda, no summary

---

## Structure

```
[One sentence: what capability the reader will have when done]

Prerequisites: [list what must be true / exist before step 1]

1. [Imperative action]. [Optional: because X.]
   [Optional: warning if this step has a non-obvious failure mode]
2. [Next action].
   ...
N. [Final action — the reader now has the capability]
```

---

## Voice texture

Right: "Create a `{domain}-domain` Maven module with zero framework dependencies.
Because `devtown-app` depends on `devtown-domain`, not the reverse — placing CDI
annotations in `domain` would break the dependency rule."
Wrong: vague steps that bundle two actions ("create and configure the module"),
steps that assume context ("add the usual CDI wiring"), steps without completion
signals, steps in passive voice ("the module should be created").

---

## Anti-slop for tutorial

- Each step verb is imperative: Create, Define, Add, Extend, Implement, Annotate
- Prerequisites are explicit — not implied by context
- The "because X" clause uses specific technical reasons, not vague rationale
- Domain names and class names from examples are generic placeholders
  (`{domain}`, `ClassName`) when the goal is replication
- Friction points describe the actual failure mode — not "you might encounter issues"
