# Concurrent consumers of a shared iterator race traversal-state updates with backing-state ownership or cleanup.

Multiple threads use one stateful or one-shot iterator whose cursor, live traversal resource, cached result, or owned backing object is shared. The reports split into cursor/resource races and one-time ownership races: some permit overlapping traversal or duplicate initialization, while others invalidate or release shared state during another call.

## Precondition

A shared iterator exposes mutable traversal state or a backing resource/reference to concurrent callers without serializing the complete next-operation, including cursor advancement, resource access, exhaustion, and ownership cleanup.

## Critical operation

A worker observes the iterator as available, then reads or advances the shared cursor, traverses the backing state, initializes a shared cached result, or consumes the iterator-owned backing reference.

## Interference

Another worker concurrently performs the same traversal or initialization, reaches exhaustion, closes the live resource, clears the shared owner, or releases the backing object before the first operation has finished.

## Invalid assumption

An availability check is treated as exclusive ownership, cursor check/use/update is treated as one operation, and a borrowed backing pointer or shared cache is assumed to remain valid or to be initialized by only one worker.

## Failure

Cursor races can produce duplicate, skipped, or out-of-bounds results; overlapping resource closure or ownership cleanup can cause stale or freed-state access, double release, refcount corruption, or process termination; concurrent lazy initialization can instead leave duplicate results leaked. These are distinct failure modes rather than one universal outcome.

## Scope

The common pattern is unsynchronized sharing of iterator traversal state plus insufficiently coordinated backing-state lifetime. The reports differ materially: cursor races may yield wrong or out-of-bounds results without freeing memory; resource closure and one-shot exhaustion can invalidate in-flight borrowed state; and lazy cache initialization can leak a duplicate without stale-state access. The pattern does not claim that every shared iterator crashes or that every race involves ownership.

## Search strategy

1. Find shared iterators whose availability check, cursor read, item access, and cursor update are separate unsynchronized operations.
2. Check exhaustion and close paths for an atomic claim or lock that ensures exactly one worker clears and releases iterator-owned backing state.
3. Check that each traversal acquires a strong lifetime guarantee for a backing resource or object before dereferencing it, and retains it until the traversal ends.
4. Check one-shot and lazy-cache initialization paths for atomic consume-or-publish semantics, and verify losing workers dispose of duplicate results without releasing the published value.
5. Check whether a resource-returning operation copies or otherwise protects data before releasing the lock that guards the underlying traversal resource.

## Evidence

- [#73069](../micro_taxo/gh_73069.md): Concurrent iteration could close a shared traversal resource while another worker still used it, while concurrent initialization of per-entry cached state could create duplicate cached objects and leak the loser; the report therefore supports both lifetime/cleanup and non-atomic publication mechanisms.
- [#153928](../micro_taxo/gh_153928.md): Shared sequence iterators had an unsynchronized cursor check/read/increment that could read beyond the sequence, and concurrent exhaustion could release the same backing sequence more than once while another call still accessed it.
- [#154043](../micro_taxo/gh_154043.md): A shared one-shot iterator allowed multiple workers to observe the same owned object, use it, and independently clear and release it, causing double release and use-after-free; an atomic consume fixes this ownership race.
- [#154130](../micro_taxo/gh_154130.md): Concurrent exhaustion of a shared iterator could double-release its single backing-object reference, while a sibling traversal held only a borrowed pointer and continued using the object after it was freed, producing immediate or delayed corruption.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0008](../macro_taxo_before_hybrid/workflow-0008.md)
- [workflow-0163](../macro_taxo_before_hybrid/workflow-0163.md)
