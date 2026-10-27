# Concurrent handshake cleanup double-frees shared native state

Two worker threads initiate overlapping secure handshakes through shared native connection state. One handshake encounters a cleanup path that releases an internal allocation while the other handshake still references or owns it. The second handshake later performs its own cleanup on the same allocation without coordinated ownership or lifetime protection. The allocation is released twice, and memory-safety instrumentation aborts the process instead of allowing both handshakes to finish safely.

## Precondition

Shared mutable execution or native state is reachable by concurrent readers, writers, resetters, consumers, native calls, or cleanup paths.

## Critical operation

An operation reads, updates, publishes, consumes, validates, dereferences, or cleans up shared state while requiring coherent contents, stable lifetime, or exclusive ownership.

## Interference

Another operation concurrently writes, resets, replaces, resizes, clears, reinitializes, enters the same native context, or releases related state without the same effective synchronization, atomic publication, lifetime rule, or ownership protocol.

## Invalid assumption

A runtime guard, timing delay, one-sided atomicity, prior bounds check, borrowed reference, partial critical section, isolation boundary, or presumed exclusive cleanup is assumed to serialize all relevant accesses and preserve state or ownership.

## Failure

The overlap can produce a sanitizer-reported race, lost or contradictory state, invalid intermediate observations, out-of-bounds access, stale or freed-state use, double release, corruption, native-library failure, or a crash.

## Scope

Membership was manually restricted to the evidence listed below. This subgroup covers the single mechanism described by its member evidence.

## Search strategy

1. Search for shared mutable records, flags, pointers, containers, buffers, descriptors, registries, and native contexts reached by multiple threads; identify every reader, writer, resetter, and cleanup path.
2. Check that all related reads, writes, check-and-update sequences, and dependent fields use one complete synchronization or atomic-publication protocol, including test, debug, and representation paths.
3. Trace borrowed references, exported buffers, replaceable objects, resized storage, and native allocations to verify stable lifetime through the full use and exclusive or reference-counted cleanup.
4. Check whether locks or runtime guards are suspended or released during native calls, polling, callbacks, or blocking regions while the shared state remains in use.
5. Stress concurrent initialization, reconfiguration, reset, mutation, handoff, invocation, shutdown, and cleanup under race and memory-safety instrumentation.

## Evidence

- [#140608](../micro_taxo/gh_140608.md): Concurrent native handshake paths can both reach cleanup for the same allocation, supporting a distinct shared-lifetime and cleanup-ownership failure that manifests as double release.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0107](../macro_taxo_before_hybrid/workflow-0107.md)
