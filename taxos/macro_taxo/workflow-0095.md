# A concurrency check polls or delays before directly inspecting shared state that another thread updates atomically, but performs the inspection with a non-atom

A concurrency check polls or delays before directly inspecting shared state that another thread updates atomically, but performs the inspection with a non-atomic, unsynchronized read.

## Precondition

Shared synchronization state is concurrently accessible, with one thread updating it through atomic operations while another thread later checks its value.

## Critical operation

The checking thread reads the shared state directly to assert an expected combination of bits or flags after timing-based polling or delay.

## Interference

The worker can still perform an atomic update while the checking thread executes that ordinary read; the delay or polling does not establish a synchronization relationship.

## Invalid assumption

Assuming that timing-based progress or the writer's atomic update makes a concurrent non-atomic read safe.

## Failure

A race detector reports a data race between the atomic write and ordinary read, causing the concurrency test or assertion run to fail.

## Scope

This is a singleton cluster. It supports the mixed atomic-write/non-atomic-read pattern in concurrency tests, specifically where timing-based progress is mistaken for synchronization; it does not establish that all polling or delayed inspections are unsafe.

## Search strategy

1. Search for shared synchronization flags or bit fields written with atomic operations but read directly in assertions or diagnostics.
2. Check whether sleeps, polling loops, or timing-based progress checks precede a non-atomic read of state updated by another thread.
3. Verify that every cross-thread read of atomically updated state uses an atomic load or an equivalent lock-protected access.

## Evidence

- [#140263](../micro_taxo/gh_140263.md): The report documents a race between an atomic update of shared lock-state bits by a worker and a direct read by the checking thread after sleep-based polling; replacing the direct read with a relaxed atomic load removes the race.
