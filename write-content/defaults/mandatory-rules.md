# Blog Writing — Mandatory Rules

These rules apply to every blog entry regardless of author, project, or voice.
They are not style preferences — they are craft constraints that cannot be
overridden by a personal style guide or invocation-time instructions.

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
comfortably in a blog. Either trim to the essential lines (use `// ...` to elide
uninteresting parts), or link to the full source and quote only the interesting section.

**Don't include:** boring setup, trivial getters/setters, standard library calls with
no interesting twist, anything easily reconstructed from the description, complete
file/class dumps.

---

## Images

Images do for a post what code snippets do — they make abstract things concrete and give a post texture that pure prose can't. Apply the same judgment: include when genuinely useful, not to pad.

**Three reasons to include an image:**

1. **UI work → always screenshot** — when the entry is about building or changing a UI, generate a mock screenshot or capture a PNG of the actual interface and include it. Seeing the thing being discussed is worth more than any description of it.

2. **Generated images** — consider whether a diagram, mockup, or generated visual would illustrate something better than prose or code. Architecture decisions, data flows, before/after states — these often benefit from a visual.

3. **Web search** — consider searching for images that make the content more interesting or easier to understand: explanatory diagrams, illustrations, or images that add character. Use judgment on tone — a well-chosen image can do work that words can't.

**Formatting:**
- Resize to content width in the post
- Link the image to its full-size version so readers can click for detail
- Add descriptive alt text

**Image index — when web searching:**

Any image found by web search that is used or considered worth keeping goes into the project's image index at `docs/images/IMAGE-INDEX.md`. This preserves the find for future entries without re-searching.

Each entry:

```markdown
## slug-or-descriptive-title
**Source:** URL
**Description:** What the image shows
**Intent:** What it communicates or why it was found
**Possible uses:** Contexts or topics where it could work
**Used in:** YYYY-MM-DD-NN-entry-slug.md (or "not yet used")
```

Create `docs/images/IMAGE-INDEX.md` on first use with a simple header:
```markdown
# Image Index

Images found for use in blog entries — descriptions, intent, and possible uses.
```

---

## Headings

Thematic headings are primary. Structural labels are scaffolding.

**Priority order:**
1. Already thematic → keep it. `## The --skills flag that didn't exist` is already good.
2. Bare structural slot → add a thematic description: `## What we tried: Three failed approaches`
3. Never trade thematic for structural. `## The Pivots (There Were Several)` → `## What we tried` is always a loss.

**Smell check before committing:**
- Could any H2 appear unchanged in a completely different post? If yes, it's too generic.
- Did a heading change make it shorter and more generic? If yes, revert.
- Does an H2 container have H3s doing all the work? The H2 needs to carry meaning too.

---

## Structure

**No preamble.** Never open with "In this post I will..." or "Today we'll explore...".
Jump straight to the topic.

**No trailing summary.** Don't restate what was just said. Don't add "Thanks for reading."
Don't add a "Next:" template footer. Ends when the point is made.

**No template footers.** `**Next:** ...` is scaffolding, not writing. If there's a
forward-looking note, integrate it as a natural sentence. If there's nothing to say
forward, end on the last real point.

**Series posts (Part 1 of N):** each part is written to stand alone. Series navigation
(← Previous / → Next) is added by `publish-blog` at publish time — not at write time.
A previous part may be revised to link forward once the next part is published.

---

## Content Focus — Write for the Reader, Not the Process

Blog entries are for people who use or evaluate the software. They care about
what was built, why, what was discovered, and what decisions were made. They do
not care how the development process was run.

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
| "I handed execution to the brainstorming skill." | Omit entirely. |
| "Claude reviewed the code before committing." | Omit entirely. |
| "TDD was non-negotiable for this session." | Omit entirely. |

**The test:** Would a developer using this library care about this sentence?
If it's about how the code was produced rather than what it does or why it was
designed that way — cut it.

The exception: if the process IS the subject of the entry (e.g. an entry about
AI-assisted development workflows, written for that audience), name it explicitly
in Step 0 Layer 3 as an invocation override. Otherwise, default is omit.

---

## Factual Accuracy

Diary entries must reflect what actually happened, not a dramatised version of it.

**Never fabricate or inflate:**
- Timeframes ("weeks" when it was days, "months" when it was weeks)
- Scale ("dozens of files" when it was three)
- Difficulty ("fought with X for hours" when it was one attempt)

**Avoid theatrical dramatisation.** The diary voice is direct and honest, not heightened. Don't write as if the stakes were higher than they were. "Everything hung by a thread" when it was a debugging session, "the moment everything changed" when it was a routine decision — these raise the temperature unnecessarily and read as performance. The exception is intentional self-deprecating humour, where the exaggeration is obviously the joke.

If the actual facts feel underwhelming, write them accurately anyway. A reader who later checks git history and finds the timeline doesn't match will lose trust in everything else the entry says. The accurate version is always the defensible one — the only one that survives contact with evidence.

**Verify before writing:** any duration, count, or magnitude claim should be checkable against `git log`, file diffs, or session context. If you can't verify it, either qualify it as an estimate ("roughly a day", "several files") or leave it out.

---

## Third-Party Reference Review — MANDATORY, NEVER SKIPPABLE

This rule applies to every draft, every time. It cannot be skipped due to
invocation context or time pressure. The review process — presenting flagged
sentences and waiting for Keep/Rephrase/Delete — is what gives the author
control. If the author explicitly asked for specific content to be included,
they will choose Keep. The process still runs; it just confirms the intent.

### What triggers a flag

Any sentence that refers to — or makes a statement about — a named person (other
than the author or Claude) or an identifiable group must be flagged before the
entry is written to disk. This includes:

| Category | Examples |
|----------|----------|
| **Opinion** | Any evaluative statement — "X is brilliant", "Y doesn't get it" |
| **Characterisation** | Personality, competence, attitude, approach of a person |
| **Generalisation** | "developers tend to...", "the Java community always...", "managers never..." |
| **Frustration / complaint** | "X was unhelpful", "Y's team doesn't understand this" |
| **Competitive** | Favouring or criticising a product, company, or community in a way that could embarrass |
| **Blame** | "X's decision caused this problem" — even if accurate |
| **Gossip** | Inside knowledge about what someone did, said, or decided that they haven't made public |
| **Presumptuous** | Speaking for someone else's thoughts or motivations — "X probably thought...", "Y clearly doesn't care..." |
| **Reputational** | Anything affecting how someone is perceived professionally, even if factually correct |
| **Overly familiar** | Using private knowledge of someone in a public context |
| **Unsolicited praise** | "X is the best engineer I know" — can embarrass, create jealousy, or read as sycophantic publicly |
| **Political / cultural** | Anything touching politics, nationality, religion, gender, ethnicity |
| **Personal** | Any information the subject might prefer not to be public |

**The test:** If the subject of this sentence read it, could they feel embarrassed,
misrepresented, criticised, patronised, or uncomfortable? If yes — flag it.
**If unsure — flag it.**

### Safe exceptions — no flag needed

These do not need author review:

- **Factual citations** — "X wrote this paper", "Y founded this company"
- **Technical attribution** — "Built on Quarkus, maintained by Red Hat"
- **Public announcements** — "Anthropic released Claude 4", "GitHub open-sourced X"
- **Quoting someone's own public words** — from a blog post, talk, or documentation
- **Tools as tools** — "We used AWS S3", "Built in IntelliJ" — no evaluative statement attached

### The review process — non-negotiable

After drafting and before writing to disk:

1. Scan the complete draft for every sentence containing a reference to a named
   person (other than the author or Claude) or an identifiable group.

2. Present each flagged sentence to the author:

   ```
   ⚠️  Third-party reference — author approval required:

   Sentence: "<exact sentence>"
   Reason flagged: <one-line reason from the category table>

   Options:
     [K] Keep as written
     [R] Rephrase — describe what to change
     [D] Delete this sentence
   ```

3. Wait for the author's decision on each flagged sentence before proceeding.

4. Apply all decisions, then re-scan the revised draft to confirm no flagged
   sentences remain.

5. Only after zero flagged sentences remain may the entry be written to disk.

**There is no shortcut.** If the author is not available to review, do not
write the entry. Hold the draft and wait.

---

## Pre-Draft Gate

Before generating any prose, answer these questions. Do not draft until complete.

**Voice classification:**
- Is Claude a participant? If yes — for each section, decide in advance: "I", "we", or "Claude [verb]"?
- Which moments are Claude-naming moments (catching something, reporting back, going off-script)?
- Is Claude introduced by name before "we" is first used?

**Style guide check:**
- Has the voice layer (common or personal) been loaded?
- After drafting, verify each "What to Avoid" item before presenting.
- Do not show a draft that fails the style guide — fix first.

**Factual accuracy check:**
- Does the draft make any claims about duration, count, or magnitude?
- If yes: verify each one against git log, file diffs, or session context before presenting.
- If unverifiable: qualify as an estimate or remove.

**Third-party reference check — runs after drafting, before writing to disk:**
- Scan the full draft for any sentence referencing a named person (other than
  the author or Claude) or an identifiable group.
- Present every flagged sentence to the author using the review format above.
- Wait for approval on each. Zero unresolved flags before writing.
- This step cannot be skipped, deferred, or abbreviated.
