# A native-operation wrapper forwards a caller-supplied buffer without validating its operation-specific minimum capacity.

An undersized output buffer reaches a native operation that writes a fixed-layout result, allowing the write to exceed the buffer and be detected only after possible memory corruption.

## Precondition

The selected native operation requires a fixed-size or operation-specific output area, but the caller provides an empty or undersized buffer.

## Critical operation

The wrapper invokes the native operation with the caller's buffer, or a derived temporary buffer, without first verifying sufficient capacity for that operation.

## Interference

The native operation writes its result according to its own size requirements, beyond the buffer length accepted by the wrapper.

## Invalid assumption

The wrapper assumes the caller supplied a suitably sized buffer or that generic buffer handling can determine safety without operation-specific size knowledge.

## Failure

The overrun may corrupt stack or heap memory; post-operation guard detection raises a fatal low-level system error instead of a recoverable argument-size error.

## Scope

Supported by two related reports involving operation-dependent native output sizes and zero-length buffers. The pattern applies to wrappers that lack operation-specific capacity knowledge; it does not imply that every buffer API can or should prevalidate arbitrary native operations.

## Search strategy

1. Inspect native-operation wrappers that dispatch operation codes and pass caller-provided buffers without operation-specific capacity checks.
2. Find fixed-size native output writes whose destination capacity comes directly from a caller-supplied buffer length.
3. Trace empty and undersized-buffer paths to confirm they are rejected before the native call rather than checked only afterward.
4. Review post-call canary or guard failures and verify whether they produce fatal internal errors instead of input-validation errors.

## Evidence

- [#141338](../micro_taxo/gh_141338.md): An empty caller buffer was forwarded for an operation requiring a larger fixed-size result, and the native write overran the temporary buffer, producing a detected buffer-overflow system error.
- [#144206](../micro_taxo/gh_144206.md): An empty mutable buffer was supplied for an operation requiring a fixed-size result; the wrapper could not generically validate the operation-specific size before invocation, and overflow detection produced a system error.
