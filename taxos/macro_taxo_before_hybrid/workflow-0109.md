# An enumeration walks a registry containing inactive tombstones while sizing output only for active entries.

A retained registry entry becomes inactive by losing its backing resource, but enumeration still traverses the retained entry set while sizing results from the active-resource count.

## Precondition

A resource registry retains entries after resources are closed, destroyed, or released, representing inactive entries with no backing resource while maintaining a count of active resources.

## Critical operation

An enumeration allocates result storage from the active-resource count and traverses the registry, reading backing-resource fields for each retained entry.

## Interference

A resource lifecycle operation marks an entry inactive without removing it from the registry traversal structure.

## Invalid assumption

The enumeration assumes every retained registry entry still has a backing resource and that the active count equals the number of entries it will process.

## Failure

The enumeration dereferences a null backing-resource pointer and can also write beyond storage sized for active entries, producing a process-terminating memory-safety failure instead of returning the active-resource list.

## Scope

This is a singleton cluster: the pattern is scoped to registries that retain inactive entries during lifecycle transitions and enumerate them through a backing-resource pointer.

## Search strategy

1. Inspect registry enumerators for retained entries whose backing-resource pointer may be null.
2. Compare the allocation count with the number of entries actually traversed, including inactive or tombstoned entries.
3. Trace close, destroy, and release paths to determine whether they remove entries or only clear their backing-resource pointers.
4. Check every dereference of a registry entry's backing resource for an explicit active-entry guard.
5. Verify that the returned count is incremented only for entries actually emitted into the output buffer.

## Evidence

- [#140652](../micro_taxo/gh_140652.md): The report reproduces a crash after resource closure and the fix skips retained entries with null backing resources while counting and emitting only active entries; added coverage also confirms closed and destroyed entries are excluded from enumeration.
