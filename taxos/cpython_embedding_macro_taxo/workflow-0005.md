# Sentinel pointer escapes into a generic pointer operation

Empty or absent data is represented by a null, uninitialized, end-of-object, or otherwise non-addressable pointer; a later generic path performs pointer arithmetic, typed pointer formation, or a bulk-memory call before handling that representation explicitly.

## Precondition

A state permits no logical elements or no current buffer/argument storage, while retaining a pointer sentinel that is null or does not satisfy the alignment, provenance, or object-bound requirements of the next operation.

## Critical operation

The implementation derives an offset pointer, reconstructs one during relocation, forms a typed pointer, or passes the sentinel to a bulk-memory routine.

## Interference

A generic copy, argument-packing, resize, or buffer-relocation path processes the sentinel state as though it held an ordinary addressable range.

## Invalid assumption

No bytes being logically transferred, or no eventual dereference occurring, makes pointer arithmetic, typed-pointer formation, and low-level routine arguments harmless even when their pointer preconditions are unmet.

## Failure

Undefined behavior produces null-pointer, pointer-overflow, or misalignment diagnostics and can permit compiler assumptions inconsistent with the sentinel state.

## Scope

The shared mechanism is broader than null bulk copies: it covers sentinel pointers escaping into any operation whose pointer preconditions apply independently of logical data length. The reports do not establish a rule about all empty-state handling outside pointer arithmetic, typed-pointer formation, relocation, and bulk-memory operations.

## Search strategy

1. Trace every nullable or empty-buffer pointer through generic copy, packing, resize, and relocation paths; require an explicit sentinel branch before pointer arithmetic.
2. Guard zero-count bulk-memory operations before constructing their source or destination arguments when either pointer can be null or otherwise invalid.
3. Inspect empty and immutable sentinel layouts used by generic storage code; verify every derived typed pointer has valid alignment and object bounds even for zero elements.
4. When serializing pointers as offsets across buffer replacement, encode null explicitly and restore it without arithmetic.
5. Audit interfaces that permit a null argument vector or data pointer for empty input; normalize it to a valid pointer or ensure all downstream consumers preserve the nullable contract.

## Evidence

- [#71757](../micro_taxo/gh_71757.md): Empty containers reached bulk-copy and move operations with null pointers and zero lengths; fixes skipped those calls, and the report notes sanitizer diagnostics and optimizer concerns.
- [#81319](../micro_taxo/gh_81319.md): A no-argument dispatch path forwarded a null argument array to a zero-length bulk copy; the fix conditioned the copy on a nonzero count.
- [#96678](../micro_taxo/gh_96678.md): An argument-packing path allowed a null argument array and then performed offset arithmetic on it; discussion and fixes establish that the nullable convention was incompatible with downstream pointer operations.
- [#127563](../micro_taxo/gh_127563.md): An empty sentinel layout produced a misaligned typed pointer that was passed to a zero-size bulk copy; the report establishes that forming and passing the invalid pointer remained undefined behavior.
- [#144759](../micro_taxo/gh_144759.md): Null fields representing absent buffer positions were converted to offsets during buffer relocation and later reconstructed with pointer arithmetic, causing pointer-overflow undefined behavior; the fix encoded null separately.
- [#146196](../micro_taxo/gh_146196.md): A zero-length text write could pass a null source pointer to a bulk-memory routine; an early zero-length return removed the undefined behavior.
