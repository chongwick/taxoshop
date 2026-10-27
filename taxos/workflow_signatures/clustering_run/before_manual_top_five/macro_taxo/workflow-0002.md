# Literal reserved marker in display text is misinterpreted as a formatting directive

An interface accepts display text containing literal caller content but later processes that text as a substitution template during rendering.

## Precondition

A caller supplies display text containing a reserved substitution marker without the escaping required by the formatting syntax.

## Critical operation

The rendering path applies substitution expansion to the supplied display text.

## Interference

The reserved marker is parsed as the start of a substitution directive instead of remaining literal display content.

## Invalid assumption

The implementation assumes display text is valid template text, or that callers will escape literal reserved markers themselves.

## Failure

Rendering raises a formatting error and fails to display the intended text.

## Scope

This is a singleton pattern, scoped to display interfaces that intentionally apply substitution formatting during rendering; it does not generalize to display paths without template interpretation.

## Search strategy

1. Inspect display-text rendering paths for implicit formatting or substitution of caller-controlled strings.
2. Check whether reserved syntax characters in supplied display text are escaped before template expansion.
3. Trace malformed or incomplete substitution-directive errors back to the original display-text boundary.
4. Verify documentation and validation distinguish literal display text from substitution templates.

## Evidence

- [#57894](../micro_taxo/gh_57894.md): The report shows that a literal percent marker in supplied help text is later processed by percent-style substitution, interpreted as an invalid directive, and rejected; escaping the marker produces the intended literal output.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0002](../macro_taxo_before_hybrid/workflow-0002.md)
