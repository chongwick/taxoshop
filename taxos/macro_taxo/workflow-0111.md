# A legacy global-registration path is invoked for a component created with an incompatible managed state layout.

Legacy registration rejects components whose state is defined through a structured or slot-based layout.

## Precondition

A module-like component is created with managed, slot-based, or otherwise structured state that the legacy registration mechanism does not support.

## Critical operation

Invoke the legacy global-registration operation on that component.

## Interference

The registration path encounters the component's incompatible state layout and cannot map it into the legacy global-state model.

## Invalid assumption

The caller assumes the legacy registration operation accepts every module-like component regardless of its state-layout representation.

## Failure

Registration is rejected with an internal system-level error instead of completing.

## Scope

This is a cautiously scoped singleton pattern: it establishes incompatibility between one legacy registration path and slot-based managed state, but does not show that all legacy operations or all structured state layouts are incompatible.

## Search strategy

1. Check legacy registration callers for components created with managed or slot-based state layouts.
2. Trace registration preconditions and verify that structured state layouts are explicitly supported.
3. Search for internal errors raised when legacy and managed state models are mixed.
4. Audit callers that ignore or fail to validate compatibility before invoking registration.

## Evidence

- [#140751](../micro_taxo/gh_140751.md): The report demonstrates that invoking a legacy registration operation on a component with slots is rejected with a system-level error, and that this rejection is expected behavior.
