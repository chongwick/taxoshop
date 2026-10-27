# Reentrant finalization republishes an object while its destruction path still owns teardown, leaving shared lifetime bookkeeping inconsistent.

Reentrant finalization can restore an object’s visibility in a shared registry after destruction has begun, while the original teardown still proceeds and invalidates the object.

## Precondition

A managed object is being destroyed, and its finalization path can invoke user-controlled or indirect callback code before teardown has completed.

## Critical operation

The destruction path runs that finalization logic while the object is still eligible to be associated with a shared registry or retention structure.

## Interference

The callback re-registers, retains, or otherwise republishes the object in that registry during the in-progress destruction.

## Invalid assumption

The remaining teardown assumes finalization cannot make the object reachable again, so it continues unregistering, releasing, or invalidating the object without reconciling the new registry entry.

## Failure

The registry later exposes the retained entry, and subsequent access reaches storage or state already invalidated by teardown, causing use-after-free behavior or a process-terminating failure.

## Scope

This is a cautiously scoped singleton pattern. It applies to managed-object destruction paths that permit reentrant finalization and shared registry visibility; the report does not establish a broader rule covering all finalizer callbacks or all resurrection mechanisms.

## Search strategy

1. Inspect destruction paths for callbacks or finalizers that run before all registry links and object state are dismantled.
2. Check whether finalization code can re-register, retain, resurrect, or republish the object through shared lookup structures.
3. Verify that teardown detects and handles renewed reachability before releasing or invalidating object storage.
4. Trace registry lookups after destruction for entries whose target may have been invalidated during reentrant finalization.

## Evidence

- [#142556](../micro_taxo/gh_142556.md): The report shows that finalization can re-register a managed object while its destructor is still running; the destructor then continues and frees the object, leaving the registry pointing at invalid storage and causing a crash on later use.
