# Instrumented capability probes can hang during platform/runtime startup before application code executes.

A build-time probe is synchronously executed with memory-safety instrumentation enabled. On some platform/toolchain/runtime combinations, instrumentation startup conflicts with dynamic-loader or allocator initialization and spins indefinitely before the probe reaches its application logic. The configuration driver therefore waits forever instead of observing a normal probe result.

## Precondition

The configuration process compiles and runs a generated capability-test executable with memory-safety instrumentation on a platform/toolchain combination whose runtime startup path may be incompatible with system loader or allocator initialization.

## Critical operation

The configuration process synchronously launches the instrumented probe and waits for it to terminate so it can determine the capability result.

## Interference

The instrumentation runtime initializes before the executable's application entry point and enters an incompatible shadow-memory or allocator startup path that does not complete.

## Invalid assumption

The probe will reach its application code and either succeed, fail, or exit promptly, making synchronous execution safe for configuration detection.

## Failure

The probe consumes CPU or remains stuck during process initialization, causing the configuration step to hang indefinitely rather than report a probe failure or continue.

## Scope

This is a singleton cluster. The evidence establishes the pattern for one sanitizer-enabled configuration probe on one macOS environment; it does not establish that all instrumented probes or platforms exhibit the behavior.

## Search strategy

1. Inspect configure-time capability checks for generated executables built with sanitizers or other instrumentation and executed synchronously.
2. Trace instrumented probe startup before the application entry point, including dynamic-loader, allocator, shadow-memory, and runtime-constructor initialization.
3. Check whether probe execution has a timeout or an isolated failure path for runtimes that can hang before application code begins.
4. Review platform- and toolchain-specific instrumentation settings for incompatibilities with system startup or memory-allocation initialization.

## Evidence

- [#145199](../micro_taxo/gh_145199.md): A generated configuration probe consumed CPU without reaching its entry point. The stack was in instrumentation, allocator, loader, and system initialization, supporting a platform-dependent startup hang that leaves the synchronous configuration driver waiting.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0151](../macro_taxo_before_hybrid/workflow-0151.md)
