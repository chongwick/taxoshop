# A fixed-size alternate signal stack is allocated without validating worst-case signal-handler stack usage; signal-path execution can corrupt the heap-backedっ

A fault-reporting component allocates an alternate signal stack with a platform-sensitive fixed heuristic, and excessive signal-handler stack use corrupts that allocation before teardown.

## Precondition

A fault-reporting subsystem uses a heap-backed alternate signal stack whose size is chosen by a fixed multiplier or other heuristic rather than being established from the complete handler call chain and platform requirements.

## Critical operation

A diagnostic or fault signal executes on the alternate stack and invokes handler logic, potentially including a prior handler or other callbacks.

## Interference

The signal-path stack usage exceeds the reserved region and overwrites bytes or allocator metadata beyond the valid stack allocation.

## Invalid assumption

The heuristic-sized alternate stack is sufficient for every supported platform and handler path, and therefore remains intact until normal cleanup.

## Failure

Later cleanup fills, validates, or frees the corrupted allocation; memory instrumentation detects the out-of-bounds state and terminates the process, although the corruption occurred earlier.

## Scope

This is a singleton cluster. The report supports a cautiously scoped pattern involving heap-backed alternate signal-stack corruption and delayed detection, but the enlargement experiment did not change the observed allocation or failure, so it does not conclusively prove that simple undersizing alone is the root cause.

## Search strategy

1. Inspect alternate-signal-stack allocations for fixed constants or multipliers that are not derived from measured worst-case handler usage.
2. Trace every handler and chained-handler call reachable on the alternate stack, and compare its worst-case stack use with the reserved size on each target platform.
3. Check whether signal-stack allocations have guard regions, explicit overflow detection, or tests that exercise the deepest diagnostic path.
4. Verify that teardown-time allocator failures are correlated with earlier writes to the signal-stack allocation rather than treated as the point of origin.

## Evidence

- [#124001](../micro_taxo/gh_124001.md): The report repeatedly shows a heap allocation originating in alternate signal-stack setup and a later teardown-time debug fill triggering a heap-buffer-overflow. It identifies a fixed stack-size heuristic as weak and reproduces the failure across multiple target environments and releases; increasing the nominal multiplier did not eliminate the same
