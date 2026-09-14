import io
BIG = 2**62 - 1
for op in ("read", "readline", "read1"):
    try:
        s = io.StringIO("abc")
        s.seek(BIG)
        print("=== StringIO.%s after seek(2**62-1) ===" % op)
        getattr(s, op)()
        print("   -> returned, no report")
    except Exception as e:
        print("   -> %s: %s" % (type(e).__name__, e))
