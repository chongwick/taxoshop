# A capacity-sensitive I/O test derives its workload from a reported external-buffer size and uses that single estimate to trigger backpressure.

Tests that infer an external system's usable capacity from an advertised size can miss the intended saturation state when the real capacity is larger or changes dynamically.

## Precondition

The test needs to force an asynchronous I/O path into backpressure, while the relevant external buffer is controlled by the operating system or another implementation outside the test.

## Critical operation

The test queries the externally reported capacity and writes approximately that amount, expecting the operation to fill the external buffer and make the application's pending-write buffer observable.

## Interference

The external implementation accepts substantially more data than the reported capacity, potentially because capacity is dynamically allocated or the report excludes usable message space.

## Invalid assumption

The reported capacity is an exact upper bound on data acceptance and one workload sized from it is sufficient to force backpressure.

## Failure

The backpressure assertion fails even though the write remains valid, producing a false test failure; repeated writes or an observation-based saturation condition are needed instead.

## Scope

This cluster contains one report, so the pattern is scoped to capacity-driven backpressure tests involving externally reported buffer sizes; it does not establish that all capacity reports are inaccurate or that looping is universally required.

## Search strategy

1. Find tests that size a workload directly from an operating-system or external-component capacity report.
2. Check whether a single write at the reported capacity is assumed to make an external buffer full.
3. Inspect whether the test observes actual pending data or blocking before asserting that backpressure occurred.
4. Look for environment-dependent capacity, dynamic allocation, or reports that exclude usable payload space.

## Evidence

- [#122136](../micro_taxo/gh_122136.md): A test wrote data sized from reported socket-buffer capacities, but a Linux kernel accepted more data than advertised, so the application's write buffer stayed empty and the backpressure assertion failed; the fix looped until pending data was actually observed.
