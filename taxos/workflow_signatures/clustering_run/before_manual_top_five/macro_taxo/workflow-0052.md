# Unchecked failure results contaminate downstream processing and error-recovery paths

A low-level conversion, coercion, probe, or dependency lookup reports failure through an error sentinel, pending exception, or missing result, but its caller continues into later control flow. The downstream path then treats invalid state as usable, converting a recoverable argument, loading, or runtime error into an internal assertion, SystemError, or crash.

## Precondition

A reconfiguration or runtime-support path invokes an operation that may fail while converting a value, probing alternatives, or retrieving a required dependency; failure is represented by a sentinel or absent result and may leave an exception pending.

## Critical operation

The caller does not immediately distinguish failure from a valid result before branching, attempting a fallback, or invoking the returned value.

## Interference

The failure state reaches subsequent logic: an error sentinel may be coerced into a valid boolean/status, a pending exception may remain set during another probe or call, or a missing dependency may be passed to a call operation.

## Invalid assumption

The caller assumes that the helper or lookup succeeded, produced a usable result, and left no pending exception, instead of treating failure as an immediate exceptional path or explicitly preserving and propagating the original error.

## Failure

Downstream code mishandles the sentinel, calls an absent value, or invokes another operation with an exception already pending, causing an internal assertion or SystemError, aborting, or crashing instead of reporting the original recoverable error.

## Scope

The cluster combines two related but distinct mechanisms: unchecked conversion/coercion or probe failures that leave a sentinel and/or pending exception, and an unchecked dependency lookup in a fallback diagnostic path that yields no callable result. The shared pattern is failure-result validation and error-state propagation, not leaked ownership or stale/freed memory; it does not claim that all downstream crashes have one identical helper or representation.

## Search strategy

1. Inspect conversion, coercion, probe, and attribute-lookup helpers for sentinel or null results that also establish an exception.
2. Verify that every caller checks failure immediately before branching, retrying, falling back, or invoking another operation.
3. Check whether negative or null failure results can be coerced into ordinary boolean/status values or passed as callable dependencies.
4. Trace fallback probes and diagnostic paths to ensure they explicitly clear, preserve, or propagate pending exceptions before continuing.
5. Exercise invalid arguments, failing conversions, failed first probes, and removed support dependencies to confirm recoverable errors survive downstream handling.

## Evidence

- [#111942](../micro_taxo/gh_111942.md): Invalid reconfiguration arguments and conversions could fail without immediate handling; later processing used the invalid state and crashed instead of returning the argument or conversion exception.
- [#140650](../micro_taxo/gh_140650.md): A user-provided state value that raised or could not be converted to a boolean produced an error sentinel that downstream closed-state logic treated as a valid result, causing a SystemError rather than propagating the TypeError or original exception.
- [#141307](../micro_taxo/gh_141307.md): A failed initial symbol probe left an exception pending while alternate probing and module creation continued, eventually reaching an internal call assertion instead of returning the loading error.
- [#142737](../micro_taxo/gh_142737.md): Fallback traceback handling looked up a required support operation after it had been removed, failed to validate the missing result, and later attempted to call it, triggering an assertion instead of displaying the original exception.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0044](../macro_taxo_before_hybrid/workflow-0044.md)
- [workflow-0133](../macro_taxo_before_hybrid/workflow-0133.md)
