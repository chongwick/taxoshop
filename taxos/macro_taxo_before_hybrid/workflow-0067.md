# A short-lived build-time helper retains allocations owned by initialized runtime configuration, so leak checking converts completed generation into a failed‌‍‌‍

A short-lived build-time helper retains allocations owned by initialized runtime configuration, so leak checking converts completed generation into a failed build.

## Precondition

A build-time executable initializes runtime configuration whose scalar, list, registration, or other nested fields can allocate independently.

## Critical operation

The helper performs its generation task and then destroys the configuration through an incomplete cleanup path.

## Interference

Leak-detection instrumentation inspects allocations still reachable or outstanding when the helper exits and treats them as leaks.

## Invalid assumption

Releasing the outer configuration object, or relying on the process being short-lived, is assumed to release or harmlessly discard all allocations owned by its nested state.

## Failure

The helper exits nonzero after leak reporting, causing the build target to fail even though generation produced its intended output.

## Scope

The shared pattern is incomplete cleanup of sanitizer-visible state in short-lived build helpers. The reports do not establish that every allocation in the older sanitizer report had the same configuration-specific root cause, so the pattern should not be generalized to all build-time leaks.

## Search strategy

1. Find build-time executables that initialize runtime or configuration state and trace their exit cleanup.
2. For every owned configuration field, verify that cleanup releases both the field value and any nested list elements, arrays, or registration storage.
3. Search sanitizer-enabled build commands for helpers whose leak-checking exit status is propagated to the build system.
4. Compare each allocation API used during configuration setup with the matching deallocator on every success and failure path.

## Evidence

- [#121847](../micro_taxo/gh_121847.md): A sanitizer-enabled build helper completed generation but reported outstanding allocations at process exit and failed the build; later investigation also connected the affected newer configuration path to missing deep cleanup, while noting that older-version leaks could include separate runtime allocations.
- [#138756](../micro_taxo/gh_138756.md): A build-time helper allocated configuration strings and related state, but its free routine released only the enclosing object and omitted owned members; leak detection then caused the generation target to fail until deep cleanup was added.
