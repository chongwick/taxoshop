# A zero-magnitude numeric object leaves a nominally unused storage unit uninitialized, but a conversion helper reads that unit and incorporates it into scaling—ภ

A zero-magnitude numeric object leaves a nominally unused storage unit uninitialized, but a conversion helper reads that unit and incorporates it into scaling—potentially by multiplying it by the zero magnitude—before producing the converted value.

## Precondition

An object represents zero magnitude while its first numeric storage unit remains uninitialized because the representation treats that unit as unused.

## Critical operation

A value-conversion or compact-value helper unconditionally reads the first storage unit and uses it in arithmetic with the object's magnitude or size.

## Interference

Memory-safety instrumentation tracks the read of the indeterminate unit and treats its propagation through arithmetic as an uninitialized-value use, even when the arithmetic would mathematically cancel it.

## Invalid assumption

The zero magnitude or neutralizing arithmetic is assumed to make reading the unused unit harmless, so the helper is allowed to access it without first checking for zero.

## Failure

The conversion is flagged as an uninitialized-memory use and may abort under instrumentation; the implementation therefore fails sanitizer-instrumented builds or operations despite the intended numeric result being zero.

## Scope

Both reports describe the same underlying case and one explicitly identifies the other as a duplicate. The pattern is scoped to numeric representations with omitted or lazily initialized payload storage and conversion code that reads payload data before guarding the zero-magnitude case; it does not claim that every uninitialized read is neutralized by arithmetic or that every sanitizer report indicates a distinct defect.

## Search strategy

1. Check whether zero-valued numeric objects can retain uninitialized payload units.
2. Inspect conversion helpers for unconditional reads of payload storage before checking magnitude or element count.
3. Search for arithmetic that multiplies, masks, or otherwise neutralizes an indeterminate payload value only after reading it.
4. Run memory-initialization instrumentation through zero-value conversion and compact-representation paths.

## Evidence

- [#102509](../micro_taxo/gh_102509.md): The report identifies a zero-sized numeric representation whose first payload unit is read by a conversion helper and then multiplied by zero; memory instrumentation reports the read, and the eventual fix initializes the unit.
- [#106914](../micro_taxo/gh_106914.md): The report independently describes the same mechanism: a zero-magnitude object's first payload unit may be uninitialized, a compact-value conversion reads it while multiplying by zero, and MemorySanitizer terminates the instrumented operation.
