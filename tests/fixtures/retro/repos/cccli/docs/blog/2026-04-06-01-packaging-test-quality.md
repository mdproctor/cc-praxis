# Claude Desktop CLI — Packaging and Test Quality

**Date:** 2026-04-06
**Type:** phase-update

---

## What we were trying to achieve: the .app bundle and honest test coverage

Plan 5 ended with the app working but still requiring `-Dcccli.dylib.path=...`
on every launch. Two things to fix before Plan 5b: package it as a proper
`.app` bundle, and make the test suite earn its numbers.

## What we believed going in: packaging would be the easy part

I thought bundling would be mechanical — directory structure, copy files, sign
it. The interesting work would be the dylib auto-detection logic. And I thought
expanding test coverage would take a few hours. I didn't expect to find a JVM
crash.

## The bundle, the test review, and a SIGTRAP with no explanation

### The bundle

Claude built Plan 6 cleanly. Three pieces: `@rpath @executable_path/../Frameworks`
added to `native-image.properties` (so the binary finds the dylib at bundle-relative
path), `resolveDylibPath(executablePath)` added to `MacUIBridge` (tries bundle
detection via `ProcessHandle`, falls back to the system property), and
`scripts/bundle.sh` which assembles `Contents/MacOS/`, `Contents/Frameworks/`,
`Info.plist`, and ad-hoc signs it. Wired into `mvn install -Pnative`.

The bundle runs. Log shows `Detected .app bundle — using bundle dylib at:
.../Contents/Frameworks/libMyMacUI.dylib`. No system property needed.

### The test quality review

The suite was at 58 tests when I asked: are these genuinely good, or did we
inflate the count? Claude wrote the analysis. Nine tests were filler — a constant
check (`SIGINT == 2`), smoke tests that only assert no exception, two tests that
checked the same happy path with slightly different wording. The honest number
of genuinely valuable tests was closer to 49.

The important additions: `echoFlagIsDisabledAfterOpen` (regression test for the
double-echo bug — write to master without a subprocess, nothing should echo back),
a real `sendSigIntIsDeliveredToProcess`, a real `resizeSetsTerminalDimensions`,
and the full `MacUIBridgeTest` suite covering all three resolution branches of
`resolveDylibPath`. The filler tests stayed but got noted — they don't inflate
the quality score.

### Exit 133

Claude's first attempt at testing resize used `stty size` as a subprocess —
spawn it after resize, capture the output, verify rows and cols. It crashed the
JVM. Exit code 133. No error. No stack trace. No indication of what failed.

Exit 133 = 128 + 5 = SIGTRAP. On macOS AArch64, that's a PAC (Pointer
Authentication Code) violation — the kind that happens when a function pointer
gets corrupted.

We isolated it by bisecting. `PosixLibraryTest` alone — fine. `PtyProcessTest`
alone — fine. `PosixLibraryTest` then `PtyProcessTest` in the same surefire JVM
fork — crash. Further: which `PosixLibraryTest` tests caused it? The original
three (open/close master only) — fine. The write/read test — crash.

The pattern: calling Panama FFM `write()` or `read()` on a PTY slave fd corrupts
something inside Panama's downcall infrastructure. The next test class that invokes
any Panama downcall hits the corruption and SIGTRAP. Fix: `reuseForks=false` in
surefire. Each test class gets a fresh JVM.

For the resize test itself: `TIOCGWINSZ` read-back after `TIOCSWINSZ` returns 0,0
on macOS for disconnected PTYs — the ioctl returns success but the data doesn't
persist. macOS PTY behaviour, not our bug. Resize stays as a smoke test with that
noted.

For `sendSigIntIsDeliveredToProcess`: shell trap approaches failed (script-mode
signal handling, timing races). Python handler — timed out. Working approach:
spawn `/bin/sleep 30`, send SIGINT, poll `waitpid(WNOHANG)` until exit. No output
capture. Either the signal killed it or it didn't.

## Sixty tests, all green

The suite sits at 60 tests. The filler ones are annotated — they don't inflate
the quality score. The two hard tests both verify the right thing rather than
the easy thing. WKWebView + xterm.js is next, now that the .app bundle exists.
