# Unbounded decoding of malformed variable-length metadata

A metadata iterator advances a raw cursor through encoded records without enforcing the buffer boundary for each byte or field it consumes.

## Precondition

An object carries truncated, malformed, or representation-incompatible encoded metadata that can be supplied to its iterator.

## Critical operation

The iterator decodes record fields and advances its cursor while deriving the next range or position.

## Interference

A zero-length record or an unterminated variable-length field prevents normal progress or termination, so decoding continues after the cursor reaches the metadata boundary.

## Invalid assumption

The decoder assumes each requested field is fully present and that iteration cannot require another record at end of input; any boundary assertion is not an effective runtime validation.

## Failure

The iterator accesses memory beyond the metadata buffer, disclosing adjacent data or causing memory corruption and a crash.

## Scope

The common mechanism is unchecked iteration over encoded location metadata. The reports demonstrate both fixed-width and variable-length record forms; they do not establish that all malformed object fields or all deserialization paths share this defect.

## Search strategy

1. Verify that every metadata-byte read checks the remaining buffer length before dereferencing.
2. Verify that every variable-length decode rejects input ending before its terminator.
3. Verify that zero-length records cannot cause an iterator to decode another record after reaching end of input.
4. Verify that release builds return a malformed-input error rather than relying on assertions for cursor bounds.

## Evidence

- [#99974](../micro_taxo/gh_99974.md): A truncated encoded location record caused unchecked variable-length field reads past the metadata buffer and exposed adjacent heap bytes; assertions would have detected the boundary violation.
- [#99975](../micro_taxo/gh_99975.md): A zero-length decoded range kept iteration active after the valid metadata bytes were consumed, causing a subsequent fixed-width record read beyond the buffer; the only guard was an assertion.
- [#121112](../micro_taxo/gh_121112.md): Malformed or foreign serialized objects led to memory corruption and crashes during metadata iteration; the report identifies the shared location reader as not bounds-checked and reproduces it with unterminated encoded metadata.
