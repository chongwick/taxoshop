# Resource ownership is lost when initialization or replacement overwrites the only cleanup handle for an earlier allocation.

Resource ownership is lost when initialization or replacement overwrites the only cleanup handle for an earlier allocation.

## Precondition

An acquired resource is represented by mutable object metadata or a singleton state slot that is also writable during later initialization or replacement.

## Critical operation

A later initialization or replacement acquires or installs new state and writes it into that shared metadata or state slot.

## Interference

The write discards the earlier resource's only reachable cleanup handle before the earlier resource is explicitly released.

## Invalid assumption

Teardown assumes the current object or state slot still identifies every resource acquired previously.

## Failure

The earlier resource becomes unreachable and is leaked; repeated replacement can cause persistent memory growth, while a one-time replacement can cause a one-time leak.

## Scope

The shared mechanism is loss of cleanup reachability during reinitialization or replacement. The reports differ between per-object allocation metadata and library-managed singleton state, and do not establish that every instance repeats indefinitely or that automatic release is always safe when external users may still hold references.

## Search strategy

1. Trace each acquisition and verify that the previous owner is released before its cleanup handle is overwritten.
2. Inspect initialization and replacement assignments to ownership fields or singleton resource slots for an explicit release of the prior value.
3. Check teardown and error paths against all resources acquired before reinitialization, replacement, or alignment adjustment.
4. Run repeated acquire-reinitialize-teardown sequences under leak detection and verify one release per acquisition.

## Evidence

- [#140067](../micro_taxo/gh_140067.md): An aligned allocation stored its original base address in object metadata, and later object initialization overwrote that field; teardown could no longer recover the base address, so repeated object creation leaked allocations.
- [#144067](../micro_taxo/gh_144067.md): A first terminal resource was stored in a singleton current-state slot, then later terminal initialization replaced the slot without freeing the previous resource, leaving that allocation unreachable.
