# Unchecked downstream truncation after expanding a fixed-format diagnostic field

Adding variable-length metadata to a diagnostic component can exceed a fixed-width formatter later in the rendering path, silently publishing a truncated description.

## Precondition

A user-visible diagnostic header combines existing variable-length identity metadata with a build-information component that is rendered through a fixed-capacity formatting path.

## Critical operation

Extend the build-information component with generated descriptors for additional configuration choices.

## Interference

The downstream formatter retains its fixed output limit and truncates the expanded component while constructing the displayed header.

## Invalid assumption

Assume that allocating or budgeting more storage for the component is sufficient without validating every downstream display limit against the complete worst-case header.

## Failure

Users receive an incomplete, potentially misleading diagnostic description because trailing build metadata is cut off.

## Scope

Singleton cluster: scoped to diagnostic text whose expanded component is later rendered through a fixed-capacity formatting path.

## Search strategy

1. Trace each expanded diagnostic field through every formatter and display path, and compare their capacities with the full worst-case output.
2. Search for fixed-width format specifiers, fixed-size buffers, and explicit truncation around version, banner, and build-information rendering.
3. Construct worst-case combinations of variable identity data and optional configuration descriptors, then assert that displayed output is complete.
4. When increasing a metadata field's storage budget, audit downstream copies and composed headers for independent size limits.

## Evidence

- [#100086](../micro_taxo/gh_100086.md): Adding build-configuration descriptors to a version diagnostic caused the displayed header to truncate the new information because a downstream formatting limit remained fixed; the accepted resolution moved the details to a dedicated test-reporting output.
