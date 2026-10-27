# Unchecked runtime type replacement on fixed-size contiguous objects

A runtime permits an object backed by fixed-size contiguous storage to adopt a replacement type without proving that the replacement has an equivalent length, element size, and element representation. The original allocation remains in place, but later indexed or bulk writes use the replacement layout, causing writes beyond the allocation; memory-safety instrumentation then terminates the process.

## Precondition

An object uses a fixed-size contiguous backing allocation, and the runtime permits its type metadata to be replaced after creation.

## Critical operation

Perform type replacement without validating compatibility of the old and new lengths, element sizes, and element representations.

## Interference

The replacement metadata changes how subsequent element access computes storage offsets while the object continues to reference its original allocation.

## Invalid assumption

Later access operations assume that the current type's layout describes an allocation large and correctly represented enough for that layout.

## Failure

An indexed assignment or bulk write computes an out-of-bounds destination and produces a heap buffer overflow, which memory-safety instrumentation detects and uses to terminate the process.

## Scope

This is a cautiously scoped singleton pattern supported by one report. It covers fixed-size contiguous array-like objects with mutable runtime type metadata; it does not establish that all dynamic type replacement or all layout mismatches are vulnerable.

## Search strategy

1. Find mutable type or class replacement paths for objects with inline or contiguous storage, and verify that old and new layouts are compared before replacement.
2. Trace indexed and bulk write operations after type replacement, checking whether offsets and element widths come solely from current type metadata.
3. Check whether compatibility validation compares storage length, total size, and element representation rather than only nominal type identity.
4. Inspect sanitizer-reported heap writes involving objects whose allocation was created under a different type than the one used for access.

## Evidence

- [#143005](../micro_taxo/gh_143005.md): The report demonstrates that replacing an array object's type without matching length, total element storage size, and element type leaves the original allocation in place; a later array assignment interprets that allocation through the incompatible layout and triggers a heap buffer overflow.
