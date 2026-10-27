# A dynamically extensible numeric or state-restoration boundary admits a value whose concrete type is not validated before it enters an integer-specialized fast/

A dynamically extensible numeric or state-restoration boundary admits a value whose concrete type is not validated before it enters an integer-specialized fast path. The path relies on the value preserving the required integer representation, but caller-supplied state or user-overridable numeric behavior can violate that invariant, causing an internal assertion instead of a recoverable type error or fallback.

## Precondition

An interface accepts externally supplied state or invokes customizable numeric behavior, and the resulting value is not checked against the concrete integer type required by the downstream path.

## Critical operation

The implementation passes that unchecked value into integer-specific normalization, arithmetic, or comparison logic.

## Interference

The supplied state is non-integer, or an overridable numeric operation returns a non-integer value despite originating from an integer-like operand.

## Invalid assumption

The downstream implementation assumes that the value still has the expected integer representation and satisfies its internal numeric invariants.

## Failure

An internal assertion is triggered during the specialized path rather than producing a recoverable type error or selecting a safe fallback.

## Scope

The shared pattern is limited to dynamically extensible or externally supplied values crossing into representation-specific integer fast paths without validation. The reports differ in whether the unexpected value is supplied directly or produced by an overridden operation; this taxonomy does not claim that every type mismatch or every assertion failure has the same cause.

## Search strategy

1. Inspect state-restoration entry points for externally supplied values that reach integer-only arithmetic without an exact-type check.
2. Trace results of overridable numeric operations before they enter code that assumes an integer representation.
3. Search assertions in numeric fast paths whose operands originate from callbacks, special methods, or deserialization/state inputs.
4. Verify that unexpected result types produce an explicit error or fallback before invariant-dependent operations begin.

## Evidence

- [#141312](../micro_taxo/gh_141312.md): A state-restoration entry point accepted non-integer input and passed it into integer-specific range-state arithmetic, where the unchecked representation assumption caused an assertion failure; adding validation changed the outcome to a type error.
- [#143006](../micro_taxo/gh_143006.md): A numeric comparison path invoked user-overridable negation on an integer-derived operand, received a non-integer result, and then reached logic assuming an integer result; the fix removed or guarded that assumption to prevent the assertion.
