# Unchecked size, width, and position metadata drives native writes beyond allocated storage

Native or low-level code performs a memory write after trusting caller-controlled, callback-controlled, or derived metadata that may not match the destination’s actual capacity or layout. The cluster includes native-width parser stores, operation-specific output buffers, underestimating size hints, invalid formatter suffix assumptions, and boundary-selected execution layouts.

## Precondition

A low-level routine receives a destination, buffer, output representation, size estimate, native-width type, or execution position whose actual storage requirements can differ from the metadata accepted by the routine.

## Critical operation

The routine computes a destination offset, storage layout, or write width from that metadata and performs the native write or in-place mutation before establishing that the selected storage is valid and sufficiently large.

## Interference

The metadata underestimates required capacity, uses an incompatible native width, selects an invalid boundary, or describes output that is empty or lacks an assumed suffix; validation is absent, too permissive, or occurs only after the write.

## Invalid assumption

The code assumes that an accepted size hint, format-compatible value, caller-provided buffer, formatter result, or execution position accurately describes a writable layout and satisfies the downstream operation’s exact requirements.

## Failure

The write exceeds stack, heap, global, or object storage, or initializes an undersized internal layout, causing memory corruption, sanitizer-detected overflow, assertion or process termination, or a fatal low-level error instead of a recoverable argument or state-validation failure.

## Scope

The six reports involve metadata that does not match storage capacity or layout: native-width mismatches, invalid execution positions, undersized output buffers, underestimated producer sizes, and formatter suffix assumptions. They do not establish one buffer API or that every member causes actual memory damage.

## Search strategy

1. Compare every native format unit or write width with the exact destination object type and size, especially where fixed-width objects receive native-width stores.
2. Require each operation-specific native output size to be validated before invoking the operation with caller-supplied or temporary storage; do not rely solely on post-call guard detection.
3. Treat iterator or producer size estimates as advisory, and verify capacity or grow storage before writing the first yielded element, including zero-capacity and shared-empty paths.
4. Check formatter and callback output before indexing length-minus-one or removing assumed suffixes; validate both nonempty length and the actual trailing byte or code unit.
5. Trace externally set execution positions through validation, instruction mapping, allocation, and initialization, and reject boundary values that do not correspond to a fully allocated layout.

## Evidence

- [#89391](../micro_taxo/gh_89391.md): A format-driven parser stored values using native integer widths into narrower fixed-width destinations, so the parser’s accepted format did not guarantee that the destination object could hold the write.
- [#140802](../micro_taxo/gh_140802.md): An externally modified execution position at a lower boundary was accepted and later selected an execution-record initialization layout smaller than the fields written during resume.
- [#141338](../micro_taxo/gh_141338.md): A caller supplied an empty buffer for a native operation requiring an operation-specific structure, and the wrapper detected the resulting overflow only through a fatal buffer-overflow error.
- [#143003](../micro_taxo/gh_143003.md): A zero-valued iterator length hint caused shared zero-capacity storage to be retained while the consumer wrote yielded elements before ensuring capacity, corrupting the shared buffer.
- [#143377](../micro_taxo/gh_143377.md): Formatter output was assumed to be nonempty and newline-terminated; empty output made the final-position write occur outside the allocated string buffer, while unterminated output also invalidated the cleanup assumption.
- [#144206](../micro_taxo/gh_144206.md): A mutable empty buffer was passed to a native operation requiring a fixed-size result; without operation-code-specific capacity knowledge, the wrapper could only detect the possible overwrite after invocation and reported a fatal system error.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0022](../macro_taxo_before_hybrid/workflow-0022.md)
- [workflow-0114](../macro_taxo_before_hybrid/workflow-0114.md)
- [workflow-0122](../macro_taxo_before_hybrid/workflow-0122.md)
- [workflow-0135](../macro_taxo_before_hybrid/workflow-0135.md)
- [workflow-0138](../macro_taxo_before_hybrid/workflow-0138.md)
