# write-content

Universal content creation skill. Presents a guided Q&A to determine what you're writing, how to structure it, and how it should sound — then applies the right rules before and after generation.

---

## Using It

Invoke the skill and answer the Q&A. Four questions maximum, single-letter answers, defaults marked.

**Worked example — writing a diary entry:**

```
What are you writing?
  [D] Diary  ←
> D (or Enter)

Voice?
  [P] Personal — mark-proctor-voice.md  ←
> P (or Enter)

Writing:  Diary — Explanation/discursive
Voice:    Personal (mark-proctor-voice.md)
```

**Worked example — writing a Gotchas section for arc42stories:**

```
What are you writing?
  [T] Technical documentation
> T

Which section?
  [2] Gotchas  →  How-to/diagnostic
> 2

Voice?
  [P] Personal — mark-proctor-voice.md  ←
> P (or Enter)

Writing:  Tech doc / Gotchas — How-to/diagnostic
Voice:    Personal (mark-proctor-voice.md)
```

**Auto-routing** skips Q1 when the invocation is unambiguous — "write a diary entry", "write the Gotchas section for layer X", "write the Pattern to replicate" route directly without asking.

After the Q&A, the skill loads the relevant files and runs the pre-draft gate before generating anything.

---

## The Three Layers

Every piece of content is defined by three independent choices, each answered by the Q&A:

| Layer | Q&A question | What it determines | Where the rules live |
|---|---|---|---|
| **Form** | Q1 — What are you writing? | Structure, length, audience, when to use | `forms/` |
| **Mode** | Q2/Q2b — Sub-type or section | How information is presented | `modes/` |
| **Voice** | Q3 — Voice? | How it sounds | `voice/` + personal style |

These are orthogonal. A diary entry (form) uses explanation/discursive mode with Mark Proctor's personal voice. An arc42stories Gotcha section (technical documentation form) uses how-to/diagnostic mode with common voice. Choosing a form doesn't determine the mode; choosing a mode doesn't determine the voice.

**Why three layers?** "Writing style" was doing the work of all three simultaneously — which is why per-type guidance never felt quite right. Separating them makes the rules precise and composable.

---

## Complete Form × Mode Mapping

Every valid combination. The Q&A routes to exactly one row.

| Form | Sub-type | Mode | Mode file |
|---|---|---|---|
| Diary | — | Explanation/discursive | `modes/explanations.md` |
| Note | musing | (form-defined) | — |
| Note | idea | (form-defined) | — |
| Article | tutorial | Tutorial | `modes/tutorial.md` |
| Article | how-to / procedural | How-to/procedural | `modes/how-to.md` |
| Article | how-to / diagnostic | How-to/diagnostic | `modes/how-to.md` |
| Article | explanation / discursive | Explanation/discursive | `modes/explanations.md` |
| Article | explanation / comparative | Explanation/comparative | `modes/explanations.md` |
| Article | commentary | (form-defined) | — |
| Article | essay | Argumentation/essay | `modes/argumentation.md` |
| Brief | — | Reference/lookup | `modes/reference.md` |
| News | — | (form-defined) | — |
| Tech doc | "What it adds" | Explanation/comparative | `modes/explanations.md` |
| Tech doc | Gotchas | How-to/diagnostic | `modes/how-to.md` |
| Tech doc | Key files | Reference/inventory | `modes/reference.md` |
| Tech doc | Key wiring | Reference/lookup | `modes/reference.md` |
| Tech doc | Pattern to replicate | Tutorial | `modes/tutorial.md` |
| Tech doc | Architectural decisions | Argumentation/rationale | `modes/argumentation.md` |
| Tech doc | ADRs | Argumentation/decision | `modes/argumentation.md` |
| Tech doc | Anti-patterns | How-to/diagnostic | `modes/how-to.md` |
| Tech doc | §8 crosscutting table | Reference/pointer | `modes/reference.md` |

**(form-defined)** means the mode is implicit in the form file — no separate mode file is loaded. These forms are simple enough that the form file already encodes the structural character.

`modes/_universal.md` is always loaded first, for every row.

---

## Modes

Mode is the structural constraint set — how information is organised and presented. The Q&A selects the mode; the mode file tells the skill what structure to apply.

### What each mode prescribes

**Tutorial** (`modes/tutorial.md`)
Numbered imperative steps. One action per step. Zero assumed domain knowledge. Ends when the reader can do the thing.
*Used for: Article/tutorial, tech doc Pattern to replicate*

**Explanation/discursive** (`modes/explanations.md`)
Author-centric. Personal voice allowed. Analogies from unexpected domains. "I used to think X, but it turns out Y." No length cap — ends when the mental model is complete.
*Used for: Diary, Article/explanation (concept)*

**Explanation/comparative** (`modes/explanations.md`)
System-centric. Before:/After: contrast as the organising principle. Hard length cap (2–4 sentences + bullets). No personal voice. Explicit "Not closed here" scope boundary.
*Used for: Tech doc "What it adds", §9.3 "What this delivers"*

**How-to/procedural** (`modes/how-to.md`)
Steps from a working state toward a goal. Goal stated upfront. Warnings and edge cases included. "Why this step, not that" where non-obvious.
*Used for: Article/how-to*

**How-to/diagnostic** (`modes/how-to.md`)
**Symptom:** what the reader actually sees. **Cause:** root mechanism, not the symptom restated. **Fix:** exact action — no hedging, no "might", no "generally".
*Used for: Tech doc Gotchas and Anti-patterns*

**Reference/lookup** (`modes/reference.md`)
Find a specific term or fact. Tables and bullets only. No prose paragraphs. No explanation of why.
*Used for: Brief, tech doc Key wiring, Glossary*

**Reference/inventory** (`modes/reference.md`)
Enumerate what exists. `path/to/File.java` — one sentence: what it is and what it does. Not "this file contains X" — that's obvious.
*Used for: Tech doc Key files*

**Reference/pointer** (`modes/reference.md`)
Points to authoritative content elsewhere. One line per reference: what it covers and why to go there. Does not duplicate the referenced content.
*Used for: Tech doc §8 crosscutting table*

**Argumentation/rationale** (`modes/argumentation.md`)
"Why X rather than Y: reason. Tradeoff: what X costs." One paragraph. No hedging the conclusion.
*Used for: Tech doc Architectural decisions*

**Argumentation/decision** (`modes/argumentation.md`)
ADR format: Context → Decision → Consequences. Names the alternative considered. States tradeoffs including unwanted consequences.
*Used for: Tech doc ADRs*

**Argumentation/essay** (`modes/argumentation.md`)
Extended argument over numbered sections. Opens with a claim. Three appeals in priority order: logos (evidence), ethos (credibility), pathos (passion). Counter-arguments addressed inline. Ends without hedging.
*Used for: Article/essay*

### Form-defined forms (no mode file)

Note/musing, Note/idea, Article/commentary, and News load only voice files. Their structural character is defined in the form file itself — brief enough that a separate mode file adds nothing.

### Recognising wrong-mode output

If generated prose reads as AI-sounding despite clean banned-word lists: check the mode. The underlying cause of AI-sounding prose is **mode mismatch** — content that requires How-to/diagnostic was generated in Explanation/discursive. Wrong mode generates wrong structure; wrong structure generates the prose patterns we associate with AI output. The mode selects the structure; the structure prevents the banned patterns from appearing in the first place.

---

## Anti-Slop Rules

Anti-slop operates at two levels.

### Universal rules (`voice/anti-slop.md`)

Applies to everything regardless of form, mode, or voice:

**Banned words:** delve, tapestry, realm, crucible, nuanced, intricate, game-changer, groundbreaking, transformative, leverage (verb), synergy, seamlessly, holistic, robust, paradigm, cutting-edge, innovative, exciting journey

**Banned patterns:**
- Opening with "In this post/article I will..."
- Closing with "In conclusion..." or "Thanks for reading"
- Hedging with "it's worth considering that" or "one might argue"
- Superlatives without evidence ("the best", "the most powerful")
- Theatrical dramatisation ("everything hung by a thread")
- Starting consecutive sentences with "This" or "It"
- Generic filler: "It's important to note", "It's worth mentioning"

### Per-mode voice texture

Each mode file ends with a "Voice texture" section — Right: / Wrong: examples specific to that mode. These are not in `voice/anti-slop.md` because they differ by mode:

- Explanation/comparative: specific class names and verbs ("displaces", "fires"). Wrong: gerund openings, chained dashes, passive voice
- How-to/diagnostic: Fix statements cannot use "might", "could", "generally". Wrong: softening the action
- Reference/inventory: telegraphic, denser than a human would naturally write. Wrong: narrative framing, "this file contains X"

### Per-form voice guidance

Note, Article, Brief, and News form files each have a "Voice by sub-type" section. Article/commentary, News — voice-forward, no mode file, character comes from the form.

---

## Pre-Draft Gate (Step 2)

Runs after the Q&A and before any prose is generated. Shows an explicit checklist — **do not proceed to writing until all four items show ✅**.

```
Pre-draft gate:
☐ Voice classified — I/we/Claude register decided per section
☐ Content focus checked — process narration removed
☐ Factual accuracy checked — durations/counts verified
☐ Banned words scanned — anti-slop.md applied
```

**Voice classification** — for diary, article, note, brief, news: decide "I", "we", or "Claude [verb]" for each section before drafting. The I/we/Claude register system (in `voice/mandatory-rules.md`) is the most violated rule — classifying it at the gate prevents mid-draft confusion.

For technical documentation: confirm target section, its mode, and that the correct mode file is loaded. No I/we/Claude register — tech docs are system-centric, no author-as-participant.

**Content focus** — strips process narration before it gets written. Sentences about build passing, test counts, methodology followed, agent counts, which skills were invoked — these are how the code was produced, not what the reader cares about. The gate removes the instinct before the draft, not as a post-draft edit.

**Factual accuracy** — any claim about duration, count, or magnitude must be verifiable against git log, file diffs, or session context. If unverifiable, qualify as an estimate or remove. Unverified timeframes ("weeks" when it was days) destroy reader trust when they check the git history.

**Why a gate, not a reminder?** Post-draft editing for these issues is harder and less reliable than preventing them. The gate converts implicit rules into an explicit checkpoint that cannot be skipped.

---

## Quality Check (Step 4)

Runs after the draft is written, before anything is shown or saved.

**Scan test:** strip all labels (bold lead-ins, headings, structured prefixes) and read only those in sequence. The result should be a complete factual skeleton with no gaps. A fact that only exists in prose body text is invisible to scanning — and invisible to LLMs loading the document for session context.

**Mode check:** does the output match the declared mode? Gotcha → Symptom/Cause/Fix structure. Key wiring → bold lead-in + 1–3 sentences per point. "What it adds" → Before:/After: then bullets. A mode check catches structural drift that the gate can't prevent.

**Human-sound check:** no banned words, no AI structural patterns from `voice/anti-slop.md`.

**Intent check:** right form, right audience, ends when the point is made. A diary entry shouldn't read like an article. An article shouldn't require the reader to have been there.

**Third-party review** (from `mandatory-gates.md`) — after drafting and before writing to disk: scan the complete draft for any sentence referencing a named person (other than the author or Claude) or an identifiable group. Present each flagged sentence with Keep / Rephrase / Delete. Zero unresolved flags before writing to disk. This cannot be skipped.

---

## File Reference

### Mode files

| File | Modes |
|---|---|
| `modes/_universal.md` | All — scannability, heading test, element selection, sweet spot principle |
| `modes/explanations.md` | Discursive / Comparative |
| `modes/how-to.md` | Procedural / Diagnostic |
| `modes/reference.md` | Lookup / Pointer / Inventory |
| `modes/argumentation.md` | Decision / Rationale / Essay/sustained |
| `modes/tutorial.md` | Tutorial |

### Form files

| File | Form |
|---|---|
| `forms/diary.md` | Diary — project narrative, in-the-moment |
| `forms/note.md` | Note — musing (quick reaction) or idea (specific proposal) |
| `forms/article.md` | Article — full treatment for wider audience |
| `forms/brief.md` | Brief — maximum density, scanning is the experience |
| `forms/news.md` | News — external event or announcement |
| `forms/technical-documentation.md` | Technical documentation — multi-mode, maintained alongside system |

### Voice files

| File | What it governs |
|---|---|
| `voice/anti-slop.md` | Universal banned words and patterns |
| `voice/common-voice.md` | Default voice — peer-to-peer, opinionated, intellectually honest |
| `voice/mandatory-rules.md` | I/we/Claude register; code block rules; image rules; content focus |
| `mandatory-gates.md` | Pre-draft gate and third-party review (process control, not voice) |

---

### Common voice

`voice/common-voice.md` is the fallback when no personal style file is configured. It gives functional prose that is clear and credible without prescribing a specific personality:

- **Peer to peer** — practitioner talking to other practitioners; not a teacher simplifying for beginners
- **Opinionated and direct** — states positions clearly; no hedging with "it might be the case that"
- **Intellectually honest** — includes failed attempts, wrong turns, genuine uncertainty
- **Not deferential about Claude** — neither party is infallible; write it as it actually happened

Common voice produces good prose. It won't sound like a specific person — that's intentional. It's the baseline everyone starts from.

---

### Personal voice

If you write regularly, create a personal style file. The Q&A will detect and offer it automatically. It composes with any form and mode — personal voice loads on top of common voice, overriding where they conflict.

**Where it lives:** `~/claude-workspace/writing-styles/`

**What to put in it:**

A personal style file captures the things that make your writing recognisably yours — not rules, but fingerprints:

- **What you always say** — phrases, constructions, rhythms that recur. "The thing is..." / "Which means..." / short punchy declaratives before longer technical ones.
- **What you never say** — words or constructions you actively avoid. "Robust", "leverage", "paradigm" may already be in anti-slop, but yours might be subtler.
- **Sentence length pattern** — do you default long and technical? Short and declarative? Mixed? At what rhythm?
- **Audience assumptions** — how much prior knowledge do you assume? Do you name tools without explanation?
- **Characteristic stance** — opinionated and direct? Measured and careful? Self-deprecating when warranted? How do you handle uncertainty?
- **What to avoid in your specific voice** — not universal anti-slop, but the things *you* drift toward when unguarded (over-hedging, excessive caveats, over-explaining, starting too many sentences with "I")

The more specific, the better. "Peer to peer, opinionated" is common voice. "Opens with the observation before the claim, tends to short paragraph breaks, uses 'which means' to chain technical consequences, allows typos and rough edges in notes" is personal voice.

**Loading it:**

The skill checks `~/claude-workspace/writing-styles/` at Step 0. If files are found, it offers `[P] Personal` as the Q3 default. You can have multiple files for different content types (e.g. `blog-technical.md` for blog posts, `mark-proctor-voice.md` for the linguistic fingerprint layer) — the skill lists them and loads the most relevant one.

If no file exists, `voice/common-voice.md` loads instead. No configuration needed — presence or absence of the file is the switch.

---

## Theoretical Background

The Form/Mode/Voice taxonomy converged independently with four established frameworks developed across 200 years. Newman (1827) called modes "rhetorical modes." Kinneavy (1969) called them "aims." Britton (1970) called them "functions." Diátaxis (2017) called them "types." All four arrived at the same underlying set of distinctions from completely different starting points with no knowledge of each other. Kinneavy, finding the same convergence across eight scholars in 1969, called it "almost fearful symmetry."

The term **mode** comes from Newman and Anker — deepest lineage (1827) and already in the four-dimension framework this skill builds on.

**The multi-mode document** — every framework assumes a document has one mode. Technical documentation (arc42stories, CLAUDE.md, platform guides) has multiple modes across sections. None of the five frameworks address this. write-content addresses it by declaring a mode map per multi-mode form, allowing the correct mode to be selected per section.

Full research notes: `docs/content-taxonomy-article-notes.md` in the cc-praxis project repo.
