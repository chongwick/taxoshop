# When a concurrency sanitizer instruments the test target but a linked dependency remains uninstrumented, synchronization performed inside that dependency is not

A sanitizer job analyzes only instrumented portions of the process; an uninstrumented dependency can hide synchronization from the race detector, producing a misleading race result.

## Precondition

A concurrency-sanitized test or executable links against a dependency that participates in the tested concurrent operations but was built without compatible sanitizer instrumentation.

## Critical operation

Run concurrent code through the dependency while the sanitizer tracks accesses in the instrumented test and runtime components.

## Interference

The dependency's internal synchronization and related memory-access events are invisible to the sanitizer, so its ordering cannot be incorporated into the detector's happens-before analysis.

## Invalid assumption

Assume that instrumenting the test target alone gives the sanitizer complete visibility into the synchronization behavior of every linked component.

## Failure

The sanitizer emits a false-positive data-race diagnostic for valid dependency-mediated synchronization, causing the sanitizer test job to fail or forcing the affected concurrency test to be skipped.

## Scope

This is a cautiously scoped singleton pattern: the evidence concerns one sanitizer workflow and one external dependency, but the generalized mechanism applies to dependency-mediated synchronization whenever instrumentation coverage is incomplete.

## Search strategy

1. Check sanitizer CI jobs for linked third-party or system dependencies that are not rebuilt with the same sanitizer instrumentation.
2. Trace sanitizer test link and runtime paths to verify that the instrumented dependency build is actually selected instead of an uninstrumented system or cached copy.
3. Inspect dependency build flags and cache keys for sanitizer-specific compiler and linker options.
4. Review race reports involving synchronization inside external libraries and verify whether the reported accesses originate in instrumented code or an uninstrumented dependency.

## Evidence

- [#143750](../micro_taxo/gh_143750.md): The report explicitly proposes rebuilding the cryptographic dependency with thread-sanitizer instrumentation for sanitizer CI to avoid false positives, and its fix adds sanitizer flags to that dependency's build and configures the test target to use the rebuilt copy.
