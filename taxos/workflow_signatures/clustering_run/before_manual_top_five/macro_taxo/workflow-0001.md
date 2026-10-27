# Runtime execution state crosses thread or process boundaries without revalidation, causing identity or lifetime failures

Low-level execution state associated with threads, cached identifiers, or fork-sensitive instrumentation is reused after concurrency or process-boundary changes without proving that its owner, identity, and lifetime are still valid. The shared pattern is unsafe state continuity; the concrete mechanisms differ between inherited thread-local state, colliding identifiers used for cache lookup, and sanitizer-sensitive profiling state after duplication.

## Precondition

The runtime maintains execution state whose validity depends on a particular live thread, unique identifier, process image, allocator, or instrumentation environment, while concurrent thread creation or process duplication can change those relationships.

## Critical operation

A thread or child process initializes, retrieves, or re-enters a runtime path using existing thread-associated, identifier-keyed, or fork-sensitive state.

## Interference

Process duplication can preserve state belonging to threads absent from the child; concurrent creation can assign duplicate identifiers and make identifier-keyed caches alias distinct states; or sanitizer instrumentation can expose unsafe interactions between a duplicated child and inherited low-level profiling state.

## Invalid assumption

Previously stored execution state remains uniquely associated with the current live execution context and remains valid across thread creation, identifier reuse, process duplication, and instrumentation-specific runtime changes.

## Failure

The runtime may reject a mismatched state and terminate, return or modify another thread's context, access released or invalid state and crash, or fail intermittently in the duplicated child with a low-level memory-safety fault.

## Scope

This mixed cluster supports an umbrella rule about execution state whose validity is not re-established after concurrency or process-boundary changes. It does not imply one mechanism: the first report concerns inherited stale ownership after fork and identifier reuse, the second concerns concurrent identifier collision and cache aliasing, and the third only establishes a sanitizer-dependent crash in a forked profiling path without identifying the precise invalid state.

## Search strategy

1. Trace every thread-local or identifier-keyed state lookup across process duplication and verify that ownership and provenance are revalidated before reuse.
2. Check all supposedly unique execution-state identifier allocation for atomicity or locking, then verify that caches cannot alias distinct live states on duplicate identifiers.
3. Inspect initialization helpers for set-if-absent behavior when a thread or child may inherit stale state, and require explicit replacement or cleanup where ownership changes.
4. Audit profiling, tracing, unwinding, trampoline, allocator, and signal state used after process duplication, and test those paths under memory-safety instrumentation for intermittent child failures.

## Evidence

- [#54726](../micro_taxo/gh_54726.md): The report establishes that thread-specific values from vanished parent threads could remain visible after process duplication; identifier reuse caused a new child thread to observe the old state, and non-overwriting initialization led to fatal identity validation failure.
- [#83957](../micro_taxo/gh_83957.md): The report establishes that concurrent thread-state creation could produce duplicate supposedly unique identifiers; identifier-based context caching then aliased distinct live states, producing cross-thread context corruption and invalid access or crashes.
- [#109580](../micro_taxo/gh_109580.md): The report establishes that a fork-based low-level profiling or trampoline path crashed randomly in builds using address, memory, or undefined-behavior sanitizers, supporting a separate sanitizer-sensitive failure when inherited instrumentation state is exercised by the child.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0001](../macro_taxo_before_hybrid/workflow-0001.md)
- [workflow-0016](../macro_taxo_before_hybrid/workflow-0016.md)
- [workflow-0041](../macro_taxo_before_hybrid/workflow-0041.md)
