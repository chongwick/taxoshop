# Concurrent unsynchronized access to shared mutable storage or state

Multiple threads retain aliases to the same mutable storage or object state, while at least one operation mutates it and another reads or mutates it concurrently without a complete shared synchronization protocol.

## Precondition

Mutable backing storage, container representation, iterator state, extension state, or external-library state is reachable by multiple threads or through independent views, handles, or callbacks.

## Critical operation

A thread performs an in-place update, read-modify-write, publication, reordering, exhaustion transition, or buffer handoff on that shared state while another thread accesses related bytes, fields, pointers, metadata, or lifetime state.

## Interference

The accesses are not ordered by the same lock, atomic protocol, ownership rule, or safe snapshot mechanism. Partial protection is insufficient when aliases bypass the lock, a dependent field is published before its contents, a private cursor is updated outside the container lock, or a consumer retains a buffer after handoff.

## Invalid assumption

The implementation assumes that object reachability, a sequencing point, atomic access to one field, or locking only the enclosing container makes the entire representation and its lifetime stable for concurrent readers and writers.

## Failure

The conflicting accesses constitute undefined behavior or an invalid intermediate state. Race detectors report the conflict, and executions may observe inconsistent data, corrupt container state, trigger assertions or crashes, double-release or use freed memory, or expose stale or partially initialized contents.

## Scope

The shared mechanism is broader than byte buffers: the reports cover aliases to raw storage, containers, iterators, scalar fields, pointers, and external-library objects. It applies where concurrent access is permitted or accidentally exposed; some APIs may instead require caller-provided synchronization, and a race-detector report alone does not establish that the implementation must serialize intentionally unsupported use.

## Search strategy

1. Search for shared backing storage or views passed to multiple threads and verify that every read and write uses one common synchronization or ownership protocol.
2. Inspect multi-field publication and mutation sequences and verify that dependent contents become visible before indexes, pointers, lengths, or state flags are exposed.
3. Check every reader path—including formatting, length queries, iteration, callbacks, and cleanup—for the same lock or atomic protocol used by writers.
4. Find in-place algorithms on shared containers and require locking, atomic element updates, or copy/snapshot-and-swap isolation before mutation.
5. Stress shared handles and buffers with concurrent mutation, exhaustion, reuse, and destruction under a race detector and memory-safety instrumentation.

## Evidence

- [#130977](../micro_taxo/gh_130977.md): Independent views of one mutable byte backing store concurrently perform element reads and writes; the race detector reports the plain read/write conflict.
- [#131325](../micro_taxo/gh_131325.md): A reusable read buffer is handed to an asynchronous consumer before the producer has established the required sequencing, allowing a later fill to race with transmission of the earlier view.
- [#132869](../micro_taxo/gh_132869.md): Concurrent lookup can observe an index before the associated key is initialized because publication order and lookup synchronization do not match, producing an invalid null entry and crash.
- [#142717](../micro_taxo/gh_142717.md): Multiple threads perform compound push, pop, and read operations on one shared sequence without synchronization, corrupting its transient representation and causing an invalid-memory crash; the JIT exposed the timing but was not the underlying contract.
- [#144356](../micro_taxo/gh_144356.md): Iterator length and advancement race with set mutation and with concurrent use of the same iterator; protecting only the underlying set leaves iterator cursor, exhaustion, and reference-release state vulnerable to races and double release.
- [#149142](../micro_taxo/gh_149142.md): A shared numeric context performs unsynchronized flag read-modify-write and clearing operations across threads, so status and trap state require a common mutex or equivalent coordination.
- [#151277](../micro_taxo/gh_151277.md): Concurrent comparison reads mutable external-library string storage while another operation replaces its contents, and the library's internal synchronization does not cover both access paths.
- [#153908](../micro_taxo/gh_153908.md): A writer uses atomic or critical-section updates while representation code reads the same fast-path scalar or slow-path pointer plainly, causing both a race and, for replaced objects, a possible use-after-free.
- [#154756](../micro_taxo/gh_154756.md): An in-place ordering algorithm writes sequence slots while other threads iterate the same sequence; plain stores race with readers, motivating synchronization or copy-and-swap isolation.
