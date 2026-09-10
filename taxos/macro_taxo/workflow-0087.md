# An instrumentation or diagnostic mode unconditionally replaces an explicitly selected compatible subordinate configuration with its own default.

A build configuration enables a diagnostic mode and explicitly selects a compatible allocator or related implementation, but mode setup overwrites that selection with a default.

## Precondition

A configuration supports both a mode-specific default and an explicit user selection for the same subordinate behavior, and the selections are valid together.

## Critical operation

The mode's configuration logic assigns its preferred default to the subordinate option.

## Interference

That assignment is unconditional and occurs even when the user has already supplied an explicit value.

## Invalid assumption

The configuration logic assumes the subordinate option is unset or that the mode's default must always take precedence.

## Failure

The explicit selection is silently discarded, producing a valid build with unintended behavior and no clear indication that the requested override was ignored.

## Scope

This is a cautiously scoped singleton pattern covering configuration precedence defects involving a mode-derived default and an explicit compatible subordinate choice. The report does not establish that all mode defaults are incorrect—only that they must not override explicit user input when the combination is supported.

## Search strategy

1. Check mode-specific setup for unconditional writes to options that are also user-configurable.
2. Verify default assignments occur only when the corresponding option remains unset.
3. Review precedence handling for explicit command-line or configuration-file values versus feature-derived defaults.
4. Test combined configurations where a diagnostic mode is enabled alongside an explicit compatible implementation choice.

## Evidence

- [#136872](../micro_taxo/gh_136872.md): The report states that enabling address-sanitizer disables an explicitly requested memory allocator, although the combination works when the unconditional disabling assignment is removed; the accompanying comment explicitly says the user option should override the default.
