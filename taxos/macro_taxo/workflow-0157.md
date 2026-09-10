# Unsynchronized concurrent reinitialization can invalidate a previously checked position before a reader dereferences shared state.

A shared stateful object exposes a reader and a reinitialization path that can run concurrently without one object-level synchronization protocol.

## Precondition

The same object is accessed by multiple threads, and a reader performs a bounds check on mutable state that a reinitializer can change concurrently; the runtime permits these operations to overlap.

## Critical operation

The reader checks whether an index is within a fixed-capacity backing store and, in a separate operation, uses that index to read the corresponding element.

## Interference

A concurrent reinitialization resets or otherwise updates the state, including the checked index, between the reader's validation and its indexed access.

## Invalid assumption

The reader assumes that the index and its relationship to the backing store remain unchanged after the check until the access completes.

## Failure

The reader can dereference outside the valid backing store, causing undefined behavior such as adjacent-memory disclosure or process termination.

## Scope

This cluster contains one detailed underlying vulnerability analysis, so the pattern is scoped to shared state objects where concurrent reinitialization changes reader-relevant bounds or indices between validation and use; it does not establish that every concurrent reset causes an out-of-bounds access.

## Search strategy

1. Check whether any initializer, reset, or reseed path can mutate an index or capacity-related field without acquiring the same synchronization used by readers.
2. Check whether a bounds check and the subsequent indexed access are separated by an unlockable or concurrently interruptible region.
3. Check whether readers and reinitializers of one object use a common object-level lock or an atomic snapshot/versioning protocol.
4. Check reset paths for assignments that move an index to a sentinel or capacity value while another thread may still use a previously validated index.

## Evidence

- [#149816](../micro_taxo/gh_149816.md): The report documents a shared state object whose reader checks an index against capacity, while an unlocked concurrent initializer resets that index before the reader performs the indexed read, producing an out-of-bounds access with possible crash or memory exposure.
