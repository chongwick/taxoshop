# A callback receives a raw pointer into a heap buffer without its allocation extent, then indexes relative to that pointer and exposes the selected element to a

Unchecked indexing through a raw callback pointer permits managed conversion of an element outside the underlying heap allocation.

## Precondition

A callback interface exposes a raw pointer into a heap allocation without carrying the buffer's valid extent, while callback code can supply an arbitrary element index.

## Critical operation

The callback performs indexed access and passes the resulting position through a native-to-managed conversion that reads the element from memory.

## Interference

The indexed-access or conversion path does not validate that the requested position lies within the original allocation or within the callback's valid element range.

## Invalid assumption

The implementation assumes that every index used with a callback-provided pointer refers to an element in a sufficiently large valid buffer.

## Failure

The conversion reads beyond the heap allocation, producing a heap out-of-bounds read and potentially terminating the process instead of returning a recoverable bounds error.

## Scope

This is a cautiously scoped singleton pattern supported by one report: it covers raw-pointer callback indexing whose downstream element conversion lacks extent validation. It does not establish that all callback APIs or all out-of-bounds accesses share this mechanism.

## Search strategy

1. Inspect callback interfaces that pass raw element pointers without an explicit length or end pointer.
2. Trace every indexed dereference performed on callback-supplied pointers and verify bounds are checked against the original allocation.
3. Check native-to-managed conversion routines for reads that trust a pointer and index without validating the accessible extent.
4. Audit callbacks that receive derived pointers rather than the allocation base for assumptions that the pointer still carries buffer-size information.

## Evidence

- [#140409](../micro_taxo/gh_140409.md): A callback receives pointers into a small heap buffer, applies a deliberately distant index to one pointer, and the element conversion reads beyond the allocation, triggering a heap-buffer-overflow and process abort.
