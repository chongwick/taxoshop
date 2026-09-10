# Instrumented configure-time probes fail for environmental reasons and are misclassified as capability results

Optional profiling or sanitizer instrumentation is propagated into configure-time test programs. If the instrumented executable cannot run because its runtime support or platform linkage is unavailable, the probe reports a false negative or a misleading capability error. Later configuration or compilation then fails in a location unrelated to the underlying instrumentation incompatibility.

## Precondition

The build enables optional instrumentation, and the same instrumented compiler/linker flags are applied to small configure-time programs that are compiled, linked, and executed to detect platform or library capabilities.

## Critical operation

Run the generated probe executable and use its exit status or observed result to set a configuration feature or dependency flag.

## Interference

Instrumentation adds a runtime or platform-linkage dependency that is missing or incompatible, causing the probe executable to terminate before testing the requested capability.

## Invalid assumption

A failed instrumented probe reflects absence of the tested capability, rather than failure of the probe's instrumentation runtime or execution environment.

## Failure

Configuration records an incorrect feature or dependency result, producing either an immediate misleading configuration error or a later build failure such as an incomplete conditional type definition being embedded by value.

## Scope

The reports share the probe-execution misclassification mechanism, but their downstream manifestations differ: one reaches a misleading compile-time type error after configuration, while the other stops during configuration with a false library-capability diagnostic. The evidence does not establish that every instrumentation combination fails or that all such failures produce an incomplete-type error.

## Search strategy

1. Trace profiling, sanitizer, coverage, and similar flags into every configure-time compile/link/run probe.
2. Check whether each instrumented probe has the required runtime libraries, loader symbols, and platform support before interpreting its result.
3. Audit probe failure paths to distinguish execution or loader failures from genuine negative capability tests.
4. Find conditionally emitted type definitions controlled by probe results and verify that by-value consumers cannot compile when the probe is falsely negative.

## Evidence

- [#114453](../micro_taxo/gh_114453.md): An optional profiling flag was added to probe commands; on the affected platform the resulting executables failed at load time because of an unresolved runtime symbol. Configuration consequently recorded an incorrect dependency result, and the main build later reported an incomplete conditional type used by value.
- [#116891](../micro_taxo/gh_116891.md): Enabling thread-sanitizer instrumentation caused a library capability probe to report a false negative; the report identified missing compiler runtime support as the remedy. This supports the shared mechanism of instrumented probes failing before testing the requested capability, while the failure may surface directly as a misleading configuration診
