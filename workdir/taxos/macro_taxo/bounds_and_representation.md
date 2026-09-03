# Macro Taxonomy: Bounds And Representation Invariants

## Pattern
Python-visible inputs reach a C API whose representation assumptions are not
validated at the boundary. Size, index, opcode, frame layout, Unicode writer,
or buffer metadata then no longer matches the allocation or object shape used
by native code.

## Common Boundary Types
- Buffer slices, memoryviews, and ctypes assignments.
- Frame, bytecode, code-object, and instruction-sequence construction.
- Unicode decoding and formatting writers.
- Argument conversion, internal test APIs, and extension constructors.

## Failure Shapes
- Heap or global buffer overflow.
- Null dereference from malformed metadata.
- Debug assertion on a violated C invariant.
- Undefined behavior from arithmetic or pointer assumptions.

## Defensive Rule
Validate externally derived sizes, offsets, opcodes, and object types before
allocation or pointer arithmetic. After callbacks or coercions, recompute
dependent bounds rather than relying on a value captured before the boundary.

## Representative Micro-taxonomies
- [#140802](../micro_taxo/gh_140802.md): tracing creates invalid coroutine
  frame state.
- [#140750](../micro_taxo/gh_140750.md): JSON indentation caching overflows a
  buffer.
- [#143005](../micro_taxo/gh_143005.md): ctypes array assignment overflows via
  `__class__` swap.
- [#144163](../micro_taxo/gh_144163.md): malformed internal code-assembler
  metadata reaches a null dereference.
- [#141336](../micro_taxo/gh_141336.md): codec error handling violates Unicode
  writer accounting.

## Membership Rule
Group micro-taxonomies with heap/global buffer overflow, assertion failure,
null pointer dereference, undefined behavior, malformed bytecode, or invalid
buffer and index inputs.
