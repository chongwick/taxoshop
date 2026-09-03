# Macro Taxonomy: Concurrent Shared State

## Pattern
Free-threaded execution allows two threads to read, mutate, finalize, or
iterate over state that older GIL-based assumptions treated as serialized. The
missing synchronization may be an absent critical section, non-atomic field,
borrowed reference, or iterator cursor shared between consumers.

## Common State At Risk
- Mutable container internals and iterator cursors.
- Context, thread, and interpreter-global state.
- OpenSSL, ctypes, and extension-module structures.
- Reference-counted fields observed while another thread clears them.

## Failure Shapes
- ThreadSanitizer data-race reports.
- Double decref, stale borrowed reference, and use-after-free.
- Nondeterministic crash or corruption when iterator and owner advance apart.

## Defensive Rule
Define ownership and synchronization for each shared field. Protect compound
operations with the same critical section that protects mutation, use atomics
only for independently meaningful fields, and avoid exposing a mutable cursor
to multiple threads.

## Representative Micro-taxonomies
- [#154756](../micro_taxo/gh_154756.md): concurrent `list.sort()` access.
- [#154130](../micro_taxo/gh_154130.md): dictionary iterator double decref.
- [#153852](../micro_taxo/gh_153852.md): collection of free-threading races.
- [#154524](../micro_taxo/gh_154524.md): ctypes buffer access without the
  resize critical section.
- [#143756](../micro_taxo/gh_143756.md): OpenSSL binding races.

## Membership Rule
Group micro-taxonomies tagged `data race`, mentioning free-threading, TSan,
threads, concurrent access, shared iterators, or non-atomic state.
