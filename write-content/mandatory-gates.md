# Mandatory Gates

Process control for content generation. These are not writing rules — they are
control flow gates that must run at specific points in the workflow regardless
of form, mode, voice, or invocation context.

Loaded explicitly in SKILL.md Step 5 (pre-draft gate) and Step 7 (quality check
+ third-party review). Cannot be skipped.

---

## Pre-Draft Gate (Step 5 — before writing begins)

Do not generate any prose until all items below are resolved.

**Voice classification:**

For forms with author participation (diary, article, note, brief, news):
- Is Claude a participant? If yes — for each section, decide in advance:
  "I", "we", or "Claude [verb]"?
- Which moments are Claude-naming moments (catching something, reporting back,
  going off-script, getting something wrong)?
- Is Claude introduced by name before "we" is first used?

For technical documentation:
- Confirm target section and its mode from the mode map in
  `forms/technical-documentation.md`
- Confirm the correct mode file is loaded for this section
- No I/we/Claude register applies — technical docs are system-centric

**Style guide check:**
- Has the voice layer (personal or common) been loaded?
- After drafting, verify each "What to Avoid" item in the voice file before presenting
- Do not show a draft that fails the style guide — fix first

**Factual accuracy check:**

For any duration, count, or magnitude claim:
- Verify against `git log`, file diffs, or session context before presenting
- If unverifiable: qualify as an estimate ("roughly a day", "several files") or remove
- Never fabricate or inflate timeframes, scale, or difficulty

---

## Third-Party Reference Review (Step 7 — after drafting, before writing to disk)

**Non-negotiable. Cannot be skipped due to invocation context or time pressure.**

If the author explicitly asked for specific content to be included, they will
choose Keep. The process still runs — it confirms the intent.

### What triggers a flag

Any sentence referring to a named person (other than the author or Claude)
or an identifiable group must be flagged:

| Category | Examples |
|---|---|
| **Opinion** | "X is brilliant", "Y doesn't get it" |
| **Characterisation** | Personality, competence, attitude of a person |
| **Generalisation** | "developers tend to...", "the Java community always..." |
| **Frustration / complaint** | "X was unhelpful", "Y's team doesn't understand this" |
| **Competitive** | Favouring or criticising a product in a way that could embarrass |
| **Blame** | "X's decision caused this problem" — even if accurate |
| **Gossip** | Inside knowledge about what someone did that they haven't made public |
| **Presumptuous** | Speaking for someone else's motivations — "X probably thought..." |
| **Reputational** | Anything affecting how someone is perceived professionally |
| **Overly familiar** | Using private knowledge in a public context |
| **Unsolicited praise** | "X is the best engineer I know" |
| **Political / cultural** | Anything touching politics, nationality, religion, gender, ethnicity |
| **Personal** | Any information the subject might prefer not to be public |

**The test:** If the subject of this sentence read it, could they feel embarrassed,
misrepresented, criticised, patronised, or uncomfortable? If yes — flag it.
**If unsure — flag it.**

### Safe exceptions — no flag needed

- **Factual citations** — "X wrote this paper", "Y founded this company"
- **Technical attribution** — "Built on Quarkus, maintained by Red Hat"
- **Public announcements** — "Anthropic released Claude 4", "GitHub open-sourced X"
- **Quoting someone's own public words** — from a blog post, talk, or documentation
- **Tools as tools** — "We used AWS S3", "Built in IntelliJ" — no evaluative statement

### The review process

After drafting and before writing to disk:

1. Scan the complete draft for every sentence containing a reference to a named
   person (other than the author or Claude) or an identifiable group.

2. Present each flagged sentence:
   ```
   ⚠️  Third-party reference — author approval required:

   Sentence: "<exact sentence>"
   Reason flagged: <one-line reason>

   Options:
     [K] Keep as written
     [R] Rephrase — describe what to change
     [D] Delete this sentence
   ```

3. Wait for the author's decision on each flagged sentence before proceeding.

4. Apply all decisions, then re-scan to confirm zero flagged sentences remain.

5. Only after zero flagged sentences remain may the content be written to disk.

**There is no shortcut.** If the author is not available to review, hold the
draft and wait. Do not write to disk with unresolved flags.
