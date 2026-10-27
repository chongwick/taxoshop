# Optimized execution leaks generated artifacts

An optimization path materializes generated execution artifacts without completing their ownership lifecycle, causing sanitizer-visible leaks across otherwise unrelated workloads.

## Precondition

An optional tracing, compilation, or execution-optimization path is enabled, and the workload reaches a code path eligible for optimization under leak-detection instrumentation.

## Critical operation

The optimizer converts an intermediate execution representation into a newly allocated generated execution artifact for the optimized path.

## Interference

The artifact is not transferred to a durable owner with teardown responsibility, or the corresponding release path is absent when optimized execution ends or the process shuts down.

## Invalid assumption

The implementation assumes that a generated artifact created during optimization will be reclaimed automatically or that its lifetime is covered by an existing execution object's cleanup, even though the allocation has a separate ownership obligation.

## Failure

Leak instrumentation reports the generated artifact as a direct allocation at process termination, potentially turning tests or build-time helper executions into failures.

## Scope

The reports support a shared lifecycle defect in the optimization-generated artifact, while the triggering workload varies substantially: repeated calls, a single complex operation, and build-time code generation. They do not establish that repetition is required or that every optimized artifact leaks.

## Search strategy

1. Trace every allocation of generated execution artifacts from creation to an explicit release or owner teardown.
2. Check whether optimized and non-optimized execution paths use the same ownership and destruction protocol for generated state.
3. Inspect early exits, failed optimization, replacement, and shutdown paths for generated artifacts that are created but never registered or freed.
4. Run representative short-lived optimized workloads under leak detection and verify that allocation counts return to baseline after execution.

## Evidence

- [#139750](../micro_taxo/gh_139750.md): A repeated workload with optimization enabled reaches generated execution-artifact allocation, and leak detection reports the artifact because it is never freed.
- [#139827](../micro_taxo/gh_139827.md): A distinct application operation reaches the same optimizer allocation and produces the same unfreed generated artifact, showing that the trigger is not specific to the application API.
- [#142985](../micro_taxo/gh_142985.md): Build-time module-processing executions allocate generated artifacts through the optimizer and fail under leak detection, confirming the issue also occurs in short-lived helper processes rather than only in long-running repeated calls.
