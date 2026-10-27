# Exceptional exits bypass cleanup for partially acquired ownership

A routine acquires owned references or temporary allocations before a multi-stage operation completes, but some exceptional or validation exits bypass the release logic.

## Precondition

A function establishes ownership of a resource or temporary reference before subsequent conversion, compilation, iteration, or optimized execution has finished.

## Critical operation

A later stage can fail after that ownership is established, including recoverable exceptions, validation failures, or compilation errors that preserve an error state without following the ordinary return path.

## Interference

Control flow returns, jumps, or transfers into another execution path before a unified cleanup block runs, or cleanup is incorrectly delegated to a later stage that is never reached.

## Invalid assumption

The implementation assumes every failure reaches the same cleanup point or uses one specific failure sentinel, overlooking exceptional paths that retain ownership while bypassing that cleanup.

## Failure

The owned reference or allocation remains live after the operation fails; repeated failures accumulate unreclaimed objects and produce reference-count or leak-detector reports.

## Scope

The reports share an exceptional-control-flow and ownership-cleanup mechanism across different subsystems. They do not establish that every leak involves garbage-collector registration, compilation, or generated code; those are implementation-specific variants.

## Search strategy

1. Trace every owned reference or temporary allocation from acquisition through all returns, gotos, exception transfers, and handoffs.
2. Check whether conversion, compilation, validation, or iterator failures can occur after ownership is acquired but before the common cleanup block.
3. Verify that cleanup is centralized or explicitly executed on recoverable exceptions, not only on success and one designated null or fatal path.
4. Inspect generated wrappers and helper callees for mismatched ownership conventions when a conversion succeeds but a later argument or operation fails.
5. Exercise each exceptional branch repeatedly with mortal or uniquely allocated objects and compare reference counts or allocation totals.

## Evidence

- [#139540](../micro_taxo/gh_139540.md): An execution object acquired an owned reference before compilation and optimized execution completed; compilation failure and an exception-bearing optimized exit could bypass the decrement, leaving the object allocated.
- [#139748](../micro_taxo/gh_139748.md): Argument conversion created a strong reference, but later conversion failures could exit the generated wrapper before the implementation-level cleanup ran, leaking the converted object.
- [#139749](../micro_taxo/gh_139749.md): A recoverable runtime exception during optimized execution reproduced an unreclaimed execution object allocated along the optimized path, consistent with exceptional exit bypassing ownership release.
- [#140517](../micro_taxo/gh_140517.md): An iterator-processing routine accumulated temporary item references, then strict-mode validation errors returned before the shared cleanup released the already acquired items.
