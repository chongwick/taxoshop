# I’m reading the three detailed analyses and will extract only the mechanism they jointly support.

Unchecked representation-specific access after a weakly validated boundary admits an alternate record or object representation.

## Precondition

A low-level routine receives data from an extensible, weakly typed, heterogeneous, or malformed input boundary, while its implementation relies on a concrete record layout or field type.

## Critical operation

The routine performs a direct typed cast, layout-specific field read, indexing operation, or formatting access without first validating the concrete representation of each input.

## Interference

A refactor, compatibility path, or missing validation allows a wrapper record, duck-typed object, or malformed metadata value to bypass the expected-type check and reach that operation.

## Invalid assumption

Sequence membership, partial protocol compatibility, or a field’s nominal role is incorrectly treated as proof that the value has the exact internal layout and field type required by the accessor.

## Failure

The accessor reads beyond the object or global buffer, producing undefined or nondeterministic data and potentially a sanitizer-detected buffer overflow, segmentation fault, or process termination.

## Scope

The reports share an unchecked boundary between flexible input representations and layout-specific native access. They differ in trigger details—mixed internal records, partial duck typing, and malformed metadata—so the pattern does not require a parser refactor or a particular record kind.

## Search strategy

1. Trace every producer of a low-level consumer’s inputs and verify that concrete element or object types are validated at the boundary.
2. Check heterogeneous sequences for consumers that cast or index every element as one record subtype, especially first or last elements used for metadata.
3. Inspect fast paths for duck-typed or user-defined objects and confirm that representation-specific accessors are guarded by runtime type checks.
4. Review malformed or user-controlled metadata paths for formatters and field readers that assume strings, layouts, or lengths without validation.
5. Compare refactored collection and dispatch paths with their predecessors for lost filtering, wrapper unwrapping, or type checks.

## Evidence

- [#85863](../micro_taxo/gh_85863.md): An iterative argument collector passed a mixed sequence containing wrapper records to code that treated the final item as an expression record, so layout-specific metadata reads crossed the object boundary.
- [#125318](../micro_taxo/gh_125318.md): A native fast path accepted a custom object implementing only part of the expected temporal interface, then read an internal field belonging to the concrete temporal type, causing an out-of-bounds read and possible segmentation fault.
- [#140471](../micro_taxo/gh_140471.md): Malformed field metadata containing a non-string value reached a string-specific formatter, whose representation-dependent length access produced a global-buffer-overflow.
