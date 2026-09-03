# Macro Taxonomy: JIT And Execution-State Invalidation

## Pattern
The interpreter, optimizer, and JIT exchange assumptions about bytecode,
frame layout, trace state, callable identity, and stack values. A mutation,
trace hook, deoptimization edge, or initialization failure makes one layer's
cached representation invalid while another continues executing it.

## Common State At Risk
- Uop traces, executor entries, and optimizer metadata.
- Frame instruction pointers and evaluation stacks.
- Callable/type feedback and lazy JIT trampolines.
- Tracing state initialized during thread or interpreter lifecycle changes.

## Failure Shapes
- Optimizer or interpreter assertions.
- Segfault in generated cases or JIT trampoline.
- Stale executable state after tracing or code-object mutation.
- JIT initialization leak.

## Defensive Rule
Make invalidation explicit at each transition between interpreter and optimized
code. Verify trace/debug state before using cached feedback, and make
deoptimization restore a frame and stack representation that the interpreter
can validate.

## Representative Micro-taxonomies
- [#148716](../micro_taxo/gh_148716.md): tracing state changes before a JIT
  threshold transition.
- [#144280](../micro_taxo/gh_144280.md): symbolic truthiness crash in the uop
  optimizer.
- [#141621](../micro_taxo/gh_141621.md): UBSan JIT trampoline failure.
- [#139834](../micro_taxo/gh_139834.md): lazy JIT trampoline crash under
  ASan/UBSan.
- [#141542](../micro_taxo/gh_141542.md): JIT tracing initialization leak.

## Membership Rule
Group micro-taxonomies whose title, component, or evidence names JIT, uops,
optimizer, executor, trampoline, deoptimization, or generated frame execution.
