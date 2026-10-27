# Boundary-unsafe speculative lookahead in text processing.

A text-processing routine inspects a neighboring character while evaluating a multi-element candidate or optimized search path, although the current position may be at the logical input boundary.

## Precondition

The input ends at the current processing position, while a candidate probe or optimized mismatch/skip path may require one additional character.

## Critical operation

The routine uses a pointer or index for the current element and performs candidate probing, mismatch handling, or skip logic that reads the following element.

## Interference

The remaining-length or end-position check is omitted, delayed until after the probe, or not propagated to the helper performing lookahead.

## Invalid assumption

A following character is available whenever the current position is treated as a possible candidate start or search position.

## Failure

The routine reads one element beyond the supplied input, producing an out-of-bounds access detectable by memory-safety instrumentation and potentially terminating the process instead of completing normally.

## Scope

Both reports establish unchecked one-element lookahead at a text-input boundary, but the mechanisms differ: encoding candidate selection versus optimized substring-search skipping. The umbrella pattern is limited to speculative neighboring-character access in boundary-sensitive text processing.

## Search strategy

1. Check every multi-character candidate probe for an explicit remaining-length test before reading the following character.
2. Inspect optimized mismatch and skip branches for current-position-plus-one accesses when the current position can be the final valid position.
3. Verify that helpers receive a buffer and length sufficient for every lookahead they may perform.
4. Exercise candidate misses and multi-character representations exactly at the input boundary under memory-safety instrumentation.

## Evidence

- [#101180](../micro_taxo/gh_101180.md): A character encoder tested multi-character representations through a helper given only the current character; a boundary case caused a read of the next element, requiring bounded input and conditional population of that element.
- [#127971](../micro_taxo/gh_127971.md): An optimized text-search path inspected the character after the current position during mismatch and skip handling, including at the last possible position; an explicit boundary guard removed the out-of-bounds read.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0036](../macro_taxo_before_hybrid/workflow-0036.md)
