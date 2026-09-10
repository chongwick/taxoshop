# Re-entrant mutation of an operation subject during operand conversion invalidates previously selected type-specific dispatch.

A compound operation dispatches based on the subject’s runtime type, then invokes user-controlled conversion code to obtain an operand. That callback can mutate the subject’s runtime type before the operation finishes, leaving the operation with stale dispatch and type assumptions.

## Precondition

A compound operation selects a type-specific implementation for a subject and invokes user-controlled conversion code before that implementation completes.

## Critical operation

The operation obtains or converts an operand through a callback and then proceeds to invoke the previously selected implementation on the original subject.

## Interference

The callback mutates the original subject’s runtime type while the operation is in progress; any cached type metadata must also remain safely retained across the callback.

## Invalid assumption

The operation assumes that the subject still has the type, layout, and associated metadata that justified the earlier dispatch, without revalidating those conditions after user code returns.

## Failure

The stale implementation accesses the subject under incompatible type or layout assumptions, causing an invalid internal access and process termination instead of a recoverable operation or type error.

## Scope

This is a cautiously scoped singleton pattern based on one report. It covers re-entrant compound operations whose conversion callbacks can mutate the operation subject; it does not claim that every callback-induced mutation causes a crash.

## Search strategy

1. Check compound operations for user-controlled conversion callbacks between dispatch selection and type-specific subject access.
2. Check whether conversion callbacks can mutate the subject’s runtime type or replace its representation during the operation.
3. Check whether cached dispatch and type metadata are revalidated and safely retained after callbacks return.
4. Check failure paths for invalid field access when the subject no longer matches the implementation selected before re-entry.

## Evidence

- [#142883](../micro_taxo/gh_142883.md): The report demonstrates that operand conversion can change the left-hand subject’s runtime class during multiplication, after which the previously selected operation function is still called and can crash; the corrective behavior is to detect the type change and raise a type error.
