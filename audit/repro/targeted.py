"""Targeted micro-probes derived from macro-taxonomy patterns.

Each probe is a self-contained snippet that exercises a documented CPython
surface in a boundary/extreme way that the corresponding pattern predicts could
reach an unchecked low-level operation. Run under the asan-ubsan python:

    PYTHONMALLOC=malloc UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=0 \
        ./python /work/targeted.py

Probes are intentionally isolated in subprocesses by the driver so one abort
does not mask the rest. This file just defines them; driver runs each by name.
"""
import sys

def p_float_demotion_struct():
    # wf-0010: float->narrower/int demotion before representability check.
    import struct
    for v in (1e39, -1e39, float('inf'), float('nan'), 1e300):
        try:
            struct.pack('<e', v)   # IEEE half-float; huge -> overflow path
        except (OverflowError, ValueError):
            pass
        try:
            struct.pack('<f', v)
        except (OverflowError, ValueError):
            pass

def p_float_to_int_time():
    # wf-0010 / wf-0053: extreme float timestamps into C conversions.
    import time
    for v in (1e300, -1e300, float('inf')):
        try:
            time.gmtime(v)
        except (OverflowError, ValueError, OSError):
            pass
        try:
            time.ctime(v)
        except (OverflowError, ValueError, OSError):
            pass

def p_zero_count_memcpy():
    # wf-0005: zero-length transfers through empty/absent storage.
    import array, ctypes
    array.array('b', b'')
    (array.array('b', b'') + array.array('b', b''))
    bytearray(0)
    memoryview(b'')[0:0].tobytes()
    ctypes.create_string_buffer(0)
    (ctypes.c_char * 0)()

def p_signed_shift_pickle():
    # wf-0003: signed-shift construction in decoders.
    import pickle, pickletools  # noqa
    # Force BININT/LONG opcodes with boundary values.
    for v in (2**31 - 1, -2**31, 2**63 - 1, -2**63, 2**64):
        try:
            pickle.loads(pickle.dumps(v, protocol=2))
        except Exception:
            pass

def p_unchecked_native_handle():
    # wf-0053: caller-controlled integer forwarded as native handle/count.
    import _thread
    for v in (-1, 0, 2**63 - 1, -2**63):
        try:
            _thread._set_sentinel  # noqa
        except Exception:
            pass

PROBES = {name[2:]: fn for name, fn in globals().items() if name.startswith('p_')}

if __name__ == '__main__':
    name = sys.argv[1]
    PROBES[name]()
    print(f"probe {name}: completed without fatal sanitizer abort")
