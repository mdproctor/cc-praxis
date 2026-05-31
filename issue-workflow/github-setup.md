# GitHub Setup Reference

Used by `issue-workflow` Phase 0 Steps 4–5.

---

## Standard Labels

Create these labels if missing. They map to GitHub's auto-generated changelog sections:

| Label | Changelog section | When to use |
|-------|-----------------|-------------|
| `epic` | — | Parent issue grouping related child issues |
| `enhancement` | ✨ New Features | New capability or improvement |
| `bug` | 🐛 Bug Fixes | Something was broken |
| `documentation` | 📚 Documentation | Docs only, no code change |
| `performance` | ⚡ Performance | Faster, leaner, cheaper |
| `security` | 🔒 Security | Security fix or hardening |
| `refactor` | 🔧 Internal | Code change, no user-visible effect |

```bash
gh label create "epic" --color "#7057ff" --description "Parent issue grouping related work" --repo {owner/repo}
gh label create "enhancement" --color "#84b6eb" --description "New feature or improvement" --repo {owner/repo}
gh label create "bug" --color "#d73a4a" --description "Something is broken" --repo {owner/repo}
gh label create "documentation" --color "#0075ca" --description "Documentation only" --repo {owner/repo}
gh label create "performance" --color "#e4e669" --description "Performance improvement" --repo {owner/repo}
gh label create "security" --color "#e11d48" --description "Security fix or hardening" --repo {owner/repo}
gh label create "refactor" --color "#6e6e6e" --description "Code change without user-visible effect" --repo {owner/repo}
```

---

## Scale and Complexity Labels

Every issue must carry one scale label and one complexity label. Create these in every repo:

```bash
gh label create "scale: XS"        --color "d4edda" --description "Lines of change"                        --repo {owner/repo}
gh label create "scale: S"         --color "a8d5b5" --description "Single class / small file"              --repo {owner/repo}
gh label create "scale: M"         --color "f0c27f" --description "Multi-class / multi-file"               --repo {owner/repo}
gh label create "scale: L"         --color "e8956d" --description "Substantial feature"                    --repo {owner/repo}
gh label create "scale: XL"        --color "c0392b" --description "Major rework"                           --repo {owner/repo}
gh label create "complexity: Low"  --color "dbeafe" --description "Clear path, no unknowns"                --repo {owner/repo}
gh label create "complexity: Med"  --color "93c5fd" --description "Some design or unknowns"                --repo {owner/repo}
gh label create "complexity: High" --color "1d4ed8" --description "Significant unknowns, design required"  --repo {owner/repo}
```

---

## Work Tracking CLAUDE.md Template

Add or update the `## Work Tracking` section:

```markdown
## Work Tracking

**Issue tracking:** enabled
**GitHub repo:** {owner/repo}
**Changelog:** GitHub Releases (run `gh release create --generate-notes` at milestones)

**Automatic behaviours (Claude follows these at all times in this project):**
- **Before implementation begins** — when the user says "implement", "start coding",
  "execute the plan", "let's build", or similar: check if an active issue or epic
  exists. If not, run issue-workflow Phase 1 to create one **before writing any code**.
- **Before writing any code** — check if an issue exists for what's about to be
  implemented. If not, draft one and assess epic placement (issue-workflow Phase 2)
  before starting. Also check if the work spans multiple concerns.
- **Before any commit** — run issue-workflow Phase 3 (via git-commit) to confirm
  issue linkage and check for split candidates. This is a fallback — the issue
  should already exist from before implementation began.
- **All commits should reference an issue** — `Refs #N` (ongoing) or `Closes #N` (done).
  If the user explicitly says to skip ("commit as is", "no issue"), ask once to confirm
  before proceeding — it must be a deliberate choice, not a default.
```
