# workflow-0077 — Concurrent contexts race on shared process-wide state

> Threads / subinterpreters / free-threaded contexts share libc static buffers, module globals,
> lazy caches, or one-time-init tables without a complete synchronization or publication
> protocol.

10 fresh sites. **TSan leads** — build/run the free-threaded TSan image
`taxoshop/cpython-tsan-ft:current` (`Py_GIL_DISABLED=1`), `-e PYTHONMALLOC= -e
TSAN_OPTIONS=halt_on_error=1:history_size=7`. "Reachability" is the thread schedule.

Policy note: weigh each by whether it is a *distinct shared-state class* (libc static / true
process global), not just "share one object across threads" (that class is being consolidated
upstream, see audit7 NOTES).

---

## Site 1 — `time.tzset` writes process-global `tzname`/`timezone`/`altzone`/`daylight`  ⭐

**Site.** `time_tzset` (`Modules/timemodule.c:1168`) calls libc `tzset()` and then
`init_timezone` publishes the module attributes; `time.localtime`/`strftime`/`mktime` read the
libc `tzname[]` globals (e.g. `Modules/timemodule.c:655-659`).

**Reasoning.** `tzset()` mutates process-global timezone state and libc's `tzname[]` static
array with no CPython lock, while another thread is inside `localtime`/`strftime` reading those
globals (and copying `tm_zone` pointers into strings).

**Why it fits.** Process-wide libc state mutated/read from multiple contexts without a common
protocol (`#129824`-class), plus static-storage pointer reuse.

**Reachability.** Thread A loops `time.tzset()` (after `os.environ['TZ']='...'`); thread B loops
`time.localtime()` / `time.strftime('%Z')`. No ctypes.

**Trigger hypothesis.** A's `tzset` overwrites `tzname[0]` while B copies `tm_zone`/`tzname[0]`
→ torn/garbage read; TSan flags the global write vs. read.

**Confidence & dup-check.** Medium. libc `tzname` is inherently unsynchronized; confirm CPython
adds no guard. `gh search issues "tzset thread"`.

---

## Site 2 — `locale.localeconv()` returns a pointer into libc's static `struct lconv`

**Site.** `_locale_localeconv_impl` (`Modules/_localemodule.c:305`) does `lc = localeconv();`
then reads `lc->decimal_point`, `lc->grouping`, etc. The comment at `:307` even notes "hopefully
the localeconv result survives the C library calls."

**Reasoning.** `localeconv()` returns a pointer to a single process-global static struct that the
next `setlocale`/`localeconv` overwrites. Two threads (or one thread doing `localeconv` while
another does `setlocale`) race that static struct.

**Why it fits.** Shared libc static storage read while another context mutates it (sibling of the
original set's `setlocale` site, different function).

**Reachability.** Thread A loops `locale.localeconv()`; thread B loops
`locale.setlocale(locale.LC_ALL, "C")` / `"en_US.UTF-8"`.

**Trigger hypothesis.** B's `setlocale` rewrites the `lconv` fields while A dereferences
`lc->grouping`/`decimal_point` → garbage/torn read.

**Confidence & dup-check.** Medium. Confirm CPython copies fields under a lock (it may hold the
GIL only). `_localemodule` has a known history of locale/thread edges.

---

## Site 3 — `syslog` process-global `S_ident_o` / `S_log_open` across openlog/syslog/closelog

**Site.** `Modules/syslogmodule.c` keeps module-global `S_ident_o` (`:71`) and `S_log_open`
(`:72`); `openlog` writes them (`:192-193`), `syslog` reads `S_ident_o`/`S_log_open`
(`:225`,`:241`), `closelog` clears them (`:276-279`) — all with no lock.

**Reasoning.** Concurrent `openlog`/`syslog`/`closelog` from multiple threads race the global
identity object pointer and the open flag; `closelog` can `Py_CLEAR(S_ident_o)` while `syslog`
holds/derefs it.

**Why it fits.** Module-global lifecycle/flag state mutated and read from multiple contexts
without publication (`#129824`-class); also a potential UAF on `S_ident_o`.

**Reachability.** Thread A loops `syslog.openlog("A"); syslog.syslog("x"); syslog.closelog()`;
thread B does the same with `"B"`.

**Trigger hypothesis.** A's `closelog` `Py_CLEAR`s `S_ident_o` while B's `syslog` reads it →
data race / use-after-free of the ident object.

**Confidence & dup-check.** Medium. Clearly unlocked globals. Confirm no `PyMutex` was added
(pwd/grp got one; syslog may not). `gh search issues "syslog thread"`.

---

## Site 4 — Process-global extension-module cache `_PyRuntime.imports.extensions`

**Site.** `Python/import.c` uses `#define EXTENSIONS _PyRuntime.imports.extensions` (`:82`); the
cache is a **runtime-global** hashtable of loaded extension defs, consulted/updated by
`_find_cached_def` / `update_global_state_for_extension` on (re)import.

**Reasoning.** Two subinterpreters (or free-threaded threads) importing the same extension
concurrently read/write this shared hashtable during first-load publication.

**Why it fits.** Process-global lookup table with one-time-init/publication under concurrency
(`#140260`-class).

**Reachability.** Multiple threads/subinterpreters simultaneously `import` the same C extension
for the first time (`importlib.reload` to re-trigger, or fresh subinterps).

**Trigger hypothesis.** Concurrent `_find_cached_def` miss → both insert into the shared
hashtable, racing its buckets.

**Confidence & dup-check.** Medium, **dup-risk**: `EXTENSIONS` likely has an
`extensions.mutex`. Verify every access path takes it (the miss→insert window especially).
Compare `#140260`.

---

## Site 5 — `_datetime` C-API capsule / singleton constants one-time init across subinterpreters

**Site.** `Modules/_datetimemodule.c` publishes the `PyDateTime_CAPI` capsule and cached
singletons (`us_per_*`, min/max, epoch) on module init; some are process-global rather than
per-interp.

**Reasoning.** Two subinterpreters initializing `_datetime` concurrently can both run the
lazy-init writer for a shared singleton/capsule with no once-guard → double init / torn pointer.

**Why it fits.** One-time init of process-global tables from concurrent contexts (`#140260`).

**Reachability.** Two subinterpreters (`concurrent.interpreters`) `import datetime`
simultaneously.

**Trigger hypothesis.** Both run the capsule/constant publication; TSan flags the shared write.

**Confidence & dup-check.** Medium. `_datetime` has been partly per-interp'd; confirm which
statics remain shared and unguarded. Compare `#140260`/`#129824`.

---

## Site 6 — `socket.getservbyname` / `getprotobyname` libc static-struct races

**Site.** `socket_getservbyname` / `socket_getprotobyname` (`Modules/socketmodule.c`) call libc
`getservbyname()` / `getprotobyname()`, which return pointers into a per-process static
`servent`/`protoent` that the next call overwrites.

**Reasoning.** Concurrent calls from two threads race the libc static result buffer; CPython
reads `sp->s_port`/`p_proto` after the call with no lock around the static struct.

**Why it fits.** Shared libc static storage read while another context overwrites it (the
`setlocale`/`localeconv` family).

**Reachability.** Two threads loop `socket.getservbyname("http")` /
`socket.getprotobyname("tcp")`.

**Trigger hypothesis.** Thread B's `getservbyname` overwrites the static `servent` while A reads
`sp->s_port` → torn read.

**Confidence & dup-check.** Medium. These libc calls are classically non-reentrant; confirm
CPython doesn't wrap them in a lock (`netdb`-style). Some platforms have `_r` variants —
check which CPython uses.

---

## Site 7 — `time.localtime` / `gmtime` static `struct tm` reuse

**Site.** `time_localtime` / `time_gmtime` (`Modules/timemodule.c`) convert via `localtime`/
`gmtime`, which on platforms without the `_r` variant return a pointer to a shared static
`struct tm`; CPython reads its fields to build the `struct_time`.

**Reasoning.** If the `_r` variant is unavailable (or not used), two threads racing
`localtime()`/`gmtime()` overwrite and read the same static `tm`.

**Why it fits.** Shared static storage across contexts (`#129824` family).

**Reachability.** Two threads loop `time.localtime()` / `time.gmtime()`.

**Trigger hypothesis.** Interleaved fills of the static `tm` → one thread reads fields written by
the other's call.

**Confidence & dup-check.** Low-medium, **platform-dependent**: modern CPython prefers
`localtime_r`/`gmtime_r`. Confirm the build's `#ifdef HAVE_*_R`; only a lead where the non-`_r`
fallback is compiled.

---

## Site 8 — `readline` module global editing state

**Site.** `Modules/readline/readline.c` drives GNU readline through process-global state
(`rl_*` globals, the module's completer/`begidx`/`endidx`, history), none of it lock-protected.

**Reasoning.** readline is fundamentally single-instance/process-global. Concurrent
`readline.get_line_buffer()`/`insert_text()`/`set_completer()` from two threads race the shared
`rl_line_buffer`/completer pointer.

**Why it fits.** Process-global library state accessed from multiple contexts without a protocol.

**Reachability.** Thread A loops `readline.set_completer(f)` / `readline.get_completer()`;
thread B loops `readline.get_line_buffer()`. (Niche; needs the extension built.)

**Trigger hypothesis.** A rebinds the completer object while B reads it → data race / UAF on the
completer.

**Confidence & dup-check.** Low (niche, contract is "not thread-safe"). A race report alone may
be "caller must synchronize"; include only to bound the family.

---

## Site 9 — `_json` C scanner/encoder process-global singletons on cross-subinterp init

**Site.** `Modules/_json.c` `_json` module init builds the C `Scanner`/`Encoder` types and any
module-level singletons; if any speedup table/singleton is process-global rather than per-interp,
concurrent first-import from two subinterpreters races its publication.

**Reasoning.** Same one-time-init hazard as `#140260`: two subinterpreters run the lazy-init
writer for a shared `_json` static with no once-guard.

**Why it fits.** Cross-context one-time init of extension process-global state.

**Reachability.** Two subinterpreters `import json` / `import _json` simultaneously.

**Trigger hypothesis.** Both execute the shared-singleton init; TSan flags the write-write.

**Confidence & dup-check.** Low-medium. Most `_json` state is per-type/per-interp now; confirm
whether any `static` mutable singleton remains. Compare `#140260`.

---

## Site 10 — `_curses` global `SCREEN`/`initialised` window state

**Site.** `Modules/_cursesmodule.c` keeps process-global initialization flags and the shared
`SCREEN`/`stdscr`; window methods and `initscr`/`endwin`/`setupterm` mutate this global state
with no lock.

**Reasoning.** Concurrent curses calls from two threads race the global `initialised` flag and
the shared `SCREEN` pointer (init vs. teardown vs. draw).

**Why it fits.** Process-wide library lifecycle/flag state accessed from multiple contexts
(`#129824` family); teardown-vs-use can also UAF the `SCREEN`.

**Reachability.** Thread A `curses.initscr()`/`endwin()` loop; thread B window draw calls.
Requires a tty/curses env (hard headless).

**Trigger hypothesis.** A's `endwin`/`delscreen` frees `SCREEN` while B draws through it → race /
UAF. (Cf. open curses crash reports #155875/#156946.)

**Confidence & dup-check.** Low (niche, hard to test headless). curses is rarely fuzzed; note the
recent curses crash issues suggest this corner is live.
</content>
