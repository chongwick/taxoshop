# A lock-acquisition path asserts that a successful ownership handoff must leave the lock’s state marked as held, even though the protocol permits another worker—

A lock-acquisition path asserts that a successful ownership handoff must leave the lock’s state marked as held, even though the protocol permits another worker to release it concurrently.

## Precondition

Multiple workers contend for a shared lock, and a waiting worker receives ownership through a handoff.

## Critical operation

The recipient completes the acquisition path and validates the lock’s current state before reporting successful acquisition.

## Interference

Another permitted worker releases the lock concurrently, clearing its visible held state before or around the recipient’s return.

## Invalid assumption

Successful handoff guarantees that the lock remains visibly held until acquisition completion.

## Failure

The valid interleaving violates the assertion and terminates the process instead of reporting successful acquisition.

## Scope

This is a cautiously scoped singleton pattern for lock implementations that permit one worker to release a lock acquired by another, including during handoff completion; it does not apply to protocols that forbid such releases or guarantee stable state through return.

## Search strategy

1. Inspect handoff-based acquisition paths for assertions that ownership transfer requires the lock to remain marked held.
2. Check whether the synchronization contract permits a different worker to release the lock during or immediately after handoff.
3. Compare asserted state invariants with the protocol’s permitted ownership and release semantics.
4. Review whether acquisition success remains valid when the lock state changes concurrently before the result is returned.

## Evidence

- [#143424](../micro_taxo/gh_143424.md): The report shows that ownership obtained through handoff can be followed by a permitted concurrent release, leaving the lock state clear while the acquisition routine is completing; the stronger state assertion then aborts the process.
