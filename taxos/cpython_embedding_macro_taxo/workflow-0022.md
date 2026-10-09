# Parser format-unit destination-width mismatch overwrites adjacent storage

A variadic argument parser writes a value according to the native C type implied by its format unit, while the caller supplies a fixed-width destination whose storage may be narrower on some platforms.

## Precondition

A parser format unit denotes a native integer type whose width can exceed that of the fixed-width object passed as its output destination.

## Critical operation

Parse the input directly into that fixed-width destination through the variadic parser interface.

## Interference

The parser performs a native-width store that extends past the destination object into adjacent stack storage.

## Invalid assumption

Assuming that a fixed-width integer is interchangeable with the native type required by a parser format unit, regardless of platform-specific type widths.

## Failure

A stack buffer overflow corrupts adjacent memory and is exposed as a sanitizer-detected crash.

## Scope

Singleton cluster. The evidence supports mismatches between variadic parser format-unit destination types and fixed-width integer objects; it does not establish a general rule for unrelated conversion interfaces.

## Search strategy

1. Audit every variadic parser call and verify that each output pointer has exactly the native C type required by its format unit.
2. Flag parser format units for native-width integers when their destinations use fixed-width integer typedefs.
3. Check platform builds where native unsigned long or long differs in width from the intended fixed-width field.
4. Require parsing into the documented native destination type, followed by an explicit checked or intentional conversion to fixed-width storage.

## Evidence

- [#89391](../micro_taxo/gh_89391.md): A native unsigned-integer parser format wrote into a narrower fixed-width destination, producing a sanitizer-reproducible stack buffer overflow; the repair used native parser destinations and explicit casts when assigning to fixed-width fields.
