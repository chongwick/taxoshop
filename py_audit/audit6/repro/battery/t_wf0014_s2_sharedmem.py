# wf0014 Site 2: SharedMemory.buf memoryview used after close() unmaps segment
from multiprocessing import shared_memory
shm = shared_memory.SharedMemory(create=True, size=64)
mv = shm.buf
try:
    shm.close()          # unmaps
    print("byte after close:", mv[0])   # read through unmapped pointer
except Exception as e:
    print("sharedmem", type(e).__name__, e)
finally:
    try: shm.unlink()
    except Exception: pass
print("sharedmem done")
