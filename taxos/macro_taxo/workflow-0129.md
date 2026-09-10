# Native or low-level code obtains an object through an overridable, re-entrant, or replaceable operation and expects a specific internal type or layout.

Native or low-level code obtains an object through an overridable, re-entrant, or replaceable operation and expects a specific internal type or layout.

## Precondition

A low-level path crosses a dynamic trust boundary such as a factory, constructor, cache method, or attribute lookup, then receives a generic object value.

## Critical operation

The path immediately uses that value as a specific internal representation, accessing fields or state through an unchecked cast or equivalent assumption.

## Interference

User-controlled behavior at the trust boundary returns or exposes an object with an incompatible type or smaller layout.

## Invalid assumption

The value's provenance through the expected callback, cache, attribute, or constructor is treated as proof that it satisfies the required representation contract.

## Failure

Representation-specific access or state mutation operates on the wrong object, causing type confusion, heap out-of-bounds access, or process termination instead of a recoverable validation error.

## Scope

The four reports support a general unchecked-use pattern across factories, constructors, caches, and attribute lookups—not only factory initialization. The exact consequence varies by representation and access path; the shared risk is treating dynamically obtained objects as validated internal representations without checking type and layout first.

## Search strategy

1. Audit every dynamic callback, constructor, cache operation, and attribute lookup consumed by low-level code for immediate unchecked representation use.
2. Search for casts from generic object values to internal structs after dynamic dispatch or object creation.
3. Verify the required exact or compatible type before every metadata, field, or buffer access.
4. Check that malformed dynamic results are rejected before state mutation, cache updates, or decoder execution.

## Evidence

- [#142595](../micro_taxo/gh_142595.md): A replaceable type-producing call returned a non-type object that was cast to an internal type representation and dereferenced during initialization; the fix validates the result before use.
- [#142781](../micro_taxo/gh_142781.md): Replaceable cache operations returned an object incompatible with the requested instance type, and the consumer treated it as a valid internal instance; the fix validates cache results before dependent state updates.
- [#143376](../micro_taxo/gh_143376.md): A dynamically supplied attribute returned an arbitrary small object that a decoder treated as a larger internal identifier structure, producing a heap-buffer-overflow; the proposed fix validates the identifier type.
- [#143636](../micro_taxo/gh_143636.md): An overridable constructor returned a nonconforming object during replacement, after which the consumer accessed it as the expected namespace representation; the fix rejects the result before copying internal state.
