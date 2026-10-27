# Concurrent advancement of a shared stateful iterator interleaves a multi-field traversal-state update, desynchronizing the cursor and causing a subsequent dere-

Concurrent callers can corrupt a shared iterator whose traversal cursor is represented by several coupled fields, turning a valid iteration step into an invalid pointer dereference.

## Precondition

The same stateful iterator instance is advanced concurrently in a free-threaded environment, and its traversal state includes coupled level, position, and node-reference fields.

## Critical operation

Advance one logical iteration step through a multi-level structure, updating several cursor fields across descent or ascent operations.

## Interference

Another thread interleaves its reads and writes while the first step is only partially complete, leaving the cursor level and associated position or node-reference slots inconsistent.

## Invalid assumption

The cursor level always identifies an initialized, current, valid node reference whose lifetime remains safe to dereference.

## Failure

The next iteration step reads or dereferences a null, stale, or otherwise wild node pointer, causing a memory-safety crash instead of only producing skipped or duplicated results.

## Scope

This is a cautious singleton pattern based on one report. It applies to shared iterators with multi-field mutable traversal state and pointer-bearing cursor slots; the evidence does not establish the rule for all iterator implementations or for concurrent mutation of the underlying collection.

## Search strategy

1. Check whether one iterator object can be advanced by multiple threads without per-iterator synchronization.
2. Trace every multi-step cursor update and verify that level, position, and node-reference fields cannot be observed in a partially updated combination.
3. Check whether cursor slots contain borrowed or otherwise lifetime-sensitive references that can be dereferenced after an interleaved update.
4. Verify that the next-step logic validates the selected cursor slot before type inspection, size inspection, or other pointer dereference.

## Evidence

- [#154535](../micro_taxo/gh_154535.md): A shared depth-first iterator cursor was advanced concurrently without synchronization; interleaved updates mismatched the current level with its node-pointer slot, and the next step dereferenced a stale or null borrowed pointer, producing a segmentation fault even though the underlying structure was immutable.
