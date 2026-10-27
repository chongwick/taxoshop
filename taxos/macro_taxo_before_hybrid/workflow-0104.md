# Unchecked or externally mutable runtime metadata violates a representation invariant, allowing later low-level consumers to crash when they use the value as its

A structured runtime state or metadata field is accepted or modified without enforcing its required representation. Later execution uses that field through an operation that assumes the invariant, so an incompatible value reaches low-level object or memory handling and crashes instead of producing a recoverable validation error.

## Precondition

Runtime state or metadata contains fields with required representation invariants, and callers can supply or mutate those fields without complete validation.

## Critical operation

A later execution path consumes the field using a specialized operation that requires the expected representation, such as mapping access or object-reference handling.

## Interference

Validation is incomplete, or the supportedness boundary permits direct mutation that bypasses invariant-preserving construction.

## Invalid assumption

The downstream consumer assumes the field still has its required representation because the earlier state-construction or mutation path did not establish that invariant.

## Failure

The incompatible value is processed by low-level runtime code, causing invalid object or memory access and a process crash rather than a recoverable type or state error.

## Scope

The reports share the invariant-bypass-to-low-level-crash mechanism, but differ in boundary: one is a missing validation check in a state-restoration path, while the other is unsupported direct mutation of runtime metadata. The pattern therefore covers both incomplete validation and explicitly unsupported invariant-breaking mutation, not all malformed input generally.

## Search strategy

1. Check every state-restoration or deserialization field for validation of optional values before storing them.
2. Trace metadata fields from mutation or replacement APIs to consumers and verify that each consumer's representation assumptions are enforced.
3. Search for low-level lookups, reference operations, or pointer-dependent access performed without a local type or invariant check.
4. Check whether public mutation APIs can create internally inconsistent structured objects that later execution treats as trusted state.

## Evidence

- [#140590](../micro_taxo/gh_140590.md): A missing check on an optional mapping-valued state field allowed a non-mapping value to be stored; later mapping-oriented processing could reach invalid low-level access and crash.
- [#140776](../micro_taxo/gh_140776.md): Direct replacement of a code object's metadata with a value of the wrong representation broke an internal invariant; later function construction treated the metadata as valid and crashed during low-level object handling.
