"""Minimal deterministic repro for the HZ incremental-decoder over-read.

Root cause: Modules/cjkcodecs/_codecs_cn.c DECODER(hz) reads INBYTE2 (the 2nd
input byte) BEFORE REQUIRE_INBUF(2) verifies two bytes are available, in the
`c == '~'` branch. When a lone '~' is left pending and then re-decoded from the
tightly PyMem_Malloc'd pending buffer (multibytecodec.c:1201), the read lands
one byte past the allocation -> heap-buffer-overflow.

Run under the asan-ubsan interpreter. Prints which variant trips ASan (the
process aborts on the tripping variant, so variants are ordered least->most
likely and we flush before each).
"""
import sys, codecs

variant = sys.argv[1] if len(sys.argv) > 1 else "incremental_empty"

def incremental_empty():
    d = codecs.getincrementaldecoder('hz')()
    print("feed 1: b'~' final=False", flush=True)
    d.decode(b'~', False)          # '~' buffered as pending (size 1)
    print("feed 2: b'' final=False -> re-decode tight 1-byte buffer", flush=True)
    d.decode(b'', False)           # tight malloc(1); INBYTE2 over-reads

def incremental_final():
    d = codecs.getincrementaldecoder('hz')()
    d.decode(b'~', False)
    print("feed 2: b'' final=True", flush=True)
    d.decode(b'', True)

def oneshot():
    # Likely does NOT trip (bytes carries trailing NUL inside its allocation).
    print("oneshot b'~'.decode('hz')", flush=True)
    print(repr(b'~'.decode('hz', 'replace')), flush=True)

{'incremental_empty': incremental_empty,
 'incremental_final': incremental_final,
 'oneshot': oneshot}[variant]()
print(f"variant {variant}: completed WITHOUT abort", flush=True)
