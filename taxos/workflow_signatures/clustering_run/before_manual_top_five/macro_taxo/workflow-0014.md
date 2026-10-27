# Stale non-owning aliases across owner release or storage replacement

A raw pointer, metadata reference, or derived address remains usable-looking after the owner releases the target or backing storage moves, and later code consumes the alias without restoring or revalidating it.

## Precondition

Code derives or caches a non-owning alias to object metadata, contained data, or an allocation while a cleanup, release, or resizing operation can destroy that target or replace its backing storage.

## Critical operation

Cleanup drops the target's last ownership reference, releases a container that owns the aliased value, or reallocates and moves the backing allocation without preserving the alias as a valid offset or reacquiring it afterward.

## Interference

Control proceeds to deallocation, diagnostic construction, parsing, or other code that reads, formats, traverses, or compares the retained alias after that lifetime or storage transition.

## Invalid assumption

The code assumes that retaining the address is sufficient because the logical object or owner is still in scope, or assumes that a derived pointer remains valid across release or reallocation without an explicit ownership guarantee or pointer restoration.

## Failure

The alias refers to freed or obsolete storage, causing use-after-free, stale-buffer access, crashes, invalid diagnostics, or corrupted parsing and results.

## Scope

This mixed cluster shares stale-alias lifetime failure, but the invalidation mechanisms differ: owner teardown can free metadata, container release can free a borrowed value, and reallocation can move backing storage without freeing the logical data. These are not ownership leaks; the common defect is using a non-owning or un-rebased alias after its validity boundary.

## Search strategy

1. Trace every raw pointer, metadata reference, string-data pointer, and derived buffer address across decref, release, cleanup, and deallocation calls; verify the target remains owned until the final use.
2. Inspect realloc, resize, buffer-growth, and replacement paths for cached interior pointers and require offsets or equivalent stable handles to be saved and restored on every affected state path.
3. Check error-reporting and formatting paths for borrowed character data or container elements used after releasing the container that owns them.
4. Review deallocation callbacks and teardown routines for metadata inspected after cleanup; snapshot required flags or retain explicit ownership before invoking cleanup.
5. Audit alternate control-flow branches, nested parser modes, and failure paths to ensure aliases are repaired or invalidated even when the target changes representation or storage.

## Evidence

- [#88350](../micro_taxo/gh_88350.md): A deallocation path retained a pointer to type metadata, invoked cleanup that could remove the metadata's last ownership reference, and then inspected the freed metadata.
- [#103718](../micro_taxo/gh_103718.md): Tokenizer state cached pointers into a growable buffer, but reallocation could replace that buffer without correctly restoring all derived pointers, leaving later parsing to read the old allocation.
- [#139210](../micro_taxo/gh_139210.md): An error path released a container owning an event string before formatting the string through a borrowed character pointer, so the formatter read freed string storage.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0014](../macro_taxo_before_hybrid/workflow-0014.md)
