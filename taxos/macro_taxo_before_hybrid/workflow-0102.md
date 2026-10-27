# Malformed cloned executable metadata bypasses safe rejection and reaches invariant-dependent internal validation or execution

A low-level executable object is reconstructed with metadata or instruction structure inconsistent with its stored layout, allowing internal invariant failures to surface as fatal errors.

## Precondition

A caller can clone or reconstruct an executable object while supplying independently editable metadata or instruction fields.

## Critical operation

The replacement object is created and then accepted for validation or execution using those altered fields.

## Interference

The supplied counts, variable descriptors, captured-variable metadata, or instruction stream no longer agree with the object’s remaining layout.

## Invalid assumption

Internal validation or execution assumes that reconstructed executable objects already satisfy cross-field construction invariants and does not safely reject every inconsistent combination.

## Failure

The malformed object triggers an internal system error or assertion failure instead of a recoverable invalid-object error.

## Scope

Both reports concern deliberately tampered low-level executable objects outside ordinary construction paths; they support the shared invariant-breach pattern, not a general claim about normally created executable objects.

## Search strategy

1. Check clone or reconstruction APIs that accept independently editable executable metadata fields.
2. Check whether parameter, variable, capture, and instruction counts are cross-validated against stored layouts before acceptance.
3. Check execution paths for assertions or unchecked assumptions about metadata matching instruction operands and associated descriptors.
4. Check malformed executable-object handling to confirm inconsistent combinations become recoverable errors rather than process-level failures.

## Evidence

- [#140564](../micro_taxo/gh_140564.md): Changing positional and keyword-only parameter counts on a cloned executable object to mutually inconsistent values caused internal validation to report an internal error.
- [#141390](../micro_taxo/gh_141390.md): Adding captured-variable metadata and a matching-looking instruction prefix without preserving the evaluator’s required metadata/instruction invariant caused an execution-time assertion failure.
