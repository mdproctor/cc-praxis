# Heading Smell Check

Run these five checks before committing. Each catches a specific failure mode.

**1. The character drain check.** Read just the H2 headings in order, like a table of contents. Could any of them appear unchanged in a completely different blog post about a completely different project? If yes, they've lost their specificity. `## What we tried` could be in any post ever written. `## The Pivots (There Were Several)` belongs to this one.

**2. The before/after check.** For every heading you changed, ask: did the new version gain something, lose something, or both? If the new version is shorter and more generic — stop. You replaced thematic content with structural scaffolding. Changes should add, never only subtract.

**3. The dropped heading check.** For every heading that existed before your edit and doesn't exist after — where did its content go? If the answer is "I merged it into another section," check that the merged section still has a heading that signals what the content is. Merging two sections into headingless prose quietly buries the structure the reader was using.

**4. The H2 container check.** If you have an H2 with H3 subsections beneath it, read the H2 alone. Does it say anything interesting? `## What we tried` says nothing — the H3s do all the work. But H3s are invisible to a scanner. The H2 needs to carry meaning too.

**5. The substitution test.** For any heading you replaced, ask: if the original author saw this new heading, would they recognise it as an improvement or feel like something was lost? A thematic heading that someone wrote with care — `## Six Pivots, Zero Architecture Changes`, `## The GCD Block That Never Ran` — signals intent. Replacing it with a structural slot signals you didn't read it carefully.

**The underlying principle:** thematic headings are primary, structural labels are additive. Before changing any heading, ask: am I adding value or extracting it?
