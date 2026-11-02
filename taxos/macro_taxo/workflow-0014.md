# Borrowed or derived handles are used after reentrancy, concurrency, mutation, or teardown invalidates their owner or backing storage.

A non-owning pointer, reference, view, cache entry, iterator position, or metadata slot survives an operation that can invalidate the object or storage it designates, then is used as though it remained valid.

## Precondition

Code retains a borrowed or derived handle to an object, allocation, buffer, container element, interpreter state, stack entry, or related backing resource while another operation, callback, thread, or lifecycle event can invalidate that target.

## Critical operation

A decrement, release, resize, reallocation, container mutation, callback, garbage-collection pass, interpreter shutdown, or concurrent teardown invalidates or frees the target while the retained handle remains reachable.

## Interference

Control returns to, or another execution context enters, code that dereferences, traverses, indexes, formats, compares, or otherwise uses the retained handle without first reacquiring or validating ownership.

## Invalid assumption

The code assumes that the target cannot be destroyed or replaced during the intervening operation, or treats a borrowed reference, cached pointer, exported view, or stale slot as an ownership guarantee.

## Failure

The stale handle accesses freed, moved, released, or otherwise invalid storage or object state, causing use-after-free, stack-use-after-return, out-of-bounds access, crashes, corrupted results, or unsafe behavior.

## Scope

The reports share an ownership and lifetime-ordering failure, but the invalidated target is not always a byte buffer and the invalidation may come from reentrancy, concurrency, mutation, refcounting, garbage collection, interpreter shutdown, or external resource teardown. One report manifests as a heap-buffer-overflow rather than a sanitizer-labeled use-after-free; it is included because the same stale borrowed-container-storage mechanism causes the invalid access.

## Search strategy

1. Trace every borrowed pointer, reference, view, iterator position, cache entry, and raw buffer address across callbacks, conversions, comparisons, formatting, and other callouts that may run arbitrary code.
2. Find decref, release, resize, reallocation, container-mutation, garbage-collection, shutdown, and cross-thread teardown paths and verify that retained handles are kept alive or invalidated before use.
3. Inspect code that captures a handle before invoking user code or releasing synchronization and verify that it reacquires ownership or validates the target after the call returns.
4. Check temporary views and exported buffers for explicit release or invalidation before their backing allocation can be destroyed or resized.
5. Review error and fallback paths separately; confirm they do not dereference an object after dropping its last reference or after a callback mutates the relevant container.

## Evidence

- [#80434](../micro_taxo/gh_80434.md): A pointer into a deallocated buffer remains usable after the buffer owner is destroyed, directly supporting stale borrowed storage access.
- [#88350](../micro_taxo/gh_88350.md): Interpreter finalization frees a heap object while cleanup later follows a reference to that object, supporting missing lifetime ownership during teardown.
- [#96572](../micro_taxo/gh_96572.md): A stale object reference remains in tracing metadata after the object is freed and is later traversed, supporting invalid retained bookkeeping references.
- [#101975](../micro_taxo/gh_101975.md): Garbage collection traverses a stack slot whose bounds were not updated after an element was freed, supporting stale lifetime metadata causing invalid access.
- [#103718](../micro_taxo/gh_103718.md): Buffer reallocation leaves cached pointers into tokenizer state referring to the old allocation, supporting failure to repair derived pointers after storage movement.
- [#108253](../micro_taxo/gh_108253.md): A version cache retains a stale pointer after the associated object changes or is deallocated, supporting invalid cache entries used after target lifetime ends.
- [#113591](../micro_taxo/gh_113591.md): Two runtimes independently manage shared objects and one frees memory still expected by the other, supporting cross-owner lifetime mismatches.
- [#114106](../micro_taxo/gh_114106.md): Mutation of underlying mapping state leaves cached data used after it was freed, supporting stale cached values after invalidation.
- [#115243](../micro_taxo/gh_115243.md): An element obtained from a container can be freed during comparison before subsequent use, supporting borrowed element access across reentrant or concurrent work.
- [#116510](../micro_taxo/gh_116510.md): Interpreter shutdown frees GC metadata or interned objects still referenced by another interpreter, supporting cross-lifetime shared state.
- [#120289](../micro_taxo/gh_120289.md): A user-controlled timer callback mutates profiler state while a borrowed internal object remains in use, supporting callback-induced invalidation.
- [#120298](../micro_taxo/gh_120298.md): A comparison can mutate a list and free an element after it was fetched but before later use, supporting borrowed container-element lifetime failure.
- [#124878](../micro_taxo/gh_124878.md): Interpreter finalization races with a daemon thread holding thread-state pointers, supporting concurrent teardown of retained state.
- [#135636](../micro_taxo/gh_135636.md): A reference-count increment operates on an object whose storage has already been freed, supporting use of a stale object pointer before ownership is secured.
- [#139210](../micro_taxo/gh_139210.md): An error-reporting path decrements an object and then uses the same pointer, supporting immediate post-release dereference.
- [#139400](../micro_taxo/gh_139400.md): A subparser can outlive the parent parser whose state backs it, supporting derived parser state used after owner destruction.
- [#140138](../micro_taxo/gh_140138.md): Subinterpreter shutdown can free interpreter state while daemon-thread activity still uses it, supporting teardown races over shared state.
- [#140651](../micro_taxo/gh_140651.md): Parsing retains a pointer into storage that is later freed and then reads through it, supporting direct stale-buffer access.
- [#140815](../micro_taxo/gh_140815.md): A watchdog thread reads frame data concurrently with frame destruction, supporting unsynchronized access to state being finalized.
- [#142557](../micro_taxo/gh_142557.md): Formatting invokes user code that mutates and clears the formatted bytearray while the formatting path still relies on its storage, supporting reentrant invalidation.
- [#142558](../micro_taxo/gh_142558.md): Argument conversion can clear or resize the searched bytearray after a raw buffer is captured, supporting stale buffer use across conversion.
- [#142560](../micro_taxo/gh_142560.md): Search helpers capture a raw buffer before a reentrant argument operation invalidates it, supporting owner mutation during an intervening callout.
- [#142664](../micro_taxo/gh_142664.md): Hash computation invokes user code that releases or mutates the view or its exporter while the hash path still uses the view, supporting reentrant lifetime invalidation.
- [#142665](../micro_taxo/gh_142665.md): Slice parsing releases or truncates the underlying buffer after a subview is created, leaving the subview with a dangling pointer.
- [#142783](../micro_taxo/gh_142783.md): A cache accessor returns a newly created object as though it were borrowed and releases it too early, supporting incorrect ownership transfer.
- [#142830](../micro_taxo/gh_142830.md): Callbacks mutate or clear callback state during their own execution while surrounding code continues using the old context, supporting callback-induced stale state.
- [#143004](../micro_taxo/gh_143004.md): A mapping lookup returns a borrowed value, and an arithmetic callout mutates the mapping before the value is reused, supporting borrowed-reference invalidation across user code.
- [#143197](../micro_taxo/gh_143197.md): A reentrant conversion replaces and decrements an object while the outer operation continues writing through the old object pointer, supporting stale self access.
- [#143309](../micro_taxo/gh_143309.md): Environment conversion can mutate the source mapping during key or value processing, invalidating retained traversal data before later use.
- [#143547](../micro_taxo/gh_143547.md): A failing callback causes its object to be freed, but fallback logging reuses the dangling pointer, supporting error-path lifetime failure.
- [#144172](../micro_taxo/gh_144172.md): Tracing retains pointers to strings created by a subinterpreter and accesses them after that interpreter frees them, supporting cross-component ownership failure.
- [#144281](../micro_taxo/gh_144281.md): A shared-memory buffer can become invalid while a view assignment still targets it, supporting external backing-resource invalidation.
- [#144475](../micro_taxo/gh_144475.md): Representation code iterates borrowed tuple entries after reentrant mutation replaces and frees the original tuple, supporting stale container storage access and out-of-bounds behavior.
- [#144833](../micro_taxo/gh_144833.md): An error path decrements an object to destruction and then reads through the released pointer, directly supporting post-release dereference.
- [#146011](../micro_taxo/gh_146011.md): A child view retains a borrowed pointer to fields in a context object that can be explicitly destroyed, supporting derived view lifetime failure.
- [#148382](../micro_taxo/gh_148382.md): A borrowed context pointer is used after intervening callbacks replace and free the context, supporting callback-induced owner invalidation.
- [#151046](../micro_taxo/gh_151046.md): A temporary view is retained by a callee after its short-lived backing buffer is released, directly supporting dangling view access.
- [#151403](../micro_taxo/gh_151403.md): A conversion callback mutates the argument sequence and frees its current item, while an error path still reads that item through a borrowed pointer.
