# 0091 OOM error-path sweep. For each target, fail the k-th allocation after arming and
# run the op; a clean MemoryError is good, an ASan abort (double-free/UAF) is the bug.
import sys, gc, _testcapi

def arm(k):
    _testcapi.set_nomemory(k, k+1)
def disarm():
    _testcapi.remove_mem_hooks()

def sweep(name, fn, kmax=60):
    for k in range(kmax):
        gc.collect()
        arm(k)
        try:
            fn()
        except MemoryError:
            pass
        except Exception as e:
            pass
        finally:
            disarm()
    print(f"  {name}: swept k=0..{kmax-1} clean")

# ---- targets ----
def t_getnameinfo():
    import socket
    try: socket.getnameinfo(("127.0.0.1", 80), 0)
    except OSError: pass

def t_time_fromiso():
    import datetime
    for s in ("00:00:00.500000+10:00", "12:34:56.123456+05:30:15", "23:59:59+23:59"):
        try: datetime.time.fromisoformat(s)
        except ValueError: pass

def t_date_fromiso():
    import datetime
    for s in ("2023-01-01T00:00:00.500000+10:00","2024-12-31T23:59:59.999999-05:00"):
        try: datetime.datetime.fromisoformat(s)
        except ValueError: pass

def t_pickle_reduce():
    import pickle, io
    class Ev:
        def __reduce__(self):
            return (list, (), {'a':1}, iter([1,2,3]), iter([('k','v')]))
    try: pickle.dumps(Ev())
    except Exception: pass

def t_csv_writerow():
    import csv, io
    w = csv.writer(io.StringIO())
    try: w.writerow(["aaaa","bbbb",12345,"cccc"*20,object()])
    except Exception: pass

def t_getgrouplist():
    import os
    try: os.getgrouplist("root", 0)
    except Exception: pass

def t_sched_aff():
    import os
    try: os.sched_getaffinity(0)
    except Exception: pass

def t_groupby():
    import itertools
    try:
        g = itertools.groupby([1,1,2,3,3], key=lambda x: x)
        list(g)
    except Exception: pass

def t_et_deepcopy():
    import xml.etree.ElementTree as ET, copy
    e = ET.Element("root")
    for i in range(10):
        c = ET.SubElement(e, f"c{i}"); c.text = "t"*10; c.set("a","v")
    try: copy.deepcopy(e)
    except Exception: pass

def t_json_default_circular():
    import json
    def default(o):
        l = []; l.append(l); return l
    class Bad: pass
    try: json.dumps(Bad(), default=default)
    except Exception: pass

TARGETS = {
    "getnameinfo": t_getnameinfo,
    "time_fromiso": t_time_fromiso,
    "date_fromiso": t_date_fromiso,
    "pickle_reduce": t_pickle_reduce,
    "csv_writerow": t_csv_writerow,
    "getgrouplist": t_getgrouplist,
    "sched_aff": t_sched_aff,
    "groupby": t_groupby,
    "et_deepcopy": t_et_deepcopy,
    "json_default_circular": t_json_default_circular,
}

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for name, fn in TARGETS.items():
        if only and name != only: continue
        print(f"[target] {name}", flush=True)
        sweep(name, fn)
    print("ALL DONE")
