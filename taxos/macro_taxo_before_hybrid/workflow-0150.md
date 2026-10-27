# unserialized inspection of a concurrently changing container

A lock-free inspection path reads container metadata or backing storage while the container is still being built or concurrently resized, cleared, or otherwise structurally modified.

## Precondition

A container can become visible to another thread before construction is complete, or can be structurally mutated concurrently with readers in a free-threaded execution model.

## Critical operation

A reader performs a size, memory-footprint, representation, hash, or similar inspection by directly reading internal counters or walking backing storage without synchronizing the complete representation.

## Interference

The writer changes the inspected counter, capacity, table, or backing-storage pointer, including reallocating or clearing storage, while the reader accesses related state.

## Invalid assumption

Treating the container as immutable or stable based on its public type or intended steady-state semantics—and making only an individual scalar read atomic—is assumed to make the whole inspection safe, even though publication may precede initialization and related metadata and storage are not protected together.

## Failure

The access is a data race and may yield transient or inconsistent observations, sanitizer reports, or invalid storage access and a crash; for an object intended to be immutable, readers may also observe construction-time contents.

## Scope

The reports support a pattern about concurrent inspection during construction or structural mutation, especially in free-threaded runtimes. They do not show that every lock-free read is unsafe: safety can hold after publication is complete when the representation is genuinely immutable, or when the read protocol and publication mechanism protect all related state.

## Search strategy

1. Check whether every read-only size, footprint, representation, or hash path is synchronized with concurrent structural mutation.
2. Trace object publication and reachability to verify that no partially initialized container can be discovered by another thread.
3. Audit lock-free readers for coupled reads of counters, capacity, table pointers, and backing arrays whose updates are not protected by one common protocol.
4. Check resize, clear, and empty-state transitions for writes that race with inspection reads or can invalidate a storage pointer after it is observed.

## Evidence

- [#145036](../micro_taxo/gh_145036.md): A footprint query atomically read a capacity field while concurrent append/pop operations updated capacity during resize and clearing; the unsynchronized field access triggered a ThreadSanitizer race, and an attempted direct capacity lookup could dereference cleared storage.
- [#151722](../micro_taxo/gh_151722.md): A supposedly immutable mapping was discoverable while construction was still inserting and resizing entries; concurrent length, representation, and hash reads accessed counters and the entry table without synchronization, producing races and observations of a changing object.
