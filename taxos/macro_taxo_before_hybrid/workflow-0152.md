# Unsynchronized concurrent access to replaceable, reference-owned object fields

A shared object field stores a replaceable object reference or state marker, and concurrent readers, consumers, or mutators access it without one consistent synchronization and ownership protocol.

## Precondition

The field can be replaced, cleared, or conditionally tested by one thread while another thread reads, consumes, or derives behavior from it; the field's value may also be reference-counted or otherwise lifetime-managed.

## Critical operation

A thread reads or tests the field, or uses the pointed-to object's contents, while another thread performs a replacement, clear, or test-and-set update.

## Interference

The read and update are not covered by the same lock or critical section, or the reader does not acquire a strong/stable reference before using the value; an atomic store alone may leave the check, ownership transition, or subsequent use unsynchronized.

## Invalid assumption

It is assumed that an ordinary or individually atomic pointer access makes the whole read/update operation safe, that a value observed by a reader remains alive, or that a pre-update check uniquely determines the outcome of a concurrent mutation.

## Failure

Threads can observe stale or contradictory state, multiple threads can report a one-shot mutation as successful, race detectors can report a data race, or a reader can use a value after it has been replaced and released, causing memory-safety failure.

## Scope

The reports share a concurrent read/update and ownership-linearization failure, but the resulting symptom varies: semantic non-atomicity, race detection, or use-after-free. The pattern applies to replaceable reference-bearing fields and related state transitions, not to every concurrent field access or every pointer race.

## Search strategy

1. Find shared object fields that are read directly while another path replaces, clears, or conditionally updates them.
2. Check whether every read and write of a replaceable pointer uses the same lock or critical section, including precondition checks before the write.
3. Check whether readers acquire a strong reference or equivalent lifetime protection before dereferencing or formatting a concurrently replaceable value.
4. Check test-and-set or delete paths for a non-atomic check followed by an atomic store, exchange, or release.
5. Run race detection while stressing concurrent getters, setters, consumers, representation, invocation, and deletion of the same object.

## Evidence

- [#145272](../micro_taxo/gh_145272.md): Concurrent reads and replacement of a function-associated object reference used ordinary field access on the read side; the fix paired atomic loading with atomic exchange, directly supporting the need to synchronize both sides of the transition.
- [#146270](../micro_taxo/gh_146270.md): Concurrent deletion first checked whether a member reference was absent outside the update's critical section, allowing multiple deletions to appear successful and producing a race report; moving the check into the synchronized update restored one-shot semantics.
- [#153981](../micro_taxo/gh_153981.md): A representation operation borrowed a replaceable counter object while another operation swapped and released it; the unsynchronized read caused a race and could use a freed object, and the fix took a synchronized strong-reference snapshot.
- [#154821](../micro_taxo/gh_154821.md): Multiple function-associated reference fields were read, replaced, or mutually cleared concurrently, including fields consumed during invocation; unsynchronized replacement and release caused data races, requiring coordinated synchronization across the related fields.
