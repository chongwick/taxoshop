# A caller relies on a failed native out-parameter remaining null to decide whether shared cleanup may release a result.

A failed native lookup can leave its output parameter non-null or otherwise unusable, and generic cleanup may mistake that value for an owned successful result.

## Precondition

The caller initializes an output pointer and routes both success and failure through cleanup that conditionally releases it.

## Critical operation

Invoke a native lookup through an output parameter and branch on its error status.

## Interference

The callee or platform implementation changes the output parameter before returning an error, possibly after internally discarding temporary state.

## Invalid assumption

The caller assumes that a non-null output after failure is a valid, caller-owned result whose release is required and safe.

## Failure

Shared cleanup performs a duplicate or invalid release, corrupting allocator state; a later lookup or memory access may then crash instead of returning the original recoverable error.

## Scope

Singleton report. It supports a narrowly scoped pattern for native lookup APIs with ambiguous out-parameter state on failure; the report's original crash was not conclusively proven to have this mechanism as its root cause.

## Search strategy

1. Inspect every native out-parameter call whose failure path reaches cleanup, and verify the callee contract defines the output value and ownership on error.
2. Trace whether cleanup is selected solely by a non-null out pointer rather than by a confirmed successful return and transferred ownership.
3. Check whether the callee can allocate, clean up, or partially populate the output before reporting failure, including platform-specific implementations.
4. Review failure-path tests under alternate native-library implementations for double release, invalid free, heap corruption, or leaks.

## Evidence

- [#100795](../micro_taxo/gh_100795.md): The report documents a lookup wrapper that conditionally released an output pointer after a failed native call; discussion identified that an implementation could leave the pointer non-null or garbage, causing an unexpected duplicate or invalid release. The proposed fix treated the failed output as invalid, while maintainers noted the original user
