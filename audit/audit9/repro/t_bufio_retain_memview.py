import gc
import io
class EvilRaw(io.RawIOBase):
    saved = None
    def readable(self): return True
    def readinto(self, b):
        EvilRaw.saved = b            # retain transient memoryview into BufferedReader's buffer
        try: b[0] = 65
        except Exception: pass
        return 0                      # EOF
br = io.BufferedReader(EvilRaw(), buffer_size=8192)
br.read(10)                           # fill_buffer -> readinto(memoryview into self->buffer)
mv = EvilRaw.saved
print("got view", mv is not None, "nbytes", mv.nbytes if mv else None)
del br
gc.collect()                          # BufferedReader freed -> internal buffer freed
# write through the retained, now-dangling memoryview
mv[0] = 66
print("done", mv[0])
