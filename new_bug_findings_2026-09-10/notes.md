# Audit notes

## Method

1. Read the causal search strategy in `taxos/macro_taxo/workflow-0080.md`.
2. Used documented Python extension behavior as the oracle: `csv.reader`
   consumes an iterator, and `asyncio` task registration maintains internal
   task sets while equality/hash callbacks may execute Python code.
3. Checked candidate issue numbers against `taxos/bugs.txt` and the local
   micro/workflow reports.
4. Checked upstream issue state on 2026-09-10. Both selected reports are
   closed; currently open crash reports such as [#154997](https://github.com/python/cpython/issues/154997)
   and [#155376](https://github.com/python/cpython/issues/155376) were excluded.
5. Ran both minimized scripts with the installed CPython 3.13.3. Each ended
   with signal 11 / shell exit 139.

## Verification limitation

The repository's Dockerfile pins CPython at `f5394c257ce` and enables ASan and
UBSan. The local Docker daemon was not accessible in this session; an approved
Docker invocation was rejected. Therefore the checked-in `sanitizer-output.txt`
files are complete verbatim ASan outputs copied from the linked upstream
reports, while `native-run.txt` records the local native crash checks. No claim
is made that a fresh sanitizer binary was run in this workspace.

## Parent pattern

Both findings inherit from
[`workflow-0080`](../taxos/macro_taxo/workflow-0080.md), whose mechanism is
that a native operation holds borrowed state across a callback that can mutate,
replace, clear, or destroy that state.
