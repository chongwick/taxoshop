# Macro Taxonomy: Re-entrant Callbacks And Protocol Methods

## Pattern
Native CPython code calls back into Python while holding a raw pointer, a
borrowed reference, cached state, or a partially updated container. Python
code then invokes a protocol method or explicit mutator that frees, closes, or
replaces the state. The original C frame resumes with an invalid assumption.

## Common Boundary Types
- Numeric conversion: `__index__` changes state during size or offset handling.
- Hashing and equality: `__hash__` and `__eq__` mutate a container mid-lookup.
- Iteration and conversion: an iterator or callback closes its owner mid-call.
- Codec, profiler, and trace hooks: user callbacks run inside internal state
  transitions.

## Failure Shapes
- Use-after-free from a retained local C pointer.
- Null dereference after a callback closes or clears an owner field.
- Bounds error when a callback changes the size used by a later copy.
- Assertion failure when a callback invalidates a decoder or frame invariant.

## Defensive Rule
Treat every Python-callable operation as a re-entrancy boundary. Do not retain
raw aliases across it without ownership; after it returns, reload and validate
state or prevent destructive mutation for the duration of the call.

## Representative Micro-taxonomies
- [#143545](../micro_taxo/gh_143545.md): profiler timer `__index__` clears the
  active context.
- [#142663](../micro_taxo/gh_142663.md): `memoryview` comparison re-enters via
  `struct.Struct.unpack_from`.
- [#142665](../micro_taxo/gh_142665.md): slicing re-enters through `__index__`.
- [#142637](../micro_taxo/gh_142637.md): `OrderedDict` operations re-enter via
  equality.
- [#143662](../micro_taxo/gh_143662.md): SQLite `text_factory` closes a
  connection while a cursor callback is active.

## Membership Rule
Group micro-taxonomies whose reported failure, trigger, or pattern tags name a
Python callback, a dunder protocol method, `re-entrant` behavior, or mutation
of the owner during a native operation.
