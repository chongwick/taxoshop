# Optimized execution keeps top-of-stack values in registers or another fast cache, then exits to a path that requires canonical stack storage.

A singleton pattern where an optimized execution side exit fails to materialize cached stack state before fallback execution.

## Precondition

An optimized execution path maintains live stack values in a fast cache while fallback execution depends on canonical stack storage.

## Critical operation

Transfer control from optimized execution to fallback execution at a side exit.

## Interference

The side exit updates cache-depth or related metadata without flushing the live cached values into canonical stack storage.

## Invalid assumption

Fallback execution assumes the canonical stack contains the current live values because the exit metadata indicates a valid state.

## Failure

Fallback code consumes missing or stale stack data as a valid value and performs an invalid dereference, terminating the process.

## Scope

This is a cautiously scoped singleton pattern. The evidence supports unsynchronized cached stack state specifically across an optimized-code side exit, not a broader rule about all cache-coherence or fallback failures.

## Search strategy

1. Inspect every optimized-to-fallback side exit and verify that all live cached stack values are materialized before control transfer.
2. Check whether side-exit metadata updates can occur without corresponding writes to canonical stack storage.
3. Trace fallback consumers for unchecked reads of stack slots immediately after optimized execution exits.
4. Add tests that force side exits while top-of-stack values remain cached and verify both state correctness and process survival.

## Evidence

- [#142718](../micro_taxo/gh_142718.md): The report identifies a crash caused by top-of-stack caching that did not save cached registers on side exits; the fix explicitly flushes the stack to memory before transferring control.
