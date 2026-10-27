# Format-driven native-width parsing into narrower fixed-width storage

A format-based argument parser writes an integer using the width of a native type into a destination object declared with a fixed-width integer type.

## Precondition

A parser accepts a format specification and caller-provided destination pointers, and a native integer type named by the format can be wider than the fixed-width destination on some supported ABI.

## Critical operation

The parser stores the parsed value according to the format unit's native integer width at the destination address.

## Interference

The destination object is narrower than the width used by the parser, so the store extends beyond the object's bounds into adjacent memory.

## Invalid assumption

Code assumes that matching numeric range or apparent integer compatibility makes a native-width format unit safe for a fixed-width integer object.

## Failure

The out-of-bounds store corrupts adjacent stack memory and can be detected as a stack-buffer-overflow or cause later process termination.

## Scope

This cluster contains one report, so the pattern is scoped to format-driven integer parsers whose native-width storage contract is violated by fixed-width destinations; it does not establish that every parser or every integer conversion has this failure mode.

## Search strategy

1. Inspect every format-driven integer parse and compare each format unit's documented native storage width with the exact destination object's type and size.
2. Search for fixed-width integer objects passed by address to parsers whose format units name native short, int, long, or long-long types.
3. Review code on ABIs where native integer widths differ, and verify that each parser destination is either the exact native type or parsed through a width-matched temporary.
4. Check sanitizer reports and stack layouts around parser calls for writes larger than the declared destination object.

## Evidence

- [#89391](../micro_taxo/gh_89391.md): The report attributes the stack overflow to a native-width unsigned-integer format unit receiving a pointer to a narrower fixed-width integer object; the parser consequently wrote past that object, and the fix changed both the destination declarations and format units to width-compatible types.
