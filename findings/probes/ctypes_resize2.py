import ctypes
# Large initial buffer -> heap-allocated b_ptr (not inline)
buf = (ctypes.c_char * 4096)()
buf[:16] = b"ABCDEFGHIJKLMNOP"
mv = memoryview(buf)                 # exports view.buf = heap b_ptr
ctypes.resize(buf, 1 << 20)          # realloc -> moves+frees old 4096 heap block
_ = [bytes(500000) for _ in range(8)]  # churn allocator into the freed region
data = mv.tobytes()                  # reads freed old b_ptr
print("read ok:", data[:16], flush=True)
