# Reentrant invalidation of retained native state during user-code boundaries.

A native operation retains borrowed objects, raw storage, cached bounds, iteration state, or resource handles across user-controlled work. Reentrant mutation invalidates that state, but execution resumes through the old view.

## Precondition

The operation captures unowned objects, pointers, buffers, lengths, indexes, iterators, tables, or resource handles before conversion, comparison, hashing, formatting, cleanup, I/O, or callback dispatch that may execute arbitrary code.

## Critical operation

The operation invokes user-defined behavior or destruction while continuing to depend on the captured object lifetime, storage address, structural layout, bounds, representation, iterator state, or associated resource.

## Interference

Reentrant code clears, resizes, replaces, detaches, releases, destroys, or recursively re-enters the owner, backing storage, resource, or active operation context.

## Invalid assumption

The operation assumes the captured state remains live and structurally consistent, or that a borrowed object remains available, after the reentrant boundary.

## Failure

Continuation through stale or null state causes use-after-free, null dereference, out-of-bounds access, invalid iteration, corrupted results, or process termination instead of defined recovery.

## Scope

The common pattern is reentrant invalidation of retained native state, spanning object lifetimes, buffers, tables, iterators, resources, exception state, and recursive context. Some cases use stale or freed state; others use null or reshaped state. Ownership leaks alone are outside scope.

## Search strategy

1. Audit every user-code boundary for borrowed objects, raw pointers, cached lengths, indexes, iterators, tables, and resource handles used afterward.
2. Check whether conversions, comparisons, hashing, formatting, callbacks, destructors, or I/O can mutate, clear, replace, detach, release, or recursively re-enter the active owner.
3. Verify strong lifetime protection and revalidation of identity, storage, bounds, representation, iterator state, and resource attachment after the boundary.
4. Inspect cleanup, error, fallback, and teardown paths for stale borrowed elements or context pointers reused after failure, destruction, or owner replacement.

## Evidence

- [#115243](../micro_taxo/gh_115243.md): Custom comparison can clear a container after an element is borrowed but before the native operation finishes using it.
- [#120289](../micro_taxo/gh_120289.md): An external callback can disable or clear the active profiling context while its caller continues through that context.
- [#120298](../micro_taxo/gh_120298.md): Rich comparison can clear an operand container while the enclosing comparison still uses borrowed final elements.
- [#130555](../micro_taxo/gh_130555.md): Element destruction during cleanup can mutate the same mapping while the clearing loop still uses its embedded storage.
- [#140551](../micro_taxo/gh_140551.md): Hash or equality reentrancy can clear or reshape a mapping while lookup or insertion retains old representation assumptions.
- [#142555](../micro_taxo/gh_142555.md): Index conversion can clear or shrink a target sequence before assignment completes bounds checks and writes.
- [#142557](../micro_taxo/gh_142557.md): Formatting can run user code that mutates or clears byte storage still needed by the formatting path.
- [#142558](../micro_taxo/gh_142558.md): Argument conversion can invalidate a captured byte buffer before a search operation resumes.
- [#142559](../micro_taxo/gh_142559.md): Index conversion can clear a searched byte buffer after pointer and length capture but before continued access.
- [#142560](../micro_taxo/gh_142560.md): A search helper can retain raw storage across an argument call that invalidates its owner.
- [#142594](../micro_taxo/gh_142594.md): A state callback can detach an underlying resource, leaving a later close step with a null backing handle.
- [#142637](../micro_taxo/gh_142637.md): Equality can reshape an ordered mapping while deletion continues with stale table and node state.
- [#142663](../micro_taxo/gh_142663.md): Element unpacking can release a view and resize its exporter while comparison still uses the old buffer.
- [#142664](../micro_taxo/gh_142664.md): Hashing can mutate or release a view exporter while the hash operation still uses the view.
- [#142731](../micro_taxo/gh_142731.md): Key hashing can replace and release an instance mapping while attribute access still uses its old pointer.
- [#142732](../micro_taxo/gh_142732.md): Iterator reentry can clean up iterator state retained by the outer iteration.
- [#142734](../micro_taxo/gh_142734.md): User item access or insertion can mutate a source mapping while copying retains iteration and borrowed-entry state.
- [#142782](../micro_taxo/gh_142782.md): Key equality can clear a cache and free the currently visited node before lookup continues.
- [#142828](../micro_taxo/gh_142828.md): Callback equality can clear a callback list while removal retains pointers into the old list.
- [#142829](../micro_taxo/gh_142829.md): Value equality can mutate compared maps and free keys or values still used by the outer comparison.
- [#142830](../micro_taxo/gh_142830.md): Callbacks can mutate or clear callback state during execution while surrounding code uses the old context.
- [#142831](../micro_taxo/gh_142831.md): Encoding callbacks can mutate mappings or sequences while the encoder traverses borrowed entries.
- [#142882](../micro_taxo/gh_142882.md): Index conversion can clear a destination array before a subsequent write through its cached buffer.
- [#142884](../micro_taxo/gh_142884.md): A sink callback can clear an array after chunk metadata and pointers are cached but before output completes.
- [#143004](../micro_taxo/gh_143004.md): A mapping lookup can return a borrowed value, then arithmetic reentrancy can mutate the mapping before reuse.
- [#143007](../micro_taxo/gh_143007.md): Numeric conversion can detach an associated resource before the operation calls through its cached handle.
- [#143008](../micro_taxo/gh_143008.md): A flush callback can detach a wrapped resource before a later step uses its backing handle.
- [#143195](../micro_taxo/gh_143195.md): A length query can clear byte storage before conversion continues reading the original buffer.
- [#143196](../micro_taxo/gh_143196.md): Custom multiplication can destroy an encoder while cache construction continues with stale encoder assumptions.
- [#143197](../micro_taxo/gh_143197.md): Reentrant conversion can replace and release an object while the outer operation writes through its old pointer.
- [#143198](../micro_taxo/gh_143198.md): Iterator setup can close an associated connection before execution reuses cached statement state.
- [#143200](../micro_taxo/gh_143200.md): Index conversion can clear an element's child storage before slicing continues through it.
- [#143236](../micro_taxo/gh_143236.md): Key comparison can clear frame locals while name lookup continues through the old locals state.
- [#143308](../micro_taxo/gh_143308.md): Truth conversion can release a serialization buffer before serialization copies from its retained view.
- [#143309](../micro_taxo/gh_143309.md): Environment conversion can mutate a source mapping while retained traversal data is still consumed.
- [#143310](../micro_taxo/gh_143310.md): Element conversion can clear an input list while outer conversion traverses old slots.
- [#143375](../micro_taxo/gh_143375.md): Offset conversion can detach a buffered writer before seek resumes with stale buffered state.
- [#143378](../micro_taxo/gh_143378.md): Buffer acquisition can close or mutate the target before the write path finishes with its storage.
- [#143379](../micro_taxo/gh_143379.md): Boolean conversion can reinitialize a format object and free code storage still being traversed.
- [#143380](../micro_taxo/gh_143380.md): Parameter processing can invalidate an associated connection before execution uses it.
- [#143543](../micro_taxo/gh_143543.md): Equality can advance or replace an iterator's current keys while the outer grouping comparison still uses them.
- [#143544](../micro_taxo/gh_143544.md): Error construction can replace or free an exception type while decoding still relies on the old type.
- [#143545](../micro_taxo/gh_143545.md): Index conversion can clear profiler state while initialization or stopping writes through the old context.
- [#143546](../micro_taxo/gh_143546.md): Equality can mutate or clear participating sets while probing and cleanup use stale tables.
- [#143547](../micro_taxo/gh_143547.md): A failing callback can free its object, after which fallback logging reuses the dangling pointer.
- [#143635](../micro_taxo/gh_143635.md): Attribute lookup can clear a shared argument list and free an argument before later representation probes.
- [#143637](../micro_taxo/gh_143637.md): Index conversion can clear a control list while parsing continues with captured items and bounds.
- [#143638](../micro_taxo/gh_143638.md): Reentrant assignment can recursively mutate serializer state while the outer operation still uses it.
- [#143639](../micro_taxo/gh_143639.md): Key hashing can re-enter loading and free pending objects still used by outer insertion.
- [#143662](../micro_taxo/gh_143662.md): Text conversion can close an associated database before cursor iteration calls through the cleared handle.
- [#144128](../micro_taxo/gh_144128.md): Index conversion can clear a source list and release the element being converted before conversion completes.
- [#144475](../micro_taxo/gh_144475.md): Representation can iterate borrowed entries after reentrant replacement and freeing of the original container.
- [#144922](../micro_taxo/gh_144922.md): A write callback can clear, shrink, or reallocate an array after metadata and pointers are cached.
- [#148382](../micro_taxo/gh_148382.md): Callbacks can replace and free a context while a borrowed context pointer remains in use.
- [#148625](../micro_taxo/gh_148625.md): Rich comparison can free an object whose type or fields the enclosing comparison reads afterward.
- [#151403](../micro_taxo/gh_151403.md): Path conversion can mutate its argument sequence and free the current item while an error path reads it.
- [#154189](../micro_taxo/gh_154189.md): Key hashing can replace argument and keyword containers behind cached raw pointers during a call.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0014](../macro_taxo_before_hybrid/workflow-0014.md)
- [workflow-0080](../macro_taxo_before_hybrid/workflow-0080.md)
- [workflow-0137](../macro_taxo_before_hybrid/workflow-0137.md)
