# When an optimized worker allocates auxiliary per-worker tracing state, a shutdown path that clears abandoned workers can leak that allocation if its cleanup isT

A worker-local optimization or tracing allocation is created during execution, but the worker's abandonment-time teardown releases only the ordinary worker state and leaves the auxiliary allocation reachable by no owner.

## Precondition

A worker performs optimized work that lazily allocates private tracing or profiling state, and the worker may be abandoned during runtime shutdown rather than completing its normal exit path.

## Critical operation

The runtime tears down the abandoned worker by clearing its standard per-worker state and deleting it through the shutdown cleanup path.

## Interference

Shutdown bypasses or short-circuits the worker's normal completion cleanup, while the auxiliary tracing state is managed separately from the ordinary worker state.

## Invalid assumption

The teardown path assumes that clearing or deleting the worker's standard state also releases every allocation created for that worker.

## Failure

The auxiliary tracing allocation remains unreclaimed after shutdown, and leak detection reports a memory leak instead of clean termination.

## Scope

This cluster contains one report, so the pattern is scoped to abandoned-worker shutdown cleanup and auxiliary state allocated by an optimized or tracing subsystem; it does not establish that all worker leaks arise from shutdown or from tracing state.

## Search strategy

1. Trace every per-worker allocation made by optimized, tracing, or profiling subsystems and verify that the abandoned-worker shutdown path frees each one.
2. Compare normal worker-exit cleanup with interpreter or runtime shutdown cleanup for resources stored outside the ordinary worker-state structure.
3. Inspect worker-state clear/delete routines for auxiliary pointers, lazily initialized buffers, and subsystem-specific destructors that are absent from the generic teardown.
4. Add a shutdown test that abandons an actively optimized worker and runs leak detection to confirm that all worker-local auxiliary state is released.

## Evidence

- [#144068](../micro_taxo/gh_144068.md): The report demonstrates that an abandoned daemon worker allocated private JIT tracing state, shutdown cleared and deleted the worker through a special cleanup path, and the omitted tracer release caused a leak; the fix explicitly added that release to worker-state clearing.
