# Concurrent non-atomic mutation or initialization of concurrency-visible object metadata races with ownership and lifecycle inspection

A shared or newly reachable object exposes ownership, reference-count, lifecycle, or validity metadata to concurrent threads while another operation changes multiple metadata fields or bulk-initializes storage. The cluster covers two related mechanisms: lifecycle promotion can overlap owner reference-count activity or publication, while allocation-time bulk clearing can overlap lock-free header inspection.

## Precondition

An object can be reached or inspected concurrently, and its concurrency-visible metadata is accessed through a mixture of ordinary stores, atomic operations, locks, or bulk memory writes that are not governed by one consistent synchronization protocol.

## Critical operation

One thread either promotes the object to a stronger retention state while rewriting ownership or reference-count metadata, or initializes an allocation by bulk-clearing memory that includes the object header before explicit header initialization is complete.

## Interference

During that operation, another thread may acquire or release references, inspect ownership or lifecycle state, observe the object through a shared pool, or perform lock-free validation of the header.

## Invalid assumption

The implementation assumes that same-thread completion of initialization, atomicity of individual readers, or later correction of metadata makes the transition safe, even though non-atomic multi-field updates or byte-wise bulk writes can overlap concurrent metadata access.

## Failure

Observers can see mixed, transient, or inconsistent ownership, reference-count, retention, or validity metadata, causing incorrect lifecycle decisions, corrupted reference state, a real data race, memory-safety failure, or process termination. The reports do not establish that the common failure must involve stale or freed state.

## Scope

This mixed cluster supports an umbrella pattern about unsynchronized writes to concurrency-visible object metadata. Issues 113956, 128137, and 129701 concern pooled-object publication and retention-state promotion; issue 130019 concerns allocation-time bulk initialization of headers. The evidence does not support conflating leaked ownership with stale or freed state, nor claiming that every reference-count race or allocator memset has this form.

## Search strategy

1. Inspect shared-object retention or lifecycle-promotion paths for non-atomic writes to ownership, reference-count, or state fields that can overlap owner-thread reference operations.
2. Check that publication, lookup, promotion, and cleanup of pooled objects use one compatible lock or atomic-access discipline, and that reference-count adjustments are thread-safe.
3. Search allocation and reuse paths for memset, zeroing, or other bulk writes that cover concurrency-visible headers before those headers are initialized.
4. Verify that lock-free readers cannot inspect header metadata during bulk initialization, and that fields read atomically are also written atomically or protected by the same synchronization protocol.

## Evidence

- [#113956](../micro_taxo/gh_113956.md): Shows that promoting an object owned by another thread can race with that owner's reference-count operations; safe handling requires ownership or merged-reference checks and atomic stores for metadata observed concurrently.
- [#128137](../micro_taxo/gh_128137.md): Shows that a lifecycle-classification field changed during retention promotion must use atomic reads and writes when other threads can inspect it.
- [#129701](../micro_taxo/gh_129701.md): Shows that insertion, promotion, and reference-count adjustment need coordinated locking and thread-safe decrements so another thread cannot observe or use an object during a partially completed transition.
- [#130019](../micro_taxo/gh_130019.md): Shows that non-atomic full-allocation clearing can race with concurrent reads of ownership and reference metadata, including transient header values that appear valid or match another thread.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0049](../macro_taxo_before_hybrid/workflow-0049.md)
- [workflow-0079](../macro_taxo_before_hybrid/workflow-0079.md)
