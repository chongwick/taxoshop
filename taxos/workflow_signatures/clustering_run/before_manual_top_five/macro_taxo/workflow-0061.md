# Instrumentation compatibility failures contaminate configuration probes or target linkage

Optional profiling, sanitizer, or similar instrumentation is integrated without validating its compatibility with the selected compiler, runtime, platform, and other instrumentation modes.

## Precondition

An instrumentation mode is enabled and its flags or support libraries are propagated into configure-time probes or production link commands.

## Critical operation

Compile, execute, or link instrumented programs while using their results or assembled inputs to determine capabilities or produce the target.

## Interference

The instrumentation may be rejected by the compiler, make probe executables unloadable or crash because runtime support is missing, conflict with another instrumentation mode, or introduce support-library symbols incompatible with the target's runtime linkage.

## Invalid assumption

A failed instrumented probe is treated as a genuine negative capability result, or instrumentation support is assumed compatible with the selected toolchain and runtime linkage.

## Failure

Configuration records false feature or dependency settings and may fail later with an unrelated incomplete-type error; alternatively, the instrumented target fails directly at link time with unresolved runtime, library, exception, allocation, or initialization symbols.

## Scope

The shared pattern is failure to validate instrumentation compatibility before relying on instrumented probes or links. Issues 86434, 114453, and 116891 primarily demonstrate configuration contamination by compiler or runtime incompatibility, with differing downstream diagnostics; issue 150467 demonstrates the related direct link-time incompatibility. The reports do not establish one universal instrumentation mode, platform, failure phase, or required remediation.

## Search strategy

1. Trace optional instrumentation flags and support libraries into every configure-time compile, link, and run probe.
2. Check that probe failures distinguish compiler rejection, loader or startup failure, and missing instrumentation runtime from genuine capability absence.
3. Verify that enabled instrumentation modes are mutually compatible and that their runtime and support-library requirements match the target's platform and runtime linkage.
4. Inspect conditional configuration outputs and later type consumers for false negatives caused by failed instrumented probes.
5. Compare instrumented link inputs with the selected runtime-library convention and audit unresolved symbols by originating library.

## Evidence

- [#86434](../micro_taxo/gh_86434.md): The report shows compiler-specific sanitizer flags being added before compiler support was checked; incompatible flags then caused a later capability probe to fail, leading to a misleading configuration result until an upfront flag validation was added.
- [#114453](../micro_taxo/gh_114453.md): The report shows profiling flags producing executables that failed at startup because a required process-environment symbol was unavailable; configure misclassified those probe failures, and the resulting false settings surfaced later as an incomplete conditional type used by value.
- [#116891](../micro_taxo/gh_116891.md): The report shows thread-sanitizer configuration producing a false library-capability result because the compiler runtime support package was missing; the report also records that incompatible sanitizer combinations should be rejected explicitly.
- [#150467](../micro_taxo/gh_150467.md): The report shows an instrumented Windows target failing at link time because instrumentation support libraries and the selected runtime objects required incompatible runtime, C-library, exception, allocation, and initialization symbols.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0018](../macro_taxo_before_hybrid/workflow-0018.md)
- [workflow-0052](../macro_taxo_before_hybrid/workflow-0052.md)
- [workflow-0160](../macro_taxo_before_hybrid/workflow-0160.md)
