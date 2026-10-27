# A resource-owning wrapper enters failure cleanup before its resource field has been initialized to a defined empty state.

Failed external-resource construction can leave wrapper cleanup with an indeterminate or unavailable ownership marker, so destructor-based cleanup cannot reliably account for resources involved in the failed attempt.

## Precondition

A wrapper allocates its own state and has a destructor or rollback path that conditionally releases an external resource through a stored handle.

## Critical operation

The wrapper invokes external resource creation and immediately relies on the returned handle to represent all cleanup-relevant state.

## Interference

Creation fails during setup, potentially after the external implementation has performed partial allocation, and returns no usable handle while wrapper teardown still runs.

## Invalid assumption

A failure return or null handle is assumed to mean that no cleanup-relevant state exists, or that the wrapper's handle field is already safely initialized for failure teardown.

## Failure

Failed attempts can leave partial allocations unreclaimed or make cleanup act on stale indeterminate state, producing leaks or unsafe repeated teardown; repeated failures can grow memory usage.

## Scope

This cluster contains one report. It supports a cautiously scoped pattern for wrappers around external resource creation, especially where failure can occur after partial setup and cleanup is destructor-driven; it does not establish that every failed creation returns a hidden usable handle or that every such bug is solely an external-library leak.

## Search strategy

1. Inspect every constructor failure path where a destructor may run before each ownership field is explicitly initialized.
2. Check whether an external create/open call can perform side effects before returning a failure sentinel or null handle.
3. Verify that cleanup state distinguishes no resource acquired from partially initialized or failed acquisition state.
4. Exercise repeated failed creation attempts and inspect whether all underlying allocations are reclaimed.

## Evidence

- [#144069](../micro_taxo/gh_144069.md): The report describes an external database-opening operation that can allocate internal state before failure, while the wrapper is decremented and deallocated without a usable handle; the fix initializes the ownership field before the call and hardens teardown, supporting a failure-path ownership and initialization mismatch pattern.
