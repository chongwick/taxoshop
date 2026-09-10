# Zero-count memory transfer through absent or invalid storage

An empty-state or zero-length path reaches a memory-transfer operation with a null, invalid, or improperly aligned pointer, even though no elements are transferred.

## Precondition

The computed transfer count can be zero while the corresponding storage is absent or while pointer derivation produces a pointer that does not satisfy the pointed-to type or library contract.

## Critical operation

Unconditionally form source or destination pointers and invoke a byte/element copy or move primitive using the zero count.

## Interference

The language rules, library contracts, compiler assumptions, and undefined-behavior sanitizers still require valid pointer arguments and may also reject invalid pointer formation or alignment, independently of whether any bytes would be accessed.

## Invalid assumption

A zero transfer count makes every pointer argument irrelevant and therefore permits null, invalid, or misaligned pointers to be passed or formed.

## Failure

Undefined-behavior diagnostics such as nonnull or misalignment reports, with behavior exposed to optimizer-dependent transformations and possible faults if the same path is later used with a nonzero count.

## Scope

The shared mechanism is broader than null pointers: empty representations can yield invalid or misaligned derived pointers, and the problematic operation may be pointer formation as well as the transfer call. The reports concern C-style memory operations and sanitizer/compiler contracts; they do not establish that every zero-length API must accept a null pointer.

## Search strategy

1. Check every zero-length copy or move path for null or absent backing storage before the transfer call.
2. Check whether typed or offset pointers are formed from empty-state storage before testing or using the element count.
3. Check callers that represent empty buffers with null pointers and verify the callee's pointer contract for zero counts.
4. Check sanitizer reports around memory primitives for invalid pointer arguments even when the reported size is zero.

## Evidence

- [#71757](../micro_taxo/gh_71757.md): Multiple empty-container operations computed zero-sized transfers and still passed null storage to memory primitives, producing undefined-behavior sanitizer reports; the remediation was to skip such transfers.
- [#81319](../micro_taxo/gh_81319.md): A zero-argument calling path allowed a null argument array to flow into an unconditional copy, and the sanitizer reported the null source pointer despite a zero copy length.
- [#127563](../micro_taxo/gh_127563.md): An empty internal representation caused a derived typed pointer to be invalid or misaligned before an unconditional zero-sized copy; the report explicitly notes that pointer formation itself can be undefined even without a read.
- [#146196](../micro_taxo/gh_146196.md): A caller supplied a null character pointer with length zero, and the function reached a copy and pointer-processing path until an explicit zero-length early return was added.
