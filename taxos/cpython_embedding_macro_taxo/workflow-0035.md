# Failure-status output pointer is treated as owned cleanup state

A wrapper must make ownership depend on the native call's success status, not merely on whether its result-output pointer is non-null after a failed call.

## Precondition

A native result-producing routine reports failure, while the postcondition for its output pointer on failure is unspecified or does not guarantee a valid caller-owned null value.

## Critical operation

The wrapper routes the failure through shared cleanup that conditionally releases a result pointer.

## Interference

A failing implementation leaves a non-null, stale, or otherwise non-owned value in the output pointer after internally handling partial results.

## Invalid assumption

The cleanup path assumes that a non-null output pointer proves successful ownership transfer, despite the failing status.

## Failure

Cleanup releases storage not owned by the caller, potentially double-freeing or corrupting allocator state and causing a later process crash instead of a recoverable error.

## Scope

Singleton cluster. This pattern is limited to native interfaces whose failure-path output-pointer ownership is absent, ambiguous, or unreliable; the report discusses the triggering implementation as possible rather than conclusively reproducing it.

## Search strategy

1. Audit native calls with result-output pointers and verify the documented output-pointer state for every failure return.
2. Require cleanup ownership checks to be gated by an explicit successful-status or ownership flag, not pointer non-nullness alone.
3. Inspect shared error labels that release result pointers after a call whose status indicates failure.
4. Test wrappers against failing implementations that overwrite output pointers before returning an error.
5. Review error paths for native routines that may internally discard partial results before returning failure.

## Evidence

- [#100795](../micro_taxo/gh_100795.md): The report identifies a wrapper cleanup path that released a non-null result pointer after a failed native lookup; the proposed mitigation clears that pointer on failure to prevent an unexpected release, described as a potential double free with delayed, difficult-to-reproduce crashes. It also notes that the exact failure-output contract was unders
