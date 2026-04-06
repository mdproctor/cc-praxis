# Seven Things That Don't Work in AppKit (And What Does)

**Date:** 2026-04-04
**Type:** phase-update

---

Building the split-pane UI for Claude Desktop CLI took one session with Claude and produced seven distinct bugs. None of them crashed the app. Most of them produced no error at all. They just silently didn't work — which, it turns out, is the hardest kind of bug to fix.

Here's a quick map of the journey:

| # | Bug | Silent? | Root cause |
|---|-----|---------|------------|
| 1 | NSSplitView swallows all events | ✅ | `window.contentView` replaced |
| 2 | WKWebView renders nothing | ✅ | WebContent subprocess fails without `.app` bundle |
| 3 | GCD blocks never execute | ✅ | `[NSApp run]` inside `dispatch_async` locks the main queue |
| 4 | Output pane never updates | ✅ | Bug 3 — dispatching from upcall context |
| 5 | NSTextField cursor invisible | ✅ | AppKit empty-field blink timer bug |
| 6 | Placeholder text invisible | ✅ | System placeholder colour on dark background |
| 7 | JVM vs native image thread crash | ❌ | Different threads call `myui_start()` in each mode |

---

## Bug 1: NSSplitView silently swallows all events

The natural choice for a two-pane layout is `NSSplitView`. I created one, set it as `window.contentView`, added the output view and input field. The window appeared, the split looked right, and nothing responded to clicks or keypresses — no error, no warning, just silence.

**What we tried (all failed):**
- `[window recalculateKeyViewLoop]` after replacement
- Explicit `[window makeFirstResponder:subview]`
- Different view hierarchies inside the split

We found the fix by stripping everything back to the minimum: one `NSTextField` added directly to `window.contentView` without replacing it. That worked immediately.

```
BROKEN — replace contentView        WORKING — add to contentView
─────────────────────────────       ──────────────────────────────
NSWindow                            NSWindow
  └── NSSplitView  ❌                 └── NSView (original, keep it)
       ├── WKWebView                        ├── NSTextView  (output)
       └── NSTextField                      └── NSTextField (input)
       ↑ replaces contentView               ↑ addSubview:, never replace
         breaks responder chain               responder chain intact
```

**Rule: Never replace `window.contentView`. Add views to it.**

When you call `window.contentView = myNewView`, you silently break an internal connection AppKit maintains between the window and its responder chain. The existing content view AppKit creates for you has this wired correctly. Replacing it destroys it.

---

## Bug 2: WKWebView renders nothing in a JVM process

The output pane was designed for WKWebView + xterm.js. The WebView appeared with the correct size. I loaded HTML. I called `evaluateJavaScript:`. The completion handler reported no error. Nothing appeared on screen, ever. The `WKNavigationDelegate` (`didFinishNavigation:`, `didFailNavigation:`) never fired.

```
Production (.app bundle) ✅         Development (JVM from terminal) ❌
──────────────────────────          ─────────────────────────────────
Host Process (.app)                 Host Process (java)
   │                                   │
   │  IPC (sandbox-permitted)          │  IPC ──────── ✗ silent failure
   │                                   │
   ▼                                   ▼
WebContent Process                  WebContent Process
(renders HTML/JS)                   (fails to start or communicate)
```

WKWebView spawns a separate `WebContent` process. In a proper `.app` bundle, macOS sets up the IPC correctly. In a JVM process launched from a terminal with no bundle, the IPC silently fails. Everything appears to succeed from the ObjC side — the effects just never arrive.

**For development, we replaced WKWebView with NSTextView.** It's entirely in-process, works perfectly, and the API can be designed so the renderer is swappable. WKWebView returns in production, where the `.app` bundle makes the subprocess model work.

---

## Bug 3: The GCD block that never ran

This is the one that explained everything else.

When I needed to do something after the AppKit run loop started — set initial focus, fix the cursor, update the display — the natural approach was `dispatch_async(main_queue, block)`. These blocks were queued. They never executed.

Here's why:

```
Time ──────────────────────────────────────────────────────────────────────►

GCD main queue (serial):

╔══════════════════════════════════════════════════════════════════════════╗
║  dispatch_async(main_queue, ^{                                           ║
║      setupUI();                                                          ║
║      [NSApp run];  ◄── blocks here (run loop running)                   ║
║      signal(done); ◄── only when app terminates                         ║
║  });                                                                     ║
╚══════════════════════════════════════════════════════════════════════════╝
      ▲ this block never finishes (from GCD's view)
      
      While this block is "running", no new blocks can execute:
      
      dispatch_after(50ms, main_queue, focusBlock)   ── queued, never drains
      dispatch_async(main_queue, updateBlock)        ── queued, never drains
      dispatch_after(200ms, main_queue, cursorFix)   ── queued, never drains
```

GCD serializes the main queue. The outer block containing `[NSApp run]` never returns — the app is running. So GCD holds the lock. Every `dispatch_async` or `dispatch_after` targeting the main queue silently queues and waits forever.

**AppKit events still work** because `[NSApp run]` pumps CFRunLoop directly, bypassing GCD entirely. Typing, clicking, window delegate callbacks — all go through CFRunLoop, not GCD.

**What works instead:**

```
AppKit delegate methods fire INSIDE the run loop — GCD not involved:

windowDidBecomeKey:          ✅  fires when window gains focus
applicationDidFinishLaunching: ✅  fires on app startup
NSTimer (scheduledTimer...)  ✅  fires via CFRunLoop
windowWillClose:             ✅  fires on window close

GCD targeting main queue:

dispatch_async(main_queue, ...)   ❌  blocked by outer block
dispatch_after(N, main_queue, .) ❌  blocked by outer block
performSelector:afterDelay:       ❌  same mechanism, same result
```

---

## Bug 4: Text submitted but never appeared

With the output pane switched to NSTextView, the call chain looked like this:

```
User presses Enter
       │
       ▼
NSTextField action (AppKit, main thread)
       │
       ▼
ObjC callback → Panama upcall → Java handler
       │                             │
       │                    Log.info("Input received")   ✅ appears
       │                             │
       │                    bridge.appendOutput(text)
       │                             │
       ▼                             ▼
ObjC myui_append_output()     Panama downcall
       │
       ├── dispatch_async(main_queue, ^{          ❌ never runs (Bug 3)
       │       [theOutputView setString:...];
       │   });
       │
       └── fix: [NSThread isMainThread] ?         ✅ synchronous update
               [theOutputView setString:...];        works immediately
```

Java logged `"Input received: hello"`. The NSTextView didn't update. Bug 3 again — the ObjC function was dispatching to the main queue. Once we understood the dispatch block would never run, the fix was immediate: detect the thread and update synchronously.

```objc
if ([NSThread isMainThread]) {
    doAppend(str);   // synchronous — already on the right thread
} else {
    dispatch_async(dispatch_get_main_queue(), ^{ doAppend(str); });
}
```

---

## Bug 5: NSTextField cursor invisible until first Enter

The text field worked — keystrokes appeared. But there was no blinking cursor. The field looked dead. After pressing Enter once, the cursor appeared.

```
Initial state (bug):          After first Enter (works):
─────────────────────         ──────────────────────────
┌─────────────────────┐       ┌─────────────────────┐
│                     │       │                     │
│  (no cursor, but    │       │  |  (cursor blinks, │
│  keystrokes work)   │  →    │  text appears here) │
│                     │       │                     │
└─────────────────────┘       └─────────────────────┘
field editor active           action fired, field cleared,
blink timer NOT started       re-focus started timer correctly
```

This is a documented AppKit bug. When an empty NSTextField gains first responder programmatically, the field editor is installed (keystrokes work) but the insertion-point blink timer never starts. After Enter fires the action and the field transitions through a non-empty state, a full re-focus cycle starts the timer.

**Canonical fix:** A no-op string assignment after `makeFirstResponder:`:

```objc
[inputField setStringValue:@" "];
[inputField setStringValue:@""];
```

But every attempt we made to schedule this via `dispatch_after` failed (Bug 3). The only place it works reliably is `windowDidBecomeKey:` — an AppKit delegate that fires inside the run loop at exactly the right moment.

---

## Bug 6: Placeholder text invisible on dark background

One line: `placeholderString` uses a semi-transparent system grey intended for light backgrounds.

```
NSTextField on dark background (#1E1E1E):

placeholderString = @"Type here..."    ← near-invisible (system grey)
placeholderAttributedString with       ← readable (explicit 50% grey)
  NSForegroundColor: (0.5, 0.5, 0.5)
```

Use `placeholderAttributedString` with an explicit colour.

---

## Bug 7: JVM vs native image threading model

In JVM mode, Quarkus calls `@QuarkusMain.run()` on a **worker thread**. In native image, it calls `run()` on the **OS main thread**. AppKit requires the main thread for all UI. The same `myui_start()` needs to handle both.

| Mode | Thread calling `run()` | `[NSApp run]` approach | Blocker |
|------|----------------------|------------------------|---------|
| JVM (`mvn quarkus:dev`) | Worker thread | `dispatch_async` to main, semaphore blocks worker | Worker thread |
| Native image (GraalVM) | OS main thread | `dispatch_async` to main, `CFRunLoopRun()` | CFRunLoop |

If you call `dispatch_semaphore_wait` from the main thread after dispatching to the main queue — you get an immediate deadlock. `CFRunLoopRun()` is the escape hatch: it pumps the main run loop, processes the dispatched block (which calls `[NSApp run]`), and returns when `CFRunLoopStop()` is called.

```objc
if ([NSThread isMainThread]) {
    // Native image: main thread. Use CFRunLoopRun to process the queued block.
    dispatch_async(dispatch_get_main_queue(), ^{
        setupAndRun();
        CFRunLoopStop(CFRunLoopGetCurrent());
    });
    CFRunLoopRun();
} else {
    // JVM mode: worker thread. Block worker until app terminates.
    dispatch_semaphore_t done = dispatch_semaphore_create(0);
    dispatch_async(dispatch_get_main_queue(), ^{
        setupAndRun();
        dispatch_semaphore_signal(done);
    });
    dispatch_semaphore_wait(done, DISPATCH_TIME_FOREVER);
}
```

---

## What This Cost and What It Bought

Seven bugs. All silent except one. Most of them variants of the same threading problem — once Bug 3 was understood, it retrospectively explained three others.

The pattern we used: add the right NSLog in the right place, strip back to the minimum test case, verify one assumption at a time. Most bugs resolved in minutes once the diagnostic information was in hand. The GCD serialisation bug was the exception — it took a proper understanding of how `[NSApp run]` interacts with the GCD main queue before any fix made sense.

What working with Claude gave me wasn't just speed. Claude could hold the full context — the threading model, the AppKit behaviour, the Panama FFM constraints, the JVM vs native image differences — and reason across all of them simultaneously. When the dispatch block turned out to be the thread running through every other symptom, that was a cross-cutting insight that would have taken me much longer to reach alone.

---

## Quick Reference

If you're building something similar and hit a wall, check these first:

```
Symptom                              → Check
─────────────────────────────────────────────────────────────
Nothing responds to clicks/keyboard  → Did window.contentView get replaced?
WKWebView blank, no errors           → Running without .app bundle?
dispatch block never executes        → Is [NSApp run] inside dispatch_async?
UI update from upcall not appearing  → Are you dispatching when on main thread?
NSTextField cursor invisible         → Apply windowDidBecomeKey: blink fix
Crash: "must be on main thread"      → JVM vs native image thread branch missing
```

