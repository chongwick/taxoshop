# Reentrant user-code execution invalidates native state before later use

A native operation retains a borrowed pointer, cached size, container slot, or backing-resource handle across a user-code boundary. The user code mutates, detaches, closes, replaces, or releases that state, but the operation resumes using its pre-bound view instead of acquiring a protected reference or validating the state again.

## Precondition

The operation has validated or captured native state and then performs conversion, iteration, comparison, callback dispatch, or another protocol operation capable of executing user code.

## Critical operation

The operation invokes that user-controlled protocol or callback while retaining raw pointers, borrowed objects, cached dimensions, or assumptions about an attached resource for subsequent work.

## Interference

Reentrant code invalidates the retained state by clearing or resizing a container, releasing a buffer, detaching or closing a resource, replacing object fields, freeing an exception or execution context, or recursively mutating the same operation object.

## Invalid assumption

After the user-code boundary, the previously validated handle, pointer, object lifetime, container layout, size, or associated resource is still valid and unchanged.

## Failure

The resumed operation reads or calls through stale, cleared, freed, or out-of-bounds state, producing a null dereference, use-after-free, invalid read, heap overread, crash, or possible data corruption instead of a recoverable error.

## Scope

The shared pattern is broader than backing-resource detachment and broader than numeric conversion: the reports include container mutation, buffer release, object replacement, recursive use, and callback-driven invalidation. It is scoped to operations that retain native state across a user-code or equivalent reentrant boundary; it does not claim that every callback or mutation is unsafe when state is protected or revalidated.

## Search strategy

1. Check every conversion, protocol dispatch, comparison, iterator operation, and callback for user-code execution while raw pointers, borrowed references, cached sizes, or resource handles remain live.
2. Check whether reentrant code can clear, resize, detach, close, release, replace, or recursively re-enter the object whose state was captured before the call.
3. Check that every potentially invalidating boundary is followed by a lifetime-preserving reference or a fresh validity, identity, pointer, and size check before native state is used.
4. Check that invalidation is converted into a defined exception or abort path rather than dereferencing the stale state or continuing with cached bounds.

## Evidence

- [#143007](../micro_taxo/gh_143007.md): Numeric conversion of a caller-supplied position invokes user code that detaches the underlying resource; the operation then calls through the cleared handle.
- [#143008](../micro_taxo/gh_143008.md): A flush callback detaches the wrapped resource before a later operation uses the wrapper's backing handle.
- [#143195](../micro_taxo/gh_143195.md): A separator length query clears the byte storage before the hex conversion continues reading the original buffer.
- [#143198](../micro_taxo/gh_143198.md): Creating or obtaining a parameter iterator can close the database connection before cursor execution reuses cached statement state.
- [#143200](../micro_taxo/gh_143200.md): Index conversion can clear an element's child storage before slice processing continues with that storage.
- [#143236](../micro_taxo/gh_143236.md): Mapping lookup can execute key comparison code that clears frame locals while name lookup continues through the old locals state.
- [#143308](../micro_taxo/gh_143308.md): A callback result's truth conversion releases the buffer being serialized before serialization copies from the retained view.
- [#143310](../micro_taxo/gh_143310.md): String conversion of an element can clear the input list while the outer argument conversion continues traversing its old slots.
- [#143375](../micro_taxo/gh_143375.md): Offset conversion can close or detach the buffered writer before seek resumes with its buffered state.
- [#143378](../micro_taxo/gh_143378.md): Buffer acquisition can run user code that closes or mutates the target buffer before the write path finishes using its internal storage.
- [#143380](../micro_taxo/gh_143380.md): Sequence-length or parameter processing can reentrantly invalidate the database connection before execution uses the connection state.
- [#143544](../micro_taxo/gh_143544.md): Error construction can reenter and replace or free the exception type while the decoder still holds the old type assumption.
- [#143545](../micro_taxo/gh_143545.md): External timer index conversion can clear the profiler while initialization or stopping still writes through the profiler context.
- [#143637](../micro_taxo/gh_143637.md): Ancillary-data index conversion can clear the control list while the parser continues using its captured items and bounds.
- [#143638](../micro_taxo/gh_143638.md): Reentrant mapping assignment during pickle state processing can recursively mutate the same serializer state while the outer operation still uses it.
- [#143662](../micro_taxo/gh_143662.md): Text conversion through a user factory can close the database before cursor iteration calls a database helper with the cleared handle.
- [#144128](../micro_taxo/gh_144128.md): Element index conversion can clear the source list and release the element being converted before conversion completes.
- [#144922](../micro_taxo/gh_144922.md): A write callback can clear, shrink, or reallocate the array after block metadata and storage pointers were cached.
- [#148625](../micro_taxo/gh_148625.md): Rich comparison can execute user code that frees an object whose type or fields the enclosing comparison still reads afterward.
- [#154189](../micro_taxo/gh_154189.md): Keyword hashing can reenter object state replacement and free the argument and keyword containers behind cached raw pointers.
