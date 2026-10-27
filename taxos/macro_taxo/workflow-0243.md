# Concurrent evaluation loses shared interrupt state

Multiple execution contexts concurrently perform evaluations that update shared process-wide state recording an unhandled interrupt. One context records the interrupt, while another evaluation clears the same shared state as part of its own initialization. The unsynchronized updates race, allowing the clearing operation to erase the other context’s indication. A later termination check reads the cleared state and fails to handle the pending interrupt correctly.

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

- [#128130](../micro_taxo/gh_128130.md): One concurrent evaluation records pending interrupt state while another evaluation resets the same process-wide marker during setup, so unsynchronized reset loses state.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0075](../macro_taxo_before_hybrid/workflow-0075.md)
