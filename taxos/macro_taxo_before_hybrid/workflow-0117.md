# A runtime retains specialized executable state across teardown, then cleanup resumes it after the optimization subsystem has been disabled; the stale state reën

A runtime retains specialized executable state across teardown, then cleanup resumes it after the optimization subsystem has been disabled; the stale state re-enters optimization code that assumes the subsystem is still active.

## Precondition

A frequently executed operation has been specialized, and a suspended or otherwise retained computation can still execute that specialized representation during cleanup or finalization.

## Critical operation

Teardown disables the optimization or execution subsystem without first invalidating, de-specializing, or otherwise quarantining every already-specialized operation.

## Interference

Cleanup resumes the retained computation and dispatches the stale specialized operation while subsystem shutdown is in progress or already complete.

## Invalid assumption

Optimization entry points assume that reaching them proves the optimization subsystem remains enabled, rather than defensively handling specialized state that outlived the subsystem.

## Failure

A debug invariant or equivalent state check observes the disabled subsystem and aborts instead of safely bypassing optimization or falling back to the generic operation.

## Scope

This is a singleton cluster, so the pattern is cautiously scoped to shutdown or finalization races involving retained specialized execution state. The report establishes stale specialized state and unsafe optimizer re-entry, but does not justify a broader rule covering all cache invalidation or all concurrent subsystem shutdowns.

## Search strategy

1. Check finalization and shutdown paths for global optimization-state changes that leave specialized instructions or cached executors reachable.
2. Trace suspended frames, generators, callbacks, and deferred cleanup for execution after subsystem teardown begins.
3. Verify that disabling an optimization subsystem invalidates or safely gates every already-specialized operation before retained computations can resume.
4. Inspect optimizer entry points for unconditional assertions that subsystem-enabled state follows from the caller’s specialized representation.

## Evidence

- [#140936](../micro_taxo/gh_140936.md): The report shows that a hot control-flow operation remains specialized after runtime finalization disables the JIT, and that finalization of a live suspended computation re-enters the stale operation, triggering an assertion that the JIT is enabled; the fix adds a disabled-state guard and returns without optimization.
