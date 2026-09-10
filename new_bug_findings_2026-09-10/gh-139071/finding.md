# Recursive set insertion corrupts deallocation accounting

Parent pattern: [`workflow-0080`](../../taxos/macro_taxo/workflow-0080.md)

Upstream reference: [CPython issue #139071](https://github.com/python/cpython/issues/139071)

## Why this fits the pattern

The documented object model permits `__hash__` and `__eq__` to execute Python
code. The reproducer makes equality re-enter `_asyncio._register_task()` while
the outer set insertion still holds its collision-table bookkeeping. Recursive
failure unwinding reuses the same dummy slot and increments `used` repeatedly.
Later set destruction trusts the corrupted count and reads beyond the allocated
table.

## Reproduction

```console
$ /opt/homebrew/opt/python@3.13/bin/python3.13 repro.py
Segmentation fault: 11
```

The full script is in [`repro.py`](repro.py). The installed interpreter was
CPython 3.13.3 (Homebrew, Clang 16), and the shell status was 139.

## Deduplication

The issue is absent from the repository corpus and was closed upstream. It is
not an open-issue duplicate as of 2026-09-10. The complete sanitizer report
posted upstream is preserved in [`sanitizer-output.txt`](sanitizer-output.txt).

## Impact

A pure-Python callback sequence can corrupt a native set and terminate the
interpreter during finalization. The trigger uses `_asyncio`'s private
registration helper to reach the relevant internal set; the memory-safety
failure is in the native set insertion/deallocation invariant.
