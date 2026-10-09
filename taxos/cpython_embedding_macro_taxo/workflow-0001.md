# Stale thread-local state survives process duplication and is mistaken for a newly created thread's state after native thread-identifier reuse.

A child created from a multithreaded process can retain thread-local associations belonging to parent threads that do not exist in the child. If a subsequently created child thread reuses such an identifier, initialization may preserve the stale association and later retrieve state for the wrong thread.

## Precondition

A multithreaded process stores thread-specific execution state in TLS, and the platform's TLS behavior can retain associations across process duplication for threads absent from the child.

## Critical operation

The process is duplicated, then the child creates a thread and initializes its per-thread execution state.

## Interference

The new child thread reuses an identifier associated with a vanished parent thread, causing TLS lookup to expose that thread's inherited stale value.

## Invalid assumption

Initialization assumes that a pre-existing TLS value proves the current thread has already been initialized and therefore must not be replaced.

## Failure

A later lookup returns execution state owned by a different thread; consistency validation detects the mismatch and terminates the child.

## Scope

Singleton cluster. This pattern is scoped to environments where TLS associations can survive process duplication in a way that becomes visible after native thread-identifier reuse; it is not evidence that ordinary conforming TLS implementations exhibit this behavior.

## Search strategy

1. Audit post-duplication paths for TLS keys that are not reinitialized before child threads can be created.
2. Find TLS initialization routines that skip assignment when a value already exists, and verify the existing value belongs to the current thread and process generation.
3. Check whether platform TLS implementations can preserve values across process duplication and whether native thread identifiers can be reused in the child.
4. Trace all per-thread state lookups after child thread creation and require ownership validation before use.

## Evidence

- [#54726](../micro_taxo/gh_54726.md): A multithreaded parent duplicated a child in which a newly created thread reused an absent parent's identifier; inherited TLS returned the old thread state because initialization retained an existing value, and a thread-state ownership check aborted. The reported fix reinitialized the relevant TLS after duplication.
