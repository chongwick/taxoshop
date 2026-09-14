# float->int/time_t cast overflow probes (workflow-0010)
import time, datetime, os
BIG = [1e300, -1e300, float('inf'), float('-inf'), float('nan'), 1e19, 2.0**63, -(2.0**63)-1e5]
def tryall(fn, label):
    for v in BIG:
        try:
            fn(v)
        except (OverflowError, ValueError, OSError, TypeError) as e:
            pass
        except Exception as e:
            print(label, type(e).__name__, e)
tryall(lambda v: time.gmtime(v), "time.gmtime")
tryall(lambda v: time.localtime(v), "time.localtime")
tryall(lambda v: time.ctime(v), "time.ctime")
tryall(lambda v: time.sleep(v), "time.sleep")
tryall(lambda v: datetime.datetime.fromtimestamp(v, datetime.timezone.utc), "dt.fromtimestamp")
tryall(lambda v: datetime.date.fromtimestamp(v), "date.fromtimestamp")
print("done float_time")
