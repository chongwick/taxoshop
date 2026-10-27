# Shared stateful iterator advances or consumes mutable state without making the availability check, use, and exhaustion cleanup one atomic/serialized operation.

Multiple threads share one iterator whose cursor and/or backing-resource ownership is stored in mutable iterator state. Concurrent calls can overlap while consuming the same state.

## Precondition

A single stateful iterator is used concurrently, and its next-item operation reads a live backing object/resource or cursor before synchronizing the operation that advances, exhausts, clears, or releases that state.

## Critical operation

A worker checks that the iterator is available, then retrieves or indexes through the backing state and advances or consumes the iterator-owned state.

## Interference

Another worker concurrently reaches exhaustion or performs the same consume-and-clean-up path, clearing the shared ownership slot and releasing the backing object/resource, or racing the cursor update.

## Invalid assumption

The availability check and the later access or cleanup are treated as if they were indivisible, and cleanup is assumed to be performed by only one worker even though multiple workers can observe the same live state.

## Failure

A worker uses the backing state after it has been released, or multiple workers release the same ownership reference; cursor races can also cause invalid indexing. The result is use-after-free, double release/refcount corruption, out-of-bounds access, and potentially process termination.

## Scope

The shared mechanism is concurrent use of a single stateful iterator with unsynchronized advancement or one-time ownership cleanup. The reports differ in whether the backing state is a native resource, a sequence object, or a one-shot object; the generalization does not require every iterator to be resource-backed or every race to produce a use-after-free.

## Search strategy

1. Find iterators whose next operation checks a non-null/live resource or ownership field and later dereferences it outside the same lock or atomic consume operation.
2. Check whether concurrent exhaustion can clear an iterator-owned backing object and release it more than once.
3. Check cursor bounds tests and cursor increments for a shared iterator that are separate non-atomic operations.
4. Check one-shot iterator paths for a check-then-use-then-clear sequence that should instead atomically claim ownership or hold a critical section through the use.

## Evidence

- [#73069](../micro_taxo/gh_73069.md): Concurrent consumers of one iterator could observe its backing directory resource as available while another consumer exhausted and closed it, allowing retrieval through a released resource; the report also identifies unsynchronized shared-entry caching as a related race.
- [#153928](../micro_taxo/gh_153928.md): Concurrent consumers of one sequence iterator raced both the cursor and exhaustion ownership; one thread could advance the cursor between another thread’s bounds check and read, while multiple threads could release the backing sequence during exhaustion.
- [#154043](../micro_taxo/gh_154043.md): Concurrent consumers of a one-shot iterator could both observe the same owned object, use it, and then clear/release it, producing double release and use-after-free.
