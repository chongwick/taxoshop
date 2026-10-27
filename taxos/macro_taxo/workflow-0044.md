# Sanitizer leak checking aborts otherwise successful short-lived runtime or build subprocesses

Short-lived runtime and build helpers can complete their functional work yet fail at process exit when leak-detecting instrumentation observes residual runtime or instrumentation state, or when subprocess setup removes the configuration that suppresses known residual allocations.

## Precondition

A test or build invokes a short-lived runtime subprocess under leak-detecting sanitizer instrumentation; the subprocess may initialize runtime state, use profiling instrumentation, or intentionally replace its inherited environment.

## Critical operation

The subprocess performs its validation, generation, or startup work and then enters process shutdown, where runtime finalization, instrumentation exit handlers, and the sanitizer leak check run.

## Interference

The leak check can run with sanitizer suppression settings removed by environment isolation, before multi-phase runtime initialization/finalization has reclaimed all allocations, after an abbreviated exit path, or after profiling shutdown has allocated bookkeeping state.

## Invalid assumption

Functional success and ordinary subprocess termination are assumed to imply leak-clean shutdown, and environment isolation or instrumentation-specific exit behavior is assumed not to affect sanitizer leak-detection semantics.

## Failure

LeakSanitizer reports residual direct or indirect allocations as fatal, the subprocess returns failure, and the enclosing test or build validation target aborts even though the component checks or artifact-generation work completed.

## Scope

This is a mixed umbrella pattern. The reports share a fatal process-exit leak result masking successful functional work, but the mechanisms differ: lost sanitizer configuration, incomplete runtime teardown or abbreviated exit, and profiling-runtime shutdown bookkeeping. It does not conflate leaked ownership with stale or freed-state use, and it does not establish that every sanitizer leak or every instrumented subprocess has this failure mode.

## Search strategy

1. Inspect short-lived subprocesses and build helpers that run with leak-detecting sanitizers and verify whether their exit status is determined by process-exit leak reports.
2. Trace all runtime and instrumentation allocations made during initialization, validation, profiling, and exit handlers to confirm they are reclaimed before leak checking.
3. Check tests that launch children with an empty or replaced environment for removal of sanitizer options, suppression files, preload settings, or related configuration.
4. Compare normal, abbreviated, explicit, EOF, and profiler-enabled exit paths to ensure shutdown ordering is equivalent before sanitizer reporting.
5. Run build-time generators with sanitizer and profiling instrumentation together and distinguish runtime leaks from profiling-runtime exit bookkeeping.

## Evidence

- [#104472](../micro_taxo/gh_104472.md): An empty-environment subprocess removed sanitizer configuration that normally suppressed known runtime allocations; leak detection then made the otherwise successful test fail, leading to a sanitizer-specific skip.
- [#104791](../micro_taxo/gh_104791.md): Sanitizer leak detection failed during build-time module validation after the checks themselves completed, with the report attributed to incomplete multi-phase runtime initialization and finalization.
- [#135618](../micro_taxo/gh_135618.md): Immediate runtime exit exposed startup-created metadata allocations, while the same report also records sanitizer-enabled build helpers failing at exit because profiling bookkeeping remained allocated.
- [#144199](../micro_taxo/gh_144199.md): A sanitizer- and profiling-instrumented build helper completed generation work but failed when exit-time profiling bookkeeping was reported as direct and indirect leaks, causing the enclosing profile build to stop.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0034](../macro_taxo_before_hybrid/workflow-0034.md)
- [workflow-0038](../macro_taxo_before_hybrid/workflow-0038.md)
- [workflow-0083](../macro_taxo_before_hybrid/workflow-0083.md)
- [workflow-0146](../macro_taxo_before_hybrid/workflow-0146.md)
