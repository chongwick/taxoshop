# Malformed compact location metadata reaches unchecked or assertion-only decoders

Compact location metadata is treated as trusted internal data even when truncated, incompatible, or structurally inconsistent. Release decoding can overread the logical buffer, while invariant checks in diagnostic paths can terminate the process instead of reporting malformed input.

## Precondition

An attacker, tool, serialized artifact, or low-level object-construction path can provide compact metadata that is truncated, foreign-format, or inconsistent with the associated instruction data.

## Critical operation

A lazy iterator or diagnostic decoder parses variable-length location records to produce source positions, line ranges, or related derived metadata.

## Interference

The decoder either advances and reads record fields without proving that enough bytes remain, including after zero-progress records, or reaches assertion-based cursor and continuation checks before malformed input has been rejected.

## Invalid assumption

The implementation assumes metadata was produced in a canonical format, that each record is complete, and that structural invariants can safely be enforced with assertions rather than validated as recoverable input.

## Failure

One mechanism interprets adjacent memory as additional metadata and can expose unrelated values or cause downstream memory corruption and crashes; the other aborts on an internal assertion when malformed metadata violates decoder invariants.

## Scope

The cluster is mixed rather than a single failure mechanism: issues 99974, 99975, and 121112 establish unchecked logical-boundary decoding and adjacent-memory or corruption consequences, while issues 140935, 142736, and 143430 establish assertion-only rejection of malformed low-level metadata. The reports support a pattern for compact executable-location metadata readers and diagnostic iterators, not all parsers, and do not justify conflating adjacent-memory reads with stale or freed-state use.

## Search strategy

1. Check every variable-length record and fixed-width field read for a logical remaining-length proof before cursor advancement.
2. Inspect zero-progress, terminator, continuation, and retry loops to ensure they cannot read another record after the payload is exhausted.
3. Find diagnostic decoders whose cursor, continuation, or derived-state assertions can be reached from externally constructed or foreign metadata before validation.
4. Exercise truncated, incompatible, and instruction-count-mismatched metadata in release and debug builds and require a recoverable malformed-input result rather than adjacent-memory reads, corruption, or process termination.

## Evidence

- [#99974](../micro_taxo/gh_99974.md): A truncated continuation-encoded location payload caused variable-length fields to be read beyond the logical buffer, exposing adjacent heap bytes as derived position data.
- [#99975](../micro_taxo/gh_99975.md): A record with zero decoded address progress caused iteration to retry after the valid payload ended and read additional bytes outside the logical metadata buffer.
- [#121112](../micro_taxo/gh_121112.md): Foreign serialized executable metadata reached the same unchecked location decoder through a tooling path, producing memory-integrity failures and crashes; the report later explicitly identified the missing bounds checks.
- [#140935](../micro_taxo/gh_140935.md): Structurally invalid continuation bytes supplied through low-level object construction reached diagnostic decoding and triggered an internal assertion.
- [#142736](../micro_taxo/gh_142736.md): A one-byte location table attached to an executable object violated cursor and continuation invariants during diagnostic parsing and aborted on assertion.
- [#143430](../micro_taxo/gh_143430.md): Metadata too short for the associated instruction stream reached position iteration and triggered the decoder's cursor and state assertions.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0032](../macro_taxo_before_hybrid/workflow-0032.md)
- [workflow-0116](../macro_taxo_before_hybrid/workflow-0116.md)
