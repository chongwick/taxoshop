# Boundary-sensitive text processing performs speculative lookahead for a multi-element candidate without first proving that the next element lies within the user

A text-processing fast path examines a neighboring character while testing a multi-character encoding or search candidate, but the current position may be at the logical end of the input.

## Precondition

The input ends at the current processing position, while the selected candidate probe or skip heuristic may require reading one additional character.

## Critical operation

The routine performs candidate probing, mismatch handling, or search skipping using an unvalidated next-element access.

## Interference

Boundary validation is omitted, delayed until after the probe, or the probe receives a pointer that represents only the current element even though the candidate logic assumes a following element is available.

## Invalid assumption

A following character exists whenever the current position is treated as a possible candidate start.

## Failure

The routine reads one element beyond the input boundary, producing an out-of-bounds access detectable by memory-safety instrumentation and potentially causing a process-terminating fault; functional correctness may otherwise appear unaffected.

## Scope

The reports share an unchecked one-element lookahead at an input boundary, but differ in purpose: one occurs during multi-character encoding candidate selection and the other during optimized substring-search skipping. The pattern is scoped to text-processing routines with speculative neighboring-character access, not to encoders alone.

## Search strategy

1. Check every multi-character candidate probe for an explicit remaining-length test before reading the following character.
2. Inspect optimized search skip and mismatch branches for accesses at current_index + 1 when current_index can equal the final valid position.
3. Verify that helper routines receive a buffer and length sufficient for every lookahead they may perform.
4. Exercise candidate misses and multi-character representations exactly at the input boundary under address sanitization.

## Evidence

- [#101180](../micro_taxo/gh_101180.md): A character encoder tested candidate representations through a path that could inspect a second character even when only the current character was supplied; a combining-character boundary case caused an out-of-bounds read, fixed by providing bounded two-element input and populating the second element only after confirming it exists.
- [#127971](../micro_taxo/gh_127971.md): Optimized string-search mismatch and skip paths unconditionally inspected the character after the current search position, including when that position was the last possible pattern start; adding a boundary guard prevented the one-past-end read.
