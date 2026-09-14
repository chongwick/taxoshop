import _testcapi, sys
op = sys.argv[1]; k = int(sys.argv[2])

def make_op(name):
    if name == "getaddrinfo":
        import socket
        return lambda: socket.getaddrinfo("localhost", 80, proto=socket.IPPROTO_TCP)
    if name == "pickle_loads":
        import pickle
        blob = pickle.dumps({"a":[1,2,3],"b":(4,5,{"c":6}),"d":"e"*20,"f":list(range(30))})
        return lambda: pickle.loads(blob)
    if name == "pyexpat":
        import xml.parsers.expat as x
        def go():
            p = x.ParserCreate()
            p.Parse("<r a='1' b='2'><c>text</c><d/></r>", True)
        return go
    if name == "et_fromstring":
        import xml.etree.ElementTree as ET
        return lambda: ET.fromstring("<r a='1'><c>t</c><d>u</d><e/></r>")
    if name == "zoneinfo_ff":
        import zoneinfo, io
        blob = open("/usr/share/zoneinfo/UTC","rb").read()
        return lambda: zoneinfo.ZoneInfo.from_file(io.BytesIO(blob))
    if name == "interp_queue":
        import _interpqueues as q
        import _interpreters  # register shareables
        qid = q.create(2, 0, 0) if False else q.create()
        return lambda: (q.put(qid, b"hello", 0, 0), q.get(qid))
    if name == "excgroup":
        return lambda: ExceptionGroup("g", [ValueError("x"), TypeError("y"), KeyError("z")])
    if name == "str_format":
        return lambda: "{0!r:>{1}}-{2:.3f}-{3}".format([1,2,3], 10, 3.14159, {"a":1})
    if name == "list_sort_key":
        return lambda: sorted([3,1,2,5,4]*6, key=lambda x: (x, -x, str(x)))
    if name == "dict_update":
        return lambda: dict(zip(range(30), range(30)))
    if name == "bytes_decode_utf8":
        return lambda: (b"caf\xc3\xa9 \xe2\x9c\x93 stuff"*4).decode("utf-8")
    if name == "codecs_incr":
        import codecs
        def go():
            d = codecs.getincrementaldecoder("utf-8")()
            d.decode(b"caf\xc3"); d.decode(b"\xa9 test", True)
        return go
    if name == "traceback_fmt":
        import traceback
        def go():
            try:
                def a(): 1/0
                a()
            except Exception:
                traceback.format_exc()
        return go
    raise SystemExit("unknown")

fn = make_op(op)
for _ in range(3):
    try: fn()
    except Exception: pass
_testcapi.set_nomemory(k, k+1)
try:
    fn(); print("OK k=%d"%k)
except MemoryError: print("MemoryError k=%d"%k)
except Exception as e: print("EXC k=%d %s"%(k, type(e).__name__))
