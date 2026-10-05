import sys
sys.setrecursionlimit(200000)

def try_compile(label, src):
    try:
        compile(src, "<t>", "exec")
        print(label, "compiled OK")
    except RecursionError:
        print(label, "RecursionError (guarded)")
    except SyntaxError as e:
        print(label, "SyntaxError", str(e)[:40])
    except Exception as e:
        print(label, type(e).__name__, str(e)[:40])

N = 100000

# bracket-free deep AST nesting (bypasses tokenizer paren limit)
try_compile("attr",     "x" + ".a" * N)                       # Attribute chain
try_compile("unary_neg","x=" + "-" * N + "y")                  # UnaryOp chain
try_compile("unary_not","x=" + "not " * N + "y")               # nested not
try_compile("unary_inv","x=" + "~" * N + "y")                  # invert chain
try_compile("binop",    "x=" + "y+" * N + "y")                 # BinOp chain
try_compile("ternary",  "x=" + "y if y else " * N + "y")       # nested IfExp
try_compile("lambda",   "x=" + "lambda:" * N + "y")            # nested Lambda
try_compile("await",    "async def f():\n x=" + "await " * N + "y")  # nested Await
try_compile("star",     "x=" + "*" * 1 + "y")                  # (sanity)
try_compile("yield",    "def f():\n x=" + "(yield " * 5 + "y" + ")" * 5)
print("t_nested2 done")
