# Unsynchronized concurrent access to shared runtime state

Concurrent execution accesses shared object, interpreter, extension, iterator, cache, lifecycle, or resource state without a synchronization protocol that covers all conflicting operations.

## Precondition

The same mutable state, including state mutated lazily or during initialization, teardown, iteration, or caching, is reachable from multiple threads.

## Critical operation

A thread reads, writes, initializes, advances, clears, or releases that shared state.

## Interference

Another thread concurrently performs a conflicting access to the same state without a common lock, atomic protocol, or lifetime handoff.

## Invalid assumption

The implementation assumes that prior serialization, apparent read-only use, one-time initialization, or independent callers prevents overlap or makes ordinary field access safe.

## Failure

The conflicting accesses constitute a data race with undefined behavior; race instrumentation reports it, and some cases produce corrupted state, leaks, double release, crashes, or invalid results.

## Scope

This pattern is broader than shared byte storage: the evidence covers any shared mutable runtime state. It does not claim that all concurrent use is unsafe; it applies when conflicting accesses lack a common synchronization, atomic-publication, or lifetime-management protocol.

## Search strategy

1. Audit shared fields read or written after releasing global or object-level serialization.
2. Require lazy cache and one-time initialization paths to use an atomic publication or a lock.
3. Check iterator advance, close, clear, and destruction paths for concurrent ownership and lifetime handoff.
4. Review extension and foreign-library callbacks for shared mutable context, configuration, and resource state.
5. Test concurrent getters, setters, initialization, finalization, and iteration under race detection.

## Evidence

- [#73069](../micro_taxo/gh_73069.md): Concurrent iteration, cached metadata creation, and resource closure accessed shared iterator and entry state without sufficient coordination.
- [#113956](../micro_taxo/gh_113956.md): Allocation-related object state required thread-affine initialization to avoid concurrent unsafe state changes.
- [#116912](../micro_taxo/gh_116912.md): Concurrent access to a shared operating-system resource handle produced a race report.
- [#128013](../micro_taxo/gh_128013.md): Concurrent lazy creation and publication of a text representation raced with access to the same object state.
- [#128050](../micro_taxo/gh_128050.md): Concurrent readers and writers of callable dispatch metadata raced during invocation.
- [#128100](../micro_taxo/gh_128100.md): Attribute access and concurrent dictionary setup conflicted on shared object state.
- [#128130](../micro_taxo/gh_128130.md): Concurrent evaluation raced on a shared runtime signal-status field.
- [#128133](../micro_taxo/gh_128133.md): Concurrent hash caching performed an ordinary read and write of the same shared field.
- [#128137](../micro_taxo/gh_128137.md): Concurrent interning mutated shared text-object or intern-table state without complete synchronization.
- [#128144](../micro_taxo/gh_128144.md): Concurrent member retrieval and replacement conflicted on a shared object reference field.
- [#128212](../micro_taxo/gh_128212.md): A representation update raced with a consistency check reading the same text-object state.
- [#129701](../micro_taxo/gh_129701.md): Concurrent intern-table operations exposed unsynchronized shared interning state.
- [#129824](../micro_taxo/gh_129824.md): Subinterpreter concurrency exercises exposed races in shared interpreter-related state.
- [#130019](../micro_taxo/gh_130019.md): Concurrent type allocation accessed shared allocation-related state without adequate synchronization.
- [#130091](../micro_taxo/gh_130091.md): Thread-local-storage deletion raced with thread attachment over shared lifecycle state.
- [#130421](../micro_taxo/gh_130421.md): Concurrent extension use exposed races across reference, allocation, construction, operation, and interpreter-initialization state.
- [#130605](../micro_taxo/gh_130605.md): Concurrent executor activity exposed a race in thread-acquisition state.
- [#130977](../micro_taxo/gh_130977.md): Concurrent buffer export, release, and shared container access lacked a complete publication and lifetime protocol.
- [#132886](../micro_taxo/gh_132886.md): Even with global serialization enabled, operations releasing it allowed a shared resource handle to race.
- [#133473](../micro_taxo/gh_133473.md): Concurrent queue activity triggered a race report on shared synchronization-related state.
- [#140138](../micro_taxo/gh_140138.md): Daemon-thread shutdown overlapped with shared runtime state changes.
- [#140257](../micro_taxo/gh_140257.md): Finalization and a concurrently active daemon thread raced over interpreter lifecycle state.
- [#140260](../micro_taxo/gh_140260.md): Concurrent interpreter/module initialization raced while publishing shared module state.
- [#140263](../micro_taxo/gh_140263.md): A two-thread locking exercise exposed an unsynchronized conflicting access.
- [#142717](../micro_taxo/gh_142717.md): Concurrent execution in generated code caused a race that manifested as an invalid memory access.
- [#143756](../micro_taxo/gh_143756.md): Concurrent foreign-library binding operations raced on shared binding or library state.
- [#144356](../micro_taxo/gh_144356.md): Iterator metadata was read and updated concurrently without a sufficient atomic protocol.
- [#145272](../micro_taxo/gh_145272.md): Concurrent replacement and use of function metadata raced on shared function state.
- [#145933](../micro_taxo/gh_145933.md): Concurrent cryptographic-library use exposed a shared-state race.
- [#149142](../micro_taxo/gh_149142.md): Shared arithmetic-context flags were mutated non-atomically while concurrently accessed.
- [#150191](../micro_taxo/gh_150191.md): Concurrent callback-related cryptographic processing raced over shared data consumed by a foreign routine.
- [#150284](../micro_taxo/gh_150284.md): Concurrent thread-list traversal and thread attachment exposed shared interpreter-state races.
- [#151277](../micro_taxo/gh_151277.md): A concurrent callback scenario reproduced a race in shared data passed to a foreign routine.
- [#151722](../micro_taxo/gh_151722.md): Readers observed a mapping while its construction and resizing still mutated shared storage.
- [#152741](../micro_taxo/gh_152741.md): Inspection of thread exception state raced with concurrent thread attachment.
- [#153014](../micro_taxo/gh_153014.md): A configuration getter and setter concurrently read and wrote a shared debug flag.
- [#153201](../micro_taxo/gh_153201.md): Concurrent cryptographic test activity exposed shared memory races observable by race detection.
- [#153852](../micro_taxo/gh_153852.md): A collection of minimal concurrent reproducers documented recurring unsynchronized shared-state accesses in free-threaded execution.
- [#153908](../micro_taxo/gh_153908.md): A representation operation plainly read iterator state while another thread could update it.
- [#153928](../micro_taxo/gh_153928.md): Concurrent text-object operations raced on shared representation and lifetime state, including a crash manifestation.
- [#154043](../micro_taxo/gh_154043.md): Concurrent advancement of one iterator raced on its current-object field and could double release it.
- [#154044](../micro_taxo/gh_154044.md): Concurrent lazy name-cache initialization raced and could leak a losing cached value.
- [#154130](../micro_taxo/gh_154130.md): Sharing an iterator across threads allowed concurrent state updates and duplicate release of its referenced container.
- [#154535](../micro_taxo/gh_154535.md): Concurrent iterator advancement corrupted a shared cursor and could crash.
- [#154756](../micro_taxo/gh_154756.md): Concurrent sorting accessed mutable sequence state without a protocol preventing conflicting operations.
- [#154821](../micro_taxo/gh_154821.md): Concurrent reads and updates of function naming metadata raced on shared fields.
