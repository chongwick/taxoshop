# Backend-dependent cleanup of temporary compatibility-probe records can leak separately allocated nested fields.

A platform-specific bulk cleanup operation releases temporary probe records but fails to reclaim some separately allocated fields contained within them.

## Precondition

Initialization performs a compatibility probe that creates temporary records whose nested text or payload fields have independent allocations, and cleanup behavior differs across supported backends.

## Critical operation

The probe is cleaned up through a backend-provided bulk removal or reset operation.

## Interference

One backend's bulk cleanup releases the outer records while leaving some embedded allocations unreclaimed.

## Invalid assumption

The caller assumes that the bulk cleanup operation recursively releases every allocation owned by each temporary record on every backend.

## Failure

The retained nested allocations survive initialization and are reported as a process-level memory leak by leak detection.

## Scope

This is a cautiously scoped pattern from a singleton report: it generalizes to backend-dependent cleanup of temporary records with nested allocations, but does not establish that all bulk cleanup APIs or all compatibility probes have this defect.

## Search strategy

1. Search initialization and compatibility-probe code for temporary records containing independently allocated nested fields.
2. Trace every backend implementation of bulk cleanup and verify that it releases both outer records and embedded allocations.
3. Compare bulk reset APIs with per-record removal APIs and check the ownership of every returned record and nested field.
4. Check whether probe cleanup uses a backend-specific path when the backend's bulk cleanup is known not to be recursive.

## Evidence

- [#150536](../micro_taxo/gh_150536.md): A compatibility probe created temporary history records with separately duplicated text fields; on one platform, the bulk history reset released the records but not all duplicated strings, while explicit per-record removal and field deallocation eliminated the leak.
