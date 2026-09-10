# Sanitizer-uncovered undefined behavior in fault injection and callback dispatch

Low-level test or runtime paths suppress undefined-behavior instrumentation while deliberately triggering faults or adapting callbacks through generic interfaces. Removing the suppression exposes both fabricated fault operations and incompatible indirect-call signatures.

## Precondition

A low-level path relies on undefined operations to provoke a fault, or passes callbacks with concrete return types through a generic function-pointer interface; sanitizer checks are disabled around that path.

## Critical operation

Re-enable undefined-behavior instrumentation and execute or generate the fault-triggering or callback-dispatch path.

## Interference

The sanitizer instruments the operation before the intended signal or callback behavior can complete, and function-pointer type mismatches become diagnosable indirect-call violations.

## Invalid assumption

The compiler, target ABI, or runtime will consistently turn fabricated undefined behavior into the desired fault, and differently typed callbacks are interchangeable when their argument lists appear similar.

## Failure

Execution aborts with a fatal undefined-behavior diagnostic or the build/test path becomes unreliable instead of reaching the intended fault handler or dispatch result.

## Scope

This is a singleton report; it supports the pattern for C code that combines sanitizer suppression with deliberate fault injection or typed-callback adaptation. It does not establish that every sanitizer suppression or every generic callback interface has this defect.

## Search strategy

1. Search for sanitizer-suppression attributes around deliberate null dereferences, division by zero, invalid shifts, or other operations used to provoke faults.
2. Check every generic callback wrapper and indirect call for exact agreement between the callback's declared return and parameter types and the wrapper signature.
3. Search generated dispatch code for casts from typed function pointers to generic function-pointer types.
4. Replace synthetic undefined fault triggers with explicit, platform-appropriate signaling and add typed wrappers or generator-time signature checks.

## Evidence

- [#133157](../micro_taxo/gh_133157.md): The report removes suppression from deliberate fault-triggering code, replaces arithmetic undefined behavior with explicit signal delivery, deletes an unnecessary null-read test, and replaces incompatible callback casts in generated lookahead dispatch with signature-specific wrappers and generator checks.
