# Unchecked speculative lookahead at a character-sequence boundary

Text-processing code performs a lookahead read while selecting a multi-unit representation or applying a search heuristic, without ensuring that the next element is within the supplied sequence.

## Precondition

A character-sequence operation reaches its final available element or invokes a lookahead-capable helper with only the current element available.

## Critical operation

The operation speculatively examines the following element to choose an encoding or determine a search skip.

## Interference

The lookahead path runs when no following in-bounds element exists.

## Invalid assumption

The implementation assumes the next-element address is readable without independently validating the sequence boundary or providing sufficient probe storage.

## Failure

An out-of-bounds read occurs, detected by memory-safety instrumentation or potentially causing a crash or undefined behavior.

## Scope

The shared mechanism is boundary-unsafe speculative lookahead in character-sequence processing; the reports differ in whether the lookahead supports encoding selection or search skipping.

## Search strategy

1. Find next-element indexing or pointer lookahead in character-processing loops and verify the next position is in bounds before dereference.
2. Find callbacks or helpers passed only a current-element address and verify their maximum lookahead fits the supplied buffer.
3. Test failed-match and multi-element-mapping paths at the final input position under address-safety instrumentation.

## Evidence

- [#101180](../micro_taxo/gh_101180.md): An encoding designation probe could inspect a second character despite receiving storage for only the current character; supplying a two-element buffer prevented the out-of-bounds read.
- [#127971](../micro_taxo/gh_127971.md): String-search skip logic inspected the element after the final viable match position; adding an explicit boundary check prevented the one-past-end read.
