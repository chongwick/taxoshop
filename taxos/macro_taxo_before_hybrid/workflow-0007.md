# Using raw storage or an address with insufficient alignment for a stricter-aligned typed object or access

Code uses storage whose guaranteed alignment is weaker than the alignment required by the type being placed or accessed, including addresses shifted within otherwise valid storage.

## Precondition

An allocator, byte buffer, generated-code region, or derived address does not guarantee the alignment required by a typed object or typed load/store.

## Critical operation

Place the object there or convert the address to a pointer for the stricter-aligned type and perform a typed read or write.

## Interference

Allocator guarantees, packed or byte-oriented layouts, and address offsets can leave the effective address misaligned even when the surrounding storage is valid and large enough.

## Invalid assumption

Treating raw byte accessibility, allocation success, object size, or tolerance on a particular processor as evidence that typed alignment requirements are satisfied.

## Failure

The operation has undefined behavior and may be diagnosed by alignment sanitizers, miscompiled under compiler alignment assumptions, or cause a runtime fault.

## Scope

The cluster supports a general raw-storage alignment mismatch pattern, not only allocator-backed object placement. The two JIT reports are closely related manifestations of unaligned typed memory access, while the allocator report demonstrates the same contract failure at object allocation; the pattern does not claim that every unaligned byte operation is invalid.

## Search strategy

1. Check every custom or pool allocator against the maximum alignment required by objects it may serve.
2. Check every typed pointer cast from byte storage or an arbitrary address for a proven alignment guarantee.
3. Check pointer arithmetic and packed layouts to ensure offsets preserve the target type's alignment.
4. Replace alignment-sensitive raw-memory loads and stores with an alignment-safe representation or byte-copy operation when alignment is not guaranteed.

## Evidence

- [#72174](../micro_taxo/gh_72174.md): A pool allocator supplied weaker alignment than required by a structure containing a stricter-aligned member, producing sanitizer-reported misaligned member access and motivating a stronger allocator alignment.
- [#139269](../micro_taxo/gh_139269.md): Typed reads and writes through casts targeted byte-oriented locations at unaligned offsets; sanitizers reported misaligned accesses and the fix used alignment-agnostic byte copies.
- [#139834](../micro_taxo/gh_139834.md): The same class of unaligned typed JIT accesses was observed during ordinary execution, with sanitizer reports preceding a segmentation fault in generated-code execution.
