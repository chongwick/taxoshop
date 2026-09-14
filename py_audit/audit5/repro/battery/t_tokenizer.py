# Fuzz the streaming C tokenizer (readline mode, extra_tokens=1) — exercises the
# gh-153569 offset/pointer refactor with a growing/realloc'ing source buffer.
# A retained stale char* into the old buffer -> ASan heap-UAF.  (workflow-0014 #103718)
import io, tokenize, _tokenize

def toks(src_bytes):
    try:
        list(tokenize.tokenize(io.BytesIO(src_bytes).readline))
    except Exception:
        pass

def toks_str(src):
    try:
        list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
        pass

# grow the buffer: short lines then progressively huge lines force realloc/move
def growing(nlines, width):
    parts = []
    for i in range(nlines):
        parts.append("x" + "="*1 + str(i) + " " * (i*width) + "# type: int\n")
    return "".join(parts)

CASES = [
    b"x = 1  # type: int\n" * 200,
    b"# type: ignore\n" * 500,
    (b"a" + b"b"*5000 + b" = 1  # type: ignore\n") * 50,
    b"'''" + b"line\n"*2000 + b"'''\n",              # huge multiline string spans refills
    b"x = \\\n" * 3000 + b"1\n",                      # line continuations span refills
    b"f'''" + b"{x}\n"*2000 + b"'''\n",              # multiline f-string
    b"t'''" + b"{x}\n"*2000 + b"'''\n",              # multiline t-string (new)
    ("é" * 3000 + " = 1  # type: int\n").encode(),   # non-ascii ident + type comment
    b"def f(\n" + b"    a,\n"*2000 + b"): pass\n",
    growing(400, 40).encode(),
    b"#!/usr/bin/env python\n" + b"x=1\n"*1000,
    b"\xef\xbb\xbf" + b"x = 1 # type: int\n"*500,     # BOM + type comments
]
for c in CASES:
    toks(c)

# also drive TokenizerIter directly with a readline that returns growing chunks
def make_rl(lines):
    it = iter(lines)
    def rl():
        try: return next(it)
        except StopIteration: return b""
    return rl

for extra in (True, False):
    lines = [b"x=1 # type: ignore\n"] + [b"y"+b"z"*i+b"=2 # type: int\n" for i in range(1,300)]
    try:
        for _ in _tokenize.TokenizerIter(make_rl(lines), extra_tokens=extra):
            pass
    except Exception:
        pass

print("done tokenizer")
