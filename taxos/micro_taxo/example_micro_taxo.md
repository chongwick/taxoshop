# Micro Taxonomy: CPython #143545

## Metadata
- Issue: https://github.com/python/cpython/issues/143545
- Component: `Modules/_lsprof.c`
- Bug class: use-after-free
- Detection: ASAN

## Root Cause
`ProfilerContext` remains referenced by the active C frame while
`call_timer()` executes Python-controlled code. Re-entrant Python calls
`prof.clear()`, which frees the active context. Execution then returns
to the original C frame, which continues accessing the freed context.

## Trigger
1. Profiler installs/uses a `ProfilerContext`.
2. External timer is called.
3. Timer result invokes user-controlled `__index__`.
4. `__index__` calls `prof.clear()`.
5. `clearEntries()` frees `currentProfilerContext`.
6. `initContext()` or `Stop()` resumes and accesses the freed context.

## Relevant State
- Owner: `ProfilerObject`
- Invalidated state: `ProfilerContext`
- Owner field: `currentProfilerContext`
- Retained alias: local `ProfilerContext *self`

## Re-entrancy Boundary
- `call_timer()`
- `_PyTime_FromSecondsObject()`
- user-controlled `__index__`

## Invalidating Operation
- `Profiler.clear()`
- `clearEntries()`
- `PyMem_Free(currentProfilerContext)`

## Stale Use
- `initContext()`
- `Stop()`

## Fix
Prevent `clearEntries()` from freeing profiler state while the timer
callback is active using an `inCallback` re-entrancy guard.

## Pattern Tags
- reentrancy
- callback
- user-controlled-protocol
- state-invalidation
- raw-pointer-lifetime
- owner-local-alias
- use-after-free
