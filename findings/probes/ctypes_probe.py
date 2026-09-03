import ctypes

def check(name, fn):
    try:
        fn(); print(f"{name}: no crash", flush=True)
    except Exception as e:
        print(f"{name}: {type(e).__name__}: {e}", flush=True)

# 1) resize object while a memoryview is exported, then touch the view
def t_resize_mv():
    buf = (ctypes.c_char * 8)()
    mv = memoryview(buf)
    ctypes.resize(buf, 4096)   # realloc b_ptr while mv exported
    mv[0] = 65                 # write into (possibly freed) old buffer
    _ = bytes(mv)

# 2) resize while memoryview exported (read)
def t_resize_mv_read():
    buf = (ctypes.c_char * 8)()
    mv = memoryview(buf)
    ctypes.resize(buf, 65536)
    _ = mv[0]

# 3) array item assignment with __index__ that resizes the owning object
def t_arr_index_resize():
    Arr = ctypes.c_int * 4
    a = Arr()
    class I:
        def __index__(self):
            ctypes.resize(a, 4096); return 0
    a[I()] = 5

# 4) from_buffer then mutate underlying bytearray (resize)
def t_from_buffer():
    ba = bytearray(b"AAAAAAAA")
    arr = (ctypes.c_char * 8).from_buffer(ba)
    try:
        ba.clear()   # should be blocked (exported); if not -> UAF
    except BufferError:
        pass
    arr[0] = 66

for n,f in [("resize_mv_write",t_resize_mv),("resize_mv_read",t_resize_mv_read),
            ("arr_index_resize",t_arr_index_resize),("from_buffer_clear",t_from_buffer)]:
    check(n,f)
print("DONE")
