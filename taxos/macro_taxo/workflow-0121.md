# A callback-driven streaming decoder underestimates output capacity when recovery both emits replacement text and resumes from an earlier input position.

A callback-driven streaming decoder underestimates output capacity when recovery both emits replacement text and resumes from an earlier input position.

## Precondition

Malformed input invokes a user-defined recovery callback that can return replacement text and choose a resume position, including one that leaves more input to decode.

## Critical operation

The decoder computes or updates its minimum output-buffer requirement before applying the callback's replacement and revised resume position.

## Interference

The callback emits replacement text while rewinding the input position, increasing the remaining input that will subsequently be decoded.

## Invalid assumption

Capacity accounting assumes an already reserved output unit or accounts only for a replacement-length delta, instead of enforcing space for the full replacement plus all newly remaining input.

## Failure

The decoder's capacity invariant becomes false, causing an internal assertion or abort rather than safely processing the malformed input; the same rewind behavior may also permit non-progressing repeated recovery.

## Scope

This is a cautiously scoped singleton pattern derived from one decoder implementation. It generalizes to callback-based streaming decoders whose recovery handlers can alter both emitted output and the resume position; it does not establish that all rewind-capable recovery designs must be rejected, only that their capacity and progress invariants require explicit handling.

## Search strategy

1. Trace every recovery-callback path that can both return replacement output and modify the resume position.
2. Verify that required capacity includes the full replacement length and the complete remaining input after the callback, including rewinds.
3. Check whether capacity calculations rely on a pre-reserved output character or use replacement_length minus one as an adjustment.
4. Add guards or progress checks for callbacks that resume at the same or an earlier input position, and verify invariant failures cannot abort decoding.

## Evidence

- [#141336](../micro_taxo/gh_141336.md): The report demonstrates that a custom decoder recovery callback returning replacement text and rewinding input leaves the writer one character short because accounting adds only replacement length minus one; it supports the generalized capacity-invariant failure and also records that rewinding can cause non-progressing repeated recovery.
