# Partial-object cleanup dereferences absent optional state and duplicates a transferred parent release

When a child is linked to a parent before full initialization, a later allocation failure can invoke cleanup that is unsafe for partial state and inconsistently accounts for parent ownership.

## Precondition

A newly allocated child acquires a parent association before all fields required by its destructor, including optional cleanup state, are initialized.

## Critical operation

A subsequent allocation or initialization step fails and the error path disposes of the partially initialized child.

## Interference

Child destruction dereferences the still-absent optional state and releases the parent association, while surrounding failure handling also releases that parent ownership independently.

## Invalid assumption

The destructor is safe for every initialization stage, and the parent ownership reference remains separately owned after child cleanup.

## Failure

Recoverable allocation failure instead causes cleanup-time null dereference and duplicate parent release, potentially crashing or corrupting ownership accounting.

## Scope

This is a cautiously scoped singleton pattern: it generalizes the interaction between partial-object destruction, optional cleanup state, and premature parent ownership transfer, not all null dereferences or double releases.

## Search strategy

1. Trace every allocation failure after child-parent association and verify cleanup is safe at each partial-initialization stage.
2. Check destructors and cleanup helpers for unguarded dereferences of optional fields that are initialized only later.
3. Map parent ownership transfers and confirm exactly one release occurs across destructor and error-path cleanup.
4. Force failures at each initialization allocation and verify the original error propagates without crashes or ownership-count changes.

## Evidence

- [#144984](../micro_taxo/gh_144984.md): The report shows a child parser retaining its parent before later allocations complete; failure cleanup invokes destruction with a null handler table, while parent cleanup and the error path both decrement the parent reference.
