# Building a Native macOS Claude Code Client: An Architecture Diary

**Date:** 2026-04-04
**Type:** day-zero

---

## What I'm building: a smarter interface for Claude Code

Claude Code is a powerful CLI tool, but it runs in a terminal. I wanted something better: a macOS desktop application that wraps Claude Code with a smarter input/output experience.

The idea is a split-pane window. The top pane is a full terminal emulator showing Claude's output, exactly as it appears in the CLI. The bottom pane is where it gets interesting: a native text input that watches the terminal output and upgrades itself to match what Claude is presenting. When Claude shows a list of choices, the input becomes a list picker. When it asks yes/no, it becomes a confirmation widget. Type '/' and it becomes a slash command browser. At any point, a keyboard shortcut drops back to raw terminal mode if anything goes wrong.

Simple idea. Surprisingly interesting architecture.

---

## The Starting Vision: TamboUI

Before writing a line of code, I already had a clear picture of where I wanted to end up.

The problem with wrapping a CLI in a desktop app is that a terminal emulator is a character grid. Everything Claude produces — responses, tool call results, file edits, thinking blocks — gets flattened into rows and columns of ANSI-coloured text. That's a ceiling. You can't make results expandable, show diffs as side-by-side comparisons, or add per-message actions. The text is already rendered; there's nothing left to work with.

The real goal was **direct API mode**: talk to the Anthropic API directly, receive structured events, and render each one as a rich widget. Clickable tool call panels. Streaming code blocks with syntax highlighting. Collapsible thinking sections. The kind of output claude.ai gives you, but in a native desktop app.

My intended renderer for this was **TamboUI** — a Java widget framework with a diff-based repaint engine, designed exactly for building rich conversation UIs from structured streaming events. The vision was a `ConversationWidget` composed of `MessageWidget` instances, each containing `TextWidget`, `CodeBlockWidget`, `ToolCallWidget` and so on.

This shaped the core architectural decision from the start: a clean `OutputRenderer` interface so that the renderer is swappable without touching anything else:

```java
interface OutputRenderer {
    void accept(SessionEvent event);
    void clear();
}
```

In v1, `OutputRenderer` would be backed by a terminal emulator. Eventually, it would be backed by TamboUI. `MainWindow` would never know the difference.

---

## The Pragmatic v1: JediTerm + JavaFX

With TamboUI as the destination, I needed a practical starting point.

Direct API mode requires building a full widget rendering pipeline. That's not v1 work. For v1, I just needed something that renders Claude Code's output faithfully — and JediTerm (JetBrains' production-grade terminal emulator, the same one IntelliJ uses) does exactly that, with zero reimplementation of Claude Code's rendering. Pair it with pty4j for PTY subprocess management, JavaFX for the window and input pane, GraalVM + Gluon Client for native image packaging, and you have a working app.

The architecture was clean. The `OutputRenderer` interface meant the TamboUI swap later would be a one-class change. I felt good about it.

So I started working through the open questions.

---

## Working Through the Architecture — and Finding the Real Problem

Working through this with Claude, we examined five unresolved architectural questions:

1. **SwingNode vs TerminalFX** — JediTerm is a Swing component. Embedding it in JavaFX requires SwingNode. The risk: Retina rendering can be blurry (Swing and JavaFX have different HiDPI scaling pipelines), and focus management between the two toolkits is fragile. The vision document itself called this "the biggest v1 risk."
2. **`claude` binary resolution** — macOS `.app` bundles don't inherit shell PATH; how to find the binary at runtime.
3. **GraalVM + JavaFX build toolchain** — validate the Gluon Client native image build early; JavaFX reflection config requirements can surface late.
4. **PTY resize events** — straightforward: wire `SIGWINCH` from JediTerm's resize callback to pty4j. No real decision needed.
5. **Slash command overlay** — JediTerm has no overlay buffer; deferred to a later phase.

The SwingNode question kept nagging at me. Yes, the `OutputRenderer` interface would isolate the risk — I could swap in a TerminalFX renderer if SwingNode proved unusable. But I was designing around a problem rather than solving it.

And then the real question surfaced: **why am I accepting a non-native UI at all?**

---

## Wanting Native — and Hitting Constraints Fast

I started thinking about this more seriously. JavaFX renders its own widgets. It doesn't use AppKit. The text input isn't NSTextView. The scroll bars aren't native. Spell-check doesn't work. Users notice these things even if they can't say why.

I wanted native macOS controls. We explored what that actually meant.

**Swift + AppKit** was the ideal answer. SwiftTerm (a pure Swift terminal emulator) for the top pane, NSTextView for the input. Genuinely native in every sense. The problem: I can only code in Java. Swift is immediately off the table.

**JavaFX + WebView + xterm.js** was an intermediate option. Keep JavaFX as the window shell, but replace JediTerm-in-SwingNode with a JavaFX `WebView` hosting xterm.js. JavaFX's `WebView` uses WebKit under the hood on macOS — native-quality rendering, no Swing bridge, no Retina problem. The input pane and window chrome would still be JavaFX, not AppKit — not truly native — but it would solve the terminal rendering problem cleanly.

I seriously considered this. The sticking point: the input field users type into constantly would still not be NSTextView. No system spell-check, no autocorrect, no native OS text shortcuts. That's a meaningful compromise.

**SWT** (Eclipse's widget toolkit) looked genuinely promising. SWT wraps real native OS controls — on macOS, an SWT `Text` widget *is* an `NSTextView`. Eclipse IDE is the proof that it works at scale for Java developers. Native controls, Java code. This seemed like the answer.

Then we looked closer. SWT uses JNA (Java Native Access) for its native layer. JNA loads native libraries at runtime via reflection and dynamic class loading — patterns that GraalVM's static analyser cannot see through at build time. Getting JNA to work in a GraalVM native image requires fragile substitution configuration that breaks on library updates. No clean native image story. Ruled out.

**Java + JNI directly to AppKit** — theoretically possible, practically a maintenance nightmare. Ruled out.

I was stuck. I wanted Java *and* a truly native macOS UI *and* a clean native image build. The options I'd explored each broke on one of those constraints.

---

## A Fresh Perspective: The Parallel Brainstorm

At this point I tried something different. I opened a completely separate Claude Code session — one with no knowledge of this project at all — and gave it a single abstract problem: *how do you build a macOS desktop app that keeps as much logic as possible in Java while delivering a truly native UI, with minimal native code to maintain?*

The reason for the isolation: if I'd asked in the same session, it would have anchored on my existing design and optimised around it. Starting fresh, with only the abstract problem, produces genuinely different thinking. It's a useful technique — use one session to explore freely, another to evaluate the results against your actual constraints.

That fresh session produced a compelling approach:

- A tiny, purpose-built **Objective-C bridge** (`MyMacUI.dylib`) exposing only the AppKit primitives the app needs, via a clean C ABI
- **Panama FFM API** (Java's Foreign Function & Memory API, stable since Java 22) as the bridge — no JNA, no runtime reflection, fully visible to GraalVM's static analyser
- **Quarkus Native** (GraalVM/Mandrel) to compile the Java side to a standalone native binary
- **Objective-C over Swift** for the bridge — Panama's `jextract` generates bindings from C headers cleanly; Swift's ABI is name-mangled and unstable

The brainstorm was designed for a generic business app: windows, buttons, labels, menus. It had no idea we needed a terminal emulator.

---

## Evaluating the Brainstorm Against Reality

We evaluated it against what we're actually building.

The architecture held up well. Panama FFM + Objective-C C ABI is exactly the right mechanism. Quarkus Native fits. The minimal bridge principle is sound.

The gap: **AppKit has no terminal emulator widget.** There's no `NSTerminalView`. Implementing one in Objective-C would be a large, fragile codebase that completely contradicts the minimal bridge principle.

The fix became obvious: add **WKWebView** to the bridge's primitive set, and run **xterm.js** inside it. WKWebView uses WebKit — native-quality rendering on macOS. xterm.js is the industry-standard VT terminal emulator, used by VS Code and GitHub Codespaces. It handles every ANSI/VT100 sequence Claude Code produces with zero custom rendering code. The Objective-C bridge just needed one more primitive: WKWebView creation and a JavaScript evaluation method.

The architecture absorbed it cleanly:

| Primitive | AppKit control | Purpose |
|-----------|---------------|---------|
| Main window | NSWindow | App shell |
| Split layout | NSSplitView | Terminal top / input bottom |
| Terminal pane | WKWebView | Hosts xterm.js |
| Input pane | NSTextView | Native — real spell-check, autocorrect |
| Menu bar | NSMenu | Standard macOS menus |

---

## One More Pivot: Dropping pty4j

I'd planned pty4j for PTY subprocess management. It works well in JVM mode. But pty4j uses JNA under the hood — the exact same problem that killed SWT.

Since we're already committed to Panama FFM for the AppKit bridge, the fix is consistent: use Panama FFM for PTY management too. The POSIX PTY API (`posix_openpt`, `grantpt`, `unlockpt`, `ptsname`, `posix_spawn`, `ioctl(TIOCSWINSZ)`) is callable directly from Java via Panama. No additional dependencies. Fully visible to GraalVM at build time.

One subtlety: calling `fork()` directly inside a GraalVM native image is unsafe — the child inherits the parent's heap state mid-initialisation. `posix_spawn()` handles process creation cleanly instead, with full support for file descriptor inheritance, which is how the slave PTY is handed to the `claude` subprocess as its stdin/stdout/stderr.

---

## Revisiting the Long-Term Vision

After all that, I paused and looked back at where I'd started: TamboUI as the long-term output renderer.

Here's the problem: TamboUI is a Java-side widget framework. In the original JavaFX design, it slotted cleanly behind the `OutputRenderer` interface — both lived in the Java/JavaFX world. But in the new architecture, the UI layer is AppKit via the Objective-C bridge. There's no JavaFX surface for TamboUI to render into.

The `OutputRenderer` interface still makes sense. The swap still makes sense. But the destination has changed.

For direct API mode in the new architecture, the natural renderer is already sitting right there: **replace xterm.js in the WKWebView with a richer web renderer** that handles structured API events instead of raw terminal bytes. Instead of a terminal emulator, a custom web UI that renders message bubbles, streaming text, collapsible tool calls, code blocks — essentially what claude.ai does, running inside a native WKWebView backed by WebKit. The Java side sends structured events; the web layer renders them.

This is actually *more* capable than TamboUI was intended to be, and it fits the architecture we already have. TamboUI was the right vision for the wrong stack. The new stack points somewhere better.

---

## Where I Am Now (And It Might Change Again)

This is my best understanding of the right architecture based on everything explored so far. It hasn't been built yet.

Some of these decisions will survive contact with reality; some probably won't. The open questions still on the table — how PTY bytes flow to xterm.js, whether `posix_spawn` correctly establishes a controlling terminal, how AppKit callbacks and Quarkus worker threads hand off to each other — are the kind of things that only resolve when you actually write the code. Any of them could force another pivot.

That's fine. The point of this exploration wasn't to find the perfect architecture on paper. It was to find a solid, well-reasoned starting point that I can build on and adjust as reality pushes back.

The current plan:

| Concern | Technology |
|---------|-----------|
| Native macOS UI | AppKit via Objective-C bridge (MyMacUI.dylib) |
| Java ↔ native bridge | Panama FFM API + jextract |
| Terminal pane (v1) | WKWebView + xterm.js |
| Rich renderer (future) | WKWebView + custom web UI (structured API events) |
| Input pane | NSTextView |
| PTY management | Panama FFM → POSIX libc |
| Java runtime | Quarkus Native (GraalVM/Mandrel) |

The module structure:

```
claude-desktop/
├── mac-ui-bridge/    ← Objective-C: MyMacUI.dylib
├── app-core/         ← Java: PTY, session, interaction logic (no UI)
└── app-macos/        ← Java: Panama bindings, Quarkus wiring, .app packaging
```

The `SessionProvider` and `OutputRenderer` interfaces from the very first design survived every pivot intact. The abstractions were right all along; only the implementations changed.

---

## What This Process Has Shown Me

The entire exploration — from the first JavaFX sketch to the final Objective-C bridge decision — happened across a single working session using Claude Code.

We explored each option to the depth needed to make a real decision, then either rejected it with a clear reason or built on it. Some pivots came from hard constraints (can't code Swift, JNA kills GraalVM), some from a better idea surfacing (the parallel brainstorm), and one from honest re-examination of an assumption I'd carried from the start (TamboUI).

Claude didn't make the decisions. I did. But we worked through the research and trade-off analysis together, and explored quickly enough that changing direction felt cheap rather than costly. An exploration that might have taken days of reading, prototyping, and dead ends happened in a single session.

That speed is what makes pivoting feel acceptable rather than costly. If the Objective-C bridge turns out to be harder to work with than expected, or if Panama FFM upcalls have issues I haven't anticipated, or if WKWebView and NSTextView don't play nicely in a split pane — I'll explore the next option the same way. Fast, deliberate, documented.

That's the mode I want to keep working in throughout this project. And when a pivot happens, it'll show up here. The Maven scaffolding and first NSWindow creation are next — the first real test of whether any of this survives contact with actual code.
