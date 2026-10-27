# I’m reading the full report first, then I’ll distill only the shared causal mechanism into the required JSON.

A generalized taxonomy entry for a workflow cluster.

## Precondition

A byte-oriented interface accepts externally supplied or otherwise arbitrary bytes for a logical scalar whose in-memory representation permits only a restricted set of valid encodings.

## Critical operation

The implementation copies the bytes directly into an object of the logical scalar type, or otherwise reinterprets them as that type, without validating or normalizing the representation.

## Interference

A noncanonical byte pattern enters the scalar object through the raw-byte path, bypassing the type’s ordinary value conversion, which would have produced a canonical encoding.

## Invalid assumption

Later code assumes that every object of the scalar type contains a valid representation and treats the copied bytes as an ordinary value.

## Failure

Reading or operating on the object invokes undefined behavior or sanitizer diagnostics and can produce platform-, compiler-, or architecture-dependent results, including an incorrect logical value.

## Scope

This is a cautiously scoped singleton pattern. The evidence specifically concerns native logical scalar representations and raw buffer conversion; it does not establish that every noncanonical byte conversion has the same semantics or failure mode.

## Search strategy

1. Search for memcpy, byte casts, or buffer-to-scalar reads involving representation-constrained logical or enum-like types; verify that inputs are validated or normalized first.
2. Inspect deserialization, unpacking, and buffer-casting paths that construct typed objects directly from arbitrary bytes; check whether noncanonical encodings are rejected.
3. Trace every later read of objects populated from raw bytes; confirm the code cannot observe invalid or trap representations before canonicalization.
4. Compare native-layout and portable-layout conversion paths; verify that implementation-table substitutions do not route portable bytes into native type semantics.],
5. evidence2? no
6. scope_note2? no

## Evidence

- [#83870](../micro_taxo/gh_83870.md): The report documents byte unpacking and buffer casting into a native logical type via direct memory copying. Inputs such as arbitrary nonzero bytes were not canonical valid encodings; subsequent reads triggered undefined-behavior sanitizer diagnostics or produced different boolean results across compilers and architectures. It also records that the
