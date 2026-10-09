# Escaped managed-object references across runtime or ownership lifetimes

Managed objects or their metadata are retained outside the state that owns them, so later cleanup, reinitialization, or a foreign finalizer can act on references whose lifetime has ended.

## Precondition

An extension, embedding layer, or foreign-runtime bridge retains managed-object references in persistent state or exposes them to another owner beyond their originating runtime, interpreter, or collector lifetime.

## Critical operation

The owning runtime tears down state, reinitializes, or runs finalization and releases objects that the retained references still designate.

## Interference

Persistent extension state or a foreign finalizer subsequently reads, copies, decrements, or frees a retained reference after its owner has reclaimed it; alternatively, cleanup is suppressed to avoid that outcome.

## Invalid assumption

A managed-object pointer remains valid and may be released by retained or foreign state after the owning runtime or ownership domain has ended.

## Failure

Cleanup suppression leaves allocations reachable as leaks; otherwise stale-reference use produces use-after-free, invalid or double free, memory corruption, or a crash.

## Scope

The common mechanism is lifetime and ownership escape of managed objects, not teardown alone. One report concerns a foreign-runtime bridge rather than repeated runtime initialization, and the leak reports may be benign process-lifetime retention unless the retained state is reused or cleanup is made strict.

## Search strategy

1. Audit process-global and static state for managed-object pointers, type metadata, and caches; bind each to its owning runtime or interpreter instance.
2. Verify every extension and embedding teardown path releases owned managed objects and nulls persistent references before runtime destruction.
3. Exercise initialize–use/import–finalize–reinitialize cycles under address and leak sanitizers.
4. Review foreign-runtime finalizers and callbacks to ensure they use the owning runtime's lifetime and release protocol rather than directly freeing or decrementing shared objects.
5. Flag cleanup exemptions that preserve managed objects across shutdown; replace them with explicit teardown and reconstruction on the next initialization.

## Evidence

- [#100773](../micro_taxo/gh_100773.md): Shows persistent extension state retaining allocation across runtime shutdown, with conversion from shared state to instance-associated state used to address teardown leakage.
- [#113190](../micro_taxo/gh_113190.md): Shows that retaining runtime-created objects across finalization causes leaks when cleanup is withheld, while freeing them makes stale references after reinitialization use-after-free hazards.
- [#113576](../micro_taxo/gh_113576.md): Provides a sequential initialize/finalize/reinitialize reproducer where an extension retained state from a prior runtime and later copied freed storage; isolating extension state per interpreter resolves the newer branches.
- [#113591](../micro_taxo/gh_113591.md): Shows a foreign runtime's finalizer releasing an object through the wrong ownership/lifetime path, producing a crash; the analysis identifies illegal retained references or destruction in the bridge rather than collector scheduling.
