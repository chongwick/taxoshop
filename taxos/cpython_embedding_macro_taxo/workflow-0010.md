# Unchecked out-of-range floating-point conversion to a narrower numeric representation

A finite floating-point value that may not fit the destination representation is converted before its representability is established, relying on an out-of-range conversion whose behavior is undefined.

## Precondition

A finite floating-point value, possibly after rounding or scaling, can lie outside the range representable by the intended narrower floating-point or integral destination.

## Critical operation

The implementation performs the floating-point narrowing or floating-point-to-integral conversion before checking that the source value fits the destination range.

## Interference

For an out-of-range source, the language leaves the conversion behavior undefined; compiler, platform, or optimization choices may therefore change the produced result or invalidate reasoning based on it.

## Invalid assumption

The converted value is assumed to be a reliable value or overflow indicator that can safely be inspected afterward to detect overflow or preserve existing conversion behavior.

## Failure

Overflow handling becomes unreliable and the program invokes undefined behavior, producing sanitizer findings or behavior that can vary with the build environment.

## Scope

The shared mechanism is out-of-range floating-point conversion before validation. The reports cover both narrowing floating-point conversions and conversions from floating point to integral representations; they do not establish a rule for conversions between already-integral types.

## Search strategy

1. Find every cast from floating-point to a narrower floating-point or integral type, and require a range check before the cast.
2. Trace rounded, scaled, or decomposed floating-point intermediates into numeric casts, and verify that each intermediate fits its destination.
3. Inspect overflow detection that compares a value after conversion with its source, and replace it with pre-conversion representability validation.
4. Audit uses of converted infinities, wraparound-like results, or conversion errors as overflow sentinels, and ensure the conversion itself is defined first.

## Evidence

- [#75554](../micro_taxo/gh_75554.md): Shows multiple floating-point demotions and floating-point-to-integral conversions where conversion preceded overflow detection; the remediation adds destination-range checks before conversion and handles an out-of-range floating narrowing without performing the invalid conversion.
- [#77756](../micro_taxo/gh_77756.md): Reports sanitizer-detected float-cast-overflow at several floating-point conversion sites, notes that compiler optimization changes can alter prior undefined behavior, and identifies the need for defined conversion or explicit error handling.
