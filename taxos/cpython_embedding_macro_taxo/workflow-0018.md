# Non-default toolchain modes invalidate capability evidence

A profiling, instrumentation, or target-selection setting changes the effective compiler, linker, runtime, or API-visibility context, but capability detection and the final build do not consistently validate that context.

## Precondition

A build uses a non-default profiling, sanitizer, or target configuration whose support depends on a compatible compiler, runtime libraries, system ABI, or target-version macros.

## Critical operation

The build applies that configuration while probing capabilities or linking normal build targets, then uses the results to select feature definitions or dependent libraries.

## Interference

The altered configuration rejects a flag, lacks its runtime support, crashes an executed probe, exposes a symbol to linking but not to headers, or otherwise makes probe/link results unrepresentative of the consumer compilation environment.

## Invalid assumption

The build assumes that a probe result or inferred instrumentation library is valid evidence of feature availability and toolchain compatibility, without verifying compilation, linking, execution, headers, and target settings under the same effective configuration.

## Failure

Configuration propagates incorrect feature or library decisions, or the incompatible instrumentation runtime reaches the final link, producing a misleading downstream compile-time API/type error or unresolved-symbol link failure.

## Scope

The shared pattern is configuration-context mismatch, not specifically probe execution or incomplete types: most reports show poisoned capability detection, while the final-link case is the same unvalidated instrumentation/toolchain compatibility problem without a documented downstream probe result.

## Search strategy

1. Check every optional profiling or sanitizer mode for an explicit compile-and-link support test before adding its flags globally.
2. Find executed configuration probes and require loader or runtime failures to be reported separately from negative capability results.
3. Check that API-availability probes include the same headers, feature-test macros, target triple, and deployment level as consuming sources.
4. Inspect generated feature macros and auto-added libraries after a failed probe before allowing dependent compilation.
5. Check sanitizer or profiling runtime libraries against the selected compiler, linker, and C runtime combination.

## Evidence

- [#86434](../micro_taxo/gh_86434.md): An unsupported instrumentation flag was added globally and caused later configuration checks to fail; the remedy was to reject the mode immediately when the compiler cannot accept the flag.
- [#114453](../micro_taxo/gh_114453.md): Profiling made generated probe executables fail at load time, so runtime-dependent checks recorded false results, including an unnecessary library decision and an invalid type-size result that led to a downstream incomplete-type error.
- [#116891](../micro_taxo/gh_116891.md): A sanitizer-enabled configuration misdiagnosed a standard library capability because the compiler runtime package required by the selected instrumentation mode was absent.
- [#143640](../micro_taxo/gh_143640.md): A capability probe reported an API present even though consumer headers hid its declaration for the selected target level; configuring the compiler with the correct target context resolved the mismatch.
- [#150467](../micro_taxo/gh_150467.md): Address instrumentation combined with a particular compiler/runtime toolchain produced final-link unresolved symbols, demonstrating that instrumentation support must include compatible runtime linkage rather than only accepted flags.
