import itertools
import os
import subprocess
import sys


CODECS = [
    "hz",
    "gb2312",
    "gbk",
    "gb18030",
    "big5",
    "big5hkscs",
    "cp932",
    "shift_jis",
    "shift_jisx0213",
    "euc_jp",
    "euc_jisx0213",
    "euc_kr",
    "cp949",
    "johab",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
]


def run_case(codec, payload, final):
    code = (
        "import codecs\n"
        f"d = codecs.getincrementaldecoder({codec!r})()\n"
        f"d.decode({payload!r}, False)\n"
        f"d.decode(b'', {final!r})\n"
    )
    env = os.environ.copy()
    env.setdefault("ASAN_OPTIONS", "detect_leaks=0:abort_on_error=1:symbolize=1")
    env.setdefault("UBSAN_OPTIONS", "print_stacktrace=1:halt_on_error=1")
    proc = subprocess.run(
        [sys.executable, "-c", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    out = proc.stdout + proc.stderr
    return proc.returncode, out


def main():
    payloads = [bytes([b]) for b in range(256)]
    payloads.extend(bytes(pair) for pair in itertools.product(range(256), repeat=2))
    for codec in CODECS:
        print(f"## {codec}", flush=True)
        for payload in payloads:
            for final in (False, True):
                rc, out = run_case(codec, payload, final)
                if b"AddressSanitizer" in out or b"runtime error:" in out:
                    print(f"HIT codec={codec!r} payload={payload!r} final={final} rc={rc}", flush=True)
                    sys.stdout.buffer.write(out)
                    return 1
        print("ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
