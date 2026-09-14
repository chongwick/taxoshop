# float->int cast probes across misc C modules (workflow-0010)
import math, os, select, socket
BIG = [1e300, -1e300, float('inf'), float('-inf'), float('nan'), 2.0**63, 1e19]
def tryall(fn, label):
    for v in BIG:
        try: fn(v)
        except (OverflowError, ValueError, OSError, TypeError) as e: pass
        except Exception as e: print(label, type(e).__name__, e)
tryall(lambda v: math.ldexp(1.0, int(v)) if v==v and abs(v)<1e18 else 0, "ldexp")
tryall(lambda v: math.factorial(v) if v==v else 0, "factorial")
tryall(lambda v: round(1.0, v) if v==v and abs(v)<1e18 else 0, "round-ndigits")
tryall(lambda v: os.lseek(0, int(v), 0) if v==v and abs(v)<1e18 else 0, "lseek")
tryall(lambda v: select.select([],[],[],v), "select.timeout")
# chr / int-ish
tryall(lambda v: __import__('time').strftime("%Y", __import__('time').gmtime(0)), "strftime")
print("done float_misc")
