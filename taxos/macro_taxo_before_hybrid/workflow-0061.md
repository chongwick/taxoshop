# Unvalidated extreme geometry arguments cross an interface into a lower-level component whose internal representation or arithmetic cannot safely handle them.

A wrapper forwards caller-controlled dimensions or coordinates without enforcing the downstream component’s actual safe range, allowing overflow or invalid memory access instead of a controlled range error.

## Precondition

A caller can provide an unusually large geometry value that is representable by the wrapper’s input type but outside the lower-level component’s safe operational range.

## Critical operation

The interface passes that value into a lower-level resize, window, layout, or allocation operation that performs narrower conversion, arithmetic, indexing, or memory computation.

## Interference

The interface omits validation or normalization against the downstream component’s effective range and relies on the dependency to reject the value safely.

## Invalid assumption

Because the value is accepted or representable at the wrapper boundary, it is assumed to remain valid for all downstream representations and calculations.

## Failure

The lower-level component overflows or computes invalid state or addresses, causing a segmentation fault or later crash rather than returning a range or argument error.

## Scope

The shared pattern is unsafe forwarding of extreme geometry values across an interface. One report involves narrower dimension conversion and a later refresh crash; the other involves an extreme coordinate and an immediate lower-level memory fault. The reports do not establish that every instance requires a later refresh or that the wrapper alone can determine all valid limits.

## Search strategy

1. Check every wrapper that forwards dimensions, coordinates, lengths, or counts to a lower-level library for explicit validation against the callee’s documented and implementation-level limits.
2. Search for conversions from wider integers to narrower signed types before calls that allocate, resize, index, or compute offsets.
3. Trace extreme-value handling through downstream arithmetic and verify that overflow, invalid allocation sizes, and out-of-bounds geometry produce controlled errors.
4. Review whether a successful boundary conversion is incorrectly treated as evidence that the dependency can safely process the value.

## Evidence

- [#120378](../micro_taxo/gh_120378.md): Oversized resize dimensions were accepted as general integers even though the downstream terminal library used narrower signed dimensions; internal overflow corrupted state and a subsequent screen operation crashed, motivating explicit range rejection.
- [#140462](../micro_taxo/gh_140462.md): An extreme window coordinate was forwarded unchanged to the lower-level window library; the library failed to reject it before internal geometry processing and dereferenced an invalid address, producing a segmentation fault.
