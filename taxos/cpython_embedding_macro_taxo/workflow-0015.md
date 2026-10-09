# Unchecked raw-byte reinterpretation as a native logical value

Raw storage is treated as a native logical scalar even though that type permits only canonical object representations; portable nonzero-is-true semantics are thereby conflated with native representation semantics.

## Precondition

A byte-oriented unpacking or view-cast operation accepts storage that may contain arbitrary byte values and exposes it as a logical value.

## Critical operation

The operation copies or reinterprets the raw storage as a native logical object, then reads that object without first converting, validating, or canonicalizing the value.

## Interference

The input storage contains a noncanonical nonzero bit pattern that is not a valid representation of the native logical type.

## Invalid assumption

Every nonzero byte is a valid native true representation, so a raw logical-object read preserves portable nonzero-is-true behavior.

## Failure

Reading the invalid logical representation has undefined behavior, producing a sanitizer diagnostic or a platform-dependent incorrect logical result.

## Scope

Singleton cluster. This pattern is scoped to native logical/boolean representations with restricted valid encodings; the report does not establish that every raw scalar reinterpretation has the same failure mode.

## Search strategy

1. Find byte-unpacking and buffer-view paths that copy or reinterpret raw storage directly as native logical objects.
2. Verify that fixed or portable logical formats do not substitute a native logical-type handler solely because their sizes match.
3. Trace casts from arbitrary byte or integer elements to logical views and require canonicalization, validation, or an explicitly representation-dependent contract.
4. Exercise logical unpacking and casts with nonzero values other than the canonical true encoding under undefined-behavior sanitizers.
5. Review generated conversion tests to ensure they do not create noncanonical native logical representations before reading them.

## Evidence

- [#83870](../micro_taxo/gh_83870.md): A raw byte buffer was copied into and read as a native logical object; noncanonical nonzero bytes triggered undefined-behavior diagnostics and, on one platform, evaluated as false. The report also shows that selecting native handling for a fixed-size logical format incorrectly imported representation-dependent behavior, while casts of arbitrary raw
