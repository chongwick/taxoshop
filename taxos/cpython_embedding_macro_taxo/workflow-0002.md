# Unescaped literal marker in template-enabled display text

A display-text field supports runtime template substitution but receives a literal substitution marker that is not escaped.

## Precondition

A caller supplies display text to an interface whose help or presentation strings undergo percent-style template expansion.

## Critical operation

The interface renders the text by applying its substitution formatter with presentation parameters.

## Interference

The supplied text contains a single percent marker intended for literal display, followed by text that the formatter parses as an invalid conversion.

## Invalid assumption

The caller assumes the display text is rendered verbatim rather than interpreted as a template, and does not escape the literal marker.

## Failure

Formatting raises an invalid-conversion error and prevents the display text from being rendered.

## Scope

Singleton cluster: this pattern is limited to percent-style expansion of display/help text and does not establish behavior for other template syntaxes or arbitrary user-input fields.

## Search strategy

1. Check every template-enabled display-text input for literal percent markers that are not escaped.
2. Trace help and presentation rendering paths for late percent-style formatting of caller-supplied strings.
3. Verify that documentation for substitution-capable text fields states the literal-marker escape sequence.
4. Add rendering tests with literal percent markers followed by ordinary text.

## Evidence

- [#57894](../micro_taxo/gh_57894.md): A help-text value containing a literal single percent marker was later percent-formatted during rendering, causing an unsupported-format-character error; escaping it as a doubled marker rendered the intended literal character.
