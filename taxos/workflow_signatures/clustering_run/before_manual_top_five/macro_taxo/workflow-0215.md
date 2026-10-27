# Retained derived state or mapped-buffer access reaches storage after its owner or backing resource becomes invalid

Native code retains a borrowed pointer, view, derived object, or mapped destination whose validity depends on another owner or backing resource. A later read, write, parsing step, formatting operation, or bulk serialization access occurs after that dependency has been destroyed, released, truncated, or otherwise made unusable. The cluster includes both ownership/lifetime failures and externally invalidated mapped-storage failures; an invalid destination may also be observed without an established cause.

## Precondition

Code exposes or retains derived state, a non-owning pointer, a view, or a mapped destination while its owner, allocation, parser context, temporary buffer, or backing resource can be destroyed, released, resized, truncated, or rendered unusable independently.

## Critical operation

A later native operation dereferences, reads, writes, slices, formats, parses, or bulk-serializes through the retained state or destination.

## Interference

The owner is deallocated, a temporary view or buffer is released, reentrant code mutates or invalidates the backing storage, an external operation truncates or damages mapped storage, or the native operation receives an already unusable destination.

## Invalid assumption

The retained handle and the storage it designates remain valid and usable for the later operation, even though the handle does not itself establish ownership or the backing resource may have changed independently.

## Failure

Native access reaches freed, dangling, truncated, unmapped, or otherwise unusable storage, producing a use-after-free, invalid read or write, heap or buffer memory error, SIGBUS or SIGSEGV, or process termination instead of a recoverable invalid-state or buffer error.

## Scope

This mixed cluster includes borrowed-state lifetime errors and externally invalidated mapped storage. The common step is using a view or destination without establishing its continued validity. Not every view must own its backing resource. The cause of the invalid destination in issue 140777 remains unresolved, so that member supports only the observed access failure.

## Search strategy

1. Trace every borrowed pointer, derived object, view, mapped address, and temporary buffer across owner destruction, release, resizing, truncation, callbacks, and reentrant operations; verify explicit lifetime protection or invalidation.
2. Check native read, write, slice, formatting, parsing, and bulk-copy paths for validity checks at the access site after a dependency may have been invalidated.
3. Inspect parent-child and view-owner relationships for strong ownership where the child continues to use parent state, or explicit nulling and safe-error handling where ownership is intentionally borrowed.
4. Review memory-mapped and shared-storage paths for external shrinkage, unmapping, resource closure, or platform faults, and ensure invalid backing storage cannot reach unchecked native writes.
5. Audit temporary exported views passed to callbacks or user methods to ensure they are released or invalidated immediately after the call and cannot access a freed temporary buffer.
6. Separate reports of leaked or prematurely released ownership from reports of stale or externally invalidated storage; do not infer the invalidation cause when the report only establishes an unusable destination.

## Evidence

- [#66234](../micro_taxo/gh_66234.md): An open file-backed database continues using mapped contents after the file is externally emptied, and a subsequent update reaches invalid storage and terminates the process rather than returning a normal database error.
- [#80434](../micro_taxo/gh_80434.md): A pointer into a buffer remains usable after the buffer owner is deleted, and later access reads freed memory.
- [#139400](../micro_taxo/gh_139400.md): A derived parser remains capable of using parent parser state after the parent is released, requiring the parent-child lifetime to be retained until the child no longer uses it.
- [#140777](../micro_taxo/gh_140777.md): Shared-memory aggregate initialization reaches a native packing write whose destination is unusable and aborts with a bus fault; the report does not establish how that destination became invalid.
- [#142665](../micro_taxo/gh_142665.md): A subview is created before reentrant slice-index processing, which releases or truncates the underlying mapping and leaves the subview with a dangling pointer used by later access.
- [#144281](../micro_taxo/gh_144281.md): A shared-memory-backed view assignment can reach invalid mapped storage during a native copy and terminate with SIGBUS rather than consistently producing a recoverable buffer error; the precise trigger is disputed and may require low-level resource faulting.
- [#146011](../micro_taxo/gh_146011.md): A retained child mapping object stores borrowed parent state; deleting the parent leaves the child pointing at freed context storage, and later representation reads it.
- [#151046](../micro_taxo/gh_151046.md): A callback retains a temporary view over a short-lived buffer, then accesses it after the call when the buffer has been released; proper release converts the stale access into a safe invalid-view error.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0004](../macro_taxo_before_hybrid/workflow-0004.md)
- [workflow-0014](../macro_taxo_before_hybrid/workflow-0014.md)
- [workflow-0112](../macro_taxo_before_hybrid/workflow-0112.md)
