# Incomplete rebasing of retained pointers when replacing a parser input buffer

A stateful parser retains direct pointers into a mutable input buffer across a stack of parsing modes. Buffer growth or replacement must preserve every live intra-buffer reference independently of the mode's current classification.

## Precondition

Parsing an unfinished, potentially nested construct leaves one or more active state records holding pointers into the current input buffer; such records may have changed mode while still retaining those pointers.

## Critical operation

The parser grows, reallocates, or replaces the input buffer, invalidating the old allocation.

## Interference

The relocation protocol snapshots and restores only records selected by their current mode, or is omitted on a buffer-replacement path, so a pointer-bearing record is skipped.

## Invalid assumption

Current mode classification reliably identifies every state record that owns a pointer into the buffer, and all input-buffer transitions preserve such references.

## Failure

Later parsing or diagnostic construction dereferences an unrebased pointer into freed storage, causing a heap use-after-free and process termination.

## Scope

Singleton cluster. The evidence establishes this pattern for a parser mode stack and input-buffer transitions; it does not establish that unrelated pointer caches follow the same failure mode.

## Search strategy

1. Find every input-buffer reallocation, free, and replacement; require all live intra-buffer pointers to be converted to offsets before invalidation and rebuilt afterward.
2. Audit every parser-state stack record for fields that point into the input buffer, regardless of its current mode tag.
3. Verify that every buffer-transition branch uses the same snapshot-and-restore protocol, including direct replacement paths.
4. Exercise unterminated nested and multiline constructs whose active state changes mode before buffer growth or replacement, then trigger error reporting.

## Evidence

- [#103718](../micro_taxo/gh_103718.md): An unfinished interpolated construct retained input-buffer pointers across nested modes; both reallocation and direct replacement left pointers stale when updates were selectively applied or skipped, and later syntax-error handling read freed memory.
