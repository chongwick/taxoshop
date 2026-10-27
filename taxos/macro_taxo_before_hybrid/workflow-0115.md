# Module-created managed objects remain indirectly reachable when teardown destroys modules before clearing retained callbacks.

A teardown-ordering bug where a long-lived callback registry preserves a reachability path into module-created runtime objects, preventing their reclamation.

## Precondition

Module initialization creates managed types and associated metadata, and a process- or interpreter-scoped callback registry retains a callback or callback-related object graph connected to those module-created objects.

## Critical operation

Shutdown destroys or finalizes modules while the callback registry is still populated.

## Interference

The retained callback graph keeps the module-created type graph reachable during module destruction and subsequent cleanup.

## Invalid assumption

Teardown can safely destroy modules before clearing callback registries, assuming module cleanup or a later interpreter-state cleanup will remove all remaining references.

## Failure

The managed type and transitively owned metadata are not reclaimed and leak detection reports them as indirect leaks.

## Scope

This is a singleton cluster, so the pattern is scoped to callback-retention interactions with module-created managed object graphs during interpreter or process shutdown; it does not establish that all callback registries or all module finalization paths share this defect.

## Search strategy

1. Trace shutdown ordering and verify callback registries are cleared before unloading modules that create managed runtime types.
2. Search for interpreter- or process-scoped callback containers whose retained callbacks can reference module objects, types, descriptors, or metadata.
3. Check whether module finalization relies on a later state-clear phase to break references that must be removed before module destruction.
4. Add teardown tests with callback registration enabled and leak detection to confirm module-created object graphs are fully reclaimed.

## Evidence

- [#140860](../micro_taxo/gh_140860.md): The report reproduces indirect leaks of a module-created managed type and its descriptors, dictionaries, strings, and related metadata when a retained audit callback is active; the proposed fix clears the callback registry before module destruction, directly supporting the teardown-ordering mechanism.
