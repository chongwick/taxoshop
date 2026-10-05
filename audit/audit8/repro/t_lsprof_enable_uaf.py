# NEW BUG: heap-use-after-free in _lsprof (the cProfile C accelerator).
#
# _lsprof's external timer runs arbitrary Python (CallExternalTimer). Profiler.disable() and
# Profiler.clear() refuse to run while the timer is executing (they check the POF_EXT_TIMER
# flag), but Profiler.enable() has NO such guard. Calling enable() from inside the timer, while
# the profiler is active, re-registers the sys.monitoring callbacks and corrupts the
# ProfilerContext chain/freelist that ptrace_enter_call / Stop / flush_unmatched manage.
# A subsequent disable() then frees a ProfilerContext that is still referenced -> heap-UAF.
#
# Pure Python, no ctypes. ASan: heap-use-after-free at Modules/_lsprof.c:383 (ptrace_enter_call);
# on a normal build: "malloc(): unaligned tcache chunk detected" / abort.
import _lsprof

prof = _lsprof.Profiler()

def evil_timer():
    try:
        prof.enable()          # reentrant, UNGUARDED (unlike disable()/clear())
    except Exception:
        pass
    return 0

prof.__init__(timer=evil_timer)
prof.enable()

def foo():
    return 1

foo()                          # one profiled call: timer fires -> enable() corrupts state
prof.disable()                 # frees a still-referenced ProfilerContext -> use-after-free
print("no crash")
