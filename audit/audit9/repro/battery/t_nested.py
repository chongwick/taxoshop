import sys
sys.setrecursionlimit(100000)

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

N = 500

# nested list comprehensions
try_compile("listcomp", "".join("[" for _ in range(N)) + "0" + "".join(" for _ in x]" for _ in range(N)))
# nested set/dict comprehensions
try_compile("setcomp", "".join("{" for _ in range(N)) + "0" + "".join(" for _ in x}" for _ in range(N)))
# nested generator expressions
try_compile("genexp", "".join("(" for _ in range(N)) + "0" + "".join(" for _ in x)" for _ in range(N)))
# nested inlined comprehensions inside a function (the gh-156091 area)
try_compile("func_listcomp", "def f():\n return " + "".join("[" for _ in range(N)) + "0" + "".join(" for _ in x]" for _ in range(N)))
# deeply nested f-strings
try_compile("fstring", "x=" + "f'{" * N + "0" + "}'" * N)
# deeply nested parentheses expression
try_compile("parens", "x=" + "(" * N + "0" + ")" * N)
# deeply nested subscripts
try_compile("subscript", "x" + "[0]" * N + "=1")
# deeply nested await/comprehension mix in async function
try_compile("async_comp", "async def f():\n return " + "".join("[" for _ in range(N)) + "0 async for _ in x" + "]" * N)
print("t_nested done")
