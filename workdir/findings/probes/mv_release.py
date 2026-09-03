# memoryview lifetime / release edge cases
import array
ba = bytearray(b"abcdefgh"*4)
m = memoryview(ba)
try:
    m2 = m[::2]
    m.release()
    # use m2 after parent view released (m2 holds its own ref to exporter)
    _ = bytes(m2)
    m2.release()
except Exception as e: print("exc", type(e).__name__)
# assign into memoryview with evil __index__ that releases the view
class Evil:
    def __index__(self):
        try: mm.release()
        except Exception: pass
        return 65
ba2 = bytearray(b"x"*16); mm = memoryview(ba2)
try: mm[Evil()] = 66
except Exception as e: print("exc", type(e).__name__)
print("OK mv_release")
