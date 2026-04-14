---
layout: post
title: "cc-praxis — Where Claude Lives Now"
date: 2026-04-09
type: phase-update
entry_type: note
subtype: diary
projects: ["cc-praxis"]
---
# cc-praxis — Where Claude Lives Now

**Date:** 2026-04-09
**Type:** phase-update

---

## What I was trying to achieve: a home for methodology artifacts

The day started with a rename — `session-handover` → `handover` — which had been nagging since the terminology was settled weeks ago. Naming matters; a skill called `session-handover` when the act is a handover and the artifact is a handoff was a constant small confusion.

The bigger question: where should handovers, snapshots, ADRs, and blog entries live? Right now they go into the project repo alongside the code. For Drools or any upstream project I contribute to but don't own, that's a non-starter. Even for projects I do own, it creates noise — methodology churn mixed into code history.

The answer is a companion workspace directory outside the project repo. Getting there took three attempts.

## The design that almost worked, and the nine problems

A separate Claude had already done most of the design work in a parallel session — I found it on a branch: `claude/identify-non-coding-docs-vkAAd`. A workspace at `~/claude/private/<project>/`, all skills writing to workspace paths. Solid groundwork.

I brought Claude in to review it. We went through the remaining open questions — co-worker model, submodules vs filesystem discovery, the `design/` folder format — and converged on most of the details. Then I asked Claude to attack the design. Find every reason it won't work.

Claude came back with nine. The most serious: if Claude opens in the workspace (CWD) rather than the project, the project's `CLAUDE.md` never auto-loads. Skills route on project type, run build commands, follow commit conventions — all from `CLAUDE.md`. Also: `add-dir` doesn't persist across sessions, so every session needs a manual step just to reach the project.

The nine problems pointed toward "Claude should open in the project, not the workspace." But that breaks the artifact routing: any skill that writes to CWD — including superpowers skills outside anyone's control — would write to the project repo. The only way to make all skills write to the workspace universally is to make the workspace the CWD.

The fix was a symlink.

```bash
ln -sf ~/claude/private/cc-praxis/CLAUDE.md /path/to/project/CLAUDE.md
echo "CLAUDE.md" >> /path/to/project/.git/info/exclude
```

The workspace `CLAUDE.md` becomes the project's `CLAUDE.md` — same file, two paths. Claude opens in the workspace. If someone opens in the project by mistake, they still get full config. `.git/info/exclude` hides the symlink without touching the tracked `.gitignore`, which matters for projects like Drools where I have no commit rights.

The workspace `CLAUDE.md` also became the routing hub: a session-start `add-dir` instruction and an artifact locations table that overrides skill defaults:

```markdown
## Session Start
Run `add-dir /absolute/path/to/project` before any other work.

## Artifact Locations
| Skill         | Writes to     |
|---------------|---------------|
| brainstorming | `specs/`      |
| writing-plans | `plans/`      |
| handover      | `HANDOVER.md` |
```

`workspace-init` generates all of this. One command per project per machine. The implementation — `workspace-init` skill, path updates to five existing skills, hook extensions — is next session's work.

## What the health check found

A tier-3 project health check closed out the day. Write-blog was 568 lines; it's now 452, with the entry template, visual elements guide, and heading checks extracted to supporting files. The project-type validator was flagging historical blog entries for incomplete type lists — fixed with a one-line directory exclusion for frozen content. The `handover` rename had orphaned the skill's README description; that's back.

Most remaining findings were documentation lag from the workspace model not being implemented yet. Expected.
