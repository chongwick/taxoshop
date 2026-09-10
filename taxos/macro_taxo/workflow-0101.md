# A collector-visible object is registered before all traversal-relevant fields are initialized; a setup-time operation triggers collection during this partial-in

A collector-visible object is registered before all traversal-relevant fields are initialized; a setup-time operation triggers collection during this partial-initialization window, and traversal dereferences an uninitialized field.

## Precondition

An object is registered for automatic collection before every field that collector traversal may read has been initialized to a valid state.

## Critical operation

A subsequent setup or metadata-computation operation can allocate, invoke callbacks, or otherwise trigger collection.

## Interference

Collection runs while object initialization is still incomplete.

## Invalid assumption

The collector assumes that every registered object already has valid values in all traversal-relevant fields.

## Failure

Traversal reads the uninitialized field as valid state and dereferences it, causing a segmentation fault instead of safe collection.

## Scope

This is a singleton cluster, so the pattern is cautiously scoped to collector traversal of partially initialized registered objects and does not establish a broader rule for unrelated initialization-order failures.

## Search strategy

1. Check whether objects become collector-visible before all fields read by traversal callbacks are initialized.
2. Trace constructor and setup operations for allocations or callbacks that can trigger collection between registration and final initialization.
3. Verify that traversal code validates optional or not-yet-initialized child state before dereferencing it.
4. Audit managed-object creation paths for a registration-before-initialization ordering gap.

## Evidence

- [#140431](../micro_taxo/gh_140431.md): The report states that newly created managed execution objects were tracked before all traversal-accessed fields were initialized; a later origin or metadata computation could trigger collection, whose traversal read the missing field and crashed.
