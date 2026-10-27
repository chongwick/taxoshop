# Static special instances are exposed to collector traversal despite lacking the ordinary object layout.

A collector-traversable type is also used for immutable or static special instances whose storage omits fields required by ordinary collectible objects.

## Precondition

A type is shared by ordinary heap objects and special static instances that lack header metadata or reference fields expected by collectible objects.

## Critical operation

The garbage collector dispatches the type's traversal routine for one of those special instances during collection or cleanup.

## Interference

The traversal reads layout-dependent fields at offsets valid for ordinary heap objects but outside the special instance's valid storage.

## Invalid assumption

Type-level traversal eligibility is treated as proof that every instance has the complete collectible-object layout and can be traversed identically.

## Failure

The traversal performs an out-of-bounds read in static storage, triggering a memory-safety failure and aborting the process.

## Scope

Both reports evidence the same incident, so this pattern is limited to traversal-capable types with compact static special instances mistakenly exposed to the collector. They do not establish a rule for all static records or all layout mismatches.

## Search strategy

1. Inspect every traversal-enabled type for static, immutable, or immortal instances sharing that type.
2. Verify that each instance reaching traversal has every header and reference field the routine accesses.
3. Trace collector admission checks to ensure noncollectible special instances are excluded before traversal.
4. Run memory-safety instrumentation through collection and cleanup paths that may encounter static instances.

## Evidence

- [#118074](../micro_taxo/gh_118074.md): The fix excludes statically stored special instances from collection because the shared traversal routine otherwise reads beyond their object storage.
- [#118113](../micro_taxo/gh_118113.md): The sanitizer trace shows cleanup-time traversal reading before a static instance whose storage lacks the metadata expected by ordinary collectible objects; the report was identified as a duplicate.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0057](../macro_taxo_before_hybrid/workflow-0057.md)
