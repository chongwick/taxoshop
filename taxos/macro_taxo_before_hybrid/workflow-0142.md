# Increasing a trace-length limit beyond the generated-code subsystem’s supported size can produce invalid executable metadata that later cleanup cannot safely un

A trace-size configuration exceeds the generated-code capacity, allowing a trace whose compiled representation is too large for reliable metadata/instruction bookkeeping; cleanup then encounters metadata that no longer identifies the expected entry instruction and crashes.

## Precondition

A tracing optimizer permits traces larger than the generated-code subsystem’s machine-code or representation limits.

## Critical operation

The optimizer records and compiles an unusually long trace into executable code.

## Interference

The generated-code size limit is reached or exceeded, leaving executable metadata inconsistent with the generated instruction sequence or its entry location.

## Invalid assumption

Cleanup assumes every executable has intact metadata pointing to the expected entry instruction.

## Failure

Detaching or invalidating the executable dereferences invalid metadata and triggers an assertion or segmentation fault instead of rejecting, truncating, or safely discarding the oversized trace.

## Scope

This is a cautiously scoped singleton pattern. It supports oversized trace configuration crossing a generated-code limit and exposing inconsistent metadata during cleanup; it does not establish that every trace overflow or every compiler limit produces the same corruption or failure mode.

## Search strategy

1. Check whether configurable trace or IR limits can exceed the generated-code buffer, machine-code, or bookkeeping limits.
2. Trace oversized-compilation paths through metadata construction and verify that size-limit failures abort or truncate before publication.
3. Inspect executable cleanup and invalidation for unchecked assumptions about entry-instruction metadata.
4. Test boundary and over-limit traces under debug and sanitizer builds, including cleanup after failed or partially constructed compilation.

## Evidence

- [#143751](../micro_taxo/gh_143751.md): Raising the trace-length setting substantially caused the actual machine-code optimizer to compile a long trace and later crash during executable detachment when an assertion found that the referenced instruction was not the expected entry instruction; the report’s follow-up identifies a generated-code limit as the cause.
