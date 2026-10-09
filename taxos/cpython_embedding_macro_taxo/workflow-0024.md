# Deferred inherited annotations lose their defining-module context when a subclass generator emits a new callable in a different module.

Preserve declaration context for deferred annotations copied from inherited metadata into generated callables, so later resolution remains bound to the namespace in which each annotation was written.

## Precondition

A generated class inherits fields or callable parameters whose annotations are stored as deferred strings and whose defining module differs from the module generating the derived class.

## Critical operation

The generation step constructs a new initializer-like callable using the inherited fields and carries their deferred annotation text into that callable.

## Interference

The generated callable is associated with the derived class's globals, which may omit names from the defining module or bind the same names differently.

## Invalid assumption

The generator assumes a raw deferred annotation can be evaluated correctly in the generated callable's namespace, or that combining available base namespaces can reconstruct its original meaning.

## Failure

Later annotation resolution raises an unresolved-name error or resolves an inherited annotation to a shadowing type rather than its original type.

## Scope

Singleton cluster. The evidence specifically concerns generated initializer annotations inherited across modules; it supports preserving provenance for deferred inherited annotations, not a general rule for all reflective metadata.

## Search strategy

1. Inspect generated callables that copy string annotations from inherited fields or parameters.
2. Trace which global namespace each deferred annotation uses when an inherited member is emitted into generated code.
3. Test derived classes defined in a different module where the inherited annotation's name is absent locally.
4. Test derived classes whose module defines a same-named, incompatible symbol and verify inherited annotations retain their original binding.
5. Require deferred annotation representations to retain per-annotation declaration-module context rather than relying on a merged namespace.

## Evidence

- [#89737](../micro_taxo/gh_89737.md): A cross-module inheritance case showed generated initializer annotations failing when a referenced name was unavailable in the generated callable's module; a same-name override case also demonstrated that aggregating namespaces can bind inherited annotation text to the wrong type. The proposed remedy attached the defining module to deferred-annotat
