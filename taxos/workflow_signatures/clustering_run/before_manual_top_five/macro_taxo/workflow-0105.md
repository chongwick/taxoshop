# Concurrent operations access coupled shared state without synchronizing the complete state transition

Free-threaded workers concurrently read or update related counters, thresholds, collection metadata, or iterator cursors, but synchronization covers only individual fields or an enclosing object rather than the full logical state transition.

## Precondition

The same runtime-owned state is reachable by multiple threads, and its meaning depends on coupled fields, shared collection state, exhaustion/lifecycle state, or pointer-bearing traversal slots.

## Critical operation

A thread performs a collection-accounting update or decision, advances a stateful iterator, computes iterator metadata, or reads dependent fields using plain or only partially compatible synchronization.

## Interference

Another thread concurrently updates related counters or collection contents, advances or exhausts the same iterator, or interleaves another part of the same multi-field transition, allowing a partially updated combination to be observed.

## Invalid assumption

Atomic access to one field, locking only the backing collection, immutability of the underlying structure, borrowed-reference reachability, or the former global interpreter lock was assumed to serialize the complete operation and keep dependent fields mutually consistent.

## Failure

Race instrumentation reports conflicting accesses; collection decisions can use inconsistent accounting, iterator results can be skipped, duplicated, or prematurely exhausted, and a desynchronized cursor can cause an invalid null or wild-pointer dereference and crash. The evidence does not require an ownership leak or actual freed storage.

## Scope

This mixed cluster shares incomplete synchronization of coupled concurrent state, but the mechanisms differ: accounting races can yield bad decisions, collection/iterator races can yield inconsistent traversal state, and the multi-field cursor race can crash through a logically stale or null pointer without any concurrent structural mutation. The reports do not establish a general rule about leaked ownership or freed storage.

## Search strategy

1. Search for shared counters, thresholds, flags, cursors, indexes, and pointer slots whose meaning depends on other fields; verify that one synchronization protocol covers the complete logical update and read.
2. Check atomic and non-atomic accesses to the same state, including diagnostic, length, exhaustion, and decision paths, and require compatible ordering or a common lock.
3. Trace iterator advancement across every descent, ascent, exhaustion, and reference-slot update; ensure another caller cannot observe a partially updated cursor.
4. Check whether protecting a backing collection leaves iterator-local state, collection metadata, or lifecycle transitions concurrently accessible through aliases.
5. Stress shared iterators and accounting paths alongside mutation, exhaustion, and concurrent allocation under race and memory-safety instrumentation.

## Evidence

- [#133473](../micro_taxo/gh_133473.md): Concurrent allocation and collection activity accessed shared accounting counters and collection thresholds through mixed atomic and plain operations, producing race reports and potentially inconsistent collection-trigger decisions.
- [#144356](../micro_taxo/gh_144356.md): Iterator metadata and advancement raced with concurrent collection mutation, exhaustion, and other calls on the same iterator; synchronizing only part of the state left dependent length, cursor, and exhaustion fields exposed.
- [#154535](../micro_taxo/gh_154535.md): Concurrent advancement of one iterator interleaved updates to a multi-field traversal cursor containing borrowed node pointers; the underlying structure was immutable, yet cursor desynchronization led to a null or wild-pointer dereference and crash.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0077](../macro_taxo_before_hybrid/workflow-0077.md)
- [workflow-0081](../macro_taxo_before_hybrid/workflow-0081.md)
- [workflow-0164](../macro_taxo_before_hybrid/workflow-0164.md)
