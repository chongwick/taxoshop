# Sanitizer exposure of nonportable fault injection and signature-unsafe callback dispatch

Low-level failure tests or dispatch paths rely on operations that are undefined in the language or ABI: deliberate invalid accesses or arithmetic to provoke faults, and calls through generic function-pointer interfaces whose signatures do not exactly match the target. With sanitizer instrumentation active or restored, these paths are diagnosed before their intended signal handling or callback behavior can be observed.

## Precondition

A low-level path deliberately fabricates a fault with undefined operations, or stores and invokes callbacks through a generic interface without preserving an exactly compatible function signature; sanitizer checks are active or disabled around the path.

## Critical operation

Execute the deliberate fault path or perform the indirect callback dispatch while sanitizer instrumentation is active or has been re-enabled.

## Interference

The sanitizer intercepts the fabricated invalid operation or reports the incompatible indirect call, and may abort before the expected fault signal, supervised process termination, or callback result completes.

## Invalid assumption

The implementation assumes that undefined operations will reliably produce the desired platform-level fault and that callbacks with merely similar argument layouts are interchangeable through a generic function-pointer interface.

## Failure

Execution or the associated test fails with sanitizer diagnostics or an unexpected abort instead of validating the intended fault-handling or callback-dispatch behavior.

## Scope

The reports support one umbrella pattern with two distinct mechanisms: sanitizer interception of intentional process-failure injection, and sanitizer-visible undefined behavior in callback dispatch or fault-trigger code. They do not establish that every sanitizer failure involves both mechanisms or that all generic callback storage is invalid; the callback hazard concerns invocation through a mismatched function type.

## Search strategy

1. Find tests or low-level routines that provoke faults with null reads, division by zero, invalid shifts, or other undefined operations, and replace them with explicit platform-appropriate signaling where possible.
2. Trace sanitizer-suppression annotations around fault injection and determine whether enabling instrumentation changes the observable signal, exit status, or supervisor result.
3. Check every indirect callback call and registration boundary for exact agreement of return and parameter types, including generated dispatch code and casts through generic function-pointer types.
4. Add signature-specific wrappers or generator-time checks for heterogeneous callback families, and verify sanitizer-enabled execution of each dispatch path.

## Evidence

- [#93981](../micro_taxo/gh_93981.md): A supervised worker-recovery test deliberately caused fatal memory faults; AddressSanitizer intercepted the resulting invalid access and aborted the worker with a fatal-signal report, so the test did not observe the ordinary worker-failure behavior.
- [#133157](../micro_taxo/gh_133157.md): Removing undefined-behavior suppression exposed deliberate null-read and divide-by-zero fault fabrication plus indirect callback calls with incompatible signatures; the changes replaced synthetic faults with explicit signaling, removed an unnecessary null-read path, and introduced signature-aware dispatch handling.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0026](../macro_taxo_before_hybrid/workflow-0026.md)
- [workflow-0082](../macro_taxo_before_hybrid/workflow-0082.md)
