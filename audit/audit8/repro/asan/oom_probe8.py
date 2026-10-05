# 0091 OOM error-path probe for audit8's new targets. Sweep set_nomemory(k, k+1) over each
# op; a MemoryError is clean. An ASan double-free/UAF/heap-corruption abort is the finding.
# NO ctypes.
import _testcapi, sys, io, struct, json, os

def sweep(name, fn, kmax=80):
    for k in range(kmax):
        _testcapi.set_nomemory(k, k+1)
        try:
            fn()
        except MemoryError:
            pass
        except Exception as e:
            # non-MemoryError exceptions are fine too (validation errors)
            pass
        finally:
            _testcapi.remove_mem_hooks()
    print(f"  {name}: swept {kmax} clean")

# S2 struct.unpack — many field types in one format
def op_struct():
    s = struct.Struct("<iqd10sHbf?")
    buf = s.pack(1, 2, 3.0, b"0123456789", 5, -1, 2.5, True)
    struct.Struct("<iqd10sHbf?").unpack(buf)
sweep("S2 struct.unpack", op_struct)

# S5 _json parse object (truncated + full)
def op_json():
    try: json.loads('{"a":1,"b":2,"c":[1,2,3],"d":{"e":4}}')
    except Exception: pass
    try: json.loads('{"a":1,"b":')
    except Exception: pass
sweep("S5 json.loads", op_json)

# S4 itertools.product ctor
import itertools
def op_product():
    list(itertools.product([1,2,3],[4,5],[6,7,8]))
sweep("S4 itertools.product", op_product)

# S9 os.getgroups
def op_getgroups():
    os.getgroups()
sweep("S9 os.getgroups", op_getgroups)

# S1 grp.getgrall (if available)
try:
    import grp
    def op_getgrall():
        grp.getgrall()
    sweep("S1 grp.getgrall", op_getgrall, kmax=120)
except Exception as e:
    print("  S1 grp: skipped", e)

# S3 zoneinfo load from file (crafted minimal TZif via from_file)
def op_zoneinfo():
    import zoneinfo
    # Use a real tz if present
    try:
        zoneinfo.ZoneInfo("UTC")
    except Exception:
        pass
sweep("S3 zoneinfo", op_zoneinfo)

# extra: struct.unpack_from and iter_unpack
def op_struct2():
    s = struct.Struct(">5i")
    b = s.pack(1,2,3,4,5)
    list(s.iter_unpack(b*3))
sweep("struct.iter_unpack", op_struct2)

print("oom_probe8 done")
