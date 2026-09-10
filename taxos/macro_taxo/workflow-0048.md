# A tokenizer or lexer processes input across a continued or otherwise stateful buffer-processing path.

A tokenizer or lexer processes input across a continued or otherwise stateful buffer-processing path.

## Precondition

The parser accepts input whose tokenization spans a newline, continuation, or related buffer/state transition.

## Critical operation

Tokenizer code derives a character pointer or buffer index from the current buffer base and a calculated offset.

## Interference

The state transition produces an invalid, negative, or otherwise corrupted offset used in that pointer/index calculation.

## Invalid assumption

The calculated offset is representable and remains within the tokenizer buffer's valid address range.

## Failure

Undefined-behavior instrumentation reports pointer-index arithmetic overflow during valid input processing, while the runtime continues rather than crashing.

## Scope

This is a singleton issue report with multiple reproductions. The evidence supports a tokenizer/lexer buffer-position arithmetic defect, especially on continued or stateful input paths; it does not establish that every multiline construct or every implementation has this behavior.

## Search strategy

1. Inspect lexer and tokenizer code for pointer arithmetic using offsets derived from continued-input or newline state.
2. Trace every offset used to index tokenizer buffers across input-boundary and state-transition paths.
3. Check signed/unsigned conversions and sentinel values that can turn a buffer position into an invalid large offset.
4. Verify that buffer-position calculations are range-checked before pointer arithmetic.

## Evidence

- [#113720](../micro_taxo/gh_113720.md): The report demonstrates pointer-index overflow in tokenizer processing for continued input involving an opening delimiter, an explicit line continuation, a newline, and a following expression; a later reproduction shows the same class of diagnostic in lexer-buffer code during a successful test run, supporting a narrowly scoped tokenizer buffer-arit
