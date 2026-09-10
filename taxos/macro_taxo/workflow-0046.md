# A process-embedded runtime leaks globally shared cached values when shutdown skips reclaiming values treated as permanently retained, so repeated initialize/shु

A process-embedded runtime leaks globally shared cached values when shutdown skips reclaiming values treated as permanently retained, so repeated initialize/shutdown cycles accumulate allocations.

## Precondition

The runtime creates globally shared or deduplicated values whose retention is exempted from ordinary ownership-based cleanup, and the host process restarts the runtime without exiting.

## Critical operation

Perform repeated runtime shutdown and reinitialization within the same process.

## Interference

Shutdown clears ordinary runtime allocations but skips reclamation or demotion of the shared retained values and their bookkeeping references.

## Invalid assumption

Treating shared values as permanently retained is assumed to be compatible with a shutdown contract that otherwise cleans up runtime allocations and supports clean restart.

## Failure

Leak detection reports persistent memory growth or non-clean shutdown after each cycle; changing shutdown to reclaim the values can additionally expose stale external references held across restart.

## Scope

This is a singleton cluster, so the pattern is scoped to runtimes with shared retained or interned values and in-process restart behavior; it does not claim that all shutdown leaks arise from this mechanism.

## Search strategy

1. Inspect shutdown paths for globally shared, cached, interned, or immortal values that bypass normal deallocation.
2. Trace every reference added by deduplication or permanent-retention marking and verify that shutdown removes or reconciles it.
3. Search repeated initialize/shutdown tests for memory-growth checks and confirm they exercise non-debug and production configurations.
4. Audit extensions or host code that retain shared runtime objects across shutdown and reinitialization.

## Evidence

- [#113190](../micro_taxo/gh_113190.md): The report shows that permanently retained deduplicated strings were skipped during ordinary shutdown cleanup, causing leaks across repeated runtime finalization; it also documents the restart-safety risk when cleanup is later enabled while external code still retains those values.
