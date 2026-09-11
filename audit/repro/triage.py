"""Parse ASan/UBSan log files into a deduplicated table of findings.

Groups UBSan 'runtime error:' diagnostics and ASan error headers by their
(kind, source-location) signature so we can see distinct defects rather than
repeated hits. Run on the host over collected /work/*.log and /work/ubsan.* files.
"""
import re, sys, collections

UBSAN_RE = re.compile(r'([^\s:]+\.[ch]):(\d+):\d+:\s+runtime error:\s+(.*)')
ASAN_RE = re.compile(r'ERROR:\s+AddressSanitizer:\s+([\w-]+)')

def main(paths):
    ub = collections.Counter()
    ub_example = {}
    asan = collections.Counter()
    for path in paths:
        try:
            text = open(path, errors='replace').read()
        except OSError:
            continue
        for m in UBSAN_RE.finditer(text):
            loc = f"{m.group(1)}:{m.group(2)}"
            # normalize the message: drop concrete numbers to cluster
            msg = re.sub(r'0x[0-9a-fA-F]+|\d+', 'N', m.group(3))
            key = (loc, msg)
            ub[key] += 1
            ub_example.setdefault(key, m.group(3))
        for m in ASAN_RE.finditer(text):
            asan[m.group(1)] += 1

    print("### UBSan distinct findings (location, normalized-msg) ###")
    for (loc, msg), n in ub.most_common():
        print(f"[{n:5d}] {loc}\n         {ub_example[(loc,msg)]}")
    print(f"\nTotal distinct UBSan sites: {len(ub)}")
    print("\n### ASan error kinds ###")
    for k, n in asan.most_common():
        print(f"[{n:5d}] {k}")

if __name__ == '__main__':
    main(sys.argv[1:])
