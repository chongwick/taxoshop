# Macro Taxonomy: Error-Path Cleanup And Resource Accounting

## Pattern
An operation allocates Python or native state, then takes an exception,
unsupported-feature, failed conversion, or partial-initialization path that
does not release every acquired resource. These defects are usually quiet in
normal execution and surface only through LeakSanitizer or reference-leak
testing.

## Common Sources
- Argument Clinic and converter failures.
- Extension-module constructor and setup failures.
- JIT, profiling, tracing, and thread initialization.
- Exception chaining and error-reporting paths.

## Failure Shapes
- Direct or indirect leak at process exit.
- Reference leak after a Python exception.
- Resource retained after a failed native setup step.

## Defensive Rule
Use a single ownership transfer point, initialize owned pointers to null, and
route every failure after acquisition through one cleanup path. Test failure
branches under reference and leak sanitizers, not only successful execution.

## Representative Micro-taxonomies
- [#141372](../micro_taxo/gh_141372.md): profiler monitoring setup leaks after
  incomplete initialization.
- [#141542](../micro_taxo/gh_141542.md): JIT tracing initialization leak.
- [#140517](../micro_taxo/gh_140517.md): strict `map_next` error path leak.
- [#139748](../micro_taxo/gh_139748.md): Argument Clinic converter ownership
  on error paths.
- [#140530](../micro_taxo/gh_140530.md): exception-cause failure leaks a
  reference.

## Membership Rule
Group memory and reference leaks whose title, trigger, or evidence mentions an
error path, failed setup, exception, initialization, conversion, or shutdown.
