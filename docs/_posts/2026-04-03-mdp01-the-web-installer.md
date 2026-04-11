---
layout: post
title: "cc-praxis — The Web Installer"
date: 2026-04-03
type: phase-update
---
# cc-praxis — The Web Installer

**Date:** 2026-04-03
**Type:** phase-update

---

Managing skills was entirely CLI-based. To install a bundle you ran a command. To see what was installed you ran another command. To understand how skills chain together you read Markdown.

I wanted something visual.

## What we were trying to achieve: A UI that doubles as a landing page

A web app showing all skills grouped by bundle, with live install state. Something that could serve as a GitHub Pages landing page when hosted remotely, and as a functional local installer when served by a Python server. One file, two behaviours.

## What we believed going in: A contained frontend task

One HTML file, some CSS, JavaScript to call a local API. A few days of work.

What I hadn't accounted for was how much complexity lives in "show what's installed with live state" — especially when bundle counts need to be accurate, modal dialogs need to operate on exactly the right skills, and the chain graph needs to render inline as a visual dependency viewer.

## The single-file approach

We built the entire UI as one `docs/index.html`. Context detection is a simple JavaScript check:

```javascript
['localhost', '127.0.0.1', ''].includes(location.hostname)
```

On localhost, all three tabs are live. On GitHub Pages, the Install tab is hidden — you can browse but not install. One file, two behaviours.

## The chain graph

Each skill card in the Browse view has a Chain button that inserts an inline row showing the skill's ancestry left-to-right, then its direct children with collapsible grandchildren. We went through several approaches:

- Hover tooltip — rejected, too transient
- Full modal — rejected, too heavy
- Inline row inserting above or below the card depending on viewport position — this worked

The cycle guard was non-trivial. `java-code-review → java-git-commit → java-code-review` would otherwise loop. We filter grandchildren that already appear in the ancestry chain.

## The --skills flag that didn't exist

When I actually tried the web installer against the Python bundle, it came back immediately: `sync-local: unrecognized arguments: --skills`. I'd written the server to call a command flag that didn't exist on the `sync-local` subcommand.

The existing tests had been mocking `_run` so they never caught this. The fix required adding `--skills` to `sync-local` in the installer script, then updating the server. It was the first real-world test and it broke on the first click.

## Bundle state was hardcoded

After fixing the install command, I discovered the bundle counts — "3 of 5 installed" — were hardcoded HTML that never updated. The JavaScript `applyState()` function updated individual skill rows but left bundle-level state, counts, and button visibility entirely static.

We fixed this by adding a `bundles` field to the `/api/state` response, computed from `marketplace.json`, and a `updateBundleStates()` JavaScript function that consumes it. Three bundles also had missing action buttons entirely — Principles had no Uninstall button, TypeScript had no Install button, Python had no Uninstall. All hardcoded to the wrong state.

## The modal was lying

With 2 of 5 Python skills installed, clicking the bundle Uninstall button showed "Uninstall 5 skills." It would have uninstalled all five, including three that weren't there. We fixed this by filtering `cfg.skills` against `INSTALLED` in `openModal()` — uninstall only acts on what's actually installed, install only acts on what's actually missing.

## What changed and why: A UI layer became real software

The scope expanded significantly. By the time it was done, the web installer had its own test suite: 55 server API tests, 40 real integration tests running actual installs against a temp directory, and 38 Playwright browser tests.

The integration tests — which actually run `sync-local` against a temp directory via a `CLAUDE_SKILLS_DIR` environment variable — caught the `--skills` bug immediately. Mocking the subprocess calls hid real problems. Real tests against real behaviour are the only kind that count here.

The web installer is only as correct as the state it reflects. The bundle counts, modal skill lists, and button visibility all had hardcoded values in the mockup that looked fine during development and were completely wrong once real install state loaded.
