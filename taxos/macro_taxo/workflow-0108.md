# A failure-retaining execution path preserves a local instance whose component materialized a managed runtime type and its supporting metadata, causing leak-detข

A failure-retaining execution path preserves a local instance whose component materialized a managed runtime type and its supporting metadata, causing leak detection to report that reachable type graph as indirect leakage.

## Precondition

Code runs under a test or diagnostic mechanism that retains failed execution context, including local variables and their referenced objects, while the component can materialize managed runtime types with associated descriptors or metadata.

## Critical operation

Exercise or instantiate the component so that it creates a runtime type and its supporting metadata, leaving the resulting object in a local variable.

## Interference

An unrelated exception occurs before that local object is released, and failure handling retains the exception context or execution frame.

## Invalid assumption

The failure path is assumed to discard locals promptly, or indirect leak reports are assumed to reflect only independently leaked allocations rather than objects still reachable through retained failure state.

## Failure

The retained object keeps its dynamically created type and auxiliary metadata reachable, so leak detection reports the type graph and its descendants as indirect leaks.

## Scope

Singleton cluster: this pattern is cautiously scoped to managed runtimes or extension components that create runtime type graphs and to test or diagnostic infrastructure that retains failed execution state. The report does not establish that every indirect leak is caused by exception retention or that the dynamic type creation itself is intrinsically leaking.

## Search strategy

1. Check failure handlers and test runners for retained exception contexts, tracebacks, frames, or local-variable snapshots.
2. Check whether an exception can occur after a dynamically typed or extension-backed object is assigned but before the assignment is cleared or the scope exits.
3. Trace first-use or initialization paths that allocate runtime types, descriptors, method tables, or related metadata, and identify their owning references.
4. Reproduce the leak with the dynamic-type operation and the failure path independently, then compare the combination against each component alone.

## Evidence

- [#140631](../micro_taxo/gh_140631.md): The report shows runtime type, descriptor, and metadata allocations during component initialization/use, while a faulty test expression can raise an unrelated name-resolution exception after an object is created; comments report that each feature alone is clean but their combination produces indirect leaks, supporting retained failure context as a

