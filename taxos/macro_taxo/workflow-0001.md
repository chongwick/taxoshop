# Thread-local state survives process duplication and is mistaken for the new thread's state after identifier reuse

A process duplicates while auxiliary threads exist; the child later creates a thread whose runtime identifier is reused, and inherited thread-local state is retained instead of being replaced. Subsequent lookups return state belonging to a vanished pre-duplication thread.

## Precondition

A multithreaded process stores execution context in thread-local storage, and process duplication can occur from one thread while other threads have live thread-local entries.

## Critical operation

The duplicated child initializes or creates a thread and associates its execution context with the thread-local key.

## Interference

The platform preserves thread-local values from threads that disappeared during duplication, and the new child thread receives an identifier that collides with one of those vanished threads. An initialization helper that refuses to overwrite an existing value therefore leaves the stale entry in place.

## Invalid assumption

The presence of a thread-local value implies that it belongs to the current live thread and can safely be reused during initialization.

## Failure

A later context lookup retrieves the inherited state for the vanished thread; identity or ownership validation detects that it does not match the current thread, causing a fatal error or child-process termination.

## Scope

This is a singleton cluster, so the pattern is scoped to process duplication combined with inherited per-thread state, identifier reuse, and non-overwriting initialization. The report also indicates that the behavior depended on a particular platform threading implementation and was later fixed by reinitializing the relevant TLS after duplication.

## Search strategy

1. Inspect process-duplication paths for cleanup or reinitialization of thread-local keys whose owners do not survive into the child.
2. Check thread-local initialization helpers for conditional set-if-absent behavior instead of unconditional replacement or explicit ownership validation.
3. Trace whether thread identifiers can be reused after duplication and whether inherited entries are keyed only by that reusable identifier.
4. Verify that post-duplication context lookups validate both the current thread identity and the provenance of the stored state.

## Evidence

- [#54726](../micro_taxo/gh_54726.md): The report documents that, on an affected threading implementation, thread-local values from disappeared parent threads remain visible after process duplication; identifier reuse lets a newly created child thread observe the stale value, conditional initialization preserves it, and later state validation terminates the child.
