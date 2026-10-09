# Stale native state across user-controlled or lifetime-changing execution

Native code retains a borrowed/interior pointer or cached structural state from a mutable or refcounted object across an operation that may invoke arbitrary code or trigger destruction; that execution can invalidate the retained state before native code resumes.

## Precondition

An implementation has retained non-owning access to object memory, a buffer, a cached entry, or structural metadata whose lifetime, address, length, or ownership can change.

## Critical operation

The implementation performs or resumes work using that retained state while executing an operation that can run callbacks, protocol methods, comparisons, conversions, finalizers, or another lifetime-changing action.

## Interference

The invoked code or lifecycle transition clears, resizes, closes, detaches, replaces, deallocates, or otherwise invalidates the retained object or storage.

## Invalid assumption

The resumed code assumes that the prior pointer, cached reference, capacity, bounds, cache entry, or optional subobject is still live and describes the current state.

## Failure

Continued access dereferences freed or null memory, or uses obsolete bounds or layout, producing use-after-free, null dereference, out-of-bounds access, invalid write, or a process crash.

## Scope

The shared rule is broader than index or slice conversion and broader than container backing arrays. It covers any native operation that retains non-owning state across callback-capable execution or destruction, including caches, contexts, iterators, streams, and parent-owned subobjects. A few reports demonstrate direct post-destruction stale access rather than reentrant mutation, so reentrancy is a common invalidation route, not a required precondition.

## Search strategy

1. Audit every borrowed or interior pointer, cached object reference, and cached size retained across a call that can execute application code or decref an object.
2. Treat conversions, comparisons, hashing, iteration, representation, callbacks, and property access as reentrancy points; reacquire and validate state after each one.
3. After destruction-capable cleanup or reference release, prove that no subsequent read uses the released object's metadata or an alias into it.
4. For mutable buffers and tables, prevent structural mutation while a raw view is live, or revalidate the view, length, and owner identity before resuming.
5. Test each callback boundary with code that clears, resizes, closes, detaches, replaces, or drops the last reference to the object being operated on.
6. Audit optional owned subobjects after callback-capable operations and handle their absence rather than assuming a non-null pointer.

## Evidence

- [#80434](../micro_taxo/gh_80434.md): An interior pointer was accessed after its backing buffer owner had been released.
- [#88350](../micro_taxo/gh_88350.md): A deallocation path freed an object and then read metadata from that freed object.
- [#108253](../micro_taxo/gh_108253.md): A cache retained a stale borrowed pointer after the cached object's version or lifetime changed.
- [#114106](../micro_taxo/gh_114106.md): A cached value was consumed after it had been freed.
- [#115243](../micro_taxo/gh_115243.md): Concurrent mutation during a search could free the current element unless it was kept alive.
- [#120289](../micro_taxo/gh_120289.md): A profiling context could be freed while later code still used its pointer.
- [#120298](../micro_taxo/gh_120298.md): Container comparison could continue after callback-capable element comparison invalidated relied-on state.
- [#130555](../micro_taxo/gh_130555.md): Destruction during clearing could reentrantly mutate the same mapping and invalidate its active state.
- [#140496](../micro_taxo/gh_140496.md): A stale value reached a reference-count operation after being freed.
- [#140551](../micro_taxo/gh_140551.md): Lookup callbacks could clear a mapping while lookup code still relied on its previous table state.
- [#142555](../micro_taxo/gh_142555.md): Index conversion could reenter and remove backing storage before assignment resumed.
- [#142557](../micro_taxo/gh_142557.md): Formatting callback execution could mutate a mutable byte buffer while formatting retained its storage.
- [#142558](../micro_taxo/gh_142558.md): Search helpers retained raw mutable-buffer storage across index conversion; resize or clear made it stale.
- [#142559](../micro_taxo/gh_142559.md): A conversion callback cleared a byte buffer after its raw pointer had been captured.
- [#142560](../micro_taxo/gh_142560.md): Multiple buffer-search paths exposed the same stale raw-storage hazard across conversion callbacks.
- [#142594](../micro_taxo/gh_142594.md): A callback during close could detach an owned subobject before later code dereferenced it.
- [#142637](../micro_taxo/gh_142637.md): Equality lookup could clear an ordered mapping while deletion or movement retained table pointers.
- [#142663](../micro_taxo/gh_142663.md): Comparison invoked unpacking code that could resize or release a buffer while iteration retained its pointer.
- [#142664](../micro_taxo/gh_142664.md): Hashing could execute code that released the view whose state hashing continued to use.
- [#142665](../micro_taxo/gh_142665.md): Slice-bound conversion could release underlying storage after a subview had captured it.
- [#142731](../micro_taxo/gh_142731.md): Attribute-related lookup could invoke hashing that mutated lifetime-sensitive state before the outer operation resumed.
- [#142732](../micro_taxo/gh_142732.md): Iterator advancement could reenter and invalidate iterator-owned state used by the outer iterator.
- [#142734](../micro_taxo/gh_142734.md): Copying an ordered mapping invoked item retrieval that could mutate the mapping while copy state was retained.
- [#142782](../micro_taxo/gh_142782.md): Cache-key comparison could clear a cache while lookup retained cache-entry state.
- [#142783](../micro_taxo/gh_142783.md): Weak-reference release invalidated cache state that subsequent code still assumed was present.
- [#142828](../micro_taxo/gh_142828.md): Callback-capable equality testing could mutate registration storage during unregister processing.
- [#142829](../micro_taxo/gh_142829.md): Context comparison could invoke code that changed the context state being compared.
- [#142830](../micro_taxo/gh_142830.md): A callback result conversion could alter callback-managed state while native callback handling retained it.
- [#142831](../micro_taxo/gh_142831.md): Mapping iteration could invoke encoding code that mutated the mapping while iteration state remained active.
- [#142882](../micro_taxo/gh_142882.md): Index conversion during extension could invalidate array storage before assignment used it.
- [#142883](../micro_taxo/gh_142883.md): Multiplier conversion could reenter and remove array storage before repetition resumed.
- [#142884](../micro_taxo/gh_142884.md): A writer callback could alter an array during output while output code retained its storage.
- [#143004](../micro_taxo/gh_143004.md): Arithmetic callback execution could mutate a counter-like mapping during update processing.
- [#143007](../micro_taxo/gh_143007.md): Integer conversion during seeking could detach or alter stream state before it was dereferenced.
- [#143008](../micro_taxo/gh_143008.md): Reentrant flushing could detach stream state during truncation before later use.
- [#143195](../micro_taxo/gh_143195.md): Length retrieval could run code that invalidated a byte buffer during hexadecimal conversion.
- [#143196](../micro_taxo/gh_143196.md): Arithmetic callback execution could invalidate an indentation cache while cached bounds were used.
- [#143197](../micro_taxo/gh_143197.md): State restoration invoked arithmetic that could invalidate retained iterator state.
- [#143198](../micro_taxo/gh_143198.md): Parameter iteration could reenter and invalidate cursor-cache state before reuse.
- [#143200](../micro_taxo/gh_143200.md): Subscription operations could reenter and remove element storage before continued access.
- [#143308](../micro_taxo/gh_143308.md): A callback and truth conversion could mutate serialization state while a buffer was retained.
- [#143309](../micro_taxo/gh_143309.md): Mapping key or value iteration could reenter and invalidate parsing state.
- [#143310](../micro_taxo/gh_143310.md): String conversion could reenter and detach interpreter-side object state before conversion resumed.
- [#143375](../micro_taxo/gh_143375.md): Seeking could trigger close and leave later stream code with a null owned buffer.
- [#143378](../micro_taxo/gh_143378.md): Buffer acquisition could invoke code that closed the output object while write processing continued.
- [#143379](../micro_taxo/gh_143379.md): Truth conversion could reenter and invalidate packing state before native packing resumed.
- [#143380](../micro_taxo/gh_143380.md): Sequence-length evaluation could reenter and invalidate statement or connection state before execution continued.
- [#143543](../micro_taxo/gh_143543.md): Key comparison could reenter and invalidate grouping iterator state while it was being used.
- [#143544](../micro_taxo/gh_143544.md): Error-construction callback execution could invalidate decoder state before error handling resumed.
- [#143545](../micro_taxo/gh_143545.md): External-timer conversion could reenter and free profiling context state still in use.
- [#143546](../micro_taxo/gh_143546.md): Equality comparison could reenter and structurally alter a set while intersection code retained its layout assumptions.
- [#143635](../micro_taxo/gh_143635.md): Representation lookup could invoke code that changed type-related state while representation retained it.
- [#143637](../micro_taxo/gh_143637.md): Index conversion could clear ancillary-data storage while parsing retained its bounds and pointer.
- [#143638](../micro_taxo/gh_143638.md): Deserialization assignment could invoke code that mutated state while build processing retained references.
- [#143639](../micro_taxo/gh_143639.md): Key hashing during deserialization could reenter and invalidate set-assignment state.
- [#143662](../micro_taxo/gh_143662.md): A text-conversion callback could close a connection while row-fetch code still relied on it.
- [#144128](../micro_taxo/gh_144128.md): Index callbacks could invalidate state retained by the enclosing native operation.
- [#144281](../micro_taxo/gh_144281.md): Shared backing storage could become invalid during buffer assignment, leaving an invalid write target.
- [#144475](../micro_taxo/gh_144475.md): Representation processing retained state whose lifetime or bounds could be invalidated during nested execution.
- [#144922](../micro_taxo/gh_144922.md): A write callback could mutate an array while output code retained a pointer into its storage.
- [#146011](../micro_taxo/gh_146011.md): A child object retained a pointer to parent-owned state after the parent was explicitly destroyed.
- [#148382](../micro_taxo/gh_148382.md): A borrowed reference survived execution of application code and was subsequently used after release.
- [#148625](../micro_taxo/gh_148625.md): Iterator advancement accessed element state after mutation or destruction invalidated it.
- [#151046](../micro_taxo/gh_151046.md): A callback received a temporary view that could outlive the buffer that owned its memory.
- [#151403](../micro_taxo/gh_151403.md): Path conversion could mutate argument storage while native process-launch code retained pointers into it.
- [#154189](../micro_taxo/gh_154189.md): Representation of a partially applied callable used state after its owning object or referenced data was freed.
