# precondition → critical operation → interference → invalid assumption → failure

A runtime tracks immutable aggregate containers whose contents cannot participate in cycles, inflating collector work and triggering unnecessary collections.

## Precondition

Many immutable aggregate containers are created with contents that are not eligible to participate in reference cycles, while the collector accounts for or tracks those containers as potential cyclic objects.

## Critical operation

The runtime unconditionally registers each newly created aggregate with the cycle-detecting collector and uses eligible-object counts to drive collection thresholds.

## Interference

The collector repeatedly scans containers that cannot contribute to reclaimable cycles, and the inflated population causes collection scheduling and accounting overhead.

## Invalid assumption

Treating every collector-capable immutable aggregate as requiring tracking, and treating the number of potentially trackable objects as equivalent to the number of actually tracked objects, is assumed to be an acceptable approximation.

## Failure

Allocation-heavy workloads suffer excessive collection frequency and scanning, producing a substantial garbage-collection performance regression.

## Scope

This is a singleton cluster. The evidence directly supports immutable tuple-like aggregates in a cycle-detecting garbage collector; extension to other immutable container types requires separate evidence.

## Search strategy

1. Check whether immutable aggregate constructors register objects unconditionally instead of inspecting whether their contents can participate in cycles.
2. Check whether collector thresholds and heap-size statistics count merely eligible objects rather than objects currently registered for cycle detection.
3. Check whether slicing, concatenation, repetition, packing, or copying paths preserve unnecessary tracking for immutable aggregates containing only non-cycle-participating values.
4. Check whether deferred untracking is relied upon to correct creation-time over-tracking before collection thresholds are reached.

## Evidence

- [#139951](../micro_taxo/gh_139951.md): The report shows that large numbers of small immutable aggregates containing only non-collectible values were tracked at creation, that collector accounting counted objects that were merely eligible for tracking, and that avoiding such tracking plus counting only actually tracked objects corrected the excessive-collection regression.
