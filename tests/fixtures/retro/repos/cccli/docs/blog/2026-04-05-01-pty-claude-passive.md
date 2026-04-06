# Claude Desktop CLI — The PTY Layer

**Date:** 2026-04-05
**Type:** phase-update

---

## What we were trying to achieve: spawning claude in a PTY

Working with Claude across Plans 3, 4, and 5, we took the split-pane UI from Plan 2 and connected it to the real `claude` CLI — PTY subprocess, ANSI stripping, passive mode, and a Stop button. Three plans, one connected arc.

## What we believed going in: PTY was the hard part

I expected the PTY work to be the difficult part. Raw POSIX calls through Panama FFM — `posix_openpt`, `posix_spawn`, `read`, `write`, `tcgetattr`, `ioctl` — all from scratch in Java, because no existing library (pty4j, anything JNA-based) survives GraalVM native image. That was genuinely new territory.

What I didn't expect was GCD Bug 3 coming back.

## What we tried: it was never just the PTY

I gave Claude the PosixLibrary spec and let it run — 17 POSIX functions as static `MethodHandle` fields, TDD against real PTY devices. It came back clean. PtyProcess next: open a master/slave pair, spawn a subprocess with its stdio wired to the slave, read output on a daemon thread. "Cat round-trip works," Claude reported back. Write `hello`, read back `hello`.

Then we wired PTY output to `bridge.appendOutput()`. Nothing appeared in the window.

### GCD, again

The PTY reader runs on a background thread. `myui_append_output()` used `dispatch_async(main_queue, ...)` for non-main-thread callers — correct for every case we'd seen before. But this is Bug 3: `[NSApp run]` lives inside a `dispatch_async` block, so the main queue is permanently "busy" from GCD's perspective. No background-dispatched block ever runs. We'd fixed this for the upcall path in Plan 2. Neither of us had connected the PTY reader — a different background thread, a different call site — to the same root cause. Same fix once we saw it: `performSelectorOnMainThread:waitUntilDone:NO`, which schedules on NSRunLoop instead.

### Text appeared twice

With output flowing, every line appeared twice. Claude came back from manual testing with a one-liner: "Text appears twice." We worked out why together: the PTY line discipline was echoing every byte written to the master back to the reader on top of `/bin/cat`'s own output. I asked Claude to fix it with `tcgetattr`: clear the `ECHO` bit (`0x00000008`) in `c_lflag` at byte offset 24, call `tcsetattr` back. One occurrence per line from then on.

After that, `/bin/cat` worked perfectly. We swapped it for the real binary.

### The native image wrinkle

One thing Claude hit and diagnosed: static final `MethodHandle` fields in a hand-written class still need `--initialize-at-run-time`, even though the symbols are always in libc. "linkToNative parsing failure at analysis time" — nothing in the error points to the cause. Claude came back with the diagnosis after working through the class initialization rules: the error wasn't about symbol availability — GraalVM was trying to inline through `invokeExact()` at build time, and the static initializer had to move to runtime.

### Stripping ANSI for NSTextView

Claude outputs ANSI escape sequences throughout — colours, cursor movement, progress spinners. NSTextView doesn't interpret them; they render as literal characters. I asked Claude to write a regex stripper. The first version came back with an over-broad pattern for single-char VT100 escapes — anything after `ESC` except `[` would match, including `ESC SPACE`. The code review flagged it. Claude had noted in its self-review that the pattern was "conservative but accepted" — the reviewer disagreed; Claude narrowed it to `[A-Za-z0-9=>?]` without argument. This is explicitly a development workaround — Plan 5b replaces NSTextView with WKWebView + xterm.js, which handles ANSI natively.

### Finding the binary

The `claude` binary lives in `~/.local/bin/claude`. In a native binary with no login shell, that path won't be in PATH. I asked Claude to resolve it with a `ProcessBuilder` running `/bin/zsh -l -c 'which claude'`. No native image configuration needed — `ProcessBuilder` is fully supported.

### Passive mode and the Stop button

I asked Claude to build a timer-based interaction detector: any PTY output → PASSIVE (input disabled, Stop button appears); 800ms of silence → FREE_TEXT (input re-enabled). The Stop button sends SIGINT and calls `forceIdle()` immediately — you don't wait for the quiet timer. The ObjC bridge gained `myui_set_passive_mode(int)`, implemented with `performSelectorOnMainThread:` rather than `dispatch_async`.

Claude also had to extend `myui_start()` with a seventh callback for the Stop button. My plan had a C error I'd missed — `extern` on a `static` global inside an ObjC method, which clang rejects outright. Claude didn't ask about it; it just noted the issue in its report and used a static forward declaration instead. I would have hit it at compile time either way, but I didn't have to.

Plans 4 and 5's native images built first try. Plan 3 needed two fixes: `--initialize-at-run-time` for `PosixLibrary`, and a wrong parameter count in the `posix_spawn` downcall. That last one was my mistake in the plan spec — I'd written five `void*` instead of six. Claude hit `MissingForeignRegistrationError`, which names the function but says nothing about what's wrong with the signature. It came back: "The downcall has five params but `posix_spawn` takes six — pid_t\*, path, file_actions, attrp, argv[], envp[]." Fixed.

One thing Claude did that I had to rein in: while building `InteractionDetector`, it quietly bumped the whole project from Java 22 to Java 25, added `--enable-preview` to both `pom.xml` files, and committed. `InteractionDetector` uses nothing newer than Java 8. When I pointed this out Claude agreed immediately and reverted cleanly — but it was a good reminder that Claude will optimise for making the code compile, and sometimes that means reaching for things that weren't asked for. Worth keeping an eye on.

The app works. Type a prompt, Claude responds, input blocks while it's generating, the Stop button sends SIGINT when you've had enough.

The AnsiStripper makes the output readable but crude. Colours gone, progress indicators gone, interactive elements broken. It's usable for text responses. It's not good enough for Claude Code's richer output.

The right fix is WKWebView + xterm.js. That only works in a proper `.app` bundle — we've known this since Plan 2. Packaging comes next, and then we find out what breaks.
