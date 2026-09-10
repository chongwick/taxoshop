# Concurrent access to mutable shared state without effective synchronization or lifetime protection

A shared pointer, descriptor, dispatch value, buffer, object field, or external-library state is accessed concurrently while another path can change or invalidate it.

## Precondition

An active operation reads, follows, or uses mutable shared state whose value or backing storage can be replaced, modified, freed, reinitialized, or cleaned up concurrently.

## Critical operation

The operation loads or uses that state across a period during which its validity, contents, or ownership must remain stable.

## Interference

Another thread or lifecycle path concurrently mutates, replaces, reallocates, closes, detaches, reinitializes, or frees the state; the apparent runtime guard is absent, one-sided, or suspended across the native operation.

## Invalid assumption

The operation assumes the shared value remains consistently observable and alive for the whole access, and that an apparent lock or borrowed reference provides sufficient protection.

## Failure

The overlap produces a data race or inconsistent observation; depending on the state, it can cause altered dispatch, stale or dangling references, use-after-free, heap corruption, external-library failure, or a crash.

## Scope

The shared pattern is broader than resource handles: it covers per-object fields, dispatch metadata, borrowed references, exported buffers, process-global state, and external-library state. Some reports are sanitizer-only or behaviorally benign, while others are memory-unsafe; the common defect is missing effective coordination and/or lifetime protection. It does not imply that every concurrent read is unsafe when immutable state, atomic publication, or a complete lifetime protocol is present.

## Search strategy

1. Check every shared mutable pointer, descriptor, dispatch slot, buffer address, object field, and process-global state for concurrent readers and writers.
2. Trace whether close, detach, resize, replacement, reinitialization, cleanup, or configuration paths can overlap an active operation and invalidate what it uses.
3. Verify that one effective mutex or atomic protocol covers both sides of each access and remains effective across native calls and released-lock regions.
4. Check borrowed references and exported views for lifetime guarantees lasting through the entire read or use.
5. Exercise concurrent use with lifecycle, reconfiguration, shutdown, and external-library calls under thread and address sanitizers.

## Evidence

- [#116912](../micro_taxo/gh_116912.md): A native descriptor field is written by close or detach while another thread reads it during an operation outside the usual interpreter lock, producing a sanitizer-reported race.
- [#128050](../micro_taxo/gh_128050.md): A dispatch pointer is lazily changed during a call while other threads read it, showing that even a seemingly benign fast-path mutation is still an unsynchronized shared-state race.
- [#128100](../micro_taxo/gh_128100.md): A shared object-storage pointer is read while another path replaces the storage; a borrowed reference can then outlive the replaced storage and become use-after-free.
- [#128144](../micro_taxo/gh_128144.md): An object field has an atomic writer but a non-atomic reader, demonstrating that one-sided atomicity does not make concurrent access race-free.
- [#132886](../micro_taxo/gh_132886.md): The same native descriptor race occurs where the runtime lock had been assumed to provide safety, requiring coordinated atomic reads and writes across build configurations.
- [#143756](../micro_taxo/gh_143756.md): Concurrent operations access shared external-library and object state; a method-level critical section is ineffective across a released region, so the native operation needs an explicit mutex covering its full critical sequence.
- [#144567](../micro_taxo/gh_144567.md): Concurrent mutation of process-global locale state frees or replaces storage while another thread decodes the returned pointer, causing heap use-after-free and a crash.
- [#145933](../micro_taxo/gh_145933.md): Worker operations race external-library cleanup during process exit, using library-global state after it has been freed.
- [#154524](../micro_taxo/gh_154524.md): A buffer pointer is read while resizing reallocates and frees its backing storage; synchronization alone is insufficient without a lifetime rule for live exports.
