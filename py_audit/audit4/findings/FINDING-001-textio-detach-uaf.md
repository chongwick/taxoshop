# FINDING-001: Heap use-after-free in `io.TextIOWrapper` read path via reentrant `detach()`

- **Parent pattern:** `workflow-0137` — *Reentrant user-code execution invalidates
  native state before later use* (macro_taxo). Closely related to `workflow-0014`
  (*retained pointer dereferences storage after its owner releases it*): the retained
  **borrowed** `self->buffer` reference is used across a user-code boundary that drops
  the buffer's last reference.
- **Component:** `Modules/_io/textio.c` (root cause) — crash manifests in
  `Modules/_io/bufferedio.c`.
- **Type:** Heap use-after-free (WRITE). Reachable from pure Python. `type-crash` /
  memory-safety. **No ctypes.**
- **Confirmed on:** CPython `3.16.0a0`, `origin/main` @
  `e5d4fa281c573b764b827f3defae260787024e43`. ASan+UBSan build
  (`taxoshop/cpython-asan-ubsan:current`, `--without-pymalloc`, `PYTHONMALLOC=malloc`).
- **Duplicate check:** Believed **new / not a duplicate** (see "Duplicate analysis").

## Root cause

`TextIOWrapper` reaches its underlying buffered object through a **borrowed** reference.
`buffer_access_safe()` (`textio.c:740`) returns `self->buffer` without incrementing its
refcount, with the comment:

```c
/* Returning a borrowed reference is safe since TextIOWrapper methods are
   protected by critical sections. */
_Py_CRITICAL_SECTION_ASSERT_OBJECT_LOCKED(self);
return self->buffer;
```

Critical sections serialize *concurrent* (multi-threaded) access; they do **not**
prevent single-threaded **reentrancy**. The helpers built on it immediately call a
method on that borrowed object, e.g. `buffer_callmethod_noargs` (`textio.c:774`):

```c
PyObject *buffer = buffer_access_safe(self);   // borrowed, refcount NOT incremented
if (buffer == NULL) return NULL;
return PyObject_CallMethodNoArgs(buffer, name); // outbound call into borrowed object
```

`TextIOWrapper.read()` (`_io_TextIOWrapper_read_impl`, `textio.c:2083`) calls
`self->buffer.read()` this way. The buffered object's C `read_impl` in turn runs the raw
layer's `readinto()`, which is **arbitrary user code**. If that user code calls
`TextIOWrapper.detach()`, `detach()` does:

```c
self->buffer = NULL;   // clears TextIOWrapper's only reference to the buffer
... returns the buffer to the caller (ownership transferred)
```

When the returned buffer is dropped (a bare `tw.detach()` statement), the buffered
object's refcount reaches **zero** and it is freed by `buffered_dealloc`
(`bufferedio.c:444`) — **while its own C `read_impl` is still on the stack**. C stack
frames receive `self` as a borrowed argument and hold no reference of their own, so
nothing keeps the object alive. On return up the stack, `_io__Buffered_read_impl`
(`bufferedio.c:1022`) / `_bufferedreader_raw_read` (`bufferedio.c:1667`) write through
the freed `self` → **heap use-after-free**.

`gh-143008` (which introduced `buffer_access_safe`) only hardened TextIOWrapper's
re-access of `self->buffer` *after* a callback returns (it NULL-checks and raises
`ValueError: underlying buffer has been detached`). It does **not** keep the buffer
object alive *during* the outbound call, so a reentrant `detach()` that drops the last
reference still frees the object mid-call.

## Reproducer (canonical — `repro/textio_detach_uaf.py`)

```python
import io

class EvilRaw(io.RawIOBase):
    def readable(self):
        return True
    def readinto(self, b):
        tw.detach()          # drops the last ref to the BufferedReader mid-read
        b[:3] = b"abc"
        return 3

tw = io.TextIOWrapper(io.BufferedReader(EvilRaw()), encoding="utf-8")
tw.read()
```

### Sanitizer output (`logs/textio_detach_uaf_read.asan.txt`)

```
==1==ERROR: AddressSanitizer: heap-use-after-free on address 0x50f000038a60 ...
WRITE of size 8 at 0x50f000038a60 thread T0
    #0 _io__Buffered_read_impl Modules/_io/bufferedio.c:1022
    #5 buffer_callmethod_noargs Modules/_io/textio.c:781
    #6 _io_TextIOWrapper_read_impl Modules/_io/textio.c:2083
0x50f000038a60 is located 128 bytes inside of 168-byte region ...
freed by thread T0 here:
    #1 buffered_dealloc Modules/_io/bufferedio.c:444
    ...
    #11 _io__RawIOBase_read_impl Modules/_io/iobase.c:936     (raw readinto -> user code)
    ...
    #28 _io_TextIOWrapper_read_impl Modules/_io/textio.c:2083
SUMMARY: AddressSanitizer: heap-use-after-free Modules/_io/bufferedio.c:1022 in _io__Buffered_read_impl
```

## Scope

All confirmed under the same build; each in its own process:

| Entry point | Result | Crash site |
|---|---|---|
| `TextIOWrapper.read()`        | **UAF** | `bufferedio.c:1022` (`_io__Buffered_read_impl`) |
| `TextIOWrapper.readline()`    | **UAF** | `bufferedio.c:1667` (`_bufferedreader_raw_read`) |
| `TextIOWrapper.read(n)`       | **UAF** | `bufferedio.c:1667` (`_bufferedreader_raw_read`) |
| `TextIOWrapper.write()`+flush | no crash | write path does not re-touch a freed buffer here |
| `TextIOWrapper.seek/tell/truncate` | no crash | buffered reentrancy guard raises `RuntimeError` first |

### Control — root-cause confirmation (`repro/textio_detach_control_keep_alive.py`)

If the reentrant callback **keeps the detached buffer alive**
(`saved.append(tw.detach())`), there is **no crash**: `TextIOWrapper` then raises the
expected `ValueError: underlying buffer has been detached` (the `gh-143008` guard). This
isolates the defect to the buffer object being *freed* while its C method is in flight —
i.e. the missing strong reference across the outbound call, not the detach itself.

## Suggested fix direction

Hold a strong reference to `self->buffer` for the duration of every outbound call, e.g.
have `buffer_callmethod_noargs` / `buffer_callmethod_onearg` / `buffer_getattr`
`Py_INCREF` the result of `buffer_access_safe()` and `Py_DECREF` it after the call
(mirroring the standard `workflow-0137` remedy of acquiring a lifetime-preserving
reference across a reentrant boundary). The existing post-call NULL revalidation via
`buffer_access_safe()` remains necessary and correct for detach-without-free.

## Duplicate analysis

- **`gh-153539` / consolidated report #157197 entry 93** — `TextIOWrapper.tell()`
  reentrant *snapshot* release (decoder re-enters `seek()`). Already fixed; different
  state (decoder snapshot) and code path. Not this bug.
- **#154997 (OPEN)** — "NULL pointer dereference in BufferedIO methods after re-entrant
  detach()". Different mechanism and crash class: a `BufferedIO` subclass calls its
  **own** `detach()`, NULLing `self->raw`; `bufferedio.c` then dispatches through the
  NULL `self->raw` (NULL deref, SEGV at offset `0x8`). Here, `TextIOWrapper.detach()`
  **frees the buffer object itself** (a heap **use-after-free**), because
  `textio.c` held only a borrowed reference. Different detach target
  (`TextIOWrapper` vs the buffered object), different fault (UAF of `self` vs
  NULL-deref of `self->raw`), different fix location (`textio.c` strong-ref vs
  `bufferedio.c` re-validation).
- **#154523 (CLOSED)** — free-threading *data race* on the non-atomic
  `self->buffer = NULL` store. Different (concurrency; this finding is single-threaded).
- **#157335** — mmap `__setitem__` reentrant resize; unrelated module.

No open/closed issue found describing the `TextIOWrapper` borrowed-`self->buffer`
use-after-free on the read path.
