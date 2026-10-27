# A zero-output request is rejected because an irrelevant character-bound parameter is validated before the operation handles the empty-result case.

A text-construction API receives a negative length meaning no characters should be produced, but an independent maximum-character argument is just outside its permitted range. The implementation validates that bound before short-circuiting the zero-output request, causing an internal error instead of returning the empty result.

## Precondition

The operation permits a negative or otherwise zero-output length, while also accepting a maximum-character bound that is invalid but would not affect any produced character.

## Critical operation

The implementation validates the maximum-character bound before determining that the requested output is empty.

## Interference

The out-of-range bound triggers low-level error handling before the empty-result path can return.

## Invalid assumption

Every argument must be validated before considering whether the requested output contains anything to which that argument could apply.

## Failure

A request that should produce an empty result fails with an internal error because an irrelevant bound is rejected prematurely.

## Scope

This is a cautiously scoped singleton pattern based on one report: it applies to text construction with a zero-output length and an independently validated character bound; it does not establish that all invalid arguments should be ignored for empty results.

## Search strategy

1. Check constructors with zero- or negative-length inputs for validation of per-element bounds before the empty-result short circuit.
2. Inspect whether independently supplied range limits are validated even when no elements will be created or processed.
3. Search for empty-output branches that occur after allocation, character-bound, encoding, or shape validation.
4. Verify that invalid parameters irrelevant to a zero-cardinality result are handled consistently with the API's documented empty-result behavior.

## Evidence

- [#140410](../micro_taxo/gh_140410.md): The report demonstrates that a text constructor returns an internal invalid-bound error for a negative-length request with an out-of-range maximum-character value, while the same negative-length request with a permitted bound returns the empty result.
