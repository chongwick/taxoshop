# Leak-checking a short-lived build helper that combines execution profiling with sanitizer instrumentation can mistake profiling-runtime shutdown bookkeeping for

A profile-instrumented helper performs its intended generation work but fails during process teardown because profiling bookkeeping remains allocated when leak checking runs.

## Precondition

A build compiles and runs a short-lived artifact-generation executable with both execution-profiling instrumentation and leak-detecting sanitizer instrumentation enabled.

## Critical operation

The build invokes that executable to generate source or metadata artifacts, causing the profiling runtime to initialize and later finalize its coverage bookkeeping at process exit.

## Interference

Profiling finalization allocates or retains bookkeeping objects during exit-time dumping, and those objects remain reported as live when the leak detector performs its final check.

## Invalid assumption

The build assumes that profiling runtime shutdown is leak-clean, or that exit-time profiling allocations will be exempt from the sanitizer's process-exit leak report.

## Failure

The sanitizer reports the residual profiling allocations as fatal leaks, the helper exits unsuccessfully, its generated artifact target fails, and the enclosing build pipeline aborts.

## Scope

This is a cautiously scoped singleton pattern supported by one report. It generalizes to short-lived build helpers combining execution profiling with leak detection; the report specifically demonstrates failure during exit-time profiling finalization, not a general incompatibility between profiling and sanitizers in all program lifetimes.

## Search strategy

1. Inspect build rules for helper executables compiled with both profiling instrumentation and leak-detecting sanitizers.
2. Trace profiling-runtime initialization, data dumping, and exit handlers for allocations that remain live at process termination.
3. Run each instrumented artifact generator under leak detection and verify that sanitizer reporting occurs only after all profiling teardown callbacks complete.
4. Check whether build-time helper targets treat sanitizer leak reports as fatal and whether profiling-specific leak suppression or cleanup is deliberately configured.

## Evidence

- [#144199](../micro_taxo/gh_144199.md): The reported build runs an instrumented helper during profile-generation setup; the helper triggers exit-time profiling bookkeeping allocations, LeakSanitizer reports direct and indirect residual allocations from that runtime, and the helper's failed make targets stop profile generation and the overall optimization build.
