import sys
sys.setrecursionlimit(2000000)

def try_compile(label, src):
    try:
        compile(src, "<t>", "exec")
        print(label, "compiled OK")
    except RecursionError:
        print(label, "RecursionError (guarded)")
    except (SyntaxError, ValueError, MemoryError) as e:
        print(label, type(e).__name__, str(e)[:40])
    except Exception as e:
        print(label, type(e).__name__, str(e)[:40])

for N in (1000, 10000, 50000, 200000):
    try_compile(f"subscript[{N}]", "x" + "[0]" * N)
    try_compile(f"call[{N}]",      "x" + "()"  * N)
    try_compile(f"attr[{N}]",      "x" + ".a"  * N)
    try_compile(f"mixed[{N}]",     "x" + ".a[0]()" * N)
print("t_nested3 done")
