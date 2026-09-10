# Diagnostic decoding of malformed executable-object location metadata triggers an internal assertion

A low-level mechanism allows an executable object to carry malformed or inconsistent encoded source-location metadata. Later diagnostic or position-inspection code decodes that metadata as if its structural invariants were guaranteed, so malformed continuation bytes or truncated records drive an internal assertion and process termination.

## Precondition

An executable object is constructed or modified with location-mapping metadata that is truncated, structurally invalid, or inconsistent with the object’s instruction stream.

## Critical operation

A diagnostic, disassembly, or position-iteration operation parses the object’s encoded location metadata.

## Interference

The metadata contains an invalid continuation-byte pattern or is too short to describe the associated instructions.

## Invalid assumption

The decoder assumes the metadata was produced in a valid canonical format and relies on internal cursor, line-state, and continuation invariants without first validating malformed input as recoverable data.

## Failure

An internal assertion fires during decoding, aborting the process instead of returning an invalid-metadata error.

## Scope

All three reports involve deliberately corrupted low-level executable-object metadata and diagnostic decoding; they support a boundary around unsafe or insufficiently validated object construction, not a claim that ordinarily generated metadata is malformed.

## Search strategy

1. Inspect every diagnostic or iterator path that decodes compact metadata embedded in executable objects.
2. Check whether object-replacement or low-level construction APIs validate metadata length and encoding invariants against the instruction stream.
3. Search decoder loops for assertions on continuation bits, cursor bounds, or derived state that can be reached before input validation.
4. Verify malformed or truncated metadata tests expect a recoverable error rather than process termination.

## Evidence

- [#140935](../micro_taxo/gh_140935.md): Replacing an executable object’s location table with bytes containing an invalid continuation pattern causes disassembly to reach a decoder assertion and abort.
- [#142736](../micro_taxo/gh_142736.md): A one-byte location table attached to an executable object causes disassembly to violate decoder cursor and continuation invariants, confirming that malformed metadata is treated as trusted internal data.
- [#143430](../micro_taxo/gh_143430.md): A location table too short for the supplied instruction stream causes position iteration to trigger the same bounds and state assertion during metadata parsing.
