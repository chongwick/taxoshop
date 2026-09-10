# Error-path ownership loss in native operations

An operation owns temporary state while processing input or invoking validation-dependent work, then an exceptional exit fails to discharge that ownership.

## Precondition

The operation acquires an owned intermediate, temporary, iterator, builder, callback result, or converted value before all later validation and failure-prone steps have completed.

## Critical operation

It parses, converts, builds, formats, invokes a callback, or performs another fallible step and routes failure through an error return or cleanup label.

## Interference

Invalid input or type, a rejecting callback or audit hook, a preexisting exception, or an allocation/preparation failure interrupts the normal success sequence after the owned state exists.

## Invalid assumption

The implementation assumes every failure path reaches complete cleanup and that the cleanup code still refers to the acquired resource; an early return or variable shadowing can invalidate either assumption.

## Failure

The operation reports its recoverable error but leaves the intermediate ownership live, so repeated calls or process-exit leak checking reports a direct, indirect, or reference leak.

## Scope

The shared pattern is an error-path ownership/cleanup defect in resource-managing native code, not specifically a text parser defect. Nine reports establish this mechanism; the recursion-related report has an unconfirmed, unreproducible cause and is retained as a boundary case rather than generalized evidence.

## Search strategy

1. Trace every owned allocation or reference from acquisition through each validation, callback, conversion, and allocation-failure exit; require cleanup on every path.
2. Inspect error labels and early returns after temporary-state creation; verify that each path releases all resources acquired in the current scope.
3. Check for inner-scope declarations that shadow resource variables used by shared cleanup or error labels.
4. Exercise invalid arguments, rejecting callbacks or hooks, preexisting exceptions, and simulated allocation failures immediately after each intermediate is created.

## Evidence

- [#139751](../micro_taxo/gh_139751.md): A parsing operation decodes an intermediate value before rejecting an invalid argument; the error return leaves that decoded allocation unreclaimed. The report also contains a separate unrelated reproducer, so only the parser case supports this mechanism.
- [#139988](../micro_taxo/gh_139988.md): A builder creates owned container state and accumulates values before rejecting a nonconforming argument; failure returned without finalizing the builder, leaking the builder and its contents.
- [#140398](../micro_taxo/gh_140398.md): Several conversion paths create an owned converted value before an audit hook can fail; the audit-error returns omitted release of that converted value.
- [#140406](../micro_taxo/gh_140406.md): A method result is owned before its type is validated; rejecting the wrong result type raises an error without releasing the returned object.
- [#140530](../micro_taxo/gh_140530.md): Constructing an error-related intermediate produces a mortal nonconforming value; the type-check failure jumps to a shared error path without releasing that value.
- [#140593](../micro_taxo/gh_140593.md): A parser callback path owns a content-model allocation, but an already-set error takes a direct return instead of the common finalization path, leaving the model allocated.
- [#140939](../micro_taxo/gh_140939.md): Formatting creates a temporary value before a buffer-growth operation can fail; that preparation failure jumps to the general error path without releasing the temporary.
- [#142917](../micro_taxo/gh_142917.md): The report records a sanitizer leak after an exceptional recursion-related test, but provides no confirmed ownership path, fix, or reproducible root cause; it supports only that such reports need separate validation.
- [#147998](../micro_taxo/gh_147998.md): A resource created in an inner branch is shadowed by a new declaration, so the later error cleanup sees a different binding and cannot release the resource.
- [#148484](../micro_taxo/gh_148484.md): An iterator is acquired before typecode validation and several later initialization steps; invalid typecode and other failures return without releasing it, and the fix adds cleanup to those exits.
