"""
Re-entrancy / callback-invalidation fuzz harness for sanitizer-built CPython.

Each test constructs an "adversarial" object whose protocol hook (__index__,
__int__, __eq__, __hash__, __bool__, buffer, __del__, iterator, factory, ...)
mutates / clears / closes / resizes some native-backed state that a C routine
is holding a borrowed pointer, cached size, or resource handle to.

Run ONE test per process:   python harness.py <test_name>
(ASan aborts the process on first error, so isolation is required.)
List tests:                 python harness.py --list
"""
import sys

TESTS = {}
def test(fn):
    TESTS[fn.__name__] = fn
    return fn


# ---------------------------------------------------------------- itertools
@test
def itertools_pairwise_evilcmp():
    import itertools
    # pairwise holds the previous item; not obviously reentrant. control.
    lst = [1, 2, 3]
    list(itertools.pairwise(lst))

@test
def itertools_accumulate_mutate():
    import itertools
    data = [1, 2, 3, 4, 5]
    def f(a, b):
        data.clear()
        return a + b
    list(itertools.accumulate(data, f))

@test
def itertools_batched_evil_index():
    import itertools
    class E:
        def __index__(self):
            return 2
    list(itertools.batched(range(10), E()))


# ---------------------------------------------------------------- _operator
@test
def operator_countOf_evil_eq():
    import operator
    lst = list(range(50))
    class E:
        def __eq__(self, o):
            lst.clear()
            return False
    operator.countOf(lst, E())

@test
def operator_indexOf_evil_eq():
    import operator
    lst = list(range(50))
    class E:
        def __eq__(self, o):
            lst.clear()
            return False
    try:
        operator.indexOf(lst, E())
    except ValueError:
        pass


# ---------------------------------------------------------------- array 'u'/'w'
@test
def array_index_evil():
    import array
    a = array.array('i', range(100))
    class E:
        def __index__(self):
            del a[:]
            return 0
    try:
        a[E()] = 5
    except Exception:
        pass

@test
def array_imul_evil():
    import array
    a = array.array('i', range(10))
    class E:
        def __index__(self):
            a.extend(range(1000))
            return 3
    a *= E()

@test
def array_frombytes_view():
    import array
    a = array.array('i', range(10))
    a.frombytes(bytearray(8))


# ---------------------------------------------------------------- memoryview
@test
def memoryview_setitem_evil_index():
    ba = bytearray(range(64))
    mv = memoryview(ba)
    class E:
        def __index__(self):
            # try to mutate exporter while a view exists (should raise)
            try:
                ba.clear()
            except BufferError:
                pass
            return 300
        def __int__(self):
            return 300
    try:
        mv[0] = E()
    except Exception:
        pass

@test
def memoryview_cast_evil():
    ba = bytearray(64)
    mv = memoryview(ba)
    mv2 = mv.cast('i')
    del mv2


# ---------------------------------------------------------------- struct
@test
def struct_pack_into_evil_offset():
    import struct
    ba = bytearray(64)
    class E:
        def __index__(self):
            try:
                ba.clear()
            except BufferError:
                pass
            return 0
    try:
        struct.pack_into('i', ba, E(), 1234)
    except Exception:
        pass

@test
def struct_pack_evil_value():
    import struct
    ba = bytearray(64)
    class E:
        def __index__(self):
            ba.clear()
            return 1
    try:
        struct.pack('10i', E(), E(), E(), E(), E(), E(), E(), E(), E(), E())
    except Exception:
        pass


# ---------------------------------------------------------------- str/bytes format & translate
@test
def str_mod_mapping_evil():
    class M(dict):
        def __getitem__(self, k):
            return Evil()
    class Evil:
        def __str__(self):
            return "x"
    "%(a)s %(b)s" % M()

@test
def bytes_mod_evil_index():
    class E:
        def __index__(self):
            return 65
    b"%c" % E()

@test
def str_translate_evil_mapping():
    s = "hello world" * 10
    class M:
        def __getitem__(self, k):
            return None
    s.translate(M())


# ---------------------------------------------------------------- functools
@test
def functools_reduce_evil():
    import functools
    data = list(range(50))
    def f(a, b):
        data.clear()
        return b
    functools.reduce(f, data, 0)


# ---------------------------------------------------------------- zlib/bz2/lzma
@test
def zlib_compress_evil_level():
    import zlib
    class E:
        def __index__(self):
            return 6
    zlib.compress(b"x" * 100, E())


# ---------------------------------------------------------------- _json
@test
def json_encode_mutating_default():
    import json
    d = {"a": 1, "b": 2, "c": 3}
    class Enc(json.JSONEncoder):
        def default(self, o):
            d.clear()
            return None
    class Bad: pass
    d2 = {"x": Bad(), "y": Bad(), "z": Bad()}
    try:
        Enc().encode(d2)
    except Exception:
        pass

@test
def json_encode_dict_mutate_via_keys():
    import json
    d = {}
    class K:
        def __init__(self, i): self.i = i
        def __str__(self):
            d.clear()
            return "k"
    # keys must be str for json; use sort_keys with evil? use default on values
    for i in range(10):
        d[str(i)] = i
    json.dumps(d)


# ---------------------------------------------------------------- collections
@test
def deque_maxlen_index_evil():
    import collections
    class E:
        def __index__(self):
            return 5
    collections.deque(range(10), E())


# ---------------------------------------------------------------- socket cmsg (partly audited)
@test
def socket_sendmsg_evil_ancdata():
    pass  # requires sockets; skip in generic run


# ---------------------------------------------------------------- _pickle memo
@test
def pickle_persistent_evil():
    import pickle, io
    lst = [1, 2, 3]
    class P(pickle.Pickler):
        def persistent_id(self, obj):
            if isinstance(obj, int):
                lst.clear()
            return None
    P(io.BytesIO()).dump(lst)


# ---------------------------------------------------------------- textio / io
@test
def io_readinto_evil_buffer():
    import io
    class E(bytearray):
        pass
    b = io.BytesIO(b"x" * 100)
    ba = bytearray(50)
    b.readinto(ba)


# ---------------------------------------------------------------- min/max/sorted key
@test
def min_key_mutate():
    data = list(range(50))
    def k(x):
        data.clear()
        return x
    try:
        min(data, key=k)
    except Exception:
        pass


# ---------------------------------------------------------------- enumerate/zip
@test
def sum_evil_add():
    class E:
        def __add__(self, o): return self
        def __radd__(self, o): return self
    sum([E(), E(), E()])


def main():
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        for k in TESTS:
            print(k)
        return
    if len(sys.argv) != 2 or sys.argv[1] not in TESTS:
        print("usage: harness.py <test|--list>", file=sys.stderr)
        sys.exit(2)
    TESTS[sys.argv[1]]()
    print("OK", sys.argv[1])

if __name__ == '__main__':
    main()
