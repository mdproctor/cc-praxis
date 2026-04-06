# The First Window: Building the Bridge Foundation

**Date:** 2026-04-04
**Type:** phase-update

---

## The goal: proving Panama upcalls work in GraalVM native image

Prove the architecture before building anything on top of it. The two risks that had to be validated:

1. **Panama upcalls in GraalVM native image** — Objective-C calling back into compiled Java code. If this doesn't work, every button click and window event breaks.
2. **AppKit main thread + Quarkus thread model** — AppKit requires the main thread. Quarkus manages its own threads. These two constraints have to coexist.

The milestone: an `NSWindow` appears on screen, the user closes it, a Java log line fires exactly once, and the same works as a standalone native binary with no JVM.

---

## What we built: a five-function Objective-C bridge

A minimal Objective-C bridge (`MyMacUI.dylib`) exposing five C functions:

```c
void     myui_init_application(void);
intptr_t myui_create_window(const char*, int, int, WindowClosedCallback);
void     myui_run(void);
void     myui_terminate(void);
intptr_t myui_start(const char*, int, int, WindowClosedCallback);
```

`jextract` generates Java bindings from the header. Panama FFM calls the bridge. Quarkus wires it together. GraalVM compiles the whole thing to a native binary.

---

## The Pivots (There Were Several)

Working with Claude, we hit six distinct problems before the window appeared and the upcall fired.

### Pivot 1: Quarkus isn't on the main thread in JVM mode

Our first run: `NSWindow should only be instantiated on the main thread!`

AppKit crashed immediately. Quarkus calls `@QuarkusMain.run()` on a worker thread, not the OS main thread. The fix: we moved all AppKit work to the main thread via GCD (`dispatch_async(dispatch_get_main_queue(), ...)`) and blocked the worker thread with a semaphore until the app terminates.

JVM mode: window appeared. Upcall fired.

### Pivot 2: The upcall fired twice

We saw the callback log twice. The `windowWillClose:` delegate method was firing once for the user's close action, then again when `[NSApp terminate:]` caused AppKit to close the window programmatically. One-line fix: clear the callback pointer before invoking it.

```objc
WindowClosedCallback cb = self.onClosed;
self.onClosed = NULL; // clear before invoking
cb();
```

### Pivot 3: jextract's upcall helper doesn't work in native image

The jextract-generated `WindowClosedCallback.allocate()` uses `MethodHandles.privateLookupIn()` + `findVirtual()` on a generated interface. GraalVM's static analyser can't resolve interface method handles at compile time.

Fix: we bypassed the jextract helper entirely and wrote the upcall directly using `MethodHandles.lookup().findStatic()` on our own class — a pattern GraalVM handles reliably.

```java
MethodHandle mh = MethodHandles.lookup()
    .findStatic(Callbacks.class, "onWindowClosed",
            MethodType.methodType(void.class));
return Linker.nativeLinker().upcallStub(mh, VOID_VOID, arena);
```

### Pivot 4: GraalVM initialises jextract-generated classes at build time

`UnsatisfiedLinkError: unresolved symbol: myui_start` — GraalVM tried to find the dylib symbol at image build time, before the dylib exists. Fix: we deferred initialisation of the generated package to runtime.

```properties
Args = --enable-native-access=ALL-UNNAMED \
       --initialize-at-run-time=dev.mproctor.cccli.bridge.gen
```

### Pivot 5: GraalVM's foreign metadata format was wrong (twice)

`MissingForeignRegistrationError` — upcall not registered. The GraalVM 25 error message had a bug: the JSON snippet it was supposed to print was empty.

We tried `{"foreign": {"upcalls": [{"descriptor": "()void"}]}}` first — wrong format, parse error.

Fix: we ran the JVM app with the native-image tracing agent (`-agentlib:native-image-agent`) to generate the correct metadata. The actual format GraalVM 25 expects is `directUpcalls` with class/method details, not a generic descriptor:

```json
{
  "foreign": {
    "directUpcalls": [
      {
        "class": "dev.mproctor.cccli.bridge.Callbacks",
        "method": "onWindowClosed",
        "returnType": "void",
        "parameterTypes": []
      }
    ]
  }
}
```

### Pivot 6: Native image deadlocks on window creation

We started the native binary — it loaded the dylib, then hung silently. No window, no error.

In JVM mode, Quarkus uses a worker thread for `run()`. In native image, it calls `run()` synchronously **on the OS main thread**. The `dispatch_async(main_queue) + semaphore_wait` pattern deadlocks when called from the main thread: the semaphore blocks the main thread, the GCD block can never drain.

Fix: detect the thread at runtime and branch:

```objc
if ([NSThread isMainThread]) {
    // Native image path: use CFRunLoopRun() to drain the main queue
    dispatch_async(dispatch_get_main_queue(), ^{
        myui_init_application();
        myui_create_window(...);
        [NSApp run];
        CFRunLoopStop(CFRunLoopGetCurrent());
    });
    CFRunLoopRun();
} else {
    // JVM mode path: worker thread, semaphore blocks it
    dispatch_async(dispatch_get_main_queue(), ^{ ... });
    dispatch_semaphore_wait(done, DISPATCH_TIME_FOREVER);
}
```

---

## The result: 0.017s startup, working upcall

```
00:47:01 INFO  app-macos 1.0.0-SNAPSHOT native (powered by Quarkus 3.15.0) started in 0.017s.
00:47:01 INFO  Starting Claude Desktop CLI...
00:47:01 INFO  Loading dylib from: /path/to/libMyMacUI.dylib
00:47:01 INFO  libMyMacUI.dylib loaded successfully
00:47:04 INFO  Window closed via upcall — terminating
```

**0.017 seconds.** A native macOS window, from Java, compiled by GraalVM, with a working Panama upcall back into Quarkus. No JVM. No runtime. No compromises.

The architecture holds. Every pivot was absorbed by the design — the Objective-C bridge stayed minimal, the Java side stayed clean, and the `SessionProvider`/`OutputRenderer` interfaces we defined at the start of the project remain exactly where they should be.

---

## Six pivots, zero architecture changes

Six pivots across one build session, none of them required rethinking the architecture. Each one was a local fix — a wrong format, a wrong assumption about which thread a framework uses, a GraalVM version-specific quirk.

That's the value of getting the abstractions right before writing code. The hard thinking happened in Part 1. Part 2 was just plumbing. Next came the actual UI — NSSplitView, WKWebView, NSTextView — and another seven bugs.
