# Re-entrant CSV iteration dereferences a cleared field list

Parent pattern: [`workflow-0080`](../../taxos/macro_taxo/workflow-0080.md)

Upstream reference: [CPython issue #145105](https://github.com/python/cpython/issues/145105)

## Why this fits the pattern

The [`csv.reader`](https://docs.python.org/3/library/csv.html#csv.reader)
contract consumes an arbitrary iterator. Its `__next__` method can therefore
run Python code and re-enter the same reader. The inner `next(reader)` clears
the reader's current field list; the outer parse resumes and passes the stale
NULL field list to `PyList_Append`.

## Reproduction

```console
$ /opt/homebrew/opt/python@3.13/bin/python3.13 repro.py
Segmentation fault: 11
```

The full script is in [`repro.py`](repro.py). The installed interpreter was
CPython 3.13.3 (Homebrew, Clang 16), and the shell status was 139.

## Deduplication

The issue is absent from the repository corpus and was closed upstream with
linked fixes. It is not an open-issue duplicate as of 2026-09-10. The complete
ASan report posted upstream is preserved in
[`sanitizer-output.txt`](sanitizer-output.txt).

## Impact

An ordinary documented CSV-reader entry point can be driven by a valid custom
iterator whose callback re-enters the reader. The C implementation crashes;
the failure is not a parse error that the caller can catch.
