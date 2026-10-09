# Unchecked conversion of a large relative timeout to a signed absolute deadline

A timeout implementation admits a finite relative duration but derives an absolute deadline with signed addition without first ensuring the sum is representable.

## Precondition

A blocking operation receives a large nonnegative finite timeout that is accepted by its timeout-range validation.

## Critical operation

The operation converts that relative timeout into an absolute deadline by adding it to a current clock reading in a signed time representation.

## Interference

The nonzero current clock reading reduces the remaining positive range, so the accepted timeout and current time cannot be represented as one deadline.

## Invalid assumption

Accepting the relative timeout as representable is assumed to guarantee that the derived absolute deadline is also representable.

## Failure

The signed deadline addition overflows, invoking undefined behavior and producing a runtime overflow diagnostic.

## Scope

Singleton cluster: this pattern is scoped to signed relative-timeout-to-absolute-deadline arithmetic; the report does not establish behavior for unsigned representations or timeout conversions that reject oversized values before deadline construction.

## Search strategy

1. Inspect every relative-timeout-to-deadline conversion for unchecked signed addition with a current clock value.
2. Verify that timeout limits reserve headroom for the current clock value when absolute deadlines use signed integers.
3. Require checked or saturating arithmetic before constructing absolute deadlines from durations.
4. Review retry and interruption paths that recompute remaining timeout from an absolute deadline for the same unsafe initialization pattern.

## Evidence

- [#77813](../micro_taxo/gh_77813.md): An accepted near-maximum timeout was added to a monotonic clock value, producing a signed-integer-overflow runtime diagnostic; the resolution introduced overflow-clamping deadline construction across timed waiting paths.
