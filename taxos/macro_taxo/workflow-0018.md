# Optional toolchain-specific instrumentation is enabled without confirming compiler support.

A build configuration enables an optional feature whose required compiler flags may be unsupported by the selected toolchain.

## Precondition

An optional instrumentation feature requiring compiler-specific flags is selected.

## Critical operation

The configuration unconditionally appends the feature's compiler and linker flags before validating that the selected toolchain accepts them.

## Interference

Those unsupported flags are inherited by a later compile or dependency capability probe, causing that probe to fail.

## Invalid assumption

The downstream probe failure is treated as evidence of a missing capability or dependency rather than as evidence that the feature-specific flags are incompatible with the toolchain.

## Failure

Configuration aborts with a misleading downstream check error instead of explicitly reporting that the selected toolchain does not support the requested feature.

## Scope

Singleton cluster: scoped to build configuration flows where optional compiler-specific flags are propagated into later probes before compatibility validation; it does not generalize to all misleading configuration failures.

## Search strategy

1. Check whether optional feature flags are added before compiler compatibility is validated.
2. Trace whether feature-specific compiler and linker flags leak into unrelated capability or dependency probes.
3. Verify that unsupported toolchain options produce an explicit feature-compatibility diagnostic.
4. Inspect probe setup to ensure downstream checks are not invalidated by unverified optional flags.

## Evidence

- [#86434](../micro_taxo/gh_86434.md): The report shows that enabling a compiler-specific sanitizer added incompatible flags under an unsupported compiler, causing a later address-resolution capability check to fail; the fix added an upfront compile-flag check and explicit incompatibility error.
