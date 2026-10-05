# workflow-0077 — Concurrent contexts race on shared process-wide state

> Threads / subinterpreters / free-threaded contexts share libc static return buffers, module
> globals, or process-global library state without a complete synchronization or publication
> protocol.

10 fresh sites (distinct shared-state classes from audit7's `tzname`/`localeconv`/`getserv`/
`localtime`/`syslog`/`extensions`/`_datetime`/`readline`/`_json`/`curses`). **TSan leads** —
build/run the free-threaded TSan image `taxoshop/cpython-tsan-ft:current` (`Py_GIL_DISABLED=1`),
`-e PYTHONMALLOC= -e TSAN_OPTIONS=halt_on_error=1:history_size=7`. "Reachability" is the thread
schedule. Per the audit7 policy note, each of these is a *distinct libc-static / true-global
class*, not "share one object across threads."

---

## Site 1 — `os.strerror` → libc `strerror()` static buffer  ⭐

**Site.** `os_strerror_impl` (`Modules/posixmodule.c:13930`) does `char *message =
strerror(code);` (`:13933`) then `PyUnicode_DecodeLocale(message, ...)`.

**Reasoning.** POSIX `strerror()` returns a pointer to a per-process (or per-locale) static buffer
that a concurrent `strerror()` / `setlocale()` may overwrite; CPython reads/decodes it after the
call with no lock. `strerror_r` is the thread-safe form and is *not* used here.

**Why it fits.** Shared libc static storage read while another context overwrites it (the
`localeconv`/`getserv` `#127081` family, different function).

**Reachability.** Two threads loop `os.strerror(i)` for varying `i` (and/or one thread loops
`locale.setlocale`).

**Trigger hypothesis.** Thread B's `strerror` overwrites the static buffer while A decodes it →
torn/garbage read; TSan flags the write-vs-read on the static.

**Confidence & dup-check.** **Medium.** `git log --grep "strerror.*thread"` — none; the codebase
uses raw `strerror` here (note `_posixsubprocess.c:856` explicitly avoids `strerror` as
non-async-signal-safe, corroborating its non-reentrancy). Confirm no platform maps `strerror` to a
reentrant form. `gh search issues "os.strerror thread"`.

---

## Site 2 — `os.getlogin` → libc `getlogin()` static buffer  ⭐

**Site.** `os_getlogin_impl` (`Modules/posixmodule.c:10119`) calls `name = getlogin();` (`:10156`)
then builds a `str`/`bytes` from it.

**Reasoning.** `getlogin()` returns a pointer to a static buffer overwritten by the next call;
`getlogin_r` is the reentrant form. Concurrent `os.getlogin()` from two threads races the static.

**Why it fits.** libc static return buffer read across contexts without synchronization.

**Reachability.** Two threads loop `os.getlogin()`.

**Trigger hypothesis.** Interleaved `getlogin()` fills → one thread reads the other's overwrite.

**Confidence & dup-check.** **Medium.** `git log --grep "getlogin"` shows only *test* fixes
(#139935/#139322), not thread-safety. Confirm the build compiles the non-`_r` path. `gh search
issues "getlogin thread"`.

---

## Site 3 — `os.ttyname` → libc `ttyname()` static buffer  ⭐

**Site.** `os_ttyname_impl` (`Modules/posixmodule.c:3873`) calls `ttyname(fd)` and decodes the
returned pointer.

**Reasoning.** `ttyname()` returns a pointer to a static buffer; `ttyname_r` is the reentrant
form. Concurrent `os.ttyname(fd)` races the static.

**Why it fits.** libc static return buffer shared across contexts.

**Reachability.** Two threads loop `os.ttyname(0)` / `os.ttyname(1)`.

**Trigger hypothesis.** Interleaved calls overwrite/read the same static path buffer → torn read.

**Confidence & dup-check.** **Medium.** `git log --grep "ttyname"` — none. Confirm non-`_r` path
is compiled. `gh search issues "ttyname thread"`.

---

## Site 4 — `locale.nl_langinfo` mutates process-global locale via `change_locale` + reads a static pointer

**Site.** `_locale_nl_langinfo_impl` (`Modules/_localemodule.c`, `nl_langinfo` calls at `:808`
wide / `:821` narrow) reads the static pointer from `nl_langinfo(item)` and, for non-`LC_CTYPE`
items, calls `change_locale(category, &oldloc)` — which calls **`setlocale`** (process-global) —
around the call.

**Reasoning.** `nl_langinfo()` returns a pointer into locale-owned static storage, and
`change_locale` mutates the process-global locale; two threads racing `nl_langinfo`/`setlocale`
race both the static result and the global locale state.

**Why it fits.** Shared libc static + process-global `setlocale` mutation across contexts.

**Reachability.** Thread A loops `locale.nl_langinfo(locale.ERA)`; thread B loops
`locale.setlocale(...)` / `locale.nl_langinfo(...)`.

**Trigger hypothesis.** B's `setlocale`/`change_locale` rewrites the locale while A dereferences
the `nl_langinfo` static → garbage/torn read.

**Confidence & dup-check.** **DUP-risk — check first.** This is the `setlocale`/`localeconv`
`#127081` family (audit7 FINDING-002). `nl_langinfo`'s `change_locale` was recently touched by
`#152905`/`#133740` (glibc wide-data / ERA), but for *correctness*, not thread-safety. Confirm
whether the `#127081` locale-lock (if any) covers `nl_langinfo`; only a genuinely uncovered path
is new.

---

## Site 5 — `os.putenv` / `os.unsetenv` vs `getenv` readers race the `environ` array  ⭐

**Site.** `os_putenv_impl` (`Modules/posixmodule.c:13806`) and `os_unsetenv_impl` (`:13859`,
`unsetenv(...)` at `:13884`) mutate the process `environ`; many code paths (and libc internals)
read it via `getenv()` (e.g. `getpath.c:707`, tz handling).

**Reasoning.** `putenv`/`setenv`/`unsetenv` reallocate/rewrite the `environ` array with no lock,
while a concurrent `getenv()` (in CPython or libc) walks it → classic `environ` data race /
use-after-free of a freed `environ` slot.

**Why it fits.** True process-global (`environ`) mutated and read from multiple contexts without a
common protocol (`#129824`-class).

**Reachability.** Thread A loops `os.putenv("K","V")` / `os.unsetenv("K")`; thread B loops
`os.environ.get("K")` / anything calling `getenv`.

**Trigger hypothesis.** A's `unsetenv` frees/shifts the `environ` entry while B's `getenv` reads
it → UAF / torn pointer; TSan flags the write-vs-read on `environ`.

**Confidence & dup-check.** **Medium.** `git log --grep "putenv.*thread\|environ.*race"` — none.
`environ` races are a well-known libc hazard; confirm CPython adds no guard here. `gh search
issues "os.environ thread getenv"`.

---

## Site 6 — `_gdbm` module-global `gdbm_errno` + `gdbm_strerror()` static  ⭐

**Site.** `Modules/_gdbmmodule.c` reads the process-global `gdbm_errno` (`:336`) and formats via
`gdbm_strerror(gdbm_errno)` (`:47`) on error paths.

**Reasoning.** `gdbm_errno` is a single process-global set by the last gdbm call; `gdbm_strerror`
returns static storage. Concurrent gdbm operations from two threads race `gdbm_errno` and the
strerror static → wrong/torn error messages and a data race.

**Why it fits.** Library process-global error state + static return buffer across contexts
(`#129824`-class).

**Reachability.** Two threads operate on gdbm databases (open/fetch/store) so their error paths
interleave on `gdbm_errno`. (Requires the `_gdbm` extension built — present in this image.)

**Trigger hypothesis.** Thread A's failing op sets `gdbm_errno`; thread B reads it for its own
(different) failure → race + misattributed error.

**Confidence & dup-check.** **Low-medium (niche).** `git log --grep "gdbm_errno"` — none. gdbm is
rarely fuzzed for threads. Confirm no module mutex wraps the gdbm call + `gdbm_errno` read. Same
class applies to `_dbm` (`dbm_error`/`dbm_clearerr`).

---

## Site 7 — `socket.gethostbyname` / `gethostbyname_ex` libc static `hostent`

**Site.** `_socket_gethostbyname` (`Modules/socketmodule.c:6058`) calls `gethostbyname(name)`
(`:6309`), which returns a pointer into a per-process static `hostent`.

**Reasoning.** `gethostbyname`/`gethostbyaddr` are classically non-reentrant; two threads racing
them would race the static `hostent`.

**Why it fits.** Shared libc static storage across contexts.

**Reachability.** Two threads loop `socket.gethostbyname("localhost")`.

**Confidence & dup-check.** **Low (ruling-out).** Verified guarded: socketmodule defines
`USE_GETHOSTBYNAME_LOCK` (`:205`) and takes `netdb_lock` (`PyMutex netdb_lock`, `:1195`) around
the call (`PyMutex_Lock(&netdb_lock)` at `:6305`). So the static is serialized *within CPython*.
Documented to show the correct pattern; cross off unless a platform compiles it out.

---

## Site 8 — `faulthandler` process-global dump/handler state  ⭐

**Site.** `Modules/faulthandlermodule.c` keeps process-global state (the `fatal_error` struct,
`thread` cancel/timeout state, `user_signals` table, saved handlers) mutated by
`faulthandler.enable()`/`disable()`/`dump_traceback_later()`/`cancel_dump_traceback_later()` and
read by the signal/watchdog paths.

**Reasoning.** These globals are updated with signal-level or ad-hoc synchronization; concurrent
`enable`/`disable`/`dump_traceback_later` from multiple threads (or a watchdog thread reading
while the main thread reconfigures) race the shared handler table / timeout thread state.

**Why it fits.** Process-global library lifecycle/flag state accessed from multiple contexts
(`#130605`/`#153014` config-flag-race class), with a watchdog-vs-reconfigure teardown angle.

**Reachability.** Thread A loops `faulthandler.dump_traceback_later(0.001);
faulthandler.cancel_dump_traceback_later()`; thread B loops `faulthandler.enable()/disable()`.

**Trigger hypothesis.** A reconfigures the timeout thread while B disables faulthandler, racing
the shared `thread`/`fatal_error` state → TSan report (and potential UAF on the file/handler).

**Confidence & dup-check.** **Low-medium.** faulthandler is intended to be low-level and lightly
synchronized. `git log --grep "faulthandler.*race\|faulthandler.*thread"` — none. Confirm which
globals lack atomic/locked access. `gh search issues "faulthandler thread race"`.

---

## Site 9 — `signal` module global `Handlers[]` / `is_tripped` table

**Site.** `Modules/signalmodule.c` maintains the process-global `Handlers[NSIG]` array and the
`is_tripped` flag / pending table, written by `signal.signal()`/`siginterrupt()` and read by the
trip/`PyErr_CheckSignals` path.

**Reasoning.** Although Python-level `signal.signal()` is restricted to the main thread, the
handler *objects* in `Handlers[]` are read from the signal-handling path while the main thread
reassigns them; free-threaded builds widen the window for racing the handler-object pointer
(read-vs-store) and `is_tripped`.

**Why it fits.** Process-global table with read-vs-store across contexts without full
synchronization (`#153014`/#153852 residual-race class).

**Reachability.** Main thread loops `signal.signal(signal.SIGUSR1, h1/h2)` while another context
triggers/handles signals (`signal.raise_signal(SIGUSR1)`); free-threaded build.

**Trigger hypothesis.** The trip path reads `Handlers[SIGUSR1].func` while the main thread stores
a new handler (dropping the old one's ref) → data race / UAF on the handler object.

**Confidence & dup-check.** **Low (main-thread caveat).** `signal.signal` off the main thread
raises, limiting reachability; the race needs the C trip path vs. main-thread store. `git log
--grep "signal.*race\|Handlers\["`. Confirm atomic access to `Handlers[].func`. `gh search issues
"signal handler race free-threading"`.

---

## Site 10 — `os.forkpty` / `os.openpty` → `ptsname()` static buffer

**Site.** `Modules/posixmodule.c` pty helpers use `ptsname()` (returns a pointer to a static
name buffer) when deriving the slave device name (grep `ptsname` in `posixmodule.c`).

**Reasoning.** `ptsname()` is non-reentrant (static buffer); `ptsname_r` is the safe form.
Concurrent pty allocation from two threads races the static name.

**Why it fits.** libc static return buffer shared across contexts.

**Reachability.** Two threads loop `os.openpty()` (each derives the slave name).

**Trigger hypothesis.** Interleaved `ptsname()` calls overwrite/read the same static → wrong/torn
device name; TSan flags the static access.

**Confidence & dup-check.** **Low-medium.** Verify whether CPython uses `ptsname` vs `ptsname_r`
or fills the name itself. `git log --grep "ptsname\|openpty"` / `gh search issues "openpty
thread"`.
</content>
