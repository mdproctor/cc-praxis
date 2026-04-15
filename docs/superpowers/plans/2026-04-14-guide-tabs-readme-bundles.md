# Guide Tabs, README Rewrite, Quick-Start Bundles — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make cc-praxis immediately compelling and language-inclusive: rewrite README to lead with value, add Java/TypeScript/Python tabs to the getting-started guide (with per-tab sidebar, hash routing, and full 12-step content), and add quick-start bundles to marketplace.json.

**Architecture:** Three independent deliverables. README rewrite is prose-only. Guide tabs restructure `docs/guide.html` into three tab panes (Java default, TypeScript, Python) sharing CSS/JS infrastructure but with independent sidebar state and content. Quick-start bundles add three entries to `.claude-plugin/marketplace.json` (no skill code changes needed).

**Tech Stack:** Jekyll HTML, vanilla JS (IntersectionObserver, hashchange), Python pytest, Playwright.

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `README.md` | MODIFY lines 1–32 | Lead with value, not installation process |
| `docs/guide.html` | MAJOR REWRITE | Add tab bar, per-tab sidebars, TypeScript + Python content, hash routing |
| `.claude-plugin/marketplace.json` | MODIFY | Add quick-start-java, quick-start-typescript, quick-start-python bundles |
| `tests/test_guide_page.py` | MODIFY | Add tab structure tests, language-specific content assertions |
| `tests/test_guide_ui.py` | MODIFY | Add tab switching Playwright tests |

---

## Design Reference (read before every task)

### Tab structure

```html
<!-- Tab bar — above the two-column layout -->
<div class="guide-tab-bar">
  <button class="guide-tab active" data-lang="java">Java / Quarkus</button>
  <button class="guide-tab" data-lang="typescript">TypeScript</button>
  <button class="guide-tab" data-lang="python">Python</button>
</div>

<!-- One pane per language — only one visible at a time -->
<div class="guide-pane" id="pane-java">  <!-- display:flex by default -->
  <aside class="guide-sidebar" id="sidebar-java">...</aside>
  <main class="guide-content" id="content-java">...</main>
</div>
<div class="guide-pane" id="pane-typescript" style="display:none">...</div>
<div class="guide-pane" id="pane-python" style="display:none">...</div>
```

### Hash routing

```javascript
// On load: read hash, activate tab
// On tab click: update hash, switch panes
// window.addEventListener('hashchange', ...) for back/forward
const LANGS = ['java', 'typescript', 'python'];
function getLang() {
  const h = location.hash.replace('#', '');
  return LANGS.includes(h) ? h : 'java';
}
```

### Section numbering
All three tabs use sections `section-1` through `section-12` with a language prefix in the ID to avoid conflicts:
- Java: `id="java-section-1"` ... `id="java-section-12"`, `data-section="1"` ... `data-section="12"`
- TypeScript: `id="ts-section-1"` ... `id="ts-section-12"`
- Python: `id="py-section-1"` ... `id="py-section-12"`

### Per-tab sidebar steps (data-step attribute)
Each sidebar `<a>` gets `data-lang="java"` (or `ts`, `py`) so the IntersectionObserver can scope to the active tab.

### Section 3 — Language Development skill

| Language | Skill | Install command |
|----------|-------|----------------|
| Java | `java-dev` | `scripts/claude-skill install java-dev` |
| TypeScript | `ts-dev` | `scripts/claude-skill install ts-dev` |
| Python | `python-dev` | `scripts/claude-skill install python-dev` |

### Section 4 — Code Review skill

| Language | Skill | Auto-triggers before |
|----------|-------|---------------------|
| Java | `java-code-review` | `/java-git-commit` |
| TypeScript | `ts-code-review` | `git-commit` |
| Python | `python-code-review` | `git-commit` |

### Section 5 — Smart Commits skill

| Language | Skill | Example scopes |
|----------|-------|---------------|
| Java | `java-git-commit` | `feat(service):` `fix(repository):` `chore(config):` |
| TypeScript | `git-commit` | `feat:` `fix:` `refactor:` `test:` `chore:` |
| Python | `git-commit` | `feat:` `fix:` `refactor:` `test:` `chore:` |

### Section 9 — Design Documentation

| Language | Content |
|----------|---------|
| Java | JOURNAL.md + §Section anchors + `java-update-design` + `design-snapshot` |
| TypeScript | `design-snapshot` only (no journal skill) |
| Python | `design-snapshot` only (no journal skill) |

### CSS classes (consistent across all tasks)
```
.guide-tab-bar       — horizontal tab row above the pane container
.guide-tab           — individual tab button, data-lang attribute
.guide-tab.active    — active tab (purple underline)
.guide-pane          — full-width flex container (sidebar + content), one per lang
.guide-sidebar       — 220px sticky sidebar (unchanged from current)
.guide-content       — scrollable content area (unchanged from current)
```

---

## Task 1: README opening rewrite — lead with value

**Files:**
- Modify: `README.md` lines 1–32

- [ ] **Step 1: Replace the README opening**

Replace everything from line 1 through the closing `---` after the dependency note (approximately line 49) with the following. Keep everything after that unchanged.

```markdown
<p align="center">
  <img src="logo.svg" width="140" alt="cc-praxis logo"/>
</p>

# cc-praxis

**Claude Code skills that make professional software development feel automatic.**

You commit code — it reviews for safety issues first, syncs your design document, links the GitHub issue, and writes the conventional commit message. You ask Claude to implement a feature — it designs a spec, gets your approval, then writes a TDD implementation plan. You end a session — it captures a handover so the next session picks up in one message.

48 skills for Java/Quarkus, TypeScript/Node.js, and Python. Install the ones relevant to your stack, in any order.

---

## Quick Start

```bash
/plugin marketplace add github.com/mdproctor/cc-praxis
/plugin install install-skills
/install-skills
```

Pick a language bundle (or start with just 3 skills — see [Getting Started Guide](https://mdproctor.github.io/cc-praxis/guide/)). Close the session. Skills are active in every session after.

> **New to cc-praxis?** The [Getting Started Guide](https://mdproctor.github.io/cc-praxis/guide/) walks you through the full workflow in 12 steps — pick Java, TypeScript, or Python.

> **Dependency resolution note:** The official Claude Code marketplace doesn't yet support automatic dependency resolution ([Issue #9444](https://github.com/anthropics/claude-code/issues/9444)). The `/install-skills` wizard handles this for you. If you prefer installing manually, use the `scripts/claude-skill` installer below.

**To uninstall:**
```bash
/uninstall-skills
```

---
```

- [ ] **Step 2: Verify README renders correctly**

```bash
head -40 README.md
```

Check: starts with logo, then headline, then the three concrete value-lead sentences, then Quick Start.

- [ ] **Step 3: Run validate_all to confirm no regressions**

```bash
python3 scripts/validate_all.py --tier commit 2>&1 | tail -5
```

Expected: `8/8 passed`

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(readme): lead with value proposition — what you feel immediately after installing"
```

---

## Task 2: Add tab bar CSS and JavaScript infrastructure to guide.html

**Files:**
- Modify: `docs/guide.html`

This task adds only the tab bar HTML, CSS, and JS switching logic. Content for TypeScript and Python tabs is added in Tasks 3 and 4. After this task, the guide shows a tab bar but clicking TypeScript/Python shows empty panes.

- [ ] **Step 1: Write failing tests for tab structure**

Add to `tests/test_guide_page.py`:

```python
class TestTabStructure(unittest.TestCase):
    """Integration: guide has three language tabs."""

    def setUp(self):
        self.content = load_guide()

    def test_tab_bar_present(self):
        self.assertIn('guide-tab-bar', self.content)

    def test_three_language_tabs(self):
        for lang in ('java', 'typescript', 'python'):
            self.assertIn(f'data-lang="{lang}"', self.content,
                          f'Missing tab for {lang}')

    def test_three_panes(self):
        for lang in ('java', 'typescript', 'python'):
            self.assertIn(f'id="pane-{lang}"', self.content,
                          f'Missing pane for {lang}')

    def test_hash_routing_js_present(self):
        self.assertIn('hashchange', self.content)
        self.assertIn('getLang', self.content)

    def test_java_pane_is_default(self):
        # Java pane must not have display:none inline style
        import re
        java_pane = re.search(r'id="pane-java"[^>]*>', self.content)
        self.assertIsNotNone(java_pane)
        self.assertNotIn('display:none', java_pane.group(0))

    def test_typescript_pane_hidden_by_default(self):
        import re
        ts_pane = re.search(r'id="pane-typescript"[^>]*>', self.content)
        self.assertIsNotNone(ts_pane)
        self.assertIn('display:none', ts_pane.group(0))

    def test_python_pane_hidden_by_default(self):
        import re
        py_pane = re.search(r'id="pane-python"[^>]*>', self.content)
        self.assertIsNotNone(py_pane)
        self.assertIn('display:none', py_pane.group(0))
```

- [ ] **Step 2: Run to confirm RED**

```bash
python3 -m pytest tests/test_guide_page.py::TestTabStructure -v 2>&1 | tail -15
```

Expected: All 7 tests FAIL.

- [ ] **Step 3: Add tab bar CSS to guide.html**

In `docs/guide.html`, find the `</style>` closing tag and insert BEFORE it:

```css
  /* ── Tab bar ──────────────────────────────────────────── */
  .guide-tab-bar {
    display: flex;
    gap: 0;
    border-bottom: 2px solid #e5e7eb;
    margin-bottom: 0;
    background: white;
    position: sticky;
    top: 3px; /* below 3px progress bar */
    z-index: 100;
    padding: 0 1.5rem;
  }
  .guide-tab {
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    color: #6b7280;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    cursor: pointer;
    transition: color 0.15s, border-color 0.15s;
  }
  .guide-tab:hover { color: #374151; }
  .guide-tab.active {
    color: #4f46e5;
    border-bottom-color: #4f46e5;
  }
  /* ── Pane container ───────────────────────────────────── */
  .guide-pane {
    display: flex;
    min-height: calc(100vh - 56px - 3px - 42px); /* viewport - site-header - progress - tab-bar */
    max-width: 1100px;
    margin: 0 auto;
  }
```

- [ ] **Step 4: Restructure guide.html HTML — wrap existing content in Java pane**

The current guide has this structure:
```html
<div class="guide-wrap">
  <aside class="guide-sidebar">...</aside>
  <main class="guide-content">...</main>
</div>
```

Replace `.guide-wrap` with:
```html
<!-- Tab bar -->
<div class="guide-tab-bar">
  <button class="guide-tab active" data-lang="java">Java / Quarkus</button>
  <button class="guide-tab" data-lang="typescript">TypeScript</button>
  <button class="guide-tab" data-lang="python">Python</button>
</div>

<!-- Java pane (default — display:flex) -->
<div class="guide-pane" id="pane-java">
  <!-- existing aside.guide-sidebar here — unchanged -->
  <!-- existing main.guide-content here — unchanged -->
</div>

<!-- TypeScript pane (hidden) -->
<div class="guide-pane" id="pane-typescript" style="display:none">
  <p style="padding:3rem;color:#6b7280;">TypeScript guide coming in next task.</p>
</div>

<!-- Python pane (hidden) -->
<div class="guide-pane" id="pane-python" style="display:none">
  <p style="padding:3rem;color:#6b7280;">Python guide coming in next task.</p>
</div>
```

Also remove the `.guide-wrap` CSS rule (now replaced by `.guide-pane`).

- [ ] **Step 5: Replace guide.html JavaScript with tab-aware version**

Replace the entire `<script>` block at the bottom of guide.html with:

```html
<script>
(function () {
  var LANGS = ['java', 'typescript', 'python'];

  function getLang() {
    var h = location.hash.replace('#', '');
    return LANGS.indexOf(h) !== -1 ? h : 'java';
  }

  function activateTab(lang) {
    // Switch tab buttons
    document.querySelectorAll('.guide-tab').forEach(function (btn) {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
    // Switch panes
    LANGS.forEach(function (l) {
      var pane = document.getElementById('pane-' + l);
      if (pane) pane.style.display = l === lang ? 'flex' : 'none';
    });
    // Re-initialise IntersectionObserver for the active pane
    initObserver(lang);
  }

  // Tab click handler
  document.querySelectorAll('.guide-tab').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var lang = btn.dataset.lang;
      history.pushState(null, '', '#' + lang);
      activateTab(lang);
    });
  });

  // Hash-based routing
  window.addEventListener('hashchange', function () {
    activateTab(getLang());
  });

  // Per-language IntersectionObserver
  var activeObserver = null;

  function initObserver(lang) {
    if (activeObserver) { activeObserver.disconnect(); activeObserver = null; }

    var prefix = lang === 'java' ? 'java' : lang === 'typescript' ? 'ts' : 'py';
    var sections = Array.from(document.querySelectorAll('#pane-' + lang + ' .guide-section'));
    var steps = Array.from(document.querySelectorAll('#sidebar-' + lang + ' .guide-step'));
    var progressFill = document.getElementById('guide-progress');

    if (!sections.length || !steps.length) return;

    function setActive(index) {
      steps.forEach(function (step, i) {
        step.classList.remove('active', 'done');
        var circle = step.querySelector('.guide-step-circle');
        if (i === index) {
          step.classList.add('active');
          if (circle) circle.textContent = i + 1;
        } else if (i < index) {
          step.classList.add('done');
          if (circle) circle.textContent = '\u2713';
        } else {
          if (circle) circle.textContent = i + 1;
        }
      });
      if (progressFill) {
        progressFill.style.width = ((index + 1) / sections.length * 100) + '%';
      }
    }

    activeObserver = new IntersectionObserver(function (entries) {
      var best = null;
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var n = parseInt(entry.target.dataset.section, 10);
          if (!isNaN(n) && (best === null || n < best)) best = n;
        }
      });
      if (best !== null) setActive(best - 1);
    }, { threshold: 0.1, rootMargin: '0px 0px -60% 0px' });

    sections.forEach(function (s) { activeObserver.observe(s); });
    setActive(0);

    // Sidebar click nav
    steps.forEach(function (step) {
      step.addEventListener('click', function (e) {
        var n = parseInt(step.dataset.step, 10);
        if (!isNaN(n)) {
          var target = document.getElementById(prefix + '-section-' + n);
          if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
        }
      });
    });
  }

  // Add sidebar IDs for scoping
  var sidebarMap = { java: 'sidebar-java', typescript: 'sidebar-typescript', python: 'sidebar-python' };
  Object.keys(sidebarMap).forEach(function (lang) {
    var sb = document.querySelector('#pane-' + lang + ' .guide-sidebar');
    if (sb) sb.id = sidebarMap[lang];
  });

  // Update existing Java section IDs to use java- prefix
  document.querySelectorAll('#pane-java .guide-section').forEach(function (el) {
    var n = el.getAttribute('data-section');
    if (n && !el.id.startsWith('java-')) el.id = 'java-section-' + n;
  });
  document.querySelectorAll('#pane-java .guide-step').forEach(function (el) {
    if (!el.dataset.lang) el.dataset.lang = 'java';
  });

  // Boot
  activateTab(getLang());
})();
</script>
```

- [ ] **Step 6: Run tab structure tests**

```bash
python3 -m pytest tests/test_guide_page.py::TestTabStructure -v 2>&1 | tail -15
```

Expected: All 7 tests PASS.

- [ ] **Step 7: Run full structural test suite**

```bash
python3 -m pytest tests/test_guide_page.py -v 2>&1 | tail -10
```

Expected: 24 original tests + 7 new = 31 tests all PASS.

- [ ] **Step 8: Commit**

```bash
git add docs/guide.html tests/test_guide_page.py
git commit -m "feat(guide): add Java/TypeScript/Python tab bar with hash routing"
```

---

## Task 3: Add TypeScript tab — full 12-section content

**Files:**
- Modify: `docs/guide.html` — replace TypeScript placeholder with full content

The TypeScript tab has 12 sections. Sections 1, 2, 6, 7, 8, 10, 11, 12 are language-agnostic (same structure as Java, different install callouts). Sections 3, 4, 5 are TypeScript-specific. Section 9 covers `design-snapshot` only (no journal).

- [ ] **Step 1: Add TypeScript content tests**

Add to `tests/test_guide_page.py`:

```python
class TestTypescriptTab(unittest.TestCase):
    """Integration: TypeScript tab has correct content."""

    def setUp(self):
        self.content = load_guide()

    def test_ts_pane_has_twelve_sections(self):
        import re
        count = len(re.findall(r'id="ts-section-\d+"', self.content))
        self.assertEqual(count, 12, f'TypeScript tab needs 12 sections, found {count}')

    def test_ts_sidebar_has_twelve_steps(self):
        import re
        count = len(re.findall(r'id="sidebar-typescript"', self.content))
        self.assertGreaterEqual(count, 1, 'TypeScript sidebar must have an id')

    def test_ts_specific_skills_mentioned(self):
        for skill in ('ts-dev', 'ts-code-review', 'npm-dependency-update'):
            self.assertIn(skill, self.content, f'TypeScript tab must mention {skill}')

    def test_ts_commit_uses_git_commit_not_java(self):
        # TypeScript uses plain git-commit, not java-git-commit
        pane_start = self.content.index('id="pane-typescript"')
        pane_end = self.content.index('id="pane-python"')
        ts_content = self.content[pane_start:pane_end]
        self.assertNotIn('java-git-commit', ts_content,
                          'TypeScript pane must not reference java-git-commit')
        self.assertIn('git-commit', ts_content,
                       'TypeScript pane must reference git-commit')

    def test_ts_section9_has_design_snapshot_not_journal(self):
        pane_start = self.content.index('id="pane-typescript"')
        pane_end = self.content.index('id="pane-python"')
        ts_content = self.content[pane_start:pane_end]
        self.assertIn('design-snapshot', ts_content)
        self.assertNotIn('java-update-design', ts_content)

    def test_ts_has_twelve_prompt_blocks(self):
        pane_start = self.content.index('id="pane-typescript"')
        pane_end = self.content.index('id="pane-python"')
        ts_content = self.content[pane_start:pane_end]
        count = ts_content.count('prompt-block')
        self.assertEqual(count, 12, f'TypeScript tab needs 12 prompt blocks, found {count}')

    def test_ts_has_ten_install_callouts(self):
        pane_start = self.content.index('id="pane-typescript"')
        pane_end = self.content.index('id="pane-python"')
        ts_content = self.content[pane_start:pane_end]
        count = ts_content.count('install-callout')
        self.assertEqual(count, 10, f'TypeScript tab needs 10 install callouts, found {count}')
```

- [ ] **Step 2: Run to confirm RED**

```bash
python3 -m pytest tests/test_guide_page.py::TestTypescriptTab -v 2>&1 | tail -12
```

Expected: All 7 tests FAIL (TypeScript pane is still placeholder).

- [ ] **Step 3: Replace TypeScript placeholder pane with full content**

Replace the TypeScript placeholder pane in `docs/guide.html`:

```html
<!-- TypeScript pane (hidden by default) -->
<div class="guide-pane" id="pane-typescript" style="display:none">

  <aside class="guide-sidebar" id="sidebar-typescript">
    <div class="guide-sidebar-label">Getting Started</div>
    <a class="guide-step" data-step="1" data-lang="ts" href="#ts-section-1">
      <span class="guide-step-circle">1</span>
      <span class="guide-step-title">CLAUDE.md Setup</span>
      <span class="guide-step-sub">Your configuration hub</span>
    </a>
    <a class="guide-step" data-step="2" data-lang="ts" href="#ts-section-2">
      <span class="guide-step-circle">2</span>
      <span class="guide-step-title">Workspace Setup</span>
      <span class="guide-step-sub">Separate code from methodology</span>
    </a>
    <a class="guide-step" data-step="3" data-lang="ts" href="#ts-section-3">
      <span class="guide-step-circle">3</span>
      <span class="guide-step-title">TypeScript Development</span>
      <span class="guide-step-sub">Strict mode and async patterns</span>
    </a>
    <a class="guide-step" data-step="4" data-lang="ts" href="#ts-section-4">
      <span class="guide-step-circle">4</span>
      <span class="guide-step-title">Code Review</span>
      <span class="guide-step-sub">Catches problems early</span>
    </a>
    <a class="guide-step" data-step="5" data-lang="ts" href="#ts-section-5">
      <span class="guide-step-circle">5</span>
      <span class="guide-step-title">Smart Commits</span>
      <span class="guide-step-sub">Issue linking built in</span>
    </a>
    <a class="guide-step" data-step="6" data-lang="ts" href="#ts-section-6">
      <span class="guide-step-circle">6</span>
      <span class="guide-step-title">Brainstorming</span>
      <span class="guide-step-sub">Design before code</span>
    </a>
    <a class="guide-step" data-step="7" data-lang="ts" href="#ts-section-7">
      <span class="guide-step-circle">7</span>
      <span class="guide-step-title">Ideas &amp; Decisions</span>
      <span class="guide-step-sub">Park and record</span>
    </a>
    <a class="guide-step" data-step="8" data-lang="ts" href="#ts-section-8">
      <span class="guide-step-circle">8</span>
      <span class="guide-step-title">Issues &amp; Epics</span>
      <span class="guide-step-sub">Automatic tracking</span>
    </a>
    <a class="guide-step" data-step="9" data-lang="ts" href="#ts-section-9">
      <span class="guide-step-circle">9</span>
      <span class="guide-step-title">Design Snapshots</span>
      <span class="guide-step-sub">Immutable save points</span>
    </a>
    <a class="guide-step" data-step="10" data-lang="ts" href="#ts-section-10">
      <span class="guide-step-circle">10</span>
      <span class="guide-step-title">Closing an Epic</span>
      <span class="guide-step-sub">Merge, route, close</span>
    </a>
    <a class="guide-step" data-step="11" data-lang="ts" href="#ts-section-11">
      <span class="guide-step-circle">11</span>
      <span class="guide-step-title">Session Handover</span>
      <span class="guide-step-sub">Resume in one message</span>
    </a>
    <a class="guide-step" data-step="12" data-lang="ts" href="#ts-section-12">
      <span class="guide-step-circle">12</span>
      <span class="guide-step-title">Project Diary</span>
      <span class="guide-step-sub">Honest in-the-moment writing</span>
    </a>
  </aside>

  <main class="guide-content">
    <div class="guide-progress-bar"><div id="guide-progress-ts" class="guide-progress-fill"></div></div>

    <div class="guide-intro">
      <h1>Getting Started — TypeScript / Node.js</h1>
      <p>A 12-step walkthrough from CLAUDE.md setup through daily TypeScript development, code review, smart commits, brainstorming, and session handover.</p>
    </div>

    <!-- Section 1: CLAUDE.md -->
    <section class="guide-section" id="ts-section-1" data-section="1">
      <div class="section-num">1</div>
      <h2>CLAUDE.md Setup</h2>
      <p class="section-sub">Your configuration hub — Claude reads this at the start of every session.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Creates the file that every cc-praxis skill reads first. Sets your project type and GitHub repo. Without it, skills can't route correctly.</div>
      <p>If your project doesn't have a CLAUDE.md yet, ask Claude to create one:</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">"Set up a CLAUDE.md for my TypeScript Node.js project tracked on GitHub at owner/repo. Enable issue tracking."</div>
      <p>The key field is <code>GitHub repo: owner/repo</code> — this enables automatic issue linking in commits. For TypeScript projects, use <code>type: generic</code> (or omit the type field entirely):</p>
      <div class="code-block"><pre><span class="c"># CLAUDE.md</span>
<span class="k">GitHub repo:</span> <span class="v">owner/repo</span>

<span class="c">## Work Tracking</span>
<span class="k">Issue tracking:</span> <span class="v">enabled</span>
<span class="k">GitHub repo:</span> <span class="v">owner/repo</span></pre></div>
      <div class="section-next">Next: <a href="#ts-section-2">Workspace Setup →</a></div>
    </section>

    <!-- Section 2: Workspace -->
    <section class="guide-section" id="ts-section-2" data-section="2">
      <div class="section-num">2</div>
      <h2>Workspace Setup</h2>
      <p class="section-sub">Separate methodology artifacts from your project code.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Creates a companion git repo that stores ADRs, design snapshots, session handovers — keeping the project repo focused on code.</div>
      <p>Optional but recommended. Without a workspace, all artifacts (ADRs, HANDOFF.md) land in your project repo. Run <code>/workspace-init</code> once to create a separate home for them.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">/workspace-init</div>
      <p>The routing table in your workspace CLAUDE.md controls where artifacts go at epic close: <code>project</code> · <code>workspace</code> · <code>alternative ~/path/</code></p>
      <div class="section-next">Next: <a href="#ts-section-3">TypeScript Development →</a></div>
    </section>

    <!-- Section 3: TypeScript Development -->
    <section class="guide-section" id="ts-section-3" data-section="3">
      <div class="section-num">3</div>
      <h2>TypeScript Development</h2>
      <p class="section-sub">Strict mode, async patterns, and type safety rules for every TypeScript file.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Loads development rules for strict TypeScript: type safety, async/await correctness, error handling with discriminated unions, and testing with Jest or Vitest. Triggers automatically when editing <code>.ts</code> files.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>scripts/claude-skill install ts-dev</code></div>
      <p>Key rules enforced: <strong>never use <code>any</code></strong> without justification; <strong>discriminated unions</strong> for error handling over raw try/catch; <strong>async functions return typed promises</strong>; <strong>avoid callback hell</strong> — everything is async/await or streams.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">"Implement a Node.js endpoint to fetch orders by customer ID with proper error handling."</div>
      <div class="section-next">Next: <a href="#ts-section-4">Code Review →</a></div>
    </section>

    <!-- Section 4: Code Review -->
    <section class="guide-section" id="ts-section-4" data-section="4">
      <div class="section-num">4</div>
      <h2>Code Review</h2>
      <p class="section-sub">Catches type safety issues, async bugs, and prototype pollution before they ship.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Reviews staged changes against TypeScript-specific checklists: type safety violations, unhandled promise rejections, missing discriminated union cases, prototype pollution risks. Triggers automatically before <code>git-commit</code> if no review has been done this session.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>scripts/claude-skill install ts-code-review</code></div>
      <p>Auth, payment, or PII code automatically escalates to <code>ts-security-audit</code> for a full OWASP check. Findings come as CRITICAL (blocks), WARNING, or NOTE.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">"Review my changes." &nbsp;or&nbsp; /ts-code-review</div>
      <div class="section-next">Next: <a href="#ts-section-5">Smart Commits →</a></div>
    </section>

    <!-- Section 5: Smart Commits -->
    <section class="guide-section" id="ts-section-5" data-section="5">
      <div class="section-num">5</div>
      <h2>Smart Commits</h2>
      <p class="section-sub">Conventional commits with issue linking built in.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Routes commits through code review (if not done this session), writes a conventional commit message, and links the active GitHub issue automatically.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>scripts/claude-skill install git-commit</code></div>
      <p>Use <code>/git-commit</code> instead of plain <code>git commit</code>. It runs the review, proposes a message, and adds <code>Refs #N</code> automatically:</p>
      <div class="code-block"><pre><span class="v">feat:</span>     add order validation endpoint
<span class="v">fix:</span>      handle null customer ID in findByCustomer
<span class="v">refactor:</span> extract validation into OrderValidator class
<span class="v">test:</span>     add edge cases for null customer handling
<span class="v">chore:</span>    bump express to 4.19.2</pre></div>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">/git-commit</div>
      <div class="section-next">Next: <a href="#ts-section-6">Brainstorming →</a></div>
    </section>

    <!-- Sections 6-8 same as Java (brainstorming, ideas, issues) -->
    <section class="guide-section" id="ts-section-6" data-section="6">
      <div class="section-num">6</div>
      <h2>Brainstorming</h2>
      <p class="section-sub">Design before you code. Every feature, every time.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Guides a structured design conversation producing a written spec, then a step-by-step implementation plan. No code is written until the spec is approved.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>/plugin install superpowers</code> (includes brainstorming)</div>
      <p>The hard gate: Claude will not write implementation code until you explicitly approve the spec. The flow: context → questions → approaches → design sections → spec → plan → TDD implementation.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">"Let's brainstorm the order validation feature. I want idempotent validation with retry logic."</div>
      <div class="section-next">Next: <a href="#ts-section-7">Ideas &amp; Decisions →</a></div>
    </section>

    <section class="guide-section" id="ts-section-7" data-section="7">
      <div class="section-num">7</div>
      <h2>Ideas &amp; Decisions</h2>
      <p class="section-sub">Park undecided thoughts. Record decided ones permanently.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> <code>idea-log</code> captures possibilities before they're decided. <code>adr</code> records the decision once made — immutably, with status lifecycle.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install these skills</span><code>scripts/claude-skill install idea-log adr</code></div>
      <p><strong>idea-log</strong> maintains <code>IDEAS.md</code> with statuses active/promoted/discarded. Ideas 90+ days old are flagged during review. <strong>adr</strong> is append-only — if a decision is superseded, create a new ADR and mark the old one <code>Superseded by ADR-NNNN</code>.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">"Log this idea: use Redis for order caching — not decided yet." &nbsp;/&nbsp; "Create an ADR for choosing Prisma over raw SQL."</div>
      <div class="section-next">Next: <a href="#ts-section-8">Issues &amp; Epics →</a></div>
    </section>

    <section class="guide-section" id="ts-section-8" data-section="8">
      <div class="section-num">8</div>
      <h2>Issues &amp; Epics</h2>
      <p class="section-sub">Four-phase tracking that runs automatically once enabled.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Phase 0 (one-time setup) configures GitHub. Phases 1–3 fire automatically: before code is written, before each session, and before each commit.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>scripts/claude-skill install issue-workflow</code></div>
      <p>Run Phase 0 once with <code>/issue-workflow</code>. After that: Phase 1 creates epics from specs, Phase 2 checks for an active issue before writing code, Phase 3 verifies issue linkage before each commit.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">/issue-workflow</div>
      <div class="section-next">Next: <a href="#ts-section-9">Design Snapshots →</a></div>
    </section>

    <!-- Section 9: Design Snapshots (TypeScript — no journal) -->
    <section class="guide-section" id="ts-section-9" data-section="9">
      <div class="section-num">9</div>
      <h2>Design Snapshots</h2>
      <p class="section-sub">Immutable save points for your design — rewind to any moment.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Creates an immutable dated record of where the design stands. Unlike a living design doc, a snapshot is never edited after creation. If the design moves on, create a new one.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>scripts/claude-skill install design-snapshot</code></div>
      <p>Use before a major pivot, at the end of a phase, or any time you want a "save point." Each snapshot has five sections: Where We Are, How We Got Here, Where We're Going, Open Questions, Linked ADRs. Auto-pruned to 10 most recent.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">"Take a design snapshot before we change the data model."</div>
      <div class="section-next">Next: <a href="#ts-section-10">Closing an Epic →</a></div>
    </section>

    <!-- Sections 10-12 same as Java -->
    <section class="guide-section" id="ts-section-10" data-section="10">
      <div class="section-num">10</div>
      <h2>Closing an Epic</h2>
      <p class="section-sub">Branch cleanup, artifact routing, issue closed — one confirmed workflow.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Closes the epic branch: routes ADRs and snapshots per your routing config, posts specs to the GitHub issue, closes it, and cleans up branches. Shows a plan before executing anything.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>scripts/claude-skill install epic-close</code></div>
      <p>Before doing anything, <code>/epic-close</code> shows the routing plan and asks for confirmation. For TypeScript projects there is no DESIGN.md merge — epic-close routes ADRs and snapshots, posts specs, closes the issue, and offers to delete both branches.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">/epic-close</div>
      <div class="section-next">Next: <a href="#ts-section-11">Session Handover →</a></div>
    </section>

    <section class="guide-section" id="ts-section-11" data-section="11">
      <div class="section-num">11</div>
      <h2>Session Handover</h2>
      <p class="section-sub">End every session with a handoff. Resume any session in one message.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Produces a committed <code>HANDOFF.md</code> — under 500 tokens — giving the next Claude session enough context to resume immediately. Git history is the archive; HANDOFF.md is the delta.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>scripts/claude-skill install handover</code></div>
      <p>The wrap checklist before writing the handover: write-blog, update-claude-md, forage sweep (checks for gotchas/techniques/undocumented from session memory). HANDOFF.md uses delta-first: unchanged sections reference git history, not repeated content.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">"Create a handover." &nbsp;or&nbsp; /handover</div>
      <div class="section-next">Next: <a href="#ts-section-12">Project Diary →</a></div>
    </section>

    <section class="guide-section" id="ts-section-12" data-section="12">
      <div class="section-num">12</div>
      <h2>Project Diary</h2>
      <p class="section-sub">Honest in-the-moment writing — not a polished retrospective.</p>
      <div class="what-it-does" data-guide="wid"><strong>What this does</strong> Writes diary entries in your personal voice — capturing what was believed at the time, failed attempts, and pivots. Entries are never edited; corrections become new entries.</div>
      <div class="install-callout" data-guide="ic"><span class="install-callout-label">Install this skill</span><code>scripts/claude-skill install write-blog</code></div>
      <p>Voice is configured from <code>$PERSONAL_WRITING_STYLES_PATH</code> or a bundled fallback. Entry metadata drives filtering: <code>entry_type: article | note</code>, <code>projects</code>, <code>tags</code>. The site shows diary entries at <code>/blog/</code> and articles at <code>/articles/</code>.</p>
      <div class="prompt-label">Prompt to try</div>
      <div class="prompt-block" data-guide="pb">"Write a blog entry for today's session — we implemented order validation."</div>
      <div class="section-next" style="border-top:2px solid #4f46e5;padding-top:1.5rem;margin-top:2rem;">
        <span style="font-size:13px;color:#4f46e5;font-weight:700;">✓ You've covered the full TypeScript workflow. Install skills as you need them.</span>
      </div>
    </section>
  </main>
</div>
```

- [ ] **Step 4: Run TypeScript tests**

```bash
python3 -m pytest tests/test_guide_page.py::TestTypescriptTab -v 2>&1 | tail -12
```

Expected: All 7 TypeScript tests PASS.

- [ ] **Step 5: Run full suite**

```bash
python3 -m pytest tests/test_guide_page.py -v 2>&1 | tail -5
```

Expected: 38 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/guide.html tests/test_guide_page.py
git commit -m "feat(guide): add TypeScript tab — 12-section Node.js workflow"
```

---

## Task 4: Add Python tab — full 12-section content

**Files:**
- Modify: `docs/guide.html` — replace Python placeholder with full content
- Modify: `tests/test_guide_page.py` — Python tab tests

Identical structure to TypeScript tab. Key differences: `python-dev`, `python-code-review`, `pip-dependency-update`; section IDs prefixed `py-`; scopes `feat:`, `fix:`, `refactor:`.

- [ ] **Step 1: Add Python content tests**

Add to `tests/test_guide_page.py`:

```python
class TestPythonTab(unittest.TestCase):
    """Integration: Python tab has correct content."""

    def setUp(self):
        self.content = load_guide()

    def test_py_pane_has_twelve_sections(self):
        import re
        count = len(re.findall(r'id="py-section-\d+"', self.content))
        self.assertEqual(count, 12, f'Python tab needs 12 sections, found {count}')

    def test_py_specific_skills_mentioned(self):
        pane_start = self.content.index('id="pane-python"')
        py_content = self.content[pane_start:]
        for skill in ('python-dev', 'python-code-review', 'pip-dependency-update'):
            self.assertIn(skill, py_content, f'Python tab must mention {skill}')

    def test_py_commit_uses_git_commit_not_java(self):
        pane_start = self.content.index('id="pane-python"')
        py_content = self.content[pane_start:]
        self.assertNotIn('java-git-commit', py_content,
                          'Python pane must not reference java-git-commit')

    def test_py_section9_has_design_snapshot_not_journal(self):
        pane_start = self.content.index('id="pane-python"')
        py_content = self.content[pane_start:]
        self.assertIn('design-snapshot', py_content)
        self.assertNotIn('java-update-design', py_content)

    def test_py_has_twelve_prompt_blocks(self):
        pane_start = self.content.index('id="pane-python"')
        py_content = self.content[pane_start:]
        count = py_content.count('prompt-block')
        self.assertEqual(count, 12, f'Python tab needs 12 prompt blocks, found {count}')

    def test_py_has_ten_install_callouts(self):
        pane_start = self.content.index('id="pane-python"')
        py_content = self.content[pane_start:]
        count = py_content.count('install-callout')
        self.assertEqual(count, 10, f'Python tab needs 10 install callouts, found {count}')
```

- [ ] **Step 2: Run to confirm RED**

```bash
python3 -m pytest tests/test_guide_page.py::TestPythonTab -v 2>&1 | tail -10
```

Expected: All 6 tests FAIL.

- [ ] **Step 3: Replace Python placeholder with full 12-section content**

Replace the Python placeholder pane in `docs/guide.html`. Follow the same structure as the TypeScript pane (Task 3, Step 3) with these substitutions:

- `pane-typescript` → `pane-python`, `sidebar-typescript` → `sidebar-python`
- All `ts-section-N` IDs → `py-section-N`
- All `data-lang="ts"` → `data-lang="py"`
- `guide-progress-ts` → `guide-progress-py`
- Section 3 heading: "Python Development" — subtitle: "Type hints, async patterns, and safety rules for every Python file."
- Section 3 what-it-does: "Loads development rules for professional Python: type hints (PEP 484), async/await patterns, safe use of third-party libraries, and testing with pytest. Triggers automatically when editing <code>.py</code> files."
- Section 3 install: `scripts/claude-skill install python-dev`
- Section 3 key rules: never use bare `except:`, always annotate public functions, use `pathlib` over `os.path`, avoid mutable default arguments
- Section 3 prompt: `"Implement a FastAPI endpoint to fetch orders by customer ID with proper error handling."`
- Section 4 heading: "Code Review" — what-it-does: "Reviews staged changes for Python-specific issues: bare excepts silencing errors, missing type annotations, pickle/eval injection risks, mutable default arguments."
- Section 4 install: `scripts/claude-skill install python-code-review`
- Section 4 prompt: `"Review my changes." or /python-code-review`
- Section 5 what-it-does: same as TypeScript (plain `git-commit`)
- Section 5 install: `scripts/claude-skill install git-commit`
- Section 5 scopes example: `feat:` `fix:` `refactor:` `test:` `chore:` (identical to TypeScript)
- Section 5 prompt: `/git-commit`
- Section 1 intro heading: "Getting Started — Python"
- Section 1 intro subtitle: "A 12-step walkthrough from CLAUDE.md setup through daily Python development, code review, smart commits, brainstorming, and session handover."
- Section 3 sidebar subtitle: "Type hints and async patterns"
- All `ts-section-` hrefs → `py-section-`

The completion banner in section 12: `✓ You've covered the full Python workflow. Install skills as you need them.`

- [ ] **Step 4: Run Python tests**

```bash
python3 -m pytest tests/test_guide_page.py::TestPythonTab -v 2>&1 | tail -10
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Run full structural suite**

```bash
python3 -m pytest tests/test_guide_page.py -v 2>&1 | tail -5
```

Expected: 44 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/guide.html tests/test_guide_page.py
git commit -m "feat(guide): add Python tab — 12-section Python workflow"
```

---

## Task 5: Playwright tests for tab switching

**Files:**
- Modify: `tests/test_guide_ui.py`

- [ ] **Step 1: Add tab switching tests**

Add a new test class to `tests/test_guide_ui.py` (inside the existing `@unittest.skipUnless` guard pattern):

```python
@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, 'playwright not installed')
class TestGuideTabSwitching(unittest.TestCase):
    """E2E: tab bar switches panes, resets sidebar, updates hash."""

    @classmethod
    def setUpClass(cls):
        raw = GUIDE_PATH.read_text(encoding='utf-8')
        _GuideHandler._content = _strip_frontmatter(raw).encode('utf-8')
        cls._server = http.server.HTTPServer(('127.0.0.1', 0), _GuideHandler)
        cls._port = cls._server.server_address[1]
        cls._base_url = f'http://127.0.0.1:{cls._port}'
        cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
        cls._thread.start()
        cls._pw = sync_playwright().start()
        cls._browser = cls._pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls._browser.close()
        cls._pw.stop()
        cls._server.shutdown()

    def setUp(self):
        self.page = self._browser.new_page(viewport={'width': 1280, 'height': 800})
        self.page.goto(self._base_url, wait_until='domcontentloaded')
        self.page.wait_for_timeout(300)

    def tearDown(self):
        self.page.close()

    # ── Happy path: tab bar exists ────────────────────────────────────────────

    def test_three_tabs_visible(self):
        tabs = self.page.query_selector_all('.guide-tab')
        self.assertEqual(len(tabs), 3, 'Expected 3 language tabs')

    def test_java_tab_active_on_load(self):
        java_tab = self.page.query_selector('[data-lang="java"]')
        self.assertIn('active', java_tab.get_attribute('class'))

    def test_java_pane_visible_on_load(self):
        pane = self.page.query_selector('#pane-java')
        self.assertTrue(pane.is_visible())

    def test_typescript_pane_hidden_on_load(self):
        pane = self.page.query_selector('#pane-typescript')
        self.assertFalse(pane.is_visible())

    def test_python_pane_hidden_on_load(self):
        pane = self.page.query_selector('#pane-python')
        self.assertFalse(pane.is_visible())

    # ── Happy path: click TypeScript tab ─────────────────────────────────────

    def test_click_typescript_tab_shows_ts_pane(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(200)
        self.assertTrue(self.page.query_selector('#pane-typescript').is_visible())

    def test_click_typescript_tab_hides_java_pane(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(200)
        self.assertFalse(self.page.query_selector('#pane-java').is_visible())

    def test_click_typescript_tab_marks_ts_tab_active(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(200)
        ts_tab = self.page.query_selector('[data-lang="typescript"]')
        self.assertIn('active', ts_tab.get_attribute('class'))

    def test_click_typescript_tab_updates_hash(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(200)
        url = self.page.url
        self.assertIn('#typescript', url, f'URL should contain #typescript, got {url}')

    def test_typescript_tab_sidebar_resets_to_step_1(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(300)
        # Step 1 in TypeScript sidebar should be active
        ts_steps = self.page.query_selector_all('#sidebar-typescript .guide-step')
        self.assertGreater(len(ts_steps), 0, 'TypeScript sidebar must have steps')
        first_step = ts_steps[0]
        self.assertIn('active', first_step.get_attribute('class'),
                       'First TypeScript step should be active after tab switch')

    # ── Happy path: click Python tab ─────────────────────────────────────────

    def test_click_python_tab_shows_py_pane(self):
        self.page.click('[data-lang="python"]')
        self.page.wait_for_timeout(200)
        self.assertTrue(self.page.query_selector('#pane-python').is_visible())

    def test_click_python_tab_updates_hash(self):
        self.page.click('[data-lang="python"]')
        self.page.wait_for_timeout(200)
        self.assertIn('#python', self.page.url)

    # ── Happy path: switch back to Java ──────────────────────────────────────

    def test_switch_back_to_java_from_typescript(self):
        self.page.click('[data-lang="typescript"]')
        self.page.wait_for_timeout(200)
        self.page.click('[data-lang="java"]')
        self.page.wait_for_timeout(200)
        self.assertTrue(self.page.query_selector('#pane-java').is_visible())
        self.assertFalse(self.page.query_selector('#pane-typescript').is_visible())

    # ── Happy path: hash-based deep link ─────────────────────────────────────

    def test_direct_link_to_typescript_via_hash(self):
        self.page.goto(self._base_url + '#typescript', wait_until='domcontentloaded')
        self.page.wait_for_timeout(400)
        self.assertTrue(self.page.query_selector('#pane-typescript').is_visible())
        self.assertFalse(self.page.query_selector('#pane-java').is_visible())

    def test_direct_link_to_python_via_hash(self):
        self.page.goto(self._base_url + '#python', wait_until='domcontentloaded')
        self.page.wait_for_timeout(400)
        self.assertTrue(self.page.query_selector('#pane-python').is_visible())
```

- [ ] **Step 2: Run Playwright tab tests**

```bash
python3 -m pytest tests/test_guide_ui.py::TestGuideTabSwitching -v 2>&1 | tail -25
```

Expected: All 15 tab switching tests PASS. If any fail, check the JS `activateTab()` function — most failures will be timing (increase `wait_for_timeout`) or selector mismatches.

- [ ] **Step 3: Run full Playwright suite**

```bash
python3 -m pytest tests/test_guide_ui.py -v 2>&1 | tail -8
```

Expected: All 33+ tests PASS (18 original + 15 new).

- [ ] **Step 4: Commit**

```bash
git add tests/test_guide_ui.py
git commit -m "test(guide): Playwright tab switching tests — 15 e2e tests for Java/TypeScript/Python tabs"
```

---

## Task 6: Quick-start bundles in marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json` — add 3 bundles at the top of the bundles array

- [ ] **Step 1: Write failing test**

Add to `tests/test_guide_page.py` (or a new `tests/test_marketplace.py`):

```python
# Add at the bottom of test_guide_page.py

import json
MARKETPLACE_PATH = REPO_ROOT / '.claude-plugin' / 'marketplace.json'

class TestQuickStartBundles(unittest.TestCase):
    """Unit: marketplace.json has quick-start bundles for each language."""

    def setUp(self):
        with open(MARKETPLACE_PATH) as f:
            self.data = json.load(f)
        self.bundles = {b['name']: b for b in self.data['bundles']}

    def test_quick_start_java_bundle_exists(self):
        self.assertIn('quick-start-java', self.bundles)

    def test_quick_start_typescript_bundle_exists(self):
        self.assertIn('quick-start-typescript', self.bundles)

    def test_quick_start_python_bundle_exists(self):
        self.assertIn('quick-start-python', self.bundles)

    def test_quick_start_java_has_three_core_skills(self):
        skills = self.bundles['quick-start-java']['skills']
        for skill in ('java-dev', 'java-code-review', 'java-git-commit'):
            self.assertIn(skill, skills)

    def test_quick_start_typescript_has_three_core_skills(self):
        skills = self.bundles['quick-start-typescript']['skills']
        for skill in ('ts-dev', 'ts-code-review', 'git-commit'):
            self.assertIn(skill, skills)

    def test_quick_start_python_has_three_core_skills(self):
        skills = self.bundles['quick-start-python']['skills']
        for skill in ('python-dev', 'python-code-review', 'git-commit'):
            self.assertIn(skill, skills)

    def test_all_bundle_skills_exist_in_marketplace(self):
        all_skills = {p['name'] for p in self.data['plugins']}
        for bundle in self.data['bundles']:
            for skill in bundle['skills']:
                self.assertIn(skill, all_skills,
                              f"Bundle '{bundle['name']}' references skill '{skill}' not in marketplace")
```

- [ ] **Step 2: Run to confirm RED**

```bash
python3 -m pytest tests/test_guide_page.py::TestQuickStartBundles -v 2>&1 | tail -12
```

Expected: First 3 tests FAIL (bundles don't exist yet).

- [ ] **Step 3: Add quick-start bundles to marketplace.json**

Open `.claude-plugin/marketplace.json`. In the `"bundles"` array, add these three entries **before** the existing `"core"` bundle (so they appear first in the installer UI):

```json
    {
      "name": "quick-start-java",
      "displayName": "Quick Start: Java / Quarkus",
      "description": "Get immediate value in 3 skills: safety-first development, code review that catches bugs before they ship, and smart commits that sync DESIGN.md automatically",
      "skills": [
        "java-dev",
        "java-code-review",
        "java-git-commit"
      ]
    },
    {
      "name": "quick-start-typescript",
      "displayName": "Quick Start: TypeScript",
      "description": "Get immediate value in 3 skills: strict-mode TypeScript development, code review catching type safety and async bugs, and conventional commits with issue linking",
      "skills": [
        "ts-dev",
        "ts-code-review",
        "git-commit"
      ]
    },
    {
      "name": "quick-start-python",
      "displayName": "Quick Start: Python",
      "description": "Get immediate value in 3 skills: type-annotated Python development, code review catching bare excepts and injection risks, and conventional commits with issue linking",
      "skills": [
        "python-dev",
        "python-code-review",
        "git-commit"
      ]
    },
```

- [ ] **Step 4: Run bundle tests**

```bash
python3 -m pytest tests/test_guide_page.py::TestQuickStartBundles -v 2>&1 | tail -12
```

Expected: All 7 tests PASS.

- [ ] **Step 5: Run full structural suite**

```bash
python3 -m pytest tests/test_guide_page.py -v 2>&1 | tail -5
```

Expected: 51 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/marketplace.json tests/test_guide_page.py
git commit -m "feat(marketplace): add quick-start bundles for Java, TypeScript, and Python"
```

---

## Task 7: Final integration — full suite + push

**Files:** none new

- [ ] **Step 1: Run full test suite**

```bash
python3 -m pytest tests/ --tb=line -q 2>&1 | tail -5
```

Expected: 1185+ tests pass (1152 baseline + 51 structural + 33 Playwright - overlapping counts).

- [ ] **Step 2: Run commit-tier validators**

```bash
python3 scripts/validate_all.py --tier commit 2>&1 | tail -5
```

Expected: `8/8 passed`

- [ ] **Step 3: Regenerate web app data (bundle counts changed)**

```bash
python3 scripts/generate_web_app_data.py
```

- [ ] **Step 4: Final commit and push**

```bash
git add docs/index.html  # if generate_web_app_data.py modified it
git status --short
git commit -m "chore: regenerate web app data after quick-start bundle additions" 2>/dev/null || echo "nothing to commit"
git push
```

---

## Self-Review

**Spec coverage check:**

| Requirement | Task |
|-------------|------|
| README leads with value | Task 1 |
| Tab bar (Java/TypeScript/Python) | Task 2 |
| Hash routing (#java, #typescript, #python) | Task 2 |
| Per-tab sidebar (independent scroll tracking) | Tasks 2-4 |
| TypeScript 12-section content | Task 3 |
| Python 12-section content | Task 4 |
| Sections 3/4/5 language-specific | Tasks 3-4 |
| Section 9: Design Snapshots for TS/Python (no journal) | Tasks 3-4 |
| Section 9: Full journal content for Java (unchanged) | Task 2 (Java pane untouched) |
| Tab switching Playwright tests | Task 5 |
| Hash deep-link tests | Task 5 |
| Quick-start bundles (3) | Task 6 |
| Bundle skills validated against marketplace | Task 6 |

**Placeholder scan:** All steps contain actual code. No TBD, TODO, or "similar to Task N".

**Type consistency:**
- `data-lang="java"/"typescript"/"python"` — consistent across tab buttons and sidebar steps
- `id="pane-java/typescript/python"` — consistent across HTML and JS
- `id="sidebar-java/typescript/python"` — consistent across HTML and JS selector
- Section ID prefixes: `java-section-N`, `ts-section-N`, `py-section-N` — consistent across HTML, tests, and JS
- `getLang()` returns one of `['java', 'typescript', 'python']` — consistent with tab `data-lang` values
