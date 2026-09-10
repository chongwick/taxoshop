# Fallback error handling invokes a missing dependency after an unchecked lookup.

A fallback error-reporting path retrieves a required operation from mutable support state and uses the result without validating that the lookup succeeded.

## Precondition

The normal error-reporting mechanism is unavailable, so fallback formatting must locate a lower-level support operation.

## Critical operation

The fallback formatter looks up that required operation and proceeds toward invoking the returned value.

## Interference

The operation has been removed or otherwise made unavailable before the lookup.

## Invalid assumption

The lookup is assumed to return a valid callable, with no presence or validity check on failure.

## Failure

The fallback path invokes an invalid or absent value, causing a secondary internal assertion or crash that prevents the original error from being reported.

## Scope

This cluster contains one report, so the pattern is scoped to fallback diagnostic paths that depend on mutable support state; it does not claim that all error-reporting crashes share this mechanism.

## Search strategy

1. Trace fallback error-reporting branches for lookups of required operations from mutable registries, modules, or shared support objects.
2. Check every lookup result used as a callable for explicit failure handling before invocation.
3. Inspect mutation, teardown, and reconfiguration paths for removal or replacement of dependencies used by fallback handling.
4. Verify that failures inside diagnostic or recovery paths preserve the original error instead of terminating with a secondary internal failure.

## Evidence

- [#142737](../micro_taxo/gh_142737.md): The report demonstrates that fallback traceback formatting retrieves a support operation after it has been removed, fails to check the unsuccessful lookup, and later triggers an internal assertion while attempting to report the original runtime error.
