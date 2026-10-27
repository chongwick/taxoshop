# Optional or uninitialized pointer state is converted with pointer arithmetic before its null/absence state is handled.

Optional or uninitialized pointer state is converted with pointer arithmetic before its null/absence state is handled.

## Precondition

A pointer field or pointer argument may legitimately be NULL because backing storage or a logical position has not been initialized, allocated, or supplied.

## Critical operation

Code performs pointer addition or subtraction to compute an address or offset before checking for NULL or representing the absent state explicitly.

## Interference

The arithmetic has undefined behavior; sanitizers can stop execution, and compiler assumptions about defined pointer arithmetic can invalidate subsequent checks or calculations.

## Invalid assumption

The implementation assumes that arithmetic on a NULL pointer merely preserves an absent value or safely produces a value that can later be checked.

## Failure

Execution may abort during diagnostics, compute an invalid address or offset, or crash instead of taking the intended initialization, allocation, relocation, or NULL-preserving path.

## Scope

The shared pattern is guarded NULL-pointer arithmetic in low-level C state-management code. The reports differ in whether the pointer represents absent storage, an optional argument array, or an uninitialized relocation position, and issue 96678 also contains unrelated undefined-behavior findings; this taxonomy covers only its NULL-arithmetic subset.

## Search strategy

1. Search every pointer addition and subtraction for operands that may be NULL, and require an explicit guard before the arithmetic.
2. Trace pointer fields through initialization, allocation, relocation, and restoration paths; verify that NULL states are encoded without pointer arithmetic.
3. Inspect callers of low-level routines for optional pointer arguments and check that contracts forbid NULL before any derived-pointer computation.
4. Run undefined-behavior sanitizers through uninitialized, empty, reallocation, and first-use paths, including builds with compiler overflow assumptions disabled.

## Evidence

- [#96569](../micro_taxo/gh_96569.md): A frame-storage base pointer is NULL on first use, yet code adds an offset before checking capacity and attempting to allocate storage; undefined behavior is diagnosed and the process aborts.
- [#96678](../micro_taxo/gh_96678.md): The sanitizer review identifies a callable path where an optional argument pointer can be NULL and is advanced before being passed onward; the fix removes the NULL arithmetic by tightening the pointer contract and call path.
- [#144759](../micro_taxo/gh_144759.md): Uninitialized NULL position fields are converted to offsets during buffer relocation and later reconstructed with arithmetic; explicit NULL checks and a sentinel are required to avoid undefined behavior.
