# Lazy frame-stack allocation performs pointer arithmetic before establishing that the stack base exists.

Unchecked pointer arithmetic in a lazy stack/frame allocator

## Precondition

An execution context begins evaluation with no allocated frame-stack storage, so its stack-base and limit pointers are null.

## Critical operation

The allocation fast path derives an end pointer by adding the requested frame size to the base pointer, then uses that result in a capacity comparison that is meant to select allocation.

## Interference

Adding a nonzero offset to a null pointer is undefined behavior; sanitizers can diagnose it and optimizing compilers may reason from the impossible condition.

## Invalid assumption

The capacity comparison can safely detect an unallocated stack after computing from a null base pointer.

## Failure

Ordinary first-frame execution triggers undefined-behavior diagnostics or an assertion/process abort instead of allocating backing storage and continuing.

## Scope

Singleton cluster: this pattern is limited to lazily allocated execution/frame stacks whose unallocated representation uses null pointers; the report does not establish a broader rule for all null-pointer uses.

## Search strategy

1. Find lazy allocation paths that compute an address or offset from a possibly null storage base before testing whether storage exists.
2. Audit capacity checks that compare pointers or derive pointer differences when both endpoints can represent an unallocated state.
3. Require a null/allocation-state guard before every pointer addition, subtraction, or relational comparison on resumable execution-stack state.
4. Trace context-switch and restore paths to verify that an unallocated stack state cannot reach unchecked frame-push fast paths.
5. Build with undefined-behavior sanitization and exercise first execution on a fresh or restored context with no stack storage.

## Evidence

- [#96569](../micro_taxo/gh_96569.md): A newly executing context had null frame-stack pointers; the frame-push routine added a requested size to the null base before its capacity check, producing sanitizer-reported undefined behavior and an assertion abort during ordinary initial evaluation. Discussion also notes that saved/restored coroutine state can expose the same unallocated state.
