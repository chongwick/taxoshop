# wf0080 Site 9: cProfile with evil timer that clears profiler state mid-profile
import cProfile
state = {"n": 0}
prof = None
def evil_timer():
    state["n"] += 1
    if state["n"] == 3 and prof is not None:
        try: prof.clear()
        except Exception: pass
    return float(state["n"])
prof = cProfile.Profile(timer=evil_timer)
def work():
    s = 0
    for i in range(50):
        s += i
    return s
try:
    prof.enable()
    work(); work(); work()
    prof.disable()
    prof.print_stats()
except Exception as e:
    print("lsprof", type(e).__name__, e)
print("lsprof done")
