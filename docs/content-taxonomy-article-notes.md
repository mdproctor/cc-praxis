# Content Taxonomy — Working Notes

**Status:** Notes — not yet drafted into either output
**Date:** 2026-05-13
**Source:** Session conversation on content writing and blog styles

These notes serve two distinct outputs:
- **The Article** — practitioner-facing, accessible, tells the discovery story
- **The Paper** — academic, formal proposal to unify Newman and Diátaxis into a cohesive framework

Sections marked `[ARTICLE]`, `[PAPER]`, or `[BOTH]` indicate which output they serve.

---

## The Arc `[BOTH]`

Started from a practical complaint. Ended at Samuel Newman, 1827.

The journey is the story. And the journey is shaped by a deliberate intellectual habit: when approaching an unfamiliar problem, start from first principles. Not because the existing literature doesn't matter — it does — but because arriving at your own understanding first means you know what you're looking for when you go to find it. Once the first-principles work has produced something coherent, the pivot is to find existing well-grounded work that either validates, refines, or challenges it.

This is not the fastest route. It is the most honest one.

The content taxonomy work went this way because there was no prior grounding in content taxonomy theory to draw on. The problem was approached as a practitioner problem — colleagues won't read this, what needs to change — not as a theoretical one. The theory came later, after the structure had emerged from practice. And when it came, it landed with more force than it would have if found first: not "here is a framework, let's apply it" but "here is a framework — and we arrived at the same place independently."

The pivot that drives the story:

1. **Colleagues won't read it** — the practical trigger
2. **First instinct: blame the style guide** — reasonable, wrong
3. **The real problem: two independent issues compounding**
   - Industry-wide: dense prose is now an AI trigger — readers dismiss it before engaging
   - Personal: a prose-led style, when applied by AI without the natural brevity instinct, amplifies exactly the worst characteristics of AI content
   - Neither problem alone explains the failure. Together, they make it nearly inevitable.
4. **That sends us looking for something better** — which leads to the forms, the taxonomy, and eventually Newman, 1827

Without the compounding problem, the story is "style guide was wrong, we fixed it." That's not interesting. The real story is: the style guide wasn't wrong — AI broke the assumption it depended on.

---

## Act 1 — Two Problems, One Failure `[BOTH]`

The trigger: colleagues finding content too wordy, too long, hard to engage with. Not occasionally — consistently. Good content, carefully written, being ignored.

The first instinct was to look at the style guide. It actively discouraged structure:
- "Bullet lists used sparingly"
- "Lists never dominate (~21% overall, never above 30%)"
- "Prose is the default; lists are for enumeration, not structure"

Reasonable instinct. Wrong diagnosis.

The style guide came from corpus analysis of 577 blog posts written 2006–2017. It captured a real voice — one that evolved over a decade from raw exploratory lab notes into something more strategic and precise. By the mature phase: short sentences, short paragraphs, peer-to-peer directness, opinionated positions defended with evidence, genuine enthusiasm for the technology, intellectual honesty about uncertainty. No hedging. No summarising what was just said. Ending when the point was made.

The median post was 129 words. The writing stopped when the point was made. The prose-led style was held honest by a natural brevity instinct — and by something harder to encode: the voice of a practitioner who actually cared about the work, writing to peers who also cared. That credibility came through in the precision, the willingness to name disagreements directly, the self-deprecation when warranted.

AI doesn't have that instinct. It takes the surface characteristics of the voice — connected prose, flowing argument, no lists — and applies them at the length AI naturally produces, without the judgment that made the style work. The brevity disappears. The precision softens into elaboration. The personal credibility, which only existed because a real person was making real claims from real experience, evaporates — leaving the form without the substance that justified it.

But there's a second problem, independent of the first.

**Dense connected prose is now an AI trigger.**

Readers have been conditioned — quickly and probably permanently — to associate long paragraphs, flowing connective prose, and elaborate sentence structures with AI-generated output. The format carries the association regardless of who wrote it. A significant portion of readers disengage before evaluating whether the argument is good.

This is a fundamental shift in the reading contract. Before LLMs, dense prose signalled effort and expertise — a human spent time on this, it is worth your attention. Post-LLM, that signal has been corrupted. The format that once implied quality now implies "machine output — probably not worth reading."

The contamination is environmental, not individual. It is the statistical consequence of billions of words of AI-generated content flooding the written landscape, most of it characterised by exactly those features. Readers learned the pattern. They now apply it automatically.

**The compounding effect:**

| Problem | Source | Effect alone |
|---------|--------|-------------|
| AI drops the brevity instinct | Style + AI | Prose runs longer than it should |
| Dense prose triggers AI dismissal | Environmental | Readers disengage from prose-heavy content |
| **Combined** | Both at once | Content reads as maximally AI-generated, even when the argument is good |

The style guide wasn't wrong. AI broke the assumption it depended on — that the writer knows when to stop.

The concrete evidence: devtown#24. Two versions of the same content — a prose deep-dive and a compact version with bullets and tables. Same information. Colleagues refused to read the prose version. Engaged immediately with the compact one. Not because the prose version was worse. Because it triggered dismissal before they reached the argument.

**This is not about dumbing down.** It is not about shorter attention spans. It is about a format signal that now works against the writer, regardless of intent or quality. The solution is not to write worse arguments — it is to find forms that carry good arguments without triggering the association.

---

## Act 2 — Discovering the Forms Through Practice `[ARTICLE]`

The compact version of devtown#24 had clear characteristics:
- Two-sentence problem statement
- Tables for comparisons and status tracking
- Bold lead-ins instead of topic sentences
- Diagram for flow
- Open questions as a flat list
- No narrative walk-throughs in the main body

This wasn't just "shorter prose." It was a **different mode of writing** — one where structure carries information rather than prose.

Named it: **InfoBrief** (short for Informative Brief).

The defining characteristic: *scanning IS the experience*. There is no deeper layer to pull the reader into. What you see on scan is all there is.

This contrasted with everything else we were writing, where scanning is the **entry point** — it surfaces enough for a reader to decide whether to go deeper.

From there, additional forms emerged through examination of existing content:

- **Note** — session diary, to the point, no background or conclusion. Records what happened.
- **Article** — full treatment of a topic. Background, concepts, standalone readable.
- **Essay** — has a position. Hypothesis, counter-arguments, conclusion. Tries to move the reader.
- **InfoBrief** — maximum information density, minimum prose. Scanning IS the experience.

Multi-part applies to both articles and essays.

---

## Taxonomy Classification Rules — Refined Through Corpus Validation `[BOTH]`

These rules emerged from classifying 577 real posts against the taxonomy. They refine the definitions and provide tests for edge cases.

### Note/log = coding/development log only

**Log is not a general diary.** It records technical work — coding sessions, algorithm progress, benchmark results, test milestones, API progress. NOT:
- Conference attendance or event recaps
- Personal travel or off-topic observations
- Job postings or community announcements
- Download stats or subscriber counts
- Link posts or external content shares

### Note vs Article — craft and audience intent, not privacy

**Notes are still public** — they have an audience. The distinction is effort and craft:
- **Note**: quick, rough, less shaped for a reader — assumes the reader can follow without hand-holding
- **Article**: crafted for a wider audience — provides the context and structure a reader needs

A Note written fast that you expect a small audience to read. An Article written with the expectation that many people will read it.

### Article/commentary = wider audience catch-all

**If you intend a wider audience for it, but it doesn't fit tutorial/how-to/explanation/essay, it's Article/commentary.** Even if it's off-topic, observational, or doesn't argue a position — the intent to reach a wider audience is the determining factor.

> Example: "[Off Topic] Back from my honeymoon" (252) — has the off-topic disclaimer (signalling public awareness), intended for wide readership → Article/commentary, not Note/musing

### Note/musing = catch-all for short informal Notes that aren't log or idea

Quick, rough, encoder-dominant. Can be:
- Internal thinking out loud
- Pointing at external content and reacting briefly  
- A casual observation or reaction
- A brief community announcement intended for a small/known audience

### Cross-posting — primary determination

When a post has two genuine types, use three tests to determine primary:
1. **Strip test** — which type survives if the other is removed?
2. **Intent test** — what was the author's main goal?
3. **Structure test** — which type's conventions does the post follow?

> Example: "Argentina June Workshop - Volcano update" (371) — informing event attendees of late arrival (News/event primary) with personal amusing tone (Note/musing secondary)
> Example: "Washington Rules!" (011) — substantive narrative review of an event (Article/commentary primary) that happens to cover an event (News/event secondary)

### Article/explanation = showcase category

Feature demonstrations, New and Noteworthy posts, and capability showcases are **Article/explanation** — they explain/demonstrate what a feature does. If tied to a release, cross-post with News/release as secondary.

### News/event scope

News/event covers all of these:
- Pre-event announcements ("I'm speaking at JavaOne next week")
- Event information shares — slides, videos, agenda posted after the event
- Brief event recaps — "sold out", "full house", photos, mid-event updates
- Boot camp logistics, venue announcements, registration reminders

News/event does NOT cover:
- A full narrative review of what happened at the event, with impressions, named people, technical observations → **Article/commentary** (primary) + News/event (secondary if genuinely present)

### Thin showcase rule

A post that is just one sentence + a video link or slide link — regardless of how interesting the underlying content is — is **NOT an Article**. Classify as News/release (if tied to a release), News/event (if tied to an event), or Note/musing.

The content needs to actually explain or demonstrate something in the post itself to qualify as Article/explanation.

> Example: "Build Pong in 13 minutes using JBoss Drools" (451) — one sentence + YouTube link → News/release, not Article

### Guest posts — classify by content, not authorship

Whether a post was written by a guest or by Mark doesn't affect classification. Classify by what the content does, not who wrote it.

> Example: "Rule Analytics - Looking at the AST" (042) — guest post by a student, but contains substantive technical analysis → Article/explanation

### Conference recaps — the spectrum

| Content | Classification |
|---------|---------------|
| "Here are my slides from X" | News/event |
| "Here are photos from Day 1 of X" | News/event |
| "Full house at the session" + brief note | News/event |
| Full narrative: who was there, what was discussed, vendor impressions, technical insights | Article/commentary primary + News/event secondary |

### InfoBrief — nearly absent historically

In the 577-post historical corpus, only 3 genuine InfoBriefs were found. InfoBrief is a **new form** not represented in the historical writing style. Do not force posts into InfoBrief — if in doubt, classify elsewhere.

### Canonical examples from corpus validation

| Post | Classification | Rule illustrated |
|------|---------------|-----------------|
| 007 — Rete with Lazy Joins | Article/explanation ⭐ | Deep technical explanation with Forgy correspondence |
| 011 — Washington Rules! | Article/commentary + News/event | 780w conference narrative with vendor impressions, named people, technical insights → Article primary. Strip the event context and the narrative still stands. |
| 042 — Rule Analytics (guest post) | Article/explanation | Guest post by a student — classify by content (substantive technical analysis), not authorship |
| 108 — A Vision for Unified Rules and Processes | Article/essay ⭐ | Landmark argued position — defines the KIE platform thesis |
| 189 — Drools 5.0 M5 New and Noteworthy | Article/explanation + News/release | 700w comprehensive feature walkthrough → Article primary. Tied to a release → secondary. |
| 228 — Drools Blog gains over 1000 subscribers | Note/musing | PR/community milestone — short, informal, not crafted for wide audience |
| 230 — Drools: a reflection on 5 years | Article/essay ⭐ | Reflective milestone essay — historically important primary source |
| 249 — Some articles from Java Beans dot Asia | Article/commentary | Curating external content for a wider audience → Article, not Note. Intended for broad readership. |
| 252 — [Off Topic] Back from my honeymoon | Article/commentary | Off-topic personal travel — but off-topic disclaimer signals public awareness; intended for wide readership → Article/commentary, not Note/musing |
| 257 — My first look at Drools (ORF09 feedback) | Article/commentary + News/event | Commentary about an event — shares impressions of the bootcamp → Article primary. Event context → secondary. |
| 369 — CEP Operators in Guvnor | Article/explanation + News/release | Feature showcase with enough substance (screenshots, explanation) → Article primary. Tied to a release → secondary. |
| 371 — Argentina Volcano update | News/event + Note/musing | Informing event attendees of late arrival (functional purpose) → News/event primary. Personal amusing tone → secondary. Strip event context: nothing remains. |
| 387 — Why you should learn Drools (job ad) | Note/musing | PR observation/job market signal — same pattern as subscriber count posts; not crafted for wide audience |
| 411 — The Decision Model IP Trap | Article/essay ⭐ | Argued position with evidence, addresses counter-arguments, concludes |
| 450 — Drools 5.4: AI History | Article/explanation ⭐ | Broad-audience primer — most intellectually ambitious explanatory post in corpus |
| 451 — Build Pong in 13 minutes | News/release | One sentence + YouTube link → thin showcase, not Article |
| 508 — R.I.P. RETE time to get PHREAKY | Article/explanation ⭐ | Flagship technical deep-dive — corpus centrepiece |
| 568 — BRMS/BPMS 7.0 Roadmap | Article/essay ⭐ | Rare strategic transparency — unusually candid product roadmap |
| 577 — KIE Community welcomes IBM | Article/commentary ⭐ | Landmark closing post of the corpus |

---

## Cross-Posting Rules `[BOTH]`

Cross-posts are rare. A post has one primary type and optionally one secondary type.

**When to cross-post:** Only when both types are genuinely present AND the secondary meaningfully changes how the content should be written or indexed. If the secondary is a weak echo of the primary, classify primary only.

**The primary test — three questions in order:**

1. **Strip test** — if you removed the secondary element, would the primary still work as content on its own? The one that survives stripping is secondary; the one that doesn't work without context is primary.
2. **Intent test** — what was the author's main goal? What would the reader lose if they only got the primary type?
3. **Structure test** — which type's conventions does the post follow structurally?

**Format:** `primary_type/primary_subtype + secondary_type/secondary_subtype`

**Canonical examples:**

| Example | Classification | Why |
|---------|---------------|-----|
| "CEP Operators in Guvnor" (369) — showcases a Guvnor feature tied to a release | `Article/explanation + News/release` | Primary: explains/demonstrates the feature. Secondary: tied to a release. |
| "Argentina June Workshop - Volcano update" (371) — informs attendees of late arrival, with amusing personal voice | `News/event + Note/musing` | Primary: functional event update for attendees. Secondary: personal amusing tone. Strip the event context and nothing remains. |
| "Build Pong in 13 minutes using JBoss Drools" (451) — one sentence and a YouTube link | `News/release` only | Too thin for Article. No secondary needed. |

**Showcase posts:**
- A showcase with enough substance (explanation, screenshots, code) → `Article/explanation` primary
- A showcase tied to a release → `Article/explanation + News/release`
- A thin showcase (one sentence + video link) → `News/release` only — not enough for Article

---

## The Taxonomy — Final Form (for article use) `[ARTICLE]`

*Naming confirmed: "essay" — recommended by Grok, consistent with all five academic frameworks, natural alongside tutorial/how-to/explanation/commentary.*

### Taxonomy table

| Type | Intent | Subtypes |
|------|--------|---------|
| **Note** | Capture — quick, informal, encoder-dominant | log, musing, idea |
| **Article** | Inform or argue — full treatment, crafted for a cold reader | tutorial, how-to, explanation, commentary, essay |
| **InfoBrief** | Maximum information density, minimum prose | standalone or linked |
| **News** | Something happened externally worth sharing | release, event, industry |

### Each term explained

**Note** — quick, informal, close to the writer. Assumes shared context. Less shaped for a cold reader than an article. Quick by nature — not necessarily short, but not laboured over.
- **log** — records what happened. The development diary, the session notes. Chronological, first-person, factual account of work done.
- **musing** — short, informal, encoder-dominant piece that is neither a record nor a developed proposal. Can be internal thinking out loud or a brief external reaction (link + quick take, quote + personal comment). Low investment, not fully formed.
- **idea** — developed enough to propose something specific. "We should do X because Y." A musing that has crystallised into a specific proposal.

**Article** — full treatment of a topic, standalone readable. Background is provided; a cold reader can follow without prior context. Crafted for the audience, not just for the writer.
- **tutorial** — learn by doing. The reader acquires a capability through guided practice. Sequential, hands-on, the reader does something.
- **how-to** — task completion. The reader applies existing capability to accomplish a specific goal. Practical, step-oriented, assumes some prior knowledge.
- **explanation** — understand why. Builds the reader's mental model of a concept, system, or decision. Not about doing — about understanding.
- **commentary** — informed take on a topic. Personal voice, expertise-led, no formal thesis or structured conclusion. The author has a view and shares it discursively.
- **??? (essay/thesis/case)** — argued to a conclusion. Clear position, builds evidence, addresses counter-arguments, reaches a conclusion. "When the Machine Codes" is the canonical example — six parts, a thesis that Python is the wrong default for LLM-first development, argued and concluded.

**InfoBrief** — maximum information density, minimum prose. Fully scannable — scanning IS the experience. Two modes:
- **Standalone** — self-contained, no deeper layer. The full picture at a glance.
- **Linked** — navigation layer into a longer piece. Each section, paragraph, even bullet can link to the corresponding deep-dive in an accompanying article or essay. Becomes the TLDR with links throughout.

**News** — something happened externally worth sharing. Not the author's work — something in the world.
- **release** — software release, new version, new feature. What changed and why it matters.
- **event** — conference, talk, meetup. Announcement or recap.
- **industry** — observation on something happening in the broader landscape. IBM, Nvidia, open source trends.

---

### Academic mapping table

| Our type | Newman (1827) | Kinneavy (1969) | Britton (1970) | Diátaxis (2017) |
|----------|--------------|-----------------|----------------|-----------------|
| Note/log | Narration | Expressive/individual — explicitly names "diaries" | Expressive | — |
| Note/musing | Narration | Expressive/individual | Expressive — "close to the self" | — |
| Note/idea | — | Referential/exploratory — "proposing solutions" | Expressive | — |
| Article/tutorial | Exposition | Referential/exploratory | Transactional | Tutorial |
| Article/how-to | Exposition | Referential/informative | Transactional | How-to |
| Article/explanation | Exposition | Referential/scientific | Transactional | Explanation |
| Article/commentary | — | Referential/exploratory | Transactional | — |
| Article/essay | Argumentation | Persuasive aim | Transactional | — |
| InfoBrief | Description | Referential/informative | Transactional | Reference |
| News | — | Persuasive/transactional | Transactional | — |

*Five frameworks — developed independently across 200 years from completely different starting points — converging on the same underlying taxonomy. Kinneavy (1969) called this "almost fearful symmetry" when he found it across 8 scholars. We are extending his observation by 57 years and two new domains.*

---

## Act 3 — The Structured Essay: A Form Discovered in Revision `[ARTICLE]`

"When the Machine Codes" — a 6-part series — revealed a distinct form through the revision process.

The headings did double duty:
```
## 1. At Generation Time: The Token Cost Argument
## 2. At Review Time: Static Read-Through Reliability
## 4. The Call to the Industry
```

Not purely structural. Not purely thematic. Both at once. The number gives position in the argument; the phrase gives meaning. The **hybrid heading pattern** — discovered through revision, not design.

Other characteristics:
- **Bold lead-ins** announcing turns: "A fair counter:", "The type hint caveat, stated fairly:"
- **Counter-arguments addressed inline** — not deferred to a separate objections section
- **Italic preambles** at the start of each part — orient the reader without recapping

Named it: **Structured Essay**.

---

## Act 4 — Scannability as a Universal Principle `[BOTH]`

Scannability isn't a property of one form. It's a **cross-cutting requirement** that applies to all content.

Every piece of content should allow a reader to scan it and decide whether to go deeper. The InfoBrief satisfies the reader at the scan level. Everything else uses scannability as the entry point.

This resolved a false tension between "structured" and "readable" content. You don't choose between them — you use structure to make content readable at multiple levels simultaneously.

---

## Act 5 — The Taxonomy Emerges From Intent `[BOTH]`

Tried to name the forms by their characteristics (prose vs structured, long vs short). Kept running into edge cases. "Structured" describes how something looks, not why it exists. Length is irrelevant — a note can be long if the session had a lot going on; an essay can be short if the argument is tight.

The breakthrough: organise by **intent**, not by format.

Three distinct intents, each with a test:

| Intent | Test | Content type |
|--------|------|-------------|
| "I want to inform you of X" | Delivers facts, findings, what happened | Note, InfoBrief |
| "I want you to understand X" | Builds mental model, explains why | Article |
| "I want you to believe X" | Argues a position, earns a conclusion | Essay |

**Note:** Records what happened — to the point, no background or conclusion. It doesn't carry context for a reader who came cold — it's addressed to someone who already knows the context. Size follows the session: if a lot happened, the note is longer. Not artificially limited. The note is often the seed of an article — the article gives the same content background, concepts, and conclusion for readers who didn't live through it.

**Article:** Full treatment of a topic. Background, concept explanation, standalone readable. Doesn't need a hypothesis or conclusion — it's not trying to convince you of anything. "Here's something cool." "Here's how to do Z." "Did you know about Y?" An article could be informative only — not there to convince, just to explain or show. From a website navigation perspective, articles and essays are the same category (both published under Articles/Writing). The distinction is in the writing form, not the site structure. Multi-part applies when scope requires splitting — each part standalone, together complete.

**Essay:** Has a position. Earns its hypothesis, counter-arguments, and conclusion — because it's trying to move the reader. Proposals, arguments, persuasive pieces — all essays. The "When the Machine Codes" 6-part series is an essay: it opens with a claim and spends six parts proving it. Argumentative (evidence and expertise), not persuasive (emotional appeals). Multi-part applies.

**InfoBrief (Informative Brief):** Maximum information density, minimum prose. Self-contained by default — scanning IS the experience, there is no deeper layer. The devtown#24 compact version is the canonical example. Optional navigation layer: when a longer form exists (an article or essay), the InfoBrief can link its sections, paragraphs, and bullets to the corresponding deeper content — making it a navigable entry point to the full argument. This pattern is a content architecture innovation: the InfoBrief becomes a structured index that satisfies the scanner and routes the engaged reader directly to what they care about, bypassing everything else. The navigation layer is opt-in, not a requirement of the format.

**The critical distinction for the article:** Note and InfoBrief share the same intent (inform) but different forms. The note has voice, narrative, and personal credibility. The InfoBrief strips to pure information density, structured for instant consumption. Both inform; they serve different readers in different contexts.

**What doesn't determine content type:**
- Length — irrelevant; a note can be longer than an essay
- Structure — irrelevant; an InfoBrief is highly structured but so can an essay be
- Audience — irrelevant for type determination; both note and essay can address technical peers

---

## Act 6 — The Moment of Recognition `[BOTH]`

The first-principles work had run its course. Time for the pivot — find existing well-grounded work that validates, refines, or challenges what emerged from practice.

Found two frameworks:

**Diátaxis** (Daniele Procida, ~2017) — four documentation types:
- Tutorial (learning by doing)
- How-to guide (task-oriented)
- Reference (factual lookup)
- Explanation (understanding why)

The uncomfortable part: Quarkus uses Diátaxis for its own documentation. It was right there, in the ecosystem, applied daily. Not noticed — because it was categorised as "documentation framework" and mentally filed as irrelevant to blog and article writing. The domain silo did the work that ignorance didn't need to.

**Rhetorical Modes** (Samuel P. Newman, 1827):
- Narration
- Exposition
- Description
- Argumentation

The mapping:

| Our taxonomy | Newman 1827 | Diátaxis |
|-------------|-------------|---------|
| Note | Narration | — |
| Article | Exposition | Tutorial + Explanation |
| Essay | Argumentation | — |
| InfoBrief | Description | Reference |

We had independently arrived at a taxonomy that maps directly onto work from 1827. And the modern equivalent had been in plain sight the entire time.

---

## Encoder/Decoder Theory — The Theoretical Basis for Note vs Article `[BOTH]`

*Source: Kinneavy (1969) communication triangle, validated by Grok independently reaching for the same terminology when analysing the taxonomy.*

### The framework

Kinneavy's communication triangle has four corners:
- **Encoder** — the writer/speaker
- **Decoder** — the reader/listener
- **Signal** — the text itself
- **Reality** — the subject matter the text refers to

Each aim of discourse foregrounds a different corner. Applied to our content taxonomy:

| Type | Dominant corner | Why |
|------|----------------|-----|
| Note/log | **Encoder** | Author records for themselves or a known audience; assumes shared context |
| Note/musing | **Encoder** | Author thinking out loud or reacting briefly; not shaped for a cold reader |
| Note/idea | **Encoder** | Author proposing for their own exploration; not yet crafted for an audience |
| Article/tutorial | **Decoder** | Entirely structured around the reader's learning journey |
| Article/how-to | **Decoder** | Structured around the reader's task completion |
| Article/explanation | **Decoder** | Structured around the reader's understanding |
| InfoBrief | **Reality** | The information dominates; neither encoder nor decoder foregrounded |
| News | **Reality** | Pointing at external facts in the world |

### Where it gets fuzzy

- **Article/commentary** — quite encoder-dominant (personal voice, author's take) but crafted for a public audience. Sits between encoder and decoder.
- **Article/essay** — the *position* is the encoder's, but the *argument structure* is shaped for the decoder. Both at once.

### The operationally reliable test

Encoder/decoder dominance is a useful approximation, not a universal rule. The more reliable operational test for Note vs Article is:

> **Does the content assume shared context (Note) or provide sufficient context for a cold reader to follow (Article)?**

This maps onto encoder/decoder dominance without being identical to it. A Note/musing about an external article (posts 220 and 239) is still encoder-dominant — the author's brief reaction is the content, and the reader is assumed to be able to follow a link. An Article/commentary on the same topic would explain the context and develop the argument for a reader who wasn't there.

### Why this matters for LLMs

When an LLM is asked to write a Note, it should write encoder-first: the author's voice, perspective, and reaction dominate. Assume the reader shares context. Don't over-explain.

When an LLM is asked to write an Article, it should write decoder-first: provide sufficient background, define terms, structure for a reader who comes cold. The author's voice is still present but the reader's needs shape the structure.

This distinction is more reliable than word count or structure as a guide to register and tone.

---

## Why Newman and Diátaxis Are Complementary, Not Competing `[BOTH]`

| | Newman (1827) | Diátaxis (2017) |
|--|---------------|-----------------|
| **Organises by** | Author intent — what is the writing trying to do? | Reader need — what does the reader need to accomplish? |
| **Scope** | All writing — fiction, non-fiction, academic, informal | Documentation specifically |
| **Perspective** | Author-centric | Reader-centric |
| **Coverage** | Narration, exposition, description, argumentation | Tutorial, how-to, reference, explanation |

Newman covers the full range — including essay (argumentative) and note (narrative), which have no Diátaxis equivalent. Diátaxis adds a refinement Newman misses: within the article form, tutorial (learning by doing) vs explanation (understanding why) are genuinely different reader needs.

**The synthesis:** Newman is the foundation — intent-based, all content types, 200 years proven. Diátaxis is a refinement layer — reader-need thinking, most useful within the article form. Complementary, operating at different levels.

---

## Five Independent Arrivals `[PAPER]`

The convergence is more extensive than initially identified. Five independent frameworks arrived at overlapping taxonomies across 200 years, driven by completely different problems, with no evidence any was aware of the others at the point of creation:

| Who | When | Starting point | Arrived at | Domain |
|-----|------|---------------|------------|--------|
| Newman | 1827 | First principles — classical rhetoric | Narration, exposition, description, argumentation (5 modes, later simplified) | All writing/rhetoric |
| Kinneavy | 1969 | First principles — discourse theory; communication triangle | Expressive, referential, literary, persuasive | All discourse |
| Britton | 1970 | Educational psychology — Vygotsky; how children develop writing | Transactional, expressive, poetic | Child/educational writing development |
| Procida | ~2017 | Practical problem — Django CMS docs disorganised | Tutorial, how-to, reference, explanation | Software documentation |
| This work | 2026 | Practical problem — colleagues won't read it | Note, article, essay, InfoBrief | Technical practitioner content |

**On Procida's origins:** Developed Diátaxis from practical problems with Django CMS documentation — the team found that topic-based structures were arbitrary and didn't serve users. Primary influence was Jacob Kaplan-Moss (a Django colleague), not academic rhetoric. Procida has a philosophy background but no reference to Newman, Kinneavy, or classical rhetorical theory found anywhere in his writing. He is a philosopher who rediscovered rhetoric without naming it — driven entirely by the question of what users need.

**On Kinneavy as the missing link:** Kinneavy's 1971 work predates Diátaxis by 46 years. His communication triangle provides the theoretical foundation that Diátaxis implements in practice — the decoder corner of Kinneavy's triangle is precisely what Diátaxis puts at the centre of its framework. Procida implemented what Kinneavy had theorised without knowing the theoretical precedent existed.

**The significance of four independent convergences:** The convergence across 200 years, four independent starting points, and completely different domains — rhetoric pedagogy, discourse theory, software documentation, practitioner blogging — is not coincidence. It suggests the taxonomy reflects something structurally true about the relationship between writing and readers. Every time someone has thought carefully about why people write and what readers need, they have arrived at the same underlying set of distinctions.

---

## The Gap in the Literature `[PAPER]`

**Direct search results:**
- Zero publicly indexed pages contain "rhetorical modes" and "Diátaxis" together. Not a paper, not a blog post, not a discussion thread.
- Zero pages connect Kinneavy and Diátaxis.
- Zero pages connect Newman and Diátaxis.

No academic work has:
- Explicitly connected Newman's rhetorical modes to Diátaxis
- Explicitly connected Kinneavy's communication triangle to Diátaxis
- Proposed a unified framework spanning any of these
- Applied any of these frameworks to practitioner technical content (blogs, essays, articles)
- Used rhetorical theory to improve LLM content generation guidance

Diátaxis is practitioner-originated and has not yet generated substantial peer-reviewed academic literature.

---

## MacArthur (2025) — Full Reading Notes `[PAPER]`

**Full citation:** MacArthur, M. (2025). Large language models and the problem of rhetorical debt. *AI & SOCIETY*, 40, 6425–6438. https://doi.org/10.1007/s00146-025-02403-w

**Author:** Marit MacArthur, University of California, Davis (mjmacarthur@ucdavis.edu). Background: digital humanities, writing across curriculum (WAC), computer science collaboration.

**Published:** Received 30 March 2025. Accepted 19 May 2025. Published online 25 June 2025.

**Access:** OPEN ACCESS — Creative Commons Attribution 4.0 International Licence. Can be quoted directly without copyright concerns.

---

**Rhetorical debt — exact definition (p.6432):**
> *"not quite right [writing] which we postpone making … right"* — *"writing in haste, we do not critically edit a text to suit our audience, purpose, genre and context, or when we lack the expertise to so edit it—and more recently, when we uncritically use AI-generated text"*

**Fluency fallacy — exact definition (p.6432):**
> *"the erroneous attribution of accuracy, expertise and authority to a given text or speaker based on the use of normative grammar, idiomatic syntax and vocabulary, and conventional style"*

**LLM limitation — key quote (p.6428–6429):**
> *"There are defined limits on the local rhetorical context they can assess, in part because they rely on language alone."*
> *"Texts are 'true' only in the right context.... [Yet LLMs] operate in a space where meaning is constructed rather than retrieved from elsewhere."*

---

**MacArthur's five tasks (stated in introduction):**
1. Redefine "training data" (= human expertise captured in writing) and "prompt engineering" (= prompt *writing*)
2. Review scholarship on what constitutes writing and what it means to teach writing
3. Reflect on long-term trends in professional software development — code sharing, automation
4. Identify the fundamental problem of rhetorical debt and outline its consequences
5. Argue for the new economic value of expert writing — necessitating revaluation of the humanities

**What she does NOT do:**
- Does NOT address how rhetorical frameworks could improve LLM content generation guidance
- Does NOT address content taxonomy or content types
- Does NOT connect Kinneavy's four aims to documentation or Diátaxis
- Does NOT propose a practical framework for practitioners

---

**Kinneavy's presence in MacArthur (p.6429):**
Cited in a list: *"the rhetorical dimensions of writing, with specific attention to audience (Burke 1950; Corbett 1965; Perelman and Oblrechts-Tyteca 1958; Murphy 1972; **Kinneavy 1971**)"*

Cited in passing as part of the historical rhetorical tradition — not the centrepiece of her argument. Confirms: Kinneavy is available in the rhetorical tradition MacArthur operates in, but she doesn't connect him to documentation or Diátaxis.

**Newman — NOT mentioned anywhere.**
**Anker — NOT mentioned anywhere.**
**Diátaxis — NOT mentioned anywhere.**

---

**Bitzer (1968) — The Rhetorical Situation — key connection:**
MacArthur uses Bitzer to redefine prompt engineering (p.6429):
> *"Writing instructions for a probabilistic text-generating machine, detailing the immediate rhetorical situation (Bitzer 1968) — the purpose, audience(s), guidelines for the genre, and the real-world, local context — which the machine cannot access without human guidance, because the LLM is not embedded in the immediate physical, social, cultural, political world in the which the prompting human lives."*

Bitzer's rhetorical situation (purpose, audience, genre, context) is structurally very close to Kinneavy's communication triangle (encoder, decoder, signal, reality). MacArthur is using Bitzer to describe what LLMs lack — which is precisely what Kinneavy's decoder-centred framework and Diátaxis's reader-need framework address. Our paper can make this connection explicit.

Bitzer full citation: Bitzer LF (1968) The rhetorical situation. *Philos Rhet* 1(1):1–14. [JSTOR](https://www.jstor.org/stable/40236733)

---

**Key new citation from MacArthur's references — Juszkiewicz et al. (2019):**
Juszkiewicz J, Warfel J, Losh E, Buehl J, Maher JH, Burgess HJ, Menzies T, Brock K, Omizo RM, Clark I, Nguyen MT (2019) *Rhetorical machines: writing, code, and computational ethics.* University of Alabama Press, Tuscaloosa.

**This is significant** — a book explicitly connecting rhetoric to computational/AI contexts. May be relevant to our paper. **Action: search this separately.**

**Other relevant citations from MacArthur:**
- Brock K (2019) *Rhetorical code studies: discovering arguments in and around code.* University of Michigan Press — rhetoric + code
- Burke K (1950, 1969) *A rhetoric of motives.* University of California Press
- Corbett EPJ (1965) *Classical rhetoric for the modern student.* Oxford University Press
- Perelman C, Oblrechts-Tyteca L (1958, 1969) *The new rhetoric: a treatise on argumentation.* Notre Dame
- Robbins S (2025) "What machines shouldn't do." *AI Soc.* https://doi.org/10.1007/s00146-024-02169-7 — also in *AI & Society*

---

**The Boeing 737 Max / Tesla examples (p.6433):**
- Boeing 737 Max disasters — 346 killed in Indonesia (2018) and Ethiopia (2019), cost $20 billion+. Flight manual failed to mention the MCAS automated feature because Boeing assumed experienced pilots would never need to know. Wrong audience assumption — classic rhetorical failure.
- 177 Max 9 airplanes grounded in 2024 when door plug burst open at 16,000 feet
- Tesla Cybertruck — 8 recalls since launch; font on warning lights too small to comply with safety standards

These are powerful examples of consequential documentation failure from lack of rhetorical awareness. Not just a stylistic issue — people die. Directly supports the argument that rhetorical grounding in content creation matters.

---

**The fluency fallacy — two directions:**

MacArthur identifies one direction: readers TRUST LLM output because it is fluent — when they shouldn't.

Our observation adds the mirror: readers DISTRUST human output because it RESEMBLES LLM fluency — when they shouldn't.

Same root cause — the fluency signal has been corrupted by association. MacArthur diagnoses the trust direction; we observe the distrust direction. Together they describe the complete disruption of the fluency-as-expertise signal. This is a genuine addition to MacArthur's framework.

---

**How our paper relates to MacArthur — precise positioning:**

| | MacArthur (2025) | Our paper |
|--|-----------------|-----------|
| **Problem** | LLMs create rhetorical debt — fluency without rhetorical awareness | LLM content guidance lacks rhetorical grounding — heuristics without theory |
| **Scale** | Systemic/societal/educational | Practical/content-design |
| **Prescription** | Reinvest in humanities education; revalue expert writing | Apply rhetorical frameworks to LLM content generation guidance |
| **Audience** | Educators, policymakers, humanities scholars | Technical practitioners, content strategists, prompt engineers |
| **Rhetorical tradition** | Bitzer, Kinneavy (in passing), Burke, Corbett | Newman, Kinneavy (centrepiece), Anker, Diátaxis |
| **Diátaxis** | Not mentioned | Core framework |

**Positioning:** MacArthur diagnoses rhetorical debt at the systemic level. We address the same debt at the practical level. Same journal (*AI & Society*), same conversation, constructive extension at a different scale.

---

## The Central Argument — Augmenting Heuristic-Based Evolution `[BOTH]`

This is the core claim that holds the paper and Part 5 of the series together. It needs to survive a skeptical reviewer. The framing matters enormously.

**The wrong version (doesn't survive scrutiny):**
> "The industry's LLM content heuristics are undisciplined rediscoveries of 200-year-old theory that nobody thought to apply."

Fails because: the heuristics have legitimate empirical origins (Nielsen Norman, UX research, cognitive load theory); the mapping is post-hoc; "nobody thought to apply it" is unverified.

**The right version (defensible):**
> "The industry has been developing LLM content guidance through empirical evolution — heuristics that work, refined through practice. What it lacks is theoretical direction. Rhetorical theory, developed across 200 years and independently rediscovered four times, provides exactly that — not to replace the heuristics, but to guide their evolution toward principled, context-sensitive practice."

**Why this framing works:**

The heuristics evolved through legitimate empirical observation — UX research (Nielsen Norman), readability studies, practitioner trial and error. That evolution is real and valuable. But evolution without theoretical direction is undirected: it produces rules that work in some contexts and fail in others, with no principled way to know which is which.

Rhetorical theory provides the **selection pressure** that directed evolution lacks:
- It explains *why* each heuristic works
- It identifies *when* each applies and when it doesn't
- It provides *transferable* principles rather than context-free rules

**How it resolves the key challenges:**

| Challenge | Resolution |
|-----------|-----------|
| "The heuristics come from UX research, not rhetoric" | Not competing — UX research is empirical evidence of what works; rhetorical theory explains why. Nielsen Norman tells you "short paragraphs work." Kinneavy tells you why — and therefore when they don't. |
| "The mapping is post-hoc" | Reframed as forward-looking: not "the heuristics were derived from rhetoric" but "rhetoric can direct their future development." |
| "The practical claim is vague" | Now precise: the framework provides the tutorial/how-to discrimination that undifferentiated heuristics can't. Same setting — different reader need — different guidance. |
| "Technical communicators already know this" | The gap is specifically in the LLM content guidance industry — prompt engineers, AI product teams, content strategists writing about generative AI — not in academic technical communication. |

**The MacArthur symmetry:**
- MacArthur (2025): LLMs have rhetorical debt — fluency without rhetorical awareness
- We observe: the guidance being used to reduce that debt also has rhetorical debt — heuristics without rhetorical theory
- Our proposal: augmenting heuristic-based evolution with rhetorical theory addresses both simultaneously

**The canonical example — tutorial vs how-to:**
This is the strongest worked example because it shows the framework producing guidance the heuristics cannot:

A heuristic says "use bullet points and short paragraphs for process content." Diátaxis distinguishes tutorial (learner acquiring capability) from how-to (practitioner applying capability). For the tutorial, narrative structure and sequential prose may serve better — the learner needs to build mental models, not complete tasks. For the how-to, bullets and short paragraphs are exactly right — the practitioner needs to scan and act. The heuristic applies both identically. The framework discriminates. That discrimination is the value.

**What evidence strengthens this claim:**
1. Academic database search confirming the gap (JSTOR, MLA International Bibliography, *Technical Communication* journal) — currently only web-searched
2. Additional worked examples beyond tutorial/how-to showing the framework discriminating where heuristics cannot
3. MacArthur (2025) as independent confirmation that the rhetorical dimension of LLM content is undertheorised
4. Nielsen Norman et al. as citation establishing the empirical tradition we are augmenting, not replacing

---

## The LLM Content Generation Guidance Gap `[PAPER]`

**What the search for "how to make LLMs generate better content" actually found:**

Almost none of the results address the actual question. The dominant body of material is about **GEO (Generative Engine Optimization)** — how to write your own content so that LLMs *cite it* in their responses. This is a completely different problem: not "how do we make LLMs write better" but "how do we get LLMs to notice and reference our writing."

The actual guidance on improving LLM output quality — when found at all — is entirely **heuristics-based and atheoretical**:

| Industry heuristic | Rhetorical grounding (unstated) |
|-------------------|--------------------------------|
| Use short paragraphs (2–3 sentences max) | Newman's mature style; Kinneavy's situational awareness |
| Use bullet points liberally | Anker's process analysis structure; Diátaxis's reference format |
| Lead with the conclusion (answer-first) | Classical rhetoric — argumentatio before narratio |
| Use tables for comparisons | Diátaxis's referential discourse; Anker's comparison/contrast mode |
| Back claims with data and citations | Logos first — Aristotle, operationalised by Kinneavy |
| Define entities clearly | Anker's definition mode |
| Structure content with descriptive H2/H3s | Hybrid heading pattern — discovered independently in this work |

Every heuristic being recommended by the industry maps directly onto established rhetorical theory — but the industry has no awareness of this. The heuristics are undisciplined rediscoveries of what Newman, Kinneavy, Anker, and Diátaxis already know, applied without theoretical grounding, and therefore without principled guidance on *when* each applies and *why*.

**The consequence of atheoretical guidance:**

Practitioners are told "use short paragraphs" without being told that short paragraphs serve different functions in a how-to guide (Diátaxis) vs an argumentative essay (Newman's argumentation). They're told "use bullet points liberally" without understanding that bullets fragment continuous reasoning and should not be used when ideas connect and build on each other. The heuristics work in some contexts and fail in others — and without the theoretical grounding, practitioners don't know which contexts are which.

**This is the practical argument for the paper:**

The unified framework (Newman → Kinneavy → Anker → Diátaxis → this work) doesn't just connect academic dots. It provides the theoretical grounding that LLM content generation guidance currently lacks. A practitioner who understands that they are writing expository/referential content for a reader who is at work (not studying) knows to use Diátaxis's how-to format, short paragraphs, and task-oriented structure — and knows *why*, not just *that*. The framework makes the heuristics principled.

**The paper argument in full:**

1. MacArthur (2025) diagnoses: LLMs create rhetorical debt through fluency without rhetorical awareness
2. We observe: industry guidance on improving LLM output is the same debt — heuristics without rhetorical theory
3. We show: those heuristics map directly onto Newman → Kinneavy → Anker → Diátaxis
4. We identify: four independent frameworks addressing complementary dimensions of the same problem — connected for the first time
5. We propose: ground LLM content generation guidance in established rhetorical theory — producing principled, context-sensitive guidance rather than undifferentiated rules
6. We demonstrate: the unified framework applied to practitioner technical content (note, article, essay, InfoBrief) — showing how intent × mode × reader need × form produces content-type-specific guidance that generic heuristics cannot

**Risk assessment of this argument:**

This is a strong argument. It is:
- Grounded in a documented gap (zero connections between these frameworks)
- Supported by a companion diagnostic paper (MacArthur 2025) that establishes the problem
- Practical — addresses a real guidance failure in the industry
- Constructive — proposes a solution, not just a diagnosis

The main risk: the paper could be perceived as making a claim (the unified framework improves LLM output) without empirical validation. Mitigation: frame the unified framework as a proposal and research agenda, not a proven intervention. MacArthur also makes diagnostic claims without empirical validation — the genre supports theoretical argument.

---

## The Paper Proposal `[PAPER]`

**Title candidates:**
- *Toward a Unified Content Taxonomy for Technical Practitioners: Bridging Rhetorical Theory and Documentation Practice*
- *Rhetorical Theory and LLM Content Generation: Connecting Newman, Kinneavy, and Diátaxis*
- *From Rhetorical Debt to Rhetorical Practice: A Unified Framework for LLM-Era Technical Content*

The third title positions us explicitly as the constructive complement to MacArthur (2025).

**Thesis:** Four independent frameworks — Newman (1827), Kinneavy (1971), Anker (~1998), and Diátaxis (2017) — have arrived at overlapping taxonomies of content and discourse across 200 years, driven by entirely different problems, with no awareness of each other. Each addresses a distinct orthogonal dimension of the same underlying problem. The industry guidance currently being offered to improve LLM content generation is an atheoretical rediscovery of what these frameworks already know — producing heuristics that work in some contexts and fail in others because practitioners lack the theoretical grounding to know when each applies. This paper connects these frameworks for the first time, proposes a unified model, and argues that grounding LLM content generation guidance in established rhetorical theory would produce principled, context-sensitive practice.

**The four dimensions:**

| Dimension | Framework | Question answered |
|-----------|-----------|------------------|
| **Intent** | Newman (1827) | What is the writing trying to do? |
| **Communicative aim** | Kinneavy (1971) | What element of the communication situation is foregrounded? |
| **Mode** | Anker (~1998) | What type of writing is this? |
| **Reader need** | Diátaxis (2017) | What does the reader need to accomplish? |
| **Form + scannability** | This work (2026) | What structure serves intent, aim, mode, and reader need simultaneously? |

**Core contributions:**
1. First explicit connection between Newman, Kinneavy, Anker, Britton, and Diátaxis
2. Extending Kinneavy's own "almost fearful symmetry" observation (1969) across 55 additional years and two new domains — the convergence he named now spans eight to thirteen independent frameworks
3. The Kinneavy bridge: Diátaxis implements Kinneavy's referential aim, precisely subdivided — exploratory = tutorial, scientific = explanation, informative = reference
4. Newman restoration: Bain (1866) collapsed persuasive/argumentative; the distinction matters and should be restored
5. Five independent convergences demonstrating the taxonomy reflects structural truth about writing and readers — from rhetoric, discourse theory, educational psychology, software documentation, practitioner content
6. The LLM content guidance gap: industry heuristics are atheoretical rediscoveries — principled grounding would improve them
7. Scannability as a cross-cutting structural requirement (with grounding in Nielsen Norman UX research)
8. Application to practitioner technical content — a domain no existing framework explicitly addresses

**Positioning relative to MacArthur (2025):**
MacArthur diagnoses: LLMs create rhetorical debt through fluency without rhetorical awareness.
We propose: grounding LLM content guidance in established rhetorical theory addresses this debt constructively.
Same tradition, opposite orientation. Explicitly position as constructive complement.

**Target journals (priority order):**
1. *AI & Society* (Springer) — MacArthur published here; natural home for the constructive response
2. *Technical Communication* (STC) — primary practitioner journal in the field
3. *IEEE Transactions on Professional Communication* — strong technical communication home
4. *Journal of Technical Writing and Communication* — good fit for the taxonomy work
5. *Advances in the History of Rhetoric* — if framing the Newman/Kinneavy lineage as centrepiece

---

## Newman — Important Nuance `[PAPER]`

Newman's original taxonomy had **five** modes, not four:
> *"didactic, persuasive, argumentative, descriptive, and narrative"*

The simplification to four came later (Bain, 1866). Crucially — Newman distinguished **persuasive** (appeals to will/emotion) from **argumentative** (appeals to reasoning faculties). This maps directly to the Common Core distinction and to our own: argumentative writing appeals to evidence and expertise; persuasive writing appeals to emotion.

This nuance was lost in the later simplification and is worth restoring in the unified framework.

---

## The Evolution of Newman — Where Subsequent Work Fits `[PAPER]`

Newman's taxonomy evolved through two centuries of scholarship. Understanding where each development sits clarifies what to build on and what the unified framework contributes.

**Bain (1866) — a regression, not an improvement:**
Bain collapsed Newman's five modes to four by merging persuasive and argumentative. Newman's original distinction — persuasive appeals to the will/emotion; argumentative appeals to the reasoning faculties — is the more precise and useful one. Our framework restores it. Bain's simplification has persisted in writing instruction for 150 years despite losing a meaningful distinction.

**Anker (~1998 onwards) — sub-mode elaboration within exposition:**
Anker's nine modes (*Real Writing with Readings*, Bedford St. Martin's, multiple editions) organised by purpose group:

| Purpose group | Anker modes | Newman mapping |
|--------------|------------|---------------|
| Writing to show and tell | Narration, Description | Narration, Description — direct |
| Writing to analyze and explain | Process analysis, Classification, Definition, Illustration | Exposition sub-types |
| Writing to reason and persuade | Comparison/contrast, Cause and effect, Argument | Argumentation + Exposition sub-types |

The top-level intents do not change. Anker adds granularity within exposition — she does not introduce new fundamental intents.

---

## Kinneavy — The Missing Link `[PAPER]`

**Primary citation (prefer over the book):**
Kinneavy, J.E. (1969). "The Basic Aims of Discourse." *College Composition and Communication*, Vol. 20, No. 5, pp. 297–304. JSTOR: [jstor.org/stable/355033](http://www.jstor.org/stable/355033). PDF in Downloads.

**Book (for deeper reading):**
Kinneavy, J.L. (1971). *A Theory of Discourse: The Aims of Discourse*. Prentice-Hall. [Internet Archive (free)](https://archive.org/details/theoryofdiscours0000kinn)

---

**The paper is far more significant than anticipated. Two extraordinary findings:**

### Finding 1 — Kinneavy himself documented the convergence and called it "almost fearful symmetry"

In Figure 1 of the paper, Kinneavy compiled a comparison table showing multiple independent scholars arriving at the same taxonomy: Aristotle and Aquinas, Cassirer, Morris (semiotician), Miller (communication theorist), Russell, Reichenbach, Richards, and Bühler/Jakobson.

His conclusion — direct quote (p.303):
> *"The important lesson to be drawn from this almost fearful symmetry is that no composition program can afford to neglect any of these basic aims of discourse."*

**This changes our paper fundamentally.** We are not the first to observe the convergence — Kinneavy documented it in 1969 across eight scholars. Our paper extends his observation across an additional 55 years and two new domains (software documentation practice and practitioner technical content). We are adding to a pattern he already named.

### Finding 2 — Kinneavy's referential aim maps to Diátaxis with precision

The referential aim has three explicit sub-types (Figure 2):

| Kinneavy referential sub-type | Examples | Diátaxis equivalent |
|-------------------------------|---------|---------------------|
| **Exploratory** | Dialogues, seminars, proposing solutions, diagnosis | **Tutorial** — learning by doing, open-ended exploration |
| **Scientific** | Proving points, generalising from particulars | **Explanation** — understanding why, theoretical grounding |
| **Informative** | News articles, reports, summaries, textbooks | **Reference** — factual lookup |

And separately:
| **Persuasive** | Advertising, political speeches, editorials | **—** (documentation doesn't persuade) |

Kinneavy's subdivisions of the referential aim are the direct theoretical foundation of Diátaxis's four types — more precisely than we had previously stated. Procida subdivided Kinneavy's referential aim by reader need (learning vs working) — and arrived at the same categories.

---

**The communication triangle — Figure 2:**

Encoder (writer/speaker) — Decoder (reader/listener) — Signal (linguistic product) — Reality (universe referred to).

Each aim foregrounds a different corner. Discourse dominated by Reality = referential. Dominated by Decoder = persuasive. Dominated by Signal = literary. Dominated by Encoder = expressive.

**Expressive examples in Figure 2 are revealing:**
*Of Individual:* conversation, journals, **diaries**, gripe sessions, prayer.
Our **Note** form maps exactly to Kinneavy's expressive/individual aim — a diary recording what happened, for the writer as much as any reader.

---

**The principle of classification was itself independently discovered:**

Kinneavy acknowledges (p.301):
> *"At one time I thought that this principle of classification was original with me, but I later found that Karl Bühler, a German psychologist, had used it in depth in the 1930's and that Roman Jakobson... had also used it to classify aims of discourse in the early 1960's."*

Independent convergence documented within the paper itself.

---

**Updated Kinneavy → Diátaxis mapping (more precise than before):**

| Kinneavy aim/sub-type | Diátaxis type | Precision |
|----------------------|--------------|-----------|
| Referential — Exploratory | Tutorial | High — both are about open learning and discovery |
| Referential — Scientific | Explanation | High — both are about understanding why |
| Referential — Informative | Reference | High — both are factual lookup |
| Persuasive | — | No Diátaxis equivalent |
| Expressive | — | No Diátaxis equivalent (but = our Note) |
| Literary | — | No Diátaxis equivalent |

**The remaining gap:** Kinneavy doesn't distinguish tutorial from how-to (both are exploratory/referential). Diátaxis adds the learning/working discrimination — the one thing Kinneavy's framework doesn't provide.

---

**The Kinneavy critique — worth addressing in the paper:**
Later scholarship (Fulkerson 1984) noted that aims aren't cleanly separable — scientific papers have persuasive aims. Kinneavy himself addresses this (p.297-298): *"a classification of diverse aims of discourse must not be interpreted as the establishing of a set of iron-clad categories which do not overlap... Such an exercise must be looked upon as any scientific exercise—an abstraction."* He anticipated the critique. The aims describe dominant intent, not exclusive purpose.

---

## Anker vs Kinneavy vs Diátaxis `[PAPER]`

| Dimension | Anker (~1998) | Kinneavy (1971) | Diátaxis (2017) |
|-----------|--------------|-----------------|-----------------|
| **Organises by** | Writing mode — what type of writing is this? | Communicative aim — what element of the situation is foregrounded? | Reader need — what does the reader need to accomplish? |
| **Framework** | Nine pedagogical modes | Communication triangle — four aims | Two-axis grid — action/cognition × acquisition/application |
| **Level** | Practical/pedagogical | Theoretical | Practical/domain-specific |
| **Reader explicitly central?** | No — modes are text-type categories | Partially — reader is one corner of the triangle | Yes — entirely reader-need driven |
| **Covers essay/argument?** | Yes | Yes (persuasive aim) | No — documentation doesn't argue |
| **Tutorial vs how-to distinction?** | No — both are process analysis | No — both are referential | Yes — learning vs working |
| **Domain** | All writing | All discourse | Software documentation only |

**The verdict:**
- Anker provides categorical coverage but not dimensional logic
- Kinneavy provides the theoretical foundation Diátaxis implements — closest to subsuming it
- Diátaxis adds the learning/working subdivision within referential discourse that neither Anker nor Kinneavy have
- None subsumes Diátaxis completely — each addresses a different dimension

---

## Britton (1970/1975) — The Fifth Independent Convergence `[PAPER]`

**Citations:**
- Britton, J. (1970). *Language and Learning*. Penguin Books.
- Britton, J., Burgess, T., Martin, N., McLeod, A., & Rosen, H. (1975). *The Development of Writing Abilities (11–18)*. Macmillan Education.

**Found via:** Purdy (2024) in *Composing with AI* (Computers and Composition Digital Press) — Purdy uses Britton's taxonomy to critique AI policy statements for over-emphasising transactional writing.

**Starting point:** Developmental/educational psychology. James Britton was studying how children develop writing ability, drawing on Vygotsky's work on language and thought. His question was not "what is rhetoric?" but "what function does writing serve in human development and learning?" A completely different entry point from Newman, Kinneavy, and Diátaxis.

**Britton's three functions of writing:**

| Britton | Function | Description |
|---------|----------|-------------|
| **Transactional** | Communicative | Writing to get things done — inform, instruct, persuade, argue. The primary mode of academic and professional writing. |
| **Expressive** | Personal/developmental | Writing as self-expression, exploratory, close to the writer's inner voice. Facilitates learning and thought development. |
| **Poetic** | Aesthetic | Writing as art — the text itself is the end, not the vehicle. Literary, crafted for its own sake. |

**Mapping to our taxonomy:**

| Britton | Kinneavy | Newman | Ours |
|---------|----------|--------|------|
| Transactional | Referential + Persuasive | Exposition + Argumentation | Article + Essay |
| Expressive | Expressive | Narration | Note (diary/session) |
| Poetic | Literary | — | — (no equivalent in our content types) |

**What Britton adds that others don't:**
- The expressive/transactional distinction is particularly sharp: Britton argues that education over-emphasises transactional writing at the expense of expressive writing — the same critique Purdy makes of AI policies. This is directly relevant: AI tools (and AI-influenced style guides) tend to optimise for transactional content, stripping out the expressive qualities that make writing credible and human.
- His developmental perspective explains WHY expressive writing matters: it's how humans process and consolidate learning. A note or diary isn't just "shorter" than an article — it serves a different cognitive function.
- Britton has no equivalent to Diátaxis's tutorial/how-to distinction — he's working at a more abstract level of function, not reader need.

**The Purdy connection:**
Purdy critiques AI journal policies for constructing writing as "transactional product" while ignoring Britton's expressive function. This is exactly our AI trigger argument from a different angle: when AI generates content, it defaults to transactional — producing text that informs or persuades, stripped of the expressive qualities (personal voice, intellectual honesty, genuine enthusiasm) that make writing credible to human readers. The fluency fallacy is partly a transactional fallacy.

**Why Britton strengthens our paper:**
Five independent convergences is a stronger argument than four. Britton arrived from developmental psychology — the furthest starting point from both classical rhetoric (Newman, Kinneavy) and documentation practice (Diátaxis). The convergence across five completely different disciplines and starting points makes it increasingly implausible that the taxonomy is arbitrary.

---

## Composing with AI — Relevant Chapters `[PAPER]`

**Full reference:** Ranade, N. & Eyman, D. (Eds.). (2024). *Composing with AI*. Computers and Composition Digital Press / Utah State University Press. [ccdigitalpress.org/book/composing-with-ai/](https://ccdigitalpress.org/book/composing-with-ai/)

**Open access** — full text freely available online.

**Purdy chapter (most relevant):**
Purdy, J.P. (2024). "A Textual Transaction: The Construction of Authorship in AI Policy Statements." In Ranade & Eyman (Eds.), *Composing with AI*. [URL](https://ccdigitalpress.org/book/composing-with-ai/chapters/Policy-Purdy/)
- Uses Britton's taxonomy (transactional, expressive, poetic) to critique AI policies
- Argues policies construct writing as "transactional product" — ignoring expressive function and intellectual growth
- Does NOT mention Newman, Kinneavy, Anker, or Diátaxis
- Relevant to our paper as: (a) source of Britton citation; (b) confirms the transactional bias in AI-era writing frameworks

**Other chapters worth noting (not directly relevant to our taxonomy argument):**
- Eisenhart, C. (2024). "LLMs for Style Pedagogy." — LLMs good at horizontal intertextuality (pattern-matching) but not vertical (contextual/rhetorical sensitivity). Uses Kristeva and Williams/Bizup. Not in our lineage but confirms LLMs lack contextual rhetorical awareness.
- Love, P. (2024). "Teaching Knowledge Labor and Literacy for the Age of AI and Beyond with Rhetorical Information Theory." — Uses DIKW pyramid as rhetorical framework. Different angle; confirms the broader interest in connecting information theory and rhetoric.

---

## Does Anker Subsume Diátaxis? `[PAPER]`

This is the critical question. The answer is: **categorically yes, dimensionally no.**

**Categorically yes — Diátaxis fits within Anker:**

| Diátaxis type | Anker mode | Anker purpose group |
|---------------|-----------|-------------------|
| Tutorial | Process analysis | Analyze and explain |
| How-to guide | Process analysis | Analyze and explain |
| Reference | Description | Show and tell |
| Explanation | Illustration / Cause and effect | Analyze and explain |

Anker's framework contains the same categories. A reader of Anker could predict Diátaxis's four types from within the nine modes.

**Dimensionally no — Diátaxis adds what Anker cannot provide:**

Diátaxis's real contribution is not its four categories — it is the **two-axis framework** that explains *why* those categories are distinct:

- **Action vs cognition** — is the content about doing or understanding?
- **Acquisition vs application** — is the reader learning or working?

The decisive test: Anker cannot distinguish a **tutorial** from a **how-to guide**. Both are process analysis in her taxonomy. Diátaxis separates them precisely by reader need — a tutorial serves a learner acquiring capability; a how-to guide serves a practitioner applying it. That discriminating logic is absent from Anker entirely.

Anker tells you *what kind of writing* something is. Diátaxis tells you *what the reader needs to do with it*. Different questions — which is why they're complementary rather than one subsuming the other.

**Why this matters for the paper:**
This is a stronger argument than "Diátaxis is a rediscovery of Anker." It establishes that each framework addresses a genuinely different dimension of the same underlying problem. The unification is not about picking one — it is about showing they address orthogonal aspects of content design.

---

## Five Independent Frameworks, Five Dimensions `[PAPER]`

The central finding — and the minimum contribution of this paper even without a proposed unifying theory:

| Framework | When | Starting point | Dimension addressed | Question answered |
|-----------|------|---------------|--------------------|--------------------|
| Newman (1827) | 1827 | First principles — classical rhetoric | **Intent** | What is the writing trying to do? |
| Bain (1866) | 1866 | Built on Newman | Simplification | (Regression — collapsed persuasive/argumentative) |
| Kinneavy (1969/71) | 1969 | First principles — discourse theory | **Communicative aim** | What element of the communication situation is foregrounded? |
| Britton (1970/75) | 1970 | Educational psychology — child development (Vygotsky) | **Developmental function** | What role does writing play in learning and expression? |
| Anker (~1998) | ~1998 | Pedagogical practice | **Mode** | What type of writing is this? |
| Diátaxis (2017) | 2017 | Practitioner problem — Django docs | **Reader need** | What does the reader need to accomplish? |
| This work (2026) | 2026 | Practitioner problem — colleagues won't read it | **Form + scannability** | What structure serves intent, aim, function, mode, and reader need simultaneously? |

**Five independent convergences:** Newman (classical rhetoric, 1827), Kinneavy (discourse theory, 1969), Britton (educational psychology, 1970), Diátaxis (software documentation practice, 2017), this work (technical practitioner content, 2026). Five starting points — rhetoric, discourse theory, developmental psychology, software documentation, practitioner blogging — arriving at overlapping taxonomies across 200 years with no evidence any was aware of the others at the point of creation.

Each arrived at overlapping but not identical frameworks because they were solving different problems. No one framework subsumes another. Each illuminates a dimension the others don't fully address.

**The "connect the dots" contribution — minimum paper value:**

Nobody has explicitly connected these frameworks. The literature review alone — showing four independent frameworks addressing complementary dimensions of the same underlying question, with a detailed mapping of where they overlap and where they diverge — is a genuine academic contribution. The connections have never been drawn. That is sufficient for publication regardless of whether a full unifying theory is proposed.

**The unifying theory — maximum paper value:**

A complete model: **intent × mode × reader need × form**. Any piece of technical content can be fully specified along all four dimensions. The four content types (note, article, essay, InfoBrief) emerge naturally from this four-dimensional space. Scannability is proposed as a cross-cutting structural requirement that applies across all dimensions.

Whether the paper proposes the full theory or stops at the literature review is a scope decision. Either is publishable. The literature review is the foundation; the theory is the superstructure.

---

## Paper Scope — Minimum vs Fuller Version `[PAPER]`

### The minimum paper — "connect the dots" literature review

**Is the gap real?** Yes — definitively verified. Zero indexed pages connect Newman + Diátaxis. Zero connect Kinneavy + Diátaxis. The analytical work connecting these frameworks across 200 years is genuinely novel. Publishable as-is in a rhetoric or technical communication journal.

**What the minimum paper contains:**
- The intellectual lineage: Newman → Bain (regression) → Kinneavy → Anker → Diátaxis
- The orthogonal dimension analysis: each framework addresses a different question
- The Kinneavy bridge argument: Diátaxis implements what Kinneavy theorised
- The Newman restoration: Bain collapsed persuasive/argumentative; restoring it matters
- The three independent convergences: Newman, Procida, this work
- The four-framework mapping table

**Risk level:** Low. The analysis is defensible without new data. A reviewer can disagree with the interpretation but cannot dispute the gap in the literature.

---

### The fuller paper — what would make it more valuable

**Option 1 — Propose the unified four-dimensional model**

Intent (Newman) × aim (Kinneavy) × reader need (Diátaxis) × form (this work).

*Hard challenge:* A matrix is not a contribution unless it's predictive or generative. The question a reviewer will ask: does this model allow someone to design content better than they could without it? If the answer is "it helps you classify content" — that's taxonomy for taxonomy's sake, not a theoretical advance. The model needs to generate insights or decisions that the individual frameworks don't. Without demonstrating predictive or generative power, this risks being dismissed as an elaborate Venn diagram.

*Verdict:* Include the model, but frame it as a proposal requiring validation — not a proven framework. Be honest about its current status.

**Option 2 — Empirical validation of the AI trigger claim**

The observation that dense prose now reads as AI-generated is the most timely and potentially impactful claim in this work. If validated empirically, it would be genuinely novel and highly citable.

*Hard challenge:* "Colleagues won't read it" is anecdotal, not evidence. A reviewer will ask: where's the data? Eye-tracking studies? Reading time experiments? Engagement metrics comparing prose-heavy vs structured content? Without this, the AI trigger claim cannot appear as a finding — only as a hypothesis or observation. Publishing it as a finding without evidence would be the kind of thing that damages credibility.

*Verdict:* Real opportunity, but requires empirical work — reader studies, content experiments, or at minimum a structured survey. Not doable without data collection. Flag as future work in the minimum paper; elevate to a finding only if data exists.

**Option 3 — The Kinneavy bridge as the centrepiece**

Argue that Diátaxis is a domain-specific implementation of Kinneavy's referential discourse, subdivided by reader need — and that this connection has theoretical implications for documentation practice.

*Hard challenge:* This is an analytical argument, not empirical. A reviewer could say "interesting but not falsifiable." The response: it's a historical and theoretical claim — the same kind made in intellectual history papers. Kinneavy's communication triangle demonstrably provides the theoretical foundation; the connection is traceable even if Procida didn't know it. This is the strongest analytical addition and the most defensible without data.

*Verdict:* Real, defensible, adds genuine value. This should be in the paper.

**Option 4 — Scannability as a cross-cutting structural requirement**

Propose scannability as a principle that applies across all frameworks and content types.

*Hard challenge:* This is asserted, not demonstrated. The evidence base is: one practitioner's experience, one before/after example (devtown#24), and the general observation that AI-generated prose is dense. A reviewer will ask: is there prior work on scannability in technical writing? (Yes — F-pattern reading, Nielsen Norman eye-tracking research.) Does it support this claim? Partially. But connecting scannability to content taxonomy rather than to web UX is a new argument that needs grounding.

*Verdict:* Exists as prior work in UX (Nielsen Norman, F-pattern reading). The connection to content taxonomy is novel but needs to cite that prior work rather than asserting it fresh. Include in the fuller paper with proper grounding; don't assert it without citing Nielsen Norman et al.

---

### Honest summary of fuller paper viability

| Option | Gap real? | Evidence needed | Verdict |
|--------|-----------|----------------|---------|
| Literature review | ✅ Definitively | None — analytical | **Do it** |
| Kinneavy bridge | ✅ Yes | None — analytical | **Do it** |
| Unified model proposal | ✅ Gap exists | Validation needed | Include as proposal, not finding |
| AI trigger empirical | ✅ Highly novel | Reader study required | Future work unless data collected |
| Scannability | ✅ With grounding | Cite Nielsen Norman et al. | Include with proper citation |

**The paper that can be written now, without new data:**
Literature review + Kinneavy bridge + Newman restoration + unified model as proposal + scannability with UX citation grounding. That is a full, credible, publishable paper. The AI trigger empirical work is the follow-on paper if the first lands well.

---

## Article reference to Anker `[ARTICLE]`

One sentence + link only. Example:

> The rhetorical modes tradition has been refined and expanded since Newman — Susan Anker's nine-mode taxonomy (*Real Writing with Readings*) elaborates the expository category in ways that map directly onto Diátaxis's documentation types.

---

## Citations for the Paper `[PAPER]`

| Source | Details |
|--------|---------|
| Newman, S.P. (1827) | *A Practical System of Rhetoric*. Portland: Wm. Hyde. [Internet Archive](https://archive.org/details/practicalsystemo00newmuoft) |
| Bain, A. (1866) | *English Composition and Rhetoric*. Built on Newman, established the simplified four-mode taxonomy |
| Procida, D. (~2017) | Diátaxis. [diataxis.fr](https://diataxis.fr) |
| Hewett, B.L. | *A Scholarly Edition of Samuel P. Newman's A Practical System of Rhetoric*. Brill. [link](https://brill.com/display/title/58440) |
| Hewett, B.L. (1996) | "Samuel P. Newman's A Practical System of Rhetoric: The Evolution of a Method." *Advances in the History of Rhetoric*, Vol. 1. [Taylor & Francis](https://www.tandfonline.com/doi/abs/10.1080/15362426.1996.10500508) |
| Mann, W.C. & Thompson, S.A. (1988) | Rhetorical Structure Theory — document coherence, related but different dimension |
| Hyland, K. | Metadiscourse Model — how writers mark presence and engage readers |
| Anker, S. | Nine rhetorical modes — expansion of Newman's taxonomy |
| Quarkus documentation | [quarkus.io/guides/doc-concept](https://quarkus.io/guides/doc-concept) — Diátaxis applied in the wild |
| Kinneavy, J.L. (1969) | "The Basic Aims of Discourse." *College Composition and Communication*, 20(5), 297–304. DOI: [10.2307/355033](https://doi.org/10.2307/355033) — **Prefer this over the 1971 book for citation.** 8-page journal article covering the full communication triangle (encoder, decoder, reality, signal) and the four aims (expressive, referential, persuasive, literary). Seeded the book. JSTOR access. [Semantic Scholar](https://www.semanticscholar.org/paper/The-Basic-Aims-of-Discourse.-Kinneavy/e3fb46acded22a5a2ebe632425317cede730d7e4) |
| Kinneavy, J.L. (1971) | *A Theory of Discourse: The Aims of Discourse*. Prentice-Hall. [Internet Archive (free, full text)](https://archive.org/details/theoryofdiscours0000kinn) — Full book expanding the 1969 paper. Use the 1969 paper for citation where possible; book for deeper reading. |
| Nielsen Norman Group | F-pattern reading, eye-tracking studies on scannability — prior work grounding the scannability claim. [nngroup.com](https://www.nngroup.com) |
| Anker, S. | *Real Writing with Readings* (multiple editions). Bedford St. Martin's / Macmillan. Nine rhetorical modes — sub-mode elaboration within Newman's exposition category. [Macmillan Learning](https://www.macmillanlearning.com/college/us/product/Real-Essays-with-Readings/p/1319054978) |
| Kaplan-Moss, J. | *Writing Great Documentation: What to Write* — influenced Procida |
| MacArthur, M. (2025) | Large language models and the problem of rhetorical debt. *AI & SOCIETY*, 40, 6425–6438. https://doi.org/10.1007/s00146-025-02403-w — OPEN ACCESS (CC 4.0). PDF in Downloads. The only existing academic paper connecting LLMs with rhetorical theory. Diagnostic (problem); our paper is the constructive complement (solution). Key terms: rhetorical debt, fluency fallacy. Cites Kinneavy in passing. Does NOT mention Newman, Anker, or Diátaxis. Boeing 737 Max + Tesla as rhetorical debt consequences. |
| Britton, J. (1970) | *Language and Learning*. Penguin Books. — Transactional, expressive, poetic taxonomy. Fifth independent convergence from educational psychology / Vygotsky. Found via Purdy (2024). |
| Britton, J. et al. (1975) | *The Development of Writing Abilities (11–18)*. Macmillan Education. — Full empirical study behind the taxonomy. |
| Purdy, J.P. (2024) | "A Textual Transaction: The Construction of Authorship in AI Policy Statements." In Ranade & Eyman (Eds.), *Composing with AI*. Computers and Composition Digital Press. [URL](https://ccdigitalpress.org/book/composing-with-ai/chapters/Policy-Purdy/) — Open access. Uses Britton to critique AI policies for transactional bias. |
| Ranade, N. & Eyman, D. (Eds.) (2024) | *Composing with AI*. Computers and Composition Digital Press / Utah State University Press. [Full book (open access)](https://ccdigitalpress.org/book/composing-with-ai/) — Edited collection on AI and writing. Multiple relevant chapters. |
| Bitzer, L.F. (1968) | The rhetorical situation. *Philos Rhet* 1(1):1–14. [JSTOR](https://www.jstor.org/stable/40236733) — Defines rhetorical situation as purpose, audience, genre, context. Used by MacArthur to redefine prompt engineering. Structurally close to Kinneavy's communication triangle. |
| Juszkiewicz, J. et al. (2019) | *Rhetorical machines: writing, code, and computational ethics.* University of Alabama Press. — Explicitly connects rhetoric to computational/AI contexts. Found via MacArthur references. **Needs separate search — potentially very relevant.** |
| Brock, K. (2019) | *Rhetorical code studies: discovering arguments in and around code.* University of Michigan Press. Found via MacArthur references. |
| Perelman, C. & Oblrechts-Tyteca, L. (1958, 1969) | *The new rhetoric: a treatise on argumentation.* Notre Dame. Foundational argumentation theory cited by MacArthur. |
| Aggarwal et al. (2024) | GEO (Generative Engine Optimization) paper — adding citations and statistics improves LLM citation rates. Cited in industry guidance. Useful contrast: this is about being cited BY LLMs, not about improving LLM output quality. |
| Aristotle | *Rhetoric* — Three appeals: logos (logic), ethos (credibility), pathos (emotion). Priority order for technical argumentative writing: logos first, ethos second, pathos third. Persuasive vs argumentative distinction traces back here. |
| Burke, K. (1950) | *A Rhetoric of Motives* — cited by MacArthur in rhetorical theory context |
| Corbett, E.P.J. (1965) | Classical Rhetoric for the Modern Student — cited by MacArthur |

---

## The Three Appeals — Priority Order `[BOTH]`

Aristotle identified three modes of persuasion: logos (logic), ethos (credibility), pathos (emotion). The rhetorical tradition has always known these. The priority order matters — and is rarely stated explicitly.

For technical argumentative writing, in strict priority order:

**1. Logos — argument and evidence (mandatory)**
The essay stands or falls here. Logical, evidence-led, precise. If the argument doesn't hold, nothing else saves it. This is non-negotiable. Passion, credibility, and style all become irrelevant if the argument is weak.

**2. Ethos — credibility through expertise AND character**
Credibility isn't just expertise — it's character. The personal voice is part of ethos, not pathos. A reader who trusts the person making the argument engages with it differently than a reader who encounters it from an unknown source. 577 blog posts built that trust over time: peer-to-peer, honest about uncertainty, self-deprecating when warranted, willing to name disagreements directly. Readers who connected with the author across 577 posts were more likely to engage seriously with positions they initially disagreed with. The argument is stronger because you trust the person making it. Personal voice — the practitioner voice, not the AI-polished voice — is the vehicle for ethos.

**3. Pathos — passion, not emotion**
Genuine enthusiasm for the subject. Not performance, not amplification, not dramatics. The corpus analysis across 577 posts captured it: "passionate about the work... genuine enthusiasm for the technology." This isn't marketing copy — it reads like someone who actually cares. Passion makes evidence feel important rather than merely true. It is the human layer that makes technical content worth reading rather than merely correct. But the moment passion overrides logos — when claims are inflated beyond what evidence supports — it becomes hubris. Cut it.

**Argumentative, not persuasive (Common Core distinction):**
- **Persuasive:** appeals to emotion to bypass critical thinking — emotional manipulation
- **Argumentative:** appeals to evidence and expertise, with passion as the human layer

We always want argumentative. Passion is welcome within it. Persuasive bypasses the argument and is not.

**The hubris test:** Does the passion strengthen the argument, or substitute for it? If the former — it belongs. If the latter — cut it.

**Not bombastic or dramatic — doubly important now:**
- Authenticity: bombastic writing is performance, not voice — it signals the writer cares more about effect than truth
- Format signal: dramatic prose now reads as AI-generated regardless of content quality — "everything hung by a thread", "the moment everything changed" triggers dismissal before the argument is reached

Restraint in emotional register is both honest and strategic. Passion comes through in precision and genuine engagement with the evidence — not in heightened language.

---

## Quotes Worth Preserving `[ARTICLE]`

- "Scanning IS the experience" — on InfoBrief
- "Structure navigates; prose argues" — on structured essay
- "I want to inform you of X / I want you to understand X / I want you to believe X" — the intent test
- "The style guide wasn't wrong — AI broke the assumption it depended on"
- "Dense prose used to signal expertise. It now signals machine output."
- "The format has been contaminated by association"
- "The domain silo did the work that ignorance didn't need to"

---

## Avoiding AI Slop — The Anti-Trigger Framework `[BOTH]`

*Source: Grok feedback. Critical for both the write-blog skill (actionable) and the article series (explains the problem and its solution). Connects directly to Act 1 (the AI trigger problem) and the augmenting-heuristic-evolution argument.*

---

### Why this matters

Reader backlash against AI content is real and growing. People have developed a strong "AI detector" instinct — they bounce off anything that feels generic, overly polished, repetitive, or soulless. The goal is writing that feels human, sharp, and worth reading. Our taxonomy helps because it forces intentionality — but the taxonomy alone isn't enough. The HOW matters as much as the WHAT.

This connects directly to the compounding problem in Act 1: a prose-led personal style, applied by AI without the brevity instinct, amplifies exactly the worst AI characteristics. The anti-slop techniques below are the constructive answer to that diagnosis.

---

### Core principles (universal — apply to all content types)

**1. Voice and imperfection**
Real humans hedge, use contractions, write occasional short sentences, include personal asides. Force personality and mild imperfection. Ban corporate/marketing voice entirely.

Banned words: *delve, tapestry, realm, crucible, nuanced, intricate, game-changer, groundbreaking, transformative, leverage, synergy, seamlessly, holistic, robust, paradigm* — and any word that reads like it was chosen to sound impressive rather than to communicate.

**2. Specificity over generality**
AI loves vague abstractions. Demand concrete examples, anecdotes, hard numbers, specific observations. "400% performance gain" beats "significant improvement." "129-word median post" beats "short posts." The corpus analysis on 577 posts is exactly this.

**3. Structural variety**
Break predictable patterns. No constant "Furthermore…", "In conclusion…", or repetitive 3–5 bullet lists. Vary sentence length. Mix short, punchy sentences with longer technical ones.

**4. Thinking traces**
Show the messiness of real thought instead of perfect logical flow. Uncertainty, corrections, "what I wish I knew earlier" — these signal a real human working through something. MacArthur calls this "functional linguistic competence" — understanding the real context, not just producing fluent tokens.

---

### Taxonomy-specific anti-slop techniques `[SKILL]`

Each content type has natural human textures. Use them:

**Note / log**
Should feel raw. Write like a private journal or thinking-aloud session. Allow fragments, tangents, uncertainty. A polished, structured log is a contradiction — it has already become an article.

**Note / musing**
Maximum rawness. This is the writer thinking, not communicating. Incomplete sentences, tangents, unresolved questions are features, not flaws.

**Note / idea**
A proposal, not a pitch. Rough edges are fine. The idea is what matters; the packaging is secondary.

**Article / tutorial**
Include real friction points. "I got stuck here because..." moments. "What I wish I knew before starting." The friction is what makes it believable and useful. A tutorial with no stumbling blocks reads as AI-generated.

**Article / how-to**
Step-by-step but not robotic. Include the "why this step, not that" where it's non-obvious. Acknowledge what can go wrong. Real how-tos have warnings and edge cases.

**Article / explanation**
Use analogies from unexpected domains. Show the evolution of your own understanding — "I used to think X, but it turns out Y." The journey to understanding is more valuable than the understanding stated flatly.

**Article / commentary**
Lean heavily into personal opinion and subjective experience. This is where the practitioner voice is most important. "Here's what I actually think, having worked with this for ten years" is the whole point.

**Article / essay**
Strong personal voice + clear stance. Engage counter-arguments naturally, not formulaically. Mandate one surprising or contrarian point. The "fair counter" and "type hint caveat, stated fairly" patterns from "When the Machine Codes" are exactly right.

**InfoBrief**
Ruthless editing — make it denser and more telegraphic than a human would naturally write. This ironically makes it feel more human. Experts write densely. The InfoBrief should feel like it was written by someone who knows exactly what matters and respects the reader's time.

**News**
Fast, direct, with clear sourcing. Opinion clearly separated from fact. No padding. No "this is an exciting development" — just what happened and why it matters.

---

### The master anti-slop instruction `[SKILL]`

Add this to every write-blog prompt:

```
Write in a natural, human style. Avoid all AI-sounding patterns:
- No words like: delve, tapestry, realm, crucible, nuanced, intricate, 
  game-changer, groundbreaking, transformative, leverage, synergy, seamlessly,
  holistic, robust, paradigm
- Vary sentence length. Mix short, punchy sentences with longer ones.
- Include occasional contractions and personal asides.
- Show actual thinking process, including uncertainties and minor imperfections.
- Use specific, concrete details and numbers instead of vague abstractions.
- Sound like a sharp, opinionated human who has real experience with this topic.
```

Layer these for higher quality:
- "Write as [specific persona] with [specific background] who has been thinking about this for years."
- "Include one unexpected observation or contrarian take that most people miss."
- "After writing, revise to remove any corporate or generic fluff. Make it 15% more direct and human."

---

### Workflow recommendations `[SKILL]`

**1. Generate raw → edit ruthlessly**
Use LLM for first draft, then heavy human editing pass. The first draft is raw material, not the product.

**2. Staged generation (maps to our Note → Article conversion path)**
- Stage 1: Muse/log in raw voice — thinking out loud, no editing
- Stage 2: Expand into full Article/Essay — structure applied
- Stage 3: Human revision pass — voice, specificity, anti-slop check

**3. Style anchors**
Give the LLM 2–3 examples of the best existing writing as reference before generating. The 577 corpus analysis is the grounding for Mark's voice — the style guide already operationalises this.

**4. Detection test (optional)**
After generation, ask a separate LLM: "Does this read like typical AI slop? Be brutally honest." Then fix flagged issues. This is the self-review step.

---

### The final truth

The best defence against "this looks AI-generated" is writing that is actually good and human. Even perfect anti-AI prompting won't save mediocre ideas. The taxonomy helps because it forces intentionality — especially the commentary vs essay distinction. A writer who knows they're writing an essay knows they need a thesis, counter-arguments, and a conclusion. That intentionality produces better prompts, which produce better output, which needs less editing to feel human.

**The connection to our paper argument:** This is the constructive side of MacArthur's rhetorical debt diagnosis. MacArthur says LLMs lack rhetorical awareness and produce fluency without substance. The anti-slop techniques are what rhetorical awareness looks like in practice — knowing what type of content you're producing, for whom, with what intent, and what human texture that type should have.

---

### What goes into the skill files from this section `[SKILL]`

- The master anti-slop instruction → goes into `write-blog/defaults/mandatory-rules.md` or a new `anti-slop.md` in defaults
- Taxonomy-specific textures → one paragraph per subtype in each `write-blog/forms/` file
- Staged generation workflow → goes into `write-blog/SKILL.md` main workflow
- Banned words list → goes into `write-blog/defaults/common-voice.md` (already has "What to Avoid" — extend it)
- Style anchors instruction → goes into the per-author style guide loading step

---

## What Makes a Best-in-Class LLM Writing Framework `[ARTICLE]`

*Source: Grok feedback on the taxonomy. The gap table and criteria below are article-ready — include in the standalone practical article or as a standalone piece on framework quality.*

---

### Grok's assessment of where the taxonomy sits

> "Most content systems are vague ('long-form', 'short post', 'note') or overly complex. Yours is focused, intent-driven, and academically grounded. The final 5% is what separates 'very good and usable' from 'this is genuinely best-in-class / could become a reference standard.'"

Current position: **93–95th percentile**.

---

### The gap table — what the top 5% looks like

| Aspect | Current level | Top 5% level | Gap |
|--------|--------------|-------------|-----|
| **Precision** | Good definitions | Crystal-clear boundaries + canonical examples + non-examples | Medium |
| **Usability** | Implicit decision making | Decision tree + one-page cheat sheet + LLM classifier | Small–Medium |
| **Quality control** | None yet | Per-type rubrics with scoring | Large |
| **Handling reality** | Clean categories | Graceful degradation for hybrids and edge cases | Medium |
| **Adoption and scale** | Personal workflow | Templates, automation, versioning, evolution rules | Medium–Large |
| **Validation** | Academic mapping | Tested on 100+ real pieces + iteration data | Large |
| **Extensibility** | Fixed | Mechanism to add new subtypes safely | Medium |

---

### What "top 5%" requires — prioritised

**Immediate high-impact (do these first):**
- One perfect canonical example + one anti-example per subtype
- Short quality criteria (5–7 items) for every Article subtype — for Essay: thesis clarity, counter-argument engagement, evidence quality, conclusion strength
- A classification decision tree — yes/no questions an LLM or human can follow in under 60 seconds
- Strict LLM prompt templates per subtype (the write-blog/forms/ directory is this)

**Next-level moves:**
- Metadata layer: audience level (beginner/intermediate/advanced/expert), evergreen vs temporal, update cadence
- Explicit conversion rules: when a musing becomes an idea, when an idea becomes an essay, when an essay should also have an InfoBrief version
- Hybrid handling policy: primary type + secondary tags (e.g. Article/Essay + InfoBrief)

**Elite tier (top 1–2%):**
- A small LLM classifier that reads a draft and outputs: type + confidence + missing elements + quality scores
- A retrospective: tag the last 30–50 published pieces; note where the taxonomy feels painful
- Publish the full framework openly with templates and quality criteria; get feedback
- Add versioning to the taxonomy itself (v1.0, v1.1...)

---

### Path to each percentile

| Target | What it takes |
|--------|--------------|
| **Top 5%** | Quality criteria + decision tree + canonical examples + LLM templates |
| **Top 2–3%** | All of the above + rubrics with scoring |
| **Top 1%** | All of the above + retrospective tagging + public publication with adoption data |

---

### What this means for the article

This section works as either:
1. A closing section of the standalone practical article (Proposal B) — "where this taxonomy sits and what comes next"
2. A standalone follow-on piece about framework quality in LLM-assisted writing

The gap table is the centrepiece — it's concrete, scannable, and gives practitioners a clear picture of what "good enough" vs "best in class" actually means. The criteria for each level make it actionable rather than just aspirational.

**Things to do before writing this section:**
- Tag 10–20 existing posts using the taxonomy — note friction points (this is the start of the retrospective)
- Write one canonical example + one anti-example per subtype — these become the concrete anchors

---

## Standalone Practical Article — Proposal B `[ARTICLE]`

**What it is:** A short standalone article in Mark's natural mature voice (Phase 3 — concise, direct, peer-to-peer, prose-led, ends when the point is made). 400–600 words. Not an InfoBrief — prose carries the argument, structure aids scanning. The kind of thing that would have appeared in the original 577 posts and takes three minutes to read.

**Audience:** Practitioner who wants the framework, not the history. Developer, content strategist, technical writer working with AI. Doesn't need to know who Newman is — just wants to write better content.

**What it covers:**
- The practical problem in one short paragraph — colleagues won't read it, AI has changed the reading contract
- The four content types with the intent test — brief, usable, memorable
- Scannability as the universal principle — one paragraph
- The hybrid heading pattern for longer work — a few sentences with one example
- One paragraph acknowledging the academic grounding: "This turns out to map onto 200 years of rhetorical theory — Newman (1827), Kinneavy (1971), and Diátaxis. If you want the intellectual history, [links to Parts 3 and 4 of the series]."
- Ends on the practical takeaway — not a summary, just the last real point

**What it doesn't cover:**
- Newman, Kinneavy, Anker, Diátaxis in any depth
- The four-framework table
- The literature gap
- The academic argument about unified frameworks
- MacArthur (mentioned at most in passing)

**Form:** Short article — prose-led, selective bullets/tables only where they genuinely earn their place. Not InfoBrief structure. Not structured essay with numbered sections. Just a well-made short piece in Mark's voice.

**Relationship to the series:** Can be published before the series as a standalone practical entry point, or alongside it as the "practical companion." Each part of the series can link back to it as "the short version." It doesn't require the series to exist.

**Tone reference:** The mature Phase 3 posts — strategic, concise, technically precise, trusts the reader. Peer to peer. Ends abruptly when the point is made, or with a short forward-looking note. No "in conclusion."

---

## Series Structure — Proposal A `[ARTICLE]`

Six linked articles, each standalone, chronologically tracking the discovery.

**Part 1 — The AI Reading Problem**
The practical trigger. Two compounding problems: environmental (dense prose now reads as AI) and personal (a prose-led style, applied by AI without the brevity instinct, amplifies the worst). MacArthur's fluency fallacy — in reverse. Why this isn't about shorter attention spans. The devtown#24 before/after as the concrete evidence.

**Part 2 — Finding the Forms**
What emerged from practice. InfoBrief discovered first — scanning IS the experience. Then note, article, essay named by intent, not format. Scannability as the cross-cutting principle. The forms weren't designed — they were found in existing content and named after the fact.

**Part 3 — Hiding in Plain Sight**
The pivot to theory. Diátaxis in Quarkus — right there, used daily, never noticed because it was filed as "documentation." Newman 1827. The moment of convergence: we had independently arrived at a 200-year-old taxonomy. Three independent arrivals. The domain silo as the blindspot.

**Part 4 — The Intellectual Lineage**
Newman → Bain (regression) → Kinneavy (the missing link) → Anker → Diátaxis. Each framework addressing a different dimension. Why they're complementary, not competing. The four-framework comparison table. Kinneavy as the theoretical bridge Procida implemented without knowing.

**Part 5 — The Gap Nobody Noticed**
Zero connections in the literature. MacArthur (2025) diagnosed rhetorical debt in LLMs — fluency without rhetorical awareness. Industry guidance on LLM content is atheoretical heuristics — undisciplined rediscoveries of what these frameworks already know. The gap is real and consequential.

**Part 6 — Toward a Unified Framework**
The constructive proposal. The four dimensions: intent × communicative aim × mode × reader need × form. What principled guidance looks like vs undifferentiated rules. The four content types as natural emergence. Future work — empirical validation, the AI trigger study.

---

## Article Structure `[ARTICLE]`

Form: structured essay — it has a position.
Position: *the AI era requires a rethinking of content form, and the best framework for that rethinking is grounded in classical rhetoric — work that was already there, hiding in plain sight.*

1. **The complaint** — colleagues won't read it. Good content, carefully written, being ignored.
2. **Two problems compounding** — the AI trigger (environmental) + personal style amplifies it (specific). The style guide wasn't wrong; AI broke the assumption it depended on.
3. **The fluency fallacy in reverse** — MacArthur (2025) identified that readers trust AI output because it's fluent. The mirror image: readers now distrust human output because it resembles AI fluency. Same cause; two consequences.
4. **What emerged from practice** — the forms named from use: InfoBrief, note, article, essay, structured essay. Scannability as the cross-cutting requirement.
5. **The pivot to theory** — first instinct: search for existing frameworks. Diátaxis hiding in plain sight in Quarkus documentation. The domain silo did the work that ignorance didn't need to.
6. **Newman 1827** — the moment of convergence. Independent arrival at a 200-year-old taxonomy.
7. **Why they're complementary** — the table: Newman (intent) vs Diátaxis (reader need). Not competing; orthogonal.
8. **Four independent arrivals** — Newman, Kinneavy, Procida, this work. The structural argument: every time someone has thought carefully about why people write, they arrive at the same distinctions.
9. **What follows** — scannability as baseline, intent as organising principle, the forms in practice.

**Tone:** Discovery narrative — honest about the messy, iterative process. The conclusion (200-year-old taxonomy, MacArthur 2025) is more interesting because of where it started (colleagues ignoring content).

**Open questions:**
- Show devtown#24 before/after? Best concrete illustration of the AI trigger problem.
- A/B a section of "When the Machine Codes" in the article itself? Meta, but powerful — demonstrates the principles in practice.
- How much of the 1827 discovery moment to lean into? It's the emotional peak.
- Include the MacArthur "fluency fallacy" connection? Adds authority and connects to current academic conversation — yes, but briefly.
- Include Kinneavy in the article or save for the paper? Kinneavy is complex; one sentence + link probably sufficient for the article audience.

**What NOT to include in the article** (paper-only):
- Full Anker vs Kinneavy vs Diátaxis table
- The four-dimensional unified model
- The detailed LLM guidance heuristics mapping
- The full paper structure argument

---

## Research Status — What Has and Hasn't Been Done `[PAPER]`

This section tracks the research state so future sessions can resume without repeating searches. Last updated: 2026-05-13.

### Completed searches and what they found

**Web searches — confirmed gaps:**
- "rhetorical modes" + "Diátaxis" together: **zero results** anywhere on the public web
- "Kinneavy" + "Diátaxis": **zero results**
- "Newman" + "Diátaxis": **zero results**
- LLM content generation + rhetorical theory academic papers: **one result** (MacArthur 2025 only)
- Newman + Kinneavy + Diataxis unified framework: **zero results**

These searches confirm the gap at the web level. Academic databases have not been fully searched — see Outstanding Searches below.

**Kinneavy (1969) citation network — partial search completed:**
Web searches found no papers connecting Kinneavy to Diátaxis, documentation frameworks, LLMs, or AI content generation. The 2020 *TechComm* paper ("Inform or Persuade?") applies his inform/persuade distinction to technical communication textbooks — confirms he is alive in TechComm scholarship but in a pedagogy silo, not connected to documentation frameworks. The Semantic Scholar citation page for the 1969 paper failed to load — **the full citation network has not been checked**. Outstanding action: visit [semanticscholar.org/paper/The-Basic-Aims-of-Discourse.-Kinneavy/e3fb46acded22a5a2ebe632425317cede730d7e4](https://www.semanticscholar.org/paper/The-Basic-Aims-of-Discourse.-Kinneavy/e3fb46acded22a5a2ebe632425317cede730d7e4) directly and review all citing papers.

**"Inform or Persuade? An Analysis of Technical Communication Textbooks" (2020, TechComm/STC):**
Directly cites Kinneavy in technical communication context. Applies his inform/persuade distinction to textbook analysis. Does NOT connect to Diátaxis. Useful citation for us — confirms Kinneavy is used in TechComm scholarship, validates our bridge. Paywalled: [stc.org/techcomm/2020/04/28/inform-or-persuade-an-analysis-of-technical-communication-textbooks/](https://www.stc.org/techcomm/2020/04/28/inform-or-persuade-an-analysis-of-technical-communication-textbooks/)

**Composing with AI (Ranade & Eyman, 2024) — read in full:**
Open access edited collection. [ccdigitalpress.org/book/composing-with-ai/](https://ccdigitalpress.org/book/composing-with-ai/)
Key find: Purdy chapter uses Britton's taxonomy (transactional, expressive, poetic) — identified as fifth independent convergence. Eisenhart and Love chapters also read; less directly relevant. None of the 13 chapters mention Newman, Kinneavy, Anker, or Diátaxis together. Confirms these connections have not been made in this adjacent literature either.

**Notable paper found during Kinneavy search:**

"Applications of Kinneavy's Theory of Discourse to Technical Writing" — *College English*, Vol. 40, No. 6, February 1979. A paper applying Kinneavy to technical writing was published 1979 — 38 years before Diátaxis. Cannot access full text (scanned PDF). Author unknown from available metadata. This predates Diátaxis entirely and therefore cannot connect the two — but confirms Kinneavy was being applied to technical writing decades before Diátaxis existed. Worth locating full text.
- CORE.ac.uk PDF (scanned, unreadable): [core.ac.uk/download/pdf/211341277.pdf](https://core.ac.uk/download/pdf/211341277.pdf)
- Access recommendation: search JSTOR or Google Scholar for *College English* Vol. 40 No. 6 (Feb 1979) Kinneavy technical writing

**"Inform or Persuade?" — STC Technical Communication journal (2020)**
Directly applies Kinneavy's inform/persuade distinction to technical communication textbooks. Paywalled.
- URL: [stc.org/techcomm/2020/04/28/inform-or-persuade-an-analysis-of-technical-communication-textbooks/](https://www.stc.org/techcomm/2020/04/28/inform-or-persuade-an-analysis-of-technical-communication-textbooks/)
- Worth obtaining — may reveal how Kinneavy is being applied in current TechComm scholarship

**Kinneavy on Semantic Scholar:**
- Entry with citation count and citing papers: [semanticscholar.org/paper/A-Theory-of-Discourse...](https://www.semanticscholar.org/paper/A-Theory-of-Discourse:-The-Aims-of-Discourse-Kinneavy/babed9037f40595affdb6d10d3c63afcfb66d0f6)
- **Action needed:** visit this page and check the citing papers list — any papers connecting Kinneavy to documentation, content taxonomy, or Diátaxis would appear here

**Kinneavy critique — Fulkerson (1984):**
Demonstrated that "aim in the broad sense does not determine structure" — an essay can use a classificatory mode in the service of expressive aims. This is the "aims aren't cleanly separable" challenge. Already flagged in our paper as something to address. Fulkerson, R. (1984). Knowing what "good writing" is: Some considerations. Useful citation for the limitations section.

**Technical writing as reference AND persuasive discourse:**
Documented in the literature — Kinneavy himself characterised technical writing as combining reference and persuasive aims, not purely referential. This is important nuance: our InfoBrief maps to Kinneavy's referential aim, but technical articles and essays combine aims. Supports our point that the aims describe dominant intent, not exclusive purpose.

**IEEE Transactions on Professional Communication Sept 2024 (Vol. 67, No. 3):**
Contains rhetorical analysis of genre structure in professional documentation. Not directly relevant to our paper but confirms the journal publishes rhetoric + documentation work.
- [wpa-announcements.tracigardner.com — Vol 67 No 3](https://wpa-announcements.tracigardner.com/2024/09/19/new-ieee-transactions-on-professional-communication-sept-2024-vol-67-no-3/)

---

### Outstanding searches — must complete before paper submission

**Priority 1 — Critical (affects "nobody has connected these" claim):**

1. **JSTOR full-text search** — search for: "Kinneavy" + "Diátaxis"; "rhetorical modes" + "documentation framework"; "Newman" + "documentation taxonomy"
   - Access: [jstor.org](https://www.jstor.org) — requires institutional access
   - Journals to search specifically: *Technical Communication*, *Technical Communication Quarterly*, *Journal of Technical Writing and Communication*, *Rhetoric Review*, *Advances in the History of Rhetoric*

2. **MLA International Bibliography** — comprehensive humanities/rhetoric database
   - Access: library database (institutional)
   - Search: "Kinneavy" + "documentation"; "aims of discourse" + "content types"; Newman + rhetorical modes + technical communication

3. **Google Scholar targeted search** — search directly at scholar.google.com for:
   - `Kinneavy "documentation" "content types" framework`
   - `"rhetorical modes" "documentation" unified framework`
   - `"aims of discourse" Diataxis`
   - Check Kinneavy's Semantic Scholar page for citing papers — any connecting to documentation/content taxonomy

4. ~~**Semantic Scholar citation network for Kinneavy 1969 paper**~~ ✅ **DONE** — Retrieved all 64 citations via Semantic Scholar API. Full list reviewed. Result: **zero citations connect Kinneavy to documentation frameworks, Diátaxis, content taxonomy, or AI content generation.** Citations are in composition pedagogy, ESL/EFL writing, political discourse, contrastive rhetoric, and medical writing. Only tangentially relevant: "The Implied Author in Technical Discourse" (1984) — inaccessible online, not pursuable. The gap is confirmed from the citation network. 64 citations across 55 years; none make the connection our paper makes.

**Priority 2 — Important for paper depth:**

5. **"Applications of Kinneavy's Theory of Discourse to Technical Writing"** (1979, *College English* Vol. 40 No. 6)
   - Get full text via JSTOR or Google Scholar
   - Confirm author, full argument, whether it makes connections relevant to our paper

6. **"Inform or Persuade?" STC Technical Communication (2020)**
   - Get full text via STC membership or institutional access
   - Confirm how Kinneavy's aims are being applied in current TechComm scholarship

7. **Procida's own writings** — read his blog posts and talks at diataxis.fr
   - Confirm "worked from first principles without knowing Kinneavy" claim
   - URL: [diataxis.fr/theory/](https://diataxis.fr/theory/) — the theoretical background page

8. ~~**Read MacArthur (2025) in full**~~ ✅ **DONE** — PDF read in full. Full notes above. Open access. Kinneavy cited in passing; Newman, Anker, Diátaxis not mentioned. Bitzer (1968) and Juszkiewicz et al. (2019) identified as new relevant citations.

8b. **Search Juszkiewicz et al. (2019) — *Rhetorical machines: writing, code, and computational ethics*** — found via MacArthur references. Explicitly connects rhetoric to computational/AI contexts. High relevance potential.
   - Search: Google Scholar, Amazon, University of Alabama Press catalogue

9. ~~**Read Kinneavy (1969) paper**~~ ✅ **DONE** — PDF read in full. Critical findings: (1) Kinneavy himself documented the convergence in Figure 1 and called it "almost fearful symmetry"; (2) referential aim has three sub-types (exploratory/scientific/informative) mapping precisely to Diátaxis's tutorial/explanation/reference; (3) expressive aim includes diaries — maps to our Note form; (4) principle of classification was itself independently discovered (Bühler 1930s, Jakobson 1960s). Changes our paper significantly — we are extending a pattern Kinneavy already named.

**Priority 3 — Worth exploring when time allows (parked):**

10. **Genre theory** — Swales (*Genre Analysis*, 1990), Bhatia — potentially another framework in the lineage. Search: "genre theory" + "content taxonomy" + technical communication
11. **Minimalism (John Carroll)** — potentially relevant to tutorial/how-to distinction. Carroll's minimalism predates Diátaxis and may complicate or strengthen our argument
12. **Plain language movement** — has its own theoretical tradition intersecting with our heuristics argument
13. **Spinuzzi's reading notes on Kinneavy** — [spinuzzi.blogspot.com/2015/12/reading-theory-of-discourse.html](http://spinuzzi.blogspot.com/2015/12/reading-theory-of-discourse.html) — Clay Spinuzzi is a technical communication scholar; his notes may reveal relevant connections
14. **Nielsen Norman specific studies** — identify specific papers/reports supporting scannability claim for proper citation in paper

---

## Honest Assessment — Is This Worth a Paper? `[PAPER]`

*Written after completing the core literature research. Purpose: to stress-test the contribution before investing in drafting.*

---

### What we actually found

**The core intellectual find:**
Kinneavy (1969) himself documented the convergence pattern across 8 scholars and named it "almost fearful symmetry." His referential sub-types (exploratory, scientific, informative) map precisely to Diátaxis's tutorial, explanation, and reference. This connection has never been made in 64 citations across 55 years. We are extending a pattern he already named into two new domains (software documentation practice, practitioner technical content) and five additional independent convergences (Britton 1970, Procida 2017, this work 2026).

**The gap confirmation:**
- Zero web results connecting any of these frameworks
- 64 Kinneavy citations — none in documentation, Diátaxis, or AI
- MacArthur (2025) cites Kinneavy in passing — does not make the connection
- *Composing with AI* (2024), 13 chapters — none make the connection
- The gap is verified from multiple independent search angles

---

### Is it interesting?

**Yes — to a specific audience.** The intellectual find is genuine:
- A 2017 practitioner framework (Diátaxis) independently implements what a 1969 academic paper theorised — without the practitioner knowing it
- Kinneavy himself documented "fearful symmetry" in 1969; we extend it 57 years further
- Five independent starting points (classical rhetoric, discourse theory, educational psychology, software documentation, practitioner content) converging on the same taxonomy — from Aristotle to Procida

**The "fearful symmetry" quote is the centrepiece.** Kinneavy named the phenomenon; our paper extends and applies it. That's a clean intellectual through-line.

---

### Will people care?

Honest split-audience assessment:

| Audience | Interest level | Why | Gap |
|----------|---------------|-----|-----|
| Rhetoric & composition scholars | **High** | They know Kinneavy intimately; the extension to Diátaxis is novel | May not know/care about Diátaxis or documentation practice |
| Technical communication researchers | **High** | They know Diátaxis; showing it has deep roots in 1969 rhetorical theory is validating | May not know Kinneavy |
| AI/LLM researchers | **Low without evidence** | Neither framework is in their world; the practical claim is undemonstrated | Would need empirical results to care |
| Documentation practitioners | **Mild** | Validates their practice; deepens understanding | Doesn't change what they do |

**The strongest natural audience:** readers of *Technical Communication*, *Technical Communication Quarterly*, *Rhetoric Review*, *Advances in the History of Rhetoric*. These readers sit at the intersection of rhetoric and documentation practice — exactly where the connection lives.

**The weakest claim:** that grounding LLM content guidance in rhetorical theory would improve outcomes. This is logically sound but undemonstrated. The AI/LLM audience will not be convinced without evidence.

---

### Is it relevant to a paper?

**Yes — with an honest scope.**

**The minimum paper is solid and publishable:**
- Connecting the frameworks (Newman → Kinneavy → Britton → Anker → Diátaxis)
- Extending Kinneavy's "fearful symmetry" observation by 57 years
- The Kinneavy bridge: showing Diátaxis implements Kinneavy's referential sub-types
- The 64-citation gap as evidence
- Newman restoration: Bain collapsed persuasive/argumentative; worth restoring
- Target journals: *Technical Communication*, *Technical Communication Quarterly*, *Advances in the History of Rhetoric*

This is a contribution. It is novel. It fills a documented gap. It can be written without new empirical data.

**The LLM angle is the hook, not the substance — yet:**
The practical claim (rhetorical theory can augment LLM content guidance) is interesting and timely but needs one of:
- A worked example demonstrating the framework producing guidance heuristics can't (the tutorial/how-to discrimination is the best candidate)
- Empirical evidence (reader studies, engagement data) — currently unavailable
- A much more developed theoretical argument

Without one of these, the LLM angle is a good introduction and a good "future work" section — not the centrepiece of the paper.

**The MacArthur positioning is strong:**
MacArthur (2025) in *AI & Society* diagnoses rhetorical debt; our paper proposes the constructive complement. Same journal, same theoretical tradition, different scale (systemic vs practical). That's a strong positioning even if the LLM application is underdeveloped.

---

### Where the paper is weaker

**1. The practical "so what?" is underdeveloped.**
Knowing Kinneavy theorised Diátaxis before Diátaxis existed is intellectually satisfying. But what does a documentation writer, prompt engineer, or content strategist do differently on Monday morning because of this paper? The tutorial/how-to discrimination is the best practical answer — but one example doesn't sustain a full paper's practical claim.

**2. The unified model risks being taxonomy for taxonomy's sake.**
Intent × communicative aim × mode × reader need × form — if this matrix doesn't generate decisions or predictions that the individual frameworks don't provide, it's an elaborate Venn diagram. Needs demonstrated predictive/generative value.

**3. The scannability claim needs grounding.**
Asserted, not demonstrated. Nielsen Norman provides some grounding but the connection to content taxonomy is new and thin.

**4. The AI trigger observation is anecdotal.**
"Dense prose now reads as AI-generated" — compelling, timely, but not evidenced. One before/after (devtown#24) and one practitioner's experience. Can appear as an observation, not a finding.

---

### Recommended scope for the paper

**Write now, without new data:**
Literature review + Kinneavy bridge + Newman restoration + "fearful symmetry" extension + scannability with Nielsen Norman grounding + unified model as proposal. That is a full, credible, publishable paper.

**The article series first:**
Publish the six-part series and the standalone practical article first. These:
- Test whether the argument lands with the target audience
- Build the intellectual reputation that makes the paper more citable
- May generate the reader response that provides qualitative evidence for the AI trigger claim
- Allow the practical application to be developed through audience feedback

**The empirical paper second:**
If the articles generate interest, the follow-on empirical paper — testing whether rhetorical grounding improves LLM content guidance — becomes easier to pitch and fund.

---

### The honest one-paragraph verdict

The Kinneavy → Diátaxis connection is a genuine intellectual find, the gap is real and well-evidenced, and extending Kinneavy's own "fearful symmetry" observation by 57 years is a clean contribution. The minimum paper is publishable in a technical communication or rhetoric journal. The LLM hook makes it timely. The weaknesses are: the practical application is asserted not demonstrated, and the unified model needs to show generative value not just classification. The right sequence is article series → paper → empirical follow-on. The paper should be scoped to what can be demonstrated analytically, with the LLM application as motivation and future work rather than as the central claim.

---

## AI Disclosure `[PAPER]`

This work was developed iteratively with Claude (Anthropic) as a research and drafting assistant. The intellectual framework, arguments, and conclusions are the author's; Claude assisted with literature search, literature gap identification, drafting, and refinement throughout.

**On the tool/co-author distinction:** The collaborative relationship is substantively that of co-authorship — the author drove every key insight and direction; Claude contributed research, drafting, and challenge. The distinction is procedural rather than ethical: journal policy requires a human author who can correspond, respond to reviewers, and take accountability for the work. That accountability rests with the author. The AI contribution is disclosed fully here rather than attributed in the author list.

---

## Paper Structure `[PAPER]`

1. **Introduction — the practitioner problem and the diagnostic gap**
   - The practical problem: LLM content generation guidance is atheoretical heuristics
   - MacArthur (2025) diagnoses rhetorical debt in LLM output; we propose the constructive response
   - The first-principles approach: how this work arrived at the same place as 200-year-old theory
   - Paper overview

2. **Related work — the rhetorical tradition and documentation practice**
   - Newman (1827): the foundational intent-based taxonomy; the five modes and Bain's regression
   - Kinneavy (1971): the communication triangle; four aims; the decoder corner
   - Anker (~1998): nine pedagogical modes; sub-mode elaboration within exposition
   - Diátaxis (2017): reader-need framework; two-axis grid; practitioner origin story
   - The gap: none of these frameworks have been explicitly connected; no unified framework exists; no application to practitioner technical content

3. **Four independent convergences — the structural argument**
   - Newman, Kinneavy, Procida, this work: same taxonomy, four independent origins, 200 years apart
   - The significance: convergence across domains, starting points, and eras suggests structural truth
   - Procida as a fourth independent arrival: philosopher who rediscovered Kinneavy without knowing it
   - The Kinneavy bridge: Diátaxis implements Kinneavy's referential aim, subdivided by reader need

4. **The orthogonal dimensions — why these frameworks complement rather than compete**
   - Newman: intent (author perspective)
   - Kinneavy: communicative aim (all corners of the communication triangle)
   - Anker: mode (text-type classification, pedagogical)
   - Diátaxis: reader need (decoder perspective, practical)
   - Why Anker subsumes Diátaxis categorically but not dimensionally — the tutorial/how-to discrimination test
   - Why Kinneavy is closer to Diátaxis than Anker — the decoder-centred analysis

5. **The unified framework — a proposal**
   - Intent × communicative aim × mode × reader need × form
   - Newman restoration: restoring the persuasive/argumentative distinction Bain collapsed
   - The four content types (note, article, essay, InfoBrief) as natural emergence from this space
   - Scannability as a cross-cutting structural requirement — grounded in Nielsen Norman et al.
   - Framed as a proposal requiring validation — not a proven framework

6. **Application — LLM content generation guidance**
   - Industry heuristics mapped to rhetorical theory: short paragraphs → situational awareness; bullets → referential structure; answer-first → argumentatio ordering
   - How the unified framework produces principled, context-sensitive guidance vs undifferentiated rules
   - The AI trigger problem: dense prose as format signal — the fluency fallacy in reverse
   - Worked examples: the InfoBrief, the structured essay, the technical how-to

7. **Discussion and limitations**
   - The empirical gap: AI trigger claim needs reader studies; unified model needs validation
   - Scope limits: this work is practitioner technical content — may not generalise to all domains
   - The Kinneavy critique: aims aren't cleanly separable; dominant intent, not exclusive intent
   - Future work: empirical validation; application to other content domains; LLM prompting experiments

8. **Conclusion**
   - The gap this fills: first explicit connection; constructive complement to MacArthur
   - The minimum contribution: the literature review stands independently
   - The broader implication: practitioner content guidance should be grounded in rhetorical theory, not heuristics

---

## Work To Do — Full Consolidated List

*Last updated: 2026-05-14. Resume here in future sessions.*

---

### A. Skill and Writing Style Work (no research needed — do next)

**A1. Commit uncommitted cc-praxis changes**
Files modified, not yet committed:
- `docs/prompt-snippets.md` — canonical workflow snippet
- `writing-styles/blog-technical.md` — bullet/table guidance updates
- `writing-styles/structured-essay.md` — new file
- `writing-styles/infobrief.md` — renamed from brief.md
- `writing-styles/README.md` — updated selection logic
- `docs/content-taxonomy-article-notes.md` — these notes
- `IDEAS.md` — three new entries
After committing, run `sync-local` to propagate to ~/.claude/skills/

**A2. Issue #70 — write-blog skill restructure**
Create the universal forms layer and structure principles file. Spec is clear:
```
write-blog/defaults/
  structure-principles.md     ← NEW: scannability, heading tests, element selection

write-blog/forms/
  note.md                     ← NEW: universal form
  article.md                  ← NEW: universal form (single and multi-part)
  essay.md                    ← NEW: universal form (single and multi-part)
  infobrief.md                ← NEW: universal form
```
Also: split `blog-technical.md` → universal parts into forms/, personal parts into `mark-proctor.md` in writing-styles/

**A3. Update structured-essay.md and infobrief.md**
The structured-essay.md was updated with the three-appeals section and headings analysis. Review against the full taxonomy discussion (note/article/essay/InfoBrief) to ensure consistency. infobrief.md may need updating to reflect the optional navigation layer pattern (links into accompanying article).

**A4. Run sync-local after all skill changes**
```bash
python3 scripts/claude-skill sync-local --all -y
```

---

### B. Content to Write (no research needed — do after skill work)

**B1. Proposal B — Standalone short practical article**
- 400–600 words, Phase 3 voice (concise, direct, peer-to-peer, ends when point is made)
- The four content types with intent test
- Scannability as universal principle
- One paragraph alluding to academic grounding, links to series parts 3 and 4
- NOT an InfoBrief — prose-led, selective bullets/tables
- Audience: practitioners wanting the framework, not the history

**B2. Proposal A — Six-part article series**
Parts confirmed. Draft order: Part 1 first (the hook — AI reading problem), then Part 3 (hiding in plain sight — the discovery narrative), then others.

| Part | Title | Status |
|------|-------|--------|
| 1 | The AI Reading Problem | Notes ready |
| 2 | Finding the Forms | Notes ready |
| 3 | Hiding in Plain Sight | Notes ready |
| 4 | The Intellectual Lineage | Notes ready |
| 5 | The Gap Nobody Noticed | Notes ready — strongest for general audience |
| 6 | Toward a Unified Framework | Notes ready |

**B3. A/B test on "When the Machine Codes"**
Pick one section from the 6-part series. Rewrite in two forms: current (dense prose) vs. structured/compact. Compare. Use result to validate the scannability principle in practice and inform the writing style guide.

---

### C. Research Still To Do (for the academic paper only)

**C1. Papers needed — ask user to retrieve:**

| Item | What | Why | Access |
|------|------|-----|--------|
| 1979 *College English* paper | "Applications of Kinneavy's Theory of Discourse to Technical Writing" Vol. 40 No. 6 | Only citation in our network touching technical writing | JSTOR institutional |
| "Inform or Persuade?" (2020) | *Technical Communication* (STC) | Applies Kinneavy to TechComm textbooks | STC membership |
| Juszkiewicz et al. (2019) | *Rhetorical machines: writing, code, and computational ethics* | Rhetoric + computational/AI contexts; found via MacArthur | Library/purchase |

**C2. Database searches still needed:**

| Database | Searches | Status | Access |
|----------|---------|--------|--------|
| JSTOR | `Kinneavy AND Diataxis` | ✅ DONE — zero results | Done by user |
| JSTOR | `rhetorical modes AND documentation framework` | ✅ DONE — results but unrelated | Done by user |
| JSTOR | `Newman AND documentation taxonomy` | ✅ DONE — results but unrelated | Done by user |
| JSTOR | `Kinneavy AND "technical writing"` | ❌ Not done | Institutional |
| JSTOR | `"aims of discourse" AND "technical communication"` | ❌ Not done | Institutional |
| MLA International Bibliography | All of the above | ❌ Not done | Institutional |
| Google Scholar | All key combinations | ✅ DONE — zero results | Done |
| Semantic Scholar | Kinneavy 1969 citation network (64 papers) | ✅ DONE — zero relevant | Done |

**C3. Web resources to read (free — can do in future session):**
- Procida's theoretical background: [diataxis.fr/theory/](https://diataxis.fr/theory/) — confirm first-principles claim
- Spinuzzi's Kinneavy reading notes: [spinuzzi.blogspot.com/2015/12/reading-theory-of-discourse.html](http://spinuzzi.blogspot.com/2015/12/reading-theory-of-discourse.html)

**C4. Parked — lower priority:**
- Genre theory: Swales (*Genre Analysis*, 1990), Bhatia
- Minimalism (John Carroll) — tutorial/how-to distinction
- Plain language movement — heuristics argument grounding
- Nielsen Norman specific studies — scannability citation

---

### D. Academic Paper (after article series, after remaining research)

**Recommended sequence:**
1. Write article series (B1, B2) — tests whether argument lands with audience
2. Complete remaining research (C1, C2, C3) — closes the gap verification
3. Draft paper — minimum version first (literature review + Kinneavy bridge)
4. Consider empirical follow-on (reader studies on AI trigger claim) as second paper

**Paper status:** Notes comprehensive, argument solid, gap confirmed. Ready to draft when research is complete and article series is published.

**Target journal (priority):** *AI & Society* (Springer) — MacArthur (2025) published here; natural home for constructive complement.


---

## Corpus Analysis Project — Full Design `[SKILL]`

*Three separate passes. Each pass has a clear, testable output before the next begins.*

---

### Goals

1. **Validate the taxonomy** — stress-test Note / Article / InfoBrief / News against 577 real posts written before the taxonomy existed. Flag what fits cleanly, what is forced, and what leaks through without a home.
2. **Build the corpus catalogue** — machine-readable metadata for all 577 posts with IDs, taxonomy classification, quality ratings, and topic labels.
3. **Build the content index** — inverted index by taxonomy type and by label, human-navigable.
4. **Build the linguistic fingerprint** — deep stylistic analysis from a stratified sample.

The Note/Article/InfoBrief distinction is the hardest case. InfoBrief may be nearly empty in a corpus written before the taxonomy — that itself is information. Note vs Article (encoder-dominant/quick vs decoder-standalone/crafted) will be the most contested boundary.

---

### ID System

Deterministic 3-digit counter assigned by sorting posts chronologically (filename is date-prefixed, so alphabetical = chronological). IDs 001–577. Same result every time. ID is the primary key linking the catalogue, index, and fingerprint.

---

### File Locations

```
~/claude-workspace/corpus/
  catalogue.tsv              ← all 577, machine-readable (Pass 1 output)
  label-vocabulary.md        ← seed + discovered labels + variants
  index.md                   ← inverted index by taxonomy + label (Pass 2 output)

~/claude-workspace/writing-styles/
  mark-proctor-voice.md      ← linguistic fingerprint (Pass 3 output)
```

---

### Pass 1 — Corpus Catalogue + Taxonomy Validation + Labels

#### Pass 1a — Seed-based classification and discovery

**What the agent does per post:**
- Read the post
- Assign taxonomy type + subtype (see definitions below)
- Rate confidence: high / medium / low / uncertain
- Flag if uncertain: one-line note on what's ambiguous
- Rate quality: exemplary / strong / typical / weak
- Identify phase: Explorer (2006–09) / Authority (2009–12) / Strategist (2013–17)
- Count words and assign length bucket
- Apply seed labels where they fit
- Discover and record any labels outside the seed
- Write one-line notable note

**TSV fields (catalogue.tsv):**

| Field | Values |
|-------|--------|
| id | 001–577 |
| date | YYYY-MM-DD |
| title | from frontmatter or first heading |
| path | relative to mark-proctor/ |
| type | Note / Article / InfoBrief / News |
| subtype | log / musing / idea / tutorial / how-to / explanation / commentary / essay / release / event / industry |
| confidence | high / medium / low / uncertain |
| flag | blank or one-line ambiguity note |
| quality | exemplary / strong / typical / weak |
| phase | Explorer / Authority / Strategist |
| words | integer |
| length | micro / short / medium / long |
| labels | comma-separated, seed-normalised |
| discovered | comma-separated new labels not in seed |
| notable | one-line note |

**Taxonomy definitions for the agent:**

*Note* — Quick, informal, encoder-dominant. Written fast, assumes shared context, not crafted for a cold reader. Subcategories:
- **log** — records what happened (session, project update, event recap)
- **musing** — thinking out loud or brief external reaction; encoder-dominant, low investment, not fully formed
- **idea** — developed enough to propose something specific

*Article* — Full treatment of a topic, crafted for a cold reader who needs no prior context. Subcategories:
- **tutorial** — learn by doing, reader acquires capability
- **how-to** — task completion, reader applies existing capability
- **explanation** — understand why, builds mental model
- **commentary** — informed take, personal voice, no formal thesis
- **essay** — argued to a conclusion: thesis, evidence, counter-arguments

*InfoBrief* — Maximum information density, minimum prose. Fully scannable. Rare in this corpus — flag any genuine instance.

*News* — Something happened externally worth sharing. Subcategories:
- **release** — software release, version, new feature
- **event** — conference, talk, meetup announcement or recap
- **industry** — observation on something in the broader landscape

**Hard cases — guidance for the agent:**

Note vs Article is the key boundary. If in doubt:
- Was this clearly written fast, assuming the reader knows the context? → Note
- Does it provide enough background that a cold reader could follow? → Article
- Could it be both? → classify as whichever is more dominant, flag with "Note/Article boundary"

InfoBrief is rare. Only classify as InfoBrief if the post is genuinely scannable as a complete experience — most dense posts are still Articles, just short ones.

Multi-part posts — classify each part individually. Note in the flag field if it's part of a series.

**Seed label vocabulary (Pass 1a):**

```
Technology: java, quarkus, drools, jbpm, bpmn, kie, optaplanner, vert.x,
            maven, spring, ai, llm, python, typescript, hibernate, cdi,
            infinispan, wildfly, jboss, openshift, kubernetes, docker

Concepts:   rules-engine, backward-chaining, forward-chaining,
            pattern-matching, algorithm, performance, reactive,
            event-driven, decision-table, cep, drl, rete, phreak,
            truth-maintenance, agenda, conflict-resolution, working-memory

Standards:  dmn, pmml, cmmn, bpmn2, openapi, rest, json, xml

Domain:     open-source, licensing, community, release, conference,
            benchmark, architecture, refactoring, testing, debugging

Personal:   drools-team, kie-team, jboss-team, red-hat
```

**Batching:** ~60–80 posts per agent call. ~8–10 agent calls for all 577.

---

#### Between 1a and 1b — Human review step

Review the `discovered` column from all catalogue rows. For each new label:
- Is it a variant of an existing seed label? → record as variant, map to canonical
- Is it genuinely new? → add to vocabulary
- Is it too specific to be useful? → discard

Update `label-vocabulary.md` with the expanded vocabulary and variant mappings:

```
quarkus    | seed    | variants: Quarkus, quarkus-framework, JBoss Quarkus
drools     | seed    | variants: Drools, JBoss Drools
arc        | discovered pass 1a | CDI container in Quarkus
```

---

#### Pass 1b — Full vocabulary relabelling

Re-read all 577 posts with the expanded vocabulary. Only update the `labels` and `discovered` fields. Do not redo taxonomy, quality, or other fields. Purpose: catch labels that Pass 1a missed because the label didn't exist yet, and normalize variant forms.

Output: updated catalogue.tsv with final, normalized labels.

---

### Pass 2 — Content Index

From the completed catalogue.tsv, build index.md. Mechanical transformation — no reading of posts required.

**Structure of index.md:**

```markdown
# Content Index

## By Taxonomy

### Note / log
001 — title (date)
023 — title (date)
...

### Note / musing
...

### Article / essay
...

[etc. for each type/subtype]

## By Label

### quarkus
001, 023, 045, 089 — [count: N posts]

### drools
...

[etc. for each label, sorted by post count descending]
```

Each ID in the index is navigable: look up ID in catalogue.tsv to get the path.

---

### Pass 3 — Linguistic Fingerprint

Stratified sample from the completed catalogue. Now we know which posts are exemplary per type (from quality ratings) — use those for sampling.

Sample: ~4–5 exemplary posts per phase × 3 phases + 5–8 negative examples (weak quality) = ~20–23 posts for deep analysis.

Output: fills `mark-proctor-voice.md` per the agreed structure.

---

### Taxonomy Validation — What to Watch For

The agent will flag uncertain classifications. After all passes, review:

1. **What leaks through** — posts that don't fit any type cleanly. Do they suggest a missing category?
2. **What feels forced** — posts classified correctly but where the agent notes it's a stretch. Are these genuine edge cases or taxonomy refinement opportunities?
3. **Note/Article boundary posts** — the most likely source of tension. How many? What makes them ambiguous?
4. **InfoBrief instances** — how many genuine InfoBriefs exist in the corpus? If zero, that's informative — InfoBrief is a new form not in the historical writing style.
5. **Subtype distribution** — are some subtypes nearly empty (musing? idea?)? Does that suggest they're too fine-grained, or just underrepresented in this corpus?

The taxonomy may need refinement after this pass. That is the point.

---

### Work To Do — Update

Add to section A (skill and writing work):

**A5. Run corpus analysis Pass 1a**
- Requires: catalogue.tsv template, label vocabulary seed, taxonomy definitions
- Output: catalogue.tsv (partial, labels from seed only)

**A6. Human review between 1a and 1b**
- Review discovered labels, normalize, update label-vocabulary.md
- Review flagged uncertain taxonomy classifications

**A7. Run corpus analysis Pass 1b**
- Requires: completed label-vocabulary.md
- Output: final catalogue.tsv

**A8. Build content index (Pass 2)**
- Mechanical transformation from catalogue.tsv
- Output: corpus/index.md

**A9. Run linguistic fingerprint (Pass 3)**
- Requires: completed catalogue.tsv (for stratified sampling)
- Output: writing-styles/mark-proctor-voice.md

