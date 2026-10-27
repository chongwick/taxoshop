# A low-level structured-data encoder accepts an unvalidated initial nesting level that is inconsistent with its formatting-cache contents.

When formatting nested containers, the encoder lazily caches per-depth separator and indentation strings. A caller-supplied starting depth can exceed the cache's initialized depth, exposing a synchronization flaw between logical depth and cache state.

## Precondition

An internal or low-level encoding entry point accepts a non-base initial nesting level without ensuring that the formatting cache contains entries through that level.

## Critical operation

Encoding a non-empty nested container increments the logical nesting level and requests the cached separator or indentation string for that new level.

## Interference

The cache-growth path is invoked with a logical level far beyond the cache's actual size, so its index calculations operate on a short cache rather than on entries representing the preceding level.

## Invalid assumption

The cache-growth helper assumes that entries for the immediately preceding logical level already exist whenever a deeper level is requested.

## Failure

The helper either trips its consistency assertion in diagnostic builds or reads beyond the cache allocation in unchecked builds, producing an abort or heap-buffer-overflow instead of a recoverable validation or state error.

## Scope

This is a cautiously scoped pattern from a singleton report: it applies to lazily grown depth-indexed formatting caches when an internal entry point permits an inconsistent initial depth; it does not claim that all cache-growth failures have this cause.

## Search strategy

1. Check internal encoder entry points for caller-supplied depth or level parameters that are not normalized to the cache's initialized depth.
2. Trace every lazy cache-growth index from the requested logical level back to the cache initialization size.
3. Verify that a cache-growth helper validates the requested level against actual cache length before deriving data from the previous level.
4. Exercise direct low-level calls with nonzero initial depth and a nested, non-empty container under sanitizers and assertions enabled.

## Evidence

- [#140750](../micro_taxo/gh_140750.md): A direct low-level encoder call supplied an initial depth greater than the one-entry formatting cache; encoding a nested mapping requested a deeper separator, after which the cache-growth helper asserted in a debug build and performed an out-of-bounds read under AddressSanitizer.
