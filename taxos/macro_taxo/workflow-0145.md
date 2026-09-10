# A foreign-function pointer descriptor lacks resolved target-type metadata; argument conversion consults that metadata to classify the supplied value; an absent/

A foreign-function pointer descriptor lacks resolved target-type metadata; argument conversion consults that metadata to classify the supplied value; an absent or null prototype reaches an internal non-null invariant instead of normal validation, causing an assertion abort rather than a recoverable argument-conversion error.

## Precondition

A pointer descriptor is accepted as an argument type even though its pointed-to type metadata or runtime prototype has not been resolved or initialized.

## Critical operation

Argument conversion uses the descriptor's target-type metadata to determine whether the supplied value is an instance of the expected pointed-to type and whether it can be adapted by reference.

## Interference

The unresolved descriptor propagates into conversion without an earlier validity check, leaving the expected prototype metadata null.

## Invalid assumption

The conversion path assumes every accepted pointer descriptor has non-null, fully resolved target-type metadata.

## Failure

The null metadata violates an internal assertion and aborts the interpreter, rather than producing a normal type or argument-conversion exception.

## Scope

This is a cautiously scoped singleton pattern supported by one report: pointer argument conversion in a foreign-function interface with unresolved target metadata. It does not establish that all deferred type-resolution mechanisms or all assertion failures share this cause.

## Search strategy

1. Trace every pointer-argument conversion path for null or unresolved target-type metadata before instance checks.
2. Find internal assertions that enforce descriptor invariants after descriptors have already crossed public argument-type validation.
3. Check whether malformed or incomplete descriptors produce recoverable exceptions instead of process-aborting assertions.
4. Review descriptor-construction and deferred-resolution paths for types that can be registered as argument types before their target metadata is initialized.

## Evidence

- [#144100](../micro_taxo/gh_144100.md): The report demonstrates that an incomplete pointer descriptor with missing target-type metadata reaches argument conversion, where a null prototype is asserted and the process aborts; the corrective behavior is to return a type error instead.
