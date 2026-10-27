# Unchecked boundary inputs bypass validation before low-level arithmetic, pointer, representation, or fixed-format encoding

Boundary-case inputs or derived states reach low-level operations before the invariant required by that operation has been established.

## Precondition

An input or internal state can be null, empty, out of range, malformed, or numerically extreme, such as an absent storage base, invalid encoded value, overflowing timestamp, or position outside available data.

## Critical operation

The implementation performs pointer arithmetic, direct representation access, signed shifting or arithmetic, timestamp conversion, or fixed-width packing using that state.

## Interference

A missing, asymmetric, or delayed validation/normalization path allows the boundary state to bypass the code that should establish pointer, range, numeric, or representation invariants; alternate entry points and exceptional conversions can expose the gap.

## Invalid assumption

The low-level operation assumes its pointer, offset, numeric value, encoded field, or converted representation is already valid and within its supported domain.

## Failure

Undefined behavior is reported through null or overflowing pointer operations, invalid representation loads, signed overflow, or shifts; related paths can instead raise an obscure downstream encoding error, fail to clamp extreme values, or produce a non-round-trippable representation.

## Scope

This pattern generalizes the shared invariant failure, not one specific data type or operation. The first report is an umbrella of heterogeneous sanitizer findings, while the second concerns timestamp-range validation and delayed encoding; the commonality is boundary state reaching an operation whose preconditions were not established.

## Search strategy

1. Trace every low-level pointer, offset, shift, and fixed-width packing operation back to its input and verify null, empty, range, and overflow checks occur first.
2. Search alternate constructors, setters, conversion paths, and exception handlers for inputs that bypass the primary validation or normalization routine.
3. Check all boundary clamps and encoded upper limits against the target representation's actual precision and round-trip behavior.
4. Inspect sanitizer findings involving null pointers, invalid enum or boolean representations, signed overflow, pointer overflow, and out-of-range packing for missing precondition enforcement.

## Evidence

- [#148286](../micro_taxo/gh_148286.md): The sanitizer findings cover null member access, invalid representation loads, signed overflow and shifts, and pointer arithmetic involving null or overflowing offsets, demonstrating that boundary or invalid states reached low-level operations without their required invariants.
- [#154667](../micro_taxo/gh_154667.md): Extreme and out-of-range timestamps bypassed consistent validation or clamping, causing conversion failures and later fixed-format packing errors; the proposed correction validates at entry points and clamps to a representable, round-trippable bound.
