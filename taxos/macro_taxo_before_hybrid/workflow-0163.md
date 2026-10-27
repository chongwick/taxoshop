# Concurrent exhaustion cleanup of a shared iterator releases one owner/reference more than once and can invalidate an overlapping traversal.

A concurrency pattern where shared iterator exhaustion is handled by unsynchronized one-time cleanup while other threads may still be traversing the referenced state.

## Precondition

Multiple threads can advance the same shared iterator concurrently, and its exhaustion state includes a shared owner/reference that is expected to be released once.

## Critical operation

An exhaustion path observes the shared reference, clears it, and releases the referenced traversal state.

## Interference

Concurrent exhaustion paths can observe the same reference before any clear is visible, causing multiple releases; a thread already traversing may retain only a borrowed pointer while another thread performs the release.

## Invalid assumption

A non-null shared reference is assumed to imply exclusive cleanup ownership and continued validity of the referenced state for the entire traversal.

## Failure

Ownership accounting is decremented too far or corrupted, potentially freeing the traversal state while it is still in use; the resulting stale access or later integrity check can crash the process or expose delayed memory corruption.

## Scope

This is a cautiously scoped singleton pattern. The evidence supports unsynchronized one-time exhaustion cleanup combined with borrowed traversal state, but does not establish a broader rule covering all concurrent iterator result races.

## Search strategy

1. Check every shared-iterator exhaustion path for an atomic claim that permits exactly one thread to clear and release the shared owner/reference.
2. Check that a traversal acquires a strong lifetime guarantee before using a shared pointer and releases that guarantee only after the traversal ends.
3. Check whether a failed optimistic lifetime acquisition retries or is incorrectly treated as genuine iterator exhaustion.
4. Check that pointer publication and clearing obey the lifetime-safety requirements of the retain operation used by concurrent readers.

## Evidence

- [#154130](../micro_taxo/gh_154130.md): The report demonstrates that concurrent exhaustion can double-release a single iterator-owned reference, while a sibling traversal still uses the referenced state; it also documents immediate crashes and delayed ownership corruption.
