# Pending-error paths must preserve the existing error and still execute required cleanup.

Failure-path control flow mishandles an already-pending or newly-raised error: it either continues into competing diagnostic work or exits before releasing owned intermediate state.

## Precondition

An operation processing invalid input or a failing callback has allocated intermediate data or recorded an error.

## Critical operation

The operation enters recovery, diagnostic construction, or callback/error-return handling.

## Interference

A pending error is ignored, replaced, or causes an early return that bypasses the normal failure cleanup path.

## Invalid assumption

The path assumes it may construct another diagnostic despite an existing error, or that an error-triggered early exit needs no cleanup.

## Failure

The process aborts or dereferences invalid diagnostic state, or owned intermediate data leaks while the intended error is reported.

## Scope

The shared pattern is error-path invariant handling, not parser recovery alone. Diagnostic replacement/source-state crashes are evidenced by three reports; cleanup bypass and leaks are evidenced by two. One leak report has no confirmed root cause, so the pattern does not claim a common allocation mechanism.

## Search strategy

1. Trace every pending-error and callback-failure branch to the common cleanup path before it returns.
2. Reject parser recovery or optional-parse paths that continue after a child has recorded an error.
3. Guard diagnostic construction and replacement so an existing error is preserved rather than overwritten.
4. Audit diagnostic source-location construction for absent or mutated source buffers after recovery.
5. Run malformed-input and failing-callback cases under assertion and leak detectors.

## Evidence

- [#89571](../micro_taxo/gh_89571.md): A lexical error was superseded during a later parse pass, leading structural diagnostic reporting to dereference unavailable source data and crash.
- [#89657](../micro_taxo/gh_89657.md): Optional parsing treated a tokenizer failure as successful and continued into diagnostic handling; the fix propagated the error state and corrected error-source handling.
- [#113602](../micro_taxo/gh_113602.md): A parser diagnostic attempted to overwrite an existing error and triggered an assertion; the fix stopped diagnostic construction when an error was already pending.
- [#139751](../micro_taxo/gh_139751.md): An invalid invocation returned an error while parser-created intermediate data was leaked; the report supplies no confirmed fix and also contains a separately identified unrelated reproducer.
- [#140593](../micro_taxo/gh_140593.md): A callback encountered a pending error and returned before its shared cleanup, leaking caller-owned intermediate data; routing that branch through cleanup fixed it.
