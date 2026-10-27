# Invalid lexer/tokenizer buffer offsets produce pointer-index overflow

Lexer/tokenizer buffer-position arithmetic can form invalid pointer offsets during stateful or continued input processing.

## Precondition

Valid input is processed through a lexer/tokenizer path that tracks positions across continuation, newline, or buffer-state transitions.

## Critical operation

Lexer/tokenizer code adds a calculated offset to a buffer base to obtain a character pointer or indexed position.

## Interference

Position handling supplies an invalid or overflowing offset to that pointer calculation.

## Invalid assumption

The calculated offset is representable and remains within the buffer's valid address range.

## Failure

Undefined-behavior instrumentation reports pointer-index overflow while processing input, but execution continues successfully.

## Scope

This singleton report supports a lexer/tokenizer buffer-offset pattern. Its reproductions differ in trigger context, so the evidence does not establish that all multiline input or all buffer transitions are affected.

## Search strategy

1. Inspect lexer and tokenizer pointer arithmetic fed by continuation, newline, or buffer-state variables.
2. Trace offset provenance across buffer transitions, including signed/unsigned conversions and sentinel values.
3. Check that derived buffer positions are range-validated before pointer arithmetic or indexing.
4. Exercise both interactive continued input and lexer-buffer test paths under undefined-behavior instrumentation.

## Evidence

- [#113720](../micro_taxo/gh_113720.md): The report shows pointer-index overflow during valid continued interactive input and later at lexer-buffer locations during a successful test run; both reproduce diagnostics without an interpreter crash.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0048](../macro_taxo_before_hybrid/workflow-0048.md)
