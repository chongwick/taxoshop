import sys

# Exercise the new bytearray ob_start-offset paths: advance ob_start via del b[:k]
# / take_bytes, then perform slice assigns, inserts, pops, extends with evil
# __index__ objects that resize self mid-operation.

def evil(n, action):
    class E:
        def __index__(self):
            action()
            return n
    return E()

def mk(n=2000):
    return bytearray(range(256)) * (n // 256 + 1)

# 1. front-shrink via slice-del then grow back at lo=0
b = mk()
del b[:1500]            # advance ob_start
b[0:0] = b"X" * 4000     # grow at front (lo=0)
del b[:10]
b[:5] = b"Z" * 100      # replace front, grow
assert b[:1] == b"Z"

# 2. take_bytes to advance ob_start, then slice ops
b = mk()
try:
    b.take_bytes(1000)  # advances ob_start / realigns
except Exception:
    pass
b[0:0] = b"Q" * 5000
del b[100:200]
b += b"tail" * 500

# 3. evil __index__ that shrinks self during setitem after offset
b = mk()
del b[:1000]
def shrink():
    del b[: len(b)//2]
try:
    b[5] = evil(65, shrink)
except Exception as e:
    pass

# 4. evil __index__ in insert after offset
b = mk()
del b[:800]
def grow():
    b.extend(b"A" * 6000)
try:
    b.insert(evil(3, grow), 7)
except Exception:
    pass

# 5. slice assign where values buffer is evil (resizes self via __buffer__ not possible;
#    use setitem with evil index growing then shrinking)
b = mk()
del b[:1234]
def churn():
    b.extend(b"g" * 100)
    del b[:50]
try:
    b[1:3] = bytes(evil(2, churn).__index__() * b"\x00")
except Exception:
    pass

print("t_ba_offset done", len(b))
