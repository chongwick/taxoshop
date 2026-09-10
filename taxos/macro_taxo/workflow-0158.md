# Concurrent handshake workers reuse one mutable connection or security context, and the underlying library is not safe for overlapping handshakes on that sharedÂ

Concurrent handshake workers reuse one mutable connection or security context, and the underlying library is not safe for overlapping handshakes on that shared context.

## Precondition

A workflow starts multiple handshake workers against the same mutable connection or security context.

## Critical operation

Each worker performs a handshake that accesses library-managed state stored in the shared context.

## Interference

Overlapping handshakes concurrently access that shared internal state without sufficient synchronization.

## Invalid assumption

The caller or test assumes that the shared context is safe for simultaneous handshakes, or assumes the only relevant race is the separately targeted configuration update.

## Failure

Race detection reports an internal library-state data race, causing the check to fail independently of the intended configuration-update race.

## Scope

This is a singleton cluster, so the pattern is scoped to overlapping handshakes that reuse one mutable context in a library with unsynchronized internal state. It does not establish that all connection contexts or all handshake implementations are unsafe for concurrent use.

## Search strategy

1. Check whether concurrent handshake workers reuse the same mutable connection or security context.
2. Check whether handshake code accesses library-managed context state concurrently without documented synchronization.
3. Check whether a test combines simultaneous handshakes with a separate configuration-update race.
4. Check whether race-detection failures originate from shared library context state rather than the intended application-level operation.

## Evidence

- [#150191](../micro_taxo/gh_150191.md): The report supports that multiple simultaneous handshakes against one shared context expose an internal data race, while the intended test target is a separate concurrent configuration update; reducing handshakes to one worker removes the unrelated race.
