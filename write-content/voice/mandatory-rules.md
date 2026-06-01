# Voice and Content Policy — Mandatory Rules

These rules apply to every piece of content regardless of form, mode, author,
or voice. They are craft constraints that cannot be overridden by a personal
style guide or invocation-time instructions.

**Process gates** (pre-draft gate, third-party reference review, factual accuracy
enforcement) live in `mandatory-gates.md` at the skill root — not here.

**Structural rules** (heading test, sentence/paragraph rules, element selection)
live in `modes/_universal.md` — not here.

---

## AI Collaboration Voice

### Three registers, used deliberately

**"I"** — for what the author thought, decided, believed, or wanted. Solo perspective only.
> "I expected the PTY work to be the difficult part."

**"we"** — for what the author and Claude built, tried, found, or fixed together.
> "We worked out why together: the PTY line discipline was echoing every byte..."

**"Claude"** (named directly) — when Claude's specific behaviour is worth narrating
in its own right: catching a mistake, reporting a result, going off-spec, flagging
a concern, pushing back, or getting something wrong.
> "Claude came back from manual testing with a one-liner: 'Text appears twice.'"
> "Claude didn't ask about it; it just noted the issue in its report."

### Introduce Claude before using "we"

"We" implies a named collaborator. A reader who hasn't been told Claude is involved
doesn't know who "we" refers to. Claude must appear — by name, in any register —
before "we" can be used.

**Don't — "we" before Claude has been mentioned:**
> "We built both. App 1 got asset scanning."

**Do — introduce Claude first:**
> "I brought Claude in to help with the wiring. We hit the same problem twice before realising it was a config issue."

**Do — name Claude directly first, then "we" flows naturally:**
> "Claude had wired the routes before I noticed the mismatch. We ended up reverting both."

### Vary "we" — avoid repetitive use

Repeated "we" across consecutive sentences reads as a tic. Mix in alternatives:

| Instead of another "we" | Try |
|--------------------------|-----|
| "We also found..." | "Claude and I also found..." |
| "We decided to..." | "Between us, we decided..." / "The decision was to..." |
| "We fixed it by..." | "The fix was..." |
| "We noticed that..." | "Claude flagged that..." / "I noticed that..." |

**Don't:**
> "We built the API layer. We then tested it. We found a bug. We fixed it."

**Do:**
> "We built the API layer. Testing revealed a bug — Claude flagged it during the first run. The fix was a simple backoff."

### When NOT to name Claude

Don't name Claude for routine execution — "Claude implemented PosixLibrary",
"Claude added the endpoint". Use "we" or just describe the outcome. Name Claude
only when its behaviour has character — catching, reporting, going off-script,
pushing back, or getting something wrong.

### Common register mistakes

**"we" as editorial device** — "we'll see why this matters later" — not collaboration,
it's an authorial tic. Change to "I'll return to this" or remove.

**"we" for team or community conventions** — "in Drools, we follow this pattern",
"for this project, we use alpha naming" — if this was a solo design decision or
a convention you followed alone, it's "I chose", not "we". "We" means the author
and Claude did this together.

**"we" for solo design decisions** — if the decision was the author's alone, it's "I",
not "we". The work may have been joint; the decision was singular.

**Third-person protagonist** — "the developer found", "the user believed" — always
becomes "I" or "we". There is no third-person narrator.

### Multiple Claude instances

When different Claude sessions contributed different things, name them distinctly:
> "Three separate Claude instances had each been asked to design the concept. I reviewed all three and synthesised them."
> "A separate Claude audited everything for consistency. It came back with five gaps."

Different sessions are different agents. Don't conflate them into one "Claude".

---

## Code Blocks

Two valid reasons to include a code snippet:

1. **The code IS the explanation** — the reader can't understand the point without
   seeing it. Always include a sentence explaining what it demonstrates.

2. **The code shows off the real thing** — seeing the actual API, DSL, or pattern
   gives readers a feel for the texture of the work. Use when the code is genuinely
   interesting — an elegant interface, a surprising pattern, something that makes the
   reader think "oh, that's how it looks." Not for boilerplate or trivial setup.

**The flavour test:** would a practitioner seeing this code think "that's worth showing"
or "that's just noise"? If the former, include it. If the latter, leave it out.

**Size limit:** if a snippet is more than ~15–20 lines, it's too long to read
comfortably. Either trim to the essential lines (use `// ...` to elide
uninteresting parts), or link to the full source and quote only the interesting section.

**Don't include:** boring setup, trivial getters/setters, standard library calls with
no interesting twist, anything easily reconstructed from the description, complete
file/class dumps.

---

## Images

Images make abstract things concrete and give content texture that pure prose can't.
Apply the same judgment as code blocks: include when genuinely useful, not to pad.

**Three reasons to include an image:**

1. **UI work → always screenshot** — when the entry is about building or changing a UI,
   generate a mock screenshot or capture a PNG of the actual interface and include it.

2. **Generated images** — consider whether a diagram, mockup, or generated visual would
   illustrate something better than prose or code. Architecture decisions, data flows,
   before/after states often benefit from a visual.

3. **Web search** — consider searching for images that make the content more interesting
   or easier to understand. Use judgment on tone.

**Formatting:**
- Resize to content width
- Link the image to its full-size version
- Add descriptive alt text

**Image index — when web searching:**

Any image found by web search that is used or considered worth keeping goes into the
project's image index at `docs/images/IMAGE-INDEX.md`.

Each entry:
```markdown
## slug-or-descriptive-title
**Source:** URL
**Description:** What the image shows
**Intent:** What it communicates or why it was found
**Possible uses:** Contexts or topics where it could work
**Used in:** YYYY-MM-DD-NN-entry-slug.md (or "not yet used")
```

---

## Content Focus — Write for the Reader, Not the Process

Content is for people who use or evaluate the software. They care about what was
built, why, what was discovered, and what decisions were made. They do not care
how the development process was run.

**Unless the user explicitly asks to include it, omit all process and tooling
narration.** This includes:

- How many AI agents, instances, or subagents were used
- Whether TDD, BDD, or any methodology was followed
- Whether code reviews, spec reviews, or quality gates were run
- Whether tasks were executed in parallel or sequentially
- Which Claude skills, tools, or workflows were invoked
- Internal iteration counts ("after 3 attempts", "on the second pass")

**Examples of what to cut:**

| ❌ Cut this | ✅ What the reader actually cares about |
|---|---|
| "I used TDD throughout — write test first, confirm red, implement, confirm green." | The test caught an edge case — describe the edge case. |
| "I dispatched 3 subagents to implement the scenarios in parallel." | The scenarios themselves and what they demonstrate. |
| "A spec reviewer subagent caught the missing dependency." | The dependency issue was non-obvious — explain why. |
| "We ran subagent-driven development with review gates between tasks." | Omit entirely. |
| "Claude reviewed the code before committing." | Omit entirely. |

**The test:** Would a developer using this library care about this sentence?
If it's about how the code was produced rather than what it does or why — cut it.

The exception: if the process IS the subject of the entry (an entry about
AI-assisted development workflows, written for that audience), name it explicitly
as an invocation override at Step 0. Otherwise, default is omit.
