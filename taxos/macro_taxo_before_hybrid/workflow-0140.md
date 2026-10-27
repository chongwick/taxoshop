# A build-time capability probe can enable a platform interface when it tests symbol availability under assumptions that do not match the final compiler target or

A build configuration records a platform interface as available even though the final compilation environment does not expose its declaration.

## Precondition

The build targets a platform-specific SDK, API level, or feature set in which an interface is conditionally declared, while configuration probing and final compilation do not use exactly the same target settings and header-visibility conditions.

## Critical operation

The configuration probe checks whether the interface can be declared or linked, without compiling the real use under the final target-specific headers and flags, and records a feature macro that enables the interface-dependent implementation.

## Interference

During compilation, target-specific availability guards or equivalent header conditions suppress the interface declaration for the actual target settings.

## Invalid assumption

A successful configure-time symbol or link check is assumed to prove that the interface is declared and callable in every subsequent compilation unit under the final target configuration.

## Failure

The enabled code path calls an undeclared interface; strict diagnostics, such as treating implicit declarations as errors, stop the build instead of selecting a fallback or clearly reporting the target mismatch.

## Scope

This is a cautiously scoped singleton pattern supported by one platform-specific build failure. It generalizes to mismatches between capability probes and final target/header settings, but does not establish that every probe failure is caused by a link-only test or that the interface is absent at runtime.

## Search strategy

1. Compare every platform capability probe with the exact compiler target, SDK/API, preprocessor flags, and headers used by the final build.
2. Inspect availability-guarded declarations and verify that the probe compiles a representative call with the same headers and target macros.
3. Search for feature macros set by link-only or declaration-free probes, then trace whether guarded source code relies on those macros.
4. Check whether changing target or SDK settings affects configuration results and compilation settings consistently across clean rebuilds.

## Evidence

- [#143640](../micro_taxo/gh_143640.md): The report shows a configure check marking a platform interface available while the compiler uses a lower target API level whose headers omit the declaration; the resulting feature-enabled call fails under an implicit-declaration error, and using a correctly targeted compiler is identified as the remedy.
