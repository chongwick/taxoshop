# Empty-result operations leak invalid metadata into nonempty validation or access paths

An operation determines that no output or data transfer is needed, but associated bounds, origins, or buffered state remain invalid or empty and are processed by logic intended for nonempty work.

## Precondition

The requested result has zero cardinality because of a negative length, normalized empty range, boundary position, or valid empty buffered state, while an associated parameter, origin, or snapshot is out of range or has no data.

## Critical operation

The implementation performs ordinary argument validation, lower-level access, pointer formation, or optimized scanning before completing the zero-result case.

## Interference

Zero cardinality does not short-circuit the operation or make the associated metadata safe for the nonempty path.

## Invalid assumption

Checks and routines used for nonempty work may require valid bounds, in-range origins, or nonempty backing data even when no output, transfer, or scan is required.

## Failure

A logically valid empty operation raises an internal error or assertion, or risks invalid pointer/arithmetic behavior, instead of returning an empty result or valid position.

## Scope

The common pattern is missing empty-state short-circuiting or sanitization, with two supported mechanisms: irrelevant parameter validation can precede the empty-result decision, while invalid origins or empty buffers can reach lower-level access or optimization code. These mechanisms should be distinguished during review; the reports do not establish that every invalid argument must be ignored for every empty operation, nor do they concern leaked ownership or stale/freed state.

## Search strategy

1. Check zero-length and empty-range branches for immediate completion before argument validation that only affects produced elements.
2. Trace normalized out-of-range positions and slice bounds into lower-level reads, copies, pointer arithmetic, and assertions.
3. Inspect optimized scans and position calculations for valid empty buffers that still execute nonempty-buffer assumptions.
4. Test negative lengths, maximum positions, beyond-end bounds, and empty buffered states for ordinary empty-result behavior.
5. Separate irrelevant-parameter validation failures from invalid-origin or empty-buffer access failures when reviewing fixes.

## Evidence

- [#140410](../micro_taxo/gh_140410.md): A negative-length construction request correctly implies no output, but an independently invalid maximum-character bound is validated first and causes an internal error instead of the empty result.
- [#141311](../micro_taxo/gh_141311.md): A position at the numeric maximum makes the effective read length zero, but the retained position still reaches pointer formation and assertions requiring an in-range origin, creating assertion and undefined-behavior risk.
- [#141314](../micro_taxo/gh_141314.md): A valid text-reader state leaves an empty buffered snapshot, yet position reporting runs a backward-scan optimization that assumes buffered data exists and fails an internal bounds assertion.
- [#142787](../micro_taxo/gh_142787.md): Out-of-range slice bounds normalize to an empty slice, but the retained start offset is passed to a lower-level reader whose in-bounds assertion assumes a valid nonempty access.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0100](../macro_taxo_before_hybrid/workflow-0100.md)
- [workflow-0118](../macro_taxo_before_hybrid/workflow-0118.md)
- [workflow-0120](../macro_taxo_before_hybrid/workflow-0120.md)
