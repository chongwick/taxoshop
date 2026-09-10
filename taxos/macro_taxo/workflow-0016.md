# Concurrent allocation of supposedly unique execution-state identifiers allows a cache keyed by those identifiers to alias distinct live states, causing cross-บ?

When multiple threads create execution state concurrently, an unsynchronized shared identifier allocator can issue duplicates. A cache that uses the identifier as the state’s sole identity then conflates contexts, returning one thread’s state to another; subsequent use can yield incorrect results or access released state and crash.

## Precondition

Multiple threads concurrently create or initialize live execution-state records, and their identifiers are allocated from shared mutable state without synchronization.

## Critical operation

Allocate each state’s identifier through an unsynchronized shared counter or equivalent uniqueness mechanism.

## Interference

Concurrent creators race on the shared allocation, so distinct live states can receive the same identifier; identifier-keyed caching then aliases their state or context.

## Invalid assumption

The identifier is unique and therefore sufficient to identify the owning live state for cache hits and later updates.

## Failure

A thread can read or modify another thread’s state, producing incorrect results; if the aliased cached object is no longer owned or alive, later access can cause use-after-free or a crash.

## Scope

Singleton cluster: this pattern is narrowly supported for concurrent execution-state creation with unsynchronized supposedly unique identifiers and identifier-keyed caching; it does not generalize to all cache races or all identifier reuse without that collision-to-aliasing chain.

## Search strategy

1. Check whether every shared identifier allocation is atomic or protected by the same lock that governs the associated state registry.
2. Check whether a cache treats a numeric or recycled identifier as the sole identity of a live state.
3. Check whether concurrent state creation can assign duplicate identifiers before cache insertion or lookup completes.
4. Check whether cached state references remain valid for the full period in which an identifier can be reused or collide.

## Evidence

- [#83957](../micro_taxo/gh_83957.md): The report documents concurrently created thread states receiving duplicate identifiers because the shared identifier increment was not protected; identifier-based context caching then returned another thread’s context, causing wrong results and, in observed runs, invalid access and crashes.
