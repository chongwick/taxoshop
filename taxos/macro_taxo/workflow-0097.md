# Shutdown/finalization races with residual worker activity on shared runtime or dependency state

Teardown of shared runtime, interpreter, or external-library state proceeds before all participating workers and attachment paths have stopped or completed a synchronized handoff. Residual activity then accesses, modifies, or atomically updates state during cleanup. The cluster includes both premature lifetime-ending operations and direct synchronization mismatches during teardown.

## Precondition

A shutdown, finalization, exit, or cleanup path can run while daemon workers, attaching threads, error-path thread churn, or native calls may still access shared lifecycle state or dependency-managed state.

## Critical operation

The teardown path clears, resets, removes, closes, frees, or otherwise updates shared state, sometimes with a plain store or after releasing the protection that normally orders access.

## Interference

A still-running or re-entering worker concurrently reads, follows, or updates that state, or an attachment/native path accesses it using a different atomic, lock, or ordering protocol; in some cases external-library exit cleanup runs while worker calls remain active.

## Invalid assumption

The shutdown phase assumes that prior thread cleanup, an apparent stop-the-world or lock boundary, daemon-thread hanging, the GIL, an assertion context, or one-sided atomic/locked access guarantees quiescence and lifetime safety for every remaining participant.

## Failure

Race detection reports unsynchronized conflicting accesses; depending on the mechanism, a worker may observe cleared or inconsistent state, access freed runtime or dependency storage, dereference invalid data, crash, hang, or fail shutdown testing.

## Scope

Membership was manually restricted to the evidence listed below. This mixed cluster covers shutdown before residual activity is safely ordered or finished. Some members lose backing-state lifetime during cleanup; others use unlocked reads, incompatible atomic access, or incomplete barriers. Runtime, thread, and external-library state require different ownership and synchronization checks.

## Search strategy

1. Trace every shutdown, finalization, exit, and cleanup path and verify that it waits for or otherwise prevents all daemon, attaching, re-entering, and native worker paths from accessing the affected state.
2. For each shared object or state record that can be freed or removed, identify all thread and container ownership references and verify that deallocation cannot occur until the last worker-held reference is released.
3. Compare every teardown access with concurrent worker accesses and require one complete protocol: the same mutex, compatible atomic operations, stop-the-world barrier, or explicit publication and quiescence sequence.
4. Inspect assertions, debug reads, error paths, and pre-barrier checks for shared-state access that occurs before the lock, pause, or synchronization operation that is supposed to protect it.
5. Audit calls that release runtime locks or enter external libraries during shutdown and verify that dependency cleanup or process-exit handlers cannot free their backing state while those calls remain active.

## Evidence

- [#145933](../micro_taxo/gh_145933.md): Process-exit cleanup in an external cryptographic library freed internal state while background workers continued native calls, producing a crash; the report's later analysis identifies exit overlap rather than the initially suspected startup-only race.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0014](../macro_taxo_before_hybrid/workflow-0014.md)
- [workflow-0056](../macro_taxo_before_hybrid/workflow-0056.md)
- [workflow-0077](../macro_taxo_before_hybrid/workflow-0077.md)
