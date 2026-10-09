# Type-erased heterogeneous parser sequence is treated as a homogeneous expression sequence when deriving result metadata.

A parser helper consumes a generic sequence whose elements may be wrapper records around different payload kinds, then derives source-location metadata for a constructed result from an endpoint element.

## Precondition

An optional parser-produced sequence contains wrapper records whose payload may be either an expression or a non-expression record.

## Critical operation

The helper selects an endpoint from that sequence and reads expression-specific location fields to populate the constructed result's metadata.

## Interference

The selected endpoint remains a wrapper record, and even its contained payload can be non-expression, so its memory layout does not provide the expected expression fields.

## Invalid assumption

The helper assumes that an element obtained from the generic sequence can be interpreted as an expression solely because it occurs in argument collection.

## Failure

The invalid interpretation reads beyond the actual heap object; address sanitization terminates the process with a heap-buffer-overflow (while non-sanitized builds may mask the bad metadata read).

## Scope

Singleton cluster: this pattern is scoped to type-erased parser sequences and endpoint metadata extraction; the report does not establish that all iterative parser refactors or all heterogeneous collections share this failure mode.

## Search strategy

1. Trace the concrete element type of every generic parser sequence across helper boundaries before casting or field access.
2. Inspect first- and last-element metadata derivations and verify that each endpoint has the record type whose fields are read.
3. Require variant discrimination before extracting a wrapper payload, and handle every payload kind before using type-specific metadata.
4. Review parser collection refactors for inherited endpoint or source-span logic that assumes a homogeneous sequence.
5. Run sanitizer-enabled parsing tests that exercise mixed positional, expanded, and named argument forms.

## Evidence

- [#85863](../micro_taxo/gh_85863.md): A parser argument-collection helper selected a wrapper-record endpoint from a generic sequence as though it were an expression to derive location metadata. The wrapper could contain a keyword rather than an expression, causing an out-of-bounds heap read detected by AddressSanitizer; the fix supplied location metadata separately rather than infering
