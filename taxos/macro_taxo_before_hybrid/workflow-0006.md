# Unchecked absence of installation metadata during recovery

A recovery or repackaging path fails to handle an externally removed, system-managed installation whose metadata record is missing, so absence is passed into iteration logic and becomes a type-level crash instead of a diagnostic or recovery result.

## Precondition

A system-managed installation and its metadata coexist with another installation, and the system-managed files or metadata can be removed by an uncoordinated uninstaller.

## Critical operation

A bundled recovery or repackaging component reconstructs the installation by querying its recorded file set.

## Interference

The external removal deletes the installation artifacts and metadata, causing the lookup to produce no record set.

## Invalid assumption

The recovery pipeline assumes the metadata lookup always returns an iterable collection and does not validate or explicitly handle absence.

## Failure

The recovery operation raises a type error while iterating or packaging the absent record set, masking the missing-installation condition and preventing graceful recovery.

## Scope

Singleton cluster: this pattern is directly supported by one report and is scoped to recovery or repackaging workflows that consume metadata after external removal; it does not establish that all uninstallers or all missing-metadata cases fail this way.

## Search strategy

1. Trace recovery and repackaging calls that consume installation metadata after an uninstall or external deletion.
2. Check every metadata lookup used for file enumeration for explicit handling of a missing record or absent installation.
3. Search for iteration, unpacking, or concatenation of lookup results whose contract permits no result.
4. Verify that uninstallation of system-managed files is detected and reported before recovery assumes their metadata remains available.

## Evidence

- [#72111](../micro_taxo/gh_72111.md): The report describes a system-managed installation being removed unintentionally alongside another version; the recovery path then receives no file-record metadata and passes that absent result to packaging logic, which raises a type error instead of reporting the damaged or missing installation.
