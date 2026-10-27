# Auxiliary per-thread tracing state is omitted from an alternate thread-teardown path

Optimized or instrumented execution allocates private per-thread auxiliary state, but termination through an abandoned-thread or shutdown cleanup path releases only the ordinary thread state. The auxiliary allocation remains unreclaimed and is reported as a leak.

## Precondition

A thread enters optimized or tracing execution that lazily allocates private auxiliary state, and the thread may terminate through shutdown or another path that bypasses its normal completion cleanup.

## Critical operation

The runtime clears or deletes the thread's ordinary state while the auxiliary tracing or optimization state remains separately managed.

## Interference

The alternate teardown path omits the subsystem-specific release required for the auxiliary per-thread allocation.

## Invalid assumption

The implementation assumes that clearing or deleting ordinary thread state, or ending the hosting runtime, automatically releases every allocation created for that thread.

## Failure

The auxiliary per-thread allocation remains live after thread or runtime termination, and leak detection reports a direct memory leak instead of clean shutdown.

## Scope

Both reports support the same ownership-cleanup omission for private per-thread state during non-normal thread termination. The evidence does not establish that every thread leak involves optimization or tracing, nor that normal thread completion always leaks; the distinguishing boundary is the alternate shutdown or abandonment cleanup path.

## Search strategy

1. Trace every per-thread allocation made by optimization, tracing, or profiling code to an explicit release on normal exit and abandoned-thread teardown paths.
2. Compare ordinary thread-exit cleanup with shutdown cleanup for resources stored outside the generic thread-state structure.
3. Inspect thread-state clear and delete routines for subsystem-specific auxiliary pointers, buffers, and destructors that generic teardown does not invoke.
4. Add a leak-detection test that abandons an actively optimized or instrumented thread during shutdown and verifies that all private auxiliary state is released.

## Evidence

- [#141542](../micro_taxo/gh_141542.md): The report shows optimized thread execution allocating private tracing-related state and ending with a sanitizer-reported direct leak, establishing the missing cleanup symptom on a daemon-thread termination path.
- [#144068](../micro_taxo/gh_144068.md): The report explicitly connects an abandoned daemon thread with leaked private optimization tracing state during runtime shutdown and documents that adding the subsystem-specific release to thread-state clearing removes the leak.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0094](../macro_taxo_before_hybrid/workflow-0094.md)
- [workflow-0143](../macro_taxo_before_hybrid/workflow-0143.md)
