# Concurrent identity allocation breaks caches that use the allocated identifier to validate per-execution state.

A shared counter assigns identifiers to concurrently created execution states without synchronization, allowing distinct live states to receive the same identifier. A cache keyed or validated by that identifier can then return one state’s cached context to another.

## Precondition

Multiple execution states can be created concurrently, and a shared identifier is used by a per-state context cache or cache-validation fast path.

## Critical operation

Create an execution state and allocate its identifier by incrementing the shared counter.

## Interference

Concurrent creations race during allocation and assign the same identifier to different live states; a later cache lookup or update can select the context cached for the other state.

## Invalid assumption

The allocated identifier uniquely and permanently distinguishes every live execution state, so matching identifiers prove that a cached context belongs to the current state.

## Failure

The affected execution state uses an invalid or foreign cached context, producing incorrect state-dependent results or dereferencing an object whose owner has released it, causing a crash.

## Scope

Singleton cluster: this pattern is limited to caches whose correctness depends on uniqueness of identifiers allocated during concurrent execution-state creation.

## Search strategy

1. Find shared execution-state identifier counters incremented without a lock or atomic operation.
2. Audit per-state cache keys and fast paths that use a numeric identifier as the sole ownership or identity check.
3. Verify that identifier allocation is synchronized across every concurrent state-creation path.
4. Stress concurrent creation and teardown of execution states while exercising cached context lookup and update paths.

## Evidence

- [#83957](../micro_taxo/gh_83957.md): Concurrent creation assigned duplicate execution-state identifiers; context caching confused the colliding states, yielding another state’s context, incorrect results, invalid cached objects, and crashes. Synchronizing identifier allocation fixed the issue.
