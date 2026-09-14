# memoryview slice-assignment: value.__buffer__ releases the view and frees exporter
ba = bytearray(b"A"*1000)
mv = memoryview(ba)
class Evil:
    def __buffer__(self, flags):
        mv.release()          # drop ba.ob_exports to 0
        ba.clear()            # free/realloc ba's internal buffer
        import gc; gc.collect()
        return memoryview(b"ZZZZ")   # 4 bytes to match slicelen
try:
    mv[0:4] = Evil()
    print("no crash, ret ok")
except Exception as e:
    print("exc", type(e).__name__, e)
