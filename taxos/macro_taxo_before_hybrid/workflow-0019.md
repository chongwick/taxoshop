# An ownership-transfer mismatch at a conversion boundary lets cleanup decrement a borrowed field repeatedly, corrupting its lifetime accounting and causing a use

An ownership-transfer mismatch at a conversion boundary lets cleanup decrement a borrowed field repeatedly, corrupting its lifetime accounting and causing a use-after-free, invalid free, or related memory failure.

## Precondition

A conversion or serialization path extracts a field through a borrowed-reference interface, including an exceptional or compatibility-selected path, and places that field into a newly returned aggregate.

## Critical operation

Construct the aggregate using an ownership-transferring or reference-stealing convention even though the extracted field was not newly owned.

## Interference

Destruction of the aggregate performs the expected decrement for an owned field; repeated conversions therefore apply extra decrements to the original field, which may be a shared singleton or a separately allocated value.

## Invalid assumption

The extracted field has the ownership state required by the aggregate-construction convention, or the compatibility branch preserves the same ownership semantics across host versions and value shapes.

## Failure

Reference counts become too low or negative, and later garbage collection or global finalization dereferences or frees storage that is already invalid, producing an abort, invalid free, or memory-safety error.

## Scope

The reports share the ownership mismatch and delayed cleanup failure, but differ in the affected value: one is a globally shared singleton reached through a narrow compatibility/subclass case, while the other is a field value in a reduction result. The pattern should therefore target borrowed-to-owned aggregate construction, not singleton corruption specifically.

## Search strategy

1. Inspect every aggregate-construction call that uses a reference-stealing or ownership-transferring format with a value obtained from a borrowed-item accessor.
2. Trace exceptional, subclass, and compatibility branches to verify that their selected format or helper matches the actual ownership of each argument.
3. Audit repeated conversion and aggregate-destruction paths for an extra decrement of shared, static, cached, or otherwise non-owned values.
4. Add cleanup-after-conversion checks that exercise both ordinary heap values and globally shared singleton values under repetition and finalization.

## Evidence

- [#86863](../micro_taxo/gh_86863.md): A compatibility branch selected the wrong path for a subclass-specific ambiguous conversion; that path inserted a borrowed shared value using ownership semantics that caused each repeated conversion to decrement the shared singleton, later leading finalization to attempt an invalid free.
- [#140634](../micro_taxo/gh_140634.md): A reduction helper placed a borrowed structured-field value into a returned aggregate with a reference-stealing format; destroying the aggregate over-decremented the field, and repeated copying or finalization exposed negative reference counts and memory corruption.
