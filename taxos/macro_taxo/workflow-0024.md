# When a class transformation generates or reuses an initializer for a derived class in another module, inherited deferred annotation strings retain references to

Cross-module annotation provenance is lost when transformed class metadata or generated callables carry inherited string annotations without preserving the namespace where those annotations were defined.

## Precondition

A base class has deferred textual annotations, and a class-generation or transformation step processes a derived class in a different module while inheriting those fields or generating a new initializer.

## Critical operation

The transformation copies the inherited annotation strings into generated field metadata or callable annotations and associates them with the derived class or generator namespace.

## Interference

Later annotation resolution evaluates those strings in the derived or generated callable's namespace, where names from the defining module may be absent or may resolve to same-named objects from the derived module.

## Invalid assumption

Annotation text can be resolved correctly from the namespace available during derived-class transformation, without preserving the defining module's namespace or converting the reference into a namespace-aware deferred-reference object.

## Failure

Resolving class or initializer annotations fails, or silently reconstructs inherited annotations as incorrect types.

## Scope

This is a singleton pattern, so it is scoped to class-generation or transformation workflows that propagate deferred annotations across module boundaries; it does not claim that all annotation-resolution failures have this cause.

## Search strategy

1. Trace every transformation that copies deferred annotation strings across class or module boundaries, and verify that definition-time namespace provenance is preserved.
2. Inspect generated callable metadata and confirm its annotation-resolution namespace comes from the annotation's defining context rather than the derived class or generator.
3. Search for same-named symbols in base and derived modules and test whether deferred references resolve to the defining symbol.
4. Exercise inherited annotations with absent imports, shadowed names, and generated initializers across separate modules.
5. Verify annotation resolution for both the transformed class and its generated or inherited initializer.

## Evidence

- [#89737](../micro_taxo/gh_89737.md): The report demonstrates that generated initializers for derived transformed classes inherited textual annotations from another module; resolving class and initializer hints failed or could select a shadowing same-named type until the defining module context was preserved.
