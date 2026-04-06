# The Split Pane: Seven Bugs and What They Taught Us

**Date:** 2026-04-04
**Type:** phase-update

---

## The goal: an end-to-end Java ↔ native communication pipeline

Prove the Java ↔ native UI communication pipeline end-to-end: type in a native input field, press Enter, Java receives it via Panama upcall, Java sends text back to the display pane. Simple idea. Seven bugs.

---

## Bug 1: NSSplitView blocks keyboard events

Claude and I had seven bugs to get through before the pipeline worked end to end.

I planned to use NSSplitView to split the window into terminal (top) and input (bottom) panes. We set it as `window.contentView`. Result: no mouse events, no keyboard events, nothing reached any subview.

The fix was to strip everything back to the absolute minimum — an NSTextField added directly to the existing `window.contentView` without replacing it. That worked immediately. The rule: **never replace `window.contentView`**. Add views to it.

---

## Bug 2: WKWebView's subprocess silently fails in a JVM process

I'd planned the terminal pane as WKWebView + xterm.js. The WebView appeared (correct size, correct position), we loaded HTML, evaluated JavaScript without errors, but nothing ever rendered. The `WKNavigationDelegate` never fired.

Root cause: WKWebView spawns a separate `WebContent` subprocess. In a JVM process launched from a terminal (no `.app` bundle), the IPC between host and WebContent silently fails. `evaluateJavaScript:` returns success but the result goes nowhere.

For now, we replaced WKWebView with a plain NSTextView for the output pane. It works perfectly — no subprocess, no WebKit. WKWebView + xterm.js returns in Plan 3 when the app runs as a proper `.app` bundle — where WebKit's subprocess model actually works.

---

## Bug 3: dispatch_async blocks don't drain when [NSApp run] is inside a dispatch_async

This one took the longest to find. We call `myui_start()` from a `dispatch_async(main_queue, ^{ setupUI(); [NSApp run]; })` block. From GCD's perspective, that outer block is still executing — `[NSApp run]` never returns until the app terminates. So GCD's main queue serialisation locks out any new blocks. `dispatch_async(main_queue, ...)` and `dispatch_after(...)` calls simply queue up and never execute.

AppKit events (typing, clicking, window delegates) still work because `[NSApp run]` pumps the CFRunLoop directly, bypassing GCD entirely.

**Consequence:** Any code that needs to run "after the run loop starts" must use AppKit delegate methods, not dispatch. Any synchronous UI update called from an AppKit event handler must update the view directly, not via dispatch.

This single insight explains bugs 4, 5, and 7 below.

---

## Bug 4: Text submitted by user never appeared in output pane

Java received the text (logged correctly), called `bridge.appendOutput()`, which called the ObjC `myui_append_output()` function. The function dispatched a block to the main queue to update NSTextView. The block never ran (see Bug 3).

The fix: detect which thread we're on and update synchronously:

```objc
if ([NSThread isMainThread]) {
    doAppend(str);        // synchronous — called from AppKit event handler
} else {
    dispatch_async(dispatch_get_main_queue(), ^{ doAppend(str); });
}
```

---

## Bug 5: Cursor invisible until first Enter

The NSTextField received keystrokes — text appeared as we typed — but showed no cursor. After pressing Enter — which triggers the action, clears the field, and transitions through a non-empty editing state — the cursor appeared.

This is a known AppKit bug: an empty NSTextField that gains first responder programmatically never starts the insertion-point blink timer. The canonical fix is a no-op string assignment after `makeFirstResponder:`:

```objc
[inputField setStringValue:@" "];
[inputField setStringValue:@""];
```

But every attempt we made to schedule this via `dispatch_after` failed (Bug 3 again). The fix we landed on: do it in `windowDidBecomeKey:`, an AppKit delegate method that fires inside the run loop at exactly the right moment.

---

## Bug 6: Placeholder text invisible on dark background

The NSTextField placeholder (`placeholderString`) uses the system's default placeholder colour — a semi-transparent grey that's near-invisible against a dark background. Fix: use `placeholderAttributedString` with an explicit colour.

---

## Bug 7: Cursor still missing (dispatch_after not running)

We tried `dispatch_after(50ms, main_queue, block)` to defer the cursor fix until after the run loop started. It never ran. Bug 3, again. We confirmed by adding NSLog inside the dispatch block — it never appeared in the output.

---

By the end: NSTextField → Enter → Panama upcall → Java ✅, Java → downcall → NSTextView update ✅, cursor visible from open ✅, window close → clean terminate ✅, JVM and native image both working at 0.020s.

## The Pattern

Every bug taught the same lesson from a different angle. The threading model of this architecture — GCD + AppKit + Panama FFM + Quarkus — has sharp edges. Once you understand that GCD main queue serialisation locks out dispatch blocks when `[NSApp run]` is nested inside one, everything else follows. Synchronous updates, AppKit delegates, no dispatch. That's the rule. PTY integration — actually spawning claude and routing its output — is where that rule gets tested again.
