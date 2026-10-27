# Memory-instrumented builds can fail at link time when instrumentation support libraries are combined with an incompatible runtime-library linkage mode.

A build enables optional memory instrumentation through custom compiler and linker settings, but the target’s runtime-library arrangement is incompatible with the instrumentation and support libraries.

## Precondition

The build enables memory instrumentation and supplies instrumentation-aware linker integration while retaining a specific runtime-library linkage configuration.

## Critical operation

The linker combines instrumented objects, instrumentation support libraries, and the target’s selected runtime libraries into the executable or shared library.

## Interference

The selected runtime linkage does not provide the runtime, C-library, exception-handling, or initialization symbols expected by the instrumented and support libraries.

## Invalid assumption

Instrumentation options and their inferred support libraries are assumed to be compatible with the target’s existing runtime-library linkage without verifying that their symbol and linkage requirements match.

## Failure

Linking aborts with numerous unresolved external symbols from both instrumentation support code and runtime-library objects, so the target is not produced.

## Scope

This is a cautiously scoped singleton pattern. The report establishes an instrumentation/runtime linkage incompatibility manifested as unresolved symbols, but does not prove the exact static-versus-dynamic linkage choice or whether the immediate trigger was a toolchain regression.

## Search strategy

1. Trace every instrumentation compiler and linker flag to the runtime-library selection used by the affected target.
2. Verify that all inferred or explicitly linked instrumentation support libraries use the same runtime linkage convention as the target and its dependencies.
3. Inspect unresolved symbols by originating library and confirm that the selected runtime libraries export the required initialization, standard-library, exception-handling, and allocation symbols.
4. Compare instrumented and non-instrumented link inputs across toolchain revisions to detect a changed runtime-library or instrumentation compatibility requirement.

## Evidence

- [#150467](../micro_taxo/gh_150467.md): A Windows build that injects address-sanitizer compiler and linker settings fails while linking because instrumentation thunks, support libraries, and runtime-library objects collectively reference many unavailable runtime, C-library, exception-handling, allocation, and initialization symbols.
