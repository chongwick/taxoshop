# Native consumers trust extension-controlled results without validating their extent or shape

An extension-controlled callback or overridable helper supplies a pointer, count, or structured result whose usable extent is smaller or less constrained than the consumer assumes; the native consumer performs a bounds-sensitive read without validating that contract.

## Precondition

A native operation consumes data returned by an extension-controlled callback or overridable helper, while the returned pointer lacks an explicit validated extent or the returned value has required cardinality or range constraints.

## Critical operation

The consumer indexes through the supplied pointer, uses a returned count to size a read, or fetches fixed positions from the structured result.

## Interference

Validation checks only a coarse property such as pointer/type identity or numeric convertibility, and omits the corresponding allocation bound, buffer bound, result length, or permitted numeric range.

## Invalid assumption

The implementation assumes that an extension-controlled result satisfying its outer representation or nominal callback contract also contains every element and byte range that the consumer will access.

## Failure

The native path reads outside a live buffer or beyond a result's elements, causing an out-of-bounds read or process crash instead of returning a recoverable validation error.

## Scope

This is a mixed-cluster umbrella pattern. One mechanism is an unbounded index through a callback-provided pointer; the other is unchecked semantic metadata or cardinality from an overridable helper. They share failure to validate the extent required by a native consumer, but the reports do not establish a rule about stale or freed state, ownership leaks, or all callback and override interfaces.

## Search strategy

1. Inspect callbacks that receive raw or derived pointers without an explicit validated extent, and verify every callback-side index is bounded by the original allocation.
2. Trace overridable helpers whose numeric results determine buffer slicing or native-to-managed reads, and check that returned counts are constrained to the destination range before use.
3. Audit callers that validate only an outer container type before retrieving fixed positions, and require an exact length check before positional access.
4. Find native code that converts extension-controlled values into sizes, indexes, or element pointers and verify both representation and semantic bounds are checked.
5. Separate these checks from ownership and lifetime audits: confirm the memory is live, then independently validate pointer extent, count range, and structured-result shape.

## Evidence

- [#140409](../micro_taxo/gh_140409.md): A callback receives pointers into a small live allocation and indexes one pointer far beyond the allocation; downstream element conversion reads outside the heap buffer.
- [#140607](../micro_taxo/gh_140607.md): An overridable read operation returns a byte count larger than the destination buffer or negative; the caller uses the unchecked count to construct the result, causing an out-of-bounds read.
- [#142554](../micro_taxo/gh_142554.md): An overridable helper returns a tuple with the expected outer type but only one element; the caller retrieves two fixed positions without checking length, causing an out-of-bounds read and crash.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0099](../macro_taxo_before_hybrid/workflow-0099.md)
