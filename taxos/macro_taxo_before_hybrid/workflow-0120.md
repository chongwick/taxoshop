# A buffered position-reporting optimization applies a backward scan after text consumption without accounting for a valid empty buffered state.

A text reader reaches a boundary after consuming input whose line ending can leave its lookahead buffer empty; requesting the current position invokes an optimization that scans backward through buffered data.

## Precondition

A text-reading operation has consumed input ending at a standalone carriage-return boundary, leaving the reader at a valid position with an empty buffered snapshot.

## Critical operation

The position-reporting path computes a nearby restart point and performs a backward skip or scan through the buffered snapshot.

## Interference

The input boundary causes the snapshot used by that optimization to contain zero bytes, even though the position is valid and no unread data remains.

## Invalid assumption

The optimization assumes its buffered snapshot is always nonempty and that the computed backward skip is therefore within the snapshot’s length.

## Failure

An internal bounds assertion fails and aborts position reporting instead of returning the valid current position.

## Scope

This is a cautiously scoped singleton pattern: it is supported for text-stream position reporting when a valid line-boundary state leaves an empty buffered snapshot, specifically including standalone carriage-return endings. The report does not establish that every empty-buffer optimization or every stream API has the same defect.

## Search strategy

1. Check position-calculation fast paths for backward skips that are validated against buffered data without first handling an empty buffer.
2. Search text or stream boundary handling for valid end states that produce empty lookahead snapshots.
3. Trace line-ending normalization paths, especially standalone carriage returns, into buffer-state and position-reporting code.
4. Verify that assertions guarding optimized scans distinguish empty-buffer cases from invalid offsets.
5. Test current-position reporting immediately after consuming input that ends at a standalone line boundary.

## Evidence

- [#141314](../micro_taxo/gh_141314.md): The report documents a position-reporting assertion triggered after reading input ending in a standalone carriage return; the resulting buffered snapshot is empty, while the optimization assumes buffered data exists and validates a backward skip against that empty snapshot. The merged remedy skips the optimization when the snapshot is empty and the
