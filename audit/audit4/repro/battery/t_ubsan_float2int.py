import sys
tests = []
def T(name, fn):
    tests.append((name, fn))

import time, datetime, select, socket, os, math
T("time.sleep_huge", lambda: time.sleep(1e300))
T("time.gmtime_huge", lambda: time.gmtime(1e300))
T("time.localtime_huge", lambda: time.localtime(1e300))
T("time.ctime_huge", lambda: time.ctime(1e300))
T("datetime.fromtimestamp", lambda: datetime.datetime.fromtimestamp(1e300))
T("date.fromtimestamp", lambda: datetime.date.fromtimestamp(1e300))
T("select_timeout", lambda: select.select([],[],[], 1e300))
T("socket_settimeout", lambda: socket.socket().settimeout(1e300))
T("math.factorial_neg", lambda: None)
T("time.strftime_huge", lambda: time.strftime("%Y", time.gmtime(0)))
for name, fn in tests:
    try:
        fn()
        print(name, "-> no error/exc")
    except (OverflowError, ValueError, OSError) as e:
        print(name, "->", type(e).__name__)
    except Exception as e:
        print(name, "-> other", type(e).__name__, e)
