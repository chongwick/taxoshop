# Generated optimized state has mismatched ownership across lifecycle handoffs

An optimized execution path creates generated state whose ownership changes among execution, container, and teardown contexts, but the handoff contract is incomplete or inconsistent. The resulting defect can retain the state indefinitely or release it before a remaining user is finished.

## Precondition

An optimization or generated-execution path allocates managed state with an initial reference and more than one possible owner, such as an execution context, installed container, exit record, or teardown structure.

## Critical operation

The generated state is dispatched, inserted into a durable structure, transferred to another lifecycle owner, or cleaned up after optimized execution, including failure, invalidation, and short-lived helper-process paths.

## Interference

A path omits the release after ownership transfer, while another path releases before a stealing handoff or before the object's tracking/deallocation invariants are established.

## Invalid assumption

The implementation assumes all paths use the same ownership convention and that a nearby container or cleanup phase automatically covers the generated state; conversely, it may assume an early decrement is safe without proving that no later owner still relies on the object.

## Failure

The generated state is either leaked and reported at shutdown by leak instrumentation, or prematurely freed and later accessed or decremented, producing use-after-free or related memory-safety failures.

## Scope

This is a mixed cluster with one umbrella ownership pattern and two distinct failure mechanisms: missing or misplaced release causes leaks, while premature release or invalid tracking assumptions cause stale/freed-state use. The reports support optimized/generated execution state specifically; they do not establish that every generated artifact or every lifecycle handoff has this defect.

## Search strategy

1. Trace each generated execution allocation through dispatch, installation, exception, invalidation, teardown, and process-shutdown paths, recording the owning reference at every boundary.
2. Check whether optimized execution and generated-state construction release their initial reference on every successful, exceptional, failed-compilation, and helper-process exit.
3. Verify whether insertion or registration steals, borrows, or increments a reference, and place decrements only after that ownership contract is explicit.
4. Audit object tracking and deallocation preconditions before adding cleanup on allocation-failure or early-exit paths.
5. Exercise both leak detection and lifetime-sensitive invalidation or teardown scenarios to distinguish unreleased state from stale or prematurely freed state.

## Evidence

- [#139540](../micro_taxo/gh_139540.md): Optimized generated execution state remained live across exceptional execution and teardown-related paths; the report and investigation identify inconsistent executor cleanup and reference ownership rather than a workload-specific cause.
- [#139749](../micro_taxo/gh_139749.md): A recoverable exception after optimized execution was enough to leave the generated execution allocation unreclaimed, supporting an exceptional-exit ownership gap.
- [#139750](../micro_taxo/gh_139750.md): Repeated optimized calls from an unrelated workload produced a direct leak of the generated execution object, showing that the defect is in the shared optimized-state lifecycle.
- [#139827](../micro_taxo/gh_139827.md): A separate complex operation reached the same generated-state allocation and leaked it, confirming that the trigger varies while the ownership defect is shared.
- [#142476](../micro_taxo/gh_142476.md): The attempted ownership correction exposed the second mechanism: releasing before a transfer that steals the reference caused use-after-free, while the original path leaked when the transfer or cleanup contract was missed.
- [#142985](../micro_taxo/gh_142985.md): Short-lived build helper processes also allocated generated execution state and terminated with direct leaks, showing that the defect applies to lifecycle completion and shutdown, not only repeated application workloads.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0089](../macro_taxo_before_hybrid/workflow-0089.md)
- [workflow-0090](../macro_taxo_before_hybrid/workflow-0090.md)
- [workflow-0094](../macro_taxo_before_hybrid/workflow-0094.md)
