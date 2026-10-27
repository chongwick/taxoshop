# Incremental byte-reader boundary checks use a string-derived offset that can remain zero after embedded-NUL input

An incremental byte reader derives its progress offset from NUL-terminated string length, then examines the preceding buffer element to detect a record delimiter. When embedded NUL data makes the derived length zero, the preceding-element access becomes invalid and subsequent reads may reuse the same write position.

## Precondition

A buffered reader accepts byte input that may contain an embedded NUL before the expected record delimiter and tracks the amount of valid data using NUL-terminated string length.

## Critical operation

The reader evaluates a preceding buffer element, equivalent to buffer[offset - 1], as part of deciding whether to continue reading.

## Interference

The length operation stops at the embedded NUL, so the computed offset can be zero or shorter than the bytes physically read; the offset then fails to advance despite additional buffered input.

## Invalid assumption

The code assumes the offset is positive whenever the preceding-element check executes and that a string-derived length accounts for every byte obtained by the read.

## Failure

The preceding-element access reads outside the valid buffer range, producing undefined behavior. If execution continues undetected, the unchanged offset can cause a later read to overwrite earlier input, resulting in lost or incorrectly processed data.

## Scope

This is a cautiously scoped singleton pattern supported by one report. It applies to incremental byte readers that combine NUL-terminated length accounting with unguarded preceding-element checks; it does not establish a general policy for truncating or preserving embedded-NUL data, only the boundary-safety requirement and the resulting overwrite risk.

## Search strategy

1. Search incremental buffered readers for preceding-element expressions such as buffer[length - 1] without an explicit positive-length guard.
2. Check whether NUL-terminated string-length functions measure data returned by byte-oriented reads that can contain embedded NUL values.
3. Trace the write offset after an input chunk begins with or contains NUL and verify that every subsequent read advances within the valid buffer.
4. Verify that delimiter checks are performed only after establishing that the computed length is nonzero.
5. Add tests with leading and embedded NUL bytes followed by additional records or delimiters, checking both memory safety and preservation of later input.

## Evidence

- [#140594](../micro_taxo/gh_140594.md): The report shows that embedded NUL input makes string-length accounting return zero, after which the reader accesses the buffer at offset minus one. It also demonstrates that the undefined read can be detected directly or can leave the offset unchanged so a later read overwrites previously read bytes and changes which data is processed.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0105](../macro_taxo_before_hybrid/workflow-0105.md)
