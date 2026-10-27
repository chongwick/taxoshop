# Context-sensitive syntax is validated only during later code generation, while an optimization pass can remove the construct first; residual compilation state,ā

A compiler accepts source containing a construct whose legality depends on its enclosing context, but defers that legality check until code generation. Optimization can eliminate the construct before the check runs, while later compilation still consumes related scope or coroutine metadata. The compiler then relies on the missing construct having been context-valid and may abort on an internal assertion instead of reporting a syntax error.

## Precondition

Source contains a context-sensitive asynchronous construct in an enclosing context where that construct is illegal, and the construct is located in code eligible for compile-time removal.

## Critical operation

Run the compiler's optimization pass before performing the construct's context-legality validation.

## Interference

Optimization removes the source subtree that would have triggered the recoverable syntax check, while compilation continues with scope, symbol, or coroutine metadata derived from the original source.

## Invalid assumption

Later code-generation logic assumes every remaining relevant asynchronous construct is in a permitted function-like or explicitly enabled top-level context.

## Failure

The compiler reaches an internal consistency assertion or equivalent unrecoverable failure instead of returning a syntax error for the invalid source.

## Scope

This is a singleton cluster, so the pattern is cautiously scoped to compiler pipelines where optimization may precede validation of context-sensitive asynchronous constructs. The report covers multiple asynchronous forms but does not establish that every optimization or every context-sensitive language feature behaves this way.

## Search strategy

1. Find context-sensitive syntax whose legality is checked only in code-generation visitors rather than during an always-run semantic or symbol-analysis phase.
2. Trace optimization paths that delete constant-false branches, assertions, unreachable statements, or other dead subtrees before legality checks execute.
3. Check whether removed constructs can still affect scope, symbol, coroutine, or feature flags consumed by later compilation stages.
4. Verify that later compiler assertions about enclosing context are protected by an earlier validation that cannot be bypassed by optimization.

## Evidence

- [#121637](../micro_taxo/gh_121637.md): The report demonstrates that invalid top-level asynchronous expressions and asynchronous comprehensions inside optimized-away code bypassed deferred compiler checks, leaving later compilation to assert on an invalid context; the fix moved validation earlier so a syntax error is produced across optimization levels.
