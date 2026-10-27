# Server endpoint setup assumes unrestricted address discovery returns a usable protocol family, so a disabled family can be selected and passed to socket binding

A server setup uses address discovery without constraining results to protocol families supported by the runtime, then attempts to bind using the selected result.

## Precondition

The environment disables or lacks support for a network protocol family, while endpoint discovery can still report addresses belonging to that family.

## Critical operation

Server initialization performs unrestricted endpoint discovery and uses a discovered result's protocol family to create and bind the listening socket.

## Interference

Discovery returns an endpoint in the disabled or unsupported family, potentially as the selected result.

## Invalid assumption

Every discovered endpoint family is supported by the runtime and is safe to use for binding.

## Failure

Socket creation or binding fails with a low-level unsupported-family error instead of selecting a supported endpoint or reporting a controlled configuration condition.

## Scope

This is a singleton cluster, so the pattern is scoped to server/listener setup paths where address discovery may expose protocol families unavailable in the running environment; it does not establish behavior for client connection retries or other discovery consumers.

## Search strategy

1. Check endpoint-discovery calls used for server binding and verify that the requested family is constrained to runtime-supported families.
2. Check code that selects the first or otherwise preferred discovery result and verify it filters out unsupported protocol families before socket creation.
3. Check protocol-family capability flags and build-time feature switches against all server setup paths that create and bind sockets.
4. Check binding error handling to ensure unsupported-family results are skipped or converted into an intentional, actionable failure.

## Evidence

- [#121275](../micro_taxo/gh_121275.md): A server test setup on a build without IPv6 support used address discovery that still returned an IPv6 result, selected its family for socket creation, and then failed during binding with a bad-family error; the fix constrained discovery to IPv4 when IPv6 was unavailable.
