# Undefined behavior from left-shifting values in signed integer types before establishing an unsigned bit representation

A signed value is left-shifted to form a bit-positioned representation even though valid inputs can make the operand negative or the shifted result unrepresentable in the signed type.

## Precondition

A bit-positioning operation accepts a value that may be negative or whose required high-order bits exceed the positive range of its signed intermediate type.

## Critical operation

The implementation left-shifts that value while it is still a signed integer, rather than first converting it to an appropriately sized unsigned type.

## Interference

A negative operand or an otherwise nonnegative operand with an unrepresentable shifted result reaches the signed shift.

## Invalid assumption

The code assumes signed shifting yields the intended raw bit pattern and that a later conversion or wrapping behavior makes the preceding shift safe.

## Failure

The shift has undefined behavior and sanitizer-instrumented ordinary execution emits a runtime diagnostic.

## Scope

The shared mechanism is unsafe signed left shifting, not specifically packed state encoding: the reports cover both negative operands and nonnegative operands whose shifted results exceed the signed range, and do not establish one common higher-level data structure or API.

## Search strategy

1. Audit left shifts in signed integer expressions that construct bit-positioned values.
2. Check whether each signed left-shift operand can be negative on any valid path.
3. Check whether the maximum shifted value fits in the signed result type, including use of its top bit.
4. Require conversion to a suitably wide unsigned type before shifting values intended as bit patterns.
5. Exercise startup, build, test, and binary-decoding paths with undefined-behavior shift instrumentation enabled.

## Evidence

- [#65128](../micro_taxo/gh_65128.md): Demonstrates repeated diagnostics for left shifts of negative signed values; the recorded fix converts negative values to an unsigned size type before shifting.
- [#95635](../micro_taxo/gh_95635.md): Demonstrates an ordinary execution path reaching a nonnegative signed left shift whose result cannot be represented in its signed type.
- [#96735](../micro_taxo/gh_96735.md): Demonstrates binary-value assembly reaching a nonnegative signed left shift whose result cannot be represented, with sanitizer instrumentation exposing the undefined behavior.
