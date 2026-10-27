# Reentrant teardown repopulates state after cleanup has passed it

During per-thread or component teardown, destroying stored values can execute user finalization code that re-enters the same state owner and recreates cleared state. A fixed one-pass cleanup then misses the newly created state, leaving allocations behind.

## Precondition

Teardown is clearing state that contains values whose destruction may execute arbitrary user finalization code, and that code can access the state being dismantled or related teardown state.

## Critical operation

The teardown clears state entries sequentially and destroys a value, thereby invoking its finalizer while cleanup is still in progress.

## Interference

The finalizer re-enters the teardown-owned state and recreates a container, key, sentinel, bookkeeping object, or another state entry that was already cleared or is not yet covered by the cleanup traversal.

## Invalid assumption

The cleanup sequence assumes that the set of state requiring destruction remains stable while entries are being cleared, so a fixed ordering or single pass is sufficient.

## Failure

State recreated by finalization falls outside the original cleanup sequence and remains allocated after the worker or component finishes; changing cleanup order can merely move the leak to a different state dependency.

## Scope

This is a singleton cluster, so the pattern is cautiously scoped to teardown routines that invoke reentrant user finalization while clearing mutable per-thread or related state; it does not claim that every shutdown leak involves reentrant recreation.

## Search strategy

1. Check whether teardown destroys values whose finalizers can execute user code.
2. Check whether finalizers can re-enter the state owner or recreate state associated with the teardown context.
3. Check whether cleanup uses a fixed ordered sequence or snapshot without revisiting state created during callbacks.
4. Check whether cleanup-order changes only transfer leaks between related teardown fields instead of establishing a complete reentrant cleanup protocol.

## Evidence

- [#140798](../micro_taxo/gh_140798.md): The report demonstrates that destruction of a per-thread stored value can run user finalization that recreates per-thread bookkeeping, leaving newly allocated objects leaked; its discussion generalizes the cause to sequential teardown where clearing one field can reinitialize that field or fields already cleared.
