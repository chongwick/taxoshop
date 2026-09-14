# evil-object reentrancy: __index__/__eq__/__float__ that resize/clear the target
# buffer mid-operation. If a site caches a raw pointer without bumping exports,
# ASan should catch heap-UAF/OOB. (workflow-0137/0080/0014)
import struct, array, io

def evil_index(action):
    class E:
        def __index__(self):
            action(); return 0
        def __int__(self):
            action(); return 0
    return E()

def evil_float(action):
    class E:
        def __float__(self):
            action(); return 0.0
        def __index__(self):
            action(); return 0
    return E()

def run(label, fn):
    try: fn()
    except (BufferError, TypeError, ValueError, IndexError, struct.error) as e: pass
    except Exception as e: print(label, type(e).__name__, e)

# 1) struct.pack_into into a bytearray; evil arg resizes that bytearray
for fmt, ev in [("<i", evil_index), ("<d", evil_float), ("<q", evil_index), ("<B", evil_index)]:
    ba = bytearray(64)
    run(f"pack_into {fmt}", lambda ba=ba, fmt=fmt, ev=ev: struct.pack_into(fmt, ba, 0,
        ev(lambda: ba.clear())))

# 2) struct.pack_into offset is evil and clears the target buffer
ba = bytearray(64)
run("pack_into evil-offset", lambda: struct.pack_into("<i", ba, evil_index(lambda: ba.clear()), 1))

# 3) array slice-assign with evil index resizing the array's backing? use setitem
a = array.array('b', bytes(64))
run("array setitem evil", lambda: a.__setitem__(evil_index(lambda: [a.pop() for _ in range(60)]), 1))

# 4) bytearray.__setitem__ with evil index that clears self
ba = bytearray(64)
run("bytearray setitem evil-idx", lambda: ba.__setitem__(evil_index(lambda: ba.clear()), 1))

# 5) memoryview into bytearray; assign with evil index clearing exporter (should BufferError)
ba = bytearray(64)
mv = memoryview(ba)
run("memoryview setitem evil-idx", lambda: mv.__setitem__(evil_index(lambda: ba.clear()), 1))

# 6) io.BytesIO.readinto a bytearray, but bytearray resized via subclass? just basic
b = io.BytesIO(b"x"*64)
run("bytesio readinto", lambda: b.readinto(bytearray(64)))

# 7) bytes(evil_index sequence) fallback path with mutating iterator
class EvilList(list):
    pass
run("bytes(evil)", lambda: bytes([evil_index(lambda: None)]))

print("done evil_reentrancy")
