# Unchecked failure from a conversion, coercion, or probe helper leaves an error pending; later control flow treats the result as valid and reaches a downstream-­

A low-level helper reports failure through a sentinel and pending error, but its caller continues as though it produced a valid result. Subsequent logic then violates the error-state contract and fails catastrophically instead of propagating the original argument or lookup error.

## Precondition

A reconfiguration, state-check, or loading operation invokes a helper that may fail while converting, coercing, accessing, or probing a value, leaving an error indicator pending and returning an error sentinel.

## Critical operation

The caller consumes the helper's result without immediately testing the failure sentinel, or proceeds to another operation while the helper's error remains pending.

## Interference

The pending error contaminates later branching, conversion, fallback probing, or invocation; an error sentinel may also be misinterpreted as an ordinary truthy or usable result.

## Invalid assumption

The caller assumes the helper produced a valid result and that downstream operations begin with no pending error, instead of treating the sentinel and error state as an immediate exceptional path.

## Failure

Downstream code overwrites or mishandles the original error, dereferences invalid state, triggers an internal consistency failure, or aborts/crashes rather than returning the appropriate recoverable exception.

## Scope

The reports differ in the helper involved—argument conversion, boolean coercion, and fallback symbol probing—but share the same error-state propagation defect. The pattern is scoped to callers of helpers whose failure is represented both by a sentinel/result and a pending error; it does not assert that every downstream crash has this cause.

## Search strategy

1. Inspect every conversion, coercion, attribute access, and lookup helper for an error sentinel paired with a pending error.
2. Verify that callers test failure sentinels immediately before branching, continuing, or invoking another helper.
3. Check whether error sentinels can be mistaken for valid boolean, pointer, index, or status results.
4. Trace fallback paths to ensure they explicitly preserve, clear, or propagate pending errors before making another call.
5. Add adversarial tests where conversion or lookup raises, returns an invalid type, or fails on the first probe.

## Evidence

- [#111942](../micro_taxo/gh_111942.md): Invalid reconfiguration arguments and failing value conversions were allowed to continue into later processing, producing crashes instead of the corresponding argument or conversion exception.
- [#140650](../micro_taxo/gh_140650.md): A state query whose value could not be converted to a boolean returned an error sentinel that callers treated as a valid closed-state result, causing internal error handling to fail; checking the sentinel restored exception propagation.
- [#141307](../micro_taxo/gh_141307.md): A failed first probe left an error pending while a fallback probe and subsequent call proceeded, ultimately reaching an internal assertion; clearing or propagating the probe error yielded a normal loading exception.
