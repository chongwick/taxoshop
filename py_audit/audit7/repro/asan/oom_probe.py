# Systematic OOM error-path probe: for a given operation, fail the k-th allocation
# (for k in a range) and report if it CRASHES (ASan) rather than raising MemoryError.
# Runs one k per process (caller loops k) so an ASan abort is attributable.
import _testcapi, sys

op = sys.argv[1]
k = int(sys.argv[2])

def make_op(name):
    if name == "partial":
        import functools
        return lambda: functools.partial(len, [1,2,3], key=1)
    if name == "re_compile":
        import re
        return lambda: re.compile(r"(a)(b)(c)+d[e-f]{2,3}|xyz")
    if name == "struct":
        import struct
        return lambda: struct.Struct("3sHiq10sf")
    if name == "encode_idna":
        return lambda: "xn--test".encode("idna") if False else "münchen".encode("idna")
    if name == "json_dumps":
        import json
        return lambda: json.dumps({"a":[1,2,3],"b":{"c":"d"},"e":[{"f":1}]*3})
    if name == "json_loads":
        import json
        return lambda: json.loads('{"a":[1,2,3],"b":{"c":"d"},"e":[1.5,2.5]}')
    if name == "fromisoformat":
        import datetime
        return lambda: datetime.datetime.fromisoformat("2020-01-02T03:04:05.678+09:30")
    if name == "namedtuple":
        import collections
        return lambda: collections.namedtuple("P", ["x","y","z"])
    if name == "zoneinfo_file":
        import zoneinfo, io
        # minimal valid TZif v1
        data = (b"TZif\x00" + b"\x00"*15 + b"\x00\x00\x00\x00"*3 +
                b"\x00\x00\x00\x00"  # isutcnt/... zeros
                )
        return lambda: None
    if name == "textwrap":
        import textwrap
        return lambda: textwrap.wrap("the quick brown fox "*5, width=13)
    if name == "csv_reader":
        import csv, io
        return lambda: list(csv.reader(io.StringIO("a,b,c\n1,2,3\n4,5,6\n")))
    raise SystemExit("unknown op")

fn = make_op(op)
# warm up (import/allocate caches) BEFORE arming, so we only fail op-internal allocs
for _ in range(3):
    try: fn()
    except Exception: pass

_testcapi.set_nomemory(k, k+1)   # fail exactly the k-th allocation from now
try:
    fn()
    print("OK k=%d (no fail hit)" % k)
except MemoryError:
    print("MemoryError k=%d (clean)" % k)
except Exception as e:
    print("EXC k=%d %s: %s" % (k, type(e).__name__, e))
