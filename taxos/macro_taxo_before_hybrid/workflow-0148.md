# Unvalidated mutation of an executable instruction stream exposes a metadata-only placeholder to instruction dispatch.

A caller rewrites a low-level executable stream by inserting a reserved non-instruction marker at its entry without preserving the stream’s structural invariants, and the runtime aborts when dispatch treats that marker as executable.

## Precondition

A caller can construct or mutate an executable instruction stream directly, including representations that contain reserved metadata or placeholder entries.

## Critical operation

The caller prepends such a reserved placeholder to the stream, shifting the original instructions without correspondingly updating execution boundaries or related layout metadata.

## Interference

The inserted placeholder becomes the first element seen by normal dispatch, while the stream still presents the original execution entry and structure.

## Invalid assumption

The runtime assumes that every element reachable from the execution entry is a valid executable instruction and does not validate or reject caller-produced malformed streams before dispatch.

## Failure

Dispatch encounters the reserved placeholder as an instruction, violates an internal execution invariant, and terminates fatally instead of returning a malformed-input error.

## Scope

This is a singleton cluster, so the pattern is cautiously scoped to runtimes that expose or tolerate direct mutation/construction of encoded instruction streams containing non-executable reserved entries. It does not establish that well-formed streams or supported transformation APIs are vulnerable.

## Search strategy

1. Inspect code that directly edits serialized or encoded instruction streams and verify that instruction offsets, boundaries, and auxiliary metadata are updated together.
2. Search for reserved metadata markers or placeholder encodings that can become reachable from an execution entry.
3. Check whether externally constructed executable streams are validated before the dispatcher interprets their first element.
4. Review fatal invariant checks in dispatch paths and determine whether malformed stream input is rejected before those checks are reached.

## Evidence

- [#144282](../micro_taxo/gh_144282.md): The report demonstrates that manually prefixing an encoded executable stream with a reserved cache-like placeholder shifts the original instructions; execution starts at the prefix, treats it as an instruction, and aborts on an internal invariant. The comments explicitly characterize the input as malformed and outside the runtime’s supported threat
