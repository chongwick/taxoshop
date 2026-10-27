# Dependency contract drift makes compatibility tests stale

A test suite encodes an external dependency's accepted-value domain, normalization, and diagnostics; a dependency update changes that contract, so unchanged assertions fail even though the operation remains valid.

## Precondition

Tests directly exercise behavior owned or defined by an external toolkit and assert specific accepted input forms, converted results, or error text.

## Critical operation

Run those tests after upgrading the toolkit while retaining the existing version-independent expectations.

## Interference

The toolkit broadens an option's value domain from integral values to general screen-distance values and correspondingly changes parsing, conversion, returned representations, or diagnostic wording.

## Invalid assumption

The tests assume the previous validator, normalization rules, and exact diagnostics remain stable across toolkit versions.

## Failure

Valid operations or correctly rejected inputs produce a test failure because the assertion compares current dependency behavior with an obsolete expectation.

## Scope

This is a cautiously scoped singleton pattern. The report supports dependency-driven drift in accepted values, conversion/representation, and diagnostics within compatibility tests; it does not establish that every dependency update causes this failure mode.

## Search strategy

1. Check tests that assert exact third-party error strings or validator-specific diagnostics.
2. Check shared test helpers for hard-coded conversions, rounding, clipping, or return-type assumptions tied to an external dependency.
3. Check version-gated option tests whenever a dependency changes an option's accepted input domain.
4. Check compatibility tests for assertions that distinguish integral values from unit-bearing or otherwise richer representations.
5. Check whether dependency-version branches cover changed normalization and representation behavior, not only changed input acceptance.

## Evidence

- [#124378](../micro_taxo/gh_124378.md): The report shows that an external UI toolkit changed size-related options from integer-only behavior to screen-distance values, altering conversion and error behavior; the test suite was revised to separate version-dependent expectations and update shared helpers, demonstrating stale dependency-contract assertions rather than an application failure
