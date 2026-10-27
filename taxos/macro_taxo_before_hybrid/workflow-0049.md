# Concurrent lifecycle-state promotion of shared deduplicated objects races with ownership and reference-count operations

A shared pooled object is promoted to a stronger retention or lifecycle state while concurrent threads still access its ownership, reference-count, or state metadata.

## Precondition

Multiple threads can access the same deduplicated object, and its lifecycle metadata is distributed across state, ownership, and reference-count fields that may be updated by different operations.

## Critical operation

One thread promotes or finalizes the object's lifecycle state and updates its metadata, including retention status and ownership or reference-count representation.

## Interference

Other threads concurrently inspect the lifecycle state or perform reference acquisition, release, or ownership-related operations on that same object, and shared-container publication or lookup may overlap the transition.

## Invalid assumption

The transition is treated as safe even though its metadata updates and reference-count changes are not covered by one synchronization protocol or made consistently atomic.

## Failure

Threads can observe a mixed or stale lifecycle state, perform incompatible reference-count operations, or return an incompletely transitioned object, leading to corrupted ownership or cleanup state, memory-safety failures, or process termination.

## Scope

The reports are all from one concurrent deduplication/interning subsystem and support a pattern about lifecycle-state transitions of shared objects. They do not establish that every reference-count race has this form, nor that every case requires permanent retention specifically.

## Search strategy

1. Inspect shared-object promotion paths for ordinary multi-field stores concurrent with reference acquisition, release, or ownership changes.
2. Check whether lifecycle-state reads and writes use the same lock or atomic access discipline across lookup, publication, and cleanup paths.
3. Search for direct reference-count manipulation in concurrent container transitions and verify that it cannot overlap owner-thread reference operations.
4. Review deduplication or interning code for a window between inserting an object into the shared pool and completing its retention-state transition.

## Evidence

- [#113956](../micro_taxo/gh_113956.md): Shows that promoting a shared object to permanent retention can race with the owning thread's reference-count operations; the fix avoids promotion when ownership state is unsafe and uses atomic metadata stores.
- [#128137](../micro_taxo/gh_128137.md): Shows that a concurrently observed lifecycle-status field itself must use atomic reads and writes when promotion changes the object's retained-state classification.
- [#129701](../micro_taxo/gh_129701.md): Shows that insertion, retention-state promotion, and reference-count adjustment require coordinated locking and thread-safe decrement operations to prevent another thread from observing or using the object during a partially completed transition.
