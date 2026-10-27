# Externally controlled execution-position updates accept the exact lower boundary of a resumable function, allowing resume-time state initialization to treat a “

A singleton pattern in which a tracing/debugging control changes a resumable function’s source position to its first source boundary, validation accidentally accepts that boundary, and resumption enters layout-sensitive state initialization.

## Precondition

A tracing, debugging, or equivalent control path can assign a resumable function’s execution position, and the position validator rejects only values strictly before the function’s first source position.

## Critical operation

The control path sets the execution position to exactly the first source position and then resumes execution, causing the runtime to derive and initialize an execution-record layout from that position.

## Interference

A strict-less-than boundary check admits the exact lower-bound value even though it is not a valid resumable instruction location.

## Invalid assumption

The resume path assumes every position accepted by validation denotes a normal instruction location whose derived execution state fits the already allocated heap object.

## Failure

State initialization writes beyond the heap object allocated for the smaller layout, producing a heap-buffer-overflow instead of returning a recoverable invalid-position error.

## Scope

This cluster contains one report, so the pattern is scoped to runtimes with externally mutable execution positions and resumable execution records; it does not establish that all tracing or debugging position changes have this failure mode.

## Search strategy

1. Inspect every externally writable instruction or source-position setter for an explicit equality check at the first valid boundary.
2. Compare position-validation predicates with the downstream source-position-to-instruction and execution-layout mappings, looking for strict-versus-inclusive bound mismatches.
3. Trace accepted boundary positions through resume and state-initialization paths, and verify that allocation sizes are computed from the same layout metadata used by the writes.
4. Add boundary-focused tests that assign positions immediately before, exactly at, and immediately after the first source position, including resumable and suspended executions.

## Evidence

- [#140802](../micro_taxo/gh_140802.md): The report shows a tracing callback assigning the first source line, a strict lower-bound check accepting it, resume-time frame initialization using the invalid position, and an AddressSanitizer heap write immediately past a smaller heap allocation.
