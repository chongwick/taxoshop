# Teardown-ordering retains callback-connected module runtime graphs

A process- or interpreter-scoped callback registry can keep a reference path into runtime types and metadata created during module initialization, so shutdown leaks the connected object graph when modules are destroyed before callbacks are cleared.

## Precondition

Module initialization creates managed runtime types with associated descriptors, dictionaries, strings, or other metadata, and a long-lived callback mechanism retains callback-owned state that can reference or become connected to those module-created objects.

## Critical operation

Initialize the module and activate or register the callback mechanism, then begin interpreter or process teardown.

## Interference

Teardown destroys or finalizes modules while the callback registry and its callback-related object graph are still retained, preserving reachability into the module-created graph; an unrelated failing operation may occur in the same run but is not established as the cause.

## Invalid assumption

Module cleanup, garbage collection, or later interpreter-state clearing is assumed to break all references, even though callback references must be removed before module destruction for the module-created graph to become reclaimable.

## Failure

Leak detection reports the created runtime type and transitively connected metadata as indirect leaks. This is retained reachability during teardown, not use of stale or freed state.

## Scope

Both reports support callback-retention and teardown ordering, but the first includes an incidental failing expression and does not independently prove the exact reference path. The pattern is scoped to callback systems whose retained state reaches module-created runtime object graphs during teardown; it does not generalize to every indirect leak, callback registry, or exception-associated leak.

## Search strategy

1. Trace interpreter and process shutdown ordering, and verify callback registries are cleared before modules that create managed runtime types are destroyed.
2. Search callback containers for retained closures, hooks, event records, or argument objects that can reference module objects, runtime types, descriptors, or metadata.
3. Check whether module finalization depends on clearing module-owned references while an external callback registry still holds a path into the same object graph.
4. Reproduce module initialization and callback registration independently and together under leak detection, separating teardown retention from any unrelated exception or failed operation.
5. Verify that garbage collection and later interpreter-state cleanup occur after callback references are removed rather than treating those phases as substitutes for ordering.

## Evidence

- [#140631](../micro_taxo/gh_140631.md): The report shows that a module-created managed type and its descriptors and metadata are reported as indirect leaks when combined with an active audit callback, while each feature alone is reported as clean; its unrelated name-resolution failure is not sufficient evidence for a failure-context mechanism.
- [#140860](../micro_taxo/gh_140860.md): The report directly attributes the leak to retained audit-hook references reaching a module-created managed type and records that clearing the callback registry before module destruction avoids the cycle, supporting the teardown-ordering mechanism.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0108](../macro_taxo_before_hybrid/workflow-0108.md)
- [workflow-0115](../macro_taxo_before_hybrid/workflow-0115.md)
