# Optimized execution crosses an instrumentation, exceptional-transfer, or fallback boundary without synchronizing speculative stack state

An optimized execution path carries hidden stack-state assumptions across a boundary where control leaves ordinary optimized flow. In one mechanism, tracing continues into instrumentation or exception handling instead of being abandoned; in the other, a side exit exposes cached top-of-stack values without materializing them in canonical stack storage. The resumed path then observes inconsistent stack state and crashes.

## Precondition

Optimized execution is active with stack state represented speculatively—through trace assumptions or cached values—and control may transfer to monitoring, exception handling, or fallback execution that requires synchronized frame state.

## Critical operation

Transfer control across that boundary without both terminating or deoptimizing speculative tracing when required and materializing any cached stack values into the representation consumed by the destination.

## Interference

Instrumentation or exceptional control flow redirects execution, or a side exit enters fallback code, while the optimized path's hidden stack representation remains active or incompletely synchronized.

## Invalid assumption

The destination path assumes its abstract frame and canonical operand stack already describe the current execution state because the transfer metadata or trace position appears valid.

## Failure

The destination or frame cleanup consumes missing, stale, or inconsistent stack state, producing a stack assertion or overflow in one case and an invalid memory access in the other.

## Scope

This mixed cluster supports the shared boundary invariant that optimized execution must synchronize frame and stack state before control leaves its ordinary path. The reports differ in mechanism: one leaks speculative tracing across instrumentation or exception transfer, while the other fails to flush cached stack values on a side exit. They do not establish a broader rule about all callbacks, caching, ownership, or stale/freed memory.

## Search strategy

1. Inspect every optimized-to-instrumented or optimized-to-exceptional transition and require trace termination or deoptimization before control transfer.
2. Inspect every optimized side exit and verify that all cached stack values are materialized into canonical frame storage before fallback execution.
3. Check transfer metadata against the actual stack representation, including cache depth, operand-stack height, and frame stack pointers.
4. Exercise boundary transfers with monitoring callbacks, exception paths, and nontrivial top-of-stack values, then verify both state consistency and process survival.

## Evidence

- [#142448](../micro_taxo/gh_142448.md): The report supports a tracing-boundary failure: monitoring combined with exceptional execution allowed tracing to continue across instrumented and exception-related operations, and the fix deoptimized before those boundaries to prevent inconsistent residual stack state.
- [#142718](../micro_taxo/gh_142718.md): The report supports a distinct side-exit synchronization failure: cached top-of-stack registers were not saved to canonical stack storage before fallback control transfer, and the fix flushed the stack at side exits to prevent an invalid read.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0126](../macro_taxo_before_hybrid/workflow-0126.md)
- [workflow-0132](../macro_taxo_before_hybrid/workflow-0132.md)
