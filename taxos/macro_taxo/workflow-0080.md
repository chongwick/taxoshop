# Callback re-entrancy invalidates borrowed state or backing storage during a native operation

A low-level operation invokes user-defined behavior while retaining borrowed references, raw pointers, cached sizes, iterator state, or container metadata. The callback re-enters and mutates, replaces, clears, resizes, detaches, or destroys that state before the operation resumes.

## Precondition

A native fast path holds unowned object references or cached structural/storage state across a potentially user-defined callback.

## Critical operation

The operation performs lookup, iteration, conversion, comparison, formatting, serialization, packing, I/O, insertion, or cleanup and invokes user code mid-operation.

## Interference

The callback re-enters the active object or its owner and changes the relevant container, iterator, buffer, cache, backing object, or object lifetime.

## Invalid assumption

The operation assumes the callback is observational, or assumes previously acquired pointers, references, lengths, indexes, and representation metadata remain valid after the callback.

## Failure

Continuation through stale state causes use-after-free, null dereference, out-of-bounds access, invalid iteration, assertion failure, or process termination.

## Scope

The shared mechanism is callback-driven re-entrancy, broader than embedded-container cleanup: callbacks arise from hashing, equality, conversion, iteration, formatting, I/O, serialization, and destruction. Some reports invalidate object lifetime, while others invalidate buffers, cached sizes, representation, or iteration state without immediate deallocation; the common boundary is continued use of unprotected state after arbitrary user code.

## Search strategy

1. Audit every user-callback boundary for borrowed references, raw pointers, cached lengths, indexes, and backing buffers used afterward.
2. Check whether callbacks can re-enter the active object or owner and clear, resize, replace, detach, reinitialize, or deallocate its state.
3. Check that objects are kept alive and that pointers, bounds, representation, and mutation state are revalidated after callbacks.
4. Check cleanup and teardown loops for releasing elements before detaching or snapshotting storage that later iterations still use.

## Evidence

- [#130555](../micro_taxo/gh_130555.md): Cleanup of embedded values invoked destructors that mutated the same mapping, invalidating the embedded value storage still used by the clearing loop.
- [#140551](../micro_taxo/gh_140551.md): Hash or equality during mapping lookup could clear the mapping and change its representation before insertion resumed with lookup assumptions.
- [#142555](../micro_taxo/gh_142555.md): Index or numeric conversion during sequence assignment could clear or shrink the target buffer before the write and bounds check completed.
- [#142559](../micro_taxo/gh_142559.md): Index conversion during a byte search could clear the target byte buffer after its pointer and length were captured but before searching.
- [#142594](../micro_taxo/gh_142594.md): A closed-state property callback detached the underlying stream, leaving the close operation with a null backing object.
- [#142637](../micro_taxo/gh_142637.md): Equality during ordered-mapping lookup could clear and reshape its table while deletion and node handling still used stale table pointers.
- [#142663](../micro_taxo/gh_142663.md): Element unpacking during memory comparison could release a view and resize its exporter, freeing the buffer used by later comparison iterations.
- [#142731](../micro_taxo/gh_142731.md): Hashing an attribute name could replace and release the instance mapping while attribute storage continued using the old mapping pointer.
- [#142732](../micro_taxo/gh_142732.md): An iterator callback could re-enter the same iterator, triggering cleanup of iterator state that the outer iteration still held; related iterator implementations had the same exposure.
- [#142734](../micro_taxo/gh_142734.md): User item access or insertion during ordered-mapping copy could mutate the source while copying, invalidating iteration state and previously borrowed entries.
- [#142782](../micro_taxo/gh_142782.md): Key equality during cache traversal could clear the cache and free the currently visited node before cache lookup moved or returned it.
- [#142828](../micro_taxo/gh_142828.md): Callback equality during callback-list removal could clear the list while the removal loop retained pointers into it.
- [#142829](../micro_taxo/gh_142829.md): Value equality during persistent-map comparison could mutate the compared context, prematurely deallocating maps and keys or values still being compared.
- [#142831](../micro_taxo/gh_142831.md): Encoding callbacks could mutate or clear the mapping, item list, or sequence while the encoder iterated borrowed entries.
- [#142882](../micro_taxo/gh_142882.md): Index conversion during sequence extension could clear the destination array, leaving the subsequent element write with a null buffer.
- [#142884](../micro_taxo/gh_142884.md): A sink write callback could clear the array after chunk counts and pointers were computed, while the output loop continued reading the old buffer.
- [#143196](../micro_taxo/gh_143196.md): Custom multiplication during indentation-cache creation could destroy the encoder and invalidate the cache assumptions used by the continuing encoder call.
- [#143379](../micro_taxo/gh_143379.md): Boolean conversion during packing could reinitialize the format object and free the format-code array being traversed.
- [#143543](../micro_taxo/gh_143543.md): Key equality during grouping could advance the same iterator and replace or release the current keys while the outer comparison still used them.
- [#143546](../micro_taxo/gh_143546.md): Equality during in-place set intersection could mutate or clear the participating sets while probing and cleanup still used their table state.
- [#143635](../micro_taxo/gh_143635.md): Attribute lookup during type representation could clear the shared argument list and free the argument object before subsequent representation probes.
- [#143639](../micro_taxo/gh_143639.md): Key hashing during deserialization could re-enter loading, drain the shared stack, and free pending key, value, or mapping objects still used by the outer insertion.
