# When an out-of-range cursor or slice boundary is normalized to an empty read, the invalid origin is still passed into a lower-level data-access path that is not

Degenerate empty-range requests retain an invalid source position and reach code that assumes a valid nonempty range.

## Precondition

A seekable or sliceable data source permits positions or bounds outside its actual contents, including a position at the numeric limit, and the resulting requested range can be empty.

## Critical operation

Compute or normalize the range length, then continue dispatching the request to the underlying read, copy, or pointer-based access routine.

## Interference

The empty-length result does not short-circuit the operation or sanitize the retained out-of-range origin.

## Invalid assumption

The lower-level routine assumes every request has an in-bounds origin suitable for range assertions and pointer formation, even when the transfer length is zero.

## Failure

The operation triggers a failed boundary assertion or undefined pointer arithmetic instead of returning an ordinary empty result.

## Scope

This pattern is supported by two reports involving in-memory or blob-like data access. It covers empty-range handling with invalid origins; it does not establish that every zero-length operation or every out-of-range access is unsafe.

## Search strategy

1. Check whether empty or negative-length normalization returns immediately before lower-level buffer access.
2. Trace zero-length reads and slices to confirm their origin offset is not still out of bounds.
3. Inspect assertions and pointer arithmetic for unconditional in-bounds assumptions when the transfer length is zero.
4. Test maximum representable positions and out-of-range slice bounds against empty-result behavior.

## Evidence

- [#141311](../micro_taxo/gh_141311.md): A maximum-position seek produced a zero-length read, but the retained position still reached assertions and pointer formation that assumed a usable buffer origin, causing an assertion failure and undefined behavior risk.
- [#142787](../micro_taxo/gh_142787.md): Out-of-range slice bounds produced an empty slice, but the retained start offset still reached a lower-level blob reader whose in-bounds assertion assumed a nonempty valid origin.
