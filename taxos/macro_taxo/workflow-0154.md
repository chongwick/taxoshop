# A concurrent traversal of a shared mutable mapping retrieves non-owning references to entries and later retains or processes them without synchronizing the hand

A mapping serializer or similar traversal promotes or uses borrowed entry references while another thread may mutate the mapping, allowing an entry's value to be freed before the reference is made safe.

## Precondition

Multiple threads can access a shared mutable mapping, and the traversal API exposes entry or value references whose lifetime is owned by the mapping rather than by the traversal.

## Critical operation

The traversal retrieves a non-owning entry reference and then increments its ownership or otherwise dereferences it after the retrieval step.

## Interference

Another thread removes or replaces the entry, releasing the object still referenced by the traversal.

## Invalid assumption

The non-owning reference remains valid until the traversal acquires ownership or finishes using it, even though the mapping can be mutated concurrently.

## Failure

The traversal dereferences freed memory, causing a use-after-free crash such as a segmentation fault instead of a recoverable concurrent-modification error.

## Scope

This cluster contains one report, so the pattern is scoped to concurrent traversal of mutable mappings whose iteration exposes borrowed references and whose mutation can release entries during that traversal.

## Search strategy

1. Search for mapping iteration that returns borrowed, non-owning, or container-owned references.
2. Check whether reference acquisition or retention occurs in a separate operation after each entry is retrieved.
3. Inspect concurrent mutation paths that remove, replace, or release mapping values during traversal.
4. Verify that the entire retrieval-to-retention interval is protected by an appropriate lock or container critical section.
5. Look for tests that exercise serialization or traversal concurrently with entry removal and replacement.

## Evidence

- [#146452](../micro_taxo/gh_146452.md): The report shows that concurrent removal or replacement of mapping values can invalidate borrowed references returned during traversal before ownership is acquired, producing a segmentation fault; protecting retrieval and reference acquisition with a critical section prevents the failure.
