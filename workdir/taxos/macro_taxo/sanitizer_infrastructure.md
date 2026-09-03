# Macro Taxonomy: Sanitizer, Build, And Test Infrastructure

## Pattern
Some reports do not expose an interpreter memory-safety defect directly.
Instead, they show that sanitizer configuration, platform toolchains, test
harness behavior, symbolization, or allocator choices prevent reliable
detection or produce misleading diagnostics.

## Recurring Concerns
- AddressSanitizer compatibility with PyMalloc and platform linkers.
- TSan and UBSan differences across macOS, Windows, and free-threaded builds.
- Missing symbolizers and unhelpful allocation stacks.
- Tests that time out or leak only under sanitizer instrumentation.

## Defensive Rule
Treat sanitizer builds as supported configurations: document allocator and
toolchain constraints, preserve symbols, make tests deterministic under slower
instrumented execution, and distinguish test-harness leaks from interpreter
ownership defects.

## Representative Micro-taxonomies
- [#136872](../micro_taxo/gh_136872.md): ASan with PyMalloc configuration.
- [#135830](../micro_taxo/gh_135830.md): MSVC ASan test failures.
- [#150467](../micro_taxo/gh_150467.md): ASan/MSVC linker failure.
- [#150195](../micro_taxo/gh_150195.md): UBSan failure on macOS ARM64.
- [#142917](../micro_taxo/gh_142917.md): leak report with unavailable external
  symbolization.

## Membership Rule
Group micro-taxonomies whose reported failure concerns sanitizer setup,
toolchain behavior, allocator configuration, symbolization, or a test that
only fails under instrumentation.
