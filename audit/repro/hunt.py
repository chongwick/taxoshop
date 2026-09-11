"""Focused malformed/boundary-input hunt on under-covered C decoder surfaces.

Targets the sanitizer checks still active under -fno-strict-overflow:
alignment, array-bounds, nonnull-memcpy, float-cast-overflow. Each block feeds
boundary/malformed data into a native code path predicted by a macro pattern.
Runs everything in one process with halt_on_error=0 so all findings surface.
Any real finding prints as a UBSan 'runtime error' / ASan 'ERROR' line.
"""
import os, sys, random, struct, itertools

random.seed(1234)

def banner(x):
    print(f"---- {x} ----", flush=True)

def hunt_binascii():
    # wf-0032 / wf-0155: malformed compact encodings into C decoders.
    import binascii
    fns = []
    for name in ('a2b_base64','a2b_qp','a2b_hqx','rledecode_hqx','a2b_uu','unhexlify'):
        fns.append(getattr(binascii, name, None))
    for _ in range(20000):
        n = random.randint(0, 40)
        data = bytes(random.getrandbits(8) for _ in range(n))
        for fn in fns:
            if fn is None:
                continue
            try:
                try:
                    fn(data, strict_mode=random.choice([True, False]))
                except TypeError:
                    fn(data)
            except Exception:
                pass

def hunt_struct():
    # wf-0007 alignment / wf-0022 width: unusual formats + buffers.
    fmts = ['e','f','d','h','H','i','I','q','Q','b','B','?','P','n','N']
    for _ in range(20000):
        f = '<' + ''.join(random.choice(fmts) for _ in range(random.randint(0,4)))
        try:
            sz = struct.calcsize(f)
        except Exception:
            continue
        buf = bytes(random.getrandbits(8) for _ in range(sz))
        try:
            struct.unpack(f, buf)
        except Exception:
            pass
        # unpack_from at odd offsets to probe alignment casts
        big = bytes(random.getrandbits(8) for _ in range(sz + 8))
        for off in range(0, 8):
            try:
                struct.unpack_from(f, big, off)
            except Exception:
                pass

def hunt_float_cast():
    # wf-0010 float-cast-overflow: extreme doubles into C narrowing.
    import math, time, datetime
    extremes = [1e308, -1e308, 1e300*1e300, float('nan'), 2.0**63, 2.0**64,
                -2.0**63-1, 1e39, 3.5e38, -3.5e38, 65520.0, 1e16, 9.3e18]
    for v in extremes:
        for fn in (round, math.floor, math.ceil, math.trunc):
            try: fn(v)
            except Exception: pass
        for pk in ('e','f','d'):
            try: struct.pack('<'+pk, v)
            except Exception: pass
        try: datetime.datetime.fromtimestamp(v)
        except Exception: pass
        try: datetime.timedelta(seconds=v)
        except Exception: pass

def hunt_datetime_iso():
    # wf-0155: boundary timestamp/ISO parsing.
    import datetime
    seeds = ['0000-00-00','9999-99-99T99:99:99','1-1-1','2020-01-01T00:00:00.'+ '9'*400,
             '2020-W01-1','2020-001','+0100000000-01-01', '2020-01-01T24:00:00',
             '2020-01-01T00:00:00+99:99', '\x00'*8, '2020-01-01T00:00:00,'+'0'*300]
    for s in seeds:
        for ctor in (datetime.datetime.fromisoformat, datetime.date.fromisoformat,
                     datetime.time.fromisoformat):
            try: ctor(s)
            except Exception: pass

def hunt_memoryview_cast():
    # wf-0007 alignment / wf-0136: cast/reshape on odd-sized buffers.
    for n in range(0, 40):
        b = bytearray(n)
        mv = memoryview(b)
        for fmt in ('b','h','i','l','q','f','d'):
            try:
                mv.cast(fmt)
            except Exception:
                pass
        try:
            mv.cast('b', shape=[n])
        except Exception:
            pass

def hunt_json():
    # wf-0032/wf-0036: malformed JSON into C scanner (boundary lookahead).
    import json
    seeds = ['[', '{', '"\\u', '"\\ud800', '[1,', '1e', '-', '"\\', 'NaN',
             '﻿{}', '"'+'\\uffff'*300, '[]'*0]
    for s in seeds:
        for _ in range(3):
            try: json.loads(s)
            except Exception: pass
    # random fuzz
    alph = '{}[]",:0123456789.eE+-tfnul \\/u'
    for _ in range(30000):
        s = ''.join(random.choice(alph) for _ in range(random.randint(0, 30)))
        try: json.loads(s)
        except Exception: pass

def hunt_codecs_incremental():
    # wf-0105/wf-0121: incremental decoders + error handlers on split bytes.
    import codecs
    encs = ['utf-8','utf-16','utf-32','utf-7','utf-16-le','utf-16-be',
            'shift_jis','big5','gb18030','euc-jp','iso2022_jp','cp932','hz']
    errs = ['strict','replace','ignore','backslashreplace','surrogatepass','surrogateescape']
    for enc in encs:
        try:
            dec = codecs.getincrementaldecoder(enc)
        except Exception:
            continue
        for _ in range(3000):
            d = dec(random.choice(errs))
            data = bytes(random.getrandbits(8) for _ in range(random.randint(0,6)))
            try:
                d.decode(data, False)
                d.decode(b'', True)
            except Exception:
                pass

def hunt_array():
    # wf-0005/wf-0136: array frombytes/typecode edges, empty transfers.
    import array
    for tc in 'bBuwhHiIlLqQfd':
        try:
            a = array.array(tc)
        except Exception:
            continue
        for n in range(0, 20):
            data = bytes(random.getrandbits(8) for _ in range(n))
            try:
                a.frombytes(data)
            except Exception:
                pass
            try:
                (a + array.array(tc)).tobytes()
            except Exception:
                pass

HUNTS = {k[5:]: v for k, v in globals().items() if k.startswith('hunt_')}

if __name__ == '__main__':
    names = sys.argv[1:] or list(HUNTS)
    for name in names:
        banner(name)
        try:
            HUNTS[name]()
        except Exception as e:
            print(f"  (hunt {name} raised {type(e).__name__}: {e})", flush=True)
    print("ALL HUNTS COMPLETED", flush=True)
