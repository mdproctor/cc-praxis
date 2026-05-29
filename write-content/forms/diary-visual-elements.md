# Visual Elements Reference

Used by `write-blog` Step 4. Visual content makes posts readable and credible.

---

## Code Blocks

Show the actual code that matters. Not a summary, not a reference to a file — the
real snippet. If the logic is interesting, show it. Short is better; extract the
5–10 lines that tell the story.

---

## Illustrations

Small images that give the post visual rhythm. Sources:
- Web search for a relevant diagram, photo, or graphic (`WebSearch` + `WebFetch`)
- AI-generated illustration for the specific concept (note source in alt text)

Save to `blog/images/<YYYY-MM-DD-slug-description>.png` and reference as:

```markdown
![alt text describing the image](images/YYYY-MM-DD-slug-description.png)
```

One illustration per major section is enough. Don't illustrate for its own sake —
only when a visual genuinely adds something the prose doesn't.

---

## Screenshots

**Mandatory for any UI work.**

- Clip to the relevant component or area — full-page screenshots create scroll and lose focus
- If multiple states matter (before/after, hover, error), include both clipped side by side or sequentially
- The user provides the screenshot file; save to `blog/images/` alongside the entry
- Reference with descriptive alt text: `![The skill chain graph showing bidirectional links](images/...)` not `![screenshot]`

**If a section covers UI work and has no screenshot, the entry is incomplete.**
