# Bounded instruction-stream consumers dereference an instruction after reaching the stream boundary because end-of-sequence validation is missing or bypassed.

A component processes an instruction buffer whose valid range may end immediately after a terminating instruction or may be empty after transformation. It advances or dispatches at the boundary without proving that a valid instruction remains.

## Precondition

The instruction buffer can be empty, malformed, or have a cursor/target equal to its length, including when a terminator is the final valid instruction.

## Critical operation

A scanner, target resolver, or execution dispatcher reads the instruction at the current or advanced cursor.

## Interference

Boundary conditions leave no valid instruction for that read, but control flow still invokes the read or dereferences the returned boundary position.

## Invalid assumption

Every cursor or resolved target supplied to the instruction consumer identifies an existing instruction, so an end position does not require a separate validity check.

## Failure

The consumer performs an out-of-bounds read, producing a memory-safety violation and potentially aborting or crashing the process.

## Scope

The reports differ in phase: one concerns optimization-time scanning after unreachable code, while the other concerns execution of an empty instruction buffer. The shared pattern is boundary dereference without validating that a current instruction exists; it does not require unreachable-code removal specifically.

## Search strategy

1. Check every instruction-scanning loop for a bounds check before reading the current element.
2. Check helpers that skip prefixes, extensions, or unreachable instructions for the case where advancement reaches exactly the sequence length.
3. Check every resolved branch target and dispatch cursor for validation against the instruction-buffer length before dereferencing.
4. Check code paths that accept, construct, or transform instruction buffers for empty or structurally incomplete sequences.

## Evidence

- [#79374](../micro_taxo/gh_79374.md): An optimization scan reached exactly the end of its bounded instruction array after a terminating operation, and its opcode-search helper read at that boundary; the fix added an explicit length check.
- [#140497](../micro_taxo/gh_140497.md): Execution of a deliberately empty instruction buffer caused the dispatcher to read beyond the allocated buffer, demonstrating the same missing validation when no instruction exists at the current position.
