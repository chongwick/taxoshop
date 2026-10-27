# User-provided display text containing an unescaped reserved substitution marker is later processed by a formatter that interprets the marker as a directive, so,

A display-text API accepts literal user content but routes it through substitution formatting during rendering.

## Precondition

A caller supplies display text containing a character reserved by the API's substitution syntax, without the required escaping.

## Critical operation

The rendering path applies substitution expansion to the supplied text using the API's formatting rules.

## Interference

The reserved character is parsed as the start of a substitution directive rather than preserved as literal display content.

## Invalid assumption

The implementation assumes supplied display text is already valid substitution-format text, or that literal reserved characters need no escaping.

## Failure

Rendering rejects the text with a formatting error instead of displaying the caller's intended text.

## Scope

This is a singleton pattern, so it is scoped to display interfaces that intentionally support substitution formatting and fail when literal reserved syntax is not escaped.

## Search strategy

1. Inspect display-text rendering paths for implicit formatting or substitution of caller-controlled strings.
2. Check whether reserved syntax characters in user-supplied display text are escaped before expansion.
3. Trace formatting failures for malformed or incomplete substitution directives back to the original text boundary.
4. Verify documentation and validation clearly distinguish literal display text from substitution templates.

## Evidence

- [#57894](../micro_taxo/gh_57894.md): The report shows that display text containing a literal reserved marker is passed through substitution expansion, where the marker is interpreted as an invalid directive and rendering fails; doubling the marker preserves literal output.
