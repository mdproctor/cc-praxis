# Claude Desktop CLI — Design

> Current implemented architecture. For product vision and technology rationale, see `VISION.md`.

---

## Module Structure

```
claude-desktop/
├── pom.xml              ← parent Maven POM
├── mac-ui-bridge/       ← Objective-C: MyMacUI.dylib
│   ├── MyMacUI.h
│   ├── MyMacUI.m
│   └── Makefile
├── app-core/            ← Java: PTY, session, interaction (no UI dependency)
└── app-macos/           ← Java: Panama bindings, Quarkus wiring, .app packaging
```

**Rule:** `app-core` has zero dependency on Panama FFM, AppKit, or the dylib. All public interfaces are plain Java. `app-macos` depends on `app-core` only.

---

## Technology Stack

| Concern | Technology |
|---------|-----------|
| Native macOS UI | AppKit via Objective-C bridge (MyMacUI.dylib) |
| Java ↔ native bridge | Panama FFM API + jextract |
| Terminal pane (dev) | NSTextView (WKWebView fails without .app bundle; replaced in Plan 5b) |
| Terminal pane (prod) | WKWebView + xterm.js (requires .app bundle — Plan 5b) |
| Input pane | NSTextField (single-line native text field) |
| ANSI stripping | AnsiStripper — strips VT100 codes before NSTextView display (dev only) |
| PTY management | Panama FFM → POSIX libc |
| Java runtime | Quarkus Native (GraalVM/Mandrel) |
| Packaging | Planned — macOS .app bundle (Plan 6, not yet built) |

---

## AppKit Bridge Primitives (mac-ui-bridge)

A minimal, tailored bridge — not a generic AppKit wrapper.

| Primitive | AppKit control | Purpose |
|-----------|---------------|---------|
| Main window | NSWindow | App shell |
| Output pane | NSTextView in NSScrollView | Terminal output (dev mode) |
| Input pane | NSTextField | Single-line native text input |
| Stop button | NSButton | Overlaid on input pane; fires StopClickedCallback on click |
| Passive mode | `myui_set_passive_mode(int)` | Disables input field; shows/hides Stop button |
| JS evaluation | `myui_evaluate_javascript()` | No-op placeholder; becomes active in Plan 5b |
| Callbacks | Panama upcalls | Window close, text submit, Stop button click |

---

## C ABI (mac-ui-bridge/include/MyMacUI.h)

| Function | Signature | Purpose |
|----------|-----------|---------|
| `myui_start` | `(title, w, h, html, onClosed, onTextSubmitted, onStop)` | 7-param entry point; blocks until app terminates |
| `myui_append_output` | `(const char*)` | Thread-safe; uses `performSelectorOnMainThread:` |
| `myui_set_passive_mode` | `(int passive)` | Thread-safe; disables/enables input + Stop button |
| `myui_evaluate_javascript` | `(const char*)` | No-op placeholder for Plan 5b |

**Callbacks:**
- `WindowClosedCallback` — void(*)(void) — window close
- `TextSubmittedCallback` — void(*)(const char*) — Enter pressed
- `StopClickedCallback` — void(*)(void) — Stop button clicked

---

## app-core Components

| Class | Purpose |
|-------|---------|
| `PosixLibrary` | 17+ POSIX function handles via Panama FFM downcalls |
| `PtyProcess` | PTY lifecycle: open/spawn/read/write/resize/sendSigInt/close |
| `ClaudeLocator` | Resolves `claude` binary via `/bin/zsh -l -c 'which claude'` |
| `AnsiStripper` | Strips VT100 escape sequences for NSTextView display (dev only) |
| `ClaudeState` | Enum: `FREE_TEXT`, `PASSIVE` |
| `InteractionDetector` | Timer-based mode transitions: PTY output → PASSIVE; 800ms quiet → FREE_TEXT |

**PTY POSIX calls:**

| Call | Purpose |
|------|---------|
| `posix_openpt` | Open PTY master |
| `grantpt` / `unlockpt` | Grant and unlock slave |
| `ptsname` | Get slave device path |
| `tcgetattr` / `tcsetattr` | Clear ECHO flag on master fd (prevents double output) |
| `posix_spawn` | Launch `claude` with slave as stdin/stdout/stderr |
| `ioctl(TIOCSWINSZ)` | Forward window resize to PTY |
| `read` / `write` | Byte I/O on master fd |
| `kill(SIGINT)` | Send Ctrl+C to claude subprocess (Stop button) |

---

## Data Flow

```
PTY master fd
    │ raw bytes
    ▼
PtyProcess reader thread (app-core)
    ├──→ AnsiStripper → MacUIBridge.appendOutput() → NSTextView (dev)
    └──→ InteractionDetector → ClaudeState → MacUIBridge.setPassiveMode()

NSTextField (Enter)
    │ text
    ▼
Panama upcall → Main.java → PtyProcess.write()

NSButton (Stop)
    │
    ▼
StopClickedCallback → PtyProcess.sendSigInt() + InteractionDetector.forceIdle()
```

---

## Interaction Modes

| Mode | Input surface | Status |
|------|--------------|--------|
| FREE_TEXT | NSTextField (enabled) | ✅ Built |
| PASSIVE | NSTextField (disabled) + Stop button | ✅ Built |
| SLASH_COMMAND | NSTextField + suggestion overlay | Planned |
| LIST_SELECTION | List view | Planned |
| FREE_TEXT_ANSWER | NSTextField with context label | Planned |
| CONFIRMATION | Yes/No control | Planned |
| PASSTHROUGH | Full terminal focus | Planned |

---

## Open Questions (v1)

1. **PTY bytes → xterm.js encoding** — xterm.js `term.write()` accepts UTF-8 strings or `Uint8Array`. Define the chunking and encoding contract between the Java read loop and WKWebView JS evaluation. (Active when Plan 5b is built.)
2. **Slash command overlay** — NSTextView has no overlay buffer. Evaluate transparent NSView layered over the split pane vs. popup anchored in NSSplitView. Deferred.

*Resolved:* posix_spawn + controlling terminal (works correctly), upcall thread model (`performSelectorOnMainThread:` throughout), claude binary resolution (ClaudeLocator via login shell).
