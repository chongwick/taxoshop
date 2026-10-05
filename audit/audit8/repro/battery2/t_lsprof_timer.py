# HUNT: _lsprof external timer runs arbitrary Python (CallExternalTimer, borrowed
# pObj->externalTimer, not INCREF'd). disable()/clear() are guarded by POF_EXT_TIMER, but
# __init__ (profiler_init) and enable() are NOT. profiler_init does
# Py_XSETREF(self->externalTimer, new) -> can free the currently-running timer callable, and
# generally corrupt profiler state mid-callback.
import _lsprof, sys

def variant(label, build_timer, action):
    prof = _lsprof.Profiler()
    prof.__init__(timer=build_timer(prof))
    try:
        prof.enable()
        def foo():
            return 1
        for _ in range(20):
            foo()
        prof.disable()
        print(f"  {label}: ok (no crash)")
    except Exception as ex:
        try: prof.disable()
        except Exception: pass
        print(f"  {label}: raised {type(ex).__name__}: {ex}")

# A: timer re-inits the profiler with a fresh throwaway timer -> drops the running timer's
#    last ref (it's only referenced by prof.externalTimer).
def buildA(prof):
    def evil():
        try: prof.__init__(timer=lambda: 0)
        except Exception: pass
        return 0
    return evil
variant("A timer->__init__(new)", buildA, None)

# B: timer calls enable() reentrantly (unguarded)
def buildB(prof):
    def evil():
        try: prof.enable()
        except Exception: pass
        return 0
    return evil
variant("B timer->enable", buildB, None)

# C: timer calls disable() (should be guarded -> RuntimeError)
def buildC(prof):
    def evil():
        try: prof.disable()
        except Exception: pass
        return 0
    return evil
variant("C timer->disable", buildC, None)

# D: timer calls clear() (should be guarded -> RuntimeError)
def buildD(prof):
    def evil():
        try: prof.clear()
        except Exception: pass
        return 0
    return evil
variant("D timer->clear", buildD, None)

# E: timer re-inits with NO timer (removes external timer mid-call)
def buildE(prof):
    def evil():
        try: prof.__init__()  # externalTimer -> NULL
        except Exception: pass
        return 0
    return evil
variant("E timer->__init__() no timer", buildE, None)

print("lsprof_timer done")
