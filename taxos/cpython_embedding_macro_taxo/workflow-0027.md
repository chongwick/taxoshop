# Nonportable text-editor directives in configuration generation

A configuration generator uses a line-oriented text transformation to splice generated multi-line content into an output artifact, but relies on editor syntax or invocation behavior that is not consistently supported. If the directive is rejected or left unprocessed, generated editing text can reach the shell or output artifact as executable syntax, causing configuration to abort.

## Precondition

A configuration or build-generation step must insert dynamically generated multi-line content into a generated configuration artifact.

## Critical operation

The generator invokes a line-oriented text transformation using a generated multi-line editing directive.

## Interference

The intended text transformation is not successfully consumed because the available tool rejects the directive or the directive is otherwise emitted without being processed.

## Invalid assumption

The generator assumes that its multi-line editing syntax and execution path are portable and will always transform the directive into artifact content.

## Failure

Configuration generation aborts with an editor error or with shell command/syntax errors from residual editing directives.

## Scope

The shared evidence is a configuration-generation portability failure around unprocessed multi-line text-editing directives. Only one report establishes a specific cross-implementation editor incompatibility; the other establishes the residual-directive shell failure but does not conclusively identify its underlying tool failure.

## Search strategy

1. Check every generated multi-line editor expression against each supported implementation of the selected text-processing tool.
2. Check that generated editor programs are passed to the intended processor rather than appended or evaluated as shell input.
3. Check configuration-generation error paths for unprocessed editor directives in generated artifacts.
4. Check generated configuration scripts for line-address or editor-command text that is not valid shell syntax.
5. Check tool-discovery and invocation code for a clear failure when the required transformation capability is unavailable.

## Evidence

- [#94404](../micro_taxo/gh_94404.md): A generated multi-line insertion directive worked with one text-editor implementation but was rejected by another, stopping configuration generation; replacing it with a more portable file-read insertion avoided the incompatibility.
- [#116259](../micro_taxo/gh_116259.md): Configuration created a generated shell script containing an unprocessed line-address editing directive, which the shell attempted to execute and then rejected as malformed syntax.
