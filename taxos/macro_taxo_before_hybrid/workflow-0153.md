# A record is inserted into an ownership-tracking table under one key, then a later keyed insertion fails; failure cleanup frees it without accounting for the pre

A failure path frees a resource that remains owned by a tracking container, whose teardown frees it again.

## Precondition

Initialization allocates a record and successfully registers it in an ownership-tracking table under an initial key, so the table retains responsibility for releasing it.

## Critical operation

Initialization attempts to register the same record under an additional key and handles a failed insertion.

## Interference

The failed-insertion cleanup releases the record while the table still tracks it and will release tracked records during destruction.

## Invalid assumption

The cleanup path assumes that a failed later registration means the record was never added to the table, ignoring ownership established by the earlier registration.

## Failure

Table teardown releases the already-freed record, producing a double-free or use-after-free and crashing instead of returning a recoverable initialization error.

## Scope

This is a singleton issue report, although it contains two analogous instances. The pattern is scoped to partially completed multi-key registration with container-managed ownership; it does not assert that all insertion-failure cleanup is unsafe.

## Search strategy

1. Check multi-key registration paths for manual resource release after a later insertion fails.
2. Verify whether a container still owns a resource before failure cleanup frees it.
3. Trace destructor behavior for records partially registered before an operation reports failure.
4. Inspect reference counts or ownership markers on every allocation and release path during initialization errors.

## Evidence

- [#145301](../micro_taxo/gh_145301.md): The report documents analogous initialization bugs in two keyed ownership tables: a record is successfully added under one key, a second insertion fails, local cleanup frees the record, and container destruction frees it again; the correction preserves container ownership or frees only records never inserted.
