# Generated derived-class callables resolve inherited deferred annotations in the wrong namespace.

Cross-module class transformation can detach inherited deferred annotations from their defining namespace, so later resolution of the derived class or generated initializer sees missing or shadowed names.

## Precondition

A base class exposes deferred textual annotations, and a transformation generates or reuses a derived-class initializer across a module boundary.

## Critical operation

The transformation copies inherited annotation text into generated callable metadata or resolves it using the derived class's module globals instead of preserving the defining context.

## Interference

Later type-hint evaluation lacks imports from the defining module or finds same-named objects in the derived module.

## Invalid assumption

The namespace used to build the derived class or callable is sufficient to resolve inherited annotation text.

## Failure

Annotation resolution fails or silently reconstructs inherited annotations as incorrect types.

## Scope

This singleton pattern is scoped to class-generation or transformation workflows that propagate deferred annotations across module boundaries; it does not claim that all annotation-resolution failures have this cause.

## Search strategy

1. Trace transformations that copy deferred annotation strings across class or module boundaries, and verify that definition-time namespace provenance is preserved.
2. Inspect generated or reused callable metadata and confirm its resolution namespace comes from the annotation's defining context.
3. Search base and derived modules for same-named symbols, then test whether inherited deferred references resolve to the defining symbols.
4. Exercise inherited annotations with absent imports, shadowed names, generated initializers, and reused initializers across separate modules.
5. Verify annotation resolution for both the transformed class and its initializer.

## Evidence

- [#89737](../micro_taxo/gh_89737.md): The report shows that transformed derived classes inherited textual annotations from another module, while generated or reused initializers resolved them with unsuitable globals; missing or shadowing names caused failure or incorrect results.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0024](../macro_taxo_before_hybrid/workflow-0024.md)
