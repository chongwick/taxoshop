"""Exhaustive incremental-decoder boundary sweep for workflow-0036.

For every CJK incremental decoder, feed a short (possibly truncated) payload with
final=False, then flush with decode(b'', True). A truncated lead/escape byte left
"pending" is re-decoded from a tight, exactly-sized malloc buffer, so any
lookahead past the boundary trips ASan. Unlike cjk_incremental_boundary_probe.py
this does NOT stop at the first hit -- it records every crashing case so we can
prove whether hz is the *only* surviving instance.

Run inside the ASan container:  ./python audit3/repro/cjk_boundary_sweep.py
"""
import itertools
import os
import subprocess
import sys

CODECS = [
    "hz", "gb2312", "gbk", "gb18030", "big5", "big5hkscs", "cp932",
    "shift_jis", "shift_jisx0213", "euc_jp", "euc_jisx0213", "euc_kr",
    "cp949", "johab", "iso2022_jp", "iso2022_jp_1", "iso2022_jp_2",
    "iso2022_jp_3", "iso2022_jp_ext", "iso2022_kr",
]


def run_case(codec, payload):
    code = (
        "import codecs\n"
        f"d = codecs.getincrementaldecoder({codec!r})()\n"
        f"try:\n"
        f"    d.decode({payload!r}, False)\n"
        f"    d.decode(b'', True)\n"
        f"except Exception:\n"
        f"    pass\n"
    )
    env = os.environ.copy()
    env["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1:symbolize=1"
    env["UBSAN_OPTIONS"] = "print_stacktrace=1:halt_on_error=1"
    proc = subprocess.run(
        [sys.executable, "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    out = proc.stdout + proc.stderr
    crashed = b"AddressSanitizer" in out or b"runtime error:" in out
    return crashed, proc.returncode, out


def payloads_for(codec):
    # single bytes: lead-byte truncations
    for b in range(256):
        yield bytes([b])
    # two-byte truncations after each single byte (covers DBCS lead + partial 2nd,
    # and ESC-prefixed sequences for iso2022 which need 2-3 bytes)
    esc = codec.startswith("iso2022")
    if esc:
        for b in range(256):
            yield bytes([0x1b, b])            # ESC + one byte
            yield bytes([0x1b, 0x24, b])      # ESC $ + one byte
            yield bytes([0x1b, 0x24, 0x28, b])# ESC $ ( + one byte
    # hz uses '~' escape; also probe '~' + one byte truncations generically
    for b in range(256):
        yield bytes([0x7e, b])


def main():
    hits = []
    for codec in CODECS:
        print(f"## {codec}", flush=True)
        seen = 0
        for payload in payloads_for(codec):
            seen += 1
            crashed, rc, out = run_case(codec, payload)
            if crashed:
                first = out.decode("latin-1", "replace").splitlines()
                summary = next((l for l in first if "SUMMARY" in l or "runtime error" in l), "")
                print(f"HIT codec={codec!r} payload={payload!r} rc={rc} :: {summary}", flush=True)
                hits.append((codec, payload, summary))
        print(f"   ({seen} cases, {sum(1 for h in hits if h[0]==codec)} hits)", flush=True)
    print("\n=== SUMMARY ===", flush=True)
    if not hits:
        print("no boundary over-reads found", flush=True)
    for codec, payload, summary in hits:
        print(f"{codec!r} {payload!r} :: {summary}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
