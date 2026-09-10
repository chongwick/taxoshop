# An optimizing execution tracer records ordinary control flow while instrumentation or exceptional control transfer can intervene, but does not reliably abandon,

An optimizing execution tracer records ordinary control flow while instrumentation or exceptional control transfer can intervene, but does not reliably abandon or deoptimize before that boundary. The trace then carries stale stack-state assumptions into resumed or redirected execution, where frame cleanup detects inconsistent stack state and aborts.

## Precondition

Speculative tracing is active for an execution path whose operations may invoke instrumentation callbacks or enter exception handling, with the trace assuming uninterrupted ordinary control flow and a particular operand-stack shape.

## Critical operation

The tracer advances into, or records across, an instrumented operation or exceptional transfer without first terminating or deoptimizing the trace and synchronizing execution state.

## Interference

Instrumentation or exception handling transfers control to monitoring logic or another exceptional path, potentially involving callback execution or re-entrancy, while the speculative trace remains active.

## Invalid assumption

The trace assumes that the abstract operand-stack and frame state from ordinary control flow still describe the actual execution after the instrumentation or exceptional boundary.

## Failure

Frame finalization or interpreter consistency checks observe residual stack state that does not match the actual frame state and abort, such as through a stack-level assertion or stack-overflow failure.

## Scope

This is a singleton cluster, so the pattern is scoped to the reported interaction between speculative tracing, instrumentation, and exceptional control flow. The report supports the boundary-handling mechanism, but not a broader claim about all tracing or all callback-induced stack failures.

## Search strategy

1. Check every transition from optimized tracing to instrumented operations and require trace abandonment or deoptimization before the transition.
2. Check exceptional edges and exception-raising operations for trace termination before invoking monitoring, callback, or cleanup logic.
3. Check callback and monitoring entry paths for re-entrancy while a speculative trace is active, and verify frame and operand-stack synchronization.
4. Check frame-exit and cleanup assertions against traces that cross instrumentation or exception boundaries with nonempty residual stack state.

## Evidence

- [#142448](../micro_taxo/gh_142448.md): The report reproduces only with the optimizer enabled and combines monitoring with exceptional execution; the diagnosis identifies failure to abandon tracing at instrumented instructions and before exceptional monitoring callbacks, while the fix forces deoptimization at those boundaries. The resulting inconsistency appears as stack corruption/over-
