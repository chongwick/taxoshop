# End-of-instruction-stream cursor decoded as an instruction

An instruction-processing consumer dereferences or decodes at the logical end of an instruction buffer without first proving that a complete instruction remains.

## Precondition

An optimizer or executor reaches an instruction-stream cursor equal to the stream length, either after a terminal instruction or for an empty stream.

## Critical operation

The consumer fetches or decodes an instruction at that cursor.

## Interference

An end-of-stream position is passed into the instruction-decoding path.

## Invalid assumption

A cursor at the logical endpoint identifies readable instruction storage.

## Failure

The consumer reads beyond the instruction buffer and can abort or crash.

## Scope

The reports cover distinct ways an endpoint cursor arises—normal optimization of a terminal stream and execution of a malformed empty stream. The shared pattern is the unchecked consumer-side decode at that endpoint, not a claim that all malformed streams are accepted by all construction paths.

## Search strategy

1. Audit every instruction fetch or decode to require that the cursor and full instruction width are within the buffer before dereference.
2. Trace optimizer scan cursors and control-flow targets to ensure an endpoint cursor is not passed to an instruction decoder.
3. Test instruction processing when a terminal instruction is the final entry and when the instruction stream is empty, using memory sanitizers.
4. Validate externally constructible or mutable executable objects before execution so an empty or undersized instruction stream is rejected or safely handled.

## Evidence

- [#79374](../micro_taxo/gh_79374.md): An optimization scan passed an index equal to the instruction-buffer length into a helper that dereferenced it before checking the bound, producing an out-of-bounds read after a terminal instruction.
- [#140497](../micro_taxo/gh_140497.md): Executing an executable object whose instruction sequence had been replaced with an empty buffer caused the evaluator to read a fixed-width instruction immediately past the allocation boundary.
