# Unsafe typed diagnostic formatting on exceptional paths

A validation or error path constructs a diagnostic with a typed formatting interface while its values are not guaranteed to satisfy the format directives and argument contract.

## Precondition

Malformed, excessive, or noncanonical input reaches an error or warning-reporting path with dynamically derived values.

## Critical operation

The path passes those values to a variadic or typed diagnostic formatter.

## Interference

A format directive requires a narrower representation or argument position than the supplied value provides, such as text for a non-text value or a missing argument paired with a count.

## Invalid assumption

The diagnostic formatter will receive values whose types, representations, and positions always match the format string.

## Failure

Diagnostic construction performs an invalid memory read or buffer overrun and crashes instead of returning the intended error or warning.

## Scope

The reports support a pattern about mismatched typed diagnostic-format contracts on exceptional paths, broader than missing variadic arguments. The shared mechanism is unsafe formatting assumptions; the reports do not establish that every diagnostic-format defect has the same memory-safety consequence.

## Search strategy

1. Audit every diagnostic format string against its complete argument list and each argument’s runtime type contract.
2. Check exceptional paths that format arbitrary, user-controlled, or noncanonical values.
3. Search for text-oriented directives fed by counts, pointers, keys, or generic objects without explicit conversion.
4. Exercise malformed argument and keyword inputs under memory sanitizers and verify that the intended diagnostic is produced.

## Evidence

- [#114050](../micro_taxo/gh_114050.md): An excessive-argument error path supplied only a numeric count to a format string containing an unmatched text directive, causing the count to be interpreted as a text pointer and read from an invalid address.
- [#140492](../micro_taxo/gh_140492.md): A warning path formatted a non-text keyword value with a directive requiring a text-compatible value, causing the formatter to read beyond the value’s valid storage.
- [#144169](../micro_taxo/gh_144169.md): Non-string keyword keys reached error and warning formatting that assumed text-compatible values; using a representation suitable for arbitrary objects prevented the diagnostic path from crashing.
